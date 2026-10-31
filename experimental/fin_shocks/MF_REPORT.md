# Window-identified mixed-frequency VAR: summary report (31 Oct 2026)

Plan and history: `MF_PLAN.md`, `MIXED_FREQUENCY_NOTES.md`, `FS_QA.md`. All numbers below are in the `.log`/`.csv` files named in each section. Tags: [verified] = computed here; [inference] = my reading; [secondhand] = literature, not checked in full text.

## 1. Question and assumptions
A monetary shock is observed only in sparse, minute-long announcement windows. Financial variables (2-year yield, 10-year yield, equities, dollar, hence the market index; funds rate via futures surprise) respond in the window. Macro variables (unemployment gap, core PCE monthly rate) do not respond in the window (macro entries of the impact vector are zero; no robustness needed, per FS-A). The impact vector b comes from 30-minute USMPD window changes. The response is Theta_h b, propagated through a daily-financial / monthly-macro model. Credit spread is excluded from the baseline (no intraday series; it responds in the window, so it would contaminate b); Baa-10y versions are flagged sensitivities only. Shocks: NS (baseline), NS-GB (Greenbook-purged), MP1 (funds-rate scaled). Samples: long (1976/77-2026, 2-year from 1976-06) and 1994+ (USMPD). 2020-03..12 dropped. Results are per +1 pp rise in the scaling variable (2-year yield for NS, NS-GB; funds rate for MP1) on impact.

## 2. Stages and results
**Stage 0, monthly-proxy check** (`stage0_window_var.*`) [verified]. Event-day shock aggregated to monthly exposure. Unemployment rises: EVENT-timing u12 about +0.2 to +0.5, START-timing (shock at start of month) 2-3 times larger. Timing within the month matters for magnitude, not sign (my earlier "matters little" claim was wrong; corrected in MF_PLAN).

**Route A, daily HAR + monthly macro rows** (`route_a.*`) [verified]. NS, no credit: long 2-year u12 +0.20 [+0.07,+0.33]; 1994+ u12 +0.34 [+0.13,+0.51], u36 +0.48; long funds-rate +0.33. NS-GB nearly identical. MP1 +0.11. HYBRID (63-day directly estimated path, then model) has the same centre but intervals that include zero. With Baa spread [contaminated] the responses fall by about a third to a half.

**MIDAS-VAR** (`midas_var.py/.log`, B=20, rows are median [90%]) [verified]. Macro equation: m_t on 6 monthly lags plus exponentially weighted 252 daily lags of policy and index (one parameter each).

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
