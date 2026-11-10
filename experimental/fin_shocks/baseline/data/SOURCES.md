# Raw inputs of the Note B package (`baseline/data/`)

Every file is a public series or a file of the repository; nothing is downloaded when the package runs. Tags: [verified] = checked against the source in this work;
[secondhand] = from the repository's documentation; [unverified] = origin not documented.

| File | Content | Source |
|---|---|---|
| `DGS2.csv`, `DGS10.csv` | daily 2- and 10-year Treasury constant-maturity yields | FRED [secondhand] |
| `GS10.csv` | monthly 10-year yield | FRED [secondhand] |
| `PCEPILFE.csv` | core PCE price index (monthly) | FRED [secondhand] |
| `UNRATE.csv`, `NROU.csv` | unemployment rate; natural rate (CBO, quarterly) | FRED [secondhand] |
| `EXPINF1YR.csv`, `EXPINF2YR.csv`, `EXPINF10YR.csv` | 1-, 2-, 10-year expected inflation | Federal Reserve Bank of Cleveland, via FRED [secondhand] |
| `livingston_median_growth.xlsx` | Livingston Survey median CPI expectations (pre-1982 expected inflation) | Federal Reserve Bank of Philadelphia [secondhand] |
| `rstar_onesided.csv` | one-sided r*: Laubach-Williams and Kiley | NY Fed LW estimates; Kiley; vintage not stated [unverified] |
| `RTWEXBGS.csv`, `TWEXBPA.csv` | real broad dollar indexes (spliced in 2006) | FRED / Federal Reserve Board [secondhand] |
| `shiller_cape.csv` | monthly CAPE (before 1990-92 splice) | Shiller [secondhand] |
| `gs_daily.csv` | monthly average of the daily CAPE behind the repository's GS replication (column `cape`) | repository (live-page workflow) [secondhand] |
| `gs_daily_levels.csv` | daily CAPE (`x_cape`) and dollar (`x_usd`) levels, 1990 on | repository root `fcig_gs_daily.csv`, produced by the daily workflow `fcig_gs.py`; dollar is a noon series [secondhand] |
| `usmpd_monetary_events.csv` | 30-minute-window changes around FOMC announcements (MP1, MP2, ED2-ED4, 2- and 10-year yields, S&P 500, dollar) | Federal Reserve Board USMPD (Bauer and Swanson), 'Monetary Events' sheet [secondhand] |
| `gsw_sveny02.csv` | fitted 2-year zero-coupon yield, 1961 on (months before DGS2 exists, start before 1976-06) | Gurkaynak-Sack-Wright, Federal Reserve Board [secondhand] |
| `ebp.csv` | excess bond premium (`ebp`) | Favara, Gilchrist, Lewis and Zakrajsek [secondhand]; the file's origin and vintage are not documented [unverified] |

## DFF.csv and PPIACO.csv (for the standard-method comparisons, `08_literature_style.py`)
Effective federal funds rate, daily, FRED series DFF (copied from `experimental/mp_var_fci/data/DFF.csv`; [secondhand]: not re-downloaded, vintage not recorded). Used only as the policy variable of the funds-rate Cholesky VAR cross-checks.
`PPIACO.csv`: producer price index for all commodities, monthly, FRED series PPIACO (copied from `experimental/mp_var_fci/data/PPIACO.csv`; [secondhand]: not re-downloaded). Used only in the commodity-price check of the Cholesky VARs (log, monthly average).
Literature impulse responses (Bauer and Swanson 2023 etc.) are no longer used: Section 3.1 of Note B compares standard methods estimated on our own data (Ramey 2016 and Caldara and Herbst 2019 are cited in text only; read from the papers).
