#!/usr/bin/env python3
"""Generate frequency wordlists for languages wordfreq does not cover, from the
Leipzig Corpora Collection (https://wortschatz.uni-leipzig.de, CC BY).

See docs/specs/0001-multilingual-wordlist-gapfill.md.

Input: Leipzig per-corpus packages -- either the ``*.tar.gz`` or an extracted
``*-words.txt`` (tab-separated: rank, word, frequency). Output matches the
wordfreq lists exactly::

    word-lists/<iso3>/<iso3>_leipzig_top<N>.csv   (rank,word,freq_per_million,zipf)

No network is needed at run time. Download corpora once from
https://wortschatz.uni-leipzig.de/en/download/<Language> and point --input here.

Usage:
    python scripts/build_wordlists_leipzig.py --input <dir-or-file> [--top-n 5000] [--iso3 tel]
"""
from __future__ import annotations

import argparse
import csv
import math
import sys
import tarfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_ROOT = REPO_ROOT / "word-lists"

# Leipzig filename prefix -> ISO 639-3 (the gaps from spec 0001).
PREFIX_ISO3 = {
    "tel": "tel", "mar": "mar", "guj": "guj", "hau": "hau", "jav": "jav",
    "pnb": "pnb", "pan": "pnb", "bho": "bho", "yue": "yue", "wuu": "wuu",
    "nan": "nan", "apc": "apc",
}

CITATION = (
    "Leipzig Corpora Collection (https://wortschatz.uni-leipzig.de), CC BY. "
    "Cite: Goldhahn, Eckart & Quasthoff, LREC 2012."
)


def parse_words_text(text: str) -> list[tuple[str, int]]:
    """Parse Leipzig ``*-words.txt`` content into ``[(word, count), ...]``."""
    out: list[tuple[str, int]] = []
    for line in text.splitlines():
        parts = line.split("\t") if "\t" in line else line.split()
        if len(parts) < 2:
            continue
        try:
            count = int(parts[-1])  # last field is the frequency
        except ValueError:
            continue
        word = parts[-2].strip()  # the field before the frequency
        if word:
            out.append((word, count))
    return out


def load_input(path: Path) -> str:
    """Return the ``*-words.txt`` content from a ``.tar.gz`` or a plain text file."""
    if path.suffixes[-2:] == [".tar", ".gz"] or path.suffix in {".tgz", ".gz"}:
        with tarfile.open(path, "r:gz") as tar:
            member = next(
                (m for m in tar.getmembers() if m.name.endswith("-words.txt")), None
            )
            if member is None:
                raise ValueError(f"no *-words.txt inside {path.name}")
            handle = tar.extractfile(member)
            if handle is None:
                raise ValueError(f"could not read member from {path.name}")
            return handle.read().decode("utf-8")
    return path.read_text(encoding="utf-8")


def iso3_for(path: Path, override: str | None) -> str | None:
    if override:
        return override
    prefix = path.name.split("_", 1)[0].lower()
    return PREFIX_ISO3.get(prefix)


def to_rows(pairs: list[tuple[str, int]], top_n: int) -> list[tuple[int, str, float, float]]:
    """Convert ``(word, count)`` pairs to ``(rank, word, freq_per_million, zipf)``."""
    total = sum(c for _, c in pairs)
    ranked = sorted(pairs, key=lambda wc: wc[1], reverse=True)[:top_n]
    rows: list[tuple[int, str, float, float]] = []
    for rank, (word, count) in enumerate(ranked, start=1):
        fpm = count / total * 1_000_000
        zipf = round(math.log10(fpm) + 3, 2) if fpm > 0 else 0.0
        rows.append((rank, word, round(fpm, 4), zipf))
    return rows


def convert(path: Path, top_n: int, iso3: str | None) -> str | None:
    code = iso3_for(path, iso3)
    if code is None:
        print(f"  ! cannot infer iso3 for {path.name}; pass --iso3", file=sys.stderr)
        return None
    pairs = parse_words_text(load_input(path))
    if not pairs:
        print(f"  ! no rows parsed from {path.name}", file=sys.stderr)
        return None
    rows = to_rows(pairs, top_n)
    out_dir = OUT_ROOT / code
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{code}_leipzig_top{top_n}.csv"
    with out_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["rank", "word", "freq_per_million", "zipf"])
        writer.writerows(rows)
    print(f"  {code}  {len(rows):>5} words -> {out_path.relative_to(REPO_ROOT)}")
    return code


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Leipzig-based frequency wordlists.")
    parser.add_argument("--input", required=True, help="A *-words.txt / *.tar.gz, or a directory of them.")
    parser.add_argument("--top-n", type=int, default=5000)
    parser.add_argument("--iso3", default=None, help="Override ISO 639-3 (single input file).")
    args = parser.parse_args()

    root = Path(args.input)
    if root.is_dir():
        inputs = sorted(
            p for p in root.iterdir()
            if p.name.endswith("-words.txt") or p.name.endswith((".tar.gz", ".tgz"))
        )
    else:
        inputs = [root]
    if not inputs:
        sys.exit(f"no Leipzig inputs found in {root}")

    done = sum(1 for p in inputs if convert(p, args.top_n, args.iso3) is not None)
    print(f"\nWrote {done} wordlist(s). Source: {CITATION}")


if __name__ == "__main__":
    main()
