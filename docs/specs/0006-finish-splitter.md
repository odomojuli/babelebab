# Spec 0006 — Finish the sentence splitter

- **Status:** Implemented
- **Date:** 2026-06-01
- **Related:** `src/babelebab/segmentation/`, `tests/test_golden_rules_en.py`

## 1. Problem

`split_sentences` (the regex prototype) passes only **21 of 46** English
Golden-Rule cases. The splitter is the project's namesake "divide" core, but it
mishandles abbreviations (`U.S.`, `Ph.D.`, `Co.` at sentence end), emails/URLs,
quotes, multi-punctuation, and lists. Hand-tuning regex to pass the rest is
fragile, overfit-prone, and English-only.

## 2. Goals / non-goals

**Goals:** a large, honest lift in Golden-Rule pass rate; keep `split_sentences`
backward-compatible; stay local/offline; ideally make segmentation multilingual.

**Non-goals:** hardcoding test strings; guaranteeing 46/46 (a few test
expectations are non-canonical); changing the analyze/pipeline call sites (a
follow-up can make those language-aware).

## 3. Options

| Option | Golden rules | Offline | Multilingual | Cost |
|---|---|---|---|---|
| Extend hand-rolled regex | uncertain, fragile | yes | English only | high effort, overfit risk |
| **pysbd** (pragmatic_segmenter port) | designed to pass them (~98%) | yes | 23 languages | small dep (480 KB) |

**Decision:** pluggable — **pysbd** as the backend when installed (an `[sbd]`
extra), the naive regex as the zero-dependency fallback. This mirrors the
translate (local default + optional engine) and detect (default + optional
library) patterns, and makes segmentation multilingual (pysbd covers en, es, fr,
de, it, ru, ar, fa, hi, ja, zh, ur, mr, …).

## 4. Specification

- `split_sentences(text, lang="en") -> list[str]` — backward compatible (new
  optional `lang`). `lang` accepts ISO 639-1/2 (`"en"`) or ISO 639-3 (`"eng"`),
  normalized to a pysbd code.
- If pysbd is installed and supports the language, use it; otherwise fall back to
  the regex splitter. The pysbd adapter never raises — on any error it returns
  `None` and the caller falls back.
- A `pysbd_segmenter` module: `pysbd_available()`, `pysbd_supports(code)`,
  `pysbd_split(text, code)`; `Segmenter` instances cached per language.
- Results are whitespace-stripped with empties dropped.

## 5. Approach & rationale

- A thin adapter, lazy-imported and cached; the regex prototype stays as the
  zero-dep fallback so behavior is graceful without the extra.
- Reuse the existing public API (`split_sentences`) so analyze/pipeline/detect
  pick up the improvement transparently.

## 6. Risks / limitations

- Without the `[sbd]` extra, behavior is the 21/46 baseline (documented).
- A few Golden-Rule test expectations are non-canonical (e.g. `What?!!` split);
  pysbd won't match those, so the pass rate is high but not 46/46 — reported
  honestly below.
- pysbd uses ISO 639-1/2 codes; an ISO 639-3 map covers the languages we use.

## 7. Validation

Golden-rule suite with pysbd: **39/46** (up from 21/46). The 7 remaining are
cases where pysbd segments differently from the test's hand-written
expectations — it keeps `She said... and then what?` and `What?!! You're joking!`
whole, ignores `•` bullets, splits on the errant newline, and over-splits
`5 a.m.`. These are pysbd design choices; chasing them would mean overfitting to
the test. Full suite: 63/70 (the 7 failures are exactly those golden cases);
ruff + mypy clean.
