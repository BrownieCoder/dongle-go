"""Small native UI. Serial work never runs on Tk's event thread."""
import argparse
import locale
import platform
import queue
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from .core import CoreError, DongleService
from .i18n import error_key, tr


class App:
    def __init__(self, root, service, language="en"):
        self.root, self.service, self.language = root, service, language
        self.events = queue.Queue()
        self.busy = False
        self.ready = False
        self.closed = False
        self.last_error = ""
        self.status_key = "idle"
        self.port_records = []
        self.target = tk.StringVar(value="mac" if platform.system() == "Darwin" else "windows")
        self.port = tk.StringVar()
        self.lang = tk.StringVar(value="中文" if language == "zh" else "English")
        root.title("Dongle Go · USB 4G")
        root.geometry("800x740")
        root.minsize(720, 700)
        root.configure(bg="#F6F4EC")
        root.protocol("WM_DELETE_WINDOW", self.close)
        self._build()
        root.after(100, self._poll)
        root.after(150, self.refresh)

    def t(self, key):
        return tr(self.language, key)

    def _build(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TFrame", background="#F6F4EC")
        style.configure("TLabel", background="#F6F4EC", foreground="#173A35", font=("Arial", 12))
        style.configure("TButton", font=("Arial", 12), padding=(14, 10))
        style.configure("Primary.TButton", background="#186B58", foreground="white", font=("Arial", 14, "bold"), padding=(18, 16))
        style.map("Primary.TButton", background=[("disabled", "#D5DED5"), ("active", "#125443")], foreground=[("disabled", "#4C6258")])
        style.configure("TCombobox", padding=7, font=("Arial", 12))
        self.frame = ttk.Frame(self.root, padding=30)
        self.frame.pack(fill="both", expand=True)
        f = self.frame
        f.columnconfigure(0, weight=1)
        top = ttk.Frame(f)
        top.grid(row=0, column=0, sticky="ew")
        top.columnconfigure(0, weight=1)
        ttk.Label(top, text="Dongle Go", font=("Arial", 29, "bold")).grid(row=0, column=0, sticky="w")
        self.language_box = ttk.Combobox(top, textvariable=self.lang, values=("中文", "English"), state="readonly", width=9)
        self.language_box.grid(row=0, column=1)
        self.language_box.bind("<<ComboboxSelected>>", self.change_language)
        self.tagline = ttk.Label(f)
        self.tagline.grid(row=1, column=0, sticky="w", pady=(8, 18))
        self.banner = tk.Label(f, anchor="w", padx=14, pady=12, bg="#F4E7AE", fg="#493B13", font=("Arial", 11, "bold"))
        self.banner.grid(row=2, column=0, sticky="ew")
        self.steps = ttk.Label(f, wraplength=730, font=("Arial", 12, "bold"))
        self.steps.grid(row=3, column=0, sticky="w", pady=(24, 20))
        self.target_label = ttk.Label(f, font=("Arial", 13, "bold"))
        self.target_label.grid(row=4, column=0, sticky="w")
        targets = ttk.Frame(f)
        targets.grid(row=5, column=0, sticky="w", pady=(8, 5))
        self.radios = []
        for key, label in (("mac", "Mac"), ("windows", "Windows"), ("ipad", "iPad")):
            button = ttk.Radiobutton(targets, text=label, variable=self.target, value=key, command=self.selection_changed)
            button.pack(side="left", padx=(0, 28), ipady=4)
            self.radios.append(button)
        self.hint = ttk.Label(f, wraplength=710, foreground="#53675F", font=("Arial", 10))
        self.hint.grid(row=6, column=0, sticky="w", pady=(0, 20))
        self.device_label = ttk.Label(f, font=("Arial", 13, "bold"))
        self.device_label.grid(row=7, column=0, sticky="w")
        device_row = ttk.Frame(f)
        device_row.grid(row=8, column=0, sticky="ew", pady=(8, 14))
        device_row.columnconfigure(0, weight=1)
        self.port_box = ttk.Combobox(device_row, textvariable=self.port, state="readonly")
        self.port_box.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.port_box.bind("<<ComboboxSelected>>", self.selection_changed)
        self.refresh_button = ttk.Button(device_row, command=self.refresh)
        self.refresh_button.grid(row=0, column=1)
        actions = ttk.Frame(f)
        actions.grid(row=9, column=0, sticky="ew")
        self.check_button = ttk.Button(actions, command=self.check)
        self.check_button.pack(side="left", padx=(0, 10))
        self.setup_button = ttk.Button(actions, style="Primary.TButton", command=self.apply)
        self.setup_button.pack(side="left", fill="x", expand=True)
        self.progress = ttk.Progressbar(f, mode="indeterminate")
        self.progress.grid(row=10, column=0, sticky="ew", pady=(18, 12))
        self.status_label = ttk.Label(f, wraplength=715, justify="left", font=("Arial", 12))
        self.status_label.grid(row=11, column=0, sticky="nw")
        f.rowconfigure(11, weight=1)
        bottom = ttk.Frame(f)
        bottom.grid(row=12, column=0, sticky="ew", pady=(20, 0))
        self.restore_button = ttk.Button(bottom, command=self.restore)
        self.restore_button.pack(side="left")
        self.help_button = ttk.Button(bottom, command=self.help)
        self.help_button.pack(side="right")
        self._texts()
        self._controls()

    def _texts(self):
        for widget, key in ((self.tagline, "tagline"), (self.target_label, "target"),
                            (self.hint, "target_hint"), (self.device_label, "device"),
                            (self.refresh_button, "refresh"), (self.check_button, "check"),
                            (self.setup_button, "setup"), (self.restore_button, "restore"),
                            (self.help_button, "help")):
            widget.configure(text=self.t(key))
        self.banner.configure(text=self.t("demo" if self.service.demo else "preview"))
        self.steps.configure(text="   →   ".join(self.t(k) for k in ("step1", "step2", "step3")))
        self._status(self.status_key)

    def _status(self, key):
        self.status_key = key
        self.status_label.configure(text=self.t(key))

    def _controls(self):
        self.refresh_button.configure(state="disabled" if self.busy else "normal")
        self.check_button.configure(state="normal" if self.port.get() and not self.busy else "disabled")
        self.setup_button.configure(state="normal" if self.ready and not self.busy else "disabled")
        self.restore_button.configure(state="normal" if self.port.get() and not self.busy and self.service.status()["recovery_available"] else "disabled")
        self.port_box.configure(state="disabled" if self.busy else "readonly")
        for button in self.radios:
            button.configure(state="disabled" if self.busy else "normal")

    def change_language(self, _event=None):
        self.language = "zh" if self.lang.get() == "中文" else "en"
        self._texts()

    def selection_changed(self, _event=None):
        self.ready = False
        self.last_error = ""
        self._status("choose" if self.port.get() else "none")
        self._controls()

    def _run(self, operation, call):
        if self.busy:
            return
        self.busy = True
        self.last_error = ""
        self._status({"apply": "configuring", "restore": "restoring"}.get(operation, "working"))
        self.progress.start(15)
        self._controls()

        def worker():
            try:
                result = call()
                self.events.put((operation, result, None))
            except CoreError as exc:
                self.events.put((operation, None, exc.code))
            except Exception:
                # Do not display or persist raw modem responses, identifiers or OS paths.
                self.events.put((operation, None, "internal_error"))

        threading.Thread(target=worker, name="dongle-operation", daemon=True).start()

    def refresh(self):
        self.ready = False
        self._run("ports", self.service.ports)

    def check(self):
        port, target = self.port.get(), self.target.get()
        if not port:
            return
        self.ready = False
        self._run("check", lambda: self.service.plan(port, target))

    def apply(self):
        if not self.ready:
            return
        port, target = self.port.get(), self.target.get()
        self.ready = False
        self._run("apply", lambda: self.service.apply(port, target))

    def restore(self):
        port = self.port.get()
        if port:
            self.ready = False
            self._run("restore", lambda: self.service.restore(port))

    def _poll(self):
        if self.closed:
            return
        try:
            while True:
                operation, result, error = self.events.get_nowait()
                self.busy = False
                self.progress.stop()
                if error:
                    self.ready = False
                    self.last_error = error
                    self._status(error_key(error))
                elif operation == "ports":
                    self.port_records = result
                    ports = [p["port"] for p in result if p.get("candidate")]
                    self.port_box.configure(values=ports)
                    self.port.set(self.port.get() if self.port.get() in ports else ports[0] if ports else "")
                    self._status("choose" if ports else "none")
                elif operation == "check":
                    self.ready = True
                    self._status("ready")
                elif operation == "apply":
                    self._status("demo_done" if self.service.demo else "ipad_done" if result.get("target") == "ipad" else "configured")
                elif operation == "restore":
                    self._status("demo_done" if self.service.demo else "restored")
                self._controls()
        except queue.Empty:
            pass
        self.root.after(100, self._poll)

    def help(self):
        detail = self.t("help_body")
        if self.last_error:
            detail += "\n\n" + self.t("code") + ": " + self.last_error
        messagebox.showinfo(self.t("help_title"), detail, parent=self.root)

    def close(self):
        if self.busy:
            messagebox.showinfo("Dongle Go", self.t("close_busy"), parent=self.root)
            return
        self.closed = True
        self.root.destroy()


def main():
    parser = argparse.ArgumentParser(description="Dongle Go — USB cellular setup assistant")
    parser.add_argument("--demo", action="store_true", help="Simulate a dongle; never access hardware")
    parser.add_argument("--language", choices=("en", "zh"), default=None)
    parser.add_argument("--smoke-test", metavar="REPORT_JSON", help="Run packaged GUI checks using simulation only, then exit")
    args = parser.parse_args()
    language = args.language
    if language is None:
        language = "zh" if (locale.getlocale()[0] or "").lower().startswith("zh") else "en"
    root = tk.Tk()
    app = App(root, DongleService(demo=args.demo or bool(args.smoke_test)), language)
    if args.smoke_test:
        from .smoke import schedule
        schedule(app, args.smoke_test)
    root.mainloop()
    if args.smoke_test and not app.smoke_passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
