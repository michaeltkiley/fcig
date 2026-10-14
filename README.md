# FCI-G daily replication

A daily replication of the Federal Reserve Board's **Financial Conditions Impulse on Growth (FCI-G)**,
built from public data with the Fed's published weights and formula.

Live page: https://michaeltkiley.github.io/fcig/

The page shows the index and its components (fed funds rate, long-term rates, stock market,
house prices, dollar), the level the day before the last FOMC meeting and the change since,
a waterfall of what drove that change, the daily path against the Fed's monthly releases,
and the full history since 1990 with replication errors.

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
| Stock market | Dow Jones U.S. Total Stock Market Index (Yahoo `^DWCF`), stored in `history/dwcf.csv`; S&P 500 before 1995; FRED `SP500` changes for days Yahoo has not yet supplied |
| House prices | Zillow ZHVI, United States, mid-tier, smoothed, seasonally adjusted; Case-Shiller (`CSUSHPISA`) before 2000 |
| Dollar | FRED `DTWEXBGS`, earlier `TWEXB` and `TWEXBMTH` |

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
- `.github/workflows/update.yml`: runs Monday through Saturday at 23:17 UTC and commits new data

Run locally: `pip install -r requirements.txt && python fcig_replicate.py` (or `--offline` to reuse `raw/`).

Not an official Federal Reserve product.
