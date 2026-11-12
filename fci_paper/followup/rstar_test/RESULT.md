# Does measuring conditions relative to the neutral rate improve what an index says about the economy ahead?

**Design (pre-specified, run once).** Seven families, each nominal, real and r*-gap (market level and forward impetus, GS, FRB/US level and growth impetus, FCI-G 1- and 3-year); NFCI, ANFCI as references. Outcomes at 6, 12, 24 months: unemployment gap, payroll growth (log PAYEMS), real GDP growth (GDPC1, quarterly), core PCE; plus recession within 12 months (USREC logit). Regressors: the current reading plus the outcome's own lag; Covid months dropped. 13 outcome-horizon cells x 7 families = 91 tests per contrast; primary contrasts r* vs nominal and r* vs real (182), real vs nominal secondary. Tests: Diebold-Mariano on recursive out-of-sample squared (Brier) loss from 1995 (HAC), in-sample adjusted-R2 (log-likelihood) difference with a 90% block bootstrap (24 months, 500 draws), Clark-West against own lags. The package's unemployment results are reproduced (gain 0.113, ratio 0.890). Five recessions (1980, 1981-82, 1990-91, 2001, 2007-09); 2020 is in the Covid exclusion. [verified]

**Numbers** (positive = r* better; ratios are RMSE of r* over the other step, Brier for recessions).

| | r* vs nominal | r* vs real | real vs nominal |
|---|---|---|---|
| OOS ratio < 1 | 69 of 91 | 80 of 91 | 53 of 91 |
| DM \|t\| > 1.645 (r* better / worse) | 20 (18 / 2) | 15 (13 / 2) | 14 |
| in-sample interval excludes 0 (+ / -) | 13 (9 / 4) | 5 (4 / 1) | 15 (10 / 5) |
| chance at 10% | 9 | 9 | 9 |

By outcome, r* vs nominal (mean ratio; mean DM t): payroll 0.954, 1.56; GDP 0.981, 0.83; unemployment 0.978, 0.42; core PCE 0.994, 0.35; recession 1.027, -0.50. Against real: ratios 0.98-0.99, mean t 0.8-1.3. Smallest p is 0.0008 (GS, core PCE, 24 months; its in-sample interval contains zero); Holm at 5% leaves no test. [verified]

**By episode** (r* vs nominal, mean RMSE ratio): payroll flows gain in 2008-16 (0.93) and 2021-26 (0.87); payroll levels gain before 2008 (0.92). Unemployment: gain only in 2008-16 (0.95), loss in 2017-19 and 2021-26 (1.11, 1.07). Recession: loss from 2008 on. Gains are 2-5 percent of RMSE and sit in 2008-16, not 2022-24. [verified]

**Other.** Against own lags the indexes add clearly for payroll and unemployment, little for GDP and core PCE, nothing for recessions (all 21 logits have Brier above the baseline). NFCI and ANFCI beat every common-basis index for unemployment (RMSE ratio 0.77-0.91, CW t about 2) and for recessions (Brier ratio 0.87-0.95), but not for payrolls or GDP. [verified]

**Verdict.** No detectable difference between r* and real or nominal in any single test that survives a multiple-testing correction. The pattern leans toward r*: it has the lower error in 69 and 80 of 91 comparisons, most clearly for payroll growth, and rejections against nominal are twice the chance count. The tests share data, so counts are descriptive. For recessions r* is no better (five recessions). Real vs nominal: no difference for unemployment or core PCE. [verified for counts; inference for the lean]

**Recommendation.** Yes, as the paper's one question: "Does measuring conditions relative to neutral change what an index says about activity ahead?" Answer: small same-signed gains for payrolls, GDP and unemployment (2-5 percent of RMSE), not significant after correction, nothing for core PCE or recessions. One table (counts, mean ratios by outcome) and one episode figure replace the appendix tables. Frame the r* step as justified by theory and consistent with, not proved by, outcomes; replace the "only evidence" wording in Section 5.5. Open with the literature that validates indexes by fit (FCI-G, GS, NFCI) and the neutral-rate argument (Dudley, FCI-star), then this test; state NFCI's better fit as a fact. [inference]

Code: `run_all.sh` (run_tests.py, summarize.py, common.py); outputs in `out/` (paired.csv, vs_baseline.csv, subperiods.csv, summary.txt).
