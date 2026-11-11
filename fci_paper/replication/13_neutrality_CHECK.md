# Check: step 13 against followup2/rstar_basis (02_unit_restriction.py, 03_neutrality.py)

Neutrality: the follow-up used 1000 draws; run with FCI_REPS=1000 the levels, differences and intervals match `neutrality_levels.csv` and `neutrality_diffs.csv` exactly (maximum difference 0.0). The unit restriction used 999 draws; run with FCI_REPS=999 `13_unit_restriction.csv` matches exactly (0.0). Point estimates do not depend on REPS. At the default REPS = 500 only bootstrap interval ends move (maximum 0.12 in the neutrality intervals, Monte Carlo error).
Note: the follow-up text says 11 series and 44 intervals; the design has 10 series (market at four bases, GS and FRB/US at three) and 40 intervals; the package says 10 and 40.
c = -1.518 is checked numerically against `lib/cases.py` (assert in the script).
Run time: about 10 seconds at REPS = 500. Determinism: two runs give identical CSVs.
Ported in full (all periods and comparisons are cheap and keep the random stream identical); the paper needs the P2 versus P3 rows.
