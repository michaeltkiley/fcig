# Window-identified mixed-frequency VAR: development history (31 Oct - 1 Nov 2026)

Superseded as the main write-up by `MF_REPORT.md` (1 Nov 2026), which compares the chosen specification with Bauer-Swanson and others. This file keeps the stages that led there (stage 0, routes A and B, unrestricted and restricted MIDAS on all samples).

Plan and history: `MF_PLAN.md`, `MIXED_FREQUENCY_NOTES.md`, `FS_QA.md`. All numbers below are in the `.log`/`.csv` files named in each section. Tags: [verified] = computed here; [inference] = my reading; [secondhand] = literature, not checked in full text.

## 1. Question and assumptions
A monetary shock is observed only in sparse, minute-long announcement windows. Financial variables (2-year yield, 10-year yield, equities, dollar, hence the market index; funds rate via futures surprise) respond in the window. Macro variables (unemployment gap, core PCE monthly rate) do not respond in the window (macro entries of the impact vector are zero; no robustness needed, per FS-A). The impact vector b comes from 30-minute USMPD window changes. The response is Theta_h b, propagated through a daily-financial / monthly-macro model. Credit spread is excluded from the baseline (no intraday series; it responds in the window, so it would contaminate b); Baa-10y versions are flagged sensitivities only. Shocks: NS (baseline), NS-GB (Greenbook-purged), MP1 (funds-rate scaled). Samples: long (1976/77-2026, 2-year from 1976-06) and 1994+ (USMPD). 2020-03..12 dropped. Results are per +1 pp rise in the scaling variable (2-year yield for NS, NS-GB; funds rate for MP1) on impact.

## 2. Stages and results
**Stage 0, monthly-proxy check** (`stage0_window_var.*`) [verified]. Event-day shock aggregated to monthly exposure. Unemployment rises: EVENT-timing u12 about +0.2 to +0.5, START-timing (shock at start of month) 2-3 times larger. Timing within the month matters for magnitude, not sign (my earlier "matters little" claim was wrong; corrected in MF_PLAN).

**Route A, daily HAR + monthly macro rows** (`route_a.*`) [verified]. NS, no credit: long 2-year u12 +0.20 [+0.07,+0.33]; 1994+ u12 +0.34 [+0.13,+0.51], u36 +0.48; long funds-rate +0.33. NS-GB nearly identical. MP1 +0.11. HYBRID (63-day directly estimated path, then model) has the same centre but intervals that include zero. With Baa spread [contaminated] the responses fall by about a third to a half.

**Unrestricted MIDAS-VAR** (`midas_var.py/.log`, B=20; SUPERSEDED by the restricted version in section 7, because the weights are not identified) [verified]. Macro equation: m_t on 6 monthly lags plus exponentially weighted 252 daily lags of policy and index (one parameter each).

| spec, shock | MODEL u12 | PATH u12 | PATH u36 |
|---|---|---|---|
| long 1977-, 2-yr, NS | +0.10 [-0.04,+0.12] | +0.11 [+0.01,+0.18] | +0.09 |
| long 1977-, 2-yr, NS-GB | +0.10 | +0.05 [-0.23,+0.11] | -0.38 |
| 1994-, 2-yr, NS | +0.22 [+0.10,+0.42] | +0.29 [+0.03,+0.51] | +0.78 |
| 1994-, 2-yr, NS-GB | +0.21 | +0.41 [+0.08,+0.89] | +1.00 |
| long 1974-, ff, NS | +0.02 | +0.19 [-0.12,+0.39] | +0.53 |
| long 1974-, ff, MP1 | +0.05 | +0.43 [+0.14,+0.77] | +1.82 |

Caveat [verified]: the MIDAS weight parameters hit the +-8 bounds in most equations (diagnostic printed in the log header). The macro equations are nearly autoregressive, so the daily-lag shape is not identified, and the MIDAS-VAR results should not be read as independent evidence about the shape. Sign is positive in 1994+ for every shock and path; in the long sample MODEL results are small and MIDAS with funds rate turns slightly negative at 24-36 months.

**Within-month timing test** (`within_month_test.*`) [verified]. Because the full MIDAS shape is unidentified, I tested the one question that matters: do late-month days carry different weight than early-month days in the monthly equation (one parameter delta, 12 monthly lags free)? Unemployment: delta-hat 0.0, +1.0, -0.5; F(delta=0) 0.00, 2.11, 0.66, all below the 5% critical value 3.9, so equal weights (the monthly-average structure of route A and the monthly VAR) are not rejected. Core PCE: delta-hat +1.0 in all three, F 4.6-7.9 (rejected) but the R2 gain is only 0.003-0.008. So for unemployment, a within-month MIDAS adds nothing over monthly averages. [inference] This supports using the monthly-average structure in the baseline.

**Route B, daily VAR(1) state space with monthly cumulators** (`route_b*.py/.log`) [verified]. Unemployment response is small and positive (u12 +0.04 [-0.00,+0.09]) and core PCE has the wrong sign; the transmission check (`transmission_check.log`) shows the financial-to-unemployment link per index unit at 12m: monthly VAR +0.68, route A +0.35, route B +0.07. Monte Carlo (`montecarlo*.log`) recovers the truth: with the weak link the estimators (EVENT, START, A, B) are roughly unbiased, with the strong link EVENT is biased down by about half (u12 +0.39 vs true +0.70), START slightly up, A and B within 0.01 of truth with RMSE 0.09-0.16. [inference] Route B's small response is misspecification of VAR(1) dynamics, not estimator failure.

**Contamination follow-ups** (`followups.*`) [verified]: the hypothesis that macro entries of the monthly proxy impact vector drive the result is refuted.

## 3. The "directly estimated window path" in plain words
Two ways to get the index path after the shock. MODEL: take the impact vector at the announcement and let the estimated daily dynamics carry it forward. PATH (your idea): estimate directly, by local projection on the event days, the cumulative daily response of the index and policy rate up to the end of month t+1 (about 21-42 weekdays), then switch to the monthly VAR from there. PATH uses the data rather than the daily dynamics for the first one to two months, where the daily HAR gives a flat index (about 1.0) while data show momentum (about 1.3, noisy). It costs precision (wider intervals) and buys robustness to daily-model misspecification. The 63-day "HYBRID" in route A is the same idea with a longer path. [inference] I am not aware of a paper doing exactly this; Faust-Swanson-Wright (2004) [abstract only] is the closest precedent (high-frequency futures used to identify the monetary-shock effect in a monthly VAR).

## 4. Verdict
1. The sign is robust: monetary tightening (+1 pp on the 2-year) raises the unemployment gap, in stage 0, route A, MIDAS, route B, across shock versions NS / NS-GB / MP1. Without credit spread the effect is larger, with Baa smaller (contaminated, flagged).
2. The magnitude runs from about +0.04 to +0.5 pp at 12 months, depending on (i) the index path after the window (flat in daily HAR, momentum in monthly VAR) and (ii) the strength of the financial-to-unemployment link. The 1994+ sample gives larger, tighter results (u12 +0.2 to +0.4; u36 up to +0.8) than the long sample (+0.1 to +0.2).
3. The within-month shape is not a problem for unemployment (delta test).
4. Core PCE: no robust sign (price puzzle in 1994+, positive in some others); do not claim an inflation result.

## 5. Limitations
Macro-zero-in-window and exogeneity of the window shock are assumptions; information effects are acknowledged and set aside (examined in `mp_var_fci/`). The long-sample index is interpolated monthly before 1990. MIDAS weights unidentified; bootstrap B=20 for MIDAS and larger for the others; route B is a VAR(1) misspecification; the intraday impact vector uses 30-minute windows; results rely on scaling by the 2-year yield, which is weak in the long sample.

## 6. Next steps (for decision)
P1-P4 of `PROPOSALS.md` (approved, not started); optional ICE BBB daily credit spread (1997+) as a robustness; a HAR with more lags for route A to test the flat index path.

## 7. Restricted (step-weight) MIDAS-VAR: the chosen MIDAS specification (1 Nov 2026)
Script `midas_step.py`; logs `midas_step_BASE.log` (base), `midas_step_lagfeedback.log` (first run: both orderings with lagged-only macro feedback; its +CUR rows are the +CUR robustness), csv files alongside. 200 draws (events and macro-equation residuals). Decisions FS-A7 to FS-A9 in `FS_QA.md`.

**Specification (user's choices).** Macro equations (unemployment gap, core PCE) are rows of a monthly VAR: L monthly lags of both macro variables and L monthly lags of the MONTHLY AVERAGE of the daily policy rate and daily index (equal weights within the month, a free coefficient per month), OLS; L = 6 and 12. Daily block: HAR for policy rate and index. Within-month ordering:
- BASE: macro first. Macro equations use lagged financial averages only; the daily block includes this month's and last month's macro values (markets respond to macro conditions within the month). In the event month macro has not moved, so nothing macro enters the window or the event day.
- +CUR (robustness): financial first. Macro equations add the current-month financial average; the daily block has last month's macro only (both directions in the same month would not be identified by timing).
Window impact vector b from 30-minute changes, macro entries zero, no credit spread. MODEL = daily dynamics after the event day; PATH = direct event-day path through the end of month t+1, then the model.

**Results: unemployment gap (pp) at 12 months [90%], and 36 months, per +1 pp on the 2-year (NS, NS-GB) or funds rate (MP1)** [verified]

| Sample | Lags | Shock | BASE MODEL 12m | 36m | BASE PATH 12m | +CUR MODEL 12m |
|---|---|---|---|---|---|---|
| 1977-, 2-year | 6 | NS | +0.17 [+0.07,+0.29] | +0.11 | +0.24 [-0.05,+0.66] | +0.06 [-0.03,+0.17] |
| | 6 | NS-GB | +0.16 [+0.06,+0.30] | +0.10 | +0.49 [-0.03,+1.22] | +0.05 |
| | 12 | NS | +0.18 [+0.06,+0.29] | +0.11 | +0.27 [-0.07,+0.73] | +0.08 [-0.03,+0.21] |
| | 12 | NS-GB | +0.17 [+0.06,+0.31] | +0.11 | +0.62 [-0.11,+1.46] | +0.07 |
| 1994-, 2-year | 6 | NS | +0.20 [+0.05,+0.40] | +0.47 [+0.23,+0.77] | +0.29 [-0.19,+0.81] | +0.24 [+0.03,+0.41] |
| | 6 | NS-GB | +0.19 [+0.02,+0.36] | +0.46 | +0.66 [-0.18,+1.52] | +0.23 |
| | 12 | NS | +0.20 [+0.04,+0.37] | +0.39 [+0.12,+0.68] | +0.31 [-0.24,+0.96] | +0.25 [+0.10,+0.43] |
| | 12 | NS-GB | +0.18 [+0.02,+0.34] | +0.38 | +0.78 [-0.15,+1.98] | +0.23 |
| 1974-, funds rate | 6 | NS | +0.28 [+0.21,+0.40] | +0.13 | +0.32 [-0.06,+0.71] | +0.20 [+0.10,+0.28] |
| | 6 | NS-GB | +0.27 [+0.17,+0.39] | +0.12 | +0.48 [-0.11,+1.09] | +0.19 |
| | 6 | MP1 | +0.07 [-0.00,+0.14] | +0.04 | +0.03 [-0.42,+0.55] | +0.03 |
| | 12 | NS | +0.38 [+0.29,+0.47] | +0.22 | +0.49 [+0.07,+0.94] | +0.31 [+0.22,+0.41] |
| | 12 | NS-GB | +0.36 [+0.26,+0.47] | +0.21 | +0.70 [+0.14,+1.40] | +0.29 |
| | 12 | MP1 | +0.11 [+0.03,+0.19] | +0.06 | +0.17 [-0.39,+1.00] | +0.07 |

Core PCE at 12 months: BASE MODEL between -0.16 and +0.10, every 90% interval includes zero; no inflation result.

**Reading** [inference unless marked]
1. With equal within-month weights the estimates are stable and precise. In the base case (MODEL) a tightening that raises the 2-year 1 pp raises the unemployment gap about 0.2 pp after a year, with 90% intervals excluding zero in every NS and NS-GB case. In the long samples the effect peaks in year 1-2 and fades; in 1994+ it keeps building to about 0.4-0.5 pp at three years. Funds-rate scaling gives 0.3-0.4 pp per 1 pp on the funds rate for NS; MP1 is smaller (0.07-0.11), as before.
2. The restriction fixed the unrestricted MIDAS problem [verified]: the long-sample funds-rate response went from +0.02 (weights at bounds) to +0.28/+0.38, and the long 2-year sample from +0.10 to +0.17.
3. Ordering within the month: putting macro first (BASE) barely changes the results compared with lagged-only feedback [verified: e.g. 1994+, 6 lags, u36 +0.44 -> +0.47; long 12 lags u36 +0.08 -> +0.11]. Financial first (+CUR) matters in the long 2-year sample (12m falls to +0.06-0.08, interval includes zero) but not in 1994+ (+0.23-0.25) or with the funds rate (+0.19-0.31). So the long-sample 2-year result depends on whether the current month's financial average is allowed into the unemployment equation; the 1994+ result does not.
4. PATH (direct event-day path through month t+1) gives larger centres but wide intervals that include zero at 12 months in most cases. NS-GB PATH is much larger than NS PATH, because the event-day local projections for the Greenbook-purged events show more build-up in financial conditions after the announcement; these paths are noisy.
5. 6 vs 12 lags: same at 12 months; 12 lags gives less persistence at 36 months in 1994+ and more in the funds-rate sample.

**Literature** (`LITERATURE_MIDAS.md`): no paper found with this combination. Closest: Francis, Ghysels and Owyang (2011, MIDAS, direct regression, small real effects); Gazzani and Vicondoa (2020, daily-VAR shocks as monthly proxy); Chudik and Georgiadis (2022) and Chudik and Kilian (2026, direct mixed-frequency distributed lags; extension to sparse FOMC-type shocks left to future research); Kilian (2024, monthly-average accounting of a day-d surprise, the same as our event-timing exposure).

---

# Appendix: the comparison write-up as of 1 Nov 2026 (moved here from MF_REPORT.md when the note was refocused on the core cases, FS-A17)

## Window-identified MIDAS-VAR: monetary-policy effects on unemployment and inflation, compared with Bauer-Swanson and others (1 Nov 2026)

Tags: [verified] = computed here or read in the source; [read from figure] = read off a published chart, approximate; [inference] = my reading; [secondhand] = not checked in full text. Decisions: `FS_QA.md` (FS-A7 to FS-A10). Development history (stage 0, routes A and B, unrestricted MIDAS, all earlier tables): `MF_DEVELOPMENT.md`. Literature notes: `LITERATURE_MIDAS.md`.

### 1. Summary
0. **Core cases (section 2a, FS-A16):** without the FCI no rate form gives a conventional, significant unemployment or price response (IP rises); adding the FCI makes unemployment conventional and mostly significant; netting r\* (and expected inflation) out of the rate, with the FCI, makes unemployment significant at 12-36 months for every lag length, the price level significant with 6 and 12 lags, and IP fall. Best case vs Bauer-Swanson: unemployment +0.33 vs +0.19 at 12 months, price level -0.5 vs -0.5 at 24 months, IP -0.9 vs -1.5 at 12 months.
1. **Base case** (1994+, 2-year scaling, Nakamura-Steinsson (NS) shock, MODEL, 3/6/12 monthly lags): a policy move that raises the 2-year yield 1 pp in the FOMC window raises the unemployment gap by **+0.16 to +0.21 pp at 10 months** and **+0.39 to +0.52 pp at 36 months**; every 90% interval excludes zero at 10, 24 and 36 months (one exception: NS-GB, 6 lags, at 10 months). The **core PCE price level falls by 0.24 to 0.44% at 24 months and 0.38 to 0.67% at 36 months**; with 12 lags the fall is significant at 12, 24 and 36 months, with 3 and 6 lags the interval includes zero. [verified]
2. **Bauer-Swanson's (2023) benchmark** gives almost the same numbers per 1 pp on the 2-year: unemployment about +0.22 pp at 10 months, CPI about -0.5% at 24 months and -0.8% at 50 months [read from figure]. Our unemployment response is more persistent (it keeps rising to 36 months; theirs fades after about 10 months).
3. We reach this **without a first stage** (the window move is the impact) and **without orthogonalizing the surprise**, which are the two problems Bauer-Swanson and Caldara-Herbst work hardest on. The price is an **exclusion restriction: the shock reaches unemployment and inflation only through the policy rate and the market index.**
4. A **direct regression** that does not impose that restriction (Chudik-Georgiadis / Chudik-Kilian) gives the wrong sign (unemployment falls after a hawkish surprise), driven by the 2007-09 events, and is about ten times less precise: it neither confirms nor rejects our estimate.
5. **Bauer-Swanson's other variables (section 6a):** adding IP leaves unemployment and prices unchanged, but IP does not fall as in Bauer-Swanson; adding commodity prices (IMF monthly index) gives rising commodity prices and IP (puzzles), which points to a weakness of the propagation assumption for demand-sensitive variables.
6. **Robustness:** Greenbook-purged shock (NS-GB) gives the same results; adding the current month's financial average gives the same or slightly larger; PATH gives larger and much noisier responses; the long samples give smaller, less persistent unemployment responses and a price response that depends on the lag length.

### 2. Identification and assumptions
- **Shock and impact.** NS policy-news factor (USMPD, 253 FOMC events, 1994-2026). Its impact is the 30-minute window change of the variables observed in the window: 2-year yield (scaled to +1 pp) and the market index (+0.99 per 1 pp on the 2-year). Macro variables are zero in the window. No credit spread in the impact vector (no intraday series).
- **Propagation.** A daily block (2-year yield, index; HAR form with 1-, 5-, 22- and 66-day averages; it also responds to this month's and last month's unemployment gap and core inflation) carries financial conditions forward from the event day. Monthly macro equations are rows of a monthly VAR in the unemployment gap and core PCE inflation with L lags of each and L lags of the **monthly averages** of the daily 2-year yield and index (equal weights within the month, one free coefficient per monthly lag; OLS).
- **Within-month timing.** Macro is set first in each month (from lags); markets then respond to it within the month; in the event month macro has not moved, so nothing macro enters the window or the event day. The event's position in the month comes from the empirical distribution of FOMC dates, so the event month gets only the post-announcement days (Kilian's (2024) monthly-average accounting holds by construction).
- **What identifies the macro response.** (a) The window impact (identified by timing in the 30-minute window); (b) the **exclusion restriction**: no channel from the announcement to macro other than the policy rate and the index; (c) the effect of financial conditions on macro is estimated from **all** month-to-month variation in the lagged monthly averages, so it assumes the economy responds to a given move in financial conditions the same way whatever moved them [inference: this is the assumption a reader will question most].
- **Uncertainty.** 200 draws: events resampled (window impact and event positions) and residual bootstrap of the macro equations. Daily-block coefficients held fixed.

### 2a. Core cases: does the FCI help, and do the r\* adjustments help? (FS-A16; `midas_core.py`; `midas_core.log`, `midas_core{,_irf}.csv`) [verified]
All with the NS surprise, 1994+, MODEL, BASE ordering, 200 draws; per +1 pp window move in the 2-year. Six core cases: the 2-year in three forms (nominal; minus Laubach-Williams r\*; minus 1-year expected inflation and r\*), each **without** the FCI (the daily block is the rate alone; the window impact is the 2-year move alone) and **with** the market index in the matching form (nominal index; nominal index plus the note's r\* adjustment, since the note has no "nominal minus r\*" index; r\*-gap index). The same six with IP added are robustness. \* = 90% interval excludes zero. Bauer-Swanson: benchmark Fig. 8, per 1 pp on the 2-year, read from the figure (approximate; their 90% bands are standard bootstrap bands).

**Unemployment gap (pp), monthly block [u,pi]** (cells: 3 / 6 / 12 lags)

| Rate | FCI | 12 m | 24 m | 36 m |
|---|---|---|---|---|
| 2-year nominal | no | -0.13 / -0.27* / -0.34* | -0.01 / -0.19 / -0.36* | +0.08 / -0.08 / -0.25 |
| 2-year nominal | yes | +0.18* / +0.09 / +0.07 | +0.38* / +0.29* / +0.19 | +0.42* / +0.37* / +0.24* |
| 2-year - r* | no | -0.02 / -0.10 / -0.17 | +0.10 / -0.05 / -0.25 | +0.17 / +0.01 / -0.21 |
| 2-year - r* | yes | +0.31* / +0.29* / +0.32* | +0.49* / +0.46* / +0.41* | +0.49* / +0.49* / +0.40* |
| 2-year - exp. infl. - r* | no | +0.11 / +0.06 / -0.07 | +0.19 / +0.04 / -0.13 | +0.22 / +0.03 / -0.15 |
| 2-year - exp. infl. - r* | yes | +0.32* / +0.33* / +0.33* | +0.38* / +0.37* / +0.40* | +0.32* / +0.33* / +0.36* |
| Bauer-Swanson benchmark [read from figure] | | +0.19* | +0.17 | +0.15 |

**Core PCE price level (%), monthly block [u,pi]** (cells: 3 / 6 / 12 lags)

| Rate | FCI | 12 m | 24 m | 36 m |
|---|---|---|---|---|
| 2-year nominal | no | +0.01 / +0.06 / +0.01 | -0.08 / +0.03 / +0.05 | -0.17 / -0.07 / +0.03 |
| 2-year nominal | yes | -0.09 / -0.07 / -0.10 | -0.28 / -0.24 / -0.23 | -0.42 / -0.41 / -0.36 |
| 2-year - r* | no | -0.05 / -0.04 / -0.08 | -0.15 / -0.15 / -0.14 | -0.24 / -0.28 / -0.22 |
| 2-year - r* | yes | -0.12 / -0.18 / -0.24* | -0.26 / -0.42 / -0.52* | -0.39 / -0.62 / -0.77* |
| 2-year - exp. infl. - r* | no | -0.18* / -0.12 / -0.16 | -0.29 / -0.26 / -0.27 | -0.36 / -0.39 / -0.38 |
| 2-year - exp. infl. - r* | yes | -0.22* / -0.25* / -0.30* | -0.36 / -0.50* / -0.56* | -0.47 / -0.70* / -0.74* |
| Bauer-Swanson benchmark [read from figure] | | -0.36* | -0.48* | -0.6* |

**Unemployment gap (pp), monthly block [u,pi,ip]** (cells: 3 / 6 / 12 lags)

| Rate | FCI | 12 m | 24 m | 36 m |
|---|---|---|---|---|
| 2-year nominal | no | -0.01 / -0.06 / -0.20 | +0.21 / +0.16 / -0.08 | +0.34 / +0.34 / +0.16 |
| 2-year nominal | yes | +0.41* / +0.36* / +0.25* | +0.63* / +0.62* / +0.52* | +0.57* / +0.61* / +0.57* |
| 2-year - r* | no | +0.06 / +0.02 / -0.09 | +0.23 / +0.16 / -0.08 | +0.32 / +0.23 / +0.05 |
| 2-year - r* | yes | +0.30* / +0.33* / +0.33* | +0.45* / +0.47* / +0.43* | +0.43* / +0.48* / +0.44 |
| 2-year - exp. infl. - r* | no | +0.13 / +0.11 / -0.03 | +0.23 / +0.12 / -0.03 | +0.27 / +0.10 / +0.03 |
| 2-year - exp. infl. - r* | yes | +0.30* / +0.36* / +0.33* | +0.35* / +0.38* / +0.41* | +0.30* / +0.35* / +0.38* |
| Bauer-Swanson benchmark [read from figure] | | +0.19* | +0.17 | +0.15 |

**Core PCE price level (%), monthly block [u,pi,ip]** (cells: 3 / 6 / 12 lags)

| Rate | FCI | 12 m | 24 m | 36 m |
|---|---|---|---|---|
| 2-year nominal | no | +0.01 / +0.03 / +0.06 | -0.10 / -0.09 / +0.12 | -0.21 / -0.26 / +0.11 |
| 2-year nominal | yes | -0.13 / -0.15 / -0.15 | -0.34 / -0.43 / -0.30 | -0.45 / -0.63 / -0.44 |
| 2-year - r* | no | -0.04 / -0.07 / -0.11 | -0.13 / -0.25 / -0.21 | -0.21 / -0.46 / -0.36 |
| 2-year - r* | yes | -0.10 / -0.22 / -0.33* | -0.22 / -0.50* / -0.67* | -0.31 / -0.75* / -0.97* |
| 2-year - exp. infl. - r* | no | -0.16 / -0.13 / -0.16 | -0.26 / -0.31 / -0.26 | -0.33 / -0.47 / -0.39 |
| 2-year - exp. infl. - r* | yes | -0.21* / -0.26* / -0.32* | -0.35 / -0.54* / -0.56* | -0.44 / -0.76* / -0.73* |
| Bauer-Swanson benchmark [read from figure] | | -0.36* | -0.48* | -0.6* |

**Industrial production (%), monthly block [u,pi,ip]** (cells: 3 / 6 / 12 lags)

| Rate | FCI | 12 m | 24 m | 36 m |
|---|---|---|---|---|
| 2-year nominal | no | +1.15* / +1.15* / +1.64* | +1.05 / +1.10 / +1.63* | +1.01 / +1.04 / +1.23 |
| 2-year nominal | yes | -0.17 / -0.36 / -0.08 | -0.10 / -0.14 / -0.09 | +0.50 / +0.35 / +0.27 |
| 2-year - r* | no | +0.61 / +0.61 / +1.01 | +0.51 / +0.78 / +1.31 | +0.50 / +0.89 / +1.01 |
| 2-year - r* | yes | -0.37 / -0.74 / -0.64 | -0.22 / -0.33 / -0.44 | +0.25 / +0.06 / -0.18 |
| 2-year - exp. infl. - r* | no | +0.16 / +0.13 / +0.41 | +0.22 / +0.62 / +0.80 | +0.30 / +0.88 / +0.72 |
| 2-year - exp. infl. - r* | yes | -0.45 / -0.87* / -0.89* | -0.04 / -0.24 / -0.46 | +0.41 / +0.15 / -0.08 |
| Bauer-Swanson benchmark [read from figure] | | -1.5* | -1.0* | -0.85* |

**Summary [verified for the numbers; inference for the reading].**
1. **Without the FCI nothing works.** With the 2-year alone, in any form, the unemployment response is never significantly positive (it is significantly *negative* with the nominal 2-year and 6 or 12 lags), the price level is never significant except once, and IP *rises* (significantly with the nominal rate). This is the familiar wrong-sign result of the post-1994 literature (Ramey 2016; Bauer-Swanson's unadjusted surprises; this project's Cholesky and local projections).
2. **Adding the FCI turns every unemployment response conventional and mostly significant.** With the nominal rate and FCI: +0.07 to +0.18 at 12 months (significant with 3 lags), +0.24 to +0.42 at 36 months (all significant). The daily, window-identified propagation through the index is what delivers a sensible transmission.
3. **The r\* adjustments make it robust and precise.** With the FCI and the rate net of r\* (with or without expected inflation), unemployment is significant at 12, 24 and 36 months for every lag length (+0.29 to +0.33 at 12 months; one exception at 36 months with IP and 12 lags), and nearly identical across 3, 6 and 12 lags; the price level becomes significant (with 6 and 12 lags at 24 and 36 months; at 12 months for all lags when expected inflation is also removed); and IP falls (significantly at 12 months with 6 and 12 lags in the full r - r\* case). Removing r\* without the FCI does not help: both ingredients are needed.
4. **Relative to Bauer-Swanson.** Best cases (FCI, rate net of expected inflation and r\*): unemployment +0.32 to +0.33 at 12 months against their +0.19, and +0.32 to +0.40 at 36 months against +0.15 (their band includes zero after about 18-20 months; ours excludes it); price level -0.22 to -0.30 at 12 months, -0.36 to -0.56 at 24, -0.47 to -0.74 at 36 against their -0.36, -0.48, -0.6: the same size, and significant with 6 and 12 lags; IP -0.45 to -0.89 at 12 months against -1.5, with a faster recovery. So: same sign and magnitude for prices, larger and more persistent for unemployment, smaller for IP; and obtained from FOMC windows only, without an orthogonalized instrument or Chair speeches.
5. **The earlier "base case"** (section 3: nominal 2-year with the r\*-gap index) mixes the forms; it sits between the nominal-with-FCI and r\*-with-FCI rows.
6. **Interpretation [inference].** Two things carry the identification. (a) The FCI: the window measures how far financial conditions as a whole move with policy, and the daily block carries that forward; a policy rate alone in a reduced-form link to unemployment picks up the procyclical co-movement of rates and activity (rates rise in booms), which the FCI's equity and dollar components partly offset. (b) The r\* adjustment: it removes the slow secular decline of rates since 1994 (and of expected inflation), which otherwise lines up against trending real activity. Neither appears in the high-frequency-identification literature I have read (Gertler-Karadi, Nakamura-Steinsson, Caldara-Herbst, Miranda-Agrippino-Ricco, Bauer-Swanson, Jarocinski-Karadi): their VARs use the nominal 1- or 2-year rate, and the closest idea is Caldara-Herbst's credit spread [inference, based on the papers read here, not a systematic search].
7. **Caveats.** The improvement could partly reflect that the r\*-adjusted and FCI systems fit the 1994-2026 sample better by construction (r\* and the index's weights are themselves estimated); the window impact for the FCI uses the same NS events that set the index weights; bands do not include uncertainty in the daily block or in r\*. The propagation assumption (macro responds to financial conditions the same way whatever moved them) is still the identifying assumption.

### 3. Base case (nominal 2-year with the r*-gap index; superseded as the base by section 2a, pending the user's choice): 1994+, 2-year, NS, MODEL (`midas_step.py 200 ALL 1994 3,6,12`; `midas_step_1994.log`, `midas_step_1994_L3-6-12{,_irf}.csv`) [verified]
Per +1 pp window move in the 2-year yield. Unemployment gap in pp; core PCE price level in % (monthly annualized rate cumulated, /12). Median-path point estimate [90% interval].

| Lags | u, 10 m | u, 24 m | u, 36 m | Price level, 12 m | 24 m | 36 m |
|---|---|---|---|---|---|---|
| 3 | +0.21 [+0.07, +0.34] | +0.48 [+0.26, +0.71] | +0.52 [+0.29, +0.78] | -0.08 [-0.30, +0.11] | -0.24 [-0.60, +0.15] | -0.38 [-0.90, +0.14] |
| 6 | +0.16 [+0.02, +0.32] | +0.40 [+0.17, +0.66] | +0.47 [+0.21, +0.76] | -0.13 [-0.31, +0.06] | -0.34 [-0.79, +0.12] | -0.53 [-1.24, +0.15] |
| 12 | +0.20 [+0.02, +0.32] | +0.34 [+0.08, +0.52] | +0.39 [+0.06, +0.59] | -0.20 [-0.38, -0.03] | -0.44 [-0.76, -0.05] | -0.67 [-1.18, -0.02] |

Reading [inference]: the unemployment response is robust to the lag length (12-month values +0.26, +0.20, +0.20); more lags make it a little less persistent and the price response larger and more precise. No price puzzle in any version. The earlier statement "no inflation result" (based on the 12-month inflation **rate**) was too strong: the right comparison with the literature is the price level, and with 12 lags its fall is significant.

### 4. Robustness [verified unless marked]
**4.1 PATH instead of MODEL.** PATH replaces the model's daily path of the 2-year and the index, from the event day to the end of the month after the event, by the path estimated directly by event-day local projections; the model takes over after that. 1994+, NS, u at 12 months: +0.36 [+0.01, +0.74] (3 lags), +0.29 [-0.15, +0.78] (6), +0.31 [-0.23, +0.91] (12); price level at 24 months -0.30, -0.44, -0.58, intervals include zero except with 12 lags.
- *Why PATH could be better:* it uses the data, not the HAR model, for the first one to two months, where the HAR gives a flat index (about 1.0 per unit) while the data show further tightening (about 1.3, noisy). If the daily model misses post-announcement drift, PATH captures it.
- *Why it could be worse:* the local projections pick up everything else that happens in the 21-42 trading days after each announcement (data releases, other news). With about 250 events this is noise but also possible contamination if later news is correlated with the surprise; and any information effect that shows up as drift is carried into the macro response.
- *Why it is noisier:* the variance of a cumulated daily change grows with the number of days, and the month-(t+1) average puts full weight on the noisiest days; the NS-GB event set is smaller (205 events). Hence intervals two to five times wider than MODEL.

**4.2 Greenbook-purged shock (NS-GB).** MODEL nearly identical to NS (1994+: u 12 m +0.25, +0.19, +0.18 for 3/6/12 lags; price level 24 m -0.23, -0.33, -0.43). PATH with NS-GB is much larger (+0.64 to +0.78 at 12 m) and very noisy.

**4.3 Current-month financial average in the macro equations (+CUR; financial first within the month).** 1994+, NS, MODEL u 12 m: +0.31, +0.24, +0.25 (3/6/12 lags); price level 24 m -0.28, -0.46, -0.61 (12 lags: interval excludes zero).

**4.4 Long samples (BASE, MODEL, 6 and 12 lags; `midas_step_long.log`, `midas_step_BASE_long_L6-12{,_irf}.csv`).** The window impact still comes from the 1994+ events; only the macro equations and the daily block use the long sample (index interpolated monthly before 1990).

| Sample, scaling, shock | Lags | u, 10 m | u, 24 m | u, 36 m | Price level, 24 m |
|---|---|---|---|---|---|
| 1977+, 2-year, NS | 6 | +0.16 [+0.07, +0.28] | +0.15 | +0.11 [-0.01, +0.20] | +0.12 [-0.12, +0.40] |
| | 12 | +0.19 [+0.08, +0.29] | +0.16 | +0.11 [-0.01, +0.22] | -0.18 [-0.48, +0.07] |
| 1974+, funds rate, NS | 6 | +0.28 [+0.19, +0.39] | +0.21 | +0.13 | -0.14 [-0.40, +0.14] |
| | 12 | +0.35 [+0.26, +0.43] | +0.34 | +0.22 | -0.31 [-0.62, -0.02] |
| 1974+, funds rate, MP1 | 12 | +0.10 [+0.02, +0.17] | +0.10 | +0.06 | +0.03 [-0.15, +0.17] |

The long samples agree on the first year and give less persistence; the 2-year long-sample response falls to +0.06-0.08 at 12 months under +CUR (`MF_DEVELOPMENT.md` section 7). Why 1994+ is the base: the shock is only measured from 1994, and Kilian (2024) recommends estimating on the period where the surprises exist; the long samples mix in pre-1994 macro dynamics and a pre-1990 interpolated index.

### 5. Direct regressions that drop the exclusion restriction (`direct_mfdl.py`; `direct_mfdl.log/.csv`, `direct_ardl.log/.csv`) [verified]
**Chudik-Georgiadis (2022) restricted mixed-frequency distributed lag.** Monthly outcome regressed directly on the event-day shocks, each placed by its day in the month, with a daily response that is piecewise linear between knots at 0, 1, 2, 3, 6, 9, 12, 18, 24, 30, 36 months. Unemployment in levels and in first differences; core PCE price level in differences. Same units (per +1 pp window 2-year). Because the usual HAC bands proved far too narrow, inference is by **permutation** (shock values reshuffled across the same event dates, 500 times).

| Shock, outcome | 12 m estimate | permutation null 90% at 12 m | p |
|---|---|---|---|
| NS, u levels | -2.32 | [-3.74, +3.12] | 0.28 |
| NS, u differences | -2.05 | [-1.82, +1.69] | 0.06 |
| NS-GB, u levels | -1.11 | [-5.57, +4.64] | 0.70 |
| MP1 (funds rate), u differences | -1.69 | [-1.78, +1.36] | 0.07 |
| NS, price level | +0.32 | [-1.18, +1.33] | 0.68 |
| NS, 2007-08..2009-06 events dropped, u levels | -0.65 | [-2.59, +3.69] | 0.79 |

**Chudik-Kilian (2026) pooled ARDL** (12 own lags, shock lags 0-36, pooled monthly regressor = sum of the month's shocks, i.e. a shock on a random day of the month; permutation inference as above), 12-month responses:

| Shock | u gap (p) | Price level (p) |
|---|---|---|
| NS | -1.88 (0.11) | +0.40 (0.53) |
| NS-GB | -1.19 (0.44) | +1.22 (0.15) |
| MP1 | -1.94 (0.05) | +0.90 (0.09) |
| NS, crisis events dropped | -0.69 (0.41) | +0.44 (0.43) |
| MP1, crisis events dropped | -0.81 (0.33) | +0.68 (0.28) |

Adding own lags (their recommendation) tightens the null band only modestly (NS: ±1.9 pp at 12 months instead of ±3.4 in levels) and the picture is the same: wrong signs for unemployment and prices (a price puzzle), significant only for MP1 at the 10% level, and much weaker without the 2007-09 events.

Reading [inference]: without the exclusion restriction the point estimates have the wrong sign, as in the project's earlier local projections (`mp_var_fci`, `lp_weights`) and as Bauer-Swanson find with unadjusted surprises; the wrong sign comes mostly from the 2007-09 events (dovish surprises followed by rising unemployment). The direct estimates are about ten times less precise than ours: the null band at 12 months is about ±2 to ±4 pp against our ±0.15. Our +0.2 lies inside every direct interval except the full-sample NS first-difference version, where it is just outside. So the direct regression cannot test our estimate; all the precision of the MIDAS-VAR comes from the exclusion restriction.

### 6. Comparison with the literature
Units converted to "per +1 pp" on each paper's own scaling variable. Bauer-Swanson and Caldara-Herbst values read from text unless marked [read from figure].

| Study | Identification | Sample | Unemployment | Prices | Precision |
|---|---|---|---|---|---|
| **This note, base** | window impact + exclusion through 2-year and index; MIDAS-VAR | 1994-2026 | +0.16 to +0.21 pp (10 m); +0.39 to +0.52 (36 m) | core PCE level -0.24 to -0.44% (24 m), -0.38 to -0.67% (36 m) | u: 90% excludes 0; prices: excludes 0 with 12 lags |
| **Bauer-Swanson (2023), benchmark (Fig. 8)** | proxy-SVAR; FOMC + Chair-speech surprises orthogonalized to pre-announcement news; per 2-year | VAR 1973-2020, instrument 1988-2019 | about +0.22 pp peak at 10 m, about +0.17 (24 m), +0.15 (36 m) [read from figure] | CPI about -0.2% (impact), -0.5% (24 m), -0.6% (36 m), -0.8% (50 m) [read from figure] | 90% bootstrap bands: u excludes 0 from about month 3 to about 18-20; CPI excludes 0 throughout, narrowly in months 5-12 [read from figure] |
| Bauer-Swanson, unadjusted surprises (Fig. 3 left) | same, raw surprises | same | (not in that system) | CPI about -0.4% (24 m); IP trough -1.4% per 1 pp | responses about a quarter of the orthogonalized ones |
| Bauer-Swanson, orthogonalized (Fig. 3 right) | same, FOMC only | same | (not in that system) | CPI about -3% (24 m), IP trough -5.6% per 1 pp [read from figure] | 2-year yield turns negative after about 7 months, so per-impact scaling overstates; FOMC-only orthogonalized F = 2.44 |
| **Caldara-Herbst (2019)** | Bayesian proxy-SVAR; current-month futures surprise; funds rate, IP, excess bond premium | 1993-2007 | not reported | no price response (prices dropped from the baseline for that reason) | IP about -4% per 1 pp funds rate at 2.5 years (-0.75% for an 18 bp shock); without credit spreads, no IP response |
| **Nakamura-Steinsson (2018)** | 30-min window, policy-news factor; event study | 1995-2014 | no macro VAR; Blue Chip expected growth **rises** +1.0 per unit after a tightening (information effect) | breakeven inflation barely moves | real rates move one for one for years |
| Francis-Ghysels-Owyang (2011) | FOMC-day innovation in the daily funds rate; MIDAS direct regressions | 1960-2009 | insignificant; OLS gives the wrong sign | core inflation falls significantly only after about 21 months | wide |
| This project's earlier work (`mp_var_fci`) | Cholesky and proxy-SVAR on monthly data | 1994-2026 | Cholesky: wrong sign (-0.4 per 1 pp 2-year); proxy-SVAR: F 2-6, Anderson-Rubin sets unbounded | | |

Comparisons for our funds-rate and MP1 cases (robustness only): NS scaled to the funds rate gives +0.28 to +0.35 pp at 10 months per 1 pp funds rate; MP1 gives +0.07 to +0.10. A rough conversion of Caldara-Herbst's industrial-production effect to unemployment (IP moves about three times GDP, Okun coefficient 2) gives about +0.7 pp per 1 pp [inference, rough]: larger than any of our funds-rate cases.

**Reading [inference].**
1. **Unemployment.** Our base case matches Bauer-Swanson's best-practice estimate in the first year almost exactly (+0.2 pp per 1 pp on the 2-year at 10 months) and is more persistent afterwards (+0.4 to +0.5 at 36 months against their +0.15). Theirs is identified from 30 years of surprises with a full VAR and an orthogonalized instrument; ours from the window impact plus an exclusion restriction. Two quite different routes give the same first-year number.
2. **Prices.** Our price-level decline (about -0.4% at 24 months with 12 lags) is close to Bauer-Swanson's benchmark (-0.5%) and to their unadjusted-surprise version (-0.4%), far below their FOMC-only orthogonalized version (-3%, an outlier driven by the policy reversal). Like them, we find no price puzzle; unlike Caldara-Herbst, we find a (slow) price decline.
3. **Persistence.** Our unemployment response keeps building because the 2-year and index stay elevated in the daily block (HAR) and the monthly macro equations are persistent; Bauer-Swanson's 2-year yield response decays within about two years in Fig. 8.

### 6a. Adding Bauer-Swanson's monthly variables: industrial production and commodity prices (`midas_bs.py`; `midas_bs_BS{1,2,3}.log/.csv`, `_irf.csv`) [verified]
Same design as the base case (1994+, 2-year, NS base / NS-GB robustness, BASE ordering, 200 draws), with more monthly variables in the macro block, each treated like unemployment and inflation (rows of the monthly VAR, lagged monthly averages of the daily 2-year and index, macro set first within the month and feeding the daily block). IP = 100 log INDPRO; commodity prices = 100 log IMF all-commodity index (FRED `PALLFNFINDEXM`, 1992+; Bauer-Swanson use the CRB index, not on FRED). Commodity prices enter as the monthly IMF index (user decision FS-A12); a daily oil case was tried and dropped (no free broad daily commodity index was reachable; daily WTI drifted up through a levels artifact; files `midas_bs_BS3.*` kept for the record). Per +1 pp window move in the 2-year, MODEL, NS:

| Case | Lags | u, 10 m | u, 36 m | Price level, 24 m | IP, 10 m | IP, 24 m | Commodity index, 24 m |
|---|---|---|---|---|---|---|---|
| Base (u, core PCE) | 3 / 6 / 12 | +0.21 / +0.16 / +0.20 | +0.52 / +0.47 / +0.39 | -0.24 / -0.34 / -0.44* | | | |
| Alt 1: + IP | 3 | +0.24* | +0.53* | -0.22 | +0.02 | +0.08 | |
| | 6 | +0.25* | +0.55* | -0.42* | -0.34 | +0.06 | |
| | 12 | +0.26* | +0.52* | -0.46 | -0.34 | -0.14 | |
| Alt 2: + IP + commodity index | 3 | +0.23* | +0.42* | -0.49* | +0.47 | +0.79 | +3.3 |
| | 6 | +0.15 | +0.43* | -0.46 | +0.42 | +1.18* | +5.6 |
| | 12 | +0.14 | +0.33 | -0.12 | +0.47 | +1.59* | +9.1 |
| Bauer-Swanson benchmark | | about +0.22 (peak) | about +0.15 | CPI about -0.5 | about -1.6 | about -1.0 | commodities about -4 on impact, -6 at the trough (6-8 m), about -2.6 at 24 m [read from figure] |

\* = 90% interval excludes zero. Intervals and the NS-GB, PATH and 24-month unemployment results are in the logs; NS-GB MODEL is within 0.03 of NS throughout; PATH widens everything.

Reading [inference unless marked]:
1. **Adding IP (alternative 1) leaves unemployment and prices as in the base case** (unemployment slightly larger, +0.24 to +0.26 at 10 months, all significant; price level -0.22 to -0.46 at 24 months, significant with 6 lags). **But IP itself does not fall**: about -0.3% at 10 months with 6 or 12 lags, intervals include zero, turning positive later. Bauer-Swanson's IP falls about 1.6% per 1 pp at 10 months [read from figure]. So on IP we do not match them.
2. **Adding commodity prices (alternative 2) produces puzzles**: commodity prices rise (+3 to +9% at 24 months, mostly insignificant) and IP rises significantly at 24 months with 6 and 12 lags (+1.2 to +1.6%); unemployment weakens (12 lags: +0.14 at 10 months, interval includes zero) and the price fall shrinks with 12 lags. Bauer-Swanson find commodity prices fall about 1% per 25 bp within months.
3. **What this says about the identifying assumption.** The propagation is estimated from the reduced-form link between lagged financial conditions and each monthly variable, over all sources of variation (assumption (c) in section 2). For unemployment and core prices that link has the conventional sign. For IP and commodity prices it is procyclical in 1994-2026: rates and the index rise in expansions, and IP and commodity prices rise with them (2004-06 and 2021-22 are the obvious episodes). The window impact cannot correct this, because the macro side is not identified by the shock. So the commodity and IP results are evidence that assumption (c) fails for demand-sensitive, forward-looking variables, and a warning for the unemployment result too: it may hold for unemployment only because unemployment lags. Bauer-Swanson identify the whole VAR's response to the shock, so they do not need this assumption.
4. Proposal (for decision): keep the unemployment / core-PCE system as the base; report alternative 1 as the closest like-for-like with Bauer-Swanson, with IP flagged as not matching; report alternative 2 (IMF commodity index) as a diagnostic of assumption (c).

**Quadratic time trend (FS-A13; `midas_bs.py 200 <case> 3,6,12 trend`; `midas_bs_BS{0,1,2}_trend.log/.csv`).** A trend in t and t² is added to every monthly equation (it shifts the levels but does not enter the impulse responses directly; it changes the estimated lag coefficients). MODEL, NS, 3 / 6 / 12 lags [verified]:

| Case, with trend | u, 10 m | u, 36 m | Price level, 24 m | IP, 10 m | IP, 24 m | Commodity index, 24 m |
|---|---|---|---|---|---|---|
| Base (u, core PCE) | +0.32* / +0.24* / +0.28* | +0.52* / +0.57* / +0.60* | -0.32* / -0.50* / -0.52* | | | |
| + IP | +0.34* / +0.28* / +0.27* | +0.50* / +0.52* / +0.53* | -0.40* / -0.54* / -0.56* | -0.22 / -0.40 / -0.33 | -0.10 / -0.02 / -0.31 | |
| + IP + IMF commodity index | +0.23* / +0.15 / +0.14 | +0.28* / +0.34* / +0.36* | -0.38* / -0.43* / -0.20 | +0.46 / +0.45 / +0.52 | +1.05* / +1.22* / +1.35* | +5.3 / +6.1 / +7.6 |

\* = 90% interval excludes zero. NS-GB within 0.04 of NS.

Reading [inference]: the trend makes the base-case and IP-case responses **larger and more precise** (unemployment about +0.25 to +0.35 pp at 10 months and +0.5 to +0.6 at 36; the price-level fall at 24 months now significant for every lag length, -0.32 to -0.56%). It does **not** fix IP: IP still falls only 0.2-0.4% at 10 months with intervals including zero (Bauer-Swanson about -1.6%). With commodity prices the puzzles remain (IP rises significantly at 24 months, commodity prices rise). So the IP and commodity problems are not a trend artifact; they point to the procyclical reduced-form link (item 3 above).

**2-year as r - r\* (FS-A15; `midas_bs.py 200 <case> 3,6,12 rgap`; `midas_bs_BS{0,1,2}_rgap.log/.csv`).** The daily 2-year in the daily block and in the monthly averages is replaced by its r\*-gap form, as for the note's policy variable: DGS2 minus 1-year expected inflation minus Laubach-Williams r\* (monthly, interpolated between mid-months). The window and event-day moves are unchanged (the offset moves slowly); the market index was already in r\*-gap form. No time trend. MODEL, NS, 3 / 6 / 12 lags [verified]:

| Case, 2-year as r - r* | u, 10 m | u, 24 m | u, 36 m | Price level, 24 m | IP, 10 m | IP, 24 m | Commodity index, 24 m |
|---|---|---|---|---|---|---|---|
| Base (u, core PCE) | +0.29* / +0.30* / +0.34* | +0.38* / +0.37* / +0.40* | +0.32* / +0.33* / +0.36* | -0.36* / -0.50* / -0.56* | | | |
| + IP | +0.27* / +0.33* / +0.34* | +0.35* / +0.38* / +0.41* | +0.30* / +0.35* / +0.38 | -0.35 / -0.54* / -0.56* | **-0.49* / -0.96* / -1.00*** | -0.04 / -0.24 / -0.46 | |
| + IP + IMF commodity index | +0.19* / +0.18 / +0.20* | +0.22* / +0.17 / +0.18 | +0.18 / +0.22 / +0.31 | -0.53* / -0.53* / -0.12 | +0.09 / +0.17 / +0.15 | +0.56 / +0.75 / +1.02 | +2.9 / +3.5 / +9.3* |
| Bauer-Swanson benchmark | about +0.22 (peak) | about +0.17 | about +0.15 | CPI about -0.5 | about -1.6 | about -1.0 | about -2.6 |

\* = 90% interval excludes zero (the 12-lag u at 36 m in the IP case has lower bound +0.00).

Reading [inference]:
1. **Measuring the 2-year relative to r\* brings the responses closer to Bauer-Swanson in shape.** Unemployment rises faster (+0.3 pp at 10 months) and then levels off and fades slightly (+0.3 to +0.4 at 36 months) instead of building to +0.5; the price-level fall is significant for nearly every lag length (-0.35 to -0.56% at 24 months).
2. **IP now falls**, significantly at 10 months: -0.5% (3 lags), -1.0% (6 and 12 lags), against about -1.6% in Bauer-Swanson; it recovers by 24 months. This is the first specification in which IP has the conventional sign.
3. **Why** (a reading, not tested): the nominal 2-year trends down from 1994 to 2021 with r\* and inflation expectations, while IP trends up, so in levels the reduced-form link between rates and IP picks up opposing trends; the r\*-gap removes the slow-moving part of the rate. This is consistent with the time trend (FS-A13) helping unemployment and prices but not IP: a common deterministic trend does not remove the r\* movements.
4. **Commodity prices still do not fall**, and adding them still weakens unemployment and turns IP positive at 24 months; the commodity puzzle survives the r\*-gap.

### 7. The challenges these papers identify, and whether we address them [inference unless marked]
| Challenge | Who | What they do | Us |
|---|---|---|---|
| **Weak instruments**: FOMC surprises explain little of the monthly policy-rate residual | Gertler-Karadi (2-year weak, F 0.9-5.2); Bauer-Swanson (FOMC-only orthogonalized F 2.44; 10.2 with speeches); Caldara-Herbst (2-year proxy reliability 0.01); this project (F 2-6) [verified in `mp_var_fci`] | add speeches, more events (BS); Bayesian priors on proxy reliability (CH) | **Sidestepped.** No first stage: the window move is the impact. The cost is the exclusion restriction. |
| **Predictable / endogenous surprises** (Fed response to news) bias responses toward zero and produce puzzles | Bauer-Swanson; Miranda-Agrippino-Ricco (Greenbook) | orthogonalize on pre-announcement data | **Partly.** The shock enters only through its window impact; the propagation is estimated from the reduced-form link of macro to lagged financial conditions, not from the shock's correlation with macro, so a correlation of the surprise with earlier news cannot drag the macro response toward zero the way it does in a proxy-SVAR. The Greenbook purge changes nothing. We have not used Bauer-Swanson's own orthogonalization (their predictors and speech surprises are not in our data). |
| **Information effect** (hawkish surprises signal good news) | Nakamura-Steinsson; Miranda-Agrippino-Ricco | NS: model both channels; MAR: purge on Greenbook | **Partly, by assumption.** Any channel from the announcement to activity that does not go through the 2-year and the index is excluded. Information that moves the index in the window (e.g. equities) is still included. The direct regression shows the total effect is wrong-signed and dominated by 2007-09, which is what an information effect (or crisis timing) would produce. |
| **Policy reacts to credit spreads; omitting credit attenuates everything** | Caldara-Herbst | include the excess bond premium; Bayesian proxy | **Not addressed.** Credit is not in the window impact (no intraday series; Baa versions in `MF_DEVELOPMENT.md` are contaminated and lower the responses by a third to a half). This is the main open gap. |
| **Temporal aggregation** of daily surprises into monthly proxies | Kilian (2024); Chudik-Georgiadis; Chudik-Kilian; Jacobson-Matthes-Walker [secondhand]; Gazzani-Vicondoa | monthly-average proxies; mixed-frequency distributed lags | **Addressed by construction**: the daily block and monthly averages place each event in its month. |
| **Little policy variation after 1994; sample dependence** | Ramey (2016) [secondhand]; Bauer-Swanson's response | long VAR sample with short instrument sample | **Base case works on 1994+ alone**; the long samples are robustness and agree in year one. |
| **Price puzzle** | many; Bauer-Swanson show it disappears with orthogonalization | | **No puzzle**; the price level falls slowly. |
| **Output and commodity-price responses** | Bauer-Swanson (IP and commodities fall); Caldara-Herbst (IP falls with credit in the VAR) | | **Not matched** (section 6a): IP does not fall, commodity prices rise; the reduced-form financial-to-macro link is procyclical for these variables. |

### 8. What this means for the note, and open items
- The note's claim can be: with the window impact and an explicit exclusion restriction, a 1 pp policy-induced rise in the 2-year raises unemployment about 0.2 pp within a year (0.4-0.5 pp by year three) and lowers the core price level about 0.4% after two years; these match Bauer-Swanson's best-practice estimates without needing a strong instrument. The exclusion restriction must be stated as the identifying assumption, with the direct regression as the (uninformative) check.
- Open: (i) a credit variable (ICE BBB daily, 1997+) in the window impact and the daily block, to answer Caldara-Herbst; (ii) Bauer-Swanson's orthogonalized surprises as the shock (needs their data); (iii) weak-instrument-robust comparison for the direct regression; (iv) the daily-block coefficients are not bootstrapped.

Sources: [Bauer-Swanson, NBER WP 29939](https://www.nber.org/papers/w29939) (read: sections 5.1-5.4, Figs. 2, 3, 8); [Caldara-Herbst, FEDS 2016-049](https://www.federalreserve.gov/econresdata/feds/2016/files/2016049pap.pdf) (read: sections 4, 6); Nakamura-Steinsson (2018, QJE; read earlier, notes in `../mp_var_fci/MP_QA.md`); [Francis-Ghysels-Owyang, St. Louis Fed WP 2011-009](https://doi.org/10.20955/wp.2011.009); [Chudik-Georgiadis, Dallas Fed GWP 356](https://doi.org/10.24149/gwp356); [Chudik-Kilian, Dallas Fed WP 2603](https://www.dallasfed.org/-/media/documents/research/papers/2026/wp2603.pdf); [Kilian, Dallas Fed WP 2310](https://www.dallasfed.org/-/media/documents/research/papers/2023/wp2310.pdf) (JEDC 2024).
