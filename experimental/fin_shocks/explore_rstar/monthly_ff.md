# Monthly VAR benchmarks with the funds rate added (12 lags)

P1 = proxy VAR (instrument: NS surprise summed by month; 90% Anderson-Rubin set); WE = window-impact VAR (90% block-bootstrap interval). Per +1 pp on the 2-year in the window. `*` = 90 percent set excludes zero. u = unemployment gap (pp), P = price level (percent). F = robust first-stage F of the 2-year residual on the instrument.

## P1

| start | version | FCI | VAR | F | u 12m | u 24m | P 24m | P 36m |
|---|---|---|---|---|---|---|---|---|
| 1996 | nom | no | 2-year only (stored) | 5.6 | -0.41* [-1.10, -0.09] | -0.50* [-1.17, -0.20] | +0.11 [-0.61, +0.97] | +0.13 [-0.68, +1.09] |
| 1996 | nom | no | 2-year + funds rate | 5.3 | -0.43* [-1.33, -0.11] | -0.48* [-1.19, -0.17] | +0.22 [-0.44, +1.14] | +0.28 [-0.47, +1.37] |
| 1996 | nom | yes | 2-year only (stored) | 1.8 | -0.21 unbounded | -0.29 unbounded | -0.17 unbounded | -0.19 unbounded |
| 1996 | nom | yes | 2-year + funds rate | 1.4 | -0.24 unbounded | -0.19 unbounded | -0.06 unbounded | -0.03 unbounded |
| 1996 | real | no | 2-year only (stored) | 4.7 | -0.43* [-1.69, -0.05] | -0.53* [-1.80, -0.16] | -0.09 [-1.07, +0.93] | -0.09 [-1.21, +1.04] |
| 1996 | real | no | 2-year + funds rate | 5.1 | -0.39* [-1.55, -0.01] | -0.44* [-1.47, -0.04] | -0.13 [-1.01, +0.79] | -0.13 [-1.14, +0.90] |
| 1996 | real | yes | 2-year only (stored) | 1.7 | -0.16 unbounded | -0.27 unbounded | -0.44 unbounded | -0.48 unbounded |
| 1996 | real | yes | 2-year + funds rate | 1.6 | -0.08 unbounded | -0.11 unbounded | -0.65 unbounded | -0.72 unbounded |
| 1973 | nom | no | 2-year only (stored) | 3.8 | -0.30 [-2.01, +0.13] | -0.19 [-1.48, +0.14] | +0.14 [-1.41, +2.32] | +0.21 [-1.81, +3.17] |
| 1973 | nom | no | 2-year + funds rate | 3.8 | -0.32 [-1.95, +0.09] | -0.25 [-1.48, +0.08] | +0.12 [-1.25, +2.62] | +0.17 [-1.62, +3.55] |
| 1973 | nom | yes | 2-year only (stored) | 0.5 | -0.26 unbounded | -0.16 unbounded | +0.03 unbounded | +0.03 unbounded |
| 1973 | nom | yes | 2-year + funds rate | 0.2 | -0.49 unbounded | -0.58 unbounded | -0.14 unbounded | -0.17 unbounded |
| 1973 | real | no | 2-year only (stored) | 3.2 | -0.37 [-5.52, +0.13] | -0.27 [-4.09, +0.11] | -0.10 [-2.33, +3.96] | -0.13 [-2.95, +5.54] |
| 1973 | real | no | 2-year + funds rate | 3.2 | -0.31 [-4.97, +0.20] | -0.25 [-3.50, +0.21] | -0.08 [-2.07, +5.23] | -0.11 [-2.69, +6.99] |
| 1973 | real | yes | 2-year only (stored) | 0.3 | -0.43 unbounded | -0.32 unbounded | -0.20 unbounded | -0.26 unbounded |
| 1973 | real | yes | 2-year + funds rate | 0.2 | -0.36 unbounded | -0.41 unbounded | -0.18 unbounded | -0.24 unbounded |

## WE

| start | version | FCI | VAR | F | u 12m | u 24m | P 24m | P 36m |
|---|---|---|---|---|---|---|---|---|
| 1996 | nom | no | 2-year only (stored) | 5.6 | -0.23* [-0.38, -0.06] | -0.33* [-0.52, -0.00] | +0.04 [-0.21, +0.32] | +0.04 [-0.31, +0.43] |
| 1996 | nom | no | 2-year + funds rate | 5.3 | -0.28* [-0.43, -0.12] | -0.35* [-0.57, -0.05] | +0.10 [-0.15, +0.39] | +0.13 [-0.24, +0.54] |
| 1996 | nom | yes | 2-year only (stored) | 1.8 | +0.08 [-0.10, +0.21] | +0.01 [-0.23, +0.25] | -0.14 [-0.39, +0.07] | -0.18 [-0.53, +0.10] |
| 1996 | nom | yes | 2-year + funds rate | 1.4 | +0.05 [-0.10, +0.20] | +0.08 [-0.15, +0.29] | -0.13 [-0.37, +0.10] | -0.15 [-0.45, +0.16] |
| 1996 | real | no | 2-year only (stored) | 4.7 | -0.17* [-0.27, -0.03] | -0.26* [-0.40, -0.01] | -0.04 [-0.28, +0.21] | -0.04 [-0.38, +0.28] |
| 1996 | real | no | 2-year + funds rate | 5.1 | -0.14 [-0.25, +0.01] | -0.19 [-0.35, +0.04] | -0.05 [-0.28, +0.18] | -0.03 [-0.35, +0.25] |
| 1996 | real | yes | 2-year only (stored) | 1.7 | +0.11 [-0.07, +0.24] | +0.04 [-0.18, +0.23] | -0.20 [-0.44, +0.03] | -0.23 [-0.53, +0.08] |
| 1996 | real | yes | 2-year + funds rate | 1.6 | +0.17 [-0.01, +0.29] | +0.16 [-0.07, +0.35] | -0.23 [-0.43, +0.01] | -0.25 [-0.53, +0.05] |
| 1973 | nom | no | 2-year only (stored) | 3.8 | +0.05 [-0.04, +0.13] | +0.07 [-0.03, +0.17] | -0.04 [-0.19, +0.17] | -0.07 [-0.30, +0.25] |
| 1973 | nom | no | 2-year + funds rate | 3.8 | +0.01 [-0.08, +0.10] | +0.03 [-0.08, +0.14] | -0.07 [-0.20, +0.17] | -0.11 [-0.31, +0.25] |
| 1973 | nom | yes | 2-year only (stored) | 0.5 | +0.28* [+0.14, +0.39] | +0.27* [+0.10, +0.37] | -0.07 [-0.31, +0.15] | -0.12 [-0.45, +0.21] |
| 1973 | nom | yes | 2-year + funds rate | 0.2 | +0.21* [+0.10, +0.33] | +0.17* [+0.06, +0.31] | -0.12 [-0.29, +0.13] | -0.17 [-0.40, +0.18] |
| 1973 | real | no | 2-year only (stored) | 3.2 | +0.05 [-0.04, +0.14] | +0.05 [-0.07, +0.15] | -0.31* [-0.42, -0.07] | -0.45* [-0.61, -0.07] |
| 1973 | real | no | 2-year + funds rate | 3.2 | +0.03 [-0.07, +0.11] | +0.02 [-0.09, +0.13] | -0.34* [-0.44, -0.07] | -0.47* [-0.63, -0.05] |
| 1973 | real | yes | 2-year only (stored) | 0.3 | +0.28* [+0.13, +0.39] | +0.26* [+0.07, +0.35] | -0.32* [-0.51, -0.05] | -0.44* [-0.70, -0.05] |
| 1973 | real | yes | 2-year + funds rate | 0.2 | +0.23* [+0.12, +0.33] | +0.19* [+0.06, +0.32] | -0.35* [-0.52, -0.09] | -0.46* [-0.69, -0.08] |
