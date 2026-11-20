# Changes: `mp_transmission_real.tex` against `mp_transmission_session_integration.tex` (18 Nov 2026)

The new copy rebuilds Note B on the real baseline with the funds rate. Its decisions are in `../FS_QA.md` FS-A85 to FS-A89 and its plan in `../PLAN_REAL_BASELINE.md`.

* `mp_transmission.tex` and the integration copy are untouched.
* Every number is a macro from `../baseline_real/report/numbers*.tex`, and every exhibit comes from `../baseline_real/report/`.
* The qualitative claims are asserted in `../baseline_real/claims_real.py` (52 checks; all hold).
* Sync check: `python3 check_paper.py mp_transmission_real.tex` gives 0 problems.
* Compile: pdflatex, bibtex, pdflatex twice gives 67 pages, no errors, no undefined references, no overfull boxes.

All numbers below are at 12 lags, per +1 pp on the two-year yield in the window.

## Throughout
* **Headline version.** The r*-gap version is replaced by the real version: the two-year yield, the funds rate and the FCI less expected inflation.
* **Steps.** There are two: nominal and real. The r*-gap step moves to the new Section 6.
* **The model.** The funds rate is a third daily variable, $x_\tau=(R_\tau,F_\tau,I_\tau)'$. The impact vector is $b=(1, b_F, b_I)'$ with $b_I$ = 0.72.
* **Ordinary-day material.** The figure, the box and the "times as large" ratio are cut (FS-A86).
* **Components and weights.** The old Section 4.1 (components), Section 4.2 (four calibrations), Table 7 (components) and the weights tests are cut (D10, FS-A87). The JK weights are cut too. The JK surprise stays, in the appendix.
* **Lags.** 3 lags are dropped everywhere; the appendix reports 6.

## Abstract
* **Mechanism.** The mechanism sentence no longer quotes the ordinary-day ratio. It now says the surprise tightens financial conditions by as much as the yield rises.
* **Model.** The model is described as the two-year yield, the funds rate and an FCI; "relative to the neutral rate" is dropped.
* **Shift from adding the FCI** (from 1996, 24 months, both versions): about 0.7 pp for unemployment and 0.4 percent for the price level. It was 0.6 pp and a third of a percent across three versions.
* **From 1973:** real rates alone already lower prices by as much, and the FCI adds to the rise in unemployment.
* **Variance shares.** The old sentence ("about a tenth of the variation in inflation") is dropped from the abstract. The shares fell to about 5 percent.

## 1. Introduction
* **Fact.** The paragraph now gives the window moves (10-year yield +0.53, stocks −7.7 percent, dollar +4.2 percent; the FCI +1 unit) in place of the ordinary-day comparison.
* **Result.**
  * From 1996, real: u24 goes from −0.33 to +0.40, and P24 from −0.06 to −0.49.
  * The old r*-gap figures were u24 −0.21 to +0.45, and P24 −0.32 to −0.69.
* **From 1973:** real rates alone give P24 −0.53; with the FCI, P24 −0.56 and u12 +0.19.
* **Sacrifice ratio:** 1.2 from 1996 (was 1.1) and 0.5 from 1973 (was 0.7).
* **Figure 1.** It shows real rates alone and with the FCI, 1996 and 1973 side by side. Before, it showed the r*-gap version.
* **Four conclusions.**
  * Conclusion 1 now gives shifts of 0.75 and 0.73.
  * Conclusion 2 is now "real terms matter for prices over the long sample" (r* is gone).
  * Conclusion 4 now says "about 5 percent of inflation".
* **Approach.** The third feature is now "real terms". The funds rate is introduced in the second feature.
* **Road map.** The sentences on the components and the four calibrations are gone. A sentence on Section 6 is added.

## 2. Financial Conditions and the Empirical Approach
* **2.1.** "Why relative to r*" becomes "Why real". The ordinary-day example becomes one sentence, with no number. It explains why a model with rates alone carries a surprise as an ordinary move.
* **2.2.** Two versions of the index (nominal, real). The r* version, the neutral level $\kappa r^*$ and Caballero et al. move to Section 6.
  * A new paragraph, "Two rates", covers:
    * the funds rate and the two-year yield;
    * the zero lower bound: 109 months, 30 percent of months since 1996 and 17 percent since 1974;
    * Swanson and Williams (2014) [verified on the AEA page; abstract only];
    * why the two-year yield is the unit;
    * why the bound matters more since 1996.
  * New citation: `swanson2014`, added to `references.bib`.
* **2.3 (old "One Rise in the Two-Year Yield, Two Days") is removed.**
  * Its paragraph on how much the surprise explains moves into the new 2.3, "What the Windows Show and the Identifying Assumptions".
  * The funds rate's window impact (0.72) is stated there as a result of the window identification (FS-A89). It is checked against the effective funds rate: 0.89 the day after and 0.79 a month later.
  * The proportional-weights assumption now points to the companion paper, not to a test in Section 4.
* **2.4.** The model has three daily variables. The funds rate's daily equation is linear and does not impose the lower bound. The paragraph on the time trend moves to Section 6.

## 3. Results
* **3.1, standard methods.** Unchanged: one policy rate, as in the literature. The numbers are identical to before.
* **3.2, baseline.** Nominal and real only.
  * From 1996 the two versions are nearly identical with the FCI: u24 +0.40 and P24 −0.49 in both. The shifts are +0.75/+0.73 for u and −0.44/−0.43 for P.
  * From 1973, real rates alone give P24 −0.53; the FCI adds 0.16 to u12 and leaves P about where it is. The nominal version with the FCI gives P24 −0.22.
  * Removed: the sentence on persistence that quoted `pe:rho` (the ratio is now 1.02, so it adds nothing).
* **3.3, tradeoff.**
  * Real: $\mathcal P_{24}$ −0.85 from 1996 and −1.85 from 1973, so sacrifice ratios of 1.2 (0.6 to 3.8) and 0.5 (0.2 to 1.3).
  * The nominal version is bounded from 1996 (−1.02) and undefined from 1973. It was the reverse before.
  * Removed: the footnote on the dollar.
* **3.4, shares.**
  * Policy-direction shocks since 1990 explain: in the model from 1973, u 3.2 percent and inflation 4.1 percent (were 9 and 8); in the model from 1996, u 11.6 and inflation 5.7 (were 18 and 9).
  * The share of the two-year yield is 28 percent (was 62). The text now says about a quarter, where it said most.
  * The history episodes and the 2021–22 inflation contribution (0.90) are unchanged in sign.

## 4. Tests of the Approach
* **Removed:** 4.1 (components) and 4.2 (four calibrations).
* **Persistence.**
  * The FCI's direct estimate is now above the model at 5 days (1.37 against 1.02) and for the first-month average (1.49 against 0.95). Before, they were inside.
  * The text explains this by the reversal on the announcement day; from the close before, the model is inside.
  * Matching the first month changes u24 by 0.02.
* **Monthly benchmarks.**
  * The funds rate is now in the VARs.
  * Window-impact VAR: u12 +0.17 and P24 −0.23 from 1996, about half the model.
  * Proxy VAR: first-stage F 1.6 from 1996 and 0.2 from 1973.
  * Simulation: without the FCI the proxy VAR's median has the wrong sign (−0.07 against a truth of 0.33).
* **Credit.**
  * The EBP now enters with IP, as in robustness test R2: u24 +0.37, P24 −0.51.
  * Baa: u24 +0.27 (not significant), P24 −0.61.
  * Without the FCI, adding the EBP turns u24 positive (+0.25 against −0.33).
* **Timing.** Nominal and real only. Tracking the timing adds 0.32 and 0.24 to u24 with the FCI, and 0.00 and −0.14 without it.

## 5. Robustness
* **The six tests (D6),** in a table with real and nominal panels, at 12 months:
  * 2020 left in;
  * EBP and IP added;
  * the Bauer–Swanson surprise;
  * 6 lags;
  * without the funds rate;
  * monthly equations from 1985.
* **The summary paragraph is organized by magnitudes.**
  * From 1996, u12 is 0.12 to 0.37 around 0.33, and P12 −0.07 to −0.30 around −0.27.
  * The clearly smaller responses are named: the 1985 start, and unemployment with 2020 left in from 1973.
* **New paragraph on the 1985 start:** the weakest test (u12 +0.12, P12 −0.07). Both baselines bracket it.
* **Ending in 2019:** from 1996, P24 is +0.16; from 1973, −0.42.
* **Removed:** Kiley r*, the old spline-as-robustness, IP alone, and the funds rate as an extension (it is now the baseline).
* **Moved:** the 1-year yield goes to the appendix.

## 6. Slow-Moving Rates and Financial Conditions (new, D11)
* **The spline fits a large share of the variance** (percent; from 1973 / from 1996):
  * real FCI 92 / 32;
  * real two-year yield 75 / 63;
  * real funds rate 58 / 51;
  * unemployment gap 37 / 55.
* **Relative to r\*:** a linear trend explains 60 percent of the variance of the real FCI since 1973 against 27 percent of the version relative to r*.
* **Since 1996 the spline fits more of the r\* version (56) than of the real version (32).** The author's premise holds from 1973; since 1996 the data say the opposite, and the text says so.
* **The r\*-gap step:** u24 +0.49 and P24 −0.81 from 1996; +0.39 and −0.75 from 1973.
* **The spline:** from 1996, u24 +0.32 and P24 −0.20, not significant; from 1973, +0.37 and −0.50, significant at 5 percent.
* **Further work:** one paragraph with two readings, ending on better measures of r* and of the neutral level of financial conditions.

## Conclusion
* The mechanism paragraph drops the ordinary-day ratio.
* Variance shares are now about 5 percent of inflation.
* The durable finding is now about 0.7 pp and 0.4 percent, with nominal or real rates.

## Appendices
* **Lag length:** 6 and 12 lags. At 6 lags, two significant falls in unemployment, both in the nominal version from 1973 with 2020 left in.
* **New "Further Tests":** ends 2019, Baa, the JK surprise, the 1-year yield.
* **New figure:** paths from 1973 (`fig_steps73`).
* **Removed:**
  * the per-panel tables for the components;
  * the weights tests;
  * `tab_weights4`;
  * the "three-component specification" and "ordinary movement" paragraphs of the construction details.
* **Data table:** the federal funds rate is a main series; Kiley r* is removed.
* **Unchanged:** the toy model, the relation to a monthly VAR, the bootstrap appendix (now nominal and real), the direct projection (real controls) and the persistence appendix (rewritten for the new 5-day result).

## Open for the author
* **Section 2.1 keeps one sentence of the ordinary-day logic, in words** ("financial conditions move with them by much less"), because it is the reason a rates-only model carries a surprise as an ordinary move. Cut it too if FS-A86 was meant to remove the idea as well as the exhibit.
* **The "two readings" paragraph of Section 6** is my framing of "further work" [inference]; the author may prefer a shorter version.


## After the research review of 19 Nov 2026 (FS-A91 to FS-A116)
* **Abstract and introduction:** abstract about 115 words, no results numbers; the four-conclusion list is deleted (its content is in the paragraphs before it); the roadmap has no results; "interest rates alone" replaced by "through interest rates, at most with a credit spread"; "What is new" states the difference from Gertler-Karadi and Caldara-Herbst.
* **Section 2:** the ordinary-day sentence ("financial conditions move with them by much less") is gone (the Section 2.1 item under "Open for the author" above is resolved: rates alone can work in principle, an empirical question; simulation result); funds-rate impact described as MP1 (surprise to the rate set at the meeting, GSS scaling); monetary-event windows and the SOFR switch stated; the real window impacts assume expected inflation does not move in the window; expected inflation before 1982 documented (Livingston, 1-year proxy for all horizons, the 0.16 step in 1982); the broad policy-direction measure and its backcast are stated in Section 6.
* **Section 3:** paired differences in Table 4 (the appendix duplicate is dropped); Figure 4 deleted; the Barnichon-Mesters paragraph simplified; horizons named for the 1973 unemployment shift.
* **Section 4:** credit on the Baa spread and industrial production (matched, paired), the excess bond premium removed; timing: the gain comes from the daily dynamics, not calendar position; recovery of the surprise from monthly innovations stated correctly (direction, leads, no non-invertibility claim).
* **Section 5:** the index restriction (components free) and the GS weights are rows of the robustness table; Section 5.3 reports the restriction test; "IP added" replaces "EBP and IP added".
* **Section 6 (new place, after robustness):** the variance shares and the history; "announcement surprises" and "surprises in the policy direction"; the history read in changes (Volcker, 2020s).
* **Section 7:** three r* estimates (Table 13).
* **Appendices:** the bootstrap appendix describes the bias-corrected intervals and the weights sensitivity; the further-tests table has matched Baa rows and the 1-year units; the direct projection excludes 2020 inflation from price outcomes.
* **Throughout:** bias-corrected percentile intervals; "Two rates alone" / "Two rates and FCI" labels; 31 appendix pointers rewritten as a sentence plus a footnote.

## After the second review, 20 Nov 2026 (FS-A118)
* **Sacrifice-ratio sets by direct inversion** (Table 5 and the appendix table: multiplier, cost and its set); the nominal version from 1973 has a bounded cost (about 0.9, set -0.06 to 3.1), not "undefined".
* **Introduction:** "The signs are the same in nearly every test."; the three-year cost against Barnichon and Mesters; the daily block's contribution (0.16 monthly against 0.40 daily). **Conclusion:** the 0.90 is the contribution of surprises in the policy direction, with the two sensitivities.
* **Sections 5.2 and 7:** the paired difference for the sample ending 2019; "the responses have the same signs under both treatments".
