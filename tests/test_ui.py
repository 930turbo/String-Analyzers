"""Run explicitly with STRING_ANALYZER_UI_TESTS=1 on a display-equipped machine."""
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch


@unittest.skipUnless(os.environ.get('STRING_ANALYZER_UI_TESTS') == '1', 'Desktop tests are opt-in')
class DesktopTests(unittest.TestCase):
    def setUp(self):
        import tkinter as tk
        from analyzer.ui import App
        self.root = tk.Tk()
        self.app = App(self.root)
        self.root.update()

    def tearDown(self):
        self.app.close()

    def wait_analysis(self):
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            self.root.update()
            if self.app.pending is None and self.app.future and self.app.future.done() and self.app.status.cget('text').startswith('Up to date'):
                return
            time.sleep(.01)
        self.fail('Analysis did not finish')

    def test_live_update_and_latest_generation(self):
        self.app.set_text('old')
        self.app.schedule(0)
        self.root.update()
        self.app.set_text('new new latest')
        self.wait_analysis()
        self.assertEqual(self.app.result['words'], 3)
        self.assertEqual(self.app.metrics['words'].cget('text'), '3')
        self.assertEqual(len(self.app.table.get_children()), 2)

    def test_cleanup_undo_and_find(self):
        self.app.set_text('Hello HELLO 😀')
        self.app.editor.edit_reset()
        self.app.query.insert(0, 'hello')
        self.app.find()
        self.assertEqual(len(self.app.editor.tag_ranges('match')), 4)
        self.app.operation.set('Uppercase')
        self.app.apply()
        self.assertEqual(self.app.text(), 'HELLO HELLO 😀')
        self.app.undo()
        self.assertEqual(self.app.text(), 'Hello HELLO 😀')

    def test_export_uses_current_text(self):
        self.app.set_text('one two three')
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder) / 'report.json')
            with patch('analyzer.ui.filedialog.asksaveasfilename', return_value=path):
                self.app.export()
            import json
            self.assertEqual(json.loads(Path(path).read_text())['words'], 3)

    def test_minimum_layout_and_tabs(self):
        self.root.geometry('980x700')
        self.root.update()
        self.assertLess(self.app.operation.winfo_rooty() + self.app.operation.winfo_height(), self.root.winfo_rooty() + self.root.winfo_height())
        self.assertLess(self.app.status.winfo_rooty() + self.app.status.winfo_height(), self.root.winfo_rooty() + self.root.winfo_height())
        self.app.set_text('sample words sample')
        self.wait_analysis()
        for tab in range(4):
            self.app.notebook.select(tab)
            self.root.update()
        self.assertTrue(self.app.cloud.find_all())


if __name__ == '__main__': unittest.main()
