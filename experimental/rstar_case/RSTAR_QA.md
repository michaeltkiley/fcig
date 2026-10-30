# r* cases: decisions, one at a time (started 30 Oct 2026)

Builds on the real case (`experimental/real_case/`, REAL_QA R1-R18): same data, expected inflation, weights, conversions, VAR design and comparison metric, except where
decided here. Rates are measured as gaps to the natural real rate r*.
Labels: [decided] by the user; [open] to be asked; [proposal] my suggestion, not adopted until confirmed.

## Decided at the start (user, 30 Oct; REAL_QA R16, R18)
- r* cases are separate from the real case.
- r* measures: Kiley and Laubach-Williams (LW), **one-sided estimates from the full-sample estimation** (current vintage, not real-time vintages).
  Sources already in the repository: `experimental/fci_compare/rstar_series.csv` (columns Kiley_onesided, LW_onesided; quarterly 1961Q1-2026Q2).
  Levels: Kiley 2.6 (1973) to 1.7 (2026Q2); LW 4.0 (1973) to 1.7 (2026Q2); LW falls further after 2008 (0.9 in 2015).

## Agenda
1. **Which rates are measured relative to r\***: real policy rate only, real 10-year only (as in the earlier `--rstar` variant), or both (and mortgage / BBB yields in FCI-G). [open]
2. **Kiley vs LW:** two parallel cases, or one main and the other a check. [open]
3. **Zero point for the r\*-gap rates:** keep demeaning (then r* matters only through its trend), or treat a zero gap as neutral (no demeaning of the rate gaps). [open]
4. **Quarterly to monthly:** step (hold within the quarter) or linear interpolation; months after 2026Q2. [open]
5. **Indexes rebuilt:** FRB/US EP/CP/GI, market index, GS, FCI-G (changes in r* enter the impulse?), NFCI/ANFCI (unchanged?). [open]
6. **Market output VAR:** re-estimated on the r*-gap market index? [open]
7. **Comparison and episodes:** rerun compare_real logic; against the real case. [later]

## Answers

**S1 (30 Oct).** Rates measured relative to r*: the real policy rate, the real 10-year, the BBB yield (real) and equities through the earnings yield (inverse CAPE, E/P), "all implicit
real rates" (user). Implementation notes (facts, not new choices): where BBB enters as a spread over the 10-year (FRB/US, GS), subtracting r* from both cancels, so r* changes BBB only
where it enters as a yield (FCI-G). Open follow-ups: the mortgage rate (S1a); how the equity weight carries over from 100 ln CAPE to the E/P gap (S1b).

**S1a (30 Oct).** Mortgage rate: treated like BBB: in FCI-G (where it enters as a yield) real and relative to r*; in FRB/US (a spread over the 10-year) unchanged, since r* cancels.

**S1b (30 Oct).** Equities enter as the earnings-yield gap E/P - r* (E/P = 100 / CAPE, pp), with each index's CAPE weight (per log point) converted by the fixed factor at the
1973-2026 mean E/P: weight per pp of the gap = w x (-100 / 5.65) = w x (-17.7). Option 3 (factor 100 / E/P(t)) shown and not adopted (`equity_conversion.py`).

**S2 (30 Oct).** Laubach-Williams (one-sided, full-sample) is the main r*; Kiley (one-sided) is the check.

**S3 (30 Oct).** Zero point: keep demeaning every variable over 1973-2026, as in the real case (r* matters through its movements over time, not its level).
- Implementation detail (stated, not a new choice): quarterly r* is interpolated linearly between mid-quarter months; after the last quarter (2026Q2) the last value is held.

**S4 (30 Oct).** FCI-G: r* applied consistently: changes in the funds rate, 10-year, mortgage and BBB yields are changes in their real gaps to r*; the stock term becomes the change
in the E/P gap through the S1b factor (-17.7 per pp, entered with FCI-G's stock weight; note this replaces the stock-price change with the valuation change, i.e. earnings growth drops
out); house prices and dollar as in the all-real FCI-G.

**Built (30 Oct; `rstar_indexes.py`, agenda item 5).** FRB/US EP/CP/GI, market, GS and FCI-G rebuilt under S1-S4 with LW (main) and Kiley (check); NFCI/ANFCI carried over unchanged
from the real case (no rates in them; stated, can be revisited). Against the real case, 1974-2026: levels corr 0.92-0.93 (LW) and 0.96-0.97 (Kiley), 12-month changes 0.93-0.97.
Mostly a shift in level over time: with r* high in 1973-2007 (LW about 3.3-3.6) and low after 2008 (0.6-0.9 until 2016), the r*-gap indexes are easier than the real case before 2008
and tighter after. Latest (2026-09, LW): EP_4 +0.44 (real -0.86), MKT -0.69 (-2.54), GS -1.12 (-2.77), FCI-G 1yr +0.07 (-0.04).

**S5 (30 Oct).** Market output VAR re-estimated on the r*-gap market index, same design (`var_rstar.py`). The r*-gap index predicts unemployment better than the real one:
Granger F 9.3 (LW, 4 lags; real case 4.5), unemployment-equation residual sd 0.156 vs 0.158 (4 lags) and 0.149 vs 0.152 (12); bootstrap bands above zero in months 1-36.
Yardstick Phi(12): LW 0.329 (4 lags), 0.568 (12); Kiley 0.288, 0.531 (real case 0.235, 0.501). Correlation with the r*-gap FCI-G (1-year, LW): forward impetus 0.71 / 0.82,
realized 0.74 / 0.58 (4 / 12 lags). Latest (2026-09, LW): EP -0.69, CP -1.1, forward impetus +0.5, realized -0.5 to -0.7.

**S6 (30 Oct).** Comparison: 1974-2026 against the real case, plus 1990-2026 against the real and nominal cases (nominal -> real -> r*); Kiley in summary lines
(`compare_rstar.py`, log `compare_rstar.log`, chart `compare_rstar_levels.png`).
- 1974-2026: r*-gap and real versions correlate 0.92-0.95 (LW; Kiley 0.96-0.97) in levels; the four main indexes still move together; widest windows 1975-82 and 2000-01
  (equities), as in the real case. The 1982 peak is higher (EP_4 +8.9 in Feb-Jul 1982 against +7.9 in the real case), mainly through the equity term (E/P of 15% against r* of about 3.4).
- 1990-2026 (zero 1990-2026): r* changes the picture much more than real rates did: corr real vs r* 0.57-0.63 in levels (nominal vs real 0.94-0.98), because LW r* falls
  from about 3.5 before 2008 to under 1 in 2009-16: 2009-16 looks tighter, 1990-2007 easier. Cross-index range falls again: nominal 1.16, real 0.95, r* LW 0.87, r* Kiley 0.78.
- Latest (2026-09, zero 1990-2026, LW): EP_4 +1.4, MKT +0.7, GS +0.1 (real case +0.4, -0.7, -1.1): measured against r*, conditions are tighter than average since 1990.
- Agenda items 1-7 done.

**S7 (30 Oct).** Written up: NOTE_PLAN section 4g (proposed role in the note to be confirmed) and a paragraph on gaps to r* in the weighting note's mapping section.

**S8 (30 Oct).** Additional VARs (user chose items 2 and 3; the standalone GS VAR skipped): `var_fcig_horse.py`, log `var_fcig_horse.log`.
- FCI-G scale check (a reading of +1 should raise the unemployment gap about 0.5 pp over the next 12 months; direct regression with u controls, HAC):
  1974-2026 replications: b 0.56-0.65 (all-real 0.65, se 0.13; r* LW 0.59; nominal 0.63): consistent with the claimed scale. 1990-2026: published 0.26 (se 0.12), replication 0.28:
  about half the claimed scale. 3-year lookback: 0.51 (all real, 1976-2026), 0.34 (published, 1990-2026). VAR responses to an FCI-G innovation are larger (about 1.2 at 12 months)
  but mix in the index's own persistence; the direct regression is the cleaner test.
- Horse race (predicting the unemployment gap; same VAR design; out-of-sample 12-month-ahead forecasts from 1995, ratio to a no-index benchmark):
  1974-2026: FCI-G versions best (Granger F 12-18 at 4 lags; out-of-sample RMSE ratio 0.68 r* LW, 0.76 real); level indexes significant in-sample (F 4.5-11.5, r* versions above
  real ones throughout) but no out-of-sample gain as levels (ratios about 1.0); as 12-month changes they do nearly as well as FCI-G (r* LW GS 0.71, r* LW MKT 0.76, real GS 0.79,
  real EP_4 0.89). 1990-2026: ANFCI best (F 12.8, RMSE ratio 0.52, from 2008), then GS and FCI-G (0.80-0.91); 12-month changes of ANFCI do not help.
- Side result: the 12-month change of real EP_4 has direct b 0.226 (t 3.1) on the next-12-month unemployment change, close to the FRB/US yardstick through Okun's law
  (0.4525 / 2 = 0.226); timing is not exactly matched, so this is only suggestive.

**S8a (30 Oct).** User: the forecast regressions should be local projections: u(t+12) on current and lagged u and current and lagged index. Redone in `lp_unemp.py`
(lags 0..L-1, L = 4 main and 12; HAC; 2020-2021Q1 dropped; log `lp_unemp.log`). This replaces the direct regressions and out-of-sample results of S8 (VAR Granger results stand).
- FCI-G scale: the sum of the index coefficients (a reading held over the lag window) is about the claimed 0.5 over 1974-2026 (all real 0.55 / 0.54, se 0.14 / 0.18;
  nominal 0.50 / 0.58; r* LW 0.46 / 0.44), but 0.09-0.15 (not significant) over 1990-2026 for the published series. The coefficient on the current reading alone (a new rise,
  past readings held) is larger: 1.2-1.3 (1974-2026), 0.55-0.74 (published, 1990-2026).
- Horse race: every index is significant in-sample over 1974-2026 (Wald p <= 0.02), r*-gap versions above real ones; FCI-G versions add most (adjusted R2 +0.07 to +0.08).
  Out of sample (origins 1995-2025) almost nothing beats the u-only projection: only the r* LW FCI-G (RMSE ratio 0.95 / 0.94) and r* Kiley FCI-G (0.97); level indexes 0.99-1.13.
  Over 1990-2026 the FCI-G versions are slightly below 1 at L = 4 (0.97-0.98), everything else above 1 (ANFCI 1.13-1.28 despite the best in-sample fit). The large out-of-sample
  gains in S8 came from a sparse specification with a weaker benchmark.

**S8b (30 Oct).** Detailed local-projection results (`lp_detail.py`, log `lp_detail.log`, charts `lp_detail_fcig.png`, `lp_detail_levels.png`; L = 4):
- Level indexes act through their recent change: at h = 12, c0 about +0.5 to +0.7 and c3 about -0.45 (sum near zero, 0.01-0.03), i.e. u(t+12) responds to the 3-month change of the
  index, not its level. FCI-G (already a change measure) has a positive sum (0.44-0.55, 1974-2026).
- Horizon profiles (1974-2026, FCI-G all real, sum of c): 0.20 (h3), 0.35 (h6), 0.55 (h12), 0.53 (h18), 0.43 (h24) against the claim of about 0.5 by h12. Published 1990-2026:
  0.12, 0.15, 0.14, 0.03, 0.02.
- Out of sample by subperiod (origins): the indexes help in 1995-2007 (RMSE ratios 0.78-0.94), mostly hurt in 2008-2019 (1.06-1.15; FCI-G 0.93-0.97 the exception) and hurt badly in
  2021-2025 (1.24-1.92: the 2022-23 tightening was not followed by higher unemployment). No Diebold-Mariano statistic is significant (|t| < 1.4).

**S8c (30 Oct).** Smoothed (impulse-response-weighted) indexes in the unemployment LP (`lp_smoothed.py`, log `lp_smoothed.log`; common sample 1976-2026, h = 12, L = 4 and L = 1):
- The growth-impetus forms predict; levels and current pressure do not. With the current reading only (L = 1): adjusted R2 gains 0.10-0.14 for FCI-G (1yr, 3yr), FRB/US GI_1yr+HP and
  VAR forward impetus; 0.00-0.02 for levels and current pressure. Out of sample (1995-2025): r* FCI-G 1yr 0.88, r* VAR12 forward impetus 0.89, r* VAR4 forward 0.90, r* FCI-G 3yr 0.91,
  real FCI-G 1yr 0.92, r* FRB/US GI 0.94; levels and CP 1.04-1.06. r* versions beat real ones in every family. No Diebold-Mariano t significant (best -1.1).
- With 4 lags the same ranking, smaller gains (best 0.94), and all indexes hurt in 2021-25 (1.26-1.75).
- Scale consistency (L = 1 coefficient vs the index's own claim of the 12-month unemployment effect): FCI-G 0.81 per GDP pp (claim 0.5); FRB/US GI 0.31 per funds-rate pp vs
  0.81 x 0.4525 = 0.37 implied by FCI-G's coefficient (r*: 0.30 vs 0.32); VAR12 forward impetus 0.50 (yardstick Phi(12) 0.50 real, 0.57 r*); VAR4 forward impetus 0.63-0.64
  (Phi(12) 0.24 real, 0.33 r*: the 4-lag VAR understates the effect).
- Current pressure (smoothed level) is uncorrelated with FCI-G (corr about 0) and has no predictive content.

**S9 (30 Oct).** User: store memory and update the plan; "not sure these tell us a ton, but we should report what we learned". Recorded in PROJECT_MEMORY 3g and NOTE_PLAN 4h
(proposed placement: a box in section 7). The common-experiment idea is noted as a possible extension, not started.
