# 08_stance: reproduction check

Compared every table with `followup2/stance/out/` (corr, insample, oos, primary, boot_insample, components, episode_rank, diff_series, episodes) cell by cell at REPS=500 (weights_boot.csv has 500 draws).
Maximum absolute difference: 0.0 in every table (bit-identical). One porting detail: the original out-of-sample loop stops at origin 2025-09 (the unemployment sample ends there); the shared `oos()` takes `last="2025-09"` here to reproduce that for payrolls (otherwise one extra origin, n 331 vs 330 in some cells).
New in the package (no follow-up counterpart): `08_today.csv`, the latest month's index minus the funds-rate gap (r* step, both demeaned over 1973-2026), weights-bootstrap interval, Kiley r*. It reproduces the FP-A12 readings (Market -0.93, GS -1.23, FRB/US +0.27 for the index; gap +0.46; differences -1.39, -1.69, -0.19).
The out-of-sample and episode numbers match RESULT.md (primary: unemployment mixed CW 2.31, Holm p 0.095; 2004-06 -1.29 [-1.86, -0.65]; 2022-24 -1.40 [-2.22, -0.39]).
Run time: about 4 minutes. Deterministic: a second run gives identical CSVs (md5).
