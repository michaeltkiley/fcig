# More one-sided filters tracking one-sided LW r* (Butterworth, double exponential, Kalman)

RMSE of the level against LW, pp; param = cutoff period (Butterworth, months), half-life (EWMA2, DEMA, EWMA; months); Kalman variances by maximum likelihood. Data from 1958 (2-year from June 1961); 36-month burn-in. EWMA 180 = the best filter of filters_lw.md, for reference.


## Findings (18 Nov 2026)

* **Nothing beats the EWMA of the real 2-year with a 180-month half-life** (RMSE 0.65 against LW, 1973-2026; 0.66 over 1996-2026). Brown's DEMA (half-life 480) is level with it (0.66); a first-order Butterworth comes close (0.69) only at a cutoff period of 100 years (1200 months), i.e. close to a constant set by the 1960s data. Higher-order Butterworth filters are worse at every cutoff (best 0.80-0.97): their sharper cutoff buys nothing against LW and adds lag and overshoot. The double EWMA (EWMA of an EWMA) is worse (0.75).
* **Kalman filters with maximum-likelihood variances fail** (RMSE 1.5-2.2): the likelihood of a single rate sets the irregular variance to zero, so the filtered "trend" is the rate itself (a random walk). A local linear trend adds nothing (slope variance 0). A Kalman trend tracks LW only if its signal-to-noise ratio is imposed, not estimated; with it fixed small it becomes the one-sided HP of filters_lw.md.
* **All the good filters are slow and depend on the start of the data** (EWMA 180 starting in 1966: 0.61; in 1970: 0.84; DEMA and Butterworth similar). The common finding: what tracks LW over 1973-2026 is a slow decline from the 1960s level, missing by about 0.7 pp in the 1970s and 2020s (too low) and 0.5 pp in the 2010s (too high).
* **Through the model (quick point estimates, `quick_trends_ew.md`):** EWMA 180 gives results like MA8 real and Kiley, not like LW. With the FCI, from 1996: unemployment +0.07 / +0.01 at 12 / 24 months with no trend (LW +0.41 / +0.45), +0.26 / +0.51 with the quadratic trend; price level at 24 months +0.11 (none), -0.16 (spline), -0.18 (quadratic), against LW -0.69. From 1973: unemployment +0.17 at 12 months and price level -0.55 at 24 months with no trend (LW +0.33, -0.76); weaker with either trend.
* **Why closeness to LW is not enough.** The r*-gap 2-year built with EWMA 180 correlates 0.87 with LW's over 1996-2026 (Kiley 0.86); the difference has a standard deviation of 0.66 pp. The FCI is more sensitive to r* than the 2-year: r* enters the 10-year term (weight 0.62) and the equity term, which converts E/P - r* to CAPE log points (a factor of about 20 at the average E/P, times the equity weight 0.05), about 1.6 index points per pp of r* in all. So the r*-gap FCI under EWMA 180 correlates only 0.68 with LW's over 1996-2026 (Kiley 0.72, MA8 0.69). The 1996 results depend on the specific post-1996 path of LW in both the 2-year and, more, the FCI.

## Best setting per rate and filter, fit 1973-2026

| rate | filter | best param | RMSE | bias | corr | err 1970s | 1980s | 1990s | 2000s | 2010s | 2020s |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2-year | EWMA | 180 | 0.65 | -0.09 | 0.72 | -0.72 | -0.39 | +0.34 | +0.03 | +0.51 | -0.66 |
| 2-year | DEMA | 480 | 0.66 | -0.01 | 0.69 | -0.69 | -0.44 | +0.29 | +0.12 | +0.75 | -0.43 |
| 2-year | Butterworth 1 | 1200 | 0.69 | -0.18 | 0.74 | -0.75 | -0.33 | +0.41 | -0.05 | +0.19 | -0.99 |
| 2-year | EWMA2 | 84 | 0.75 | +0.01 | 0.60 | -0.60 | -0.58 | +0.38 | +0.30 | +0.86 | -0.68 |
| funds rate | DEMA | 480 | 0.75 | -0.35 | 0.69 | -1.09 | -0.72 | -0.05 | -0.23 | +0.42 | -0.77 |
| funds rate | EWMA | 180 | 0.77 | -0.42 | 0.72 | -1.09 | -0.63 | -0.01 | -0.33 | +0.16 | -1.01 |
| 2-year | Butterworth 2 | 960 | 0.80 | +0.08 | 0.53 | -0.59 | -0.60 | +0.32 | +0.40 | +1.08 | -0.55 |
| funds rate | EWMA2 | 84 | 0.83 | -0.31 | 0.59 | -1.03 | -0.84 | +0.12 | -0.05 | +0.50 | -1.04 |
| funds rate | Butterworth 1 | 1200 | 0.83 | -0.50 | 0.74 | -1.08 | -0.51 | +0.07 | -0.41 | -0.16 | -1.35 |
| funds rate | Butterworth 2 | 960 | 0.85 | -0.24 | 0.51 | -1.05 | -0.89 | +0.09 | +0.10 | +0.74 | -0.90 |
| 10-year | Butterworth 1 | 960 | 0.89 | +0.37 | 0.58 | -0.64 | -0.02 | +1.08 | +0.57 | +1.03 | -0.33 |
| 2-year | Butterworth 3 | 600 | 0.91 | +0.09 | 0.45 | -0.56 | -0.63 | +0.33 | +0.64 | +1.15 | -0.92 |
| 10-year | EWMA | 180 | 0.91 | +0.42 | 0.50 | -0.62 | -0.22 | +0.79 | +0.62 | +1.40 | +0.16 |
| funds rate | Butterworth 3 | 720 | 0.94 | -0.13 | 0.31 | -1.09 | -0.97 | +0.02 | +0.33 | +1.13 | -0.68 |
| 10-year | DEMA | 240 | 0.96 | +0.46 | 0.54 | -0.59 | -0.02 | +1.17 | +0.76 | +1.19 | -0.31 |
| 10-year | EWMA2 | 720 | 0.97 | +0.19 | -0.80 | -0.71 | -0.68 | -0.11 | +0.08 | +1.60 | +0.97 |
| 2-year | Butterworth 4 | 480 | 0.99 | +0.14 | 0.35 | -0.57 | -0.62 | +0.21 | +0.81 | +1.36 | -0.92 |
| funds rate | Butterworth 4 | 480 | 1.01 | -0.19 | 0.39 | -1.10 | -0.93 | +0.16 | +0.55 | +0.88 | -1.35 |
| 10-year | Butterworth 2 | 480 | 1.05 | +0.40 | 0.54 | -0.42 | -0.31 | +1.48 | +0.91 | +0.91 | -0.85 |
| 10-year | Butterworth 3 | 360 | 1.13 | +0.41 | 0.53 | -0.30 | -0.53 | +1.60 | +1.15 | +0.84 | -0.92 |
| 10-year | Butterworth 4 | 300 | 1.17 | +0.45 | 0.52 | -0.24 | -0.65 | +1.57 | +1.36 | +0.84 | -0.78 |
| 10-year | Kalman local linear trend | MLE | 1.51 | +0.03 | 0.58 | -1.60 | +1.91 | +0.67 | -0.51 | -0.42 | -0.57 |
| 10-year | Kalman local level | MLE | 1.51 | +0.03 | 0.58 | -1.60 | +1.91 | +0.67 | -0.51 | -0.42 | -0.57 |
| 2-year | Kalman local linear trend | MLE | 1.78 | -0.75 | 0.67 | -1.82 | +1.35 | -0.18 | -1.60 | -1.70 | -0.97 |
| 2-year | Kalman local level | MLE | 1.78 | -0.75 | 0.67 | -1.82 | +1.35 | -0.18 | -1.60 | -1.70 | -0.97 |
| funds rate | Kalman local linear trend | MLE | 2.19 | -1.02 | 0.66 | -1.70 | +1.29 | -0.78 | -1.90 | -2.08 | -1.22 |
| funds rate | Kalman local level | MLE | 2.19 | -1.02 | 0.66 | -1.70 | +1.29 | -0.78 | -1.90 | -2.08 | -1.22 |

## Best setting per rate and filter, fit 1996-2026

| rate | filter | best param | RMSE | bias | corr |
|---|---|---|---|---|---|
| 2-year | EWMA | 180 | 0.66 | +0.04 | 0.68 |
| funds rate | DEMA | 720 | 0.69 | +0.01 | 0.63 |
| 2-year | DEMA | 360 | 0.69 | +0.01 | 0.67 |
| 2-year | Butterworth 1 | 1200 | 0.70 | -0.17 | 0.70 |
| funds rate | EWMA | 180 | 0.74 | -0.32 | 0.67 |
| funds rate | EWMA2 | 120 | 0.76 | +0.15 | 0.52 |
| 10-year | Butterworth 1 | 300 | 0.77 | -0.12 | 0.70 |
| funds rate | Butterworth 2 | 1200 | 0.81 | +0.22 | 0.49 |
| 2-year | EWMA2 | 84 | 0.81 | +0.25 | 0.58 |
| 10-year | Butterworth 2 | 120 | 0.83 | -0.34 | 0.69 |
| 10-year | EWMA2 | 24 | 0.84 | +0.06 | 0.68 |
| 10-year | Butterworth 3 | 96 | 0.85 | -0.33 | 0.68 |
| funds rate | Butterworth 1 | 1200 | 0.87 | -0.53 | 0.69 |
| 10-year | Butterworth 4 | 60 | 0.87 | -0.35 | 0.67 |
| 10-year | Kalman local linear trend | MLE | 0.89 | -0.43 | 0.67 |
| 10-year | Kalman local level | MLE | 0.89 | -0.43 | 0.67 |
| 2-year | Butterworth 2 | 960 | 0.89 | +0.38 | 0.52 |
| 10-year | DEMA | 24 | 0.91 | -0.53 | 0.69 |
| funds rate | Butterworth 3 | 720 | 0.93 | +0.32 | 0.43 |
| 10-year | EWMA | 180 | 1.03 | +0.76 | 0.61 |
| 2-year | Butterworth 3 | 600 | 1.05 | +0.41 | 0.47 |
| funds rate | Butterworth 4 | 600 | 1.06 | +0.51 | 0.31 |
| 2-year | Butterworth 4 | 480 | 1.19 | +0.53 | 0.39 |
| 2-year | Kalman local linear trend | MLE | 1.70 | -1.32 | 0.68 |
| 2-year | Kalman local level | MLE | 1.70 | -1.32 | 0.68 |
| funds rate | Kalman local linear trend | MLE | 2.16 | -1.63 | 0.59 |
| funds rate | Kalman local level | MLE | 2.16 | -1.63 | 0.59 |

## Butterworth, real 2-year, RMSE by order and cutoff period (1973-2026)

| filter        |   60 |   96 |   120 |   180 |   240 |   300 |   360 |   480 |   600 |   720 |   960 |   1200 |
|:--------------|-----:|-----:|------:|------:|------:|------:|------:|------:|------:|------:|------:|-------:|
| Butterworth 1 | 1.59 | 1.5  |  1.45 |  1.34 |  1.26 |  1.19 |  1.13 |  1.02 |  0.92 |  0.85 |  0.75 |   0.69 |
| Butterworth 2 | 1.62 | 1.53 |  1.48 |  1.38 |  1.31 |  1.24 |  1.16 |  1.01 |  0.9  |  0.83 |  0.8  |   0.83 |
| Butterworth 3 | 1.63 | 1.54 |  1.49 |  1.43 |  1.34 |  1.21 |  1.11 |  0.97 |  0.91 |  0.91 |  0.96 |   0.98 |
| Butterworth 4 | 1.64 | 1.56 |  1.5  |  1.47 |  1.31 |  1.12 |  1.05 |  0.99 |  1.01 |  1.04 |  1.04 |   1.02 |

## Kalman parameters (MLE)

* 2-year, Kalman local level: {'sigma2.irregular': np.float64(0.0), 'sigma2.level': np.float64(0.13545)}
* 2-year, Kalman local linear trend: {'sigma2.irregular': np.float64(0.0), 'sigma2.level': np.float64(0.13562), 'sigma2.trend': np.float64(0.0)}
* funds rate, Kalman local level: {'sigma2.irregular': np.float64(0.0), 'sigma2.level': np.float64(0.2964)}
* funds rate, Kalman local linear trend: {'sigma2.irregular': np.float64(0.0), 'sigma2.level': np.float64(0.29675), 'sigma2.trend': np.float64(0.0)}
* 10-year, Kalman local level: {'sigma2.irregular': np.float64(0.0), 'sigma2.level': np.float64(0.05855)}
* 10-year, Kalman local linear trend: {'sigma2.irregular': np.float64(0.0), 'sigma2.level': np.float64(0.05863), 'sigma2.trend': np.float64(0.0)}
