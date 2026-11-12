# Vintage inputs for step 17 (pseudo real time)

Downloaded 11 Nov 2026 by `followup3/real_time/01_fetch.py` (one call per series and vintage date, first of the month). Nothing is downloaded when the package runs.
The raw vintage files (about 2,100 CSVs, 8.7 MB) stay in `followup3/real_time/raw/` (gitignored); this folder holds the compact tables the step reads.

| File | Content | Source | Built from |
|---|---|---|---|
| `vintage_panel.csv` | Per origin month t (1976-03 to 2025-09): UNRATE, PAYEMS (log x 100), PCEPILFE (log x 100) as known at t (`*_k`: level, 3- and 12-month lags; vintage dated t+2 months, else t+3) and as first reported for the outcome (`*_f`: values at t and t+12 in the vintage dated t+14 months, else t+15). `vint_*` flags the series found. | ALFRED, `https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=<ID>&vintage_date=<YYYY-MM-01>&cosd=<vintage minus 5 years>`; vintages UNRATE and PAYEMS 1977-01 to 2026-11, PCEPILFE 2001-06 to 2026-11 | `followup3/real_time/03_build_rt.py`, rounded to 6 decimals |
| `nrou_vintages.csv` | CBO natural rate of unemployment (NROU, quarterly), one block per monthly vintage 2011-03 to 2026-11, observations from 2008-01 | ALFRED, same endpoint, `id=NROU`; the earliest vintage ALFRED serves is March 2011 | raw files, observations before 2008 dropped (not used) |
| `lw_realtime.csv` | Final data point of the one-sided r* in each quarterly vintage (2005Q1 on) of the New York Fed real-time Laubach-Williams file; `release` = release date. `release_as_downloaded` keeps the dates as printed in the file | `https://www.newyorkfed.org/medialibrary/media/research/economists/williams/data/Laubach_Williams_real_time_estimates.xlsx` | `followup3/real_time/02_lw_realtime.py` |

Corrected release dates in `lw_realtime.csv` (typed wrongly in the NY Fed file): vintage 2010q4 printed 2010-01-26, corrected to 2011-01-26; 2016q4 printed 2107-04-21, corrected to 2017-04-21;
2019q2 printed 2019-05-30, corrected to 2019-08-29 (the last is an inference: the date duplicated an earlier vintage's release). No vintage was published between Aug 2020 and May 2023.

Not available in real time (revised series used): Cleveland Fed expected inflation, Shiller CAPE earnings, Kiley r*, FRB/US, and the market-index weights.
Total size of this folder: about 0.6 MB.
