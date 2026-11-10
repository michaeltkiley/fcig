# Note B: u and price-level responses, 12 lags, r*-gap 2-year, per +1 pp

> **Caveat (10 Nov 2026):** the `spline` rows for the 1973, 1977 and 1982 starts in this file used only the post-1994 NBER peaks (2001, 2007, 2020) as knots, not the earlier peaks inside those samples. Only the 1994-start spline rows are as intended. The corrected long-sample spline is in `baseline/` (Robustness 2d, real version).

Unemployment gap (pp) and core PCE price level (%), at 12, 24, 36 months; * = 90% interval excludes zero. 200 draws, daily block not re-bootstrapped, NS shocks 1994+, 2020-03..12 dropped. End = full (to 2026-09) or 2019-12. Trend: none, quadratic, natural cubic spline with knots at NBER peaks (FS_QA, midas_core.py TRENDTYPE=spline). Pre-1994 starts use the spliced monthly series (FS-A29).

| Start | End | Trend | FCI | u 12 | u 24 | u 36 | P 12 | P 24 | P 36 |
|---|---|---|---|---|---|---|---|---|---|
| 1994 | 2026 | none | without | -0.08  | -0.15  | -0.16  | -0.19* | -0.31  | -0.44  |
| 1994 | 2026 | none | with | +0.34* | +0.41* | +0.37* | -0.33* | -0.61* | -0.84* |
| 1994 | 2026 | quad | without | -0.03  | +0.04  | +0.07  | -0.24* | -0.52* | -0.80* |
| 1994 | 2026 | quad | with | +0.36* | +0.50* | +0.43* | -0.33* | -0.72* | -0.97* |
| 1994 | 2026 | spline | without | -0.11  | -0.13  | -0.09  | -0.21* | -0.49* | -0.77* |
| 1994 | 2026 | spline | with | +0.37* | +0.50* | +0.44* | -0.44* | -1.02* | -1.40* |
| 1994 | 2019 | none | without | -0.14  | -0.19  | -0.16  | +0.10  | +0.10  | +0.07  |
| 1994 | 2019 | none | with | +0.30* | +0.30  | +0.23  | -0.05  | -0.12  | -0.21  |
| 1994 | 2019 | quad | without | +0.00  | +0.14  | +0.28  | +0.08  | +0.03  | -0.06  |
| 1994 | 2019 | quad | with | +0.44* | +0.60* | +0.59* | -0.05  | -0.12  | -0.22  |
| 1994 | 2019 | spline | without | -0.15  | -0.20  | -0.10  | +0.06  | -0.01  | -0.08  |
| 1994 | 2019 | spline | with | +0.33* | +0.39  | +0.37  | -0.19* | -0.46* | -0.72* |
| 1982 | 2026 | none | without | +0.07  | +0.06  | -0.02  | -0.14* | -0.24  | -0.30  |
| 1982 | 2026 | none | with | +0.20* | +0.19* | +0.11  | -0.20* | -0.35* | -0.45  |
| 1982 | 2026 | quad | without | +0.09  | +0.15  | +0.09  | -0.16* | -0.39* | -0.59* |
| 1982 | 2026 | quad | with | +0.21* | +0.25* | +0.18  | -0.22* | -0.51* | -0.74* |
| 1982 | 2026 | spline | without | +0.06  | +0.08  | +0.00  | -0.17* | -0.39* | -0.59* |
| 1982 | 2026 | spline | with | +0.19* | +0.20  | +0.14  | -0.26* | -0.64* | -0.93* |
| 1982 | 2019 | none | without | +0.09  | +0.05  | -0.04  | +0.08  | +0.22  | +0.36  |
| 1982 | 2019 | none | with | +0.18* | +0.08  | -0.07  | +0.04  | +0.17  | +0.26  |
| 1982 | 2019 | quad | without | +0.12  | +0.21  | +0.18  | +0.04  | +0.01  | -0.03  |
| 1982 | 2019 | quad | with | +0.23* | +0.23* | +0.13  | -0.00  | -0.02  | -0.09  |
| 1982 | 2019 | spline | without | +0.10  | +0.14  | +0.08  | +0.03  | -0.01  | -0.07  |
| 1982 | 2019 | spline | with | +0.18* | +0.11  | +0.01  | -0.05  | -0.16  | -0.27  |
| 1977 | 2026 | none | without | +0.23* | +0.23* | +0.10  | -0.26* | -0.62* | -0.98* |
| 1977 | 2026 | none | with | +0.33* | +0.30* | +0.20* | -0.31* | -0.71* | -1.14* |
| 1977 | 2026 | quad | without | +0.18* | +0.15  | +0.01  | -0.19* | -0.46* | -0.70* |
| 1977 | 2026 | quad | with | +0.28* | +0.20* | +0.07  | -0.24* | -0.54* | -0.81* |
| 1977 | 2026 | spline | without | +0.20* | +0.23* | +0.12  | -0.20* | -0.49* | -0.75* |
| 1977 | 2026 | spline | with | +0.28* | +0.23* | +0.11  | -0.24* | -0.53* | -0.79* |
| 1977 | 2019 | none | without | +0.27* | +0.31* | +0.18  | -0.17* | -0.43* | -0.77* |
| 1977 | 2019 | none | with | +0.37* | +0.34* | +0.20  | -0.19* | -0.45* | -0.83* |
| 1977 | 2019 | quad | without | +0.21* | +0.24* | +0.11  | -0.08  | -0.24* | -0.45* |
| 1977 | 2019 | quad | with | +0.30* | +0.20* | -0.00  | -0.12* | -0.30* | -0.54* |
| 1977 | 2019 | spline | without | +0.26* | +0.35* | +0.25* | -0.07  | -0.21* | -0.40* |
| 1977 | 2019 | spline | with | +0.32* | +0.26* | +0.08  | -0.11* | -0.24* | -0.43* |
| 1973 | 2026 | none | without | +0.18* | +0.14  | +0.04  | -0.29* | -0.64* | -0.96* |
| 1973 | 2026 | none | with | +0.31* | +0.26* | +0.20* | -0.32* | -0.75* | -1.12* |
| 1973 | 2026 | quad | without | +0.16* | +0.13  | +0.04  | -0.15* | -0.35* | -0.48* |
| 1973 | 2026 | quad | with | +0.27* | +0.18* | +0.08  | -0.18* | -0.40* | -0.53* |
| 1973 | 2026 | spline | without | +0.20* | +0.26* | +0.19* | -0.15* | -0.36* | -0.52* |
| 1973 | 2026 | spline | with | +0.27* | +0.22* | +0.15* | -0.18* | -0.39* | -0.51* |
| 1973 | 2019 | none | without | +0.20* | +0.18  | +0.07  | -0.22* | -0.51* | -0.83* |
| 1973 | 2019 | none | with | +0.33* | +0.25* | +0.15  | -0.23* | -0.54* | -0.90* |
| 1973 | 2019 | quad | without | +0.19* | +0.20  | +0.11  | -0.05  | -0.16  | -0.27* |
| 1973 | 2019 | quad | with | +0.27* | +0.16  | +0.02  | -0.07  | -0.19  | -0.31* |
| 1973 | 2019 | spline | without | +0.23* | +0.34* | +0.27* | -0.03  | -0.11  | -0.22  |
| 1973 | 2019 | spline | with | +0.29* | +0.22* | +0.11  | -0.05  | -0.12  | -0.20  |


## Treatment of 2020 (full sample, 12 lags, r*-gap)

Baseline = monthly dependent rows Mar-Dec 2020 dropped, daily block uses 2020. `in` = nothing dropped. `monthly + daily out` = monthly rows and daily HAR rows Mar-Dec 2020 dropped (2020 values still enter as lags and as the monthly macro regressors in the daily block). Env `T2020` in `midas_core.py`; ending 2019 is unaffected. Same conventions as above.

| Start | Trend | 2020 | FCI | u 12 | u 24 | u 36 | P 12 | P 24 | P 36 |
|---|---|---|---|---|---|---|---|---|---|
| 1994 | none | monthly out (baseline) | without | -0.08  | -0.15  | -0.16  | -0.19* | -0.31  | -0.44  |
| 1994 | none | monthly out (baseline) | with | +0.34* | +0.41* | +0.37* | -0.33* | -0.61* | -0.84* |
| 1994 | none | 2020 in | without | -0.28  | -0.06  | +0.04  | -0.18* | -0.39* | -0.62* |
| 1994 | none | 2020 in | with | +0.31  | +0.47* | +0.41* | -0.36* | -0.71* | -0.97* |
| 1994 | none | monthly + daily out | without | -0.08  | -0.15  | -0.16  | -0.18* | -0.31  | -0.44  |
| 1994 | none | monthly + daily out | with | +0.35* | +0.41* | +0.37* | -0.33* | -0.61* | -0.84* |
| 1994 | quad | monthly out (baseline) | without | -0.03  | +0.04  | +0.07  | -0.24* | -0.52* | -0.80* |
| 1994 | quad | monthly out (baseline) | with | +0.36* | +0.50* | +0.43* | -0.33* | -0.72* | -0.97* |
| 1994 | quad | 2020 in | without | -0.18  | +0.19  | +0.28  | -0.22* | -0.56* | -0.88* |
| 1994 | quad | 2020 in | with | +0.25  | +0.46* | +0.38* | -0.29* | -0.67* | -0.92* |
| 1994 | quad | monthly + daily out | without | -0.03  | +0.03  | +0.07  | -0.23* | -0.52* | -0.80* |
| 1994 | quad | monthly + daily out | with | +0.37* | +0.50* | +0.45* | -0.33* | -0.72* | -0.98* |
| 1994 | spline | monthly out (baseline) | without | -0.11  | -0.13  | -0.09  | -0.21* | -0.49* | -0.77* |
| 1994 | spline | monthly out (baseline) | with | +0.37* | +0.50* | +0.44* | -0.44* | -1.02* | -1.40* |
| 1994 | spline | 2020 in | without | -0.38* | -0.07  | +0.09  | -0.18* | -0.52* | -0.88* |
| 1994 | spline | 2020 in | with | +0.29  | +0.55* | +0.48* | -0.39* | -0.96* | -1.32* |
| 1994 | spline | monthly + daily out | without | -0.11  | -0.13  | -0.09  | -0.21* | -0.49* | -0.76* |
| 1994 | spline | monthly + daily out | with | +0.38* | +0.50* | +0.45* | -0.44* | -1.02* | -1.40* |
| 1982 | none | monthly out (baseline) | without | +0.07  | +0.06  | -0.02  | -0.14* | -0.24  | -0.30  |
| 1982 | none | monthly out (baseline) | with | +0.20* | +0.19* | +0.11  | -0.20* | -0.35* | -0.45  |
| 1982 | none | 2020 in | without | -0.09  | -0.01  | +0.02  | -0.12  | -0.24  | -0.36  |
| 1982 | none | 2020 in | with | +0.13  | +0.09  | +0.07  | -0.19* | -0.34* | -0.47* |
| 1982 | none | monthly + daily out | without | +0.07  | +0.06  | -0.02  | -0.14* | -0.24  | -0.30  |
| 1982 | none | monthly + daily out | with | +0.20* | +0.16  | +0.07  | -0.19* | -0.35* | -0.43  |
| 1982 | quad | monthly out (baseline) | without | +0.09  | +0.15  | +0.09  | -0.16* | -0.39* | -0.59* |
| 1982 | quad | monthly out (baseline) | with | +0.21* | +0.25* | +0.18  | -0.22* | -0.51* | -0.74* |
| 1982 | quad | 2020 in | without | -0.06  | +0.11  | +0.12  | -0.14* | -0.39* | -0.62* |
| 1982 | quad | 2020 in | with | +0.14  | +0.21  | +0.18  | -0.21* | -0.51* | -0.78* |
| 1982 | quad | monthly + daily out | without | +0.08  | +0.14  | +0.09  | -0.16* | -0.39* | -0.59* |
| 1982 | quad | monthly + daily out | with | +0.21* | +0.23* | +0.15  | -0.22* | -0.50* | -0.72* |
| 1982 | spline | monthly out (baseline) | without | +0.06  | +0.08  | +0.00  | -0.17* | -0.39* | -0.59* |
| 1982 | spline | monthly out (baseline) | with | +0.19* | +0.20  | +0.14  | -0.26* | -0.64* | -0.93* |
| 1982 | spline | 2020 in | without | -0.10  | +0.05  | +0.07  | -0.14* | -0.39* | -0.63* |
| 1982 | spline | 2020 in | with | +0.17  | +0.25  | +0.22  | -0.25* | -0.64* | -0.96* |
| 1982 | spline | monthly + daily out | without | +0.06  | +0.07  | +0.01  | -0.16* | -0.39* | -0.59* |
| 1982 | spline | monthly + daily out | with | +0.19* | +0.17  | +0.09  | -0.26* | -0.62* | -0.89* |
| 1977 | none | monthly out (baseline) | without | +0.23* | +0.23* | +0.10  | -0.26* | -0.62* | -0.98* |
| 1977 | none | monthly out (baseline) | with | +0.33* | +0.30* | +0.20* | -0.31* | -0.71* | -1.14* |
| 1977 | none | 2020 in | without | +0.02  | +0.06  | +0.06  | -0.22* | -0.54* | -0.90* |
| 1977 | none | 2020 in | with | +0.22  | +0.19* | +0.20  | -0.28* | -0.65* | -1.06* |
| 1977 | none | monthly + daily out | without | +0.22* | +0.23* | +0.11  | -0.26* | -0.62* | -0.98* |
| 1977 | none | monthly + daily out | with | +0.34* | +0.29* | +0.18* | -0.30* | -0.70* | -1.12* |
| 1977 | quad | monthly out (baseline) | without | +0.18* | +0.15  | +0.01  | -0.19* | -0.46* | -0.70* |
| 1977 | quad | monthly out (baseline) | with | +0.28* | +0.20* | +0.07  | -0.24* | -0.54* | -0.81* |
| 1977 | quad | 2020 in | without | -0.04  | +0.01  | -0.02  | -0.16* | -0.40* | -0.65* |
| 1977 | quad | 2020 in | with | +0.13  | +0.11  | +0.07  | -0.21* | -0.50* | -0.79* |
| 1977 | quad | monthly + daily out | without | +0.18* | +0.15  | +0.01  | -0.19* | -0.46* | -0.70* |
| 1977 | quad | monthly + daily out | with | +0.28* | +0.18* | +0.02  | -0.24* | -0.53* | -0.78* |
| 1977 | spline | monthly out (baseline) | without | +0.20* | +0.23* | +0.12  | -0.20* | -0.49* | -0.75* |
| 1977 | spline | monthly out (baseline) | with | +0.28* | +0.23* | +0.11  | -0.24* | -0.53* | -0.79* |
| 1977 | spline | 2020 in | without | +0.02  | +0.16  | +0.12  | -0.17* | -0.46* | -0.73* |
| 1977 | spline | 2020 in | with | +0.13  | +0.11  | +0.07  | -0.21* | -0.49* | -0.78* |
| 1977 | spline | monthly + daily out | without | +0.20* | +0.23* | +0.12  | -0.19* | -0.48* | -0.75* |
| 1977 | spline | monthly + daily out | with | +0.29* | +0.21* | +0.07  | -0.24* | -0.53* | -0.77* |
| 1973 | none | monthly out (baseline) | without | +0.18* | +0.14  | +0.04  | -0.29* | -0.64* | -0.96* |
| 1973 | none | monthly out (baseline) | with | +0.31* | +0.26* | +0.20* | -0.32* | -0.75* | -1.12* |
| 1973 | none | 2020 in | without | -0.05  | -0.00  | -0.00  | -0.23* | -0.50* | -0.78* |
| 1973 | none | 2020 in | with | +0.18* | +0.15* | +0.14  | -0.27* | -0.62* | -0.94* |
| 1973 | none | monthly + daily out | without | +0.18* | +0.14  | +0.04  | -0.29* | -0.64* | -0.96* |
| 1973 | none | monthly + daily out | with | +0.32* | +0.24* | +0.16  | -0.32* | -0.74* | -1.11* |
| 1973 | quad | monthly out (baseline) | without | +0.16* | +0.13  | +0.04  | -0.15* | -0.35* | -0.48* |
| 1973 | quad | monthly out (baseline) | with | +0.27* | +0.18* | +0.08  | -0.18* | -0.40* | -0.53* |
| 1973 | quad | 2020 in | without | -0.11  | -0.04  | -0.02  | -0.09  | -0.23  | -0.36* |
| 1973 | quad | 2020 in | with | +0.07  | +0.04  | -0.00  | -0.12  | -0.30* | -0.43* |
| 1973 | quad | monthly + daily out | without | +0.16* | +0.13  | +0.04  | -0.15* | -0.34* | -0.48* |
| 1973 | quad | monthly + daily out | with | +0.28* | +0.15  | +0.04  | -0.18* | -0.40* | -0.52* |
| 1973 | spline | monthly out (baseline) | without | +0.20* | +0.26* | +0.19* | -0.15* | -0.36* | -0.52* |
| 1973 | spline | monthly out (baseline) | with | +0.27* | +0.22* | +0.15* | -0.18* | -0.39* | -0.51* |
| 1973 | spline | 2020 in | without | -0.03  | +0.16  | +0.15  | -0.11  | -0.28* | -0.44* |
| 1973 | spline | 2020 in | with | +0.09  | +0.08  | +0.04  | -0.12  | -0.30* | -0.42* |
| 1973 | spline | monthly + daily out | without | +0.19* | +0.26* | +0.19* | -0.15* | -0.36* | -0.52* |
| 1973 | spline | monthly + daily out | with | +0.28* | +0.21* | +0.12  | -0.18* | -0.39* | -0.50* |
