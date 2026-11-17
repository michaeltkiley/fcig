# explore_decomp: historical and variance decompositions for Note B (exploratory)

The question (user, 17 Nov 2026): with policy shocks identified in announcement windows, can the role of monetary policy shocks be traced over the full history, back to 1973, by a historical decomposition, and what share of the variance do they explain? Decisions in `DECOMP_QA.md`; results in **`REPORT.md`**. Nothing here feeds Note B's package or paper; Note B's code (`../baseline/lib/`) is imported read-only.

**Second round (current; REPORT.md Parts A and B):**

| Step | Script | Writes |
|---|---|---|
| A1 | `A1_core.py` (about 40 min, 4 cores) | `results_core/<case>.csv`, `_paths.csv` (Note B's model from 1973 and 1996, all versions, 3/6/12 lags); `results_core/draws/` (not committed) |
| A2 | `A2_monthly.py` (10 min) | `results_core/monthly_benchmarks.csv` (proxy, window-impact and Cholesky VARs: monthly averages from 1973, end of month from 1990 and 1996) |
| C | `C_core_tables.py` | `results_core/tables_core.md` |
| B1 | `B1_daily_shocks.py` (5 s) | `results_route2/daily_shocks_<step>_<fci>.csv`, `daily_summary.csv` (shocks recovered from Note B's daily innovations, 1990-2026) |
| B2 | `B2_route2.py [--start 1996-01]` (3 min) | `results_route2/hd_*.csv`, `shares*.csv`, `overlap*.csv` (Route 2 through Note B's model) |
| B3 | `B3_bands.py` (10 min) | `results_route2/bands_shares.csv`, `bands_hd_*.npz` (not committed) |
| B4 | `B4_episodes.py` | `results_route2/episodes.csv` |
| D, E | `D_figures.py`, `E_tables.py` | `figures/A*`, `figures/B*`; `results_route2/tables_route2.md` |

Order: A1, A2, C, B1, B2 (and with `--start 1996-01`), B3, B4, E, D. `REPORT.md` = the written text, then `tables_core.md`, `tables_route2.md` and, as the appendix, the first round's `results/tables.md`.

**First round (appendix):**

| Step | Script | Writes |
|---|---|---|
| lib | `lib_r2.py` | Route 2 machinery: data (monthly averages from 1973, end of month from 1990), VAR, window and proxy columns, shock recovery, historical decomposition, variance shares, lead/lag tests |
| 1 | `01_run.py` (1 min) | `results/summary.csv`, `results/fevd.csv`, `results/hd_<case>.csv`, `results/shocks_<case>.csv` (all cases: 3 steps x with/without FCI x 4 data versions x 3/6/12 lags x WE/P1/WE2 x 2020 in/dummy) |
| 2 | `02_boot.py` (10 min, 4 cores) | `results/boot_summary.csv`, `results/boot_hd_*.npz` (not committed; regenerate) |
| 3 | `03_route1_draws.py` (30 min) | `results/route1_*.npz` (Route 1 with Note B's model and its bootstrap; not committed) |
| 4 | `04_figures.py` | `figures/fig1-7` (png, pdf) |
| 5 | `05_sim_invertibility.py` (5 s per 100 samples) | `results/sim_invertibility.csv` (Note B's model as the true process) |
| 6 | `06_noteb_shares.py` | `results/noteb_shares.csv` (variance shares of the surprises with Note B's responses) |
| 7 | `07_tables.py` | `results/tables.md` (every table in REPORT.md) |
| 8 | `08_episodes.py` | `results/hd_episodes_rstar_avg1973.csv` (T6) |

Order: 1, 2, 3, 5, 6, 8 (episode table), 4, 7. `REPORT.md` = the written text followed by `results/tables.md`. Run from this folder with `PYTHONPATH=../baseline` for step 5. Requirements as `../baseline/requirements.txt` plus `tabulate`.
