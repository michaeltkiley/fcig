# One-sided trends that track one-sided Laubach-Williams r*

Target: LW r* (real filters) and 2-year expected inflation + LW (nominal filters; the nominal neutral 2-year that the baseline subtracts). One-sided filters of monthly averages. RMSE of the level in pp (no rescaling); bias = mean(filter - target); errors 2008-15 and 2016-26 = mean error in those years. Burn-in 36 months for EWMA and HP; HP lambda is monthly (quarterly x 81).


## Findings (18 Nov 2026)

* **Real rates track LW; nominal rates do not track 2-year expected inflation + LW.** The best real filter (RMSE 0.65 pp, 1973-2026) is as close to LW as Kiley's r* is (0.63). The best nominal filters (RMSE 1.6-2.0) are nearly the current rate (3-6 month windows): the nominal target moves with expected inflation (the 1970s-80s), which any slow trend of the nominal rate misses, and a fast one is not a trend.
* **The best one-sided trend is very slow:** an exponentially weighted average of the real 2-year with a half-life of about 15 years (180 months; 120-240 within 0.08 of the best). Real funds rate: same (half-life 20 years, RMSE 0.75). Real 10-year: half-life 10 years (0.89), biased up (term premium). Fit 1996-2026 the ordering is the same (real 2-year EWMA 180: 0.66).
* **Moving averages and one-sided HP are worse** at any window: the best MA of the real 2-year (144 months, the longest the 1973 sample allows) has RMSE 1.18 and falls 1-2 pp below LW after 2008 (it averages the post-2008 negative real rates fully; LW, and the long EWMA that still remembers the 1990s, fall less). One-sided HP improves monotonically with lambda up to the largest value tried (monthly 1.3e10, RMSE 1.12), i.e. towards a recursively fitted linear trend: what tracks LW is a slow decline, not a cyclical trend. The 8-year MA (real, RMSE 1.29) and the quarterly-1600 HP (1.81) used earlier are poor approximations.
* **Benchmarks:** a constant has RMSE 0.92; an in-sample linear time trend 0.57 (LW falls about 0.47 pp per decade over 1973-2026). So the best rate filter beats a constant clearly but is no better than a straight line; much of what LW does over this sample is a smooth decline.
* **Errors of the best filter (EWMA 180, real 2-year)** by decade: 1970s -0.7, 1980s -0.4, 1990s +0.3, 2000s 0.0, 2010s +0.5, 2020s -0.7. It is too low in the inflationary 1970s and since 2020 (negative real rates in 2020-22) and too high in the 2010s.
* **Caveats.** The long EWMA depends on the start of the data (initialized in June 1961): starting it in 1966 gives RMSE 0.61, in 1970 0.84. LW is quarterly, interpolated to months, and is itself one-sided but estimated on the full sample's parameters, so "tracking LW" partly means tracking a smooth model output. The affine refinements (a + b x filter) fitted in-sample improve little (0.64); fitted on 1973-95 and applied to 1996-2026 they are worse (1.4-1.8).

## Best parameter per rate and filter, fit over 1973-2026

| kind | rate | filter | best parameter | RMSE | bias | corr | RMSE affine in-sample (a, b) | error 2008-15 | error 2016-26 |
|---|---|---|---|---|---|---|---|---|---|
| nominal | 10-year | MA | 6 | 1.57 | +0.05 | 0.87 | 1.34 (+1.46, 0.74) | +0.25 | -0.82 |
| nominal | 10-year | HP | 1440 | 1.57 | +0.04 | 0.87 | 1.33 (+1.52, 0.74) | +0.19 | -0.78 |
| nominal | 10-year | EWMA | 3 | 1.58 | +0.05 | 0.86 | 1.37 (+1.45, 0.75) | +0.28 | -0.84 |
| nominal | 2-year | EWMA | 3 | 1.80 | -0.74 | 0.89 | 1.21 (+2.36, 0.68) | -1.67 | -1.26 |
| nominal | 2-year | MA | 6 | 1.82 | -0.75 | 0.90 | 1.20 (+2.39, 0.68) | -1.73 | -1.23 |
| nominal | 2-year | HP | 1440 | 1.89 | -0.75 | 0.89 | 1.21 (+2.49, 0.66) | -1.84 | -1.17 |
| nominal | funds rate | EWMA | 24 | 2.02 | -0.92 | 0.83 | 1.49 (+2.44, 0.69) | -0.92 | -2.11 |
| nominal | funds rate | MA | 6 | 2.15 | -1.01 | 0.89 | 1.22 (+2.84, 0.62) | -2.06 | -1.37 |
| nominal | funds rate | HP | 1440 | 2.30 | -1.01 | 0.88 | 1.27 (+2.98, 0.59) | -2.19 | -1.29 |
| real | 2-year | EWMA | 180 | 0.65 | -0.09 | 0.72 | 0.64 (+0.31, 0.90) | +0.96 | -0.48 |
| real | funds rate | EWMA | 240 | 0.75 | -0.36 | 0.70 | 0.66 (+0.19, 1.08) | +0.80 | -0.53 |
| real | 10-year | EWMA | 120 | 0.89 | +0.39 | 0.56 | 0.76 (+0.51, 0.68) | +1.57 | +0.02 |
| real | 10-year | MA | 180 | 1.03 | +0.30 | 0.59 | 0.74 (+1.17, 0.46) | +1.11 | -0.66 |
| real | funds rate | HP | 12960000000 | 1.11 | -0.42 | 0.74 | 0.62 (+1.50, 0.45) | +0.03 | -1.86 |
| real | 2-year | HP | 12960000000 | 1.12 | -0.34 | 0.67 | 0.68 (+1.51, 0.43) | +0.24 | -1.63 |
| real | 2-year | MA | 144 | 1.18 | -0.52 | 0.73 | 0.63 (+1.57, 0.44) | -0.28 | -1.93 |
| real | 10-year | HP | 1296000000 | 1.21 | +0.36 | 0.53 | 0.78 (+1.39, 0.37) | +1.32 | -0.71 |
| real | funds rate | MA | 180 | 1.25 | -0.73 | 0.72 | 0.64 (+1.64, 0.46) | -0.26 | -2.18 |

## Best parameter per rate and filter, fit over 1996-2026

| kind | rate | filter | best parameter | RMSE | bias | corr | RMSE affine in-sample (a, b) | RMSE affine fit 1973-95, out of sample |
|---|---|---|---|---|---|---|---|---|
| nominal | 10-year | EWMA | 3 | 0.90 | -0.35 | 0.83 | 0.76 (+1.18, 0.78) | 1.93 |
| nominal | 10-year | MA | 6 | 0.91 | -0.36 | 0.83 | 0.76 (+1.21, 0.77) | 1.85 |
| nominal | 10-year | HP | 1440 | 0.94 | -0.38 | 0.83 | 0.77 (+1.28, 0.76) | 1.83 |
| nominal | funds rate | EWMA | 120 | 1.16 | +0.20 | 0.68 | 1.01 (+1.37, 0.63) | 6.56 |
| nominal | 2-year | EWMA | 84 | 1.23 | +0.15 | 0.72 | 0.95 (+1.68, 0.56) | 6.98 |
| nominal | 2-year | MA | 144 | 1.49 | -0.66 | 0.74 | 0.93 (+2.32, 0.51) | 7.48 |
| nominal | funds rate | MA | 240 | 1.59 | +0.01 | 0.71 | 0.97 (+2.28, 0.44) | 10.88 |
| nominal | 2-year | HP | 1440 | 1.80 | -1.33 | 0.83 | 0.78 (+2.56, 0.55) | 1.55 |
| nominal | funds rate | HP | 12960000000 | 1.82 | +0.59 | 0.68 | 1.01 (+2.19, 0.40) | 6.03 |
| real | 2-year | EWMA | 180 | 0.66 | +0.04 | 0.68 | 0.64 (+0.36, 0.80) | 1.82 |
| real | funds rate | EWMA | 240 | 0.68 | -0.17 | 0.66 | 0.66 (+0.26, 0.95) | 1.81 |
| real | 10-year | EWMA | 36 | 0.77 | -0.08 | 0.70 | 0.62 (+0.85, 0.58) | 1.55 |
| real | 10-year | MA | 60 | 0.81 | -0.32 | 0.70 | 0.62 (+0.96, 0.60) | 1.44 |
| real | 2-year | MA | 300 | 0.88 | -0.10 | 0.65 | 0.66 (+1.00, 0.50) | nan |
| real | 10-year | HP | 1440 | 0.91 | -0.44 | 0.66 | 0.66 (+1.08, 0.56) | 1.44 |
| real | funds rate | MA | 300 | 0.97 | -0.46 | 0.67 | 0.65 (+1.17, 0.51) | nan |
| real | 2-year | HP | 12960000000 | 1.06 | -0.53 | 0.71 | 0.61 (+1.25, 0.48) | 1.56 |
| real | funds rate | HP | 12960000000 | 1.20 | -0.79 | 0.70 | 0.62 (+1.37, 0.48) | 1.47 |

## Full grid, 2-year, fit over 1973-2026 (RMSE)

| kind | filter | param | RMSE | bias | corr |
|---|---|---|---|---|---|
| nominal | EWMA | 3 | 1.80 | -0.74 | 0.89 |
| nominal | EWMA | 6 | 1.84 | -0.73 | 0.88 |
| nominal | EWMA | 12 | 1.88 | -0.70 | 0.85 |
| nominal | EWMA | 18 | 1.91 | -0.67 | 0.83 |
| nominal | EWMA | 24 | 1.93 | -0.63 | 0.82 |
| nominal | EWMA | 36 | 1.98 | -0.55 | 0.78 |
| nominal | EWMA | 48 | 2.03 | -0.48 | 0.74 |
| nominal | EWMA | 60 | 2.08 | -0.43 | 0.70 |
| nominal | EWMA | 84 | 2.19 | -0.36 | 0.63 |
| nominal | EWMA | 120 | 2.34 | -0.34 | 0.52 |
| nominal | EWMA | 180 | 2.56 | -0.44 | 0.37 |
| nominal | EWMA | 240 | 2.70 | -0.58 | 0.23 |
| nominal | EWMA | 360 | 2.88 | -0.85 | 0.02 |
| nominal | EWMA | 480 | 2.99 | -1.07 | -0.13 |
| nominal | EWMA | 720 | 3.12 | -1.35 | -0.31 |
| nominal | HP | 1440 | 1.89 | -0.75 | 0.89 |
| nominal | HP | 14400 | 2.00 | -0.76 | 0.87 |
| nominal | HP | 129600 | 2.10 | -0.78 | 0.85 |
| nominal | HP | 1296000 | 2.16 | -0.79 | 0.84 |
| nominal | HP | 12960000 | 2.34 | -0.74 | 0.83 |
| nominal | HP | 129600000 | 2.62 | -0.28 | 0.78 |
| nominal | HP | 1296000000 | 2.59 | +0.61 | 0.72 |
| nominal | HP | 12960000000 | 2.57 | +0.94 | 0.70 |
| nominal | MA | 6 | 1.82 | -0.75 | 0.90 |
| nominal | MA | 12 | 1.88 | -0.74 | 0.88 |
| nominal | MA | 24 | 1.99 | -0.72 | 0.85 |
| nominal | MA | 36 | 2.06 | -0.71 | 0.82 |
| nominal | MA | 48 | 2.10 | -0.68 | 0.81 |
| nominal | MA | 60 | 2.11 | -0.66 | 0.79 |
| nominal | MA | 72 | 2.12 | -0.63 | 0.78 |
| nominal | MA | 84 | 2.13 | -0.60 | 0.77 |
| nominal | MA | 96 | 2.16 | -0.56 | 0.76 |
| nominal | MA | 120 | 2.23 | -0.51 | 0.72 |
| nominal | MA | 144 | 2.30 | -0.44 | 0.68 |
| real | EWMA | 3 | 1.69 | -0.75 | 0.70 |
| real | EWMA | 6 | 1.60 | -0.74 | 0.72 |
| real | EWMA | 12 | 1.47 | -0.73 | 0.75 |
| real | EWMA | 18 | 1.37 | -0.70 | 0.77 |
| real | EWMA | 24 | 1.29 | -0.67 | 0.78 |
| real | EWMA | 36 | 1.16 | -0.60 | 0.79 |
| real | EWMA | 48 | 1.05 | -0.53 | 0.79 |
| real | EWMA | 60 | 0.96 | -0.46 | 0.78 |
| real | EWMA | 84 | 0.83 | -0.35 | 0.76 |
| real | EWMA | 120 | 0.71 | -0.22 | 0.74 |
| real | EWMA | 180 | 0.65 | -0.09 | 0.72 |
| real | EWMA | 240 | 0.66 | -0.01 | 0.71 |
| real | EWMA | 360 | 0.71 | +0.07 | 0.69 |
| real | EWMA | 480 | 0.75 | +0.12 | 0.68 |
| real | EWMA | 720 | 0.81 | +0.16 | 0.66 |
| real | HP | 1440 | 1.83 | -0.75 | 0.66 |
| real | HP | 14400 | 1.85 | -0.76 | 0.66 |
| real | HP | 129600 | 1.81 | -0.78 | 0.68 |
| real | HP | 1296000 | 1.71 | -0.81 | 0.73 |
| real | HP | 12960000 | 1.63 | -0.86 | 0.76 |
| real | HP | 129600000 | 1.51 | -0.77 | 0.76 |
| real | HP | 1296000000 | 1.23 | -0.46 | 0.70 |
| real | HP | 12960000000 | 1.12 | -0.34 | 0.67 |
| real | MA | 6 | 1.73 | -0.75 | 0.68 |
| real | MA | 12 | 1.69 | -0.75 | 0.69 |
| real | MA | 24 | 1.61 | -0.74 | 0.72 |
| real | MA | 36 | 1.53 | -0.73 | 0.73 |
| real | MA | 48 | 1.47 | -0.72 | 0.75 |
| real | MA | 60 | 1.41 | -0.71 | 0.76 |
| real | MA | 72 | 1.36 | -0.69 | 0.76 |
| real | MA | 84 | 1.32 | -0.66 | 0.76 |
| real | MA | 96 | 1.29 | -0.63 | 0.76 |
| real | MA | 120 | 1.23 | -0.58 | 0.75 |
| real | MA | 144 | 1.18 | -0.52 | 0.73 |

Reference, Kiley r* vs LW, 1973-2026: RMSE 0.63, bias -0.29, corr 0.83.
