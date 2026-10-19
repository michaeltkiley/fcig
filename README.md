# FCI-G daily replication

A daily replication of the Federal Reserve Board's **Financial Conditions Impulse on Growth (FCI-G)**,
built from public data with the Fed's published weights and formula.

Live page: https://michaeltkiley.github.io/fcig/

One page with two tabs, **Fed FCI-G** and **Goldman-style FCI**. Each has a **Data** tab (summary tiles and one waterfall of
what changed since a comparison date you choose, by default the day before the last FOMC meeting) and a **Replication** tab
(method, checks against the published series, full history, data timing). Every tab ends with the disclaimer, notes and references.
`gs.html` just redirects to the Goldman-style tab (`#gs`).

## Next year, if conditions hold

Alongside the index, the page shows the growth impulse still to come a year from now from the
changes already in the index, if financial variables stay where they are. The Fed's weight on a
change made i quarters ago is beta(i+4) - beta(i), its effect on growth over the next four
quarters; row i + 4 of the same table, beta(i+8) - beta(i+4), is its effect in the four quarters
after that. Applying those rows to the same 12 (or 4) quarters of changes gives the next-year
measure, with the same components, range bars and waterfall from a chosen date. It uses only the
Fed's published weights but is not a Fed series.

## Method

Ajello, Cavallo, Favara, Peterman, Schindler and Sinha (2023),
["A New Index to Measure U.S. Financial Conditions,"](https://www.federalreserve.gov/econres/notes/feds-notes/a-new-index-to-measure-us-financial-conditions-20230630.html)
FEDS Notes, Technical Appendix. `multipliers.csv` is the weights file from the Fed's code release.
Three-month changes in each variable over the last 12 quarters (baseline) or 4 quarters (one-year
lookback) are multiplied by the weights and summed. Units are percentage points of real GDP growth
over the next year; positive values are a headwind.

## Data

| Variable | Source |
|---|---|
| Federal funds rate | FRED `DFF` |
| 10-year Treasury | FRED `DGS10` |
| 30-year mortgage rate | FRED `MORTGAGE30US` (Freddie Mac PMMS) |
| BBB yield | FRED `BAMLC0A4CBBBEY` (ICE BofA), stored in `history/bbb_ice.csv` because FRED keeps only three years; Moody's Baa (`DBAA`) before Oct 2023 |
| Stock market | Dow Jones U.S. Total Stock Market Index (Yahoo `^DWCF`), stored in `history/dwcf.csv` and extended from Yahoo's data API or, when that is rate-limited, the closing price on Yahoo's quote page; S&P 500 before 1995; FRED `SP500` changes for any day still missing |
| House prices | Zillow ZHVI, United States, mid-tier, smoothed, seasonally adjusted; Case-Shiller (`CSUSHPISA`) before 2000 |
| Dollar | FRED `DTWEXBGS`, earlier `TWEXB` and `TWEXBMTH` |

## Filling data that is not daily or not yet published

Inputs that publish weekly, monthly or with a lag are carried to the latest equity trading day by a simple rule
(`fill()` in `fcig_replicate.py`); real observations are never altered and `asof` in `data.json` still shows each
series' last real date.

| Input | Rule |
|---|---|
| Federal funds rate, 10-year Treasury, BBB, dollar | constant at the last value |
| Mortgage rate | 10-year Treasury plus the average of the last four weekly spreads, on the Thursdays after the last survey |
| House prices | trailing six-month average monthly growth, for each month-end up to the latest day |

The Goldman-style index already uses the same idea: rates and spread held constant, the dollar carried forward (or
moved with the ICE dollar index when available), and ten-year earnings (CAPE) grown at their trailing 12-month rate.

## Accuracy

Against the Fed's published monthly values, the total index has an RMSE of about 0.05 (3-year
lookback) and 0.04 (1-year) since 2024, and about 0.09 and 0.07 since 1990. The remaining
differences come mainly from the mortgage-rate series and a few month-ends where the Fed's stock
data appear to use the previous day's close.

## Files

- `fcig_replicate.py`: downloads inputs, updates `history/`, writes the outputs below
- `data.json`: data for `index.html`
- `fcig_replication_daily.csv`, `fcig_replication_monthly.csv`: results for both lookbacks with all components (monthly file includes the Fed's published values)
- `fomc_meetings.json`: FOMC meeting start dates, refreshed from the Fed's calendar page
- `.github/workflows/update.yml`: runs Monday through Saturday at 23:17 UTC and commits only when the data change

Run locally: `pip install -r requirements.txt && python fcig_replicate.py` (or `--offline` to reuse `raw/`).

Not an official Federal Reserve product.

## Goldman Sachs-style FCI

The Goldman-style tab (built by `fcig_gs.py`, data in `gs_data.json` and `fcig_gs_daily.csv`) is a daily levels index
using Goldman's published weights (fed funds 4.4%, 10-year 45.1%, BBB spread 39.6%, CAPE 4.9%, dollar 6.0%),
normalized to a 2000-2025 mean of 100. The Data tab shows only a waterfall from a chosen earlier date; the
Replication tab has the method, level check against published Goldman values (the replication runs about
0.6 above them), comparison with the Fed's FCI-G, and the data-currency rules. CAPE is made daily as
S&P 500 / E10, with E10 backed out from multpl.com's Shiller CAPE and extrapolated at its trailing growth
rate past the last anchor; the dollar is carried forward (or extended with DXY) past FRED's lag.
Not a Goldman Sachs product; the exact normalization and dollar index are proprietary.

Validation against Goldman's own series: `history/gs_nyfed_digitized.csv` holds Goldman's monthly FCI (Jan 1990-Jul 2022),
read from the vector chart on slide 18 of the New York Fed's July 2022 Investor Advisory Committee presentation
(`tools/digitize_nyfed.py`; about 0.01 resolution). Goldman's series is a monthly average. Against it the replication's
monthly changes correlate at 0.99 (slope 1.01); the level runs about 0.35 high on average and drifts between roughly 0 and 0.6.
