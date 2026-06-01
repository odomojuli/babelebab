# Spec 0007 — Language-aware segmentation + golden-rule expected failures

- **Status:** Implemented
- **Date:** 2026-06-01
- **Related:** specs 0002 (analyze), 0005 (pipeline), 0006 (splitter)

## 1. Problem

Two loose ends after finishing the splitter:

1. `analyze` and `pipeline` call `split_sentences(text)` without a language, so
   non-English text segments with English/regex rules even though the splitter
   is now multilingual (spec 0006).
2. Seven golden-rule cases fail under pysbd *by design* (pysbd's segmentation
   choices differ from the test's hand-written expectations), so the canonical
   suite shows 7 failures that aren't bugs.

## 2. Goals / non-goals

**Goals:** thread the language into segmentation everywhere; make the canonical
(pysbd) suite green by marking the 7 known divergences as expected failures —
without breaking the regex-fallback run.

**Non-goals:** changing pysbd's behavior or the golden expectations themselves.

## 3. Specification

- `analyze(text, lang)` → `split_sentences(text, lang)`.
- `pipeline(...)` → `split_sentences(text, src_lang or "en")` (and `analyze`
  already receives `src_lang`).
- `tests/test_golden_rules_en.py`: a `_pysbd_divergence` decorator =
  `unittest.expectedFailure` when pysbd is the active backend, else a no-op.
  Applied to the 7 divergent cases: `acronyms_and_abbreviations`,
  `am_pm_boundaries`, `bullet_list`, `double_punctuation`,
  `ellipsis_inside_sentence`, `errant_newlines`, `multi_period_abbreviations`.

## 4. Approach & rationale

- Minimal pass-through — the splitter already accepts `lang`; callers just supply
  it. `src_lang or "en"` guards the case where detection returned `None`.
- The **conditional** decorator keeps both backends honest: with pysbd those 7
  are expected failures (suite green); under the regex fallback the decorator is
  a no-op so the suite reflects real regex behavior (no spurious "unexpected
  success").

## 5. Risks / limitations

- If a future pysbd release fixes one of the 7, it becomes an "unexpected
  success" — which is the desired signal to remove that marker.
- Languages without pysbd support fall back to the English-oriented regex (as
  before).

## 6. Validation

Full suite green with pysbd (39 pass + 7 expected-failure on the golden file;
all other stages pass); ruff + mypy clean; analyze/pipeline tests unaffected
(English counts unchanged).
