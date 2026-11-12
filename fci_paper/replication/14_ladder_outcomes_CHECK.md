# Check: step 14 against followup/rstar_test

Compared `results/14_paired.csv`, `14_vs_baseline.csv`, `14_subperiods.csv` with `followup/rstar_test/out/` (REPS = 500, same seed and random stream): maximum absolute difference 0.0 in every column (273, 299 and 1071 rows).
Counts equal `out/summary.txt`: r* vs nominal 69 of 91 ratios below 1, 20 DM rejections at 10 percent (18 r* better), in-sample intervals exclude zero in 12 (9 positive); r* vs real 80, 15 (13), 5 (4). The follow-up RESULT.md text says 13 (9/4) for in-sample r* vs nominal; summary.txt and the package give 12 (9/3) [the text was stale]. Holm at 5 percent leaves none; at 10 percent one test (r* vs nominal).
New here: Holm adjusted p-values (`dm_p_holm`) and the tidy table `14_summary.csv`.
Run time: 48 seconds. Determinism: two runs give identical CSVs. No grid reduction.
