# Development

## Requirements

Python 3.10+ and Tcl/Tk 8.6+. The core and CLI use only the standard library; the desktop uses `tkinter`. Python's Windows installer includes Tk; Linux distributions may need their `python3-tk` package. No browser, server, Electron runtime, or NLP corpus is involved.

```sh
python stringanalyzer.py
python -m unittest discover -s tests -v
```

For desktop integration tests on Windows PowerShell:

```powershell
$env:STRING_ANALYZER_UI_TESTS = '1'
python -m unittest discover -s tests -v
```

Desktop tests create real Tk windows and verify live results, rapid edit handling, undo/search, exports, and minimum-size layout. Core tests cover empty input, Unicode, filters, phrases, metrics, limits, formats, and CLI file/stdin/error paths. Live MySQL and Kafka connections require separately configured services and are not covered by these tests.

## Layout

| File | Responsibility |
| --- | --- |
| `analyzer/core.py` | Deterministic analysis, text transformations, report serialization |
| `analyzer/ui.py` | Tk UI, debounced worker analysis, charts, dialogs |
| `analyzer/cli.py` | Argument parsing, bounded UTF-8 input, CLI errors |
| `stringanalyzer.py` | Entry point |
| `stringanalyzer-mysql.py` | Optional streaming database adapter |
| `stringanalyzer-apache-kafka.py` | Optional bounded Kafka consumer |

Live analysis waits 400 ms after edits and runs on a single background worker. Tk updates remain on the UI thread. Generation checks discard stale results; export takes a fresh snapshot. Input is capped at 2 million characters. Memory and time scale with input and distinct words/phrases; the cap is not a memory guarantee.

## Portable Windows build

Build on Windows; PyInstaller does not cross-compile Windows executables from another OS.

```powershell
python -m pip install -r requirements-build.txt
python -m PyInstaller --clean --noconfirm --onefile --windowed --name StringAnalyzer stringanalyzer.py
```

The output is `dist/StringAnalyzer.exe`. It bundles Python and Tk, so users do not need Python installed. The single-file launcher extracts its runtime to a temporary directory on startup. The app does not persist user text or settings. Build from a clean virtual environment for reproducibility and minimal dependencies. The EXE is unsigned.

GitHub Actions tests Python 3.10, 3.12, and 3.13 on Windows, macOS, and Linux, then separately builds a Windows artifact. Download the artifact from a successful run; this repository does not automatically publish releases. Preview images in `docs/images` are captures of the actual desktop app.
