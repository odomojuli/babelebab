# babelebab

A divide-and-conquer toolkit for multilingual NLP: break language down into
its smallest reliable units — sentences and high-frequency words — across the
world's most-spoken languages.

The name is a palindrome built on *Babel*: source ↔ target, mirrored.

## What's here

Two threads run through the project.

**1. Segmentation — the "divide."** Splitting text into sentences reliably,
which is harder than splitting on `.!?` because of abbreviations (`Dr.`,
`Co.`), acronyms (`U.S.A.`), decimals (`3.14`), URLs, and quotes. The
`golden_rules/` directory holds reference cases for this in 14 languages, ported
from the well-known sentence-boundary-detection "Golden Rules" set.

**2. Lexicon — the "conquer."** Building core-vocabulary lists from
authoritative frequency sources (COCA 60k, Oxford 3000/5000 by CEFR, NGSL+SFI,
Longman 3000, Norvig/Google n-grams) and translating the top 1k–5k words into
~15 of the most-spoken languages across ~11 machine-translation engines, so the
engines can be compared head-to-head. That data lives under `analysis/`.

## Layout

```
babelebab/
├── pyproject.toml          # packaging, dependencies, tooling config
├── src/babelebab/
│   ├── segmentation/       # sentence splitting + acronym/numeric helpers
│   └── languages/          # ISO 639 language metadata
├── tests/                  # golden-rule test suites
├── scripts/                # data-prep utilities (chunkers, frequency analysis)
├── golden_rules/           # SBD reference cases, 14 languages
├── analysis/               # frequency lists + multi-engine MT comparisons
├── language-codes/         # ISO 639 + Ethnologue reference tables
├── top-lang/               # languages ranked by speakers (Ethnologue 2024)
└── word-lists/             # per-language word lists
```

## Quickstart

```bash
# editable install with dev tooling
pip install -e ".[dev]"

# run the golden-rule tests
pytest

# lint and type-check
ruff check .
mypy
```

```python
from babelebab.segmentation import split_sentences

split_sentences("Hello World. My name is Jonas.")
# ['Hello World.', 'My name is Jonas.']
```

## Status

The segmentation entry point, `babelebab.segmentation.split_sentences`, is wired
up but still a **baseline**: it currently delegates to a regex prototype that
passes **21 of 46** English golden-rule cases. The failing cases (abbreviations,
quotes, emails, ellipses) are the target for the next round of work, after which
the goal is to extend coverage to the other 13 languages' golden-rule suites.

The lexicon thread is currently raw data plus collection scripts; turning the
per-engine translation files into an actual head-to-head comparison is not yet
built.

## Direction (open)

What babelebab ultimately becomes is still undecided. The current structure
deliberately keeps these options open:

- **A multilingual segmentation library** — a lightweight, rules-first
  alternative to heavier NLP toolkits, validated by the golden-rule suites.
- **A core-vocabulary language resource** — frequency-ranked words with a
  best-pick translation per language, useful for language learning.
- **A machine-translation benchmark** — which engine translates core vocabulary
  best, per language, with the `analysis/` data as evidence.

## Notes

- Requires Python 3.9+.
- A natural next tidy-up is consolidating the reference-data directories
  (`analysis/`, `golden_rules/`, `language-codes/`, `top-lang/`, `word-lists/`)
  under a single `data/` root.
