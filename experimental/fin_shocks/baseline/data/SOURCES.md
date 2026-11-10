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

## Literature values (`literature_irfs.csv`)
Impulse responses of other studies, read from the printed figures of the papers (not from replication files), for the comparison in Note B Section 3.3 [secondhand/read from figure: accuracy about +-0.005 per 25 bp shock, +-0.02 per 1 pp].
- **Bauer and Swanson (2023), NBER WP 29939** (published in NBER Macroeconomics Annual 2022, Vol. 37; the pdf was fetched from nber.org and checked page by page). Scaling stated in the paper: shock normalized so that the **two-year Treasury yield rises 25 bp on impact**, where the VAR uses the **end-of-month** two-year yield (p. 32 of the paper: "Gertler and Karadi (2015) also used the month-average Treasury yield in their analysis while we use the end-of-month values"). Values per 1 pp = 4 x the values per 25 bp. Figure 8 (benchmark, orthogonalized surprise, 90% bands): unemployment +0.19, +0.17, +0.15 and CPI -0.36, -0.48, -0.60 after 12, 24, 36 months (these equal the values the earlier draft of Note B had recorded). Figure B.1, last column (unadjusted surprise, includes unemployment): unemployment -0.17 on impact, crossing zero after about 7 months (read from the zoomed figure), +0.06, +0.15, +0.16 after 12, 24, 36 months; CPI -0.24, -0.38, -0.54.
- **Miranda-Agrippino and Ricco (2021)** via Bauer and Swanson (2023) Figure 7 (p. 48), which replicates their Figure 3 exactly: shocks of 100 bp in the **one-year** yield (not comparable in unit; not plotted). With the unadjusted Gertler-Karadi instrument (FF4GK) the unemployment response is about -0.15 pp on impact, crosses zero after about six to seven months (read from the zoomed figure) and is about +0.27 after 24 months; with the orthogonalized instruments (MPI, MPINEW_BC) it is positive from impact (about +0.3 to +0.4 at 12 months). Qualitative use only.
`literature_own_units.csv`: the series of the Miranda-Agrippino and Ricco (2021) unemployment panel (as replicated in Bauer and Swanson 2023, Figure 7: 100 bp in the one-year yield), read from the printed figure (+-0.02) and drawn in its own units in `report/fig_lit.pdf`. Not comparable in size with our responses; shown only for its sign pattern. (Jacobson, Matthes and Walker 2026 and Brennan et al. 2025 were read and deliberately not used: their shocks and outcomes are too different.)

## DFF.csv (added for the literature-style comparisons, `08_literature_style.py`)
Effective federal funds rate, daily, FRED series DFF (copied from `experimental/mp_var_fci/data/DFF.csv`; [secondhand]: not re-downloaded, vintage not recorded). Used only as the policy variable of the funds-rate Cholesky VAR cross-checks.
