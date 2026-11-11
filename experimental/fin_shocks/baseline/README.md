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
| 7 | `07_report.py` | `results/`, `output/` | `report/tab_*.tex`, `report/fig_*.pdf`, `report/numbers.tex` (macros for every number quoted in the note's text); also asserts the qualitative claims of Note B Section 3 and fails if they stop being true |

Then `cd report && pdflatex baseline_robustness.tex` (twice).

Reproduce: `pip install -r requirements.txt`; `python3 01_data.py && python3 02_indexes.py && python3 03_estimate.py --jobs 4 && python3 04_monthly_var.py && python3 05_tradeoff.py && python3 06_proxy_simulation.py && python3 08_literature_style.py && python3 07_report.py` (about 8 minutes).

* `cases.py` is the single list of cases (12 panels, 28 estimations, plus 6 monthly-VAR systems on end-of-month series from 1996; edit it to add or drop cases). `lib/model.py` documents the model and `lib/monthly.py` the monthly-VAR benchmarks (equations, assumptions, references) and `lib/simulate.py` the Monte Carlo in which the r*-gap model is the true process (monthly proxy VAR only; the extended simulation is archived in `../legacy/simulation_extended/`); `lib/daily.py` the daily data and announcements; `data/SOURCES.md` the inputs and what is unverified.
* Specification: Nakamura-Steinsson policy news (252 announcements, January 1996 on; monthly equations start in January 1996, the first announcement with all window variables), 12 monthly lags in the main tables (3 and 6 in the appendix), no deterministic trend except the spline of Robustness 2c-d, 500 bootstrap draws (announcements and monthly residuals; the daily block is not re-estimated).
* Verification: the model reproduces the earlier experimental engine (`../legacy/`) to the rounding of its stored results (5e-5) on seven case types, and the market index and weights reproduce Note A's files exactly.

The path files `results/<case>_paths.csv` include the 2-year yield at the end of each month (`kind = fin_eom`), used to relate the window unit to the end-of-month unit of the monthly VARs. Step 8 (`08_literature_style.py`, run before step 7) estimates the standard methods of Note B Section 3.1 (recursive VARs, monthly proxy VAR without the FCI) on the same data and units; code in `lib/litstyle.py`.
