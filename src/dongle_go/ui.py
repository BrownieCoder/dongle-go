"""Warm, illustrated desktop view. Device operations remain in app/core."""
from pathlib import Path
import tkinter as tk
import tkinter.font as tkfont

import customtkinter as ctk
from PIL import Image, ImageDraw

CANVAS = '#F7F7F2'
INK = '#263A32'
MUTED = '#647269'
LINE = '#E2E7DE'
GREEN = '#1F654D'
MINT = '#EAF2E7'
YELLOW = '#F5C451'


class FocusButton(ctk.CTkButton):
    """CTk's rounded button with explicit keyboard operation and focus feedback."""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('corner_radius', 12)
        kwargs.setdefault('height', 40)
        kwargs.setdefault('border_width', 2)
        kwargs.setdefault('border_color', kwargs.get('fg_color', LINE))
        super().__init__(*args, **kwargs)
        self._rest_border = self.cget('border_color')
        self._canvas.configure(takefocus=1)
        self._canvas.bind('<Return>', self._keyboard_activate)
        self._canvas.bind('<space>', self._keyboard_activate)
        self._canvas.bind('<FocusIn>', lambda _: super(FocusButton, self).configure(border_color='#B56A12'))
        self._canvas.bind('<FocusOut>', lambda _: super(FocusButton, self).configure(border_color=self._rest_border))

    def _keyboard_activate(self, _event):
        self.invoke()
        return 'break'

    def configure(self, require_redraw=False, **kwargs):
        if 'border_color' in kwargs:
            self._rest_border = kwargs['border_color']
        super().configure(require_redraw=require_redraw, **kwargs)
        if 'state' in kwargs:
            self._canvas.configure(takefocus=0 if kwargs['state'] == 'disabled' else 1)


class KeyboardComboBox(ctk.CTkComboBox):
    """Keep readonly selection usable without a pointer."""
    def __init__(self, *args, command=None, **kwargs):
        self.selection_command = command
        super().__init__(*args, command=command, **kwargs)
        self.bind('<Down>', lambda _: self._cycle(1))
        self.bind('<Up>', lambda _: self._cycle(-1))

    def _cycle(self, direction):
        values = self.cget('values')
        if self.cget('state') != 'disabled' and values:
            current = values.index(self.get()) if self.get() in values else -1
            value = values[(current + direction) % len(values)]
            self.set(value)
            if self.selection_command:
                self.selection_command(value)
        return 'break'


def device_icon(kind):
    """Original code-drawn UI icons, supersampled for sharp desktop rendering."""
    image = Image.new('RGBA', (120, 96), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    if kind == 'ipad':
        draw.rounded_rectangle((28, 5, 91, 89), radius=10, outline=INK, width=6)
        draw.line((52, 77, 69, 77), fill=INK, width=4)
    else:
        draw.rounded_rectangle((15, 8, 105, 67), radius=7, outline=INK, width=6)
        if kind == 'windows':
            for x, y in ((47, 26), (62, 26), (47, 41), (62, 41)):
                draw.rectangle((x, y, x+10, y+10), fill=INK)
        draw.line((9, 80, 112, 80), fill=INK, width=6)
        draw.line((51, 79, 69, 79), fill=INK, width=8)
    return ctk.CTkImage(light_image=image, dark_image=image, size=(30, 24))


class ModernView:
    def _font(self, size=14, weight='normal'):
        return ctk.CTkFont(family=self.font_family, size=size, weight=weight)

    def _label(self, master, text='', size=14, weight='normal', color=INK, **kwargs):
        kwargs.setdefault('anchor', 'w')
        kwargs.setdefault('justify', 'left')
        return ctk.CTkLabel(master, text=text, font=self._font(size, weight), text_color=color, **kwargs)

    def _build(self):
        ctk.set_appearance_mode('light')
        available = set(tkfont.families(self.root))
        preferred = ('PingFang SC', 'Microsoft YaHei UI', 'Noto Sans CJK SC', 'Segoe UI', 'Arial')
        self.font_family = next((f for f in preferred if f in available), 'Arial')
        self.frame = ctk.CTkFrame(self.root, fg_color=CANVAS, corner_radius=0)
        self.frame.pack(fill='both', expand=True)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self.frame, fg_color=CANVAS, corner_radius=0)
        header.grid(row=0, column=0, sticky='ew', padx=28, pady=(20, 16))
        header.grid_columnconfigure(1, weight=1)
        self.brand_mark = self._label(header, 'D', size=22, weight='bold', fg_color=YELLOW,
                                      width=40, height=40, corner_radius=12, anchor='center')
        self.brand_mark.grid(row=0, column=0, padx=(0, 11))
        self._label(header, 'Dongle Go', size=24, weight='bold').grid(row=0, column=1, sticky='w')
        self.mode_chip = self._label(header, size=12, color=GREEN, fg_color=MINT,
                                     corner_radius=14, width=102, height=30, anchor='center')
        self.mode_chip.grid(row=0, column=2, padx=16)
        self.language_box = KeyboardComboBox(header, variable=self.lang, values=['中文', 'English'],
            state='readonly', width=112, height=34, corner_radius=10, fg_color='white',
            border_color=LINE, button_color=LINE, button_hover_color='#D2DBD0', text_color=INK,
            dropdown_fg_color='white', dropdown_text_color=INK, dropdown_hover_color=MINT,
            font=self._font(13), command=lambda _: self.change_language())
        self.language_box.grid(row=0, column=3)

        self.content = ctk.CTkFrame(self.frame, fg_color=CANVAS, corner_radius=0)
        self.content.grid(row=1, column=0, sticky='nsew', padx=24, pady=(0, 16))
        self.content.grid_columnconfigure(1, weight=1)
        self.content.grid_rowconfigure(0, weight=1)
        self.hero = ctk.CTkFrame(self.content, width=310, corner_radius=24, fg_color='#EEF1E5')
        self.hero.grid(row=0, column=0, sticky='nsew', padx=(0, 18))
        self.hero.grid_propagate(False)
        self.hero.grid_columnconfigure(0, weight=1)
        self.hero.grid_rowconfigure(3, weight=1)
        self._label(self.hero, 'LITTLE DONGLE. BIG POSSIBILITIES.', size=10, weight='bold', color=GREEN).grid(
            row=0, column=0, sticky='w', padx=24, pady=(25, 12))
        self.hero_title = self._label(self.hero, size=32, weight='bold')
        self.hero_title.grid(row=1, column=0, sticky='w', padx=24)
        self.tagline = self._label(self.hero, size=13, color=MUTED, wraplength=255)
        self.tagline.grid(row=2, column=0, sticky='w', padx=24, pady=(8, 2))
        mascot_path = Path(__file__).with_name('assets') / 'mascot.png'
        with Image.open(mascot_path) as source:
            mascot = source.convert('RGBA')
        self.mascot_image = ctk.CTkImage(light_image=mascot, dark_image=mascot, size=(282, 282))
        self.mascot_label = ctk.CTkLabel(self.hero, text='', image=self.mascot_image)
        self.mascot_label.grid(row=3, column=0, pady=(0, 4))
        self.speech = self._label(self.hero, size=13, weight='bold', fg_color='white',
                                  corner_radius=14, height=42, anchor='center', wraplength=250)
        self.speech.grid(row=4, column=0, sticky='ew', padx=20, pady=(0, 14))
        self.steps = []
        for number in range(1, 4):
            row = ctk.CTkFrame(self.hero, fg_color='transparent')
            row.grid(row=4+number, column=0, sticky='ew', padx=25, pady=(0, 8))
            self._label(row, str(number), size=11, weight='bold', fg_color='#DEE7D7',
                        corner_radius=10, width=22, height=22, anchor='center').pack(side='left', padx=(0, 9))
            label = self._label(row, size=12, color=MUTED)
            label.pack(side='left')
            self.steps.append(label)
        self._label(self.hero, 'USB  /  4G  /  GO', size=11, weight='bold', color='#84907E').grid(
            row=8, column=0, sticky='w', padx=25, pady=(5, 20))

        # Scroll only the task area on short/small screens; all actions stay reachable.
        self.workspace = ctk.CTkScrollableFrame(self.content, fg_color=CANVAS, corner_radius=0,
            scrollbar_button_color='#D6DED2', scrollbar_button_hover_color='#BAC8B7')
        self.workspace.grid(row=0, column=1, sticky='nsew')
        self.workspace.grid_columnconfigure(0, weight=1)
        self.main_title = self._label(self.workspace, size=25, weight='bold')
        self.main_title.grid(row=0, column=0, sticky='w', padx=5, pady=(4, 5))
        self.intro = self._label(self.workspace, size=13, color=MUTED, wraplength=510)
        self.intro.grid(row=1, column=0, sticky='w', padx=5, pady=(0, 19))
        self.card = ctk.CTkFrame(self.workspace, fg_color='white', corner_radius=22,
                               border_width=1, border_color=LINE)
        self.card.grid(row=2, column=0, sticky='ew', padx=2)
        self.card.grid_columnconfigure(0, weight=1)
        self.target_label = self._label(self.card, size=15, weight='bold')
        self.target_label.grid(row=0, column=0, sticky='w', padx=24, pady=(22, 12))
        targets = ctk.CTkFrame(self.card, fg_color='transparent')
        targets.grid(row=1, column=0, sticky='ew', padx=24)
        self.radios = []
        self.device_images = []
        for i, (key, label) in enumerate((('mac', 'Mac'), ('windows', 'Windows'), ('ipad', 'iPad'))):
            targets.grid_columnconfigure(i, weight=1, uniform='devices')
            icon = device_icon(key)
            self.device_images.append(icon)
            button = FocusButton(targets, text=label, image=icon, compound='top', height=77,
                width=100, font=self._font(13, 'bold'), fg_color='#F7F8F5', hover_color='#EEF2E9',
                text_color=INK, border_color=LINE, text_color_disabled=MUTED,
                command=lambda k=key: self._select_target(k))
            button.grid(row=0, column=i, sticky='ew', padx=(0 if i == 0 else 5, 0 if i == 2 else 5))
            self.radios.append(button)
        self.hint = self._label(self.card, size=12, color=MUTED, wraplength=475)
        self.hint.grid(row=2, column=0, sticky='w', padx=24, pady=(10, 18))
        ctk.CTkFrame(self.card, height=1, fg_color=LINE).grid(row=3, column=0, sticky='ew', padx=24)
        self.device_label = self._label(self.card, size=15, weight='bold')
        self.device_label.grid(row=4, column=0, sticky='w', padx=24, pady=(18, 10))
        device_row = ctk.CTkFrame(self.card, fg_color='transparent')
        device_row.grid(row=5, column=0, sticky='ew', padx=24)
        device_row.grid_columnconfigure(0, weight=1)
        self.port_box = KeyboardComboBox(device_row, variable=self.port, state='readonly', height=43,
            corner_radius=11, border_width=1, border_color=LINE, fg_color='#F7F8F5',
            button_color='#EAF0E6', button_hover_color='#DDE7D6', text_color=INK,
            dropdown_fg_color='white', dropdown_text_color=INK, dropdown_hover_color=MINT,
            font=self._font(13), command=self.selection_changed)
        self.port_box.grid(row=0, column=0, sticky='ew', padx=(0, 10))
        self.refresh_button = FocusButton(device_row, text='', width=112, height=43,
            font=self._font(12, 'bold'), fg_color='white', hover_color=MINT, text_color=GREEN,
            border_color=LINE, command=self.refresh)
        self.refresh_button.grid(row=0, column=1)
        self.port_hint = self._label(self.card, size=11, color=MUTED)
        self.port_hint.grid(row=6, column=0, sticky='w', padx=26, pady=(6, 14))
        actions = ctk.CTkFrame(self.card, fg_color='transparent')
        actions.grid(row=7, column=0, sticky='ew', padx=24, pady=(0, 17))
        actions.grid_columnconfigure(1, weight=1)
        self.check_button = FocusButton(actions, text='', width=144, height=48,
            font=self._font(13, 'bold'), fg_color='#EFF3EC', hover_color='#E0E8D9',
            text_color=INK, text_color_disabled='#7C897D', border_color='#EFF3EC', command=self.check)
        self.check_button.grid(row=0, column=0, padx=(0, 10))
        self.setup_button = FocusButton(actions, text='', height=48, font=self._font(14, 'bold'),
            fg_color=YELLOW, hover_color='#EAB33B', text_color=INK, text_color_disabled='#7B796A',
            border_color=YELLOW, command=self.apply)
        self.setup_button.grid(row=0, column=1, sticky='ew')
        self.status_panel = ctk.CTkFrame(self.card, fg_color='#F3F5EF', corner_radius=14)
        self.status_panel.grid(row=8, column=0, sticky='ew', padx=24, pady=(0, 18))
        self.status_panel.grid_columnconfigure(1, weight=1)
        self.status_icon = self._label(self.status_panel, '·', size=20, weight='bold', width=24,
                                       anchor='center', color=GREEN)
        self.status_icon.grid(row=0, column=0, rowspan=2, sticky='n', padx=(12, 5), pady=12)
        self.status_title = self._label(self.status_panel, size=13, weight='bold')
        self.status_title.grid(row=0, column=1, sticky='w', padx=(0, 14), pady=(12, 3))
        self.status_label = self._label(self.status_panel, size=12, color=MUTED, wraplength=430)
        self.status_label.grid(row=1, column=1, sticky='ew', padx=(0, 14), pady=(0, 12))
        self.progress = ctk.CTkProgressBar(self.card, mode='indeterminate', height=4,
                                        fg_color=MINT, progress_color=GREEN)
        self.progress.grid(row=9, column=0, sticky='ew', padx=24, pady=(0, 12))
        self.progress.grid_remove()
        bottom = ctk.CTkFrame(self.card, fg_color='transparent')
        bottom.grid(row=10, column=0, sticky='ew', padx=20, pady=(0, 14))
        self.restore_button = FocusButton(bottom, text='', width=142, height=34, font=self._font(12),
            fg_color='white', hover_color='#F1F4EC', text_color=MUTED,
            text_color_disabled='#A0A79D', border_color='white', command=self.restore)
        self.restore_button.pack(side='left')
        self.help_button = FocusButton(bottom, text='', width=118, height=34, font=self._font(12),
            fg_color='white', hover_color='#F1F4EC', text_color=GREEN, border_color='white', command=self.help)
        self.help_button.pack(side='right')
        self.banner = self._label(self.workspace, size=11, color=MUTED, wraplength=520)
        self.banner.grid(row=3, column=0, sticky='w', padx=8, pady=(14, 8))
        self._texts()
        self._controls()
        self._compact = None
        self._resize_job = None
        self.root.bind('<Configure>', self._schedule_resize, add='+')
        self.root.after_idle(self._responsive)
        for control in [*self.radios, self.port_box, self.refresh_button,
                        self.check_button, self.setup_button, self.restore_button, self.help_button]:
            focus_widget = control._entry if isinstance(control, KeyboardComboBox) else control._canvas
            focus_widget.bind('<FocusIn>', lambda event, widget=control:
                self.root.after_idle(lambda: self._reveal(widget)), add='+')

    def _reveal(self, widget):
        if self.closed or not widget.winfo_exists():
            return
        canvas = self.workspace._parent_canvas
        top = widget.winfo_rooty() - canvas.winfo_rooty()
        bottom = top + widget.winfo_height()
        height = canvas.winfo_height()
        offset = top - 8 if top < 0 else bottom - height + 8 if bottom > height else 0
        if offset:
            canvas.yview_moveto(max(0, (canvas.canvasy(0) + offset) /
                                   max(1, self.workspace.winfo_height())))

    def _select_target(self, target):
        if not self.busy:
            self.target.set(target)
            self.selection_changed()

    def _schedule_resize(self, event):
        if event.widget is self.root and self._resize_job is None:
            self._resize_job = self.root.after(80, self._responsive)

    def _responsive(self):
        self._resize_job = None
        if self.closed:
            return
        compact = self.root.winfo_width() < 950
        if compact != self._compact:
            self.hero.grid_remove() if compact else self.hero.grid()
            self._compact = compact
        width = max(330, self.workspace.winfo_width() - 74)
        self.hint.configure(wraplength=width)
        self.status_label.configure(wraplength=max(270, width-40))
        self.intro.configure(wraplength=width+25)
        self.banner.configure(wraplength=width+25)

    def _texts(self):
        for widget, key in ((self.tagline, 'tagline'), (self.hero_title, 'hero_title'),
                            (self.main_title, 'main_title'), (self.intro, 'intro'),
                            (self.speech, 'speech'), (self.target_label, 'target'),
                            (self.hint, 'target_hint'), (self.device_label, 'device'),
                            (self.refresh_button, 'refresh'), (self.check_button, 'check'),
                            (self.setup_button, 'setup'), (self.restore_button, 'restore'),
                            (self.help_button, 'help'), (self.port_hint, 'port_hint')):
            widget.configure(text=self.t(key))
        self.mode_chip.configure(text=self.t('demo_chip' if self.service.demo else 'preview_chip'))
        self.banner.configure(text=self.t('demo' if self.service.demo else 'preview'))
        for index, label in enumerate(self.steps, 1):
            label.configure(text=self.t(f'step{index}').split('  ', 1)[-1])
        self._status(self.status_key)

    def _status(self, key):
        self.status_key = key
        self.status_label.configure(text=self.t(key))
        if key in ('working', 'configuring', 'restoring'):
            title, symbol, tint = 'status_working', '…', '#EEF3E9'
        elif key in ('ready', 'demo_done', 'configured', 'ipad_done', 'restored'):
            title = 'status_demo_done' if key == 'demo_done' else 'status_ready' if key == 'ready' else 'status_verify'
            symbol, tint = '✓', '#EAF3E7'
        elif key in ('idle', 'choose', 'none'):
            title, symbol, tint = 'status_start', '→', '#F1F4ED'
        else:
            title, symbol, tint = 'status_attention', '!', '#FFF2DB'
        self.status_title.configure(text=self.t(title))
        self.status_icon.configure(text=symbol)
        self.status_panel.configure(fg_color=tint)

    def _controls(self):
        self.refresh_button.configure(state='disabled' if self.busy else 'normal')
        check_active = bool(self.port.get()) and not self.busy
        first_action = check_active and not self.ready
        self.check_button.configure(state='normal' if check_active else 'disabled',
            fg_color=YELLOW if first_action else '#EFF3EC',
            border_color=YELLOW if first_action else '#EFF3EC')
        active = self.ready and not self.busy
        self.setup_button.configure(state='normal' if active else 'disabled',
                                    fg_color=YELLOW if active else '#EAE8DC',
                                    border_color=YELLOW if active else '#EAE8DC')
        self.restore_button.configure(state='normal' if self.port.get() and not self.busy
            and self.service.status()['recovery_available'] else 'disabled')
        self.port_box.configure(state='disabled' if self.busy else 'readonly')
        for key, button in zip(('mac', 'windows', 'ipad'), self.radios):
            selected = self.target.get() == key
            button.configure(state='disabled' if self.busy else 'normal',
                fg_color=MINT if selected else '#F7F8F5', border_color=GREEN if selected else LINE)
        self.progress.grid() if self.busy else self.progress.grid_remove()
