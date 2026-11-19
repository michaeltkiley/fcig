# Plan for the research review of 19 Nov 2026 (Note B)

Review: `REVIEW_19NOV.pdf` (8 pp., "Financial conditions and monetary transmission"). It compares the Sunday draft (`mp_transmission.pdf`, the r*-gap text of 13 Nov) with the current draft (`mp_transmission_real.pdf`, 18 Nov). The reviewer did not have the estimation files. Their numbers are taken from the PDFs or are proposed re-estimates.

**How we use this file.** We take the items one at a time. For each one I give what the review asks, where it applies, whether it reverses an earlier decision of yours, my recommendation, and the work involved. Nothing is done until you approve an item. Each decision is recorded in `fin_shocks/FS_QA.md` as FS-A91 onward, and the outcome is noted here under "Decision".

**Where the review conflicts with your decisions.** Its headline asks reverse four of them: the ordinary-day comparison and the A/B/C split (FS-A81, FS-A86), the components test (D6 revised, D10), the four weight calibrations (FS-A87), and the alternative r* estimate (D5). These are flagged **[reverses ...]** below.

Checks I made on the current text before writing this plan: [verified] means checked in `mp_transmission_real.tex` or `.pdf`; [review] means taken from the review and not yet checked.

---

## Part 1. The four big decisions (the review's "Three decisions" plus history)

### 1. The ordinary-day comparison and the A/B/C split  **[reverses FS-A81, FS-A86]**
*Review (pp. 2):* The text says a model with rates alone carries an announcement forward as an ordinary rate increase. That is an empirical claim, and Sunday's Table 5 tested it: A = full model from the window impact, B = the same model from the ordinary-day FCI impact, C = rates only. Restore it in the real two-rate model with common draws. The ordinary FCI innovation is projected jointly on the 2-year and funds-rate innovations on non-announcement days and evaluated at (1, 0.72), with the slopes re-estimated in each draw. Hold both rate impacts fixed from A to B, label B−C as "state change plus re-estimated propagation", and put the monthly-loading sensitivity in a note. The 1996 results go in the text, the 1973 and nominal results in the appendix. Replace Figure 4 with this exhibit.
*Where:* Section 2.1 keeps the ordinary-day logic in words (FS-A90 point 1). `lib/model.estimate` still computes path B, but only with the 2-year (FS-A86).
*My view:* The review is right that the text makes a claim it no longer tests. There are two consistent ways out: (a) restore the test, or (b) rewrite the Section 2.1 sentences as economic intuition and make no empirical claim about an ordinary rate increase. Your reasons for dropping the split (it is not a standard VAR object, it depends on the horizon and on the benchmark) still hold. **Recommend (b).** As an option, I can compute A/B/C in `baseline_real/` as a record only, so we know the answer.
*Work:* (b) is a few sentences. Computing (a) means extending path B to a joint projection on two rates with per-draw slopes; that is half a day of code plus bootstrap time.
*Decision:*

### 2. The FCI-components test  **[reverses D6 revised, D10]**
*Review (p. 3):* Using one index at every lag imposes a restriction that the event-window weights do not test. In the Sunday r*-gap model, freeing all three components moved the 1996 price response from −0.72 to +0.06, a paired difference of +0.78 [0.44, 1.12], and joint proportionality was rejected for inflation (p = .041). Current Table G6 (ending in 2019) also shows the 1996 price response barely depends on the FCI. Refit the restricted, equities-free and all-free cases in one daily component system that includes both rates. Report the paired contrasts for both outcomes and both starts, and recompute the multiplier sets. One paragraph and one exhibit.
*Where:* Note A now has this test (Section 5.4, step 37, FP-A75), but on Note A's own model. In the r*-gap Note B, freeing all three removed most of the 1973 price response as well (FS-A81).
*My view:* This is the review's strongest point. The price result is the one exposed to it, and Note A's test is on a different model, so it does not answer the question for Note B. **Recommend: run it in `baseline_real/` first (the extension of `lib/model` to the funds rate with components, already scoped in D6), then decide whether the text gets a paragraph or a sentence that points to Note A.** If the price result survives, that is new evidence for the baseline. If it does not, the text has to say so.
*Work:* code extension and three cases × two starts × two versions with bootstrap: about a day.
*Decision:*

### 3. Placement of the historical exercise (Figure 5, Table 6)
*Review (pp. 1, 5):* Put the history after the tests of the transmission estimates. Keep the 0.90 pp 2021–22 number once, stated precisely (see item 15).
*Where:* the history currently sits in Section 3, before Section 4 (persistence, timing, credit) [verified: Table 6 and Figure 5 come before Tables 7–9].
*My view:* Reasonable. It lets the reader see the transmission evidence before an application that needs extra assumptions. **Recommend: move it to a short section after Section 5 (robustness), before Section 6 (slow-moving rates).**
*Work:* restructuring only.
*Decision:*

### 4. The Phillips multiplier stays prominent; define it earlier
*Review (p. 5):* Keep the multiplier as the policy reading and move the definition (current p. 19) earlier.
*My view:* Agree. **Recommend: define it in the introduction, in one sentence, where the trade-off is first mentioned.**
*Work:* small.
*Decision:*

---

## Part 2. Headline numbers and policy

### 5. Paired intervals in Table 4
*Review:* Put the paired 90% intervals into Table 4: [0.37, 1.04] for unemployment and [−0.82, −0.09] for prices; nominal shifts +0.75 and −0.44.
*Where:* the paired differences are now in appendix Table H8 [verified: H8 exists].
*Recommend:* yes. Add a "Difference" column with the interval, from the same draws.
*Work:* `07_report` change.
*Decision:*

### 6. State the horizon whenever the long-sample unemployment claim appears
*Review:* From 1973 the real unemployment response rises from 0.03 to 0.19 at a year, but the change at 24 months is only +0.08.
*Recommend:* yes. Audit every sentence about the 1973 unemployment shift and give its horizon.
*Decision:*

### 7. Barnichon–Mesters at three years
*Review (p. 5):* BM report about −0.15 at three to four years (1990–2008, high-frequency shocks). Our three-year multiplier is −0.61 [−1.23, −0.11], an implied cost of 1.6 [0.81, 9.09], and their point estimate (about 6.7 in cost terms) lies inside that set. Compare at three years in prose and keep two years as the preferred horizon. Note that the two studies differ in sample, shock, price measure and estimator.
*Recommend:* yes, after I check BM's numbers in the paper itself [review numbers, not yet verified]. Two sentences.
*Decision:*

### 8. Confidence-set geometry for the multiplier
*Review:* Where cumulative unemployment is near zero, report the actual set, which can be unbounded or disjoint, by inverting the test for unemployment/price directly. Add a 2019-end row to Table H9.
*Where:* the sets are "exact" (FS-A43). I will check whether they are already inverted for the ratio as reported.
*Recommend:* check first. If they are already inverted, add only the 2019 row and a note on the shape of the sets.
*Decision:*

### 9. Opening paragraphs
*Review (p. 7):* proposes a new opening (repricing within minutes; the same surprises through two models; the sign of the unemployment response changes; the price response depends more on the sample). It asks to drop the four-item list after the opening, because the matched estimate appears five times (opening, list, roadmap, results, last paragraph).
*Where:* the house style (CLAUDE.md, WRITING_GUIDE) puts the approach as First/Second/Finally features after the result. The four-conclusion list came from FS-A81.
*My view:* The proposed opening fits your style, except "the price response depends more on the sample". That is a hedge in the introduction, which your style rules out, unless item 2 or item 11 makes it a finding. **Recommend: cut the repetitions to one early estimate, one explanation and one policy reading; your call on the list; decide the price sentence after items 2 and 11.**
*Decision:*

---

## Part 3. Literature and model comparisons

### 10. State the novelty precisely
*Review (p. 4):* "the evidence ... traces a policy surprise through interest rates alone" (the abstract's first sentence [verified, l. 53]) overstates the gap: Gertler–Karadi trace credit costs and term premia, and Caldara–Herbst study spreads. The sharper claim is that the window fixes the initial rate-path direction and the experiment varies which financial prices carry it forward. Bring the p. 23 point (a valid instrument identifies the total response with the channels omitted) into the introduction.
*Recommend:* yes. Rewrite the abstract's first sentence and one paragraph of the introduction.
*Decision:*

### 11. Risk appetite: replace "carries the same channel"
*Review:* Bauer–Schmeling–Schrimpf and Boehm–Kim–Kroner can coexist with these results. Equities carry cash-flow news as well as discount rates, and the model cannot attribute the activity response to risk appetite. Replace "My index carries the same channel" [verified, p. 4] with a conditional claim.
*Recommend:* yes, one sentence.
*Decision:*

### 12. Bauer–Swanson comparison
*Review:* Their responses are a magnitude check, but a rough match does not isolate the effect of cleaning the surprise. The 201-event test changes only the initial direction, and the ordinary-data dynamics do most of the work.
*Where:* the text already compares magnitudes (Figure 8: +0.17 pp, −0.5% CPI) [verified, p. 18] and says "They obtain conventional signs by cleaning the surprise".
*Recommend:* soften that causal sentence to what the comparison shows, and describe the 201-event test as a change in the initial direction only.
*Decision:*

### 13. Timing comparison (Table 9)
*Review (p. 4):* The difference in differences, +0.38 pp (0.73 against 0.35), also changes the financial dynamics and the impact, not only the calendar timing. To isolate timing, use the same equations, impact, events and draws, change only the assumed weekday of the announcement (first day against a midpoint), and report the paired change. Reconcile the "end-of-month series" wording in Table 9's note with the monthly averages used since FS-A77.
*Where:* Table 9's note says "end-of-month series" [verified]. The benchmarks moved to monthly averages in FS-A77, so the note is out of date. The text's claim that "the financial channel is the larger one" [verified] rests on this table.
*Recommend:* fix the note (an error). Run the timing-only counterfactual: it is the clean test of a claim the text already makes. If the timing-only difference is small, credit the daily financial path in words.
*Work:* fix trivial; counterfactual about half a day.
*Decision:*

### 14. Credit comparison (Table 8)
*Review (p. 4):* Adding EBP and IP moves the rates-only unemployment response from −0.33 to +0.25, so the FCI's incremental effect falls from +0.73 to +0.12. "Neither credit measure changes the result" [verified, p. 22] misses that. Report the paired difference, separate EBP from IP in matched regressions, and note that the Baa row's rates-only cell is the baseline's, so that row has no matched comparison.
*My view:* The review is right, and this is substantive: credit and the FCI may carry overlapping information, which links to Caldara–Herbst. D6 put EBP and IP together for the robustness table; that can stay there.
*Recommend:* in Section 4, run EBP alone, IP alone and both, each without and with the FCI, plus Baa with its own rates-only case, all on common draws. Report the incremental FCI effect and its paired interval, and rewrite the sentence to say what the table shows.
*Work:* about half a day.
*Decision:*

---

## Part 4. Identification and data checks

### 15. Historical accounting: precision and labels
*Review (pp. 5–6):*
(a) Measured-surprise variance ratios (0.7% and 0.3%) and the projection of all daily innovations on the announcement direction (10.7% and 5.6%) are different objects. Ordinary-day innovations that line up with the window vector may be data or earnings news. Say so, and cite Plagborg-Møller–Wolf.
(b) Table 6's "of which on days without an announcement" is 12.6, above the total 11.6 [verified]. Relabel it, show the covariance, and say these are variance ratios, not an additive decomposition.
(c) Give the projection metric and formula, the scale factor, the denominator sample, and what the bands condition on.
(d) The 0.90 pp 2021–22 number: state it once, as the 1973 model's contribution from innovations aligned with the policy direction. Add a sensitivity with the March–December 2020 shocks set to zero and the measured-window contribution for the same dates.
(e) Label pre-1990 a backcast. Removing the scaling raises the variance ratios from 3.6% to 14.7% (inflation) and from 3.4% to 13.8% (unemployment); report that.
(f) Distinguish the date of an innovation from its later contribution (Volcker 1980–82).
*Recommend:* yes to all, with (b) first because it is an arithmetic presentation error. (d) and (e) are small new computations in `baseline_real/`.
*Decision:*

### 16. Direct-projection check
*Review:* Align the appendix direct projection (unemployment +1.15 [−2.74, 3.39] at 24 m) with the main specification: pandemic exclusion, lagged funds-rate control, event sample.
*Recommend:* yes. Rerun it aligned and report it plainly in the appendix.
*Decision:*

### 17. Appendix E scenarios
*Review:* The 66-day FCI estimate is 0.67 against the model's 0.66, with interval [−0.10, 1.52]. Scaling the path to those endpoints gives unemployment from −0.11 to +0.98 and prices from −0.10% to −0.94% at 24 m. Add one sentence in Section 4.1 saying these are conditional scenarios.
*My view:* The fact is fair. But it needs to be stated as a fact (the direct estimate matches the model; the interval is wide) without hedging the result.
*Recommend:* one sentence, after I reproduce the numbers.
*Decision:*

### 18. Monthly recovery (Appendix B1): regression direction and wording
*Review:* B1 regresses the measured surprise on monthly innovations, but the text (pp. 13 and 40) describes the reverse regression. With six leads, R² rises from 1.2% to 19.5% (p = .18) from 1996 and from 0.2% to 20.0% (p = .02) from 1973. Describe this as weak contemporaneous recovery of a noisy proxy, not proof of structural non-invertibility.
*Recommend:* check the direction in the code and fix the text to match; report the leads result; reword the claim to what the regression shows.
*Decision:*

### 19. Expected inflation before 1982 (Livingston)
*Review:* Livingston's 10-year question began in 1990. Document how the pre-1982 2- and 10-year proxies are built and spliced to Cleveland, and which horizon deflates the funds rate. An alternative early series and a 1982 start would be useful, because the long-sample price result depends on deflation.
*Recommend:* document it in the data appendix (from the code, [verified] when done). Run the 1982 start in the baseline model as one appendix test. An alternative early long-run series only if you want it.
*Decision:*

### 20. Window inputs
*Review:* Say whether equation (7) uses raw FF1 or MP1 (adjusted for meeting timing). Verify the mapping into the daily effective-rate impact, its month-end convention, and the 0.72 estimate. The USMPD has distinct statement and monetary-event windows and switches from Eurodollar to SOFR contracts. Correct the blanket "30-minute" label in Table 1 [verified, Table 1 notes]. State that the real window impacts assume no contemporaneous response of expected inflation.
*Where:* FS-A89 says MP1.
*Recommend:* yes to all. Check in the code which USMPD window and which contracts are used, then fix Table 1's note and add the assumption sentence.
*Decision:*

### 21. Audit of labels and samples (G6, Baa, normalization)
*Review:* G6 calls the Baa model r*-gap; Table 8 calls it real. The long-sample Baa row has 467 observations against 623 for its comparator. G6's one-year normalization needs reconciling with Appendix G.
*Recommend:* audit and fix. The 467 observations are probably the start of the Baa daily data; if so, state it and use a matched comparator.
*Decision:*

### 22. Bootstrap conditional on the weights
*Review:* The intervals hold the FCI weights fixed. Label them as conditional on the weights and, if feasible, add one paired sensitivity that re-estimates the weights in each draw.
*Where:* `fci_paper/` already has a bootstrap of the weights (Note A).
*Recommend:* label yes. The weights-in-the-draw sensitivity is your call; it is feasible by reusing Note A's code.
*Decision:*

---

## Part 5. Structure and wording

### 23. Alternative neutral-rate estimate in the appendix  **[reverses D5]**
*Review:* If levels relative to r* keep quantitative prominence, Sunday's alternative r* (Kiley) belongs in an appendix row.
*Recommend:* keep D5. In the current text r* is in Section 6 as an open question, not prominent.
*Decision:*

### 24. The four weight calibrations  **[reverses FS-A87]**
*Review:* Bring back one appendix table on current inputs (Sunday: +0.46 to +0.63 across market, FRB/US and GS weights). It shows the result travels beyond the companion paper, a different question from item 2.
*Recommend:* your call. My lean is to keep FS-A87 (it belongs to Note A), unless item 2 shows that the price result depends on the index restriction, in which case the calibrations become relevant.
*Decision:*

### 25. Figure 4
*Review:* Figure 4's real panels repeat Figure 1's left side. Its nominal comparison can go into Table 4.
*Recommend:* check the overlap. If it is real, drop Figure 4 and add the nominal rows to Table 4 (with item 5). Whether a mechanism exhibit replaces it depends on item 1.
*Decision:*

### 26. Wording audit
*Review:* Use "the two rates" consistently. Replace "in every robustness test" with the sample and horizon. Say that EBP and IP enter together. Make the §2.3 sentence on credit and expectations name the variables §4.3 adds. Replace "determines the estimated employment consequences" with the measured change. Throughout, distinguish changes in point estimates, paired differences and significant differences.
*Recommend:* yes, as one pass at the end, with a claim in `claims_real.py` for every changed number.
*Decision:*

### 27. Review's order of work
*Review:* (1) reproduce Table 4 and H8, carry the paired comparison to both starts and the 2019 end, reconcile the rate inputs; (2) components and the initial-movement split; (3) applications, variance arithmetic, the three-year benchmark; (4) Figure 4, introduction, label audit.
*Recommend:* the same order once the decisions are made, with errors first (items 13 note, 15b, 18, 20, 21).
*Decision:*

---

## Order in which I propose we go through the items
1. Items 1–4 (the decisions that set the shape of the revision).
2. Items 13, 15, 18, 20, 21 (errors and labels in the current draft).
3. Items 2 (if approved), 14 and 13's counterfactual (new estimates, which may change the text).
4. Items 5–12 and 16–17, 19, 22 (headline, policy, literature, checks).
5. Items 23–26 (structure and wording), then item 9 (the opening) last, once the results are settled.
