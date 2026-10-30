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
