# What changes if the real version, not the r*-gap version, is Note B's baseline (18 Nov 2026)

All from the package's stored results (500 draws, 12 lags, March-December 2020 dropped, no trend), except the real-version EBP and Bauer-Swanson tests (run here: `real_core_missing.py`). Per +1 pp on the 2-year in the window; `**` / `*` = 95 / 90 percent interval excludes zero.

## Figure 1 (two baselines, yield alone and with the FCI): real vs r*-gap

| Sample | Version | FCI | u 12m | u 24m | u 36m | P 12m | P 24m | P 36m |
|---|---|---|---|---|---|---|---|---|
| 1996 | real | no | -0.28* | -0.35* | -0.30* | -0.08 | -0.06 | -0.06 |
| 1996 | real | yes | +0.17* | +0.23* | +0.22 | -0.22* | -0.38* | -0.50* |
| 1996 | r*-gap | no | -0.10 | -0.21 | -0.25 | -0.20* | -0.32 | -0.44 |
| 1996 | r*-gap | yes | +0.41* | +0.45* | +0.40 | -0.38* | -0.69* | -0.94* |
| 1973 | real | no | +0.09 | +0.08 | +0.02 | -0.23* | -0.49* | -0.72* |
| 1973 | real | yes | +0.25* | +0.13 | +0.02 | -0.24* | -0.55* | -0.79* |
| 1973 | r*-gap | no | +0.17* | +0.15 | +0.05 | -0.28* | -0.64* | -0.97* |
| 1973 | r*-gap | yes | +0.33* | +0.24 | +0.15 | -0.32* | -0.76* | -1.14* |

(* here = 90 percent interval excludes zero, from the paths files.)

## Sacrifice ratio at 24 months (-1/kappa; kappa set in brackets from results/tradeoff.csv)

| Sample | real with FCI | r*-gap with FCI |
|---|---|---|
| 1996 | 0.86 (kappa -1.16 [-5.51, -0.25]; ratio about 0.2 to 4.0) | 1.05 (kappa -0.95 [-1.99, -0.32]; ratio about 0.5 to 3.1) |
| 1973 | 0.64 (kappa -1.56 [-3.72, -0.75]; ratio about 0.3 to 1.3) | 0.67 (kappa -1.49 [-2.92, -0.72]; ratio about 0.3 to 1.4) |

## Robustness table (Section 5, 12 months), real vs r*-gap with the FCI

| Test | REAL u 1996 | REAL P 1996 | REAL u 1973 | REAL P 1973 | r*-gap u 1996 | r*-gap P 1996 | r*-gap u 1973 | r*-gap P 1973 |
|---|---|---|---|---|---|---|---|---|
| Baseline | +0.17* | -0.22** | +0.25** | -0.24** | +0.41** | -0.38** | +0.33** | -0.32** |
| 2020 left in | +0.09 | -0.23** | +0.10 | -0.18** | +0.33 | -0.42** | +0.18 | -0.27** |
| Kiley r* | +0.10 | -0.14 | +0.14 | -0.26** | (same) | (same) | (same) | (same) |
| Spline trend (real) | +0.18 | -0.15 | +0.29** | -0.21** | (same) | (same) | (same) | (same) |
| EBP added | +0.06 | -0.16 | +0.16** | -0.23** | +0.39** | -0.33** | +0.22** | -0.31** |
| Components, equities free | +0.04 | -0.15 | +0.30** | -0.26** | +0.35** | -0.26** | +0.32** | -0.30** |
| Bauer-Swanson surprise | +0.20** | -0.23** | +0.28** | -0.24** | +0.46** | -0.39** | +0.36** | -0.33** |
| 3 lags | +0.36** | -0.24** | +0.05 | -0.04 | +0.37** | -0.22 | +0.12 | -0.09 |
| 6 lags | +0.26** | -0.20* | +0.17** | -0.13 | +0.38** | -0.30** | +0.27** | -0.20* |
| IP added | +0.28** | -0.21** | +0.27** | -0.21** | +0.37** | -0.43** | +0.33** | -0.28** |
| Funds rate in daily block | +0.33** | -0.27** | +0.19** | -0.28** | +0.43** | -0.42** | +0.31** | -0.38** |
| LW r*-gap (the current baseline) | +0.41** | -0.38** | +0.33** | -0.32** | - | - | - | - |