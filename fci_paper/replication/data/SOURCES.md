# Inputs of the package (`data/`)

Every file is a public series or a file of the repository; nothing is downloaded when the package runs. Snapshot of October 2026, copied from the companion note's package (`fci_note/replication/data/`).
Tags: [verified 11 Nov 2026] = the file is byte-identical to the copy in `experimental/fin_shocks/baseline/data/`, which was compared on 11 Nov 2026 with a fresh download from the source named
(see `experimental/fin_shocks/baseline/data/SOURCES.md` for the differences found); [secondhand] = from the documentation of the companion note, not re-checked; [derived] = constructed by repository code.
A re-check against fresh downloads was attempted on 11 Nov 2026 for the FRED files not in the first group and failed: the FRED endpoint returned errors from this session's network.

| File | Content | Source and check |
|---|---|---|
| `GS10`, `UNRATE`, `NROU`, `EXPINF1YR`, `EXPINF10YR`, `TWEXBPA`, `RTWEXBGS` (.csv) | 10-year yield; unemployment rate; CBO natural rate; Cleveland Fed 1- and 10-year expected inflation; real broad dollar (two series, spliced in 2006) | FRED. [verified; `RTWEXBGS` with differences: 105 months from February 2014 differ from today's FRED values by up to 0.15 index points, a later revision] |
| `FEDFUNDS`, `BAA`, `MORTGAGE30US`, `TWEXBMTH`, `DTWEXBGS`, `CPIAUCSL`, `CUUR0000SEHA`, `CSUSHPISA`, `SP500`, `NFCI`, `ANFCI` (.csv) | Federal funds rate; Moody's Baa yield; 30-year mortgage rate; nominal broad dollar (two series); CPI; CPI rent; Case-Shiller home prices; S&P 500; NFCI and ANFCI | FRED, Federal Reserve Bank of St. Louis [secondhand] |
| `rstar_onesided.csv` | One-sided r*: Laubach-Williams (`LW_onesided`) and Kiley (`Kiley_onesided`) | LW [verified: identical to the New York Fed 'LW Current Estimates' file, estimates of 26 Aug 2026, final point 2026Q2]. Kiley's series is the author's own estimate with no public file to compare [secondhand] |
| `shiller_cape.csv` | Monthly CAPE to September 2023 | Shiller, `ie_data.xls`, column P/E10 [verified] |
| `shiller_sp500.csv`, `shiller_home_price.csv` | S&P 500 and real home price index (Shiller), used before the FRED series start | Shiller's online data [secondhand] |
| `gs_daily.csv` | Daily GS FCI replication (`gs_fci`) and daily CAPE (`cape`) from 1990 | Repository (`fcig_gs.py`: public FRED data, ICE BofA BBB spread, Shiller E10 via multpl.com) [derived]. The monthly mean of the daily CAPE was compared with Shiller's CAPE in Note B's check: correlation 1.0, mean absolute difference 0.01 to 0.05 by decade |
| `livingston_median_growth.xlsx` | Livingston Survey median CPI expectations | Federal Reserve Bank of Philadelphia [verified only as identical to Note B's copy; its source was not re-checked: secondhand] |
| `usmpd_monetary_events.csv` | Changes in futures, yields, S&P 500 and DXY around FOMC announcements | U.S. Monetary Policy Event-Study Database, Federal Reserve Bank of San Francisco, sheet 'Monetary Events' [verified against the SF Fed file; the SF Fed file has one later event, 28 Oct 2026, after the sample end] |
| `fed_monthly_1yr.csv`, `fed_monthly_3yr.csv`, `multipliers.csv` | Published FCI-G (1- and 3-year lookback) and its multipliers | Federal Reserve Board, FEDS Notes data and code release [secondhand] |
| `frbus_paths.csv`, `frbus_hike_paths.csv` | FRB/US simulations: GDP responses to persistent unit shifts in each variable and to a persistent 1 pp funds-rate hike | Repository (`experimental/ms_fci/frbus_paths.py`, public FRB/US package, VAR expectations) [derived; not re-run in this package] |

Unverified inputs that matter most for the results: Kiley r* (robustness only), the FRB/US simulations (comparison index), the daily CAPE and GS series (GS conversion and CAPE after 1990), the Livingston Survey (expected inflation before 1982), the pre-2006 dollar splice.

Added 13 Nov 2026 (FP-A54; downloaded in this session, then read only by steps 28-30):

| File | Content | Source and check |
|---|---|---|
| `bauer_swanson_surprises.csv` | Bauer-Swanson monetary policy surprise `MPS` and orthogonalized surprise `MPS_ORTH`, 1988-2019 | michaeldbauer.com, `FOMC_Bauer_Swanson.xlsx`, sheet 'High-Freq FOMC Announcemt Surp', downloaded 13 Nov 2026 [verified: columns copied unchanged] |
| `ebp.csv` | Gilchrist-Zakrajsek spread and excess bond premium, monthly 1973-01 to 2026-10 | Federal Reserve Board, FEDS Notes `ebp_csv.csv`, downloaded 13 Nov 2026 [verified: unchanged copy] |
| `fcistar_results.xlsx` | FCI* (one-sided), FCI-G (3-year lookback) and output gap, quarterly 1990Q2-2024Q4, as published by Caballero, Caravello and Simsek | github.com/tcaravello/fcistar, `_results/fci_star_results.xlsx` (commit cloned 13 Nov 2026) [verified: unchanged copy] |
