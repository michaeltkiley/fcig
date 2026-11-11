# Check: 16_weights_drift.py against followup3/weights_drift/

Compared `results/16_*` with `followup3/weights_drift/out/` at REPS=500 (same seed, same draw order):

- weight paths (278 rows, expanding and rolling20): maximum absolute difference 0.0
- bootstrap bands at year ends (32 rows, points, 5/95 percentiles, width ratios): 0.0
- pseudo-real-time index series (nominal, real, r*; levels and forward impetus): 0.0
- index sensitivity table (correlations, VAR response at 12 months, gaps): 8e-14
- RESULT.md figures reproduced: expanding after 2010 10-year and dollar always inside the baseline band, equity outside at 10 of 124 dates; rolling 10-year weight outside at 21 dates; correlations 0.94-0.98; Phi(12) 0.52 vs 0.65 (r*).

Run time about 45 seconds. Two consecutive runs give byte-identical CSVs. New relative to the follow-up: extra columns (n_out counts, Phi at 6 and 24 months), `16_var_response.csv`, and the tidy figure data `16_weight_path.csv` (columns kind = path / bootstrap / baseline, series, window, date, value, lo, hi). The figure itself (follow-up `03_figure.py`) is left to 07_report.py.
