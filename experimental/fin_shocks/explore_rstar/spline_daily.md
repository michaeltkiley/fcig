# Real version with the FCI, cubic spline in the monthly equations only or in the monthly and daily equations (12 lags, 500 draws)

Per +1 pp on the 2-year in the window: u = unemployment gap (pp), P = price level (percent). `**` / `*`: 95 / 90 percent interval excludes zero; 90 percent intervals in brackets. Monthly spline knots: from 1996 1996-01, 2001-03, 2007-12, 2020-02, 2026-09; from 1973 1974-01, 1980-01, 1981-07, 1990-07, 2001-03, 2007-12, 2020-02, 2026-09. Daily spline (daily block, 1996-2026 in both): 1996-01, 2001-03, 2007-12, 2020-02, 2026-09. No-trend rows: the package's real baseline.

## From 1996

| trend | u 12m | u 24m | u 36m | P 12m | P 24m | P 36m |
|---|---|---|---|---|---|---|
| no trend | +0.17* [+0.01, +0.35] | +0.23* [+0.00, +0.50] | +0.22 [-0.04, +0.57] | -0.22** [-0.38, -0.05] | -0.38** [-0.75, -0.07] | -0.50* [-1.03, -0.05] |
| spline, monthly equations only | +0.18 [-0.08, +0.31] | +0.20 [-0.18, +0.44] | +0.18 [-0.22, +0.44] | -0.15 [-0.31, +0.09] | -0.29 [-0.67, +0.17] | -0.39 [-0.91, +0.23] |
| spline, monthly and daily equations | +0.14 [-0.10, +0.25] | +0.13 [-0.20, +0.32] | +0.09 [-0.15, +0.27] | -0.12 [-0.28, +0.09] | -0.21 [-0.54, +0.13] | -0.24 [-0.64, +0.17] |

## From 1973

| trend | u 12m | u 24m | u 36m | P 12m | P 24m | P 36m |
|---|---|---|---|---|---|---|
| no trend | +0.25** [+0.11, +0.35] | +0.13 [-0.07, +0.26] | +0.02 [-0.15, +0.17] | -0.24** [-0.33, -0.11] | -0.55** [-0.69, -0.25] | -0.79** [-1.01, -0.31] |
| spline, monthly equations only | +0.28** [+0.13, +0.40] | +0.23* [+0.01, +0.43] | +0.12 [-0.10, +0.36] | -0.23** [-0.34, -0.10] | -0.58** [-0.78, -0.29] | -0.80** [-1.10, -0.37] |
| spline, monthly and daily equations | +0.23** [+0.09, +0.36] | +0.12 [-0.07, +0.33] | +0.03 [-0.10, +0.20] | -0.20** [-0.30, -0.09] | -0.43** [-0.63, -0.22] | -0.51** [-0.79, -0.20] |
