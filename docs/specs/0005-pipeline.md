# Spec 0005 — End-to-end pipeline

- **Status:** Implemented
- **Date:** 2026-06-01
- **Related:** specs 0002 (analyze), 0003 (lemmatize), 0004 (detect); `segmentation`, `translate`

## 1. Problem

The four stages — detect, segment, analyze, translate — work in isolation. We
want one entry point that composes them into a single structured result, while
keeping each step optional and the stages independently usable.

## 2. Goals / non-goals

**Goals:** one `pipeline(text)` running detect → segment → analyze, with optional
translation; each step guarded/optional; a structured `PipelineResult`; reuse
the existing stages unchanged; dependency-injectable (detector, lexicon, engine)
for testing and flexibility; pure-local (translation only runs when the caller
supplies an `Engine`).

**Non-goals:** choosing or downloading translation models (the caller provides
the engine); recomposition beyond joining sentences; concurrency/batching.

## 3. Specification

### 3.1 Signature
```
pipeline(text, *, src_lang=None, detector=None, analyze_text=True,
         lexicon=None, translate_to=None, engine=None) -> PipelineResult
```

### 3.2 Control flow
1. **Detect** — if `src_lang` is None, run `detector` (or the default
   `detect`); set `src_lang` from the result. Otherwise skip detection.
2. **Segment** — `split_sentences(text)` (empty for blank input).
3. **Analyze** — if `analyze_text` and a `src_lang` is known, run `analyze`;
   a missing wordlist (`FileNotFoundError`) yields `analysis=None` rather than
   raising.
4. **Translate** — only when both `translate_to` and `engine` are given:
   translate each sentence via the engine; `translated_text` is the joined
   output.

### 3.3 `PipelineResult`
`text`, `src_lang: str|None`, `detection: DetectionResult|None`,
`sentences: list[str]`, `analysis: AnalysisResult|None`,
`tgt_lang: str|None`, `translations: list[TranslationResult]`,
`translated_text: str|None`; plus `summary() -> str`.

### 3.4 Top-level API
Re-export `pipeline`, `PipelineResult`, and the stage callables `detect`,
`analyze`, `split_sentences` from the `babelebab` package root.

## 4. Approach & rationale

- A **thin orchestrator** — no new logic, just composition — so each stage stays
  the source of truth and independently testable.
- **Dependency injection** (detector/lexicon/engine) keeps it deterministically
  testable (e.g. translate with `IdentityEngine`) and lets callers plug in a real
  CTranslate2 engine without changes here.
- **Translation per sentence** matches the segmentation granularity and the
  engine interface.

## 5. Risks / limitations

- A wrong detection feeds the wrong language to analyze; mitigated by the
  `src_lang` override.
- Real translation depends on the engine supplied (replay = top-1k words;
  CTranslate2 = needs a local model); the pipeline itself stays engine-agnostic.
- Per-sentence translation is sequential (fine for now).

## 6. Validation

Tests: detect+analyze on clear English; `src_lang` override skips detection;
translation wired via `IdentityEngine`; missing-wordlist → `analysis=None`;
`import babelebab` smoke (no circular imports). ruff + mypy clean; full suite.
