# Note B: review for density and ease of reading (12 Nov 2026)

Read: `mp_transmission.pdf` main text (Sections 1-6, about 12,500 words; appendices not reviewed). Compared with Kiley, "Financial Conditions and Economic Activity: Insights from Machine Learning" (FEDS 2020-095) and "Monetary Policy, Employment Shortfalls, and the Natural Rate Hypothesis" (FEDS 2024-032). The published JMCB version (doi 10.1111/jmcb.70067) is behind Wiley's paywall and could not be fetched, so the comparison is with the working paper [not checked against the published text]. No change was made to the paper by the review itself.

**Status (12 Nov 2026): the author answered yes to all four questions and asked for all issues to be addressed; applied in FS-A68 (see `../FS_QA.md`).**

## Verdict

The suspicion is right, with one refinement. The draft is dense in two different ways, and it is also repetitive and over-qualified in a few identifiable places. Fixing the second pays for fixing the first, so the paper need not get longer.

1. **Dense in the prose.** One claim per sentence has been applied so strictly that many paragraphs are lists of facts with no connecting words. The reader must supply "so", "because" and "which matters since". The author's own papers do not read this way. They use medium-length sentences with connectives ("As a result", "In contrast", "Recall that", "It turns out"), and each result is followed at once by what it means and whose work it agrees with.
2. **Dense in numbers.** Several paragraphs carry six to ten numbers (introduction paragraph 3; Section 2.2 on the Goldman comparison; 2.3 second fact; 3.2 second paragraph; 3.4 "Two points qualify this").
3. **Repetitive.** The same four results appear in the abstract, introduction, body, discussion and conclusion, often in the same words.
4. **Caveats in the wrong place.** The abstract, the introduction and the conclusion each end on a qualification. Three checks (3.3, 3.7, 3.8) sit between the main result and its policy meaning.

## What the two reference papers do that Note B does not

- **Open results sections with the message.** ML paper, Section 3: "The central results ... are two-fold. First ... Second ... The following subsections take these points up in turn." Note B's Section 3 opens with a paragraph of quotations from Ramey (2016) and four sample periods.
- **Interpret each result where it appears, and tie it to the literature there.** ML paper: the term-spread result is followed in the same sentence by "consistent with research emphasizing the slope of the yield curve in recession prediction such as Engstrom and Sharpe (2019)". Note B puts the literature in Section 1.1 and reports results in Section 3 almost without it. After Table 3 there is no sentence that says whether 0.5 percentage point of unemployment per point on the two-year yield is large or small relative to earlier estimates.
- **Explain by a worked case.** Shortfalls paper, introduction: "Consider optimal policy for this loss function following an aggregate supply (cost-push) shock ..." and then five sentences of consequence. Note B has two passages of this kind (the ordinary day against the announcement day in 2.1; earnings news against a discount-rate move in 2.4). They are the clearest in the paper. There should be more like them.
- **Say why a choice was made at the point it is made.** ML paper: each variable group enters with a reason ("Equity prices are included as a widely watched indicator with clear macroeconomic interpretation"). Note B states the GLS weights, the 12 lags, the no-trend baseline and the Corsi daily block with little or no reason.
- **End on the implication.** Both abstracts end on what the result means. Note B's abstract ends on two sentences about the sensitivity of the price result.

## Repetition (counts from the main text)

| Statement | Times | Where |
|---|---|---|
| Sacrifice ratio, 0.9 percentage-point years | 7 | abstract, intro, 3.5 (several), discussion, conclusion |
| Price result "more sensitive"; "largely disappears" with dollar and long yield separate | 6 | abstract, intro, 3.6, discussion, conclusion |
| Unemployment shift of 0.6 whatever the yield measure | 5 | abstract and conclusion in identical sentences; intro; 3.2; discussion |
| From -0.07 to 0.50 and from 0.44 to 0.81 | 3 | intro, 3.2/Table 3, discussion |
| Why measure relative to r* | 3 | intro (third feature), 2.1, 2.2 |
| Timing assumptions and how the response is traced | 4 | Table 1; "The window / The day / The month"; "Three steps"; "How the responses are computed" |
| Goldman index weights listed | 2 | 2.2, first paragraph and "The nominal version", same words |
| Monthly VAR as the first-day special case | 2 | 2.5 "Structure" and "Relation to a monthly VAR" |
| Sample of 369 months from January 1996 | 3 | 2.5 "Estimation" and "Data"; table notes |
| Wrong-signed results of standard methods after the early 1980s | 3 | intro paragraph 1, 1.1 last paragraph, 3.1 first paragraph |
| "Effects of surprises, not a decomposition of any episode" | 2 | discussion, last sentence of the paper |

## Caveats that interrupt the message

- **Abstract, last two sentences.** A reader who has not seen Section 3.6 cannot parse "when the dollar and the long yield enter separately". Proposal: one clause ("the price response is less robust than the unemployment response"), and end on the policy reading.
- **Introduction.** "A monthly benchmark gives the subsequent dynamics a larger role (Section 3.4)" qualifies a result one sentence after stating it. The paragraph "Two sections test the results" gives the price-sensitivity detail again.
- **Section 2.4, last paragraph** ("A yield-only model is not wrong by construction. My claim is narrower ..."). Defensive, and it ends on a forward reference. It belongs, shortened, where the proxy VAR is estimated.
- **Section 3.4, "Two points qualify this."** Six numbers of qualification directly after the main explanation of the paper. Move to robustness or a footnote.
- **Section 3.5.** "It is not the cost of a permanent one-point decline in annual inflation, and it differs from the three-year ratio of 1.1." Table 7 shows "undefined" in five of eight cells.
- **Section 3.8.** A check whose conclusion is that it is uninformative. One sentence in Section 4 and the appendix would do.
- **Conclusion.** Ends on "not a decomposition of any episode". It should end on the durable finding and its policy reading, as the writing guide says.

## Where more explanation and motivation would help most

1. **Introduction, paragraphs 1-2: the stakes.** "The joint responses ... measure that cost at a stated horizon, along the path policy takes to lower prices" is cryptic. The Powell quotation arrives without a link. Suggested logic, in plain sentences: policymakers judge the stance by financial conditions and say so; the empirical evidence on the effects of policy traces it through one interest rate; that evidence says tightening does not raise unemployment; if so, either policy is weak or disinflation is very costly; the question is whether the evidence or the measurement is at fault.
2. **Introduction: the one fact that carries the paper.** A surprise that raises the two-year yield 1 point raises the FCI by 0.99; an ordinary 1-point rise comes with 0.28. This is the hook and it appears as a number only in Section 2.3. Give it in the introduction in place of the decomposition sentence and several of the other numbers.
3. **Section 2.2: why these weights.** One sentence of intuition for equation (3): an asset gets more weight when it responds strongly to policy news and moves little for other reasons. The weights table (Table 10) should sit here. It now floats to Section 3.7, where it is cited by mistake (line 352 of the .tex cites `tab:weights` for a statement about persistence).
4. **Section 3.2: read the main result for the reader.** (a) "Unemployment rises by 0.65, 0.57 and 0.56" reports differences but reads as levels. (b) Say why the yield relative to r* alone lowers prices but does not raise unemployment. (c) Add one paragraph placing the size of the responses against earlier estimates (an earlier draft had a Bauer-Swanson comparison; FS-A47). (d) Move the units sentence (0.92 to 1.01, "within about 8 percent") out of the opening paragraph into a note.
5. **Section 3.5: the payoff.** The comparison with the literature is two sentences. This is where the reader learns why to care. Relate the 0.9 to conventional sacrifice-ratio estimates and say what differs in the unit (price level at two years, not a permanent fall in inflation), once, as explanation and not as a disclaimer. The introduction says "one point of unemployment for one year" and 3.5 says "half a percentage point higher for two years"; use one.
6. **Section 3.3: pose the question before answering it.** The window-impact VAR and a simulation arrive in two paragraphs with no statement of what they are for. The question is simple: could a standard monthly proxy VAR with the FCI added do the same job? Say so, answer it, and send Table 5 to the appendix.
7. **Section 2.5, "The time trend".** The paragraph gives three reasons to include a trend and then says the baseline has none. The reason (the r* adjustment is meant to do that work, and Section 4.2 tests it) is missing.
8. **Section 2.1, "A second problem".** The omitted-variables paragraph (Sims; Fernández-Villaverde et al.) motivates misspecified dynamics, and Section 3.4 then finds that dynamics account for little. Cut to a sentence or drop.

## Structure proposal (for decision)

Section 3 has eight subsections. Three are checks. A reader meets the result (3.2), then a methods comparison (3.3), then the explanation (3.4), then the policy number (3.5), then three more checks. Proposed:

- **3 Results:** 3.1 standard methods (short); 3.2 baseline; 3.3 why the FCI changes the response; 3.4 the tradeoff.
- **4 Tests of the approach:** one index or three components (now 3.6); how long the movement lasts (3.7); monthly benchmarks (3.3); direct projection in a sentence (3.8).
- **5 Robustness** (as now). **6 Conclusion**, with the discussion folded in: the first two discussion points are the conclusion's content, and the third ("what the estimates do not show") is said in Sections 2.4 and 4.

Also: move the Phillips-curve paragraph of Section 1.1 to the tradeoff subsection, where the Barnichon-Mesters comparison already is; shorten the four-explanations paragraph of 1.1.

## Small items

- "somewhat larger" (Section 4.4) breaks the guide's own rule.
- Table 11 has a "Weights of the FCI" block with no matching subsection in Section 4.
- Section 3.1: the Anderson-Rubin sentence carries four citations in the running text; a footnote would do.
- A/B/C path labels in 3.4 are heavy in prose; names ("announcement movement", "ordinary movement", "yield alone") read more easily, with the letters kept in the table.

## Questions for the author (one at a time)

1. Abstract and conclusion: reduce the price-result qualification to one clause and end on the policy reading? (This revisits the decision recorded in the writing guide, Section 3.)
2. Adopt the Section 3/4 split above?
3. Fold Discussion into Conclusion?
4. Add the size-of-effects and sacrifice-ratio comparisons with the literature (needs a short, verified set of reference estimates)?
