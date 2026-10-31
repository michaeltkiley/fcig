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

## 7. Robustness: r\* estimate, and trends in place of the adjustments (FS-A19; `midas_core.py ... kiley-0,kiley-1` and `... nom-0,nom-1,nom-real trend`; `midas_robust.log`, `midas_robust{,_irf}.csv`) [verified]
(a) **Kiley's r\*** in place of Laubach-Williams, in both the 2-year and the FCI (the FCI note's own Kiley check index). (b) **No real or r\* adjustment**: the nominal 2-year, with a quadratic time trend (t, t²) in every monthly equation instead, without the FCI, with the nominal FCI, and with the real FCI. Cells: 3 / 6 / 12 lags; \* = 90% interval excludes zero.

**Unemployment gap (pp)**

| Rate | FCI | 12 months | 24 months | 36 months |
|---|---|---|---|---|
| r\*-gap (Laubach-Williams), baseline | no | +0.08 / +0.03 / −0.08 | +0.16 / +0.04 / −0.15 | +0.20 / +0.05 / −0.16 |
| r\*-gap (Laubach-Williams), baseline | r\*-gap (LW) | +0.30* / +0.32* / +0.34* | +0.38* / +0.39* / +0.41* | +0.34* / +0.38* / +0.37* |
| r\*-gap (Kiley) | no | +0.00 / −0.11 / −0.22* | +0.06 / −0.10 / −0.29* | +0.09 / −0.07 / −0.25 |
| r\*-gap (Kiley) | r\*-gap (Kiley) | +0.38* / +0.28* / +0.15 | +0.47* / +0.36 / +0.14 | +0.37* / +0.30 / +0.09 |
| nominal, no trend (step 1-2) | no | −0.13 / −0.27* / −0.34* | −0.01 / −0.19 / −0.36* | +0.08 / −0.08 / −0.25 |
| nominal, no trend (step 1-2) | nominal | +0.18* / +0.09 / +0.07 | +0.38* / +0.29* / +0.19 | +0.42* / +0.37* / +0.24* |
| nominal + quadratic trend | no | +0.07 / −0.13 / −0.27* | +0.36 / +0.10 / −0.19 | +0.53* / +0.29 / −0.00 |
| nominal + quadratic trend | nominal | +0.44* / +0.36* / +0.28* | +0.76* / +0.75* / +0.63* | +0.76* / +0.83* / +0.77* |
| nominal + quadratic trend | real | +0.41* / +0.32* / +0.25* | +0.69* / +0.67* / +0.57* | +0.68* / +0.74* / +0.70* |
| *Bauer-Swanson (2023) benchmark* | | +0.19* | +0.17 | +0.15 |

**Core PCE price level (%)**

| Rate | FCI | 12 months | 24 months | 36 months |
|---|---|---|---|---|
| r\*-gap (Laubach-Williams), baseline | no | −0.15 / −0.13 / −0.19* | −0.22 / −0.26 / −0.31 | −0.28 / −0.39 / −0.44 |
| r\*-gap (Laubach-Williams), baseline | r\*-gap (LW) | −0.18 / −0.25* / −0.33* | −0.28 / −0.48* / −0.61* | −0.37 / −0.68* / −0.84* |
| r\*-gap (Kiley) | no | −0.13 / −0.07 / −0.12 | −0.18 / −0.11 / −0.11 | −0.22 / −0.16 / −0.10 |
| r\*-gap (Kiley) | r\*-gap (Kiley) | −0.13 / −0.12 / −0.16 | −0.21 / −0.15 / −0.06 | −0.29 / −0.21 / +0.08 |
| nominal, no trend (step 1-2) | no | +0.01 / +0.06 / +0.01 | −0.08 / +0.03 / +0.05 | −0.17 / −0.07 / +0.03 |
| nominal, no trend (step 1-2) | nominal | −0.09 / −0.07 / −0.10 | −0.28 / −0.24 / −0.23 | −0.42 / −0.41 / −0.36 |
| nominal + quadratic trend | no | −0.03 / −0.01 / −0.02 | −0.16 / −0.16 / −0.07 | −0.26 / −0.34 / −0.18 |
| nominal + quadratic trend | nominal | −0.09 / −0.11 / −0.11 | −0.24 / −0.36 / −0.31 | −0.33 / −0.54 / −0.49 |
| nominal + quadratic trend | real | −0.09 / −0.11 / −0.13 | −0.23 / −0.34 / −0.33 | −0.31 / −0.51 / −0.50 |
| *Bauer-Swanson (2023) benchmark* | | −0.36* | −0.48* | −0.6* |

**With industrial production: IP (%)**

| Rate | FCI | 12 months | 24 months | 36 months |
|---|---|---|---|---|
| r\*-gap (Laubach-Williams), baseline | no | +0.22 / +0.15 / +0.43 | +0.26 / +0.56 / +0.87 | +0.33 / +0.82 / +0.77 |
| r\*-gap (Laubach-Williams), baseline | r\*-gap (LW) | −0.47 / −0.88* / −0.91* | −0.14 / −0.32 / −0.51 | +0.36 / +0.10 / −0.12 |
| r\*-gap (Kiley) | no | +0.70 / +0.74* / +1.13* | +0.83 / +1.14* / +1.55* | +0.89 / +1.24* / +1.33* |
| r\*-gap (Kiley) | r\*-gap (Kiley) | −0.27 / −0.27 / +0.04 | +0.16 / +0.42 / +0.86 | +0.66 / +0.68 / +1.08* |
| nominal, no trend (step 1-2) | no | +1.15* / +1.15* / +1.64* | +1.05 / +1.10 / +1.63* | +1.01 / +1.04 / +1.23 |
| nominal, no trend (step 1-2) | nominal | −0.17 / −0.36 / −0.08 | −0.10 / −0.14 / −0.09 | +0.50 / +0.35 / +0.27 |
| nominal + quadratic trend | no | +1.06* / +1.26* / +1.65* | +1.03 / +1.26* / +1.64* | +1.16 / +1.00 / +1.10 |
| nominal + quadratic trend | nominal | −0.16 / −0.29 / +0.11 | −0.09 / −0.04 / +0.15 | +0.45 / +0.39 / +0.43 |
| nominal + quadratic trend | real | −0.11 / −0.25 / +0.11 | −0.04 / +0.01 / +0.14 | +0.45 / +0.39 / +0.37 |
| *Bauer-Swanson (2023) benchmark* | | −1.5* | −1.0* | −0.85* |

**(c) The 2-year minus its trailing 8-year moving average** (FS-A20), with no FCI and with each of the three FCI forms. The trend this removes compares with the Laubach-Williams trend in the r\*-gap 2-year (2-year expected inflation plus LW r\*) as follows [verified]: monthly correlation of the two trends 0.80 (1994-2026); averages 5.3 vs 5.5 (1994-2007) and 2.3 vs 2.5 (2008-2015), but 1.4 vs 3.6 (2016-2026), when the 8-year average of the 2-year fell to about 0.7-1 while LW r\* (1.1-2.0) plus expected inflation (1.3-2.5) stayed at 3-4; the resulting rate gaps correlate 0.63 (LW vs Kiley gaps: 0.88). LW r\* is the New York Fed's current one-sided estimate (vintage 26 Aug 2026), identical to the FCI note's file (checked against the NY Fed spreadsheet).

**Unemployment gap (pp)**

| 2-year minus its 8-year average, FCI | 12 months | 24 months | 36 months |
|---|---|---|---|
| no FCI | −0.22* / −0.30* / −0.36* | −0.23 / −0.28 / −0.46* | −0.22 / −0.21 / −0.40* |
| nominal FCI | +0.23* / +0.18 / +0.15 | +0.38* / +0.36* / +0.27 | +0.34* / +0.36* / +0.27* |
| real FCI | +0.25* / +0.19 / +0.15 | +0.37* / +0.36* / +0.28 | +0.31* / +0.34* / +0.29 |
| r\*-gap FCI | +0.06 / +0.08 / +0.14 | +0.10 / +0.15 / +0.18 | +0.08 / +0.15 / +0.18 |

**Core PCE price level (%)**

| 2-year minus its 8-year average, FCI | 12 months | 24 months | 36 months |
|---|---|---|---|
| no FCI | +0.19 / +0.10 / +0.02 | +0.37 / +0.22 / +0.10 | +0.50 / +0.28 / +0.17 |
| nominal FCI | +0.01 / −0.07 / −0.11 | −0.02 / −0.19 / −0.23 | −0.02 / −0.24 / −0.31 |
| real FCI | +0.02 / −0.07 / −0.14 | +0.02 / −0.15 / −0.28 | +0.05 / −0.19 / −0.38 |
| r\*-gap FCI | +0.07 / −0.05 / −0.15 | +0.19 / −0.07 / −0.27 | +0.29 / −0.06 / −0.35 |

**With industrial production: IP (%)**

| 2-year minus its 8-year average, FCI | 12 months | 24 months | 36 months |
|---|---|---|---|
| no FCI | +1.07* / +1.24* / +1.45* | +1.03 / +1.43* / +1.80* | +0.92 / +1.27* / +1.50* |
| nominal FCI | −0.32 / −0.35 / −0.12 | −0.28 / −0.01 / +0.01 | +0.15 / +0.36 / +0.31 |
| real FCI | −0.28 / −0.31 / −0.15 | −0.22 / +0.02 / −0.09 | +0.19 / +0.35 / +0.10 |
| r\*-gap FCI | +0.03 / −0.36 / −0.25 | +0.13 / +0.01 / −0.12 | +0.30 / +0.25 / −0.02 |

Reading: the moving-average adjustment does **not** do what the r\* gap does. Without the FCI the puzzle is worse (unemployment significantly negative at 12 months for all lags); with the nominal or real FCI the results look like the nominal step with the FCI (unemployment conventional, significant mainly at 24-36 months with 3 and 6 lags; prices not significant; IP not falling); paired with the r\*-gap FCI, nothing is significant. A purely statistical trend in the 2-year therefore does not substitute for r\*; the gain at the r\* step comes from the LW trend, which differs from the moving average mainly after 2016. [verified; interpretation inference]

Reading of (a) and (b):
1. **The FCI remains essential.** In every variant, without the FCI unemployment is insignificant or wrong-signed and IP rises; with the FCI unemployment is conventional. [verified]
2. **Kiley's r\* weakens the result.** With the FCI, unemployment is significant with 3 lags (+0.38 at 12 months) and at 12 months with 6 lags, but not with 12 lags; the price level is never significant; IP does not fall robustly. So the strength of the r\* step depends on the r\* estimate: Laubach-Williams delivers it, Kiley's estimate (which moves differently after 2008) much less. [verified; the reason is an inference]
3. **A quadratic trend can stand in for the r\* adjustment for unemployment, not for prices or IP.** With the nominal 2-year, a trend and the FCI (nominal or real), unemployment is significant at all horizons and lags but one, and larger and more persistent than in the baseline (+0.3 to +0.4 at 12 months, +0.7 to +0.8 at 36); the price level falls (−0.3 to −0.5% at 24-36 months) but is never significant, and IP does not fall. Without the FCI the trend does not remove the puzzle. [verified]
4. **For the note** [inference]: the FCI is robust; "removing slow-moving trends from rates" is robust for unemployment (r\* or a deterministic trend both work); the significant price and IP responses need the Laubach-Williams r\* gap specifically. The claim about r\* should be stated with that qualification.

## 8. Why the two ingredients matter [inference]
1. **Financial conditions.** The window measures how far financial conditions as a whole (long rates, equity valuation, the dollar) move with policy, and the daily block carries that forward. A policy rate alone, linked to unemployment in a reduced-form way, picks up the procyclical co-movement of rates and activity (rates rise in booms), which produces the wrong signs; the index's components carry the contractionary part of the policy move.
2. **r\*.** From 1994 to 2021 rates trend down with r\* while activity trends up; in levels, the rate-to-activity link partly picks up these opposing trends. Netting r\* out leaves the cyclical stance of policy, which is what transmits. Expected inflation, which moved little after 1994, matters little.
3. Both are needed: r\* alone does not fix the puzzles, and the FCI alone gives the right sign but imprecise, lag-sensitive estimates.
4. Qualification (section 7): the slow-moving part of rates can also be removed with a deterministic trend, which works for unemployment; significant price and IP responses need the Laubach-Williams r\* gap; Kiley's r\* gives weaker results.

## 9. Caveats
- The identifying assumption (section 1) is strong; a direct regression of unemployment on the surprises, which does not impose it, is too imprecise to test it (`MF_DEVELOPMENT.md`).
- Part of the gain may reflect a better fit by construction: r\* and the index weights are estimated, and the index weights come from the same NS events.
- The 90% intervals exclude uncertainty in the daily block and in r\*.
- Credit spreads (Caldara-Herbst) are not in the window impact.
- Bauer-Swanson's values are read from their figure.

Sources: Bauer and Swanson (2023), [NBER WP 29939](https://www.nber.org/papers/w29939); Nakamura and Steinsson (2018, QJE); Caldara and Herbst (2019, AEJ: Macro), [FEDS 2016-049](https://www.federalreserve.gov/econresdata/feds/2016/files/2016049pap.pdf); Gertler and Karadi (2015, AEJ: Macro); Ramey (2016, Handbook of Macroeconomics) [secondhand].
