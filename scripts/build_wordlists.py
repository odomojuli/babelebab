#!/usr/bin/env python3
"""Generate frequency-ranked wordlists for the project's priority languages.

Source: the offline ``wordfreq`` library (no network at run time). For each of
the top-30 languages in ``top-lang/ethnologue-2024-top30-info.csv`` that
wordfreq genuinely covers, this writes::

    word-lists/<iso3>/<iso3>_wordfreq_top<N>.csv

with columns ``rank,word,freq_per_million,zipf``.

Languages wordfreq does not cover are skipped on purpose: wordfreq otherwise
silently falls back to a *different* language's data (e.g. English for Telugu),
which would ship mislabeled lists. Skips are reported at the end.

Usage:
    python scripts/build_wordlists.py [--top-n 5000]

Requires the optional extra:  pip install "babelebab[wordlists]"
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TOP_LANG_CSV = REPO_ROOT / "top-lang" / "ethnologue-2024-top30-info.csv"
OUT_ROOT = REPO_ROOT / "word-lists"

# wordfreq 2-letter code -> ISO 639-3 directory/file name.
ISO3 = {
    "zh": "zho", "es": "spa", "en": "eng", "hi": "hin", "bn": "ben",
    "pt": "por", "ru": "rus", "ja": "jpn", "vi": "vie", "tr": "tur",
    "ko": "kor", "ta": "tam", "ar": "ara", "de": "deu", "fr": "fra",
    "ur": "urd", "it": "ita", "fa": "fas",
}


def read_top_languages(path: Path) -> list[tuple[str, str]]:
    """Return ``[(language_name, iso639_1), ...]`` from the Ethnologue top-30 CSV."""
    rows: list[tuple[str, str]] = []
    with path.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            name = (row.get("Language") or "").strip()
            iso1 = (row.get("ISO-639-1") or "").strip()
            if name:
                rows.append((name, iso1))
    return rows


def build(top_n: int) -> None:
    try:
        from wordfreq import (
            available_languages,
            top_n_list,
            word_frequency,
            zipf_frequency,
        )
    except ImportError:
        sys.exit('wordfreq not installed. Run: pip install "babelebab[wordlists]"')

    covered = set(available_languages())
    written: list[tuple[str, str, int]] = []
    skipped: list[tuple[str, str]] = []
    seen: set[str] = set()

    for name, iso1 in read_top_languages(TOP_LANG_CSV):
        if iso1 not in covered:
            skipped.append((name, "not in wordfreq"))
            continue
        if iso1 in seen:
            skipped.append((name, f"already covered by '{iso1}'"))
            continue
        iso3 = ISO3.get(iso1, iso1)
        try:
            words = top_n_list(iso1, top_n)
        except Exception as exc:  # e.g. missing CJK tokenizer
            skipped.append((name, f"{iso1}: {type(exc).__name__}"))
            continue
        seen.add(iso1)
        out_dir = OUT_ROOT / iso3
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{iso3}_wordfreq_top{top_n}.csv"
        with out_path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(["rank", "word", "freq_per_million", "zipf"])
            for rank, word in enumerate(words, start=1):
                fpm = round(word_frequency(word, iso1) * 1_000_000, 4)
                writer.writerow([rank, word, fpm, round(zipf_frequency(word, iso1), 2)])
        written.append((name, iso3, len(words)))
        print(f"  {iso3}  {name:<22} {len(words):>5} words -> {out_path.relative_to(REPO_ROOT)}")

    print(f"\nWrote {len(written)} wordlists; skipped {len(skipped)}.")
    for name, why in skipped:
        print(f"  skip {name}: {why}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build frequency wordlists via wordfreq.")
    parser.add_argument("--top-n", type=int, default=5000, help="Words per language (default 5000).")
    build(parser.parse_args().top_n)


if __name__ == "__main__":
    main()
