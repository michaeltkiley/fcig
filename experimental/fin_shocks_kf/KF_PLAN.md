# Plan: Note B as a state-space model estimated with the Kalman filter

13 Nov 2026. Proposal for the user; nothing built yet. Decisions go to `KF_QA.md`.
Source for the Note B model: `../fin_shocks/baseline/lib/model.py` and `lib/daily.py` [verified: read in full 13 Nov 2026]; baseline cases `../fin_shocks/baseline/cases.py` panel B.

## 1. The Note B model in equations (what is to be replicated)
Day tau in month t; f_tau = (pol, idx) the 2-year yield form and the FCI in the same step (nominal, real, r*-gap); m_t = (u, pi) the unemployment gap and monthly annualised core PCE inflation; fbar_t the calendar-month average of f.

- **Daily block (HAR)**, estimated by OLS on weekdays from January 1996:
  f_tau = c + B_1 f^(1)_{tau} + B_5 f^(5)_{tau} + B_22 f^(22)_{tau} + B_66 f^(66)_{tau} + D_1 m_{t-1} + D_0 m_t + eps_tau,
  where f^(h)_tau is the average of f over days tau-1 .. tau-h.
- **Monthly block**, estimated by OLS, 1996-01 to 2026-09 (369 months; 1973 start as robustness), L = 3, 6, 12 (12 main):
  m_t = a + sum_{l=1..L} A_l m_{t-l} + sum_{l=1..L} G_l fbar_{t-l} + e_t.
- **Shock**: on the announcement day f jumps by b = (1, b_F), b_F the FCI's 30-minute window move per +1 pp on the 2-year (OLS slopes on NS policy news, 252 announcements 1996-); macro entries zero. Propagated through the daily block and the monthly equations; months of 21 days in the simulation; the event-month position averaged over six bins with the empirical shares. Price level = cumulated inflation / 12.
- **Inference**: 500 draws of a block bootstrap (calendar months in moving blocks of 12; each draw takes the monthly residuals, daily rows and announcements of the months drawn; monthly equations re-estimated on a recursively rebuilt series; daily block re-estimated on the drawn rows).
- **Targets to reproduce** (12 lags, 1996-, per +1 pp on the 2-year in the window; point [90% interval]):

| Case | u, 12 m | u, 24 m | P, 12 m | P, 24 m |
|---|---|---|---|---|
| nominal, no FCI | -0.81 [-1.20, -0.38] | -0.49 [-0.82, -0.13] | 0.09 | 0.02 |
| nominal, FCI | -0.05 [-0.50, 0.35] | 0.16 [-0.24, 0.55] | -0.13 | -0.43 [-0.80, 0.02] |
| real, no FCI | -0.60 | -0.33 | -0.03 | -0.11 |
| real, FCI | 0.09 | 0.23 | -0.23 | -0.48 [-0.84, -0.12] |
| r*-gap, no FCI | -0.29 [-0.60, 0.11] | -0.07 [-0.42, 0.24] | -0.21 | -0.44 |
| r*-gap, FCI | 0.34 [-0.05, 0.76] | 0.50 [0.01, 0.95] | -0.42 [-0.60, -0.20] | -0.81 [-1.23, -0.33] |

(From `../fin_shocks/baseline/results/<form>_<fci>_upi_1996-01_all_in.csv`, lags = 12.)

## 2. Restrictions the MIDAS form imposes
- **M1 Macro first within the month.** m_t is set before any day of month t; financial moves in month t cannot affect m_t.
- **M2 Flat monthly aggregation of finance.** Macro sees finance only through equal-weight averages of past whole months (no day weights; no same-month effect).
- **M3 The daily block conditions on the month's macro value as known on every day of the month**, including the current month's u and pi, which are not observed until after the month ends.
- **M4 Two-step estimation with independent blocks.** Daily and monthly blocks estimated separately; daily and monthly innovations uncorrelated; the daily block uses 1996- only; before 1990 the monthly equations splice in monthly series for the yield and Note A's monthly index.
- **M5 Stylised calendar in the responses.** 21-day months and six event-position bins.
- **M6 Macro entries zero in the window.** Decided in FS-A5 (31 Oct 2026: 'needs no robustness check'). Kept here; not a relaxation candidate unless the user reopens it.
- **M7 Macro data measured without error.**

## 3. The same model in state-space form (stage 1, the replication)
Daily clock (weekdays, actual calendar). State: the last 66 days of f; m_t, ..., m_{t-L}; fbar_{t-1}, ..., fbar_{t-L}; the running sum of f within the current month. The transition is time-varying only at month boundaries: on the first weekday of a month the monthly equation draws m_t (innovation e_t), the macro and fbar lags shift and the running sum resets; on every day the HAR equation draws f_tau (innovation eps_tau). Observation: f daily (missing where not available), m on the last weekday of each month.

With M1 to M7 imposed and every variable observed, the filter has no state uncertainty after the first observations and the Gaussian log-likelihood is the sum of the two blocks' conditional densities. Within each block every equation has the same regressors, so **maximum likelihood equals equation-by-equation OLS**. Stage 1 should therefore reproduce Note B's point estimates to machine precision [inference: follows from the algebra; to be verified numerically]. That makes stage 1 a test of the new code (filter, calendar, aggregation, impulse responses), not new evidence. That is the purpose: every relaxation in stage 2 is then measured against a model known to equal Note B.

Impulse responses in stage 1: computed from the state-space matrices (the shock enters the state on the event day as b), with the stylised calendar of M5 so that the numbers are comparable. Inference: see KF-Q2.

Computation [inference]: with finance observed daily from 1996, only the macro part of the state is ever uncertain, so the filter can run on a small latent state with the financial lags treated as data. A latent daily FCI before 1990 (relaxation K4) breaks this and needs the full state (about 190 elements over about 13,000 weekdays from 1976); feasible in numpy but slow inside a bootstrap.

## 4. Stage 2: candidate relaxations (one at a time, each against stage 1)
- **K1 Latent daily macro with feedback within the month (relaxes M1, M2, M3).** u and pi become latent daily series whose monthly averages are the observed data (u a stock averaged over the month; pi a flow). Financial moves in month t can then move m in month t, and the daily block conditions on the macro information available at tau (the filtered latent value) rather than on the month's final value. The monthly-average dynamics are kept as in Note B; what is added is the within-month path and its coefficients. This is the relaxation the state space exists for. The exact parametrisation needs a decision (KF-Q4).
- **K2 Joint estimation, correlated innovations, measurement error (relaxes M4, M7).** One likelihood for both blocks; daily and monthly innovations allowed to correlate; measurement error on u and pi. The window identification is unchanged (the shock is still b on the event day).
- **K3 Exact calendar in the responses (relaxes M5).** Responses for each of the 252 announcements on the actual calendar, averaged. MIDAS could do this too; it belongs here because the state space runs on the actual calendar anyway.
- **K4 Long sample without splicing (relaxes the splice in M4).** One model from 1973 in which the daily 2-year yield (1976-), the daily FCI (1990-) and the monthly FCI (1973-) are all observations of the same latent daily series (missing days are missing data; Note A's monthly index is an observed monthly average). Replaces the monthly fill-in used in Note B's 1973 robustness case.
- **Not proposed:** relaxing M6 (decided); time-varying parameters or stochastic volatility (a different model, not a relaxation of Note B's form).

## 5. Order of work (proposed)
1. Data step: inputs copied into this folder (see KF-Q1), checked against Note B's files.
2. Stage 1 for the r*-gap case with the FCI, 12 lags: state-space build, likelihood equals OLS, responses equal Note B's point estimates.
3. Stage 1 inference and the rest of panel B (nominal, real; with and without the FCI; 3/6/12 lags).
4. Stage 2: K1 first, then K2, K4, K3 (or the user's order). Each reported against stage 1 on the same cases.
