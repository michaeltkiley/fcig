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
