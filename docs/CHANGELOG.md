# v2.0.0

- Rebuilt the hard-coded sample scripts as a reusable standard-library engine, offline Tk desktop app, and CLI.
- Added Unicode-aware counts, sentence/paragraph metrics, reading time, lexical diversity, character entropy, bigrams, and trigrams.
- Added a frequency table, word cloud, literal search, nine undoable text transformations, UTF-8 file input, and JSON/CSV/text reports.
- Removed runtime NLTK downloads and required wordcloud/NLTK packages. Tone now uses a documented English word-list heuristic, rather than VADER. The cloud is drawn in the UI rather than automatically writing a PNG.
- Fixed empty-input crashes, punctuation counts that previously included spaces and digits, and the overwritten word-count variable.
- Replaced MySQL credential placeholders and the unfinished Storm/Kafka spout with optional command-line adapters sharing the engine.
- Added core/CLI and desktop tests, a portable Windows build workflow, and usage/development documentation.

The program no longer writes `output.txt` or `wordcloud.png` on launch. Export reports explicitly. Original script filenames remain available; MySQL and Kafka now accept command-line configuration.
