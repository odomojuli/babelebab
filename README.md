# babelebab

A local-first, multilingual NLP pipeline: **detect → segment → analyze →
translate**, composed into one call. It breaks text down into its reliable units
— languages, sentences, words — and works offline, building on frequency data
rather than large model downloads.

The name is a palindrome built on *Babel*: source ↔ target, mirrored.

## Pipeline

```
text ──▶ detect ──▶ segment ──▶ analyze ──▶ (translate) ──▶ PipelineResult
         language    sentences   frequency    per sentence
                                 + lemmas     (optional)
```

```python
from babelebab import pipeline

r = pipeline("The quick brown foxes jump over the lazy dogs. Children are running.")
r.src_lang        # 'eng'  (auto-detected)
r.sentences       # ['The quick brown foxes jump over the lazy dogs.', 'Children are running.']
r.analysis.coverage["known"]   # fraction of tokens found in the frequency list
r.summary()       # 'pipeline: src=eng, 2 sentence(s), 100% known'
```

Translation is opt-in: pass `translate_to=` and an `engine=` and each sentence is
translated. The pipeline is engine-agnostic — supply any `babelebab.translate`
engine.

## Install

The core is pure standard library. Capabilities that need a third-party package
are optional extras, each fully offline once installed:

```bash
pip install -e .                    # core (segmentation fallback, detect, analyze, hub)
pip install -e ".[sbd,lemmatize]"   # recommended: best splitter + lemmatization
pip install -e ".[dev]"             # tests + ruff + mypy (includes sbd & lemmatize)
```

| Extra | Adds | Backed by |
|---|---|---|
| `sbd` | high-accuracy, multilingual sentence splitting | `pysbd` (offline, 23 langs) |
| `lemmatize` | surface→lemma resolution in analyze | `simplemma` (offline, 10 of our langs) |
| `local` | real local translation engine | `ctranslate2` + `sentencepiece` (CPU) |
| `wordlists` | regenerate the frequency lists | `wordfreq[cjk]` |
| `analysis` | data-prep scripts | `pandas`, `openpyxl` |

## Stages

**Detect** (`babelebab.detect`) — language identification with zero dependencies,
using Cavnar–Trenkle character n-grams built from the bundled wordlists. Covers
the 18 languages we ship lists for.

**Segment** (`babelebab.segmentation`) — `split_sentences(text, lang="en")` uses
`pysbd` when the `sbd` extra is installed (multilingual, handles abbreviations,
URLs, quotes, lists), and falls back to a zero-dependency regex splitter.

**Analyze** (`babelebab.analyze`) — `analyze(text, lang)` annotates each word with
`rank` / `zipf` / `freq_per_million` from the language's wordlist and reports
coverage, type-token ratio, mean Zipf, and rare/unknown words. With the
`lemmatize` extra, inflections resolve to their lemma (`foxes → fox`).

**Translate** (`babelebab.translate`) — an engine-agnostic hub: `translate`,
`compare` (fan out across engines), and `best_pick` (consensus). Engines:
`ReplayEngine` (offline, replays the collected `analysis/` data), the optional
`CTranslate2Engine` (local CPU models), or your own `Engine`.

```python
from babelebab.translate import register, ReplayEngine, best_pick

for provider in ("DEEPL", "AMAZON", "MICROSOFT"):
    register(ReplayEngine(provider))
best_pick("she", "eng", "fra").text   # 'elle'  (consensus across engines)
```

## Wordlists

`word-lists/<iso3>/<iso3>_wordfreq_top5000.csv` holds top-5,000 frequency lists
(`rank,word,freq_per_million,zipf`) for **18 of the top-30 languages by
speakers**, generated offline from `wordfreq`. Regenerate or extend them:

```bash
python scripts/build_wordlists.py --top-n 5000             # wordfreq languages
python scripts/build_wordlists_leipzig.py --input <dir>    # gap-fill from Leipzig (local)
```

See `word-lists/README.md` for coverage and the languages still to fill.

## Layout

```
babelebab/
├── pyproject.toml
├── docs/specs/            # design records, one per feature (0001–0007)
├── src/babelebab/
│   ├── pipeline.py        # end-to-end orchestrator + PipelineResult
│   ├── detect/            # language identification (wordlist n-grams)
│   ├── segmentation/      # sentence splitting (pysbd + regex fallback)
│   ├── analyze/           # lexicon, tokenizer, lemmatizer, analysis
│   ├── translate/         # engine hub (replay, ctranslate2, identity)
│   └── languages/         # ISO 639 language metadata
├── tests/
├── scripts/               # wordlist generators
├── word-lists/            # per-language frequency CSVs (18 languages)
├── analysis/              # frequency sources + multi-engine MT comparison data
├── golden_rules/          # SBD reference cases, 14 languages
├── language-codes/        # ISO 639 + Ethnologue reference tables
└── top-lang/              # languages ranked by speakers (Ethnologue 2024)
```

## Design records

Every feature has a short spec in `docs/specs/` covering the problem, the options
considered, the decision, and validation: 0001 wordlist gap-fill, 0002 analyze,
0003 lemmatization, 0004 detection, 0005 pipeline, 0006 the splitter, 0007
language-aware segmentation.

## Status

Python 3.9+. ruff + mypy clean. The test suite is green: **63 passing**, plus
**7 expected failures** on hard golden-rule cases that `pysbd` segments
differently from the (hand-written) expectations — documented in spec 0006.

```bash
pip install -e ".[dev]" && pytest
```

## Limitations & roadmap

- The analyze tokenizer is whitespace-based, so word-level analysis of non-spaced
  scripts (Chinese, Japanese, Korean) needs a dedicated tokenizer — not yet wired.
- Detection and wordlists cover 18 of the top 30 languages; the Leipzig gap-fill
  generator (run locally) extends the rest.
- Real translation needs a local CTranslate2 model via the `local` extra; the
  built-in `ReplayEngine` only covers the collected top-1k word data.
