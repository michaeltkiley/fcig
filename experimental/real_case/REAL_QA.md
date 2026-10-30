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

**R4 (30 Oct).** The splice is blended over 1982: the Cleveland weight rises linearly from 1/12 in January to 1 in December 1982 (the shifted Livingston series before, Cleveland after).

**R5 (30 Oct).** Macro-model real indexes as proposed:
- real policy rate (funds rate minus 1-year expected inflation) and real 10-year (minus 10-year expected inflation);
- spreads, CAPE, real dollar and house-price ratio unchanged;
- FRB/US weights and yardstick unchanged;
- eventual and current pressure and growth versions all rebuilt.

User added: extend all series back to the 1970s. Adopted without objection: before 1990, monthly-average long series (FEDFUNDS, GS10, MORTGAGE30US, Moody's BAA - GS10, Shiller CAPE, Fed real broad dollar), level-matched to the project's end-of-month series at the 1990 overlap.

**R6 (30 Oct).** House-price ratio before 1987: Shiller's home price index (monthly from 1953) over CPI rent of primary residence.

**R7 (30 Oct).** Zero point: the main version is demeaned over the full extended sample (1973-2026); the 1990-2026 mean is a check.
- Data built: `data_long.py`. Flag raised: the house-price-to-rent ratio trends up strongly (1973 about 35% below 1990s levels), partly from CPI rent mismeasurement before the mid-1980s. Question R8.

**R8 (30 Oct).** House-price variable in the real case: the ratio's deviation from its trailing 15-year (180-month) average, then demeaned like every other variable (`hp_trend.py`). Noted as a possible change for the nominal case later.

**R9 (30 Oct).** Real market index: keep the existing announcement-window weights (NS GLS: 10-year 0.6089, equities -0.0512, dollar 0.0654; 2-year-yield units) and apply them to the real 10-year, CAPE and real dollar, 1973-2026 (zero 1973-2026; 1990-2026 as a check).

**R10 (30 Oct).** GS replication, real version: Goldman weights (funds rate 0.044, 10-year 0.451, BBB spread 0.396, CAPE -0.049, dollar 0.060) applied to the real policy rate
(funds rate - 1-year expected inflation) and real 10-year (- 10-year expected inflation) as in R3, the BBB spread and 100 ln CAPE from the long data, and the **real** broad dollar
(user's choice, for consistency with the market and FRB/US indexes). 1973-2026; zero 1973-2026 (main), 1990-2026 (check). Reported in GS points; the 2-year-unit conversion
(x 0.945 / 0.98) is agenda item 8.

**R11 (30 Oct).** FCI-G: both. The published series stays as the benchmark; a real replication is the real-case FCI-G (`fcig_real.py`): Fed weights and lag structure, monthly data
from 1973 (1-year lookback from 1974-03, 3-year from 1976-03), each rate minus matched expected inflation (funds rate - 1-year; 10-year, mortgage, BBB yield - 10-year).
Stocks, house prices and the dollar left as published (nominal) pending R12. Check: the monthly nominal version matches the published FCI-G at corr 0.993 (1-year) and 0.989 (3-year), 1990-2026.
Pre-1986 stock levels: Shiller's monthly-average S&P 500 (raw/shiller_sp500.csv, from ie_data.xls).

**R12 (30 Oct).** Real FCI-G: both versions built in `fcig_real.py`: "real" (rates only real; stocks, house prices, dollar nominal as published) and "all real" (also stocks and
house prices over CPI, real broad dollar). Which is the main version: question R12a. All-real vs rates-only: corr 0.96 (1-year), 0.94 (3-year); all-real tighter by about 0.07-0.09 on average.

**R12a (30 Oct).** Main real FCI-G: "all real" (rates, stocks, house prices and dollar all real); the rates-only real version is the check.

**R13 (30 Oct).** NFCI and ANFCI unchanged (published series, month-end), 1973-2026, zero 1973-2026 (1990-2026 check); `nfci_real.py`. Flag for item 8: with the nominal-case
NS conversion (0.097, 0.185 per NS unit) the 1970s readings are very large (mid-1974: NFCI +51, ANFCI +26 in 2-year units, vs about +1.3 to +1.5 for the real market and GS indexes).

**R14 (30 Oct).** Market output VAR: the real market index itself is eventual pressure (option 3: only the market index for now; **revisit later** with the real GS index and the
all-real FCI-G in the VAR, the user's emphasis). Same design as the nominal case (`var_real.py`): 1973-01..2026-09, 2020 dummied, Cholesky u first, 4 lags main, 12 check (BIC 5).
Results almost identical to nominal: Phi(12) 0.235 (4 lags; nominal 0.227), 0.340 (5), 0.501 (12; nominal 0.507); Granger p <= 0.0013; bootstrap 95% bands above zero
from month 2-3 to 35-36. Correlation with the all-real FCI-G (1-year), 1975-2026: forward impetus 0.69 (4 lags) / 0.82 (12); realized 0.75 / 0.59. Latest (2026-09): EP -2.75,
CP -2.9, forward impetus +0.1 to +0.2, realized -0.4 to -0.6.

**R15 (30 Oct).** Conversions and units unchanged from the nominal case (GS x 0.945 / 0.98; NFCI 0.097 and ANFCI 0.185 per NS unit; FRB/US yardstick 0.4525). Files keep the full
1973-2026 history of every index; in comparisons and charts NFCI and ANFCI are shown from 1990 only (their converted 1970s values are very large, e.g. NFCI +51 in mid-1974).

**R16 (30 Oct).** r*: not part of the real case. The r*-gap cases are a separate, later set of cases building on the real case.

**R17 (30 Oct).** Comparison and episodes on the real set: 1974-2026 as the main (zero 1973-2026; ANFCI from 1990), 1990-2026 as the check against the nominal results
(`compare_real.py`, log `compare_real.log`, chart `compare_real_levels.png`). Agenda items 1-10 are done; open: revisit the market output VAR with the real GS and all-real FCI-G (R14).
