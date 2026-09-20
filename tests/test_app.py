"""Exercise real Tk widgets and background callbacks with hardware-free services."""
import time
import tkinter as tk
import unittest
from dongle_go.app import App
from dongle_go.core import DongleService, CoreError


class AppTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.app = App(self.root, DongleService(demo=True), 'en')
        self.wait(lambda: bool(self.app.port.get()))

    def tearDown(self):
        self.app.closed = True
        self.root.destroy()

    def wait(self, predicate):
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            self.root.update()
            if predicate():
                return
            time.sleep(.01)
        self.fail('UI did not settle before deadline')

    def test_demo_check_apply_restore_language(self):
        self.assertEqual(str(self.app.setup_button['state']), 'disabled')
        self.app.check_button.invoke()
        self.wait(lambda: not self.app.busy)
        self.assertTrue(self.app.ready)
        self.app.setup_button.invoke()
        self.wait(lambda: not self.app.busy)
        self.assertEqual(self.app.status_key, 'demo_done')
        self.assertFalse(self.app.ready)
        self.assertEqual(str(self.app.restore_button['state']), 'normal')
        self.app.restore_button.invoke()
        self.wait(lambda: not self.app.busy)
        self.app.lang.set('中文')
        self.app.change_language()
        self.assertIn('模拟', self.app.status_label['text'])

    def test_target_change_invalidates_plan(self):
        self.app.check()
        self.wait(lambda: not self.app.busy)
        self.app.target.set('ipad')
        self.app.selection_changed()
        self.assertFalse(self.app.ready)
        self.assertEqual(str(self.app.setup_button['state']), 'disabled')

    def test_unknown_firmware_never_enables_setup(self):
        def reject(*_):
            raise CoreError('unsupported', 'raw private response must not display')
        self.app.service.plan = reject
        self.app.check()
        self.wait(lambda: not self.app.busy)
        self.assertFalse(self.app.ready)
        self.assertEqual(self.app.status_key, 'unknown')
        self.assertNotIn('raw private', self.app.status_label['text'])

    def test_empty_list_clears_selection_and_disables_writes(self):
        self.app.service.ports = lambda: []
        self.app.refresh()
        self.wait(lambda: not self.app.busy)
        self.assertEqual(self.app.port.get(), '')
        self.assertEqual(self.app.status_key, 'none')
        self.assertEqual(str(self.app.setup_button['state']), 'disabled')
