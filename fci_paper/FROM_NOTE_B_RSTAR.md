# Handoff from Note B to Note A: r*, trends and the index (18 Nov 2026)

On 18 Nov 2026 Note B moved to the real version (two-year yield, funds rate and FCI; decisions `experimental/fin_shocks/FS_QA.md` FS-A85 to FS-A90). Several questions explored there concern the measurement of financial conditions rather than transmission, and the author agreed they suit Note A (`fci_paper/`).

This note lists them, with what is known, where the code and results are, and what a Note A analysis would add. None of it has been started in `fci_paper/`.

* Take each item one decision at a time in `FP_QA.md`.
* Every number below was computed on Note B's sample and weights (252 announcements, an intercept in the scaling, FS-A75). Recompute it on Note A's own weights and samples before using it. Note A's weights differ by about 1 percent.
* Tags: [verified] = computed and checked in this repo; [inference] = a reading, not a computation.

Where Note A stands now (`fci_paper/paper/fci_paper.tex`):
* Section 3, "Measured Relative to What? The Neutral Level", covers the three steps (nominal, real, relative to r*), the decomposition of the gap to a neutral level ($x^*_t=\iota r^*_t+c_t$) and the comparison with the published FCI* of Caballero et al. (2026).
* It uses Laubach-Williams (LW) r* only. Kiley's r* is in the data (`replication/01_data.py`), but not compared in the text, and it is flagged unverified in `FP_QA.md`.
* There is no trend analysis and no alternative r* measure.

---

## 1. Which r*? Alternative measures of the neutral rate

**Question for Note A.** How much does the stance read relative to r* depend on the r* chosen? The reading relative to r* is the one Note A argues for in levels, so its sensitivity to r* is the first thing a reader will ask about.

**What Note B built** (`experimental/fin_shocks/explore_rstar/`; results in `summary.md`, `filters_lw.md`, `filters_lw2.md`, `pc_lw.md`, `SURVEYS.md`; series in `rstar_measures.csv`, monthly 1965-2026):
* **Published estimates:** LW one-sided (New York Fed, August 2026 vintage), and Kiley one-sided.
* **Rate-based trends:**
  * an 8-year moving average of the real 2-year yield (MA8) and of the nominal 2-year (which replaces expected inflation plus r*);
  * a lagged 5-year moving average (real and nominal);
  * the 9-10-year forward rate (GSW SVEN1F09, `gsw_sven1f09.csv`) less 10-year expected inflation;
  * one-sided HP filters with monthly smoothing of 129,600 and 1,296,000 (the Ravn-Uhlig conversions of quarterly 1,600 and 16,000; cached in `hp_cache.csv`);
  * an exponentially weighted average of the real 2-year (EWMA 180 months);
  * an EWMA 120 of the simple average of the real 2-, 5- and 10-year yields;
  * one-sided filters (Butterworth, double EWMA, Kalman local level) of the level factor (first principal component) of the 2-, 5- and 10-year yields.
* **Survey:** SPF BILL10 less CPI10, placed in February, from 1992 only. No survey of long-run rate expectations goes back to 1973: the earliest are the Blue Chip surveys (long-run bill rate from 1983), and Consensus is subscription only (`SURVEYS.md`; the SPF files are in `survey_data/`).

**Findings** [verified] (`filters_lw.md`, 1973-2026, root-mean-square error against one-sided LW, in pp):
* **Real rates track LW; nominal rates do not.** The best one-sided filter is an EWMA of the real 2-year with a half-life of about 15 years (180 months). Its RMSE is 0.65, about as close to LW as Kiley's r* is (0.63). The real funds rate is next (EWMA 240 months, 0.75). The best nominal filters are at 1.6 to 2.0.
* **Benchmarks:** a constant has an RMSE of 0.92 and an in-sample linear trend 0.57. The best rate filter beats a constant but not a straight line. LW falls about 0.47 pp per decade.
* **Other filters are worse:** moving averages and one-sided HP do worse at any window. The best moving average (144 months) has an RMSE of 1.18 and runs 1-2 pp below LW after 2008. Level-factor filters do no better than a single real yield (`pc_lw.md`).
* **Errors by decade** (EWMA 180): −0.7 in the 1970s, +0.5 in the 2010s, −0.7 in the 2020s. The EWMA depends on its start date: started in 1966 its RMSE is 0.61, started in 1970 it is 0.84.
* **In Note B's model, none of the alternatives reproduced LW's results from 1996** [verified; `summary.md`]. The r*-gap result depends on LW specifically. That is a reason, in Note A, to show the index under several r* measures, not only LW.

**What a Note A analysis would add:**
* the index relative to r* under three or four of these measures (LW, Kiley, the EWMA 180 of the real 2-year, the forward rate less expected inflation, and SPF from 1992), on one figure;
* the dates at which the readings differ by more than a point;
* the correlation with the published FCI* gap under each measure (Note A's Table on FCI*).

The point would be that the stance in levels is a reading conditional on an r* measure, and how much that matters.

## 2. How strongly the index moves with r*

**Question.** By how much does the neutral level of the index move when r* moves 1 point?

**Known** [verified, Note B weights]. The r*-gap index is the real index less $\kappa r^*$, with $\kappa = w_{10y} + |w_{eq}|\cdot 100/\overline{E/P} \approx 1.5$ (Note B: 1.533). The 10-year yield contributes its weight, 0.62, and the equity term about 0.9, about three-fifths of the total.
* A 1-point fall in r* lowers the neutral level of the index by about 1.5 units, in two-year-yield equivalents.
* The two-year yield's own loading on r* is 1, so the index is about 1.5 times as sensitive to r* as the yield. This is the "c ≈ 1.5" of the random-walk r* experiment (`explore_rstar/rw_real.md`).
* Note A has the loading vector $\iota$ in equation (gapdecomp) but does not state the total.

**What Note A would add:**
* one sentence and the number, by calibration, since $\kappa$ depends on the weights: the FRB/US and two-year-signal calibrations put less on equities;
* what an r* error of a given size, say the 1-point gap between measures in item 1, does to the reading of the stance.

## 3. How much each version of the index trends

**Question.** Does measuring relative to r* remove the slow movement from the index? Over which sample?

**Known** [verified, Note B weights]:
* **Linear trend, 1973-2026** (`baseline_real/report/numbers_ext.tex`, macros `tr:n:r2`, `tr:r:r2`, `tr:s:r2`): it explains 69 percent of the variance of the nominal index, 60 percent of the real index and 27 percent of the r*-gap index. Over five decades the r* step removes most of the trend.
* **Natural cubic spline, by sample** (`baseline_real/report/tab_slow_shares.tex`). Knots are at the first and last estimation months and the NBER peaks in between. Each cell gives the percent of variance fitted, 1973 sample / 1996 sample:

| Series | Nominal | Real | r*-gap |
|---|---|---|---|
| FCI | 94 / 42 | 92 / 32 | 79 / 56 |
| Two-year yield | 85 / 69 | 75 / 63 | 56 / 45 |
| Funds rate | 75 / 61 | 58 / 51 | 40 / 38 |

* **Since 1996 the r\* step adds slow movement to the index:** the spline fits more of the r*-gap FCI than of the real one. The r* adjustment removes trend over five decades but not over the last three. A likely source [inference] is the equity term (the earnings yield against a falling r*) and the size of $\kappa$ (item 2).
* The unemployment gap is 37 / 55 and core inflation 63 / 20. Since 1996 a spline fits more than half the variance of the unemployment gap, which is why a trend weakens Note B's results since 1996.
* Code: `07_report.final_section` in `baseline_real/`. The earlier spline diagnostics are `explore_rstar/spline_fit.py`, and the trend options (quadratic, linear and level shifts at peaks) are `explore_rstar/real_trends.py` and `quick_peaks.py`.

**What Note A would add:**
* a short table of these shares for Note A's own index and calibrations;
* the decomposition of the r*-gap index's slow movement into the 10-year yield term and the equity term;
* a statement of what "relative to r\*" does to the level reading in each period.

This connects directly to Note A's argument that levels need a neutral benchmark.

## 4. Ordinary-day against announcement-window loading

**Question.** How much does the index move with the two-year yield on ordinary days, against in announcement windows?

**Known** [verified, Note B r*-gap version]:
* **Window:** 0.99 [0.89, 1.12] (one by construction once Note B's intercept fix is in, FS-A75).
* **Ordinary days:** 0.28 [0.12, 0.39], the covariance of the daily-block innovations of the FCI and the yield divided by the variance of the yield innovation, on days without an announcement. The ratio is 3.6.
* Under the four calibrations the ordinary-day loading ranges up to about 0.7. The two-year-signal and FRB/US weightings have the higher ordinary-day loadings (Note B FS-A73; `fin_shocks/baseline/report/tab_weights4.tex`).
* Note B cut the figure and the numbers (FS-A86).
* Code and figure: `fin_shocks/baseline/07c_report_review.py` (section 4), `baseline/report/fig_ordinary.pdf`, and `lib/model.ordinary_loading`.

**What Note A would add.** The fact belongs with Note A's discussion of what counts as policy news (Section 4.1, "The Market Side"). The market weighting picks the combination of assets that moves with policy news, and on ordinary days the same combination moves much less with the yield. Recompute it on Note A's weights and in the real version.

## 5. Not r*-specific, but moved from Note B to Note A

* **Components and the proportional-weights restriction** (Note B D10, Note B's old Section 4.1 and Tables 7-8). In Note B's monthly equations the unemployment response barely depends on whether the 10-year yield, equities and the dollar enter separately. The price response needs the dollar tied to the yield.
  * Formal tests: equality of the yield and dollar coefficients (equities free) is rejected in the inflation equation in the nominal and real versions.
  * Code: `fin_shocks/baseline/09_weights_test.py`, `results/weights_test.csv`, `report/tab_components.tex`, `tab_weights_test.tex`, `tab_wt_full.tex`; the specifications `cmp`, `cmpE`, `cmpR` in `baseline/lib/model.py`.
  * For Note A: a test of the index restriction in a simple macro equation, by calibration.
* **Four calibrations in the macro model** (FS-A73, dropped from Note B by FS-A87). Under the futures-factor, two-year-signal, FRB/US and Goldman weights, the r*-gap responses from 1973 agree closely: the price level falls 0.7 to 0.8 percent at 24 months under all four. The weightings with higher ordinary-day loadings give smaller shifts from adding the FCI.
  * Code: `baseline/07c_report_review.py` (section 5), `report/tab_weights4.tex`, `output/four_weights_nb.csv`.
  * Note A's question, whether subsequent activity can distinguish the calibrations, could use this as a second, identified test.
* **Weights estimated without information shocks** (Jarocinski-Karadi subset; FS-A72, dropped by FS-A87). The index built from the 157 announcements in which the two-year yield and stocks move in opposite directions correlates above 0.9 with the baseline index from 1996.
  * Code: `baseline/02_indexes.py` (the JK weights), `output/market_weights_jk.csv`, `report/tab_jk.tex`.
  * Note A's appendix on other measures of policy news is the natural home.
* **Real-time status of r\*.** Note B uses the August 2026 vintage of one-sided LW (filtered, with parameters estimated on the full sample), so it is not real time. Note A's FP-A18 already notes LW vintages from 2005. A real-time comparison of the reading relative to r* would follow from item 1.

## 6. Left in Note B (for reference)

* **A random-walk r\* estimated inside the VAR** (`explore_rstar/rw_real.py`, `rw_real.md`): the real case, with the gaps x − r* and F − 1.5 r*, filtered by exact EM inside the model. This is a transmission model, so it stays with Note B's further work (Section 6 of `mp_transmission_real.tex`).
* **Note B's final section reports:**
  * the LW r*-gap step: larger responses, u24 +0.49 and P24 −0.81 from 1996;
  * a spline trend: smaller and not significant since 1996, about the same from 1973;
  * and it frames better measures of r* and of the neutral level of financial conditions as the next step.

  Items 1 to 3 here are that next step on the measurement side.
