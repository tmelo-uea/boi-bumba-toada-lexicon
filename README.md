# Regional/Indigenous Lexicon in Boi-Bumbá Toadas — Data & Code

Supplementary material for a LAMIR 2026 submission (anonymized for double-blind review).

This repository accompanies a paper studying regional and Indigenous vocabulary in the lyrics
(*toadas*) of the two rival groups of the Boi-Bumbá festival of Parintins (Amazonas, Brazil),
Caprichoso and Garantido, across a corpus of 1,565 toadas spanning 1989–2026.

## What is (and is not) in this repository

**Included:**
- `data/corpus_metadata.csv` — title, album, year, composer, and source URL for all 1,565
  toadas. **Does not include lyric text.**
- `data/lexicon_v2.csv` — the 94-term regional/Indigenous lexicon: two-axis classification
  (etymological origin × semantic domain), tier (core/extended/excluded/toponymic-control/
  afro-identity), canonical forms and spelling variants, token and document frequencies (raw and
  institutionally-adjusted), and curatorial notes.
- `data/lexicon_methodology.md` — the full methodology note documenting every correction and
  design decision behind the lexicon (v1 → v2), including known limitations.
- `data/analysis_results/` — the output tables/figures reported in the paper: density by decade,
  keyness rankings (token and document frequency), trend-regression results.
- `annotations/cobra/` — the full double-blind annotation record for disambiguating the word
  *cobra* (mythical entity vs. animal vs. metaphor): blind annotation template, both annotators'
  labels, adjudicated final labels, and the raw agreement/disagreement log
  (Cohen's κ = 0.136, 81.5% raw agreement, 91.2% mythical after adjudication).
- `annotations/institutional_confound/` — the same record for the single-annotator classification
  of *pajé*/*cunhã*(-*poranga*)/*tuxaua* as institutional-Festival-item vs. cultural/ritual usage.
- `code/` — the full lexicon-construction, per-song scoring, and statistical-analysis pipeline
  (5 scripts, numbered in execution order). All 5 have been independently re-run end-to-end and
  verified to reproduce the exact numbers reported in the paper.

**Not included:** the full lyric text of the 1,565 toadas. The toadas are copyrighted creative
works whose rights are held by their respective composers and/or other rights holders; we judged
public redistribution of the full text corpus to carry unresolved copyright risk (see paper,
Section "Data and Code Availability"). Full lyric text is available upon reasonable request after
publication of the paper — see venue contact details in the published version, since author
contact information is withheld here to preserve double-blind anonymity during review. Short
excerpts (under ~200 characters) used as annotation context are included within the
`annotations/` CSVs, as these are quotations for methodological transparency rather than
redistribution of complete works.

## Reproducing the analysis from raw lyrics

If you have obtained the full lyric corpus (by request, as above) in the same structure as our
internal `catalogo_completo.json` — a JSON list of records with at least
`{"boi": "Caprichoso"|"Garantido", "title": ..., "year": ..., "lyric": "<full text>"}` — the
pipeline can be re-run in order:

```bash
cd code

python 01_build_lexicon_frequencies.py \
    --corpus catalogo_completo.json \
    --cobra-labels ../annotations/cobra/final_adjudicated_labels.json \
    --cobra-occurrences cobra_occurrences.json \
    --out freq_v2.json

python 02_build_lexicon_table.py \
    --freq freq_v2.json \
    --cobra-mitica-by-song ../annotations/cobra/mitica_counts_by_song.json \
    --out lexicon_v2_rebuilt.csv

python 03_score_songs.py \
    --corpus catalogo_completo.json \
    --cobra-labels ../annotations/cobra/final_adjudicated_labels.json \
    --cobra-occurrences cobra_occurrences.json \
    --institutional-labels ../annotations/institutional_confound/external_annotator_labels.csv \
    --out per_song_scores.json

python 04_temporal_analysis.py \
    --scores per_song_scores.json \
    --out-density density_by_decade.csv \
    --out-trend trend_results.json

python 05_keyness_analysis.py \
    --scores per_song_scores.json \
    --institutional-labels ../annotations/institutional_confound/external_annotator_labels.csv \
    --out-token keyness_nucleo_token_freq.csv \
    --out-doc keyness_nucleo_doc_freq.csv
```

Note: `cobra_occurrences.json` (per-occurrence lyric context snippets for the *cobra*
disambiguation task) is also not published in full here for the same copyright reason; it is
needed by scripts 01 and 03 and would be included in the same data request as the full corpus.

Without the raw lyric text, `data/analysis_results/` already contains every output these scripts
produce, generated from our own run, so the reported numbers can be inspected and checked for
internal consistency without needing to re-run the pipeline.

## Known limitations (see paper and `data/lexicon_methodology.md` for full discussion)

- Keyness tests (script 05) are reported uncorrected for multiple comparisons (46 simultaneous
  tests); treat "significant" terms as candidates, not confirmed findings.
- The institutional-confound annotation (single annotator, `annotations/institutional_confound/`)
  was not blinded to which of the two groups each toada belonged to.
- The "year" field in `corpus_metadata.csv` reflects album metadata, not necessarily original
  composition date.
- In `05_keyness_analysis.py`, the institutional adjustment is applied to token frequency but
  intentionally *not* to document frequency, to match the exact methodology already reported in
  the paper (see in-code comment). This does not change which terms are found significant.

## Requirements

See `requirements.txt`. Python ≥ 3.9. No raw-text corpus is required to inspect
`data/analysis_results/` or to read the lexicon/annotation files.

## License

Code, lexicon, corpus metadata, and analysis results in this repository are released under
CC BY 4.0 (see `LICENSE`). This license does not extend to the toadas' lyric text itself, which
is not included here and remains under the rights of its original composers/rights holders.

## Citation

Citation details will be added once the paper is de-anonymized / published. In the meantime,
please cite the associated LAMIR 2026 submission.
