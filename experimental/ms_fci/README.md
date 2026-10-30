> **Note (30 Oct 2026):** this folder holds the FRB/US sensitivities and the **macro-model levels index** (formerly "MS-style"/"five-variable"). It is **not** the market index of the note
> (that is built from policy-news responses; see `../path_fci/`, `../market_macro/`, `../PROJECT_MEMORY.md` section 9 and the glossary in the root `CLAUDE.md`). Text below is the original Oct 2026 write-up.

# EXPERIMENTAL: Morgan Stanley-style five-variable financial conditions index

Status: exploratory, unverified, not used by the daily update workflow or by `fcig_replicate.py` / `fcig_gs.py` (those only supply input data
to it). The original MS index could not be sourced, so this is a reconstruction from a third-party description. Full write-up: `NOTES.md`.

## What it is
Five variables (10-year yield, BBB spread, equity valuation, trade-weighted dollar, oil) each converted to a federal-funds-rate equivalent using
FRB/US sensitivities (GDP effect of a variable shock divided by the GDP effect of a 1 pp full-transmission funds-rate hike, q4/q8/q12), then
summed. Change version (cumulative change from a base date) and level version (deviation from the 1990-2026 mean), with nominal-, real- and
r*-gap versions of the 10-year term.

## Files
| File | Purpose |
|---|---|
| `frbus_sensitivities.py` / `.csv` | FRB/US experiments and funds-rate equivalents (needs the Python 3.9 venv in its docstring; downloads pyfrbus to `raw/frbus`) |
| `ms5_index.py` | Change index, contributions between two dates |
| `ms5_level.py` | Level index (`--real10`, `--rstar`, `--twosided`, `--erp`, `--horizon`, `--source fred\|frbus`) |
| `ms5_rstar_compare.py` | Nominal vs real vs r*-gap chart |
| `ms5_vs_gs.py` | Correlations with the GS FCI (daily/weekly/monthly) and Fed FCI-G; dual-axis chart |
| `kiley_rstar.csv` | Kiley (IJCB 2020) r* estimates, copied from the `output_gap/rstar` repo |
| `NOTES.md` | Research note: MS sources, design, exoglists, results, data inputs (section H), caveats |

Run from the repo root, e.g. `python experimental/ms_fci/ms5_vs_gs.py`. Outputs (CSV/PNG) are written next to the scripts.
Inputs from the main repo: `fcig_gs_daily.csv`, `fcig_replication_daily.csv`, and `history/` (BBB OAS, S&P 500, CAPE anchors, DXY).

## Headline results (to 20 Oct 2026)
- Level (r*-gap, q4): about +0.7 pp tighter than the 1990-2026 average; 10-year term +0.44.
- Correlation with GS FCI: daily changes about 0.9 (1990-2026), levels 0.78-0.83; with Fed FCI-G daily changes since 2020: 0.5-0.55 (GS FCI 0.7-0.84).
- Nominal vs r*-gap: levels 0.85 correlated, daily changes 0.998.

## Open items for follow-up
1. Sensitivities start from the 2040 steady-state baseline; a 2026 start would scale equivalents about 13% lower (oil about 18%). Rerun from a current baseline.
2. VAR expectations only (MCE dropped); 10-year proxies the whole long end (rg5/rg10/rg30 shifted in parallel).
3. Real-dollar splice, CAPE E10 extrapolation, and the filtered r* (high in the 1990s, 2020Q2 artifact) are the weakest data links.
4. No funds-rate term; pre-2008 fit to the funds rate is weak. The MS five-variable index itself is unverified (see NOTES.md, "Unverified claims").
5. Compare with SF Fed Proxy Funds Rate and the 12-variable Tobias index (NOTES.md section A) if a policy-rate-equivalent series is wanted.
6. If promoted: wire into the daily workflow, refresh `kiley_rstar.csv` from the r* repo each quarter.
