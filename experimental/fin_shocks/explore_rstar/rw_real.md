# Real case with a random-walk r* filtered inside the VAR (with the FCI, 12 lags, point estimates)

c (FCI loading on r*) = 1.533. Window impact on the month's averages (yield gap, FCI gap): [0.463, 0.49].

## Estimated r*

| start | first month | sd_eta (MLE, per month) | log-likelihood | EM iterations | sd of monthly change, r*_t|t | same, LW | corr with LW | RMSE vs LW (demeaned) | 2008-15 minus sample mean: RW / LW |
|---|---|---|---|---|---|---|---|---|---|
| 1996 | 1996-01 | 0.0492 | -133.9 | 2999 | 0.064 | 0.053 | 0.64 | 0.68 | -0.11 / -0.98 |
| 1973 | 1974-01 | 0.1142 | -799.5 | 1121 | 0.141 | 0.058 | -0.12 | 1.30 | +0.23 / -1.44 |

## IRFs, A monthly VAR

| start | r* | u 6m | u 12m | u 18m | u 24m | u 36m | P 6m | P 12m | P 18m | P 24m | P 36m |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1996 | RW r* (filtered in the VAR) | +0.12 | +0.18 | +0.15 | +0.14 | +0.14 | -0.07 | -0.05 | -0.06 | -0.05 | -0.03 |
| 1996 | LW r*, same VAR | +0.15 | +0.23 | +0.19 | +0.16 | +0.12 | -0.15 | -0.19 | -0.27 | -0.32 | -0.38 |
| 1996 | constant r* (real case), same VAR | +0.07 | +0.12 | +0.07 | +0.04 | +0.04 | -0.10 | -0.13 | -0.18 | -0.21 | -0.24 |
| 1973 | RW r* (filtered in the VAR) | +0.29 | +0.53 | +0.59 | +0.49 | +0.22 | -0.11 | -0.29 | -0.45 | -0.59 | -0.75 |
| 1973 | LW r*, same VAR | +0.20 | +0.33 | +0.33 | +0.26 | +0.10 | -0.08 | -0.18 | -0.30 | -0.40 | -0.57 |
| 1973 | constant r* (real case), same VAR | +0.17 | +0.29 | +0.31 | +0.26 | +0.12 | -0.04 | -0.13 | -0.24 | -0.33 | -0.46 |

## IRFs, B Note B model

| start | r* | u 6m | u 12m | u 18m | u 24m | u 36m | P 6m | P 12m | P 18m | P 24m | P 36m |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1996 | RW r* (filtered in the VAR) | +0.19 | +0.36 | +0.48 | +0.52 | +0.49 | -0.11 | -0.13 | -0.15 | -0.18 | -0.20 |
| 1996 | LW r* (package baseline) | +0.25 | +0.41 | +0.47 | +0.45 | +0.40 | -0.25 | -0.38 | -0.53 | -0.69 | -0.94 |
| 1996 | real case (package baseline) | +0.08 | +0.17 | +0.22 | +0.23 | +0.22 | -0.15 | -0.22 | -0.30 | -0.38 | -0.50 |
| 1973 | RW r* (filtered in the VAR) | +0.20 | +0.33 | +0.29 | +0.22 | +0.10 | -0.09 | -0.24 | -0.42 | -0.58 | -0.85 |
| 1973 | LW r* (package baseline) | +0.25 | +0.33 | +0.29 | +0.24 | +0.15 | -0.11 | -0.32 | -0.54 | -0.76 | -1.14 |
| 1973 | real case (package baseline) | +0.18 | +0.25 | +0.20 | +0.13 | +0.02 | -0.07 | -0.24 | -0.40 | -0.55 | -0.79 |