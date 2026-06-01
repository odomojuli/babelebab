# Spec 0001 — Multilingual wordlist gap-fill (Leipzig)

- **Status:** Implemented (generator + spec); data generated locally by the user
- **Date:** 2026-06-01
- **Related:** `word-lists/`, `scripts/build_wordlists.py` (wordfreq generator), `word-lists/README.md`

## 1. Problem

The wordfreq generator produced top-5,000 frequency lists for 18 of the top-30
languages by speakers. Eleven were skipped because wordfreq has no data for them
and *silently substitutes a different language* (it returned English for Telugu,
Mandarin for Wu, etc.), so generating them would ship mislabeled lists:

> Yue Chinese, Wu Chinese, Telugu, Marathi, Lahndi / Western Punjabi, Javanese,
> Gujarati, Hausa, Bhojpuri, Southern Min, Levantine Arabic.

We want frequency-ranked lists for these too, in the **same schema**, sourced
offline, with correct provenance.

## 2. Goals / non-goals

**Goals**

- Frequency lists for as many of the 11 as a reputable open source genuinely covers.
- Byte-for-byte schema parity with the wordfreq CSVs (drop-in for downstream code).
- Reproducible; no network at run time; clear attribution.

**Non-goals**

- Exact parity with wordfreq's corpus (a different corpus yields different
  absolute frequencies; the Zipf scale keeps magnitudes roughly comparable).
- Inventing data for varieties no open source covers well (Wu, Southern Min, and
  Levantine-as-distinct-from-MSA may remain gaps and will be reported as skipped).

## 3. Sources evaluated

| Source | Coverage of the 11 | Format | License | Sandbox fetch |
|---|---|---|---|---|
| wordfreq | 0/11 (these are precisely its gaps) | — | — | — |
| FrequencyWords (OpenSubtitles 2018) | few (Telugu; most Indic/African absent) | `word count`, ranked | CC BY-SA 4.0 | GitHub API/raw **timed out** |
| **Leipzig Corpora Collection** | Telugu, Marathi, Gujarati, Hausa, Javanese, Punjabi, Bhojpuri (Yue/Wu/Min/Levantine partial or absent) | `rank⇥word⇥freq` in `*-words.txt` inside per-corpus `.tar.gz` | **CC BY** (3.0/4.0) | portal serves `.tar.gz` (binary) — not web_fetch-able |

**Decision:** Leipzig Corpora Collection — broadest coverage of the gaps, a
permissive CC BY license, and a clean tabular format.

## 4. Sandbox constraint (how this affects "proceed")

This environment's `web_fetch` timed out against GitHub and cannot retrieve
binary archives, and bash downloaders are disallowed. Therefore **download +
generation is a local step** — consistent with the project's local-first goal.
The generator needs no network once the files are downloaded. Its conversion
logic is validated here against a synthetic fixture; the real CSVs are produced
on the user's machine.

## 5. Specification

### 5.1 Input
One or more Leipzig per-corpus packages: the `*.tar.gz`, or an already-extracted
`*-words.txt`. Expected columns (tab-separated): `rank`, `word`, `frequency`
(absolute count). The generator re-sorts by frequency and re-ranks, so a
non-standard leading column is tolerated.

### 5.2 Output
`word-lists/<iso3>/<iso3>_leipzig_top<N>.csv` with columns identical to the
wordfreq lists: `rank,word,freq_per_million,zipf`, where

- `freq_per_million = count / corpus_total × 1_000_000`
- `zipf = round(log10(freq_per_million) + 3, 2)`

The Zipf formula matches wordfreq's scale (verified: English *the* at
53,700/M → 7.73), so Leipzig and wordfreq lists are comparable.

### 5.3 Language → ISO 639-3
Telugu→`tel`, Marathi→`mar`, Gujarati→`guj`, Hausa→`hau`, Javanese→`jav`,
Western Punjabi→`pnb`, Bhojpuri→`bho`, Yue→`yue`, Wu→`wuu`, Southern Min→`nan`,
Levantine Arabic→`apc`. Inferred from the Leipzig filename prefix or `--iso3`.

### 5.4 Normalization
Trim whitespace; drop empty tokens; preserve case and script (no folding);
`--top-n` rows (default 5,000).

### 5.5 Provenance
`word-lists/README.md` records the source and CC BY notice
(© Universität Leipzig / Sächsische Akademie der Wissenschaften / InfAI); the
generator prints the citation on each run.

## 6. Approach & rationale

- **Reuse the schema + Zipf formula** so the two sources interoperate as one list set.
- **Re-rank defensively** rather than trusting the input's rank column.
- **Corpus-relative frequencies** from the file's own total; Zipf normalizes magnitude across sources.
- **Keep it a script** (mirrors `build_wordlists.py`); the shared CSV/Zipf logic can later move into a tested `babelebab.wordlists` module.

## 7. Risks / limitations

- Cross-source Zipf is approximate (news vs web corpora, different tokenizers).
- Tokenization differs from wordfreq; Sinitic varieties (Yue/Wu/Min) are lower-confidence.
- Some of the 11 may be unavailable even in Leipzig — reported as skipped, not faked.

## 8. Validation

- Synthetic `*-words.txt` and `.tar.gz` fixtures → assert per-million + Zipf math and ordering (done in-sandbox).
- Post-generation: native-script spot check, row count == top-n, UTF-8.

## 9. Local run procedure

1. Download per-language corpora from
   `https://wortschatz.uni-leipzig.de/en/download/<Language>` (e.g. a `*_100K` package).
2. `python scripts/build_wordlists_leipzig.py --input <dir-or-file> --top-n 5000`
3. Commit the resulting `word-lists/<iso3>/<iso3>_leipzig_top5000.csv`.
