# Note A: report for review (12 Nov 2026)

Paper: "Reading Financial Conditions in Units of Monetary Policy" (`fci_paper/paper/fci_paper.pdf`, 34 pages, main text about 22). Package: `fci_paper/replication/` (steps 00 to 24, `run_all.py`, sync check passing on 187 result files). Decisions and logs: `fci_paper/FP_QA.md` (FP-A27 to FP-A40).

## 1. What the paper now says

Question: how many points of monetary policy is a movement in financial conditions worth? Two calibrations answer it. The market-implied reading weights the 10-year yield, equity valuation and the real dollar by their responses to policy news in FOMC windows. The spending-equivalent reading weights them by their GDP effects in FRB/US. The paper's conclusion is that the conversion into policy units is identified up to a band.

| Finding | Number (source) | Status |
|---|---|---|
| Typical policy response, spending-equivalent reading | 0.954 funds-rate points [0.85, 1.07], persistent paths; 0.82 at half-life 4; 0.37 to 0.95 across horizons 2 to 8 quarters and paths; 1.77 for the model's own policy shock | scale is a measurement choice |
| Dollar-over-equity, model vs market (ratio of ratios) | 2.53 [1.04, 6.91] futures factor; 1.22 [0.52, 3.05] two-year yield; 3.70 through 2019; 2.16 no lower bound | direction in point estimates only; interval excludes 1 for the baseline only |
| Same contrast in points (model less market) | 0.24 [-0.01, 0.44] baseline; 0.11 [-0.07, 0.29] two-year; 0.35 through 2019 and 0.23 no lower bound (both exclude 0) | metric and ratio disagree on which definitions are "significant" |
| Size of disagreement | mean abs D / mean abs market move 0.33 (12-month, 1996-2026); 0.19 intraday; 0.36 to 0.42 other definitions | about the size of market-weight noise: 0.26 [0.08, 0.54] (bootstrap), 0.37 baseline vs two-year market weights |
| 1998-2001 (12-month changes) | market -0.06 [-0.37, 0.30], spending +0.16 [0.14, 0.18], D +0.22 [-0.16, 0.54]; dollar part of D 0.16, equity 0.05 (intervals include 0) | opposite signs in point estimates under all four definitions |
| 2022-24 | market 1.02, spending 1.01, D -0.01 [-0.28, 0.27]; equity -0.10 and dollar +0.11 offset | offset holds under futures-factor definitions only; two-year signal gives 1.21 vs 1.04 |
| Outcomes | composition not significant for unemployment or GDP under any definition; model restriction rejected for unemployment after 1996 | low power: the market index does not predict unemployment after 1996 |
| Net exports (predicted from channels) | D coefficient -0.74 [-1.06, -0.41] (1976-2026); -0.54 through 2019; -0.24 no lower bound; +0.02 two-year | equity-driven (D correlates 0.86 with equities, 0.31 with the dollar; equity part -0.97, dollar part -0.52); dollar's own coefficient -0.030 [-0.050, -0.011] |
| FRB/US channels | equity effect: consumption 92%, business investment 27%, net exports offset -33%; dollar effect: net exports 94% | stylized partial experiments, rule inactive |

## 2. What changed since your last review

1. Title changed as requested.
2. FRB/US package obtained and made reproducible (step 00; Python 3.11 venv built automatically). One vintage (Board data of 6 Oct 2026) now sits behind every FRB/US number. Effects: 0.975 -> 0.954, 2.49 -> 2.53, Figure 1 effects 0.158/0.392 -> 0.153/0.384. No asserted claim failed. Old files kept as `*_oldvintage.csv`.
3. Reframing after the 1.2 result: Figure 1 now shows the market-implied reading under both policy-news definitions; the signal table moved to Section 3.2; abstract, introduction and conclusion lead with the band; episodes are shown under every combination of measurement choices (band figure).
4. New analyses: FRB/US policy-rate experiment (step 22); weights by persistence; null benchmark for D; composition tests under each definition; net-export split by asset (steps 22 to 24).
5. Two independent referee reads (JME-style coherence; REStat-style econometrics). Their findings, all incorporated: ratio of ratios is unstable (denominator near zero), so the paper now leads with the contrast in points; the 1998-2001 attribution to the dollar is a point-estimate statement; one false sentence on the 2022-24 forecasts was fixed; the net-export result is not evidence for the dollar channel; the abstract and conclusion state the low power of the activity tests.

## 3. Things you should decide or check

- **How far to lean on the band.** The honest headline is a sensitivity result. The paper does not say which definition of policy news is right. If you want a position, it needs a new argument (the two-year yield carries maturity-specific variation that moves yields and the dollar and not equities: interpretation, not shown).
- **Policy-rate experiment.** The two-year proxy (eight-quarter average of the simulated funds rate) is my construction, and stock wealth falls 31% on impact per unit. I report the 1.77 vs 0.95 comparison with caveats. A different proxy changes the unit. You may prefer to keep this to the appendix.
- **Net-export section.** The prediction was written from the channel logic after the aggregate nulls were known. It is described that way. Consider moving the section to an appendix.
- **Open from referees, not done:** 5,000 bootstrap repetitions (the baseline ratio-of-ratios lower bound of 1.04 is within Monte Carlo noise of one); alternative surprise measures (target and path factors); a second spending-side model; propagating generated-regressor uncertainty into the Section 6 regressions.
- **Pre-existing:** Note B edits undecided; unverified items (Sack-Swanson, Powell quotes beyond the two cited, Batini-Turnbull, the title "FCI-plot", vintage and real-time inputs) remain on the lists in `FP_QA.md` and `data/SOURCES.md`.

## 4. Verification status

- Sync check: 187 stored result files reproduce; all asserted claims hold; all macros resolve [verified, 12 Nov, after the last code change].
- Both referees re-derived headline numbers from the stored CSVs and found agreement (ratio of ratios, episode readings, band ranges, net-export coefficient, disagreement ratio) [verified by the referees; I verified the final build resolves with no undefined references].
- Text claims are written to the tables as of the last build; the referee reads were of the version before the final round of edits, so a short fresh read of the last version has not been done.
- Not verified: the t-statistics on signal content (-2.2, 0.2, 8.5, 4.9), the 45% residual share, the 12 blocks of the restriction tests (from earlier steps; produced by the package scripts, not re-derived independently).
