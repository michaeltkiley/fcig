# Baseline and robustness tables for Note B (clean replication set)

Replaces the experimental `../midas_core.py` driver for the tables below. No trends except the spline in Robustness 2c-d, NS surprise only, u gap and core PCE price level (plus EBP in one case).

| File | Role |
|---|---|
| `cases.py` | the case list (12 tables, 28 estimations); edit here to add or drop cases |
| `engine.py` | estimation (trimmed from `../midas_core.py`; agrees with it to within 0.0005 on the cases compared) |
| `run_all.py` | runs the cases, one CSV each in `results/` (resumable; ~1 min per case, 4 workers) |
| `make_report.py` | writes `report/tab_*.tex` from `results/` |
| `report/baseline_robustness.tex`, `.pdf` | the document |

Reproduce: `pip install statsmodels scipy matplotlib pandas openpyxl`; `cd experimental/fin_shocks/baseline && python3 run_all.py --jobs 4 && python3 make_report.py && cd report && pdflatex baseline_robustness.tex` (twice).

Still imported from the parent folder (to be consolidated later): `mf_common`, `midas_var`, `midas_bs`, `route_a_pos`, and the `fci` utilities of Note A. The engine changes directory to `fin_shocks/` on import because those modules use relative paths.

Specification choices to confirm are listed in the PDF introduction (what "drop 2020" means; five, not six, sample cases in Robustness 1; Kiley FCI in 2a-b; spline knots at NBER peaks in 2c-d). Intervals: 200 draws; the same announcement resamples are used for every case, and the monthly resampling is seeded per case, so results do not depend on run order.
