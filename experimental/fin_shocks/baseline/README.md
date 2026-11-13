# Note B: baseline and robustness results (self-contained replication package)

Everything in the results document is built from raw inputs in `data/` by the scripts below, in order. Each step writes files that the next reads, and each can be re-run alone.
Note A's code that Note B needs (the market index, its weights and inputs) is vendored in `lib/noteA.py`; step 2 checks it against Note A's published files when the Note A package is present.

| Step | Script | Reads | Writes |
|---|---|---|---|
| 1 | `01_data.py` | `data/` | `output/data_monthly.csv`, `output/macro_monthly.csv` |
| 2 | `02_indexes.py` | `output/data_monthly.csv`, `data/usmpd_monetary_events.csv` | `output/market_weights.csv`, `output/indexes_*.csv` |
| 3 | `03_estimate.py` | `cases.py`, `output/`, `data/` | `results/<case>.csv`, `results/<case>_paths.csv`, `output/draws/` |
| 4 | `04_monthly_var.py` | `cases.py`, `output/`, `data/` | `results/monthly_<step>_<fci>_<start>.csv` |
| 5 | `05_tradeoff.py` | `output/draws/` | `results/tradeoff.csv`, `results/tradeoff_diff.csv` |
| 6 | `06_proxy_simulation.py` | `results/monthly_*`, `output/`, `data/` | `results/proxy_sim_rstar.csv`, `results/proxy_sim_summary.csv` |
| 8 | `08_literature_style.py` | `data/`, `output/` | `results/lit_style.csv`, `results/lit_style_info.csv` (Cholesky VARs with the 2-year yield or the funds rate, with and without commodity prices; monthly proxy VAR without the FCI; all horizons) |
| 9 | `09_weights_test.py` | `output/`, `data/` | `results/weights_test.csv` (three tests: all components equal; 10-year yield = dollar with equities free; equities = the rest) |
| 10 | `10_bootstrap_sensitivity.py` | `output/`, `data/` | `results/boot_sens.csv` |
| 11 | `11_persistence.py` | `output/draws/` (daily model paths), `data/` | `results/persistence.csv` (event-based yield and FCI responses at 5, 22, 66 trading days and the 22-day average, against the model) |
| 12 | `12_direct_projection.py` | `output/`, `data/` | `results/direct_projection.csv` (direct monthly projections on the surprise at 12 and 24 months) |
| 7 | `07_report.py` | `results/`, `output/` | `report/tab_*.tex`, `report/fig_*.pdf`, `report/numbers.tex` (macros for every number quoted in the note's text); also asserts the qualitative claims of Note B Section 3 and fails if they stop being true |

`07c_report_review.py` (run after 07b; revision of 13 Nov 2026 on the external review, FS_QA FS-A71) writes `tab_timing` (announcement timing and financial conditions, 2 x 2 by version), `tab_credit` (excess bond premium, daily Baa spread, and the share of excess-bond-premium changes the FCI's components account for), `tab_jk` (FCI weights from the Jarocinski-Karadi subset), `fig_ordinary` (the ordinary-day and window FCI loadings) and `report/numbers_rev.tex` (macros `bl:rv:*`), and asserts its claims. New cases in `cases.py`: R3c (daily Baa-10-year spread in the daily block, `fci="baa"`), R5c (index weights re-estimated by step 2 on the Jarocinski-Karadi subset, `fci="jkw"`; `output/market_weights_jk.csv`, `output/indexes_rstar_jkw.csv`), R5d (those weights with the Jarocinski-Karadi surprise). R6 (13 Nov 2026, FS-A73): the r*-gap index under the companion paper's other three calibrations (`fci="calY"`, `"calB"`, `"calG"`; weights in `data/four_weights.csv`), reported in `tab_weights4` by 07c. R5c and R5d and `tab_jk` are kept as a record but are not in the paper or its tables (FS-A72).

`07b_report_extensions.py` (run after 07, 09, 11, 12) writes the revision's exhibits (`tab_decomp`, `tab_matched`, `tab_components`, `tab_weights_test`, `tab_persist`, `tab_direct`, `fig_decomp`, `fig_persist`, `fig_fcis`) and `report/numbers_ext.tex`, and asserts the claims made about them.

Then `cd report && pdflatex baseline_robustness.tex` (twice).

Reproduce: `pip install -r requirements.txt`; `python3 01_data.py && python3 02_indexes.py && python3 03_estimate.py --jobs 4 && python3 04_monthly_var.py && python3 05_tradeoff.py && python3 06_proxy_simulation.py && python3 08_literature_style.py && python3 09_weights_test.py && python3 10_bootstrap_sensitivity.py && python3 11_persistence.py && python3 12_direct_projection.py && python3 07_report.py && python3 07b_report_extensions.py && python3 07c_report_review.py` (about 70 minutes with 4 cores, mostly step 3).

* `cases.py` is the single list of cases (19 panels, 53 estimations, plus 6 monthly-VAR systems on end-of-month series from 1996; edit it to add or drop cases). `lib/model.py` documents the model and `lib/monthly.py` the monthly-VAR benchmarks (equations, assumptions, references) and `lib/simulate.py` the Monte Carlo in which the r*-gap model is the true process (monthly proxy VAR only; the extended simulation is archived in `../legacy/simulation_extended/`); `lib/daily.py` the daily data and announcements; `data/SOURCES.md` the inputs and what is unverified.
* Specification: Nakamura-Steinsson policy news (252 announcements, January 1996 on; monthly equations start in January 1996, the first announcement with all window variables), 12 monthly lags in the main tables (3 and 6 in the appendix), no deterministic trend except the spline of Robustness 2c-d, 500 bootstrap draws (announcements and monthly residuals; the daily block is not re-estimated).
* Verification: the model reproduces the earlier experimental engine (`../legacy/`) to the rounding of its stored results (5e-5) on seven case types, and the market index and weights reproduce Note A's files exactly.

The path files `results/<case>_paths.csv` include the 2-year yield at the end of each month (`kind = fin_eom`), used to relate the window unit to the end-of-month unit of the monthly VARs. Step 8 (`08_literature_style.py`, run before step 7) estimates the standard methods of Note B Section 3.1 (recursive VARs, monthly proxy VAR without the FCI) on the same data and units; code in `lib/litstyle.py`.

* Revision of 11 Nov 2026 (instructions in `paper/`): the bootstrap's month, announcement and daily-row draws no longer depend on whether the FCI is in the model (the seed tag drops the FCI), so every pair of cases with and without the FCI, and the three component specifications, use common draws and contrasts are paired. `lib/model.estimate` also returns path B (the fitted FCI model started from the ordinary FCI movement, `ordinary_loading`), the daily paths after the announcement day (`fday`), and supports the component versions `cmpR` (the index built from the components), `cmpE` (equities separate, 10-year yield and dollar as one variable) and `cmp` (all three separate) on one common three-component daily block (`MGROUPS`).

## Exhibits of the paper and the scripts that produce them (state of 11 Nov 2026)

`paper/mp_transmission.tex` contains no typed result: every number is a macro `\bl{...}` (from `report/numbers.tex` written by `07_report.py` and `report/numbers_ext.tex` written by `07b_report_extensions.py`) and every table and figure is read from `report/`. The qualitative statements of the text are asserted in the two report scripts (`check_claims`, `lag_summary`, `boot_summary`, `rob_summary` in 07; `claims()` and the `chk(...)` calls in 07b), which stop with an error when a claim stops being true. To rebuild the paper from raw inputs, run the steps of the table above in order (about 60 minutes with 4 cores; `03_estimate.py --force` is the long step), then `cd ../paper && pdflatex mp_transmission && bibtex mp_transmission && pdflatex mp_transmission && pdflatex mp_transmission`.

| Exhibit in the paper | File in `report/` | Script |
|---|---|---|
| Fig. 1 (introduction), baseline paths with and without the FCI | `fig_intro.pdf` | 07 |
| Fig. 2 index against the rebuilt Goldman Sachs index; Fig. 4 the three versions | `fig_gs.pdf`, `fig_fcis.pdf` | 07b (Goldman rebuild from Note A: `data/gs_noteA_monthly.csv`) |
| Fig. 3 and Table 2, standard methods | `fig_standard.pdf`, `tab_standard.tex` (two rows; four rows in `tab_standard_all.tex`, appendix) | 07 (estimates: 08) |
| Table 3 matched comparison; Fig. 5 paths for three versions | `tab_matched.tex`, `fig_steps.pdf` | 07b, 07 |
| Table 4 proxy and window-impact VARs; simulation table | `tab_monthly_compact.tex`, `tab_proxy_sim.tex` | 07 (estimates: 04, 06) |
| Fig. 6 and Table 5, decomposition (paths A, B, C) | `fig_decomp.pdf`, `tab_decomp.tex` | 07b (draws from 03: `s0B`, `sdB`) |
| Table 6, Phillips multiplier (compact; all cases in the appendix) | `tab_tradeoff.tex`, `tab_tradeoff_full.tex` | 07b, 07 (sets: 05; 68 percent sets in `results/tradeoff.csv`) |
| Tables 7 and 8, components and weights tests | `tab_components.tex`, `tab_weights_test.tex`, `tab_wt_full.tex` | 07b (estimates: 03 panel R4c; tests: 09) |
| Tables 9-10, weights and persistence; Figs. 7-8 | `tab_weights.tex`, `fig_financial.pdf`, `fig_persist.pdf`, `tab_persist.tex` | 07, 07b (persistence: 11) |
| Table 11, robustness summary; appendix tables by panel | `tab_rob_summary.tex`, `tab_main_*.tex`, `tab_app_*.tex` | 07 (03) |
| Fig. 2 ordinary day and announcement window; timing 2 x 2; credit; JK weights (Sections 2.3, 4.4, 4.5, 5.4) | `fig_ordinary.pdf`, `tab_timing.tex`, `tab_credit.tex`, `tab_jk.tex` | 07c (03, 04) |
| Direct projection (appendix) | `tab_direct.tex` | 07b (12) |
| Lag length, bootstrap, simulation (appendix) | `tab_lags.tex`, text macros `bl:bs:*` | 07 (03, 10) |

Conventions: responses are per +1 pp on the two-year yield in the window; `**` and `*` mark the 5 and 10 percent levels; intervals are 90 percent (68 percent in the bands of the baseline figures); every pair of cases with and without the FCI, the component versions and path B share bootstrap draws (the seed tag omits the FCI). The tables written by 07 and 07b are put in the house LaTeX style by `lib/latex_style.py` (floats `[tp]`, Title Case captions, notes under the table, wide tables shrunk to the page, tall appendix tables as `longtable`).
