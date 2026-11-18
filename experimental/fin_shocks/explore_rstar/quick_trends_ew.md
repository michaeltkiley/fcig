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
| 1996 | no FCI | EWMA 180 real 2-year | none | -0.34 | -0.48 | -0.02 | +0.09 |
| 1996 | with FCI | EWMA 180 real 2-year | none | +0.07 | +0.01 | -0.04 | +0.11 |
| 1996 | no FCI | EWMA 180 real 2-year | spline | -0.31 | -0.32 | -0.04 | -0.07 |
| 1996 | with FCI | EWMA 180 real 2-year | spline | +0.20 | +0.27 | -0.10 | -0.16 |
| 1996 | no FCI | EWMA 180 real 2-year | quad | -0.25 | -0.19 | -0.09 | -0.16 |
| 1996 | with FCI | EWMA 180 real 2-year | quad | +0.26 | +0.51 | -0.12 | -0.18 |
| 1973 | no FCI | EWMA 180 real 2-year | none | +0.08 | +0.06 | -0.23 | -0.50 |
| 1973 | with FCI | EWMA 180 real 2-year | none | +0.17 | +0.13 | -0.25 | -0.55 |
| 1973 | no FCI | EWMA 180 real 2-year | spline | +0.12 | +0.20 | -0.15 | -0.33 |
| 1973 | with FCI | EWMA 180 real 2-year | spline | +0.19 | +0.19 | -0.20 | -0.40 |
| 1973 | no FCI | EWMA 180 real 2-year | quad | +0.05 | +0.03 | -0.11 | -0.24 |
| 1973 | with FCI | EWMA 180 real 2-year | quad | +0.13 | +0.05 | -0.14 | -0.29 |
