# Spec 0002 — Analyze / lexicon stage

- **Status:** Implemented
- **Date:** 2026-06-01
- **Related:** `src/babelebab/segmentation/`, `word-lists/`, spec 0001

## 1. Problem

The pipeline has segmentation (split sentences) and a set of per-language
frequency wordlists, but nothing *consumes* them. We want an **analyze** stage
that takes text + a language and returns lexical insight — per-word frequency
annotation and aggregate coverage/difficulty metrics — fully locally, reusing
the segmenter and the wordlists already in the repo.

## 2. Goals / non-goals

**Goals**

- Annotate each word token with its frequency data (`rank`, `freq_per_million`,
  `zipf`) from the language's wordlist.
- Aggregate metrics: vocabulary coverage at thresholds, type/token ratio, mean
  Zipf, rare and unknown words.
- Reuse `babelebab.segmentation.split_sentences` for sentence structure.
- Pure standard library; no network; works for the 18 wordlist languages.

**Non-goals (documented future work)**

- Word segmentation for non-spaced scripts (zho/jpn/kor need a tokenizer).
- CEFR leveling (possible later for English via `analysis/oxford-cefr/`).
- Lemmatization / stemming.

## 3. Specification

### 3.1 Inputs
`analyze(text: str, lang: str, *, lexicon=None, rare_threshold=3.0,
top_thresholds=(100, 1000, 5000), include_tokens=True)` where `lang` is an
ISO 639-3 code with a wordlist under `word-lists/<lang>/`.

### 3.2 Lexicon
Loaded from `word-lists/<iso3>/<iso3>_wordfreq_top*.csv` (schema
`rank,word,freq_per_million,zipf`). Keys are lowercased words → `(rank,
freq_per_million, zipf)`. Cached per language. Root resolves to the repo's
`word-lists/`, overridable via `BABELEBAB_WORDLISTS_ROOT` or a constructor arg.
"Known" means "present in the top-N list", so coverage is relative to list size.

### 3.3 Tokenization
`tokens = [t.lower() for t in re.findall(r"\w+", text) if not t.isdigit()]`
— Unicode word characters, lowercased, pure-number tokens dropped. (Whitespace
-delimited languages only; CJK is out of scope for v1, see §5.)

### 3.4 Outputs
`AnalysisResult`:

| field | type | meaning |
|---|---|---|
| `lang` | str | input language |
| `char_count` | int | `len(text)` |
| `sentence_count` | int | from `split_sentences` |
| `token_count` | int | running word tokens |
| `type_count` | int | distinct tokens |
| `type_token_ratio` | float | `type_count / token_count` |
| `known_count` | int | tokens found in the lexicon |
| `coverage` | dict[str,float] | `"known"` + `"top{K}"` fractions of tokens |
| `mean_zipf` | float \| None | mean Zipf over known tokens |
| `median_zipf` | float \| None | median Zipf over known tokens |
| `unknown_words` | list[str] | distinct tokens not in the lexicon |
| `rare_words` | list[str] | distinct known tokens with `zipf < rare_threshold` |
| `tokens` | list[TokenInfo] | per-token annotation (if `include_tokens`) |
| `sentences` | list[str] | from `split_sentences` |

`TokenInfo`: `text: str`, `rank: int|None`, `zipf: float|None`,
`freq_per_million: float|None`, `known: bool`.

Helpers: `AnalysisResult.summary() -> str` (one-paragraph human summary);
`to_dict() -> dict`.

### 3.5 Metric definitions
- `coverage["known"] = known_count / token_count`
- `coverage["topK"] = (tokens with rank ≤ K) / token_count`
- `mean_zipf` / `median_zipf` computed over known tokens only
- empty input → counts 0, ratios 0.0, `mean_zipf=None`

## 4. Approach & rationale

- Reuse the wordlist schema + Zipf scale, so analysis numbers line up with the
  lists and (roughly) with wordfreq.
- Keep "difficulty" as **objective metrics** (coverage, mean Zipf, rare/unknown
  counts) rather than an opaque score; callers can threshold as they wish.
- Lexicon cached per language for repeated calls.
- Live in a new `babelebab.analyze` subpackage mirroring `segmentation` /
  `translate`.

## 5. Risks / limitations

- **Non-spaced scripts** (zho/jpn/kor): `\w+` grabs whole runs; results are
  unreliable until a tokenizer is added. Documented; not blocked.
- "Unknown" means "outside the top-N list", not "not a real word".
- Short texts give noisy ratios.

## 6. Validation

Unit tests: lexicon lookup (`the` → rank 1, known; nonsense → unknown);
tokenizer (punctuation/number handling); `analyze` metrics on a known English
sentence (counts, TTR, an unknown word surfaced, `the` annotated rank 1).
ruff + mypy clean; full suite green.
