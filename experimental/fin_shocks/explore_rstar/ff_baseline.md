# Funds rate and 2-year in the model (package panel R8) as the baseline: nominal and real (18 Nov 2026)

From the package's stored results (R8: the funds rate, in the same version as the 2-year, as a third daily variable and in the monthly equations; on the announcement day it moves by its window response, 0.72 per +1 pp on the 2-year). 12 lags, 500 draws, 2020 dropped, no trend. Per +1 pp on the 2-year in the window. `**` / `*` = 95 / 90 percent. Sacrifice ratio = -1/kappa at 24 months, set from the kappa set in results/tradeoff.csv.

| Sample | Version | FCI | Model | u 12m | u 24m | u 36m | P 12m | P 24m | P 36m | Sacrifice ratio 24m [set] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1996 | nominal | yes | 2-year only | +0.13 | +0.16 | +0.16 | -0.14 | -0.29 | -0.42 | 0.83 [unbounded] |
| 1996 | nominal | yes | 2-year + funds | +0.27* | +0.40** | +0.41* | -0.18 | -0.49* | -0.68 | 0.98 [0.27, 11] |
| 1996 | real | yes | 2-year only | +0.17* | +0.23* | +0.22 | -0.22** | -0.38** | -0.50* | 0.86 [0.18, 4.0] |
| 1996 | real | yes | 2-year + funds | +0.33** | +0.40** | +0.41** | -0.27** | -0.49** | -0.61* | 1.18 [0.62, 3.8] |
| 1996 | nominal | no | 2-year + funds | -0.38** | -0.35** | -0.29 | +0.06 | -0.05 | -0.08 | - |
| 1996 | real | no | 2-year + funds | -0.24** | -0.33** | -0.25 | -0.07 | -0.06 | -0.05 | - |
| 1973 | nominal | yes | 2-year only | +0.29** | +0.19 | +0.06 | -0.01 | -0.17 | -0.33 | 2.44 [unbounded on one side] |
| 1973 | nominal | yes | 2-year + funds | +0.13 | +0.12 | +0.10 | -0.08 | -0.22 | -0.32 | 0.90 [unbounded] |
| 1973 | real | yes | 2-year only | +0.25** | +0.13 | +0.02 | -0.24** | -0.55** | -0.79** | 0.64 [0.27, 1.3] |
| 1973 | real | yes | 2-year + funds | +0.19** | +0.19 | +0.17 | -0.28** | -0.56** | -0.73** | 0.54 [0.19, 1.3] |
| 1973 | nominal | no | 2-year + funds | +0.01 | +0.13 | +0.23* | -0.07 | -0.11 | -0.11 | - |
| 1973 | real | no | 2-year + funds | +0.03 | +0.11 | +0.20* | -0.28** | -0.53** | -0.70** | - |
| 1996 | r*-gap (reference) | yes | 2-year + funds | +0.43** | +0.49** | +0.49* | -0.42** | -0.81** | -1.04** | 0.94 [0.51, 1.9] |
| 1973 | r*-gap (reference) | yes | 2-year + funds | +0.31** | +0.39** | +0.36* | -0.38** | -0.75** | -0.97** | 0.76 [0.41, 1.9] |
