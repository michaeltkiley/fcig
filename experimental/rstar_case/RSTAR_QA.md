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
