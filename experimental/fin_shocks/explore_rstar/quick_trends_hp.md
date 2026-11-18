# Quick read: 8-year moving-average r* under three trend treatments (point estimates, no bootstrap)

Per +1 pp on the 2-year in the window: unemployment gap (pp), price level (percent). 2020 (March-December) dropped. Point estimates only; no intervals.

## 12 lags

| Start | FCI | r* | trend | u 12m | u 24m | P 12m | P 24m |
|---|---|---|---|---|---|---|---|
| 1996 | no FCI | HP one-sided 1600, real | none | -0.11 | -0.32 | -0.00 | -0.02 |
| 1996 | with FCI | HP one-sided 1600, real | none | +0.13 | +0.18 | -0.18 | -0.38 |
| 1996 | no FCI | HP one-sided 1600, real | spline | -0.09 | -0.29 | +0.01 | +0.03 |
| 1996 | with FCI | HP one-sided 1600, real | spline | +0.21 | +0.26 | -0.12 | -0.23 |
| 1996 | no FCI | HP one-sided 1600, real | quad | -0.14 | -0.42 | +0.04 | +0.11 |
| 1996 | with FCI | HP one-sided 1600, real | quad | +0.20 | +0.26 | -0.12 | -0.20 |
| 1973 | no FCI | HP one-sided 1600, real | none | +0.04 | +0.08 | -0.16 | -0.36 |
| 1973 | with FCI | HP one-sided 1600, real | none | +0.25 | +0.39 | -0.19 | -0.48 |
| 1973 | no FCI | HP one-sided 1600, real | spline | +0.01 | +0.04 | -0.05 | -0.06 |
| 1973 | with FCI | HP one-sided 1600, real | spline | +0.22 | +0.28 | -0.12 | -0.23 |
| 1973 | no FCI | HP one-sided 1600, real | quad | +0.01 | +0.05 | -0.06 | -0.07 |
| 1973 | with FCI | HP one-sided 1600, real | quad | +0.19 | +0.27 | -0.09 | -0.17 |
| 1996 | no FCI | HP one-sided 16000, real | none | -0.18 | -0.44 | -0.06 | -0.18 |
| 1996 | with FCI | HP one-sided 16000, real | none | +0.03 | +0.01 | -0.19 | -0.45 |
| 1996 | no FCI | HP one-sided 16000, real | spline | -0.20 | -0.49 | -0.02 | -0.05 |
| 1996 | with FCI | HP one-sided 16000, real | spline | +0.18 | +0.15 | -0.13 | -0.28 |
| 1996 | no FCI | HP one-sided 16000, real | quad | -0.27 | -0.62 | +0.00 | -0.01 |
| 1996 | with FCI | HP one-sided 16000, real | quad | +0.09 | +0.07 | -0.11 | -0.24 |
| 1973 | no FCI | HP one-sided 16000, real | none | +0.05 | +0.09 | -0.15 | -0.34 |
| 1973 | with FCI | HP one-sided 16000, real | none | +0.17 | +0.22 | -0.21 | -0.50 |
| 1973 | no FCI | HP one-sided 16000, real | spline | +0.01 | -0.00 | -0.03 | -0.03 |
| 1973 | with FCI | HP one-sided 16000, real | spline | +0.15 | +0.16 | -0.10 | -0.20 |
| 1973 | no FCI | HP one-sided 16000, real | quad | +0.02 | +0.05 | -0.02 | +0.03 |
| 1973 | with FCI | HP one-sided 16000, real | quad | +0.11 | +0.10 | -0.07 | -0.10 |
| 1996 | no FCI | HP one-sided 1600, nominal | none | -0.19 | -0.42 | +0.14 | +0.20 |
| 1996 | with FCI | HP one-sided 1600, nominal | none | +0.05 | +0.02 | +0.02 | -0.07 |
| 1996 | no FCI | HP one-sided 1600, nominal | spline | -0.15 | -0.37 | +0.12 | +0.14 |
| 1996 | with FCI | HP one-sided 1600, nominal | spline | +0.12 | +0.09 | +0.04 | -0.02 |
| 1996 | no FCI | HP one-sided 1600, nominal | quad | -0.18 | -0.46 | +0.15 | +0.24 |
| 1996 | with FCI | HP one-sided 1600, nominal | quad | +0.12 | +0.07 | +0.07 | +0.06 |
| 1973 | no FCI | HP one-sided 1600, nominal | none | -0.00 | +0.02 | +0.03 | +0.12 |
| 1973 | with FCI | HP one-sided 1600, nominal | none | +0.17 | +0.24 | +0.05 | +0.04 |
| 1973 | no FCI | HP one-sided 1600, nominal | spline | -0.04 | -0.06 | +0.02 | +0.07 |
| 1973 | with FCI | HP one-sided 1600, nominal | spline | +0.13 | +0.11 | -0.02 | -0.04 |
| 1973 | no FCI | HP one-sided 1600, nominal | quad | -0.01 | +0.01 | +0.06 | +0.18 |
| 1973 | with FCI | HP one-sided 1600, nominal | quad | +0.15 | +0.18 | +0.06 | +0.13 |
| 1996 | no FCI | HP one-sided 16000, nominal | none | -0.25 | -0.52 | +0.08 | +0.02 |
| 1996 | with FCI | HP one-sided 16000, nominal | none | +0.01 | -0.05 | -0.04 | -0.22 |
| 1996 | no FCI | HP one-sided 16000, nominal | spline | -0.26 | -0.56 | +0.09 | +0.09 |
| 1996 | with FCI | HP one-sided 16000, nominal | spline | +0.12 | +0.02 | +0.02 | -0.05 |
| 1996 | no FCI | HP one-sided 16000, nominal | quad | -0.31 | -0.66 | +0.12 | +0.14 |
| 1996 | with FCI | HP one-sided 16000, nominal | quad | +0.04 | -0.06 | +0.07 | +0.03 |
| 1973 | no FCI | HP one-sided 16000, nominal | none | +0.01 | +0.05 | +0.05 | +0.13 |
| 1973 | with FCI | HP one-sided 16000, nominal | none | +0.15 | +0.22 | +0.02 | -0.09 |
| 1973 | no FCI | HP one-sided 16000, nominal | spline | -0.07 | -0.15 | +0.04 | +0.12 |
| 1973 | with FCI | HP one-sided 16000, nominal | spline | +0.09 | +0.04 | -0.01 | -0.03 |
| 1973 | no FCI | HP one-sided 16000, nominal | quad | -0.01 | +0.02 | +0.11 | +0.30 |
| 1973 | with FCI | HP one-sided 16000, nominal | quad | +0.10 | +0.09 | +0.09 | +0.18 |
