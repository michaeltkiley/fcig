# Check: step 17 against `followup3/real_time/`

Compared `results/17_realtime_*.csv` with `followup3/real_time/out/` (A_stance, B_rstar_rt, C_nrou_rt, D_pi, A2_levelflow, revisions, primary_holm), row by row on the identifying keys:
all 36 + 48 + 27 + 12 specification rows, 12 level-versus-flow rows, 13 revision rows and 8 Holm rows are matched, and the NROU columns rebuilt from `nrou_vintages.csv` equal the follow-up panel (same missing cells).

Maximum absolute difference in any statistic (n, gains, t, coefficients, RMSE ratios, Clark-West, Diebold-Mariano, revision statistics): 1.7e-06 (rounding of the panel to 6 decimals; the NROU-block statistics differ by 4e-14). Holm p-values: 0.0 difference. The real-time-r* index reproduces the package's `indexes_rstar.csv` to 5e-06 when the full-sample r* is used (`rt_index_check_maxdiff`).

Headline numbers match RESULT.md: du, r* step, flow t 5.50 (revised) vs 5.49 (vintage), Clark-West 1.96 vs 1.97; vintage NROU flow t 2.62, 2.64, 3.10; real-time r* flow t 3.17 to 2.23 (2.43 with vintage data).

Run time about 55 seconds; two runs give identical CSVs (md5). No bootstrap, so REPS and SEED do not enter.
