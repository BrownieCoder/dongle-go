import unittest
from dongle_go.i18n import TEXT, ERROR_KEYS, tr, error_key


class LocalizationTests(unittest.TestCase):
    def test_every_message_exists_in_both_languages(self):
        self.assertEqual(set(TEXT['en']), set(TEXT['zh']))
        self.assertTrue(all(TEXT[lang][key].strip() for lang in TEXT for key in TEXT[lang]))

    def test_errors_do_not_turn_into_success(self):
        for code in ('unsupported', 'transport', 'sim_not_ready', 'reconnect_failed', 'internal_error'):
            self.assertIn(error_key(code), TEXT['en'])
            self.assertNotIn(error_key(code), ('ready', 'configured', 'restored', 'demo_done'))

    def test_fallback_language(self):
        self.assertEqual(tr('other', 'setup'), TEXT['en']['setup'])

    def test_every_core_error_is_explicitly_localized(self):
        import ast
        from pathlib import Path
        core = ast.parse((Path(__file__).parents[1] / 'src/dongle_go/core.py').read_text())
        codes = {n.args[0].value for n in ast.walk(core) if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Name) and n.func.id == 'CoreError'
                 and n.args and isinstance(n.args[0], ast.Constant)}
        self.assertFalse(codes - ERROR_KEYS.keys())
        for code in codes:
            self.assertIn(error_key(code), TEXT['en'])
        self.assertNotEqual(error_key('snapshot_failed'), error_key('no_snapshot'))
        self.assertNotEqual(error_key('invalid_snapshot'), error_key('no_snapshot'))
