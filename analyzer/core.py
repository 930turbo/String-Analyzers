"""Shared analysis, transformations and exports for desktop and CLI."""
import csv
import io
import json
import math
import re
import unicodedata
from collections import Counter

STOPWORDS = frozenset("a an and are as at be been but by for from had has have he her his i in is it its me my not of on or our she that the their them there these they this to was we were will with you your".split())
POSITIVE = frozenset("amazing awesome beautiful best brilliant enjoy excellent fantastic fun good great happy helpful hope kind love lovely perfect success wonderful".split())
NEGATIVE = frozenset("angry awful bad broken cruel disappointing disaster fail failure fear hate horrible hurt poor sad terrible ugly unhappy useless worse worst".split())
WORD = re.compile(r"[^\W_]+(?:['’][^\W_]+)*", re.UNICODE)
MAX_CHARS = 2_000_000


def analyze(text, *, exclude_stopwords=False, case_sensitive=False):
    if len(text) > MAX_CHARS:
        raise ValueError(f"Text is limited to {MAX_CHARS:,} characters per analysis.")
    tokens = WORD.findall(text)
    normalized = [t if case_sensitive else t.casefold() for t in tokens]
    selected = [t for t in normalized if not exclude_stopwords or t.casefold() not in STOPWORDS]
    frequencies = Counter(selected)
    letters = Counter(c if case_sensitive else c.casefold() for c in text if c.isalpha())
    punctuation = Counter(c for c in text if unicodedata.category(c).startswith("P"))
    sentences = sum(bool(WORD.search(s)) for s in re.split(r"[.!?]+|\n", text))
    lower = [t.casefold() for t in tokens]
    positive, negative = sum(t in POSITIVE for t in lower), sum(t in NEGATIVE for t in lower)
    score = (positive - negative) / max(1, positive + negative)
    counts = Counter(text)
    entropy = -sum((n / len(text)) * math.log2(n / len(text)) for n in counts.values()) if text else 0
    bigrams = Counter(" ".join(normalized[i:i+2]) for i in range(len(normalized)-1))
    trigrams = Counter(" ".join(normalized[i:i+3]) for i in range(len(normalized)-2))
    return {
        "characters": len(text), "characters_no_whitespace": sum(not c.isspace() for c in text),
        "utf8_bytes": len(text.encode("utf-8")), "words": len(tokens), "analyzed_words": len(selected),
        "unique_words": len(frequencies), "sentences": sentences,
        "lines": len(text.splitlines()) if text else 0,
        "paragraphs": len(re.split(r"\n\s*\n", text.strip())) if text.strip() else 0,
        "digits": sum(c.isdigit() for c in text), "whitespace": sum(c.isspace() for c in text),
        "average_word_length": round(sum(map(len, tokens)) / max(1, len(tokens)), 2),
        "lexical_diversity": round(len(frequencies) / max(1, len(selected)) * 100, 2),
        "reading_seconds": math.ceil(len(tokens) / 238 * 60), "entropy_bits": round(entropy, 3),
        "sentiment": {"label": "Positive" if score > 0 else "Negative" if score < 0 else "Neutral",
                      "score": round(score, 3), "positive_hits": positive, "negative_hits": negative},
        "word_frequency": dict(frequencies.most_common()), "letter_frequency": dict(letters.most_common()),
        "punctuation_frequency": dict(punctuation.most_common()), "bigrams": dict(bigrams.most_common()),
        "trigrams": dict(trigrams.most_common()),
        "options": {"exclude_stopwords": exclude_stopwords, "case_sensitive": case_sensitive},
    }


def transform(text, operation):
    if operation == "Lowercase": return text.lower()
    if operation == "Uppercase": return text.upper()
    if operation == "Title case": return text.title()
    if operation == "Trim lines": return "\n".join(line.strip() for line in text.splitlines())
    if operation == "Collapse spaces": return re.sub(r"[^\S\n]+", " ", text)
    if operation == "Remove blank lines": return "\n".join(line for line in text.splitlines() if line.strip())
    if operation == "Deduplicate lines": return "\n".join(dict.fromkeys(text.splitlines()))
    if operation == "Sort lines": return "\n".join(sorted(text.splitlines(), key=str.casefold))
    if operation == "Normalize Unicode": return unicodedata.normalize("NFC", text)
    raise ValueError(f"Unknown operation: {operation}")


def export_report(result, kind="json"):
    if kind == "json": return json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if kind == "csv":
        stream = io.StringIO(newline="")
        writer = csv.writer(stream)
        writer.writerow(["section", "item", "value"])
        for key, value in result.items():
            for item, count in (value.items() if isinstance(value, dict) else [("", value)]):
                safe = "'" + str(item) if str(item).startswith(("=", "+", "-", "@", "\t", "\r")) else item
                writer.writerow([key, safe, count])
        return stream.getvalue()
    if kind == "txt":
        return "String Analyzer report\n" + "\n".join(f"{k.replace('_', ' ').title()}: {v}" for k, v in result.items()) + "\n"
    raise ValueError(f"Unknown format: {kind}")
