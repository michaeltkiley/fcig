# Weights drift: do the market weights hold up on 1996+ and after 2010?

**Question.** The weights come from 253 announcements (1996-2026). Do they drift, and does a pseudo-real-time index change the picture? Design in `common.py`; descriptive, no formal tests.

**Design.** GLS one-factor weights, NS factor recomputed inside each window. Expanding window from the 80th announcement (about 2006; check at the 100th), updated at every announcement (174 dates); 20-year rolling window from 2016 (first window 1996-2016). Announcement bootstrap, 500 draws, at year ends 2006-2025 and Sep 2026. Baseline band = 5-95 percentile of `weights_boot.csv`: 10y [0.13, 1.13], equity [-0.070, -0.029], dollar [0.021, 0.114]; baseline weights 0.61, -0.051, 0.065. [verified]

**Weight path (figure `out/weight_path.png`).**
- Expanding window, after 2010 (124 dates): 10-year always inside the baseline band (range 0.42-0.69); dollar always inside (0.047-0.071); equity outside at 10 of 124 dates (Jan 2011 to Apr 2014, down to -0.073 vs band edge -0.070). Before 2011 the 10-year weight starts at 0.99 (Dec 2006) and falls to 0.34-0.45 in 2009-10 after the crisis announcements.
- 20-year rolling window: leaves the band. 10-year weight falls to 0.05 by Sep 2026 (outside from Mar 2024, 21 dates); dollar weight 0.12-0.13 above the band at 39 dates since Apr 2021; equity weight -0.01 to -0.03 (outside Apr 2021-Nov 2022, 13 dates). The rolling 10-year weight loses the 1996-2005 announcements, which carry most of the 10-year weight; the baseline lies inside each rolling window's own bootstrap interval for the 10-year and dollar weights, but not for the equity weight (2021-26, baseline -0.051 vs rolling interval [-0.045, -0.012]). [verified]
- Imprecision: the 10-year weight has bootstrap sd 0.31, 90% interval [0.13, 1.13], 2.2% of draws negative or above 2; expanding windows' own intervals are 0.9-1.3 times as wide and include 0 until 2016. The 10-year weight is what the data least identify; its response (psi 0.53, se 0.06) is precise, the weight is not, because it depends on residual covariances. Equity and dollar weights are tighter (equity sd 0.01). [verified]

**Index sensitivity (pseudo-real-time weights; X demeaned over the full sample, so the level is not real time).** Month-t weights = expanding estimate through month t; first estimate before Dec 2006 (constant weights).

| step | corr level 1996+ | corr 12m change | corr forward impetus (baseline Phi) | gap level 2004-06 / 2009-15 / 2022-26 |
|---|---|---|---|---|
| nominal | 0.94 | 0.95 | 0.94 | -0.24 / 0.27 / -0.38 |
| real | 0.94 | 0.96 | 0.96 | 0.10 / 0.05 / -0.33 |
| r*-gap | 0.97 | 0.98 | 0.98 | 0.12 / 0.18 / -0.25 |

(Gaps are mean pseudo-real-time minus baseline, in 2-year-yield pp; baseline level sd within the episodes 0.3, 0.9-1.0, 0.7.) Forward-impetus gaps at most 0.10. At the latest reading (Sep 2026) the two coincide by construction (final weights equal the full-sample ones); the forward impetus differs: 0.51 vs 0.27 (nominal), 0.31 vs 0.12 (real), 0.30 vs 0.18 (r*). One change worth noting: the unemployment response to the pseudo-real-time r* index at 12 months is 0.52 (baseline 0.65); real 0.43 (0.61); nominal 0.39 (0.57); same sign, smaller. The 100th-announcement start changes nothing material. [verified]

**Unit.** The scale of the raw NS factor (2-year pp per unit) moves 0.38 (2006), 0.35 (2009-14), 0.38 (2019), 0.42 (2026) in the expanding window, 0.37 to 0.45 in the rolling window: a rise of about 10 percent, mostly after 2019, inside the bootstrap bands of any date. Per 1 pp of 2-year news the 10-year response is stable (0.52-0.56); the dollar response rises from 1.9 (2005) to 4.2 (2026) and the equity response is stable (-7.5 to -8.3) in the expanding window. So the unit is stable; the dollar response drifts, which moves the dollar weight little because that weight is small. [verified]

**Verdict.** Yes for the expanding window on 1996+ and after 2010 (10-year and dollar always in the band; equity briefly out at the edge, 2011-14; flows correlate 0.94-0.98 with baseline, above 0.9). No for the 20-year rolling window after 2021-24: the 10-year weight shrinks toward zero and the dollar weight rises above the band; the failure comes from dropping the 1996-2005 announcements, not from a trend in the data since 2010. 'Out of sample' is not clean: the final weights use later announcements.

**Recommendation.** One figure: `out/weight_path.png` (expanding and rolling paths, baseline band, bootstrap bars). One sentence: "Re-estimating the weights on expanding windows of announcements from 2006 keeps the 10-year and dollar weights inside the full-sample 90 percent band and the equity weight inside it except in 2011-14, and the resulting flow correlates 0.94-0.98 with the baseline; a 20-year rolling window moves the 10-year weight toward zero by 2026, which I report as the imprecision of that weight."

**Limits.** 253 announcements; one seed, 500 draws; r*, unemployment gap, CAPE not real time; demeaning is full sample.
