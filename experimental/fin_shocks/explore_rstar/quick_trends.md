# Quick read: 8-year moving-average r* under three trend treatments (point estimates, no bootstrap)

Per +1 pp on the 2-year in the window: unemployment gap (pp), price level (percent). 2020 (March-December) dropped. Point estimates only; no intervals.

## 12 lags

| Start | FCI | r* | trend | u 12m | u 24m | P 12m | P 24m |
|---|---|---|---|---|---|---|---|
| 1996 | no FCI | LW (baseline) | none | -0.10 | -0.21 | -0.20 | -0.32 |
| 1996 | with FCI | LW (baseline) | none | +0.41 | +0.45 | -0.38 | -0.69 |
| 1996 | no FCI | LW (baseline) | spline | -0.15 | -0.22 | -0.20 | -0.45 |
| 1996 | with FCI | LW (baseline) | spline | +0.38 | +0.42 | -0.43 | -0.98 |
| 1996 | no FCI | LW (baseline) | quad | -0.09 | -0.05 | -0.21 | -0.46 |
| 1996 | with FCI | LW (baseline) | quad | +0.40 | +0.50 | -0.38 | -0.78 |
| 1973 | no FCI | LW (baseline) | none | +0.18 | +0.15 | -0.28 | -0.64 |
| 1973 | with FCI | LW (baseline) | none | +0.33 | +0.24 | -0.32 | -0.76 |
| 1973 | no FCI | LW (baseline) | spline | +0.18 | +0.24 | -0.19 | -0.45 |
| 1973 | with FCI | LW (baseline) | spline | +0.29 | +0.22 | -0.25 | -0.57 |
| 1973 | no FCI | LW (baseline) | quad | +0.16 | +0.14 | -0.15 | -0.34 |
| 1973 | with FCI | LW (baseline) | quad | +0.28 | +0.13 | -0.18 | -0.40 |
| 1996 | no FCI | MA8 real 2-year | none | -0.27 | -0.37 | -0.08 | -0.02 |
| 1996 | with FCI | MA8 real 2-year | none | +0.13 | +0.16 | -0.21 | -0.29 |
| 1996 | no FCI | MA8 real 2-year | spline | -0.31 | -0.33 | -0.03 | -0.03 |
| 1996 | with FCI | MA8 real 2-year | spline | +0.21 | +0.37 | -0.07 | -0.06 |
| 1996 | no FCI | MA8 real 2-year | quad | -0.26 | -0.25 | -0.12 | -0.23 |
| 1996 | with FCI | MA8 real 2-year | quad | +0.11 | +0.21 | -0.22 | -0.42 |
| 1973 | no FCI | MA8 real 2-year | none | +0.10 | +0.09 | -0.22 | -0.51 |
| 1973 | with FCI | MA8 real 2-year | none | +0.16 | +0.15 | -0.24 | -0.56 |
| 1973 | no FCI | MA8 real 2-year | spline | +0.10 | +0.18 | -0.15 | -0.35 |
| 1973 | with FCI | MA8 real 2-year | spline | +0.16 | +0.16 | -0.18 | -0.37 |
| 1973 | no FCI | MA8 real 2-year | quad | +0.08 | +0.09 | -0.10 | -0.22 |
| 1973 | with FCI | MA8 real 2-year | quad | +0.13 | +0.10 | -0.12 | -0.26 |
| 1996 | no FCI | MA8 nominal 2-year | none | -0.34 | -0.43 | +0.01 | +0.11 |
| 1996 | with FCI | MA8 nominal 2-year | none | +0.13 | +0.14 | -0.08 | -0.09 |
| 1996 | no FCI | MA8 nominal 2-year | spline | -0.37 | -0.38 | +0.05 | +0.06 |
| 1996 | with FCI | MA8 nominal 2-year | spline | +0.25 | +0.49 | +0.03 | +0.04 |
| 1996 | no FCI | MA8 nominal 2-year | quad | -0.32 | -0.30 | -0.05 | -0.16 |
| 1996 | with FCI | MA8 nominal 2-year | quad | +0.13 | +0.27 | -0.14 | -0.39 |
| 1973 | no FCI | MA8 nominal 2-year | none | +0.10 | +0.18 | -0.03 | -0.13 |
| 1973 | with FCI | MA8 nominal 2-year | none | +0.23 | +0.29 | -0.02 | -0.20 |
| 1973 | no FCI | MA8 nominal 2-year | spline | +0.07 | +0.22 | -0.08 | -0.25 |
| 1973 | with FCI | MA8 nominal 2-year | spline | +0.24 | +0.37 | -0.09 | -0.30 |
| 1973 | no FCI | MA8 nominal 2-year | quad | +0.11 | +0.25 | +0.11 | +0.12 |
| 1973 | with FCI | MA8 nominal 2-year | quad | +0.19 | +0.26 | +0.10 | +0.05 |
