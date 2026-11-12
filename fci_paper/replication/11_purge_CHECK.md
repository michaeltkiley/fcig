# Check: step 11 against followup2/purge

Compared `results/11_corr.csv`, `11_lp.csv`, `11_var.csv`, `11_purged_indexes.csv` with `followup2/purge/out/` (same design, same seed, REPS = 500).
Maximum absolute difference: 0.0 for the purged indexes, 5e-7 for correlations, 6e-6 for LP t-statistics, 4e-5 for VAR statistics (Granger F; intervals 3e-6). All are rounding: the follow-up read indexes rounded to five decimals and the bootstrap here is vectorised over draws (same draws, same recursion, `lib/purge_purge.py`).
Run time: 31 seconds (the follow-up took about 8 minutes: its per-draw least squares was slowed by multi-threaded BLAS; `purge_util.single_thread_blas()` uses one thread).
Determinism: two runs give identical CSVs.
Core inflation is PCEPILFE from `data/` (identical to the follow-up file). No grid reduction.
