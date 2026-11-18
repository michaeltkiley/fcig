# Quick read: 8-year moving-average r* under three trend treatments (point estimates, no bootstrap)

Per +1 pp on the 2-year in the window: unemployment gap (pp), price level (percent). 2020 (March-December) dropped. Point estimates only; no intervals.

## 12 lags

| Start | FCI | r* | trend | u 12m | u 24m | P 12m | P 24m |
|---|---|---|---|---|---|---|---|
| 1996 | no FCI | HP one-sided, q1600 (m129600), real | none | -0.24 | -0.47 | -0.11 | -0.26 |
| 1996 | with FCI | HP one-sided, q1600 (m129600), real | none | +0.04 | -0.00 | -0.26 | -0.57 |
| 1996 | no FCI | HP one-sided, q1600 (m129600), real | spline | -0.27 | -0.54 | -0.03 | -0.06 |
| 1996 | with FCI | HP one-sided, q1600 (m129600), real | spline | +0.07 | -0.09 | -0.13 | -0.24 |
| 1996 | no FCI | HP one-sided, q1600 (m129600), real | quad | -0.34 | -0.62 | -0.04 | -0.11 |
| 1996 | with FCI | HP one-sided, q1600 (m129600), real | quad | +0.04 | -0.01 | -0.16 | -0.34 |
| 1973 | no FCI | HP one-sided, q1600 (m129600), real | none | +0.06 | +0.09 | -0.17 | -0.41 |
| 1973 | with FCI | HP one-sided, q1600 (m129600), real | none | +0.14 | +0.14 | -0.21 | -0.52 |
| 1973 | no FCI | HP one-sided, q1600 (m129600), real | spline | -0.01 | -0.03 | -0.06 | -0.13 |
| 1973 | with FCI | HP one-sided, q1600 (m129600), real | spline | +0.12 | +0.07 | -0.11 | -0.22 |
| 1973 | no FCI | HP one-sided, q1600 (m129600), real | quad | +0.02 | +0.05 | -0.02 | +0.01 |
| 1973 | with FCI | HP one-sided, q1600 (m129600), real | quad | +0.08 | +0.03 | -0.06 | -0.11 |
| 1996 | no FCI | HP one-sided, q16000 (m1296000), real | none | -0.26 | -0.43 | -0.14 | -0.30 |
| 1996 | with FCI | HP one-sided, q16000 (m1296000), real | none | +0.08 | +0.06 | -0.30 | -0.62 |
| 1996 | no FCI | HP one-sided, q16000 (m1296000), real | spline | -0.36 | -0.59 | -0.04 | -0.08 |
| 1996 | with FCI | HP one-sided, q16000 (m1296000), real | spline | -0.00 | -0.21 | -0.13 | -0.24 |
| 1996 | no FCI | HP one-sided, q16000 (m1296000), real | quad | -0.34 | -0.50 | -0.09 | -0.21 |
| 1996 | with FCI | HP one-sided, q16000 (m1296000), real | quad | +0.04 | -0.01 | -0.19 | -0.41 |
| 1973 | no FCI | HP one-sided, q16000 (m1296000), real | none | +0.08 | +0.12 | -0.20 | -0.50 |
| 1973 | with FCI | HP one-sided, q16000 (m1296000), real | none | +0.13 | +0.10 | -0.23 | -0.57 |
| 1973 | no FCI | HP one-sided, q16000 (m1296000), real | spline | +0.04 | +0.08 | -0.12 | -0.31 |
| 1973 | with FCI | HP one-sided, q16000 (m1296000), real | spline | +0.11 | +0.04 | -0.14 | -0.29 |
| 1973 | no FCI | HP one-sided, q16000 (m1296000), real | quad | +0.05 | +0.10 | -0.05 | -0.10 |
| 1973 | with FCI | HP one-sided, q16000 (m1296000), real | quad | +0.08 | +0.01 | -0.09 | -0.19 |
| 1996 | no FCI | HP one-sided, q1600 (m129600), nominal | none | -0.32 | -0.55 | +0.01 | -0.11 |
| 1996 | with FCI | HP one-sided, q1600 (m129600), nominal | none | +0.02 | -0.06 | -0.12 | -0.37 |
| 1996 | no FCI | HP one-sided, q1600 (m129600), nominal | spline | -0.34 | -0.61 | +0.07 | +0.07 |
| 1996 | with FCI | HP one-sided, q1600 (m129600), nominal | spline | +0.01 | -0.20 | +0.02 | -0.03 |
| 1996 | no FCI | HP one-sided, q1600 (m129600), nominal | quad | -0.41 | -0.68 | +0.06 | +0.02 |
| 1996 | with FCI | HP one-sided, q1600 (m129600), nominal | quad | -0.02 | -0.15 | +0.01 | -0.10 |
| 1973 | no FCI | HP one-sided, q1600 (m129600), nominal | none | +0.03 | +0.09 | +0.02 | -0.01 |
| 1973 | with FCI | HP one-sided, q1600 (m129600), nominal | none | +0.17 | +0.24 | +0.00 | -0.18 |
| 1973 | no FCI | HP one-sided, q1600 (m129600), nominal | spline | -0.12 | -0.19 | +0.04 | +0.09 |
| 1973 | with FCI | HP one-sided, q1600 (m129600), nominal | spline | +0.09 | +0.05 | +0.00 | -0.02 |
| 1973 | no FCI | HP one-sided, q1600 (m129600), nominal | quad | -0.00 | +0.05 | +0.13 | +0.32 |
| 1973 | with FCI | HP one-sided, q1600 (m129600), nominal | quad | +0.10 | +0.10 | +0.11 | +0.18 |
| 1996 | no FCI | HP one-sided, q16000 (m1296000), nominal | none | -0.34 | -0.51 | -0.05 | -0.18 |
| 1996 | with FCI | HP one-sided, q16000 (m1296000), nominal | none | +0.05 | -0.00 | -0.18 | -0.45 |
| 1996 | no FCI | HP one-sided, q16000 (m1296000), nominal | spline | -0.43 | -0.66 | +0.05 | +0.02 |
| 1996 | with FCI | HP one-sided, q16000 (m1296000), nominal | spline | -0.07 | -0.33 | -0.00 | -0.09 |
| 1996 | no FCI | HP one-sided, q16000 (m1296000), nominal | quad | -0.41 | -0.57 | +0.00 | -0.11 |
| 1996 | with FCI | HP one-sided, q16000 (m1296000), nominal | quad | -0.01 | -0.12 | -0.05 | -0.26 |
| 1973 | no FCI | HP one-sided, q16000 (m1296000), nominal | none | +0.06 | +0.17 | -0.01 | -0.15 |
| 1973 | with FCI | HP one-sided, q16000 (m1296000), nominal | none | +0.18 | +0.23 | -0.02 | -0.28 |
| 1973 | no FCI | HP one-sided, q16000 (m1296000), nominal | spline | -0.04 | +0.01 | -0.03 | -0.14 |
| 1973 | with FCI | HP one-sided, q16000 (m1296000), nominal | spline | +0.16 | +0.18 | -0.04 | -0.19 |
| 1973 | no FCI | HP one-sided, q16000 (m1296000), nominal | quad | +0.04 | +0.16 | +0.13 | +0.25 |
| 1973 | with FCI | HP one-sided, q16000 (m1296000), nominal | quad | +0.11 | +0.10 | +0.11 | +0.11 |
