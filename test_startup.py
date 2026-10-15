"""Startup contract tests; SDK is mocked, no remote worker or costs."""
import runpy
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

class StartupTests(unittest.TestCase):
    def test_runpod_scanner_canonical_entrypoint(self):
        source = Path('handler.py').read_text()
        self.assertIn('runpod.serverless.start({"handler": handler})', source)

    def test_running_handler_registers_callable_once(self):
        start = Mock()
        sdk = types.SimpleNamespace(serverless=types.SimpleNamespace(start=start))
        with patch.dict(sys.modules, {'runpod': sdk, 'requests': types.ModuleType('requests')}):
            runpy.run_path('handler.py', run_name='__main__')
        start.assert_called_once()
        self.assertTrue(callable(start.call_args.args[0]['handler']))

    def test_import_does_not_start_worker(self):
        start = Mock()
        sdk = types.SimpleNamespace(serverless=types.SimpleNamespace(start=start))
        with patch.dict(sys.modules, {'runpod': sdk, 'requests': types.ModuleType('requests')}):
            runpy.run_path('handler.py', run_name='handler_test_import')
        start.assert_not_called()

if __name__ == '__main__':
    unittest.main()
