# Spec 0003 — Lemmatization in the analyze stage

- **Status:** Implemented
- **Date:** 2026-06-01
- **Related:** `docs/specs/0002-analyze-lexicon-stage.md`, `src/babelebab/analyze/`

## 1. Problem

The analyze stage looks up *surface* word forms, so inflections miss the
wordlist and count as "unknown" (`jumps`, `mice`, `running`), understating
coverage and bloating the unknown/rare sets. We want to resolve surface forms to
their lemma before declaring a miss — staying local and light.

## 2. Goals / non-goals

**Goals:** surface→lemma resolution for supported languages; higher, truer
coverage; offline; optional dependency with a graceful no-op fallback; testable
without the dependency (via injection).

**Non-goals:** lemmatization for unsupported languages (no-op); POS-aware
disambiguation; stemming; changing the wordlists.

## 3. Source decision

**simplemma 1.2.0** — pure-Python, data bundled in the wheel (offline, ~65 MB
installed), supports **10 of our 18** languages: eng, spa, fra, deu, ita, por,
rus, tur, fas, hin. The other 8 (ara, jpn, kor, vie, tam, ben, urd, zho) no-op.

| Option | Multilingual (our set) | Offline | Weight |
|---|---|---|---|
| **simplemma** | 10/18 | yes (bundled) | ~65 MB, optional |
| spaCy | broad | per-model downloads | heavy |
| NLTK WordNet | English only | data download | light-ish |
| stanza | broad | model downloads + torch | heavy |

Chosen: simplemma — best local + light + multilingual fit; kept as an opt-in
`[lemmatize]` extra.

## 4. Specification

- `Lemmatizer.__call__(word, lang_iso3) -> str`: the lemma for supported
  languages, else the word unchanged (also unchanged if simplemma is missing or
  errors — always safe to call).
- `simplemma_available() -> bool`.
- `analyze(..., lemmatize: bool = True, lemmatizer: Callable[[str, str], str] | None = None)`.
  Resolution: explicit `lemmatizer` → else the default if `lemmatize` → else off.
- Per-token lookup order: surface form; on a miss (with lemmatization on), the
  lemma. On a lemma hit, `TokenInfo.lemma` records it and the token counts as
  known.
- `TokenInfo` gains `lemma: str | None` (set only when matched via the lemma).

## 5. Approach & rationale

- Lazy import; lemmatize **only on a surface miss** (cheap; clear semantics).
- Dependency injection (`lemmatizer=`) makes the integration deterministically
  testable without simplemma installed.
- An ISO 639-3 → simplemma-code map gates calls to known-supported languages.

## 6. Risks / limitations

- 65 MB optional dependency (not committed; opt-in via extra).
- Over-lemmatization can shift sense (`better` → `good`); acceptable for a
  frequency-coverage metric, flagged for callers.
- 8 languages unsupported (no-op) — documented; revisit with another lemmatizer
  if needed.

## 7. Validation

- Injected-stub tests (deterministic, no simplemma) over a synthetic lexicon: a
  lemma resolves a surface miss; `lemmatize=False` leaves it unknown.
- `@skipUnless` real-simplemma test: `jumps → jump`, `mice → mouse`.
- ruff + mypy clean; full suite green; demo showing coverage rise.
