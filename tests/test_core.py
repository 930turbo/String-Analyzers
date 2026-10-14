import csv
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from analyzer.core import MAX_CHARS, analyze, export_report, transform


class AnalysisTests(unittest.TestCase):
    def test_empty_and_punctuation(self):
        r = analyze("")
        self.assertEqual(r["words"], 0)
        self.assertEqual(r["sentences"], 0)
        self.assertEqual(r["entropy_bits"], 0)
        r = analyze(" !!! 123\n")
        self.assertEqual(r["punctuation_frequency"], {"!": 3})
        self.assertEqual(r["digits"], 3)
        self.assertEqual(r["letter_frequency"], {})

    def test_unicode_and_apostrophes(self):
        r = analyze("Café café don't don’t 你好 😀")
        self.assertEqual(r["words"], 5)
        self.assertEqual(r["word_frequency"]["café"], 2)
        self.assertGreater(r["utf8_bytes"], r["characters"])

    def test_filters_keep_totals(self):
        r = analyze("The the cat Cat!", exclude_stopwords=True, case_sensitive=True)
        self.assertEqual(r["words"], 4)
        self.assertEqual(r["analyzed_words"], 2)
        self.assertEqual(r["word_frequency"], {"cat": 1, "Cat": 1})
        self.assertEqual(r["punctuation_frequency"], {"!": 1})
        self.assertEqual(analyze("the and", exclude_stopwords=True)["unique_words"], 0)

    def test_phrases_and_metrics(self):
        r = analyze("One two one two.\n\nGood!")
        self.assertEqual(r["bigrams"]["one two"], 2)
        self.assertEqual(r["sentences"], 2)
        self.assertEqual(r["paragraphs"], 2)
        self.assertEqual(r["sentiment"]["label"], "Positive")
        self.assertEqual(analyze("aa")["entropy_bits"], 0)
        self.assertEqual(analyze("ab")["entropy_bits"], 1)

    def test_transforms(self):
        self.assertEqual(transform(" a  b\n\n a  b", "Collapse spaces"), " a b\n\n a b")
        self.assertEqual(transform("a\nb\na", "Deduplicate lines"), "a\nb")
        self.assertEqual(transform("e\u0301", "Normalize Unicode"), "é")
        self.assertEqual(transform(" x \n y ", "Trim lines"), "x\ny")
        with self.assertRaises(ValueError): transform("", "unknown")

    def test_limits(self):
        with self.assertRaises(ValueError): analyze("x" * (MAX_CHARS + 1))

    def test_exports(self):
        r = analyze("café café!")
        self.assertEqual(json.loads(export_report(r)), r)
        rows = list(csv.reader(io.StringIO(export_report(r, "csv"))))
        self.assertIn(["word_frequency", "café", "2"], rows)
        self.assertIn("String Analyzer", export_report(r, "txt"))
        self.assertIn("'=", export_report({"punctuation_frequency": {"=": 1}}, "csv"))
        with self.assertRaises(ValueError): export_report(r, "invalid")

    def test_cli_file_stdin_errors(self):
        with tempfile.TemporaryDirectory() as folder:
            source, output = Path(folder)/"input.txt", Path(folder)/"out.json"
            source.write_text("\ufeffHello hello", encoding="utf-8")
            result = subprocess.run([sys.executable, "stringanalyzer.py", "--file", str(source), "--output", str(output)], capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(output.read_text())["words"], 2)
        result = subprocess.run([sys.executable, "stringanalyzer.py", "--stdin"], input="test test", text=True, capture_output=True)
        self.assertEqual(json.loads(result.stdout)["words"], 2)
        result = subprocess.run([sys.executable, "stringanalyzer.py", "--file", "missing.txt"], capture_output=True)
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__": unittest.main()
