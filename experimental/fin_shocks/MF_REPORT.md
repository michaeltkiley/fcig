# Window-identified MIDAS-VAR: monetary-policy effects on unemployment and inflation, compared with Bauer-Swanson and others (1 Nov 2026)

Tags: [verified] = computed here or read in the source; [read from figure] = read off a published chart, approximate; [inference] = my reading; [secondhand] = not checked in full text. Decisions: `FS_QA.md` (FS-A7 to FS-A10). Development history (stage 0, routes A and B, unrestricted MIDAS, all earlier tables): `MF_DEVELOPMENT.md`. Literature notes: `LITERATURE_MIDAS.md`.

## 1. Summary
1. **Base case** (1994+, 2-year scaling, Nakamura-Steinsson (NS) shock, MODEL, 3/6/12 monthly lags): a policy move that raises the 2-year yield 1 pp in the FOMC window raises the unemployment gap by **+0.16 to +0.21 pp at 10 months** and **+0.39 to +0.52 pp at 36 months**; every 90% interval excludes zero at 10, 24 and 36 months (one exception: NS-GB, 6 lags, at 10 months). The **core PCE price level falls by 0.24 to 0.44% at 24 months and 0.38 to 0.67% at 36 months**; with 12 lags the fall is significant at 12, 24 and 36 months, with 3 and 6 lags the interval includes zero. [verified]
2. **Bauer-Swanson's (2023) benchmark** gives almost the same numbers per 1 pp on the 2-year: unemployment about +0.22 pp at 10 months, CPI about -0.5% at 24 months and -0.8% at 50 months [read from figure]. Our unemployment response is more persistent (it keeps rising to 36 months; theirs fades after about 10 months).
3. We reach this **without a first stage** (the window move is the impact) and **without orthogonalizing the surprise**, which are the two problems Bauer-Swanson and Caldara-Herbst work hardest on. The price is an **exclusion restriction: the shock reaches unemployment and inflation only through the policy rate and the market index.**
4. A **direct regression** that does not impose that restriction (Chudik-Georgiadis / Chudik-Kilian) gives the wrong sign (unemployment falls after a hawkish surprise), driven by the 2007-09 events, and is about ten times less precise: it neither confirms nor rejects our estimate.
5. **Robustness:** Greenbook-purged shock (NS-GB) gives the same results; adding the current month's financial average gives the same or slightly larger; PATH gives larger and much noisier responses; the long samples give smaller, less persistent unemployment responses and a price response that depends on the lag length.

## 2. Identification and assumptions
- **Shock and impact.** NS policy-news factor (USMPD, 253 FOMC events, 1994-2026). Its impact is the 30-minute window change of the variables observed in the window: 2-year yield (scaled to +1 pp) and the market index (+0.99 per 1 pp on the 2-year). Macro variables are zero in the window. No credit spread in the impact vector (no intraday series).
- **Propagation.** A daily block (2-year yield, index; HAR form with 1-, 5-, 22- and 66-day averages; it also responds to this month's and last month's unemployment gap and core inflation) carries financial conditions forward from the event day. Monthly macro equations are rows of a monthly VAR in the unemployment gap and core PCE inflation with L lags of each and L lags of the **monthly averages** of the daily 2-year yield and index (equal weights within the month, one free coefficient per monthly lag; OLS).
- **Within-month timing.** Macro is set first in each month (from lags); markets then respond to it within the month; in the event month macro has not moved, so nothing macro enters the window or the event day. The event's position in the month comes from the empirical distribution of FOMC dates, so the event month gets only the post-announcement days (Kilian's (2024) monthly-average accounting holds by construction).
- **What identifies the macro response.** (a) The window impact (identified by timing in the 30-minute window); (b) the **exclusion restriction**: no channel from the announcement to macro other than the policy rate and the index; (c) the effect of financial conditions on macro is estimated from **all** month-to-month variation in the lagged monthly averages, so it assumes the economy responds to a given move in financial conditions the same way whatever moved them [inference: this is the assumption a reader will question most].
- **Uncertainty.** 200 draws: events resampled (window impact and event positions) and residual bootstrap of the macro equations. Daily-block coefficients held fixed.

## 3. Base case: 1994+, 2-year, NS, MODEL (`midas_step.py 200 ALL 1994 3,6,12`; `midas_step_1994.log`, `midas_step_1994_L3-6-12{,_irf}.csv`) [verified]
Per +1 pp window move in the 2-year yield. Unemployment gap in pp; core PCE price level in % (monthly annualized rate cumulated, /12). Median-path point estimate [90% interval].

| Lags | u, 10 m | u, 24 m | u, 36 m | Price level, 12 m | 24 m | 36 m |
|---|---|---|---|---|---|---|
| 3 | +0.21 [+0.07, +0.34] | +0.48 [+0.26, +0.71] | +0.52 [+0.29, +0.78] | -0.08 [-0.30, +0.11] | -0.24 [-0.60, +0.15] | -0.38 [-0.90, +0.14] |
| 6 | +0.16 [+0.02, +0.32] | +0.40 [+0.17, +0.66] | +0.47 [+0.21, +0.76] | -0.13 [-0.31, +0.06] | -0.34 [-0.79, +0.12] | -0.53 [-1.24, +0.15] |
| 12 | +0.20 [+0.02, +0.32] | +0.34 [+0.08, +0.52] | +0.39 [+0.06, +0.59] | -0.20 [-0.38, -0.03] | -0.44 [-0.76, -0.05] | -0.67 [-1.18, -0.02] |

Reading [inference]: the unemployment response is robust to the lag length (12-month values +0.26, +0.20, +0.20); more lags make it a little less persistent and the price response larger and more precise. No price puzzle in any version. The earlier statement "no inflation result" (based on the 12-month inflation **rate**) was too strong: the right comparison with the literature is the price level, and with 12 lags its fall is significant.

## 4. Robustness [verified unless marked]
**4.1 PATH instead of MODEL.** PATH replaces the model's daily path of the 2-year and the index, from the event day to the end of the month after the event, by the path estimated directly by event-day local projections; the model takes over after that. 1994+, NS, u at 12 months: +0.36 [+0.01, +0.74] (3 lags), +0.29 [-0.15, +0.78] (6), +0.31 [-0.23, +0.91] (12); price level at 24 months -0.30, -0.44, -0.58, intervals include zero except with 12 lags.
- *Why PATH could be better:* it uses the data, not the HAR model, for the first one to two months, where the HAR gives a flat index (about 1.0 per unit) while the data show further tightening (about 1.3, noisy). If the daily model misses post-announcement drift, PATH captures it.
- *Why it could be worse:* the local projections pick up everything else that happens in the 21-42 trading days after each announcement (data releases, other news). With about 250 events this is noise but also possible contamination if later news is correlated with the surprise; and any information effect that shows up as drift is carried into the macro response.
- *Why it is noisier:* the variance of a cumulated daily change grows with the number of days, and the month-(t+1) average puts full weight on the noisiest days; the NS-GB event set is smaller (205 events). Hence intervals two to five times wider than MODEL.

**4.2 Greenbook-purged shock (NS-GB).** MODEL nearly identical to NS (1994+: u 12 m +0.25, +0.19, +0.18 for 3/6/12 lags; price level 24 m -0.23, -0.33, -0.43). PATH with NS-GB is much larger (+0.64 to +0.78 at 12 m) and very noisy.

**4.3 Current-month financial average in the macro equations (+CUR; financial first within the month).** 1994+, NS, MODEL u 12 m: +0.31, +0.24, +0.25 (3/6/12 lags); price level 24 m -0.28, -0.46, -0.61 (12 lags: interval excludes zero).

**4.4 Long samples (BASE, MODEL, 6 and 12 lags; `midas_step_long.log`, `midas_step_BASE_long_L6-12{,_irf}.csv`).** The window impact still comes from the 1994+ events; only the macro equations and the daily block use the long sample (index interpolated monthly before 1990).

| Sample, scaling, shock | Lags | u, 10 m | u, 24 m | u, 36 m | Price level, 24 m |
|---|---|---|---|---|---|
| 1977+, 2-year, NS | 6 | +0.16 [+0.07, +0.28] | +0.15 | +0.11 [-0.01, +0.20] | +0.12 [-0.12, +0.40] |
| | 12 | +0.19 [+0.08, +0.29] | +0.16 | +0.11 [-0.01, +0.22] | -0.18 [-0.48, +0.07] |
| 1974+, funds rate, NS | 6 | +0.28 [+0.19, +0.39] | +0.21 | +0.13 | -0.14 [-0.40, +0.14] |
| | 12 | +0.35 [+0.26, +0.43] | +0.34 | +0.22 | -0.31 [-0.62, -0.02] |
| 1974+, funds rate, MP1 | 12 | +0.10 [+0.02, +0.17] | +0.10 | +0.06 | +0.03 [-0.15, +0.17] |

The long samples agree on the first year and give less persistence; the 2-year long-sample response falls to +0.06-0.08 at 12 months under +CUR (`MF_DEVELOPMENT.md` section 7). Why 1994+ is the base: the shock is only measured from 1994, and Kilian (2024) recommends estimating on the period where the surprises exist; the long samples mix in pre-1994 macro dynamics and a pre-1990 interpolated index.

## 5. Direct regressions that drop the exclusion restriction (`direct_mfdl.py`; `direct_mfdl.log/.csv`, `direct_ardl.log/.csv`) [verified]
**Chudik-Georgiadis (2022) restricted mixed-frequency distributed lag.** Monthly outcome regressed directly on the event-day shocks, each placed by its day in the month, with a daily response that is piecewise linear between knots at 0, 1, 2, 3, 6, 9, 12, 18, 24, 30, 36 months. Unemployment in levels and in first differences; core PCE price level in differences. Same units (per +1 pp window 2-year). Because the usual HAC bands proved far too narrow, inference is by **permutation** (shock values reshuffled across the same event dates, 500 times).

| Shock, outcome | 12 m estimate | permutation null 90% at 12 m | p |
|---|---|---|---|
| NS, u levels | -2.32 | [-3.74, +3.12] | 0.28 |
| NS, u differences | -2.05 | [-1.82, +1.69] | 0.06 |
| NS-GB, u levels | -1.11 | [-5.57, +4.64] | 0.70 |
| MP1 (funds rate), u differences | -1.69 | [-1.78, +1.36] | 0.07 |
| NS, price level | +0.32 | [-1.18, +1.33] | 0.68 |
| NS, 2007-08..2009-06 events dropped, u levels | -0.65 | [-2.59, +3.69] | 0.79 |

**Chudik-Kilian (2026) pooled ARDL** (12 own lags, shock lags 0-36, pooled monthly regressor = sum of the month's shocks, i.e. a shock on a random day of the month; permutation inference as above), 12-month responses:

| Shock | u gap (p) | Price level (p) |
|---|---|---|
| NS | -1.88 (0.11) | +0.40 (0.53) |
| NS-GB | -1.19 (0.44) | +1.22 (0.15) |
| MP1 | -1.94 (0.05) | +0.90 (0.09) |
| NS, crisis events dropped | -0.69 (0.41) | +0.44 (0.43) |
| MP1, crisis events dropped | -0.81 (0.33) | see log |

Adding own lags (their recommendation) tightens the null band only modestly (NS: ±1.9 pp at 12 months instead of ±3.4 in levels) and the picture is the same: wrong signs for unemployment and prices (a price puzzle), significant only for MP1 at the 10% level, and much weaker without the 2007-09 events.

Reading [inference]: without the exclusion restriction the point estimates have the wrong sign, as in the project's earlier local projections (`mp_var_fci`, `lp_weights`) and as Bauer-Swanson find with unadjusted surprises; the wrong sign comes mostly from the 2007-09 events (dovish surprises followed by rising unemployment). The direct estimates are about ten times less precise than ours: the null band at 12 months is about ±2 to ±4 pp against our ±0.15. Our +0.2 lies inside every direct interval except the full-sample NS first-difference version, where it is just outside. So the direct regression cannot test our estimate; all the precision of the MIDAS-VAR comes from the exclusion restriction.

## 6. Comparison with the literature
Units converted to "per +1 pp" on each paper's own scaling variable. Bauer-Swanson and Caldara-Herbst values read from text unless marked [read from figure].

| Study | Identification | Sample | Unemployment | Prices | Precision |
|---|---|---|---|---|---|
| **This note, base** | window impact + exclusion through 2-year and index; MIDAS-VAR | 1994-2026 | +0.16 to +0.21 pp (10 m); +0.39 to +0.52 (36 m) | core PCE level -0.24 to -0.44% (24 m), -0.38 to -0.67% (36 m) | u: 90% excludes 0; prices: excludes 0 with 12 lags |
| **Bauer-Swanson (2023), benchmark (Fig. 8)** | proxy-SVAR; FOMC + Chair-speech surprises orthogonalized to pre-announcement news; per 2-year | VAR 1973-2020, instrument 1988-2019 | about +0.22 pp peak at 10 m, about +0.17 (24 m), +0.15 (36 m) [read from figure] | CPI about -0.2% (impact), -0.5% (24 m), -0.6% (36 m), -0.8% (50 m) [read from figure] | 90% bootstrap bands: u excludes 0 from about month 3 to about 18-20; CPI excludes 0 throughout, narrowly in months 5-12 [read from figure] |
| Bauer-Swanson, unadjusted surprises (Fig. 3 left) | same, raw surprises | same | (not in that system) | CPI about -0.4% (24 m); IP trough -1.4% per 1 pp | responses about a quarter of the orthogonalized ones |
| Bauer-Swanson, orthogonalized (Fig. 3 right) | same, FOMC only | same | (not in that system) | CPI about -3% (24 m), IP trough -5.6% per 1 pp [read from figure] | 2-year yield turns negative after about 7 months, so per-impact scaling overstates; FOMC-only orthogonalized F = 2.44 |
| **Caldara-Herbst (2019)** | Bayesian proxy-SVAR; current-month futures surprise; funds rate, IP, excess bond premium | 1993-2007 | not reported | no price response (prices dropped from the baseline for that reason) | IP about -4% per 1 pp funds rate at 2.5 years (-0.75% for an 18 bp shock); without credit spreads, no IP response |
| **Nakamura-Steinsson (2018)** | 30-min window, policy-news factor; event study | 1995-2014 | no macro VAR; Blue Chip expected growth **rises** +1.0 per unit after a tightening (information effect) | breakeven inflation barely moves | real rates move one for one for years |
| Francis-Ghysels-Owyang (2011) | FOMC-day innovation in the daily funds rate; MIDAS direct regressions | 1960-2009 | insignificant; OLS gives the wrong sign | core inflation falls significantly only after about 21 months | wide |
| This project's earlier work (`mp_var_fci`) | Cholesky and proxy-SVAR on monthly data | 1994-2026 | Cholesky: wrong sign (-0.4 per 1 pp 2-year); proxy-SVAR: F 2-6, Anderson-Rubin sets unbounded | | |

Comparisons for our funds-rate and MP1 cases (robustness only): NS scaled to the funds rate gives +0.28 to +0.35 pp at 10 months per 1 pp funds rate; MP1 gives +0.07 to +0.10. A rough conversion of Caldara-Herbst's industrial-production effect to unemployment (IP moves about three times GDP, Okun coefficient 2) gives about +0.7 pp per 1 pp [inference, rough]: larger than any of our funds-rate cases.

**Reading [inference].**
1. **Unemployment.** Our base case matches Bauer-Swanson's best-practice estimate in the first year almost exactly (+0.2 pp per 1 pp on the 2-year at 10 months) and is more persistent afterwards (+0.4 to +0.5 at 36 months against their +0.15). Theirs is identified from 30 years of surprises with a full VAR and an orthogonalized instrument; ours from the window impact plus an exclusion restriction. Two quite different routes give the same first-year number.
2. **Prices.** Our price-level decline (about -0.4% at 24 months with 12 lags) is close to Bauer-Swanson's benchmark (-0.5%) and to their unadjusted-surprise version (-0.4%), far below their FOMC-only orthogonalized version (-3%, an outlier driven by the policy reversal). Like them, we find no price puzzle; unlike Caldara-Herbst, we find a (slow) price decline.
3. **Persistence.** Our unemployment response keeps building because the 2-year and index stay elevated in the daily block (HAR) and the monthly macro equations are persistent; Bauer-Swanson's 2-year yield response decays within about two years in Fig. 8.

## 7. The challenges these papers identify, and whether we address them [inference unless marked]
| Challenge | Who | What they do | Us |
|---|---|---|---|
| **Weak instruments**: FOMC surprises explain little of the monthly policy-rate residual | Gertler-Karadi (2-year weak, F 0.9-5.2); Bauer-Swanson (FOMC-only orthogonalized F 2.44; 10.2 with speeches); Caldara-Herbst (2-year proxy reliability 0.01); this project (F 2-6) [verified in `mp_var_fci`] | add speeches, more events (BS); Bayesian priors on proxy reliability (CH) | **Sidestepped.** No first stage: the window move is the impact. The cost is the exclusion restriction. |
| **Predictable / endogenous surprises** (Fed response to news) bias responses toward zero and produce puzzles | Bauer-Swanson; Miranda-Agrippino-Ricco (Greenbook) | orthogonalize on pre-announcement data | **Partly.** The shock enters only through its window impact; the propagation is estimated from the reduced-form link of macro to lagged financial conditions, not from the shock's correlation with macro, so a correlation of the surprise with earlier news cannot drag the macro response toward zero the way it does in a proxy-SVAR. The Greenbook purge changes nothing. We have not used Bauer-Swanson's own orthogonalization (their predictors and speech surprises are not in our data). |
| **Information effect** (hawkish surprises signal good news) | Nakamura-Steinsson; Miranda-Agrippino-Ricco | NS: model both channels; MAR: purge on Greenbook | **Partly, by assumption.** Any channel from the announcement to activity that does not go through the 2-year and the index is excluded. Information that moves the index in the window (e.g. equities) is still included. The direct regression shows the total effect is wrong-signed and dominated by 2007-09, which is what an information effect (or crisis timing) would produce. |
| **Policy reacts to credit spreads; omitting credit attenuates everything** | Caldara-Herbst | include the excess bond premium; Bayesian proxy | **Not addressed.** Credit is not in the window impact (no intraday series; Baa versions in `MF_DEVELOPMENT.md` are contaminated and lower the responses by a third to a half). This is the main open gap. |
| **Temporal aggregation** of daily surprises into monthly proxies | Kilian (2024); Chudik-Georgiadis; Chudik-Kilian; Jacobson-Matthes-Walker [secondhand]; Gazzani-Vicondoa | monthly-average proxies; mixed-frequency distributed lags | **Addressed by construction**: the daily block and monthly averages place each event in its month. |
| **Little policy variation after 1994; sample dependence** | Ramey (2016) [secondhand]; Bauer-Swanson's response | long VAR sample with short instrument sample | **Base case works on 1994+ alone**; the long samples are robustness and agree in year one. |
| **Price puzzle** | many; Bauer-Swanson show it disappears with orthogonalization | | **No puzzle**; the price level falls slowly. |

## 8. What this means for the note, and open items
- The note's claim can be: with the window impact and an explicit exclusion restriction, a 1 pp policy-induced rise in the 2-year raises unemployment about 0.2 pp within a year (0.4-0.5 pp by year three) and lowers the core price level about 0.4% after two years; these match Bauer-Swanson's best-practice estimates without needing a strong instrument. The exclusion restriction must be stated as the identifying assumption, with the direct regression as the (uninformative) check.
- Open: (i) a credit variable (ICE BBB daily, 1997+) in the window impact and the daily block, to answer Caldara-Herbst; (ii) Bauer-Swanson's orthogonalized surprises as the shock (needs their data); (iii) weak-instrument-robust comparison for the direct regression; (iv) the daily-block coefficients are not bootstrapped.

Sources: [Bauer-Swanson, NBER WP 29939](https://www.nber.org/papers/w29939) (read: sections 5.1-5.4, Figs. 2, 3, 8); [Caldara-Herbst, FEDS 2016-049](https://www.federalreserve.gov/econresdata/feds/2016/files/2016049pap.pdf) (read: sections 4, 6); Nakamura-Steinsson (2018, QJE; read earlier, notes in `../mp_var_fci/MP_QA.md`); [Francis-Ghysels-Owyang, St. Louis Fed WP 2011-009](https://doi.org/10.20955/wp.2011.009); [Chudik-Georgiadis, Dallas Fed GWP 356](https://doi.org/10.24149/gwp356); [Chudik-Kilian, Dallas Fed WP 2603](https://www.dallasfed.org/-/media/documents/research/papers/2026/wp2603.pdf); [Kilian, Dallas Fed WP 2310](https://www.dallasfed.org/-/media/documents/research/papers/2023/wp2310.pdf) (JEDC 2024).
