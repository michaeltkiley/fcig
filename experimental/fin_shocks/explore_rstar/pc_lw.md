# One-sided filters of the level factor of the yield curve against one-sided LW r*

Target: LW (real yields) and 2-year expected inflation + LW (nominal yields). RMSE of the level, pp. interpolated e5 vs Cleveland 5-year, 1985-2026: RMSE 0.12, corr 1.00.

* nominal: full-sample PC1 loadings (2y, 5y, 10y) = [0.353, 0.335, 0.312], share of variance 0.989
* nominal: one-sided loadings range 2y 0.34-0.36, 5y 0.33-0.34, 10y 0.31-0.33
* real: full-sample PC1 loadings (2y, 5y, 10y) = [0.359, 0.333, 0.308], share of variance 0.969
* real: one-sided loadings range 2y 0.32-0.44, 5y 0.33-0.34, 10y 0.23-0.34

## Best setting per source and filter, fit 1973-2026

| kind | source | filter | param | RMSE | bias | corr | err 1970s | 80s | 90s | 00s | 10s | 20s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| nominal | simple average of 2y, 5y, 10y | none | 0 | 1.53 | -0.35 | 0.90 | -1.73 | +1.61 | +0.28 | -0.99 | -0.99 | -0.88 |
| nominal | PC1, full-sample loadings | none | 0 | 1.54 | -0.37 | 0.90 | -1.74 | +1.60 | +0.27 | -1.01 | -1.02 | -0.89 |
| nominal | PC1, one-sided loadings | none | 0 | 1.54 | -0.36 | 0.90 | -1.73 | +1.61 | +0.28 | -1.01 | -1.03 | -0.89 |
| nominal | simple average of 2y, 5y, 10y | MA | 12 | 1.69 | -0.34 | 0.87 | -1.99 | +1.69 | +0.39 | -0.83 | -0.97 | -1.05 |
| nominal | PC1, full-sample loadings | MA | 12 | 1.69 | -0.35 | 0.87 | -2.00 | +1.68 | +0.38 | -0.85 | -1.00 | -1.05 |
| nominal | PC1, one-sided loadings | MA | 12 | 1.69 | -0.35 | 0.87 | -1.99 | +1.69 | +0.39 | -0.84 | -1.01 | -1.05 |
| nominal | PC1, one-sided loadings | EWMA | 12 | 1.75 | -0.26 | 0.84 | -2.27 | +1.65 | +0.68 | -0.62 | -0.92 | -1.28 |
| nominal | simple average of 2y, 5y, 10y | EWMA | 12 | 1.77 | -0.30 | 0.84 | -2.26 | +1.65 | +0.68 | -0.60 | -0.88 | -1.28 |
| nominal | PC1, full-sample loadings | EWMA | 12 | 1.77 | -0.31 | 0.84 | -2.27 | +1.65 | +0.67 | -0.62 | -0.91 | -1.28 |
| nominal | PC1, one-sided loadings | Butterworth 1 | 120 | 1.78 | -0.25 | 0.83 | -2.32 | +1.64 | +0.73 | -0.57 | -0.89 | -1.33 |
| nominal | 2-year alone | none | 0 | 1.78 | -0.75 | 0.91 | -1.82 | +1.35 | -0.18 | -1.60 | -1.70 | -0.97 |
| nominal | simple average of 2y, 5y, 10y | Butterworth 1 | 120 | 1.79 | -0.29 | 0.83 | -2.31 | +1.64 | +0.74 | -0.56 | -0.85 | -1.32 |
| nominal | PC1, full-sample loadings | Butterworth 1 | 120 | 1.80 | -0.30 | 0.83 | -2.32 | +1.63 | +0.72 | -0.58 | -0.89 | -1.33 |
| nominal | PC1, one-sided loadings | HP | 129600 | 1.86 | -0.32 | 0.86 | -1.79 | +1.84 | +0.25 | -0.92 | -1.20 | -0.95 |
| nominal | 2-year alone | MA | 12 | 1.88 | -0.74 | 0.88 | -2.12 | +1.46 | -0.07 | -1.38 | -1.74 | -1.13 |
| nominal | simple average of 2y, 5y, 10y | HP | 129600 | 1.88 | -0.37 | 0.84 | -2.00 | +1.84 | +0.26 | -0.90 | -1.16 | -0.95 |
| nominal | 2-year alone | EWMA | 12 | 1.88 | -0.70 | 0.85 | -2.42 | +1.44 | +0.21 | -1.11 | -1.68 | -1.39 |
| nominal | PC1, full-sample loadings | HP | 129600 | 1.89 | -0.39 | 0.85 | -2.00 | +1.83 | +0.24 | -0.92 | -1.19 | -0.95 |
| nominal | 2-year alone | Butterworth 1 | 120 | 1.90 | -0.69 | 0.85 | -2.47 | +1.43 | +0.26 | -1.06 | -1.66 | -1.45 |
| nominal | simple average of 2y, 5y, 10y | Butterworth 2 | 120 | 2.07 | -0.26 | 0.77 | -2.45 | +1.74 | +0.85 | -0.41 | -0.81 | -1.57 |
| nominal | PC1, one-sided loadings | Butterworth 2 | 120 | 2.07 | -0.23 | 0.77 | -2.57 | +1.74 | +0.84 | -0.42 | -0.85 | -1.57 |
| nominal | PC1, full-sample loadings | Butterworth 2 | 120 | 2.07 | -0.28 | 0.77 | -2.46 | +1.73 | +0.83 | -0.43 | -0.84 | -1.57 |
| nominal | 2-year alone | HP | 129600 | 2.10 | -0.78 | 0.85 | -2.19 | +1.60 | -0.19 | -1.43 | -1.97 | -0.95 |
| nominal | 2-year alone | Butterworth 2 | 120 | 2.19 | -0.67 | 0.78 | -2.62 | +1.55 | +0.34 | -0.87 | -1.64 | -1.70 |
| real | 2-year alone | EWMA | 180 | 0.65 | -0.09 | 0.72 | -0.72 | -0.39 | +0.34 | +0.03 | +0.51 | -0.66 |
| real | 2-year alone | Butterworth 1 | 1200 | 0.69 | -0.18 | 0.74 | -0.75 | -0.33 | +0.41 | -0.05 | +0.19 | -0.99 |
| real | PC1, full-sample loadings | Butterworth 1 | 1200 | 0.72 | +0.11 | 0.67 | -0.66 | -0.22 | +0.69 | +0.28 | +0.68 | -0.57 |
| real | PC1, full-sample loadings | EWMA | 120 | 0.72 | +0.08 | 0.68 | -0.68 | -0.19 | +0.72 | +0.25 | +0.58 | -0.67 |
| real | simple average of 2y, 5y, 10y | Butterworth 1 | 1200 | 0.72 | +0.12 | 0.67 | -0.66 | -0.21 | +0.70 | +0.30 | +0.71 | -0.55 |
| real | simple average of 2y, 5y, 10y | EWMA | 120 | 0.73 | +0.10 | 0.67 | -0.68 | -0.18 | +0.74 | +0.27 | +0.61 | -0.65 |
| real | PC1, one-sided loadings | Butterworth 1 | 1200 | 0.75 | +0.00 | 0.60 | -0.98 | -0.47 | +0.56 | +0.22 | +0.65 | -0.59 |
| real | PC1, one-sided loadings | EWMA | 180 | 0.75 | +0.03 | 0.56 | -0.95 | -0.59 | +0.39 | +0.22 | +0.88 | -0.30 |
| real | 2-year alone | Butterworth 2 | 960 | 0.80 | +0.08 | 0.53 | -0.59 | -0.60 | +0.32 | +0.40 | +1.08 | -0.55 |
| real | PC1, full-sample loadings | Butterworth 2 | 720 | 0.89 | +0.23 | 0.50 | -0.50 | -0.52 | +0.72 | +0.72 | +1.10 | -0.68 |
| real | simple average of 2y, 5y, 10y | Butterworth 2 | 720 | 0.90 | +0.24 | 0.50 | -0.50 | -0.51 | +0.74 | +0.74 | +1.13 | -0.65 |
| real | PC1, one-sided loadings | Butterworth 2 | 720 | 0.97 | +0.14 | 0.36 | -0.87 | -0.84 | +0.62 | +0.74 | +1.14 | -0.65 |
| real | simple average of 2y, 5y, 10y | MA | 144 | 1.05 | -0.14 | 0.67 | -0.70 | -0.18 | +1.35 | -0.14 | -0.27 | -1.56 |
| real | PC1, full-sample loadings | MA | 144 | 1.05 | -0.16 | 0.67 | -0.70 | -0.19 | +1.32 | -0.16 | -0.31 | -1.58 |
| real | PC1, full-sample loadings | HP | 1296000000 | 1.16 | -0.04 | 0.62 | -1.24 | +0.16 | +1.36 | +0.27 | -0.05 | -1.60 |
| real | simple average of 2y, 5y, 10y | HP | 1296000000 | 1.16 | -0.02 | 0.61 | -1.23 | +0.17 | +1.38 | +0.30 | -0.02 | -1.57 |
| real | 2-year alone | MA | 144 | 1.18 | -0.52 | 0.73 | -0.75 | -0.31 | +0.91 | -0.56 | -0.95 | -2.04 |
| real | 2-year alone | HP | 1296000000 | 1.23 | -0.46 | 0.70 | -1.33 | +0.02 | +0.88 | -0.23 | -0.76 | -2.15 |
| real | PC1, one-sided loadings | MA | 36 | 1.36 | -0.33 | 0.70 | -1.53 | +1.17 | +0.53 | -0.76 | -1.06 | -1.06 |
| real | simple average of 2y, 5y, 10y | none | 0 | 1.55 | -0.36 | 0.64 | -1.75 | +1.63 | +0.26 | -1.03 | -1.06 | -0.78 |
| real | PC1, full-sample loadings | none | 0 | 1.56 | -0.38 | 0.64 | -1.75 | +1.61 | +0.24 | -1.06 | -1.09 | -0.79 |
| real | PC1, one-sided loadings | none | 0 | 1.56 | -0.37 | 0.64 | -1.75 | +1.63 | +0.27 | -1.05 | -1.09 | -0.79 |
| real | PC1, one-sided loadings | HP | 1296000 | 1.58 | -0.42 | 0.68 | -1.96 | +1.58 | +0.29 | -1.00 | -1.29 | -1.02 |
| real | 2-year alone | none | 0 | 1.78 | -0.75 | 0.67 | -1.82 | +1.35 | -0.18 | -1.60 | -1.70 | -0.97 |

## Best setting per source and filter, fit 1996-2026

| kind | source | filter | param | RMSE | bias | corr |
|---|---|---|---|---|---|---|
| nominal | simple average of 2y, 5y, 10y | EWMA | 24 | 1.12 | -0.56 | 0.82 |
| nominal | simple average of 2y, 5y, 10y | Butterworth 1 | 240 | 1.12 | -0.51 | 0.81 |
| nominal | PC1, full-sample loadings | EWMA | 24 | 1.13 | -0.59 | 0.82 |
| nominal | PC1, one-sided loadings | EWMA | 24 | 1.13 | -0.58 | 0.82 |
| nominal | PC1, full-sample loadings | Butterworth 1 | 240 | 1.13 | -0.53 | 0.81 |
| nominal | PC1, one-sided loadings | Butterworth 1 | 240 | 1.13 | -0.53 | 0.81 |
| nominal | simple average of 2y, 5y, 10y | none | 0 | 1.18 | -0.85 | 0.88 |
| nominal | PC1, one-sided loadings | none | 0 | 1.20 | -0.87 | 0.88 |
| nominal | PC1, full-sample loadings | none | 0 | 1.20 | -0.87 | 0.88 |
| nominal | simple average of 2y, 5y, 10y | MA | 12 | 1.20 | -0.83 | 0.86 |
| nominal | PC1, full-sample loadings | MA | 12 | 1.22 | -0.85 | 0.86 |
| nominal | PC1, one-sided loadings | MA | 12 | 1.22 | -0.85 | 0.86 |
| nominal | 2-year alone | EWMA | 84 | 1.23 | +0.15 | 0.72 |
| nominal | 2-year alone | Butterworth 1 | 720 | 1.23 | +0.08 | 0.73 |
| nominal | simple average of 2y, 5y, 10y | Butterworth 2 | 120 | 1.27 | -0.72 | 0.78 |
| nominal | PC1, full-sample loadings | Butterworth 2 | 120 | 1.28 | -0.74 | 0.79 |
| nominal | PC1, one-sided loadings | Butterworth 2 | 120 | 1.28 | -0.74 | 0.79 |
| nominal | simple average of 2y, 5y, 10y | HP | 129600 | 1.31 | -0.89 | 0.83 |
| nominal | PC1, full-sample loadings | HP | 129600 | 1.33 | -0.91 | 0.83 |
| nominal | PC1, one-sided loadings | HP | 129600 | 1.33 | -0.91 | 0.83 |
| nominal | 2-year alone | MA | 144 | 1.49 | -0.66 | 0.74 |
| nominal | 2-year alone | Butterworth 2 | 240 | 1.62 | -1.00 | 0.74 |
| nominal | 2-year alone | none | 0 | 1.70 | -1.32 | 0.86 |
| nominal | 2-year alone | HP | 129600 | 1.82 | -1.34 | 0.81 |
| real | 2-year alone | EWMA | 180 | 0.66 | +0.04 | 0.68 |
| real | 2-year alone | Butterworth 1 | 1200 | 0.70 | -0.17 | 0.70 |
| real | PC1, one-sided loadings | EWMA | 120 | 0.70 | +0.14 | 0.68 |
| real | PC1, one-sided loadings | Butterworth 1 | 960 | 0.71 | +0.07 | 0.69 |
| real | PC1, full-sample loadings | Butterworth 1 | 960 | 0.71 | +0.09 | 0.69 |
| real | PC1, full-sample loadings | EWMA | 120 | 0.71 | +0.17 | 0.68 |
| real | simple average of 2y, 5y, 10y | Butterworth 1 | 960 | 0.72 | +0.12 | 0.69 |
| real | simple average of 2y, 5y, 10y | EWMA | 120 | 0.72 | +0.19 | 0.68 |
| real | 2-year alone | Butterworth 2 | 960 | 0.89 | +0.38 | 0.52 |
| real | simple average of 2y, 5y, 10y | MA | 144 | 0.95 | -0.41 | 0.71 |
| real | PC1, full-sample loadings | MA | 144 | 0.96 | -0.43 | 0.71 |
| real | PC1, one-sided loadings | MA | 144 | 0.97 | -0.42 | 0.71 |
| real | simple average of 2y, 5y, 10y | Butterworth 2 | 480 | 0.99 | +0.08 | 0.66 |
| real | PC1, full-sample loadings | Butterworth 2 | 480 | 0.99 | +0.05 | 0.66 |
| real | simple average of 2y, 5y, 10y | HP | 1296000000 | 1.00 | -0.14 | 0.69 |
| real | PC1, full-sample loadings | HP | 1296000000 | 1.00 | -0.17 | 0.70 |
| real | PC1, one-sided loadings | Butterworth 2 | 480 | 1.01 | +0.08 | 0.66 |
| real | PC1, one-sided loadings | HP | 1296000000 | 1.09 | -0.22 | 0.71 |
| real | simple average of 2y, 5y, 10y | none | 0 | 1.20 | -0.87 | 0.72 |
| real | PC1, one-sided loadings | none | 0 | 1.22 | -0.89 | 0.72 |
| real | PC1, full-sample loadings | none | 0 | 1.22 | -0.90 | 0.72 |
| real | 2-year alone | HP | 1296000000 | 1.25 | -0.75 | 0.72 |
| real | 2-year alone | MA | 144 | 1.28 | -0.93 | 0.73 |
| real | 2-year alone | none | 0 | 1.70 | -1.32 | 0.68 |

## Findings (18 Nov 2026)

* **The level factor is practically an equal-weighted average of the three yields.** PC1 explains 99 percent of the variance of the nominal yields and 97 percent of the real ones, with loadings of about 0.36 / 0.33 / 0.31 on the 2-, 5- and 10-year yields. One-sided (expanding-window) loadings stay within 0.32-0.44 (2-year) and 0.23-0.34 (10-year), so full-sample, one-sided and simple-average versions give the same answers to within 0.03 pp.
* **Real level factor: as good as the 2-year, not better.** The best one-sided filter is an EWMA with a half-life of 120 months (RMSE 0.72 against LW, 1973-2026; 0.70 over 1996-2026), against 0.65 / 0.66 for the EWMA 180 of the real 2-year alone. The level factor needs less smoothing (the 5- and 10-year yields are already smoother) but sits higher in the 1990s-2010s (term premium: errors +0.7 in the 1990s, +0.6 in the 2010s) and does not improve the 1970s (-0.7). Moving averages and one-sided HP are worse, as for the 2-year (MA 144: 1.05; HP: 1.16).
* **Nominal level factor: no trend of it tracks 2-year expected inflation + LW** (best RMSE 1.53, unfiltered; 1.12 over 1996-2026), as for the nominal 2-year: the nominal target moves with inflation expectations, and filtering only adds lag.
* 5-year expected inflation: Cleveland Fed from 1982; before, interpolated by maturity between e2 and e10 (the interpolation matches Cleveland to 0.12 pp RMSE over 1985-2026).
