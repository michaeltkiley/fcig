# Check of step 25 (monthly agreement between the calibrations; proportionality on common draws; 5,000 draws)

Runtime 4 s at 5,000 draws; deterministic (two runs, identical checksums) [verified].

- First 500 draws are the stored draws of `weights_boot.csv` (asserted) [verified].
- Counts for 1998-2001 reproduce the external reviewer's figures: opposite signs in 7 of 48 months (3 materially at 0.25, 4 near zero), gap of at least 0.25 in 21 of 48; largest gap 0.76 (Jan 1998) [verified; reviewer said "roughly 0.7"].
- 2022-24 point readings 1.02/1.01 (baseline), 1.21/1.04 (two-year), 1.30/1.11 (no lower bound) are those of `21_episodes.csv` [verified by reading].
- Draw count matters: at 5,000 draws the baseline contrast in points is 0.24 [0.003, 0.448] (500 draws: [-0.01, 0.44]); the ratio-of-ratios lower bound is 1.08 (500 draws: 1.04). The 500-draw intervals in the paper's tables are therefore not final.
- Definitions of the categories are fixed in the script header before any number was read [verified: header written first]. Month shares use weights uncertainty only (the 12-month changes are held fixed).
- Not verified independently: the classification is not re-derived outside this script.
