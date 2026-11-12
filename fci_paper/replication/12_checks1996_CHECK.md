# 12_checks1996: reproduction check

Compared with `followup3/core_1996/out/` (var 39 rows, levelflow 78, stance 156, ladder 54, checks table 48 rows) at REPS=500 (ladder bootstrap 2 x REPS = 1000 draws, as the original): maximum absolute difference 0.0 in every numeric column.
Examples: Phi(12) market r* 0.65 [0.39, 0.83] (1973+), 0.73 [0.26, 1.00] (1996+, 12 lags), 0.58 [0.16, 0.91] (4 lags); stance CW 1.95 / 2.31 (row a), 2.0 / 2.2 (row b).
Sub-period reconciliation (market r*, Phi(12), 12 lags; new here): 1973-89 0.64, 1990-2007 0.39, 1996-2007 0.61, 1996-2019 0.83, 2009-2026 0.55, 1996-2026 0.73, matching the facts already computed; at 4 lags 0.46, 0.32, 0.30, 0.63, 0.62, 0.58.
Run time about 3 minutes (4 worker processes for the VAR bootstraps, one BLAS thread each; without that thread limit it is several times slower on a loaded machine). Deterministic: a second run gives identical CSVs (md5).
