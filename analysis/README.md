# Monetary policy surprises and the FCIs: local projections (exploratory, Oct 2026)

How the Goldman-style FCI (`fcig_gs_daily.csv`) and the replicated Fed FCI-G (`fcig_replication_monthly.csv`, 3-year and
1-year lookbacks) respond to FOMC surprises, over 12 months. Not part of the daily workflow; the scripts need
`statsmodels`, `matplotlib`, `openpyxl` and (for the IV scripts) `linearmodels`, which are not in `requirements.txt`.

## Data
- Surprises: SF Fed **USMPD** workbook (`https://www.frbsf.org/wp-content/uploads/USMPD.xlsx`, "Monetary Events" sheet,
  1994 on). It holds raw surprises (MP1, MP2, FF1-6, ED1-8, OIS, Treasury yields, S&P 500, DXY), **not** target/path factors,
  so those are built in the scripts. The same file is used by `michaeltkiley/monetary_policy_surprises`
  (`scripts/00_fetch_usmpd.py`, era definitions in `scripts/01_load_full_sample.py`). Unscheduled events with MP1 = 0 are dropped.
- Outcomes: month-end values of each index and its contributions. GS: `fci` = 100 + sum of `c_*`. Fed: `<lookback>|FCI-G` and
  its seven component columns. Components sum to the total, so component responses sum to the total response.
- Zero-lower-bound eras (same as the surprise repo): 2008-12-16 to 2015-12-16 and 2020-03-15 to 2022-03-16. "Ex-ZLB" drops those months.

## Method
Monthly LP, h = 0..12: `y(t+h) - y(t-1)` on the month's summed surprises, controls = 3 lags of the monthly change in the
(total) index and 3 lags of each shock, the same controls for every y, Newey-West errors (12 lags). Higher index = tighter.
Reduced form unless the script name says IV.

## Scripts (run from the repo root, e.g. `python analysis/lp_surprises.py path/to/USMPD.xlsx`)
| Script | What it does |
|---|---|
| `lp_surprises.py` | GS FCI on **baseline target/path** (orth: target = MP1, path = ED4 residual on MP1) and the GSS rotation; optional controls for later surprises; `lp_irf*.png`, `lp_ci_*.png` |
| `lp_alt.py` | **Swanson three factors** (FFR, FG, LSAP; my reconstruction), **Nakamura-Steinsson**, **raw 2-year** surprise; `lp_alt_*.png` |
| `lp_fed.py` | the same cases with the **Fed FCI-G** (3yr and 1yr) as the outcome; `lp_fed_*.png` |
| `lp_compare.py` | **standardized comparison**: per 1 sd of the shock, outcome in sd of the index level; matched components; `lp_compare_*.png` |
| `lpiv_2yr.py`, `lpiv_2yr_3inst.py`, `lpiv_10yr.py` | LP-IV on the 2-year (instruments: target and path, optionally the 10-year event change) and on the 10-year (instruments: 2y and 5y event changes) |

## What was found (units: per +25 bp unless stated)
- **Path / forward guidance** tightens the GS FCI on impact (about +0.2 index points, t about 3) and the Fed FCI-G (+0.06 to +0.11 pp).
  The build-up to 12 months (GS +0.4, t about 1.6; Fed 3yr +0.4, t about 2.5) is a **ZLB-era result**: ex-ZLB it is gone by about h = 3.
  Swanson FG is almost the same as baseline path (event correlation 0.87); raw 2-year and Nakamura-Steinsson give the same impact effect.
- The **target** effect is small and mixed (GS full sample about -0.1 to 0; Fed about 0 to +0.1). Swanson FFR and the GSS rotation give
  the wrong sign on impact because their "target" also lowers the 1-year-ahead rate (ED4 loading about -0.2; factors correlated about 0.5).
- **Drivers** of the 12-month response in both indices: equity first, then the dollar and BBB; fed funds, 10-year, mortgage and house prices
  contribute almost nothing. Standardized (index-sd per 1-sd shock), the indices respond alike on impact (0.03 to 0.08) and the Fed FCI-G is
  about 1.5 to 2 times larger by 12 months (distributed lag over 12 quarters versus a level with fixed weights; not tested directly).
- Controlling for **later surprises** changes almost nothing.
- **LP-IV** was weak: first-stage F about 12 (full) and 6 (ex-ZLB) for the 2-year with target+path; adding the 10-year event change lifts ex-ZLB F to
  18 and gives a significant loosening at 6 to 12 months (-0.6 at h = 12), but the over-identification test rejects at h = 0 and the user judged the
  results too odd to rely on. The 10-year-on-2y/5y version has F of 0.2 to 7 and is uninformative. The reduced-form results are the ones to use.
- **Swanson LSAP** gives the largest effects (+1.5 GS full, +2.8 ex-ZLB at 12 months, t about 4), robust to dropping the 2008 crisis and the 2001/2008
  emergency cuts, but the factor's sd is only about 3.6 bp and the reconstruction is unverified. Treat with caution.

## Caveats
- About 385 monthly observations and 8 meetings a year: wide bands beyond about 6 months. HAC errors are not weak-instrument robust (IV scripts).
- The GS equity contribution is effectively the S&P 500 response (the E10 denominator is a smooth trend). Pre-2006 the dollar series is spliced from
  older, lower-frequency indices; pre-1997 BBB is a Baa-minus-10-year proxy.
- The Fed "next year, if conditions hold" measure only exists daily from 2020 and was not used as an outcome.

## Ideas not done
Jarocinski-Karadi information split (S&P 500 sign, in USMPD), communication-channel split (Statements / Press Conferences / Minutes sheets in
USMPD), Bauer-Swanson-style orthogonalisation to lagged FCI components, tightening versus easing and the six-era split, event-day (daily) LP,
Anderson-Rubin intervals for the IV cases, checking the Swanson factors against the published ones.
