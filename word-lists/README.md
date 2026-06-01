# word-lists

Frequency-ranked vocabulary lists, one directory per language (ISO 639-3 code).

## wordfreq lists (top 5,000)

`<iso3>/<iso3>_wordfreq_top5000.csv` — generated offline from the
[wordfreq](https://github.com/rspeer/wordfreq) library.

Columns: `rank,word,freq_per_million,zipf`

- `rank` — 1 is the most frequent word
- `freq_per_million` — expected occurrences per million tokens
- `zipf` — log-frequency on wordfreq's 0–8 Zipf scale (7+ is extremely common)

Regenerate:

```bash
pip install "babelebab[wordlists]"
python scripts/build_wordlists.py --top-n 5000
```

### Coverage — 18 of the top 30 by speakers

Covered: Mandarin (`zho`), Spanish (`spa`), English (`eng`), Hindi (`hin`),
Bengali (`ben`), Portuguese (`por`), Russian (`rus`), Japanese (`jpn`),
Vietnamese (`vie`), Turkish (`tur`), Korean (`kor`), Tamil (`tam`),
Arabic (`ara`), German (`deu`), French (`fra`), Urdu (`urd`), Italian (`ita`),
Persian (`fas`).

Not in wordfreq, so **skipped on purpose** (wordfreq otherwise silently
substitutes another language's data, which would ship mislabeled lists): Yue
Chinese, Wu Chinese, Telugu, Marathi, Lahndi / Western Punjabi, Javanese,
Gujarati, Hausa, Bhojpuri, Southern Min, Levantine Arabic. Filling these in
needs another source — e.g. FrequencyWords (OpenSubtitles) or the Leipzig
Corpora.

Notes:

- `ara` is wordfreq's Arabic (Modern Standard Arabic), mapped from the top-30
  "Egyptian Arabic" entry; it is not Egyptian colloquial specifically.
- CJK lists (`zho`, `jpn`, `kor`) require tokenizer modules, pulled in by the
  `wordlists` extra (`wordfreq[cjk]`).

## Leipzig lists — gap-fill (run locally)

Languages wordfreq doesn't cover are filled from the
[Leipzig Corpora Collection](https://wortschatz.uni-leipzig.de) (CC BY),
producing `<iso3>/<iso3>_leipzig_top5000.csv` in the **same schema** as above.
Design is documented in `docs/specs/0001-multilingual-wordlist-gapfill.md`.

The corpora ship as per-language archives, so this is a local step (no network
at run time once downloaded):

1. Download a corpus (e.g. a `*_100K` package) from
   `https://wortschatz.uni-leipzig.de/en/download/<Language>`.
2. `python scripts/build_wordlists_leipzig.py --input <dir-or-file> --top-n 5000`

Targets the gaps where Leipzig has data: Telugu (`tel`), Marathi (`mar`),
Gujarati (`guj`), Hausa (`hau`), Javanese (`jav`), Western Punjabi (`pnb`),
Bhojpuri (`bho`). Yue / Wu / Southern Min / Levantine Arabic remain
lower-confidence or absent. Attribution: © Universität Leipzig / Sächsische
Akademie der Wissenschaften / InfAI, CC BY.

## Other lists

- `fra/fra_french.txt` — large French word list (pre-existing).
- `jpn/joyo-kanji.csv` — Jōyō kanji reference (pre-existing).
