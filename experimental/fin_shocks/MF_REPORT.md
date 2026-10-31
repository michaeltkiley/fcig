# Financial conditions and r* in estimating monetary transmission (draft note, 1 Nov 2026)

**Claim.** High-frequency monetary surprises give sensible, significant effects of policy on unemployment and prices only when two things are accounted for: (1) **financial conditions as a whole** (the market index, FCI) as the channel through which policy reaches the economy, and (2) the **trend in r\*** (and in expected inflation) in the level of the policy rate. Without them, the same surprises reproduce the puzzles of the post-1994 literature; with them, the puzzles disappear and the responses match or exceed the best-practice estimates of Bauer and Swanson (2023). To our knowledge [inference, based on the papers read for this project, not a systematic search] neither ingredient is used in the high-frequency-identification literature, whose VARs propagate the shock through a nominal 1- or 2-year rate.

Tags: [verified] = computed here (scripts and logs named below); [read from figure] = read off a published chart; [inference] = our reading. Exploratory work that led here is in `MF_DEVELOPMENT.md` and is not part of the note.

## 1. Method
- **Shock.** The Nakamura-Steinsson policy-news surprise (USMPD, 253 FOMC announcements, 1994-2026), measured in 30-minute windows.
- **Impact.** In the window, the 2-year yield moves (scaled to +1 pp) and, when included, the market index moves (+0.99 per 1 pp on the 2-year); unemployment and prices do not move in the window.
- **Daily block.** From the announcement day on, a daily model (HAR form: 1-, 5-, 22- and 66-day averages) carries the 2-year and, when included, the index forward; it also responds to this month's and last month's macro conditions.
- **Monthly block.** Unemployment gap and core PCE inflation are rows of a monthly VAR with L lags of each and L lags of the monthly averages of the daily variables (OLS, 1994-2026, 2020-03 to 2020-12 dropped); L = 3, 6, 12. The announcement's day in the month is taken into account (the event month gets only the post-announcement days).
- **Rate forms.** Nominal 2-year; 2-year minus Laubach-Williams r\*; 2-year minus 1-year expected inflation and r\* (the note's r\*-gap policy variable). The FCI, when included, is in the matching form (nominal index; nominal index plus the r\* adjustment; r\*-gap index). The r\* and expected-inflation adjustments move slowly, so they do not change the window moves.
- **Identifying assumption.** The announcement affects unemployment and prices only through the variables in the daily block (the 2-year, and the FCI when included), and the economy responds to a given move in those variables the same way whatever caused it.
- **Inference.** 200 draws: events resampled (window impact and event timing) and residual bootstrap of the monthly equations. \* = 90% interval excludes zero. Cells show 3 / 6 / 12 lags.
- Code and output: `midas_core.py`; `midas_core.log`, `midas_core.csv`, `midas_core_irf.csv`. Responses are per +1 pp policy-induced rise in the 2-year yield.

## 2. Step 1: the standard set-up reproduces the puzzles
Nominal 2-year as the only channel (the variable used by Gertler-Karadi and Bauer-Swanson), no FCI.

**Unemployment gap (pp)**

| Rate | FCI | 12 months | 24 months | 36 months |
|---|---|---|---|---|
| 2-year nominal | no | −0.13 / −0.27* / −0.34* | −0.01 / −0.19 / −0.36* | +0.08 / −0.08 / −0.25 |

**Core PCE price level (%)**

| Rate | FCI | 12 months | 24 months | 36 months |
|---|---|---|---|---|
| 2-year nominal | no | +0.01 / +0.06 / +0.01 | −0.08 / +0.03 / +0.05 | −0.17 / −0.07 / +0.03 |

Unemployment **falls** after a tightening (significantly with 6 and 12 lags) and prices do not move: the price and activity puzzles reported for post-1994 samples (Ramey 2016; Bauer-Swanson with unadjusted surprises; Nakamura-Steinsson's "information effect"). Industrial production, added in section 6, **rises** significantly. [verified]

## 3. Step 2: add financial conditions

**Unemployment gap (pp)**

| Rate | FCI | 12 months | 24 months | 36 months |
|---|---|---|---|---|
| 2-year nominal | no | −0.13 / −0.27* / −0.34* | −0.01 / −0.19 / −0.36* | +0.08 / −0.08 / −0.25 |
| 2-year nominal | yes | +0.18* / +0.09 / +0.07 | +0.38* / +0.29* / +0.19 | +0.42* / +0.37* / +0.24* |

**Core PCE price level (%)**

| Rate | FCI | 12 months | 24 months | 36 months |
|---|---|---|---|---|
| 2-year nominal | no | +0.01 / +0.06 / +0.01 | −0.08 / +0.03 / +0.05 | −0.17 / −0.07 / +0.03 |
| 2-year nominal | yes | −0.09 / −0.07 / −0.10 | −0.28 / −0.24 / −0.23 | −0.42 / −0.41 / −0.36 |

With the FCI as a channel, the unemployment response turns **conventional**: positive at every horizon, significant at 36 months for every lag length, at 24 months with 3 and 6 lags, and at 12 months with 3 lags. The price level falls (-0.2 to -0.4% at 24-36 months) but is not yet significant. [verified]

## 4. Step 3: remove the trend in r\*

**Unemployment gap (pp)**

| Rate | FCI | 12 months | 24 months | 36 months |
|---|---|---|---|---|
| 2-year nominal | no | −0.13 / −0.27* / −0.34* | −0.01 / −0.19 / −0.36* | +0.08 / −0.08 / −0.25 |
| 2-year nominal | yes | +0.18* / +0.09 / +0.07 | +0.38* / +0.29* / +0.19 | +0.42* / +0.37* / +0.24* |
| 2-year − r* | no | −0.02 / −0.10 / −0.17 | +0.10 / −0.05 / −0.25 | +0.17 / +0.01 / −0.21 |
| 2-year − r* | yes | +0.31* / +0.29* / +0.32* | +0.49* / +0.46* / +0.41* | +0.49* / +0.49* / +0.40* |

**Core PCE price level (%)**

| Rate | FCI | 12 months | 24 months | 36 months |
|---|---|---|---|---|
| 2-year nominal | no | +0.01 / +0.06 / +0.01 | −0.08 / +0.03 / +0.05 | −0.17 / −0.07 / +0.03 |
| 2-year nominal | yes | −0.09 / −0.07 / −0.10 | −0.28 / −0.24 / −0.23 | −0.42 / −0.41 / −0.36 |
| 2-year − r* | no | −0.05 / −0.04 / −0.08 | −0.15 / −0.15 / −0.14 | −0.24 / −0.28 / −0.22 |
| 2-year − r* | yes | −0.12 / −0.18 / −0.24* | −0.26 / −0.42 / −0.52* | −0.39 / −0.62 / −0.77* |

Removing r\* **without** the FCI does not help: unemployment is still insignificant and mostly wrong-signed. **With** the FCI, unemployment becomes significant at 12, 24 and 36 months for every lag length (+0.29 to +0.32 at 12 months) and nearly identical across lag lengths; the price level becomes significant with 12 lags. [verified]

## 5. Step 4: remove expected inflation as well (the r\*-gap policy rate)

**Unemployment gap (pp)**

| Rate | FCI | 12 months | 24 months | 36 months |
|---|---|---|---|---|
| 2-year nominal | no | −0.13 / −0.27* / −0.34* | −0.01 / −0.19 / −0.36* | +0.08 / −0.08 / −0.25 |
| 2-year nominal | yes | +0.18* / +0.09 / +0.07 | +0.38* / +0.29* / +0.19 | +0.42* / +0.37* / +0.24* |
| 2-year − r* | no | −0.02 / −0.10 / −0.17 | +0.10 / −0.05 / −0.25 | +0.17 / +0.01 / −0.21 |
| 2-year − r* | yes | +0.31* / +0.29* / +0.32* | +0.49* / +0.46* / +0.41* | +0.49* / +0.49* / +0.40* |
| 2-year − expected inflation − r* | no | +0.11 / +0.06 / −0.07 | +0.19 / +0.04 / −0.13 | +0.22 / +0.03 / −0.15 |
| 2-year − expected inflation − r* | yes | +0.32* / +0.33* / +0.33* | +0.38* / +0.37* / +0.40* | +0.32* / +0.33* / +0.36* |
| *Bauer-Swanson (2023) benchmark* | | +0.19* | +0.17 | +0.15 |

**Core PCE price level (%)**

| Rate | FCI | 12 months | 24 months | 36 months |
|---|---|---|---|---|
| 2-year nominal | no | +0.01 / +0.06 / +0.01 | −0.08 / +0.03 / +0.05 | −0.17 / −0.07 / +0.03 |
| 2-year nominal | yes | −0.09 / −0.07 / −0.10 | −0.28 / −0.24 / −0.23 | −0.42 / −0.41 / −0.36 |
| 2-year − r* | no | −0.05 / −0.04 / −0.08 | −0.15 / −0.15 / −0.14 | −0.24 / −0.28 / −0.22 |
| 2-year − r* | yes | −0.12 / −0.18 / −0.24* | −0.26 / −0.42 / −0.52* | −0.39 / −0.62 / −0.77* |
| 2-year − expected inflation − r* | no | −0.18* / −0.12 / −0.16 | −0.29 / −0.26 / −0.27 | −0.36 / −0.39 / −0.38 |
| 2-year − expected inflation − r* | yes | −0.22* / −0.25* / −0.30* | −0.36 / −0.50* / −0.56* | −0.47 / −0.70* / −0.74* |
| *Bauer-Swanson (2023) benchmark* | | −0.36* | −0.48* | −0.6* |

With the FCI and the rate net of expected inflation and r\*, every unemployment response is significant (+0.32 to +0.33 at 12 months, +0.32 to +0.40 at 36) and the price level is significant at 12 months for all lag lengths and at 24-36 months with 6 and 12 lags (-0.50 to -0.56% at 24 months). Without the FCI, the same rate still gives insignificant unemployment responses. [verified]

**Relative to Bauer-Swanson** (benchmark proxy-SVAR, FOMC and Chair-speech surprises orthogonalized to pre-announcement news, VAR 1973-2020; values per 1 pp on the 2-year [read from figure]; their 90% bands are standard bootstrap bands): our unemployment response is larger and more persistent (+0.33 against +0.19 at 12 months; their band includes zero after about 18-20 months, ours excludes it through 36); the price-level response is about the same size (-0.5% at 24 months in both). We obtain this from FOMC windows alone, without orthogonalizing the surprise or adding speeches. [inference for the comparison]

## 6. Robustness: adding industrial production
Same cases with industrial production (100 log IP) in the monthly block.

**Unemployment gap (pp)**

| Rate | FCI | 12 months | 24 months | 36 months |
|---|---|---|---|---|
| 2-year nominal | no | −0.01 / −0.06 / −0.20 | +0.21 / +0.16 / −0.08 | +0.34 / +0.34 / +0.16 |
| 2-year nominal | yes | +0.41* / +0.36* / +0.25* | +0.63* / +0.62* / +0.52* | +0.57* / +0.61* / +0.57* |
| 2-year − r* | no | +0.06 / +0.02 / −0.09 | +0.23 / +0.16 / −0.08 | +0.32 / +0.23 / +0.05 |
| 2-year − r* | yes | +0.30* / +0.33* / +0.33* | +0.45* / +0.47* / +0.43* | +0.43* / +0.48* / +0.44 |
| 2-year − expected inflation − r* | no | +0.13 / +0.11 / −0.03 | +0.23 / +0.12 / −0.03 | +0.27 / +0.10 / +0.03 |
| 2-year − expected inflation − r* | yes | +0.30* / +0.36* / +0.33* | +0.35* / +0.38* / +0.41* | +0.30* / +0.35* / +0.38* |
| *Bauer-Swanson (2023) benchmark* | | +0.19* | +0.17 | +0.15 |

**Core PCE price level (%)**

| Rate | FCI | 12 months | 24 months | 36 months |
|---|---|---|---|---|
| 2-year nominal | no | +0.01 / +0.03 / +0.06 | −0.10 / −0.09 / +0.12 | −0.21 / −0.26 / +0.11 |
| 2-year nominal | yes | −0.13 / −0.15 / −0.15 | −0.34 / −0.43 / −0.30 | −0.45 / −0.63 / −0.44 |
| 2-year − r* | no | −0.04 / −0.07 / −0.11 | −0.13 / −0.25 / −0.21 | −0.21 / −0.46 / −0.36 |
| 2-year − r* | yes | −0.10 / −0.22 / −0.33* | −0.22 / −0.50* / −0.67* | −0.31 / −0.75* / −0.97* |
| 2-year − expected inflation − r* | no | −0.16 / −0.13 / −0.16 | −0.26 / −0.31 / −0.26 | −0.33 / −0.47 / −0.39 |
| 2-year − expected inflation − r* | yes | −0.21* / −0.26* / −0.32* | −0.35 / −0.54* / −0.56* | −0.44 / −0.76* / −0.73* |
| *Bauer-Swanson (2023) benchmark* | | −0.36* | −0.48* | −0.6* |

**Industrial production (%)**

| Rate | FCI | 12 months | 24 months | 36 months |
|---|---|---|---|---|
| 2-year nominal | no | +1.15* / +1.15* / +1.64* | +1.05 / +1.10 / +1.63* | +1.01 / +1.04 / +1.23 |
| 2-year nominal | yes | −0.17 / −0.36 / −0.08 | −0.10 / −0.14 / −0.09 | +0.50 / +0.35 / +0.27 |
| 2-year − r* | no | +0.61 / +0.61 / +1.01 | +0.51 / +0.78 / +1.31 | +0.50 / +0.89 / +1.01 |
| 2-year − r* | yes | −0.37 / −0.74 / −0.64 | −0.22 / −0.33 / −0.44 | +0.25 / +0.06 / −0.18 |
| 2-year − expected inflation − r* | no | +0.16 / +0.13 / +0.41 | +0.22 / +0.62 / +0.80 | +0.30 / +0.88 / +0.72 |
| 2-year − expected inflation − r* | yes | −0.45 / −0.87* / −0.89* | −0.04 / −0.24 / −0.46 | +0.41 / +0.15 / −0.08 |
| *Bauer-Swanson (2023) benchmark* | | −1.5* | −1.0* | −0.85* |

The same sequence holds. Without the FCI industrial production **rises** (significantly with the nominal rate); with the FCI it falls; with the FCI and the rate net of expected inflation and r\* the fall is significant at 12 months with 6 and 12 lags (-0.9%), against about -1.5% in Bauer-Swanson, and recovers faster. Unemployment and prices are as in the core cases. [verified]

## 7. Why the two ingredients matter [inference]
1. **Financial conditions.** The window measures how far financial conditions as a whole (long rates, equity valuation, the dollar) move with policy, and the daily block carries that forward. A policy rate alone, linked to unemployment in a reduced-form way, picks up the procyclical co-movement of rates and activity (rates rise in booms), which produces the wrong signs; the index's components carry the contractionary part of the policy move.
2. **r\* and expected inflation.** From 1994 to 2021 the nominal 2-year trends down with r\* and inflation expectations while activity trends up; in levels, the rate-to-activity link partly picks up these opposing trends. Netting them out leaves the cyclical stance of policy, which is what transmits.
3. Both are needed: r\* alone does not fix the puzzles, and the FCI alone gives the right sign but imprecise, lag-sensitive estimates.

## 8. Caveats and next steps
- The identifying assumption (section 1) is strong; a direct regression of unemployment on the surprises, which does not impose it, is too imprecise to test it (`MF_DEVELOPMENT.md`).
- Part of the gain may reflect a better fit by construction: r\* and the index weights are estimated, and the index weights come from the same NS events.
- The 90% intervals exclude uncertainty in the daily block and in r\*.
- Credit spreads (Caldara-Herbst) are not in the window impact.
- Bauer-Swanson's values are read from their figure.

Sources: Bauer and Swanson (2023), [NBER WP 29939](https://www.nber.org/papers/w29939); Nakamura and Steinsson (2018, QJE); Caldara and Herbst (2019, AEJ: Macro), [FEDS 2016-049](https://www.federalreserve.gov/econresdata/feds/2016/files/2016049pap.pdf); Gertler and Karadi (2015, AEJ: Macro); Ramey (2016, Handbook of Macroeconomics) [secondhand].
