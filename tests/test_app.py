"""Exercise real Tk widgets and background callbacks with hardware-free services."""
import time
import tkinter as tk
import customtkinter as ctk
import unittest
from dongle_go.app import App
from dongle_go.core import DongleService, CoreError


class AppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # CTk maintains font/scaling resources per Tcl interpreter. The application
        # has one root for its lifetime, so tests share that interpreter as well.
        ctk.set_appearance_mode("light")
        cls.root = ctk.CTk()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def setUp(self):
        self.app = App(self.root, DongleService(demo=True), 'en')
        self.wait(lambda: bool(self.app.port.get()))

    def tearDown(self):
        self.app.closed = True
        self.app.frame.destroy()
        self.root.unbind("<Configure>")

    def wait(self, predicate):
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            self.root.update()
            if predicate():
                return
            time.sleep(.01)
        self.fail('UI did not settle before deadline')

    def test_demo_check_apply_restore_language(self):
        self.assertEqual(str(self.app.setup_button.cget('state')), 'disabled')
        self.app.check_button.invoke()
        self.wait(lambda: not self.app.busy)
        self.assertTrue(self.app.ready)
        self.app.setup_button.invoke()
        self.wait(lambda: not self.app.busy)
        self.assertEqual(self.app.status_key, 'demo_done')
        self.assertFalse(self.app.ready)
        self.assertEqual(str(self.app.restore_button.cget('state')), 'normal')
        self.app.restore_button.invoke()
        self.wait(lambda: not self.app.busy)
        self.app.lang.set('中文')
        self.app.change_language()
        self.assertIn('模拟', self.app.status_label.cget('text'))

    def test_target_change_invalidates_plan(self):
        self.app.check()
        self.wait(lambda: not self.app.busy)
        self.app.target.set('ipad')
        self.app.selection_changed()
        self.assertFalse(self.app.ready)
        self.assertEqual(str(self.app.setup_button.cget('state')), 'disabled')

    def test_unknown_firmware_never_enables_setup(self):
        def reject(*_):
            raise CoreError('unsupported', 'raw private response must not display')
        self.app.service.plan = reject
        self.app.check()
        self.wait(lambda: not self.app.busy)
        self.assertFalse(self.app.ready)
        self.assertEqual(self.app.status_key, 'unknown')
        self.assertNotIn('raw private', self.app.status_label.cget('text'))

    def test_empty_list_clears_selection_and_disables_writes(self):
        self.app.service.ports = lambda: []
        self.app.refresh()
        self.wait(lambda: not self.app.busy)
        self.assertEqual(self.app.port.get(), '')
        self.assertEqual(self.app.status_key, 'none')
        self.assertEqual(str(self.app.setup_button.cget('state')), 'disabled')

    def test_keyboard_selectors_and_disabled_action(self):
        self.app.language_box._cycle(1)
        self.assertEqual(self.app.lang.get(), '中文')
        self.assertEqual(self.app.main_title.cget('text'), self.app.t('main_title'))
        self.app.port_box.configure(values=['demo://dongle', 'demo://other'])
        self.app.ready = True
        self.app.port_box._cycle(1)
        self.assertEqual(self.app.port.get(), 'demo://other')
        self.assertFalse(self.app.ready)
        self.app.port_box.configure(state='disabled')
        self.app.port_box._cycle(1)
        self.assertEqual(self.app.port.get(), 'demo://other')
        self.app.setup_button._keyboard_activate(None)
        self.assertFalse(self.app.busy)

    def test_compact_keyboard_focus_scrolls_into_view(self):
        self.root.deiconify()
        self.root.geometry('780x620')
        self.root.update()
        self.app._responsive()
        self.root.update()
        self.assertFalse(self.app.hero.winfo_ismapped())
        self.app.help_button._canvas.focus_force()
        self.root.update()
        canvas = self.app.workspace._parent_canvas
        self.assertGreaterEqual(self.app.help_button.winfo_rooty(), canvas.winfo_rooty())
        self.assertLessEqual(self.app.help_button.winfo_rooty() + self.app.help_button.winfo_height(),
                             canvas.winfo_rooty() + canvas.winfo_height() + 2)
        self.root.withdraw()
