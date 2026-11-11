# 09_levelflow reproduction check

Compared with `followup/levelflow/out/` (mean_results, granger_results, recession_logit, and the monthly rows of quantile_results).

- Mean (28 rows, all columns incl. out-of-sample RMSE ratios and DM t): maximum absolute difference 0.
- Granger sum-versus-differences (14 series): maximum difference 0.
- Recession logit (14 series): maximum difference 0.
- Quantile regressions, payroll growth, tau 0.1/0.5/0.9 (42 rows): the follow-up used 200 bootstrap draws and the same seed and draw order; the package run with FCI_REPS=200 gives a maximum difference of 0 in coefficients and 5/95 percent bounds. At the default REPS=500 the bounds move by Monte Carlo error only.

Not ported by design: the out-of-sample quantile (pinball) tests and the GDP quantile regressions. The out-of-sample tail is stated as untestable: the 1995-2025 origins contain two recessions (scalars `levelflow_oos_recessions`, `levelflow_oos_recession_origins`).

Run time at REPS=500: about 5 minutes (quantile bootstrap on 4 processes; machine shared). Two runs give identical CSVs (checked).
