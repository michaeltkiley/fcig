# Note B: changes for the merge (18 Nov 2026)

`mp_transmission_session_integration.tex` against your last committed version, `mp_transmission.tex` (commit 2578e4a, FS-A74). If you have edited `mp_transmission.tex` offline since then, merge by diff: the copy changes the sections listed below and leaves the rest word for word. Decisions: `../FS_QA.md` FS-A75 to FS-A82. The copy compiles cleanly (pdflatex + bibtex, 78 pages, no errors, no undefined references or citations, no overfull boxes); the PDF is `mp_transmission_session_integration.pdf` next to it. Run `python3 check_paper.py <file>.tex` after merging; it checks that every number macro, table input, reference and citation resolves.

## What changed in the model and data (drives the numbers)
1. **Own factor scaling and weights (FS-A75).** The policy-news factor and the index weights are estimated on Note B's 252 announcements with a constant in every regression. Weights 0.62 / -0.052 / 0.066 (were 0.61 / -0.051 / 0.065); the window loading is exactly 1 (was 0.99). The other three calibrations are rescaled to window loading 1.
2. **Two baselines.** Monthly equations from 1996 (as before) and from 1973 (new, a second baseline, not a robustness row). The daily block, announcements and window impacts are the same in both.
3. **March to December 2020 dropped in every estimation** (was: in). This applies to both blocks, all benchmarks (Cholesky, proxy, window-impact VARs, simulation) and steps 09 to 12. Keeping 2020 in is now a robustness test.
4. **Monthly averages everywhere.** The end-of-month series are gone; the benchmark VARs use monthly averages (reverses FS-A48).
5. **Robustness from both starts**, reported at 12 months (FS-A78). New tests: industrial production as a third monthly variable, the funds rate in the daily block, the 1-year yield in place of the 2-year.
6. **Decompositions (new Section 3.5):** variance shares and historical contributions of measured surprises and of daily policy-direction shocks.
7. **Bug fix (FS-A81):** the 1973 component cases had financial conditions of zero before 1990. Fixed; only the 1973 component results changed.

## Headline numbers, old to new (r*-gap with the FCI, from 1996, 24 months)
| | Old (2020 in) | New (2020 out) |
|---|---|---|
| Unemployment (pp) | 0.49 | 0.45 |
| Price level (%) | -0.80 | -0.69 |
| Shift from adding the FCI, unemployment | about 0.6 | 0.62 / 0.57 / 0.66 (nominal / real / r*) |
| Ordinary-day vs window ratio | 3.6 | 3.5 |
| Sacrifice ratio, 24 m | 0.9 | 1.1 (0.7 from 1973) |

New from 1973: price level -0.76 percent at 24 months, unemployment +0.33 pp at 12 months.

## Section by section
- **Abstract.**
  - Adds the price shift (about a third of a percent) and the 1973 result (same price fall).
  - Drops "started with an ordinary day's movement ... almost no unemployment response" (FS-A81).
  - Adds the share of fluctuations (policy-direction movements explain about a tenth of inflation).
- **Introduction.**
  - The result paragraph gives the matched shifts for all three versions.
  - New paragraph on the 1973 picture: the yield alone already has conventional signs and the FCI enlarges them; the wrong sign belongs to the sample since 1996.
  - The ordinary-day counterfactual paragraph is removed.
  - Still four conclusions, but the set changed:
    1. Reversal: now all three versions, and "under every variation ... from either starting date".
    2. The r\* adjustment matters for prices: about 0.7 percent from either start.
    3. Sacrifice ratio about one.
    4. New: policy shocks are a modest source of fluctuations, with the history.
  - Your "mechanism" item is dropped (FS-A81).
  - The components footnote now says the price fall is smaller without the dollar restriction "in both samples".
- **2.2 The index.** FS-A75 method text: equation (ns) with a constant, the 252 announcements, a footnote on the companion paper's sample, the new weights.
- **2.3 One rise, two days.** "One by construction". The sentence relying on the A/B/C split is replaced by: a yield-only model learns from data in which a rise in the yield brings little financial tightening, so it treats a surprise as an ordinary rise.
- **2.4 Timing.** Equation (impact) now equals 1, with the shorter explanation.
- **2.5 Model.**
  - Two samples (359 and 623 months) and the 2020 treatment.
  - New paragraph on invertibility: why the window design does not need it. The monthly invertibility diagnostic gives R² 1.5 percent and correlation 0.10; the simulation median is 2.2 percent.
  - Bootstrap blocks before 1996 in the 1973 sample.
  - Data paragraph: monthly averages everywhere.
- **Section 3 opening.** "Four results follow."
- **3.1 Standard methods.**
  - Both samples.
  - The proxy VAR is now in the window unit, with first-stage F statistics and Anderson-Rubin sets in a footnote.
  - From 1973 the Cholesky VAR gives conventional signs (+0.12 pp, -0.08 percent).
- **3.2 Baseline.**
  - Table 3 has 1996 and 1973 columns. The old paired-difference table moves to the appendix as `tab_matched_diff`.
  - Text leads with the matched shifts and their uniformity across versions.
  - New 1973 paragraph.
  - Figure 1 is a 2x2: both samples.
- **3.3 "Why Adding the FCI Changes the Estimated Response": removed** (figure `fig_decomp`, table `tab_decomp`; FS-A81).
- **3.4 Tradeoff.** Both samples: -0.95 and -1.49; sacrifice ratio 1.1 and 0.7 at 24 months, 1.2 and 0.6 at 36.
- **3.5 How Much Do Policy Shocks Explain? (new).**
  - Measured surprises explain under 1 percent of the 24-month variance.
  - Policy-direction shocks explain:
    - through the model from 1973: 8.9 percent of unemployment and 7.8 percent of inflation since 1990, and 11.8 and 10.1 percent over 1974-89;
    - through the model from 1996: 18.0 and 9.4 percent since 1990.
  - History figure `fig_decomp_hd`; appendix tables of shares, full results and diagnostics.
- **4.1 Components.**
  - Both samples now show the same pattern. Unemployment barely depends on the specification; freeing equities leaves the price response in place; freeing the dollar as well removes most of it (from 1996: -0.66 / -0.40 / -0.07; from 1973: -0.70 / -0.68 / -0.30).
  - The index-as-one-variable column uses the components' daily block and is close to the baseline; the text says why.
  - Weights tests give the same verdicts in both samples.
- **4.2 Four calibrations.**
  - Ranges from both starts.
  - Calibrations scaled to window loading 1.
  - Kept: the sentence that the weightings with higher ordinary-day loadings give smaller shifts.
- **4.4 Monthly benchmarks.**
  - Monthly averages.
  - The window-impact VAR gives the signs at about half the size; the simulation shows this is what monthly averaging does.
  - Proxy VAR first-stage F is 3.0 and 0.6.
- **2.1, the literature, 4.3, 4.5, 4.6:** text unchanged; their numbers update through the macros.
- **Section 5 Robustness (rebuilt).**
  - 12-month table for both samples.
  - From 1996, eight of ten tests give 0.33-0.46 pp and -0.22 to -0.43 percent; the departures are Kiley r\* and the spline trend.
  - From 1973, eight of ten give 0.18-0.36 and 0.20-0.38; the departures are 3 lags and Kiley r\*.
  - Subsections:
    - 5.1 The Sample (2020 in; ends in 2019).
    - 5.2 r\* and trends.
    - 5.3 Credit, the Surprise and Lag Length (replaces your "The Surprise and Information Effects" and "Lag Length" subsections).
    - 5.4 Further Variables (new: IP, funds rate, 1-year yield).
- **Conclusion.**
  - Same order.
  - The ordinary-day counterfactual is replaced by "a model that sees only the yield treats a policy surprise as an ordinary rise in rates".
  - Adds the shares paragraph and the 1973 agreement on prices.
- **Appendices.**
  - B, relation to monthly VARs: adds the invertibility diagnostics and the Monte Carlo.
  - D, lag length: counts over the core cases from both starts. Price falls in every case at 3 and 6 lags; weights-test verdicts by sample.
  - F, persistence: compares with the matched shift, no longer path A - C.
  - H, details: the ordinary-loading paragraph now only defines the daily loading.
  - Appendix tables now label rows by version only (the caption names the panel), which fixed three tables that ran past the margin; captions that began with a lower-case word are capitalized.
  - Tables: per-panel 3/6/12-lag tables only for the baselines and components (`tab_app_B73`, `tab_app_R4c73`, the monthly-73 tables). The R1-R3 and R4 per-panel tables are generated in `baseline/report/` but no longer input.

## If you rebuild your own file against the new numbers
`check_paper.py mp_transmission.tex` reports four unresolved items:
- `\bl{rob:upos}`, `\bl{rob:n}` and `\bl{rob:no_uneg}`, from the old robustness count, which the 12-month table replaced;
- `\ref{tab:matcheddiff}`, because your file refers to the paired-difference table but does not input it.

Taking the copy's Section 5 resolves the three macros. Adding the copy's appendix line `\input{../baseline/report/tab_matched_diff}` resolves the reference.
