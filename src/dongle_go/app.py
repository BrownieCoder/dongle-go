"""Small native UI. Serial work never runs on Tk's event thread."""
import argparse
import locale
import platform
import queue
import threading
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox

from .ui import ModernView, CANVAS

from .core import CoreError, DongleService
from .i18n import error_key, tr


class App(ModernView):
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
        root.geometry(f"{min(1060, root.winfo_screenwidth()-60)}x{min(790, root.winfo_screenheight()-100)}")
        root.minsize(780, 620)
        root.configure(bg=CANVAS)
        root.protocol("WM_DELETE_WINDOW", self.close)
        self._build()
        root.after(100, self._poll)
        root.after(150, self.refresh)

    def t(self, key):
        return tr(self.language, key)

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
        self.progress.start()
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
    ctk.set_appearance_mode("light")
    root = ctk.CTk()
    app = App(root, DongleService(demo=args.demo or bool(args.smoke_test)), language)
    if args.smoke_test:
        from .smoke import schedule
        schedule(app, args.smoke_test)
    root.mainloop()
    if args.smoke_test and not app.smoke_passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
