# Financial conditions and r* in estimating monetary transmission (draft note, 1 Nov 2026)

**Claim.** High-frequency monetary surprises give sensible, significant effects of policy on unemployment and prices only when two things are accounted for: (1) **financial conditions as a whole** (the market index, FCI) as the channel through which policy reaches the economy, and (2) the **trend in r\*** in the level of rates. Without them, the same surprises reproduce the puzzles of the post-1994 literature; with them, the puzzles disappear and the responses match or exceed the best-practice estimates of Bauer and Swanson (2023). To our knowledge [inference, based on the papers read for this project, not a systematic search] neither ingredient is used in the high-frequency-identification literature, whose VARs propagate the shock through a nominal 1- or 2-year rate.

Tags: [verified] = computed here (scripts and logs named below); [read from figure] = read off a published chart; [inference] = our reading. Exploratory work that led here is in `MF_DEVELOPMENT.md` and is not part of the note.

## 1. Method
- **Shock.** The Nakamura-Steinsson policy-news surprise (USMPD, 253 FOMC announcements, 1994-2026), measured in 30-minute windows.
- **Impact.** In the window, the 2-year yield moves (scaled to +1 pp) and, when included, the market index moves (+0.99 per 1 pp on the 2-year); unemployment and prices do not move in the window.
- **Daily block.** From the announcement day on, a daily model (HAR form: 1-, 5-, 22- and 66-day averages) carries the 2-year and, when included, the index forward; it also responds to this month's and last month's macro conditions.
- **Monthly block.** Unemployment gap and core PCE inflation are rows of a monthly VAR with L lags of each and L lags of the monthly averages of the daily variables (OLS, 1994-2026, 2020-03 to 2020-12 dropped); L = 3, 6, 12. The announcement's day in the month is taken into account (the event month gets only the post-announcement days).
- **Steps: identical to the FCI note** (`fci_note`, section 3): **nominal → real → r\***. The FCI at each step is that note's market index at the same step (`indexes_nominal/real/rstar.csv`: the 10-year yield, nominal, net of 10-year expected inflation, then also net of Laubach-Williams r\*; equities as log CAPE, then as the earnings-yield gap E/P − r\*; the real broad dollar throughout; the same weights). The 2-year follows the same rule: nominal; net of matched-horizon (2-year) expected inflation (Cleveland Fed); then also net of the one-sided Laubach-Williams r\*. The daily FCI follows the daily 10-year, CAPE and dollar and is shifted so that its monthly average equals that note's index exactly. These adjustments move slowly, so the window moves are the same at every step.
- **Identifying assumption.** The announcement affects unemployment and prices only through the variables in the daily block (the 2-year, and the FCI when included), and the economy responds to a given move in those variables the same way whatever caused it.
- **Inference.** 200 draws: events resampled (window impact and event timing) and residual bootstrap of the monthly equations. \* = 90% interval excludes zero. Cells show 3 / 6 / 12 lags.
- Code and output: `midas_core.py`; `midas_core.log`, `midas_core.csv`, `midas_core_irf.csv`. Responses are per +1 pp policy-induced rise in the 2-year yield.

## 2. Step 1: the standard set-up reproduces the puzzles
Nominal 2-year as the only channel (the variable used by Gertler-Karadi and Bauer-Swanson), no FCI.

**Unemployment gap (pp)**

| Step (rate and FCI) | FCI | 12 months | 24 months | 36 months |
|---|---|---|---|---|
| nominal | no | −0.13 / −0.27* / −0.34* | −0.01 / −0.19 / −0.36* | +0.08 / −0.08 / −0.25 |

**Core PCE price level (%)**

| Step (rate and FCI) | FCI | 12 months | 24 months | 36 months |
|---|---|---|---|---|
| nominal | no | +0.01 / +0.06 / +0.01 | −0.08 / +0.03 / +0.05 | −0.17 / −0.07 / +0.03 |

Unemployment **falls** after a tightening (significantly with 6 and 12 lags) and prices do not move: the activity and price puzzles reported for post-1994 samples (Ramey 2016; Bauer-Swanson with unadjusted surprises; Nakamura-Steinsson's information effect). Industrial production, added in section 6, **rises** significantly. [verified]

## 3. Step 2: add financial conditions (nominal)

**Unemployment gap (pp)**

| Step (rate and FCI) | FCI | 12 months | 24 months | 36 months |
|---|---|---|---|---|
| nominal | no | −0.13 / −0.27* / −0.34* | −0.01 / −0.19 / −0.36* | +0.08 / −0.08 / −0.25 |
| nominal | yes | +0.18* / +0.09 / +0.07 | +0.38* / +0.29* / +0.19 | +0.42* / +0.37* / +0.24* |

**Core PCE price level (%)**

| Step (rate and FCI) | FCI | 12 months | 24 months | 36 months |
|---|---|---|---|---|
| nominal | no | +0.01 / +0.06 / +0.01 | −0.08 / +0.03 / +0.05 | −0.17 / −0.07 / +0.03 |
| nominal | yes | −0.09 / −0.07 / −0.10 | −0.28 / −0.24 / −0.23 | −0.42 / −0.41 / −0.36 |

With the FCI as a channel, the unemployment response turns **conventional**: positive at every horizon, significant at 36 months for every lag length, at 24 months with 3 and 6 lags, and at 12 months with 3 lags. The price level falls (−0.2 to −0.4% at 24-36 months) but is not significant. [verified]

## 4. Step 3: real rates

**Unemployment gap (pp)**

| Step (rate and FCI) | FCI | 12 months | 24 months | 36 months |
|---|---|---|---|---|
| nominal | no | −0.13 / −0.27* / −0.34* | −0.01 / −0.19 / −0.36* | +0.08 / −0.08 / −0.25 |
| nominal | yes | +0.18* / +0.09 / +0.07 | +0.38* / +0.29* / +0.19 | +0.42* / +0.37* / +0.24* |
| real | no | −0.02 / −0.14 / −0.25* | +0.07 / −0.10 / −0.28* | +0.12 / −0.03 / −0.21 |
| real | yes | +0.25* / +0.18 / +0.12 | +0.40* / +0.33* / +0.24* | +0.38* / +0.36* / +0.26* |

**Core PCE price level (%)**

| Step (rate and FCI) | FCI | 12 months | 24 months | 36 months |
|---|---|---|---|---|
| nominal | no | +0.01 / +0.06 / +0.01 | −0.08 / +0.03 / +0.05 | −0.17 / −0.07 / +0.03 |
| nominal | yes | −0.09 / −0.07 / −0.10 | −0.28 / −0.24 / −0.23 | −0.42 / −0.41 / −0.36 |
| real | no | −0.10 / −0.02 / −0.07 | −0.19 / −0.08 / −0.06 | −0.26 / −0.16 / −0.08 |
| real | yes | −0.17 / −0.14 / −0.18* | −0.33 / −0.32 / −0.31 | −0.44 / −0.47* / −0.41 |

Measuring rates net of expected inflation changes little, as in the FCI note, where the nominal and real indexes are close after 1990: without the FCI the puzzle remains (unemployment significantly negative with 12 lags); with it, unemployment is conventional and the 12-month response is still weak with 6 and 12 lags. [verified]

## 5. Step 4: gaps to r\* (baseline)

**Unemployment gap (pp)**

| Step (rate and FCI) | FCI | 12 months | 24 months | 36 months |
|---|---|---|---|---|
| nominal | no | −0.13 / −0.27* / −0.34* | −0.01 / −0.19 / −0.36* | +0.08 / −0.08 / −0.25 |
| nominal | yes | +0.18* / +0.09 / +0.07 | +0.38* / +0.29* / +0.19 | +0.42* / +0.37* / +0.24* |
| real | no | −0.02 / −0.14 / −0.25* | +0.07 / −0.10 / −0.28* | +0.12 / −0.03 / −0.21 |
| real | yes | +0.25* / +0.18 / +0.12 | +0.40* / +0.33* / +0.24* | +0.38* / +0.36* / +0.26* |
| r\*-gap | no | +0.08 / +0.03 / −0.08 | +0.16 / +0.04 / −0.15 | +0.20 / +0.05 / −0.16 |
| r\*-gap | yes | +0.30* / +0.32* / +0.34* | +0.38* / +0.39* / +0.41* | +0.34* / +0.38* / +0.37* |
| *Bauer-Swanson (2023) benchmark* | | +0.19* | +0.17 | +0.15 |

**Core PCE price level (%)**

| Step (rate and FCI) | FCI | 12 months | 24 months | 36 months |
|---|---|---|---|---|
| nominal | no | +0.01 / +0.06 / +0.01 | −0.08 / +0.03 / +0.05 | −0.17 / −0.07 / +0.03 |
| nominal | yes | −0.09 / −0.07 / −0.10 | −0.28 / −0.24 / −0.23 | −0.42 / −0.41 / −0.36 |
| real | no | −0.10 / −0.02 / −0.07 | −0.19 / −0.08 / −0.06 | −0.26 / −0.16 / −0.08 |
| real | yes | −0.17 / −0.14 / −0.18* | −0.33 / −0.32 / −0.31 | −0.44 / −0.47* / −0.41 |
| r\*-gap | no | −0.15 / −0.13 / −0.19* | −0.22 / −0.26 / −0.31 | −0.28 / −0.39 / −0.44 |
| r\*-gap | yes | −0.18 / −0.25* / −0.33* | −0.28 / −0.48* / −0.61* | −0.37 / −0.68* / −0.84* |
| *Bauer-Swanson (2023) benchmark* | | −0.36* | −0.48* | −0.6* |

Measuring rates relative to r\* is the decisive step. **Without** the FCI it does not fix the puzzle (unemployment insignificant). **With** the FCI, unemployment is significant at 12, 24 and 36 months for every lag length (+0.30 to +0.34 at 12 months, +0.34 to +0.38 at 36) and nearly identical across lag lengths, and the price level is significant at 12, 24 and 36 months with 6 and 12 lags (−0.48 to −0.61% at 24 months). [verified]

**Relative to Bauer-Swanson** (benchmark proxy-SVAR, FOMC and Chair-speech surprises orthogonalized to pre-announcement news, VAR 1973-2020; values per 1 pp on the 2-year [read from figure]; their 90% bands are standard bootstrap bands): our unemployment response is larger and more persistent (+0.30 to +0.34 against +0.19 at 12 months; their band includes zero after about 18-20 months, ours excludes it through 36); the price level is about the same size (−0.5 to −0.6% at 24 months against −0.48%). We obtain this from FOMC windows alone, without orthogonalizing the surprise or adding speeches. [inference for the comparison]

## 6. Robustness: adding industrial production
Same steps with industrial production (100 log IP) in the monthly block.

**Unemployment gap (pp)**

| Step (rate and FCI) | FCI | 12 months | 24 months | 36 months |
|---|---|---|---|---|
| nominal | no | −0.01 / −0.06 / −0.20 | +0.21 / +0.16 / −0.08 | +0.34 / +0.34 / +0.16 |
| nominal | yes | +0.41* / +0.36* / +0.25* | +0.63* / +0.62* / +0.52* | +0.57* / +0.61* / +0.57* |
| real | no | +0.06 / +0.02 / −0.14 | +0.22 / +0.16 / −0.05 | +0.31 / +0.26 / +0.11 |
| real | yes | +0.41* / +0.38* / +0.27* | +0.56* / +0.56* / +0.49* | +0.47* / +0.51* / +0.51* |
| r\*-gap | no | +0.10 / +0.09 / −0.03 | +0.20 / +0.13 / −0.05 | +0.25 / +0.13 / +0.01 |
| r\*-gap | yes | +0.28* / +0.34* / +0.33* | +0.35* / +0.39* / +0.41* | +0.30* / +0.37* / +0.38 |
| *Bauer-Swanson (2023) benchmark* | | +0.19* | +0.17 | +0.15 |

**Core PCE price level (%)**

| Step (rate and FCI) | FCI | 12 months | 24 months | 36 months |
|---|---|---|---|---|
| nominal | no | +0.01 / +0.03 / +0.06 | −0.10 / −0.09 / +0.12 | −0.21 / −0.26 / +0.11 |
| nominal | yes | −0.13 / −0.15 / −0.15 | −0.34 / −0.43 / −0.30 | −0.45 / −0.63 / −0.44 |
| real | no | −0.11 / −0.04 / −0.02 | −0.21 / −0.16 / +0.03 | −0.30 / −0.31 / +0.02 |
| real | yes | −0.20 / −0.18 / −0.19* | −0.37 / −0.44* / −0.32 | −0.45 / −0.62 / −0.44 |
| r\*-gap | no | −0.13 / −0.13 / −0.19* | −0.19 / −0.30 / −0.33 | −0.24 / −0.47 / −0.49 |
| r\*-gap | yes | −0.17 / −0.26* / −0.37* | −0.25 / −0.52* / −0.67* | −0.33 / −0.75* / −0.92* |
| *Bauer-Swanson (2023) benchmark* | | −0.36* | −0.48* | −0.6* |

**Industrial production (%)**

| Step (rate and FCI) | FCI | 12 months | 24 months | 36 months |
|---|---|---|---|---|
| nominal | no | +1.15* / +1.15* / +1.64* | +1.05 / +1.10 / +1.63* | +1.01 / +1.04 / +1.23 |
| nominal | yes | −0.17 / −0.36 / −0.08 | −0.10 / −0.14 / −0.09 | +0.50 / +0.35 / +0.27 |
| real | no | +0.70 / +0.68 / +1.13* | +0.71 / +0.83 / +1.29* | +0.76 / +0.92 / +1.04 |
| real | yes | −0.36 / −0.59 / −0.36 | −0.12 / −0.20 / −0.16 | +0.48 / +0.30 / +0.27 |
| r\*-gap | no | +0.22 / +0.15 / +0.43 | +0.26 / +0.56 / +0.87 | +0.33 / +0.82 / +0.77 |
| r\*-gap | yes | −0.47 / −0.88* / −0.91* | −0.14 / −0.32 / −0.51 | +0.36 / +0.10 / −0.12 |
| *Bauer-Swanson (2023) benchmark* | | −1.5* | −1.0* | −0.85* |

The same sequence holds. Without the FCI industrial production **rises** at every step (significantly with the nominal rate, and with the real rate at 12 lags); with the FCI it falls; at the r\* step the fall is significant at 12 months with 6 and 12 lags (about −0.9%), against about −1.5% in Bauer-Swanson, and recovers faster. Unemployment and prices are as in the core cases. [verified]

## 7. Why the two ingredients matter [inference]
1. **Financial conditions.** The window measures how far financial conditions as a whole (long rates, equity valuation, the dollar) move with policy, and the daily block carries that forward. A policy rate alone, linked to unemployment in a reduced-form way, picks up the procyclical co-movement of rates and activity (rates rise in booms), which produces the wrong signs; the index's components carry the contractionary part of the policy move.
2. **r\*.** From 1994 to 2021 rates trend down with r\* while activity trends up; in levels, the rate-to-activity link partly picks up these opposing trends. Netting r\* out leaves the cyclical stance of policy, which is what transmits. Expected inflation, which moved little after 1994, matters little.
3. Both are needed: r\* alone does not fix the puzzles, and the FCI alone gives the right sign but imprecise, lag-sensitive estimates.

## 8. Caveats
- The identifying assumption (section 1) is strong; a direct regression of unemployment on the surprises, which does not impose it, is too imprecise to test it (`MF_DEVELOPMENT.md`).
- Part of the gain may reflect a better fit by construction: r\* and the index weights are estimated, and the index weights come from the same NS events.
- The 90% intervals exclude uncertainty in the daily block and in r\*.
- Credit spreads (Caldara-Herbst) are not in the window impact.
- Bauer-Swanson's values are read from their figure.

Sources: Bauer and Swanson (2023), [NBER WP 29939](https://www.nber.org/papers/w29939); Nakamura and Steinsson (2018, QJE); Caldara and Herbst (2019, AEJ: Macro), [FEDS 2016-049](https://www.federalreserve.gov/econresdata/feds/2016/files/2016049pap.pdf); Gertler and Karadi (2015, AEJ: Macro); Ramey (2016, Handbook of Macroeconomics) [secondhand].
