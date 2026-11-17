# explore_decomp: historical and variance decompositions for Note B (exploratory)

The question (user, 17 Nov 2026): with policy shocks identified in announcement windows, can the role of monetary policy shocks be traced over the full history, back to 1973, by a historical decomposition, and what share of the variance do they explain? Decisions in `DECOMP_QA.md`; results in **`REPORT.md`**. Nothing here feeds Note B's package or paper; Note B's code (`../baseline/lib/`) is imported read-only.

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
