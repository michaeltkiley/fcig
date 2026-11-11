# Check: step 15 against followup/weights

Compared `results/15_cells.csv`, `15_pairs.csv`, `15_act_weights.csv`, `15_primary_family.csv` with `followup/weights/results/` (REPS = 500; bootstrap seed 20261112 = SEED + 1): maximum absolute difference 0.0 for cells, pairs and Holm/BH p-values, 2e-16 for activity-fitted shares and intervals.
Results agree with the follow-up RESULT.md: 25 of 120 raw rejections at 10 percent, 0 after Holm or Benjamini-Hochberg; geometric-mean MSE relative to the market weights 1.058, 1.042, 1.072, 1.067 (FRBUS3, PC1, EQ, ACT, change form); market shares inside the activity-fitted intervals in 6 of 10 cells, FRB/US in 5.
Not ported: the recursive path of the fitted shares (not needed for the conclusion).
Run time: 55 seconds. Determinism: two runs give identical CSVs.
