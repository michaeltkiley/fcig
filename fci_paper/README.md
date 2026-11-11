# fci_paper: "Financial Conditions Indexes on a Common Basis" (Note A as a paper)

State of 11 Nov 2026. This folder turns the companion note (`../fci_note/`, "Note A") into a paper, in the way `../experimental/fin_shocks/` turned Note B into a paper: a clean, self-contained package that rebuilds every result, a paper that contains no typed result, and decisions recorded in `FP_QA.md`. Nothing here changes `../fci_note/` or `../experimental/`. Read `../experimental/WRITING_GUIDE.md` before editing any paper text.

| Path | What it is |
|---|---|
| `paper/fci_paper.tex` (+ `.pdf`, `references.bib`, `aea.bst`, `build.sh`) | The paper. Every number is a macro `\bl{key}` from `replication/report/numbers.tex`; tables and figures are read from `replication/report/`. Build: `cd paper && ./build.sh` (pdflatex, bibtex, pdflatex twice) |
| `replication/` | The package: data (`data/`, with `SOURCES.md`), library (`lib/`), steps `01_` to `07_`, `00_verify_note_a.py`, `10_check_sync.py`, `run_all.py` |
| `reviews/` | Reviewer reports on the draft and what was done with them |
| `FP_QA.md` | Decisions (scope, style, methods) and open items |

## Run order (about 5 minutes, 500 bootstrap draws)

```
cd replication
pip install -r requirements.txt
python3 run_all.py                 # steps 1-7; or python3 01_data.py ... python3 07_report.py
python3 00_verify_note_a.py        # the package reproduces the companion note's files (needs ../../fci_note/replication/output)
python3 10_check_sync.py           # re-runs steps 1-6 in a scratch directory and compares every stored result; then step 7
cd ../paper && ./build.sh
```

TeX is not preinstalled: `apt-get update && apt-get install -y --no-install-recommends texlive-latex-base texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended texlive-bibtex-extra lmodern`.

| Step | Script | Writes (`results/`) |
|---|---|---|
| 1 | `01_data.py` | `data_monthly.csv`; numbers on inflation expectations, r*, CAPE, dollar |
| 2 | `02_weights.py` | `market_weights.csv`, `conversions.csv` (GS, NFCI, ANFCI to the benchmark's units), `frbus_weights.csv`, `weights_variants.csv` (other news series and event samples), `weights_boot.csv` (bootstrap of announcements) |
| 3 | `03_indexes.py` | `indexes_<step>.csv` (nominal, real, rstar, rstar_kiley), `groups_<step>.csv`, `market_variants.csv`, `index_boot.csv` (index summaries for each weights draw) |
| 4 | `04_var.py` | `var_specs.csv`, `var_paths_<case>.csv` (response and 68/90 percent block-bootstrap bands), `flow_<case>.csv`, `var_fi_draws.csv` |
| 5 | `05_compare.py` | `compare.csv`, `episodes.csv`, `latest_groups.csv`, `robust_rows.csv` |
| 6 | `06_activity.py` | `activity.csv` (local projections, out-of-sample forecasts), `fcig_scale.csv` |
| 7 | `07_report.py` | `report/tab_*.tex`, `report/fig_*.pdf`, `report/numbers.tex`; asserts the paper's qualitative claims (`chk(...)`) and that every macro used in `paper/*.tex` is defined |

## Exhibits of the paper

| Exhibit | File in `report/` | Script |
|---|---|---|
| Fig. 1 level indexes at each step | `fig_levels.pdf` | 07 (03) |
| Table 1 the indexes (hand-written; published weights and definitions) | in the paper | -- |
| Table 2 weights; Table 3 FRB/US and market weights | `tab_weights.tex`, `tab_frbus.tex` | 07 (02) |
| Fig. 2 expected inflation and r*; Fig. 3 market index at each step | `fig_inflation_rstar.pdf`, `fig_market_steps.pdf` | 07 (01, 03) |
| Table 4 VAR by step; Fig. 4 unemployment response; Fig. 5 level and flow | `tab_var.tex`, `fig_var.pdf`, `fig_level_flow.pdf` | 07 (04) |
| Table 5 comparison at each step | `tab_compare.tex` | 07 (05) |
| Table 6 widest and closest windows; Fig. 6 today's reading | `tab_episodes.tex`, `fig_today.pdf` | 07 (05, 03) |
| Table 7 sampling error of the weights | `tab_boot.tex` | 07 (02, 03) |
| Table 8 unemployment a year ahead; Fig. 7 FCI-G scale | `tab_activity.tex`, `fig_fcig_scale.pdf` | 07 (06) |
| Table 9 variations of the construction | `tab_robust.tex` | 07 (05) |
| Appendix: groups today, weights variants, all VAR cases, checks, real and nominal activity tables, current pressure | `tab_latestgroups.tex`, `tab_wvar.tex`, `tab_var_all.tex`, `tab_checks.tex`, `tab_activity_real.tex`, `tab_activity_nominal.tex`, `fig_current_pressure.pdf` | 07 |

## Conventions

- Units: a point of the market index or of GS is the change in conditions that a policy move raising the two-year yield by 1 percentage point brings in the announcement window; a point of the FRB/US index is a persistent 1 percentage point rise in the funds rate; FCI-G is in percentage points of GDP growth. Zero is the 1973-2026 mean of each variable (not a neutral level).
- Intervals: 90 percent (5th and 95th percentiles of the bootstrap) in tables, 68 and 90 percent bands in figures of paths. VAR bootstrap: moving blocks of 12 months of residual pairs, recursive, dummies fixed. Weights bootstrap: announcements resampled with replacement (the policy-news factor is recomputed).
- Seeds are fixed (`replication/lib/config.py`); the sync check re-runs everything and compares.

## What differs from Note A (`../fci_note/replication/`)

The data and the indexes are the same (`00_verify_note_a.py` compares the weights, the four index files, the VAR responses and the local projections; the differences are at the rounding of the old files). New: block bootstrap with 68 and 90 percent bands (Note A: independent resampling, 95 percent); sampling error of the weights by bootstrap of the announcements (Tables 2, 3, 7, Fig. 6); weights under other news series and event samples; VAR estimated from 1990 and to 2019; one row per variation (Table 9); episodes also since 1990; groups behind today's readings. Dropped from the main text: ANFCI beyond one correlation (the stress index is a different object), current pressure (appendix).
