# r* exploration: Note B's two baselines under alternative r* measures

Responses per +1 pp on the 2-year yield in the window: unemployment gap (pp) and price level (percent). `**`/`*`: 95/90 percent interval excludes zero. 500 draws; 2020 (March-December) dropped; no trend. LW and Kiley rows are the package's stored results (`baseline/results`).

## 12 lags (main)

| Start | FCI | r* measure | u 12m | u 24m | P 12m | P 24m |
|---|---|---|---|---|---|---|
| 1996 | no FCI | LW (baseline) | -0.10 | -0.21 | -0.20** | -0.32 |
| 1996 | no FCI | Kiley | -0.25** | -0.37** | -0.12 | -0.10 |
| 1996 | no FCI | MA8 real 2-year | -0.27** | -0.37** | -0.08 | -0.02 |
| 1996 | no FCI | Forward 9-10y less e10 | -0.32** | -0.45** | -0.07 | +0.08 |
| 1996 | no FCI | MA8 nominal 2-year | -0.34** | -0.43** | +0.01 | +0.11 |
| 1996 | no FCI | MA5 real 2-year, lagged | -0.29** | -0.43** | -0.11 | -0.15 |
| 1996 | no FCI | MA5 nominal 2-year, lagged | -0.38** | -0.50** | -0.02 | -0.02 |
| 1996 | no FCI | SPF BILL10 - CPI10 (1996 only) | -0.29** | -0.45** | -0.02 | +0.11 |
| 1996 | with FCI | LW (baseline) | +0.41** | +0.45** | -0.38** | -0.69** |
| 1996 | with FCI | Kiley | +0.10 | -0.02 | -0.14 | -0.02 |
| 1996 | with FCI | MA8 real 2-year | +0.13 | +0.16 | -0.21 | -0.29 |
| 1996 | with FCI | Forward 9-10y less e10 | -0.11 | -0.27** | -0.14 | +0.04 |
| 1996 | with FCI | MA8 nominal 2-year | +0.13 | +0.14 | -0.08 | -0.09 |
| 1996 | with FCI | MA5 real 2-year, lagged | +0.04 | +0.03 | -0.24* | -0.41 |
| 1996 | with FCI | MA5 nominal 2-year, lagged | +0.01 | -0.01 | -0.11 | -0.20 |
| 1996 | with FCI | SPF BILL10 - CPI10 (1996 only) | +0.15 | +0.04 | -0.01 | +0.18 |
| 1973 | no FCI | LW (baseline) | +0.17** | +0.15 | -0.28** | -0.64** |
| 1973 | no FCI | Kiley | +0.11 | +0.07 | -0.25** | -0.51** |
| 1973 | no FCI | MA8 real 2-year | +0.10 | +0.09 | -0.22** | -0.51** |
| 1973 | no FCI | Forward 9-10y less e10 | -0.02 | -0.07 | -0.13 | -0.12 |
| 1973 | no FCI | MA8 nominal 2-year | +0.10 | +0.18* | -0.03 | -0.13 |
| 1973 | no FCI | MA5 real 2-year, lagged | +0.07 | +0.09 | -0.22** | -0.52** |
| 1973 | no FCI | MA5 nominal 2-year, lagged | +0.07 | +0.17 | -0.02 | -0.14 |
| 1973 | with FCI | LW (baseline) | +0.33** | +0.24 | -0.32** | -0.76** |
| 1973 | with FCI | Kiley | +0.14 | +0.02 | -0.26** | -0.52** |
| 1973 | with FCI | MA8 real 2-year | +0.16** | +0.15 | -0.24** | -0.56** |
| 1973 | with FCI | Forward 9-10y less e10 | +0.16 | +0.03 | -0.09 | -0.05 |
| 1973 | with FCI | MA8 nominal 2-year | +0.23** | +0.29** | -0.02 | -0.20 |
| 1973 | with FCI | MA5 real 2-year, lagged | +0.14 | +0.14 | -0.23** | -0.57** |
| 1973 | with FCI | MA5 nominal 2-year, lagged | +0.22** | +0.31** | -0.00 | -0.20 |

## 6 lags

| Start | FCI | r* measure | u 12m | u 24m | P 12m | P 24m |
|---|---|---|---|---|---|---|
| 1996 | no FCI | LW (baseline) | +0.04 | +0.05 | -0.15 | -0.30 |
| 1996 | no FCI | Kiley | -0.11 | -0.13 | -0.08 | -0.11 |
| 1996 | no FCI | MA8 real 2-year | -0.17 | -0.20 | +0.01 | +0.07 |
| 1996 | no FCI | Forward 9-10y less e10 | -0.27** | -0.33** | -0.01 | +0.14 |
| 1996 | no FCI | MA8 nominal 2-year | -0.28** | -0.27 | +0.09 | +0.21 |
| 1996 | no FCI | MA5 real 2-year, lagged | -0.21** | -0.28* | -0.03 | -0.06 |
| 1996 | no FCI | MA5 nominal 2-year, lagged | -0.34** | -0.35** | +0.05 | +0.07 |
| 1996 | no FCI | SPF BILL10 - CPI10 (1996 only) | -0.10 | -0.14 | +0.06 | +0.14 |
| 1996 | with FCI | LW (baseline) | +0.38** | +0.44** | -0.30** | -0.57** |
| 1996 | with FCI | Kiley | +0.27** | +0.27 | -0.13 | -0.16 |
| 1996 | with FCI | MA8 real 2-year | +0.07 | +0.07 | -0.14 | -0.18 |
| 1996 | with FCI | Forward 9-10y less e10 | -0.13 | -0.19 | -0.07 | +0.11 |
| 1996 | with FCI | MA8 nominal 2-year | +0.01 | +0.04 | -0.02 | +0.02 |
| 1996 | with FCI | MA5 real 2-year, lagged | -0.01 | -0.05 | -0.16 | -0.29 |
| 1996 | with FCI | MA5 nominal 2-year, lagged | -0.07 | -0.08 | -0.05 | -0.10 |
| 1996 | with FCI | SPF BILL10 - CPI10 (1996 only) | +0.26** | +0.24 | +0.05 | +0.18 |
| 1973 | no FCI | LW (baseline) | +0.11 | +0.10 | -0.16 | -0.39 |
| 1973 | no FCI | Kiley | +0.06 | +0.05 | -0.12 | -0.26 |
| 1973 | no FCI | MA8 real 2-year | +0.06 | +0.07 | -0.12 | -0.29 |
| 1973 | no FCI | Forward 9-10y less e10 | -0.06 | -0.03 | +0.04 | +0.19 |
| 1973 | no FCI | MA8 nominal 2-year | +0.06 | +0.15 | +0.05 | +0.06 |
| 1973 | no FCI | MA5 real 2-year, lagged | +0.04 | +0.07 | -0.12 | -0.33* |
| 1973 | no FCI | MA5 nominal 2-year, lagged | +0.05 | +0.16 | +0.04 | -0.01 |
| 1973 | with FCI | LW (baseline) | +0.27** | +0.15 | -0.20* | -0.49* |
| 1973 | with FCI | Kiley | +0.11 | -0.01 | -0.15* | -0.35** |
| 1973 | with FCI | MA8 real 2-year | +0.15** | +0.11 | -0.17** | -0.44** |
| 1973 | with FCI | Forward 9-10y less e10 | +0.07 | +0.05 | +0.06 | +0.17 |
| 1973 | with FCI | MA8 nominal 2-year | +0.19** | +0.22** | +0.02 | -0.11 |
| 1973 | with FCI | MA5 real 2-year, lagged | +0.14* | +0.10 | -0.17* | -0.46** |
| 1973 | with FCI | MA5 nominal 2-year, lagged | +0.18** | +0.24** | +0.02 | -0.13 |

## 3 lags

| Start | FCI | r* measure | u 12m | u 24m | P 12m | P 24m |
|---|---|---|---|---|---|---|
| 1996 | no FCI | LW (baseline) | +0.13 | +0.22 | -0.18* | -0.28 |
| 1996 | no FCI | Kiley | +0.03 | +0.09 | -0.16 | -0.22 |
| 1996 | no FCI | MA8 real 2-year | -0.09 | -0.13 | +0.03 | +0.15 |
| 1996 | no FCI | Forward 9-10y less e10 | -0.27** | -0.40** | +0.09 | +0.29* |
| 1996 | no FCI | MA8 nominal 2-year | -0.19** | -0.20 | +0.17* | +0.34* |
| 1996 | no FCI | MA5 real 2-year, lagged | -0.16* | -0.23 | -0.02 | +0.03 |
| 1996 | no FCI | MA5 nominal 2-year, lagged | -0.27** | -0.31* | +0.12 | +0.21 |
| 1996 | no FCI | SPF BILL10 - CPI10 (1996 only) | +0.01 | +0.01 | +0.05 | +0.18 |
| 1996 | with FCI | LW (baseline) | +0.37** | +0.44** | -0.22 | -0.35 |
| 1996 | with FCI | Kiley | +0.40** | +0.43** | -0.16 | -0.26 |
| 1996 | with FCI | MA8 real 2-year | -0.01 | -0.06 | -0.01 | +0.08 |
| 1996 | with FCI | Forward 9-10y less e10 | -0.20** | -0.39** | +0.13 | +0.41** |
| 1996 | with FCI | MA8 nominal 2-year | -0.07 | -0.11 | +0.13 | +0.28 |
| 1996 | with FCI | MA5 real 2-year, lagged | -0.09 | -0.16 | -0.05 | -0.02 |
| 1996 | with FCI | MA5 nominal 2-year, lagged | -0.16 | -0.22 | +0.09 | +0.17 |
| 1996 | with FCI | SPF BILL10 - CPI10 (1996 only) | +0.23* | +0.20 | +0.15 | +0.34 |
| 1973 | no FCI | LW (baseline) | +0.06 | +0.11 | -0.11 | -0.20 |
| 1973 | no FCI | Kiley | +0.03 | +0.07 | -0.06 | -0.08 |
| 1973 | no FCI | MA8 real 2-year | +0.02 | +0.06 | -0.07 | -0.11 |
| 1973 | no FCI | Forward 9-10y less e10 | -0.01 | +0.06 | +0.30** | +0.88** |
| 1973 | no FCI | MA8 nominal 2-year | +0.04 | +0.15* | +0.11 | +0.34** |
| 1973 | no FCI | MA5 real 2-year, lagged | +0.02 | +0.07 | -0.07 | -0.14 |
| 1973 | no FCI | MA5 nominal 2-year, lagged | +0.05 | +0.17* | +0.08 | +0.25 |
| 1973 | with FCI | LW (baseline) | +0.12 | +0.09 | -0.09 | -0.25 |
| 1973 | with FCI | Kiley | +0.02 | -0.01 | -0.09 | -0.26 |
| 1973 | with FCI | MA8 real 2-year | +0.03 | +0.03 | -0.11 | -0.26 |
| 1973 | with FCI | Forward 9-10y less e10 | +0.03 | +0.02 | +0.27** | +0.55** |
| 1973 | with FCI | MA8 nominal 2-year | +0.06 | +0.11 | +0.04 | +0.08 |
| 1973 | with FCI | MA5 real 2-year, lagged | +0.03 | +0.03 | -0.11 | -0.28* |
| 1973 | with FCI | MA5 nominal 2-year, lagged | +0.07 | +0.13 | +0.04 | +0.04 |
