# Raw inputs of the Note B package (`baseline/data/`)

Every file is a public series or a file of the repository; nothing is downloaded when the package runs. Tags: [verified 11 Nov 2026] = compared in this work with a fresh download from the
source named (in a separate scratch directory; the comparison script reads both files and reports common dates, the largest absolute difference and the number of differing dates);
[secondhand] = from the repository's documentation, not re-checked; [derived] = constructed by repository code.

| File | Content | Source and check |
|---|---|---|
| `DGS2.csv`, `DGS10.csv`, `GS10.csv` | 2- and 10-year Treasury constant-maturity yields (daily; monthly) | FRED [verified: identical on all common dates; FRED has 7 later daily observations] |
| `PCEPILFE.csv`, `UNRATE.csv`, `NROU.csv` | core PCE price index; unemployment rate; CBO natural rate | FRED [verified: identical on all common dates; UNRATE has one later month] |
| `EXPINF1YR.csv`, `EXPINF2YR.csv`, `EXPINF10YR.csv` | 1-, 2-, 10-year expected inflation | Federal Reserve Bank of Cleveland, via FRED [verified: identical except the latest month, revised by up to 0.01 pp; FRED has one later month] |
| `DFF.csv` | effective federal funds rate (daily) | FRED [verified: identical; FRED has 11 later days] |
| `PPIACO.csv` | producer price index, all commodities (monthly) | FRED [verified: identical on all common months; FRED starts in 1913] |
| `RTWEXBGS.csv`, `TWEXBPA.csv` | real broad dollar indexes (spliced in 2006) | FRED. `TWEXBPA` [verified: identical]. `RTWEXBGS` [verified with differences: 105 months from February 2014 differ from today's FRED values by up to 0.15 index points (levels 84-122), a later revision] |
| `rstar_onesided.csv` | one-sided r*: Laubach-Williams (`LW_onesided`) and Kiley (`Kiley_onesided`); `Richmond_median` empty | LW [verified: identical to the New York Fed 'LW Current Estimates' file, estimates based on data of 26 Aug 2026, final point 2026Q2, one-sided column, 262 quarters]. Kiley's series is the author's own estimate with no public file to compare [secondhand] |
| `ebp.csv` | excess bond premium (`ebp`), Gilchrist-Zakrajsek | Federal Reserve Board file `ebp_csv.csv` [verified: same series, correlation 1.0; the file in the package is an earlier vintage, with differences up to 0.0095 and a mean of 0.0012; one later month in the current file] |
| `shiller_cape.csv` | monthly CAPE, 1881 to September 2023 | Shiller (`ie_data.xls`, column P/E10) [verified: identical on all 1,713 months] |
| `gs_daily.csv` | monthly average of the daily CAPE behind the repository's GS replication (column `cape`) | repository (live-page workflow) [derived] |
| `gs_daily_levels.csv` | daily CAPE (`x_cape`) and nominal broad dollar (`x_usd`) levels, 1990 on | repository `fcig_gs.py` (daily S&P 500 over Shiller's E10 with multpl.com's table; dollar from FRED DTWEXBGS, earlier DTWEXB and TWEXBMTH) [derived]. Checks: monthly means of `x_cape` against Shiller's CAPE, 405 months 1990-01 to 2023-09: correlation 1.0, mean absolute difference 0.01 to 0.05 by decade, largest difference 1.04; `x_usd` against FRED DTWEXBGS from 2006: identical except 5 days (largest 0.54); the earlier dollar splice was not checked |
| `usmpd_monetary_events.csv` | 30-minute-window changes around FOMC announcements (MP1, MP2, ED2-ED4, 2- and 10-year yields, S&P 500, DXY) | U.S. Monetary Policy Event-Study Database, Federal Reserve Bank of San Francisco (hosted at frbsf.org; Acosta et al. 2025; the data of Bauer and Swanson), sheet 'Monetary Events' [verified: identical on all 279 common events; the SF Fed file has one later event, 28 Oct 2026, after the sample end] |
| `gsw_sveny02.csv` | fitted 2-year zero-coupon yield, 1961 on (used before DGS2 exists, start before 1976-06) | Gurkaynak-Sack-Wright, Federal Reserve Board `feds200628.csv` [verified: identical to 5e-5 on all 16,304 common days] |
| `livingston_median_growth.xlsx` | Livingston Survey median CPI expectations (pre-1982 expected inflation) | Federal Reserve Bank of Philadelphia [secondhand, not re-checked] |
| `bauer_swanson_mps.csv` | Bauer and Swanson (2023) orthogonalized surprise (`MPS_ORTH`) for FOMC announcements 1988-2019 | the authors' posted data, copied from `experimental/fin_shocks/legacy/data/` [secondhand: the download link could not be located in this session, so not re-checked] |

Not used in the baseline package: the literature impulse responses of earlier drafts (Bauer and Swanson 2023 etc.); Ramey (2016), Caldara and Herbst (2019) and Barnichon and Mesters (2021) are cited from the papers themselves (see `paper/REFERENCE_CHECK.md`).

| `gs_replication_daily.csv` | daily replication of the Goldman Sachs FCI with its published weights (column `fci`), 1990 on | repository `fcig_gs.py` [derived]; not a Goldman series |
| `gs_published_digitized.csv` | Goldman's monthly FCI, January 1990 to July 2022, read from the vector chart on slide 18 of the New York Fed's July 2022 Investor Advisory Committee presentation (about 0.01 resolution) | repository `history/gs_nyfed_digitized.csv`, `tools/digitize_nyfed.py` [secondhand: digitized from a chart, not checked against the original file] |
