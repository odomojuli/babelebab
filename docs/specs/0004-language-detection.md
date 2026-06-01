# Spec 0004 — Language detection (detect stage)

- **Status:** Implemented
- **Date:** 2026-06-01
- **Related:** `word-lists/`, `src/babelebab/analyze/lexicon.py` (the pipeline's stage 1)

## 1. Problem

The pipeline's front door is missing: given arbitrary text we must identify its
language before segmenting / analyzing / translating. It has to stay local and
add no heavy downloads.

## 2. Goals / non-goals

**Goals:** identify language for the 18 languages we have wordlists for;
pure-local, zero new runtime dependencies; a pluggable `Detector` interface (so
a library backend can be added later); return confidence + per-language scores.

**Non-goals:** languages without a wordlist; strong accuracy on very short or
code-mixed text; separating same-script close varieties (ara/fas/urd) — best
effort, documented.

## 3. Options

| Option | Coverage | Offline | New dep |
|---|---|---|---|
| **Wordlist char n-gram (Cavnar–Trenkle)** | our 18 | yes | **none** |
| langid.py | ~97 | yes (bundled) | small |
| langdetect | ~55 | yes | small |
| fastText lid.176 | 176 | model download | download (space) |
| lingua | ~75 | yes | heavier |

**Decision:** the wordlist char n-gram model as the default — zero dependencies,
reuses the data we already built, and covers exactly the languages we support.
The `Detector` interface leaves room for an optional langid/langdetect adapter
later (a `[detect]` extra), deferred for now.

## 4. Algorithm (WordlistDetector)

Classic **Cavnar–Trenkle out-of-place rank distance** over character n-grams
(n = 1–3; word tokens padded with a boundary marker `_`):

- **Per language:** aggregate n-grams across its top-5000 words, weighted by
  `freq_per_million`; keep the 300 most frequent → `{ngram: rank}`.
- **Per input:** the same, from the text's tokens.
- `distance(text, lang) = Σ over the text's n-grams of |rank_text − rank_lang|`
  (a fixed penalty when absent), normalized by the number of text n-grams.
- Detected = minimum distance; `confidence = (d₂ − d₁) / d₂` (margin between the
  two closest languages).

Character n-grams handle non-spaced scripts (CJK) without word segmentation, and
kana vs Han separates Japanese from Chinese.

## 5. API

- `Detector` (ABC): `detect(text) -> DetectionResult`.
- `DetectionResult(lang: str | None, confidence: float, scores: dict[str, float])`
  — `scores` are distances (lower = closer); `lang=None` for empty input.
- `WordlistDetector(langs=None, *, wordlists_root=None)` — discovers languages
  from `word-lists/` when `langs` is omitted; profiles built lazily and cached.
- `detect(text)` — module helper backed by a shared default `WordlistDetector`.

## 6. Risks / limitations

- Only the 18 wordlist languages.
- Short / code-mixed text → low confidence; same-script close languages
  (ara/fas/urd) may confuse.
- Profiles come from frequency lists, not running text, so register differs
  slightly — acceptable for language ID.

## 7. Validation

Empirical run on clear samples (en/fr/es/de/ru/it/pt/tr + a CJK sample) → correct
top language; deterministic unit tests on those; ruff + mypy clean.
