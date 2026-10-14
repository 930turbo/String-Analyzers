import argparse
import sys
from pathlib import Path
from .core import MAX_CHARS, analyze, export_report


def read_text(path):
    with Path(path).open(encoding="utf-8-sig") as stream:
        text = stream.read(MAX_CHARS + 1)
    if len(text) > MAX_CHARS:
        raise ValueError(f"File exceeds {MAX_CHARS:,} characters.")
    return text


def main(argv=None):
    parser = argparse.ArgumentParser(description="Offline text analysis. No arguments opens the desktop app.")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--text", help="Text to analyze")
    source.add_argument("--file", type=Path, help="UTF-8 text file")
    source.add_argument("--stdin", action="store_true", help="Read text from standard input")
    parser.add_argument("--format", choices=["json", "csv", "txt"], default="json")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--exclude-stopwords", action="store_true")
    parser.add_argument("--case-sensitive", action="store_true")
    args = parser.parse_args(argv)
    if args.text is None and args.file is None and not args.stdin:
        from .ui import launch
        launch()
        return 0
    try:
        text = args.text if args.text is not None else read_text(args.file) if args.file else sys.stdin.read(MAX_CHARS + 1)
        report = export_report(analyze(text, exclude_stopwords=args.exclude_stopwords, case_sensitive=args.case_sensitive), args.format)
        if args.output: args.output.write_text(report, encoding="utf-8")
        else: print(report, end="")
    except (OSError, UnicodeError, ValueError) as error:
        parser.exit(2, f"error: {error}\n")
    return 0
