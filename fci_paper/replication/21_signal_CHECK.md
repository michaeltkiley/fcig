# Check of step 21 (policy-signal sensitivity)

Runtime 28 s at REPS=500; deterministic (two runs, identical CSV checksums) [verified].

Baseline reproduction [verified, asserted in the script]
- Point estimates of the four definitions equal `results/weights_variants.csv` (weights and responses, tolerance 1e-8); baseline equals `market_weights.csv`.
- The announcement-bootstrap draws (same generator, order and seed as `02_weights.py`) reproduce `weights_boot.csv` for the baseline (max abs difference of weights and responses below 1e-6).
- Ratio of ratios 2.488 [1.020, 6.811] and b4'psi 0.975 equal `18_example.csv`; baseline interval endpoints agree to 1e-4 / 1e-3.
- Colleague's rounded-weights arithmetic (2.45, 1.21, 3.60, 2.10) agrees with the unrounded values (2.49, 1.20, 3.64, 2.13) [verified].

Design choices [inference]
- Draws are paired: each definition uses the announcements of the SAME bootstrap resample that fall in its subsample (to_2019: about 200 per draw, no_lower_bound: about 195), so differences across definitions have intervals; subsample size varies by draw.
- FRB/US weights b are fixed (as in step 18); w_B = b/(b'psi) is re-normalized per definition and draw.
- The 12-month disagreement uses the r* step inputs, months 1996-2026, 24-month moving blocks drawn in common across definitions (the baseline interval therefore differs slightly from step 18's, which used a different random stream; the point 0.328 equals step 18).
- Held-out announcement windows: leave-one-event-out within each definition (the subsample definitions are evaluated on their own announcements; `dev_baseline_on_*_ratio` gives the baseline on the same announcements).
- Episodes: the same construction as step 19 (mean of 12-month changes over the months of the episode, r* step, demeaned over 1973-2026); baseline gives -0.06 / +0.16 / +0.22 for 1998-2001 and +1.02 / +1.01 / -0.01 for 2022-24 [verified].
- FCI-G (part F): row 0 of `data/multipliers.csv` is read as the effect on growth over the next four quarters of a shift now (the four-quarter effect of a persistent shift); the 10-year yield uses the sum of the 10-year, mortgage and BBB multipliers (spreads fixed); stock and dollar multipliers per 1 percent in magnitude. Dollar-over-equity RATIO comparisons are clean (same assets, horizon, persistent path). The FCI-G funds-rate multiplier is a direct effect, so the level b'psi on the FCI-G's own yardstick is not comparable; the script reports FCI-G on the FRB/US funds-rate yardstick (G(4) = 0.4525) [inference]. FCI-G lineage partly overlaps FRB/US, so agreement measures robustness within a family of calibrations.

Limits
- Intervals for the ratio of ratios are wide and skewed (a small market equity weight in the denominator); `ror_share_draws_nonpositive` is 1.2 percent in the baseline and 0 for the two-year signal. The dollar-minus-equity contrast in points is reported alongside.
- Bootstrap intervals reflect sampling of announcements only (FRB/US weights fixed). The episode intervals are over weight draws, not over the macro data.
- No claim is made about which signal is the right measure of policy: the two-year yield also carries maturity-specific news and measurement error [inference]; the evidence in part D shows what variation each captures and not why.
