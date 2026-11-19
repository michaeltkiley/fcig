# Note B with the real version as the baseline (self-contained replication package)

This package rebuilds Note B on the baseline decided on 18 Nov 2026 (`../PLAN_REAL_BASELINE.md`; decisions D1-D11 in `../FS_QA.md` FS-A85). It was copied from `../baseline/`, which stays frozen as the record of the r*-gap version. The model, data and steps are the same, with these changes:

* **Funds rate in the model by default (D1).** The federal funds rate is a third daily variable next to the 2-year yield and the FCI, in the same version as the 2-year yield. It moves on the announcement day by B_FF = 0.72 per +1 pp on the 2-year yield: the window move of current-month fed funds futures (USMPD MP1). It also enters the monthly equations, the monthly VAR benchmarks (`lib/monthly.py`), the simulation (`lib/simulate.py`) and the decomposition (`lib/decomp.py`).
  * Case key `ext`: `""` is the baseline (2-year yield and funds rate); `"noff"` is the 2-year-only model of `../baseline/` (robustness test R5); `"1y"` uses the 1-year yield in place of the 2-year, with the funds rate (appendix A4).
  * The switch is `lib/model.use_variant`.
* **Two steps (D2).** The by-version exhibits show nominal and real. The real version with the FCI is the headline (`HEAD_FORM` in `07_report.py`). The r*-gap step (LW r*) is a panel of the final section (F1).
* **Spline knots (D4).** The first knot is at the first estimation month (1974-01 for the 1973 start at 12 lags; 1996-01 from 1996). This is in `lib/model.macro_data`, tested as `spl74` in `../explore_rstar/real_trends.py`. The spline is used only in the final section (F2).
* **Lags 6 and 12 only (D9).** The 3-lag runs are dropped everywhere.
* **Robustness tests (D6, as revised by D10-D11).** There are six core tests, each run for nominal and real:
  * R1: 2020 left in.
  * R2: EBP and IP added together as monthly variables.
  * R3: the Bauer-Swanson surprise.
  * 6 lags: every case is estimated at 6 and 12 lags.
  * R5: without the funds rate.
  * R6: monthly equations from 1985 (one start).
  * R1-R3 and R5 are run from 1996 and from 1973.
* **Appendix panels kept, real version:** A1 ends 2019, A2 the daily Baa spread, A3 the Jarocinski-Karadi surprise, and A4 the 1-year yield (nominal and real).
* **Dropped:**
  * the FCI components and the weights tests (D10; left to Note A): step 09 is not run, `tab_components` and `tab_weights_test` are gone, and the `cmp*` code is kept in `lib/model.py` but unused;
  * Kiley r* (D5: LW only);
  * the ordinary-day material (FS-A86, author 18 Nov 2026): the figure comparing an ordinary day with an announcement window and its loadings, and the path-B table (already out of the paper, FS-A81); `lib/model.estimate` still computes path B, unreported;
  * the Jarocinski-Karadi weights and the four calibrations of the weights (FS-A87, author: dropped, not rebuilt in the real form; the JK surprise stays as A3).
* **Claims.** The qualitative claims are rewritten from the new results in `claims_real.py`, called by `07_report.py`. The checks of the r*-gap text in `../baseline/` are not carried over; in 07b, 07c and 07d they are removed (`pass`).

| Step | Script | Writes |
|---|---|---|
| 1 | `01_data.py` | `output/data_monthly.csv`, `output/macro_monthly.csv` |
| 2 | `02_indexes.py` | `output/market_weights.csv`, `output/indexes_*.csv` |
| 3 | `03_estimate.py --jobs 4` | `results/<case>.csv`, `results/<case>_paths.csv`, `output/draws/` (not kept) |
| 4 | `04_monthly_var.py --jobs 4` | `results/monthly_<step>_<fci>_<start>.csv` (funds rate in every system) |
| 5 | `05_tradeoff.py` | `results/tradeoff.csv`, `results/tradeoff_diff.csv` (real minus nominal, with the FCI) |
| 6 | `06_proxy_simulation.py`, `--lags 6` | `results/proxy_sim_real*.csv`, `results/proxy_sim_summary*.csv` (the real model as the true process) |
| 8 | `08_literature_style.py` | `results/lit_style*.csv` (Cholesky and proxy VARs; 12 and 6 lags) |
| 10 | `10_bootstrap_sensitivity.py` | `results/boot_sens.csv` (nominal and real) |
| 11 | `11_persistence.py` | `results/persistence.csv` (real yield and FCI) |
| 12 | `12_direct_projection.py` | `results/direct_projection.csv` (real financial lags) |
| 13 | `13_decomposition.py` | `results/decomp_*.csv`, `output/decomp/` (real model) |
| 14 | `14_sim_matched.py` | `results/sim_matched_real.csv`, `results/sim_matched_summary.csv` (the main model without and with the FCI on step 6's simulated samples; FS-A92) |
| 7 | `07_report.py`, `07b_report_extensions.py`, `07c_report_review.py`, `07d_report_decomp.py` | `report/tab_*.tex`, `report/fig_*.pdf`, `report/numbers*.tex`; `07_report.py` asserts `claims_real.py` |

Then `cd report && pdflatex results_real.tex` (twice). That is the results document for the sign-off.

Reproduce: `pip install -r requirements.txt`, then

```
python3 01_data.py && python3 02_indexes.py && python3 03_estimate.py --jobs 4 && python3 04_monthly_var.py --jobs 4 && python3 05_tradeoff.py \
&& python3 06_proxy_simulation.py && python3 06_proxy_simulation.py --lags 6 && python3 08_literature_style.py && python3 10_bootstrap_sensitivity.py \
&& python3 11_persistence.py && python3 12_direct_projection.py && python3 13_decomposition.py && python3 14_sim_matched.py \
&& python3 07_report.py && python3 07b_report_extensions.py && python3 07c_report_review.py && python3 07d_report_decomp.py
```

This takes about two hours with 4 cores, mostly step 3 (74 estimations). `CLAIMS_REPORT=1` lists failing claims instead of stopping.

## Exhibits (results document `report/results_real.tex`)

| Exhibit | File in `report/` | Script |
|---|---|---|
| Figure 1: nominal and real, rates alone and with the FCI, 1996 and 1973 | `fig_intro.pdf`, `fig_intro73.pdf` | 07 |
| Baselines at 12/24/36 months | `tab_main_B.tex` | 07 |
| Matched comparison at 24 months (both samples), paired differences | `tab_matched.tex`, `tab_matched_diff.tex` | 07b |
| Paths by version; financial response (2-year, FCI, funds rate) | `fig_steps.pdf`, `fig_financial.pdf` | 07 |
| Standard methods | `fig_standard.pdf`, `tab_standard*.tex` | 07 (08) |
| Monthly VARs with the funds rate; simulation | `tab_monthly_compact.tex`, `tab_main_monthly*.tex`, `tab_monthly_F.tex`, `tab_proxy_sim.tex` | 07 (04, 06) |
| Phillips multiplier and sacrifice ratio | `tab_tradeoff.tex`, `tab_tradeoff_full.tex` | 07b, 07 (05) |
| Decomposition of policy shocks (Section 3.5) | `fig_decomp_hd.pdf`, `tab_decomp_shares.tex`, `tab_decomp_full.tex`, `tab_decomp_diag.tex` | 07d (13) |
| Mechanisms: persistence, timing, credit | `tab_persist.tex`, `fig_persist.pdf`, `tab_timing.tex`, `tab_credit.tex` | 07b, 07c |
| Robustness summary (six tests, real and nominal, 12 months) | `tab_rob_summary.tex`, `tab_main_R.tex` | 07 |
| Final section: variance fitted by a spline; r*-gap step and spline responses | `tab_slow_shares.tex`, `tab_slow_resp.tex`, `tab_main_F.tex` | 07 |
| Appendix: panels at 6 and 12 lags, further tests, lags, direct projection | `tab_app_*.tex`, `tab_main_A.tex`, `tab_lags.tex`, `tab_direct.tex` | 07, 07b |

Conventions are as in `../baseline/`:
* responses are per +1 pp on the 2-year yield in the window;
* `**` and `*` mark the 5 and 10 percent levels;
* intervals are 90 percent (68 percent bands in the figures);
* pairs with and without the FCI share bootstrap draws.
