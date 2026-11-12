# Core results on 1996+ beside 1973+ (Note A; no FOMC-window surprises)

**Question.** Do the VAR yardstick, level-versus-flow, stance and r*-ladder results hold on 1996-2026, the sample of the weights and of Note B?

**Design** (fixed in `common.py` before estimation). Rows: **a** main (VAR 1973+, 12 lags; regressions origins 1976-03+, OOS from 1995-01); **b** fixed 1996+ throughout (VAR 12 and 4 lags; origins 1996-01+; OOS from the first origin with 96 training months = 2004-12, 211 origins, **1 recession (2008)**); **c** excluding 2008-15 (VAR: a dummy per month; regressions: origins whose t-12..t+12 window touches 2008-15 dropped; OOS 1 recession, 2001); **d** weights through 2019 (Market only); **e** origins from 1974-01 (OOS from 1983-04, 3 recessions). 2020 is dummied (VAR) or dropped by window rule (regressions) everywhere. HAC 18 in sample, 12 for OOS; VAR bootstrap 500 draws, 12-month blocks. Tables: `out/CHECKS.md`, `checks_all.csv`, `ladder.csv`.

**(i) VAR Phi(12), market** [verified, `out/var.csv`]; Granger p in brackets.
| row | nominal | real | r* |
|---|---|---|---|
| a 1973+ | 0.57 [0.29, 0.77] | 0.61 [0.32, 0.82] | 0.65 [0.39, 0.83] (p 9e-9) |
| b 1996+, 12 lags | 0.53 [0.17, 0.83] (p .08) | 0.61 [0.21, 0.87] (p .05) | **0.73 [0.26, 1.00]** (p .001) |
| b 1996+, 4 lags | 0.51 [0.26, 0.75] | 0.60 [0.30, 0.85] | **0.58 [0.16, 0.91]** (p .001) |
| c excl. 2008-15 | 0.42 [0.20, 0.59] | 0.52 [0.26, 0.70] | 0.56 [0.30, 0.72] |
| d weights to 2019 | 0.56 | 0.60 | 0.62 [0.38, 0.78] |
No sign flips; 1996+ intervals are 1.6 times as wide. GS 0.71-0.82 and FRB/US 0.44-0.75 on 1996+.

**(ii) Level vs flow, du, market t(flow) / adj-R2 gain of flow:** a nominal 3.9/0.12, real 4.3/0.13, r* 5.2/0.14; **b 2.3/0.02, 2.8/0.03, 4.2/0.05**; c 3.5-4.5/0.20-0.23; e 4.0-5.0/0.11-0.12. Level t stays below 1.3 in a, b, d, e but **is 3.9-4.9 in c** (excluding 2008-15 the "level adds nothing" statement fails). Payrolls: flow t -2.9 (a), **-0.3 to -0.8 (b)**, -3.4 (c).

**(iii) Stance, du, index given FFG (flow / mixed), market r*:** gain 0.11/0.12, t 5.5/6.2, CW 1.95/2.31 (a); **gain 0.07/0.05, t 3.7/4.0, CW 2.0/2.2, RMSE 0.94/0.96 (b)**; c gain 0.13/0.15, CW 2.7/3.5; e CW 2.4/3.2. Nominal step on 1996+: gain 0.02, CW 0.3/-0.05. Payrolls on 1996+: gain 0, CW -1.3.

**(iv) Ladder, du, market r* minus nominal, in-sample R2 difference [90% paired block bootstrap]:** 1976-95 -0.006 [-0.06, 0.04]; 1996+ **0.030 [0.001, 0.046]**; 1976+ 0.014 [-0.03, 0.04]. OOS MSE r* vs nominal: 1996+ DM t 1.2, interval [0.001, 0.27]; r* vs real DM t 0.9 [-0.03, 0.23]. The r* step helps in 1996+, not before; the gain is small and the interval touches zero.

**Verdict: holds up for the VAR and the unemployment results; fails for payrolls; the size is cut.** Decisive: Phi(12) does not change sign (0.73 and 0.58 at r*, intervals overlap 0.65); unemployment flow t 4.2 and stance CW 2.0 at r* on 1996+; "r* helps only before 1996" is not found (it is the reverse). But the in-sample R2 gain is a third to a half of the 1973+ gain, rate-only (nominal) results are weak on 1996+, and the payroll flow is not distinguishable from zero.

**Power.** 1996+ has about 30 years, two recessions (2001, 2008) plus 2020 (dropped), 12-month overlap: roughly 25 independent outcomes. Only 2008 is out of sample. Counts are descriptive (39 VAR, 78 level-flow, 156 stance, 54 ladder cases; shared data); nothing is multiple-testing adjusted.

**Recommendation.** Keep 1973+ VAR as main and show the 1996+ line in the same table. State the yardstick as "about 0.6 (0.65 [0.39, 0.83] on 1973-2026; 0.73 [0.26, 1.00] and 0.58 [0.16, 0.91] on 1996-2026 with 12 and 4 lags)". Quote 1996+ sizes for regression claims (R2 gain 0.05, not 0.14). Drop payrolls; say the level result depends on 2008-15. Sub-period 0.39 and -0.01 (rstar_basis) were not re-run.

**Limits.** r*, weights full-sample; variables revised; row b flows use 1995 index values.
