# What each trend absorbs (real case with the FCI, 12 lags, Note B's estimation months)

## From 1996 (359 months, 1996-01 to 2026-09; NBER peaks inside: 2001-03, 2007-12, 2020-02)

| trend | parameters | R^2 on trend alone: u | pi | real 2-year | real FCI | added R^2 in the u equation (12 lags) | in the pi equation | share of remaining u variance | of remaining pi variance |
|---|---|---|---|---|---|---|---|---|---|
| quadratic | 2 | 0.31 | 0.18 | 0.60 | 0.12 | 0.000 | 0.005 | 0.02 | 0.01 |
| cubic spline | 4 | 0.55 | 0.20 | 0.63 | 0.32 | 0.000 | 0.014 | 0.03 | 0.02 |
| level jumps at peaks | 3 | 0.33 | 0.31 | 0.66 | 0.20 | 0.000 | 0.039 | 0.02 | 0.07 |

## From 1973 (623 months, 1974-01 to 2026-09; NBER peaks inside: 1973-11, 1980-01, 1981-07, 1990-07, 2001-03, 2007-12, 2020-02)

| trend | parameters | R^2 on trend alone: u | pi | real 2-year | real FCI | added R^2 in the u equation (12 lags) | in the pi equation | share of remaining u variance | of remaining pi variance |
|---|---|---|---|---|---|---|---|---|---|
| quadratic | 2 | 0.02 | 0.62 | 0.31 | 0.65 | 0.000 | 0.006 | 0.00 | 0.02 |
| cubic spline | 8 | 0.38 | 0.68 | 0.75 | 0.92 | 0.000 | 0.023 | 0.04 | 0.08 |
| level jumps at peaks | 6 | 0.20 | 0.66 | 0.75 | 0.79 | 0.000 | 0.011 | 0.02 | 0.04 |

From 1996: correlation of the spline-alone fit of the unemployment gap with the gap itself 0.74; sd of the fit 1.17 vs sd of the gap 1.59.
From 1973: correlation of the spline-alone fit of the unemployment gap with the gap itself 0.62; sd of the fit 0.90 vs sd of the gap 1.45.