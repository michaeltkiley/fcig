# 10_nfci reproduction check

Compared with `followup2/nfci/out/`.

- Joint local projections (70 rows): coefficients, HAC t, gains: maximum difference 0.
- NFCI level versus flow (14 rows): 0.
- Out-of-sample encompassing / Clark-West / combination (9 rows) and recession Brier table: 0.
- NFCI on the three variables and the spread (18 rows): 0.
- Bootstrap 90% intervals of the joint projections: the follow-up used seed 1 and 999 draws; the package uses the config seed and REPS (500). Median absolute difference in the bounds 0.013 (Monte Carlo error), larger at the 24-month and quarterly horizons where blocks are few.
- Not ported: the NFCI contributions file decomposition (the file is not in the repository; the follow-up skipped it too).

Run time about 20 seconds. Two runs give identical CSVs (checked).
