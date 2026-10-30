# Real-rate case: decisions, one at a time (started 30 Oct 2026)

The base nominal case is closed (specification in `experimental/INDEX_QA.md`, results in `PROJECT_MEMORY.md` 3d-3f).
This folder builds the real case: every index uses real interest rates. Structure is unchanged where possible: no new FRB/US simulations and no new
announcement-window regressions unless decided here. Data change, the market output VAR is re-estimated, and anything else that changes is decided below.
Labels: [decided] by the user; [open] to be asked; [proposal] my suggestion, not adopted until confirmed.

## Agenda (where real rates enter)
1. **Expected inflation measure and horizon matching** (policy rate and 10-year), and its sample (back to 1973 for the market output VAR). [open]
2. **Macro-model (FRB/US) indexes:** real policy rate and real 10-year; spreads, CAPE, real dollar and house-price ratio unchanged; weights and yardstick unchanged (no new simulations). [proposal]
3. **Market index:** apply the existing nominal-window weights to the real 10-year (the earlier real versions did this), or re-estimate with event-window TIPS yields (USMPD has them). [open]
4. **GS replication:** real version of its rate components (the earlier real GS used the 10-year expectation for both rates). [open]
5. **FCI-G:** the official series is nominal-rate based; leave as published, or build a real version from the repository replication. [open]
6. **NFCI / ANFCI:** built from spreads and quantities; unchanged except for the few rate-level indicators. [proposal: unchanged]
7. **Market output VAR** (1973-2026, 2020 dummied, 4 and 12 lags): re-estimated with the real market index; current pressure and impetus rebuilt. [open: needs item 1's long expected-inflation series]
8. **Conversions and units:** GS 0.945 per point, NFCI/ANFCI weekly NS responses, FRB/US yardstick 0.4525: unchanged? [open]
9. **r*:** whether the real case also subtracts r* (earlier r* sets exist), or r* stays a separate case. [open]
10. **Comparison and episodes:** rerun `metric_v3` / `episodes_v3` logic on the real set. [later]

## Answers

**R1 (30 Oct).** Expected inflation: the Cleveland Fed model (EXPINF series, monthly from 1982), spliced to another series before 1982 (source and method: R2).

**R2 (30 Oct).** Before 1982: the Livingston Survey (Philadelphia Fed), spliced level-adjusted (shifted by its average gap to Cleveland over an overlap window; 1982-84 was the example given).

**R3 (30 Oct).** Matched horizons: the policy rate is deflated with 1-year expectations, the 10-year with 10-year expectations.
- Implementation detail (stated, not a new choice): before 1982 both horizons are extended with the Livingston 12-month CPI expectation ("base period to 12 months", semiannual, interpolated to months), each level-adjusted to its Cleveland series over 1982-01..1984-12.
