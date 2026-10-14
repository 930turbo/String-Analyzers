# Usage

## Desktop

Launch `python stringanalyzer.py` or the portable Windows EXE. Paste text, use **Sample**, or choose **Open file**. UTF-8 and UTF-8 BOM files are supported; other encodings should be converted before opening. Opening a file replaces the editor text; Undo restores it.

The four cards show total words, Unicode code points, unique analyzed words, and reading time at 238 words/minute. Tabs provide detailed statistics, frequency tables, a word cloud, and literal case-insensitive search. Frequency tables show the top 500 entries; reports contain all entries. The cloud displays up to 40 words as space allows. Long words are shortened visually.

**Hide English stop words** affects word frequencies, the cloud, unique-word counts, and lexical diversity. **Match case** separates word and letter counts. Neither changes total words, sentiment, or the source text. Phrase counts use adjacent original tokens, including stop words, and may span sentence boundaries.

Choose a cleanup operation and click **Apply**. Transformations replace the editor contents and can be undone. Changes to the text clear search highlights; search again to refresh them.

| Shortcut | Action |
| --- | --- |
| Ctrl+O | Open a file |
| Ctrl+S | Export a report |
| Ctrl+Enter | Analyze immediately |
| Ctrl+Z | Undo an editor change |

Choose an export extension of `.json`, `.csv`, or `.txt`. Export analyzes the current editor contents even if a live update is still pending. Files are only written when you explicitly export. Reports include statistics, all frequency distributions, filter options, and the tone score; they do not include the original text verbatim, but frequencies can still disclose content.

## Command line

```sh
python stringanalyzer.py --text "Good tools make good ideas." --format json
python stringanalyzer.py --file notes.txt --exclude-stopwords --output report.json
python stringanalyzer.py --file notes.txt --case-sensitive --format csv --output report.csv
```

Use `--stdin` to read a pipe. `--text`, `--file`, and `--stdin` are mutually exclusive. A missing input option launches the GUI. Run `--help` for all options. Errors return exit status 2. The GUI EXE has no console; use Python source for CLI workflows.

## How counts work

- A word is a Unicode letter/number run, optionally joined by straight or curly apostrophes. Numbers count as words. Hyphens and underscores separate tokens; emoji do not count as words. This is not language-specific segmentation for languages without spaces.
- Characters are Unicode code points, not grapheme clusters. UTF-8 bytes are counted separately. Canonically equivalent Unicode text is only merged after applying **Normalize Unicode**.
- Punctuation uses Unicode punctuation categories; whitespace, math symbols, and emoji are excluded. Letters use Unicode alphabetic classification; case-insensitive counts use case folding.
- A sentence is a word-containing segment separated by `.`, `!`, `?`, or a newline. Abbreviations and decimals can split sentences. Paragraphs are separated by blank lines. Lines follow Python `splitlines()`; a trailing newline adds no empty line.
- Lexical diversity is unique analyzed words divided by analyzed words. Shannon entropy measures the distribution of raw characters, in bits/character; it is not a security rating.
- Tone counts a small built-in English positive/negative vocabulary and uses `(positive - negative) / (positive + negative)`, or zero without hits. It does not understand negation, sarcasm, or context. It replaces the former NLTK/VADER dependency and is not comparable to a VADER score.

## Optional data adapters

These scripts require separately installed clients and an existing configured service. They emit one JSON object per line to standard output and use the same core engine. They are not included in the portable desktop EXE.

```sh
pip install mysql-connector-python
python stringanalyzer-mysql.py --host localhost --user reader --database notes --query "SELECT body FROM notes"

pip install kafka-python
python stringanalyzer-apache-kafka.py --topic notes --bootstrap-servers localhost:9092 --max-messages 100
```

MySQL prompts for a password or reads `STRING_ANALYZER_MYSQL_PASSWORD`. Use a read-only account; the initial SELECT check is a convenience, not SQL authorization. The first result column must be text or NULL. Results stream row by row and resources close on failure.

Kafka consumes UTF-8 messages, stops after the requested message count or an idle timeout (default 10 seconds), and skips malformed/oversized values with a diagnostic on stderr. It disables automatic offset commits, so analysis does not acknowledge messages for a production consumer. Use a dedicated group. Adapter connection/authentication errors propagate to the terminal. Advanced TLS/SASL configuration requires extending the client configuration in the adapter.
