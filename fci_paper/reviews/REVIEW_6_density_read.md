# Density and readability read (12 Nov 2026), revision d32ea6a

Reader: an agent given the PDF, the writing guide, the notes on the author's shortfalls working paper, and the two FEDS working papers it fetched (2024-032; 2020-095). The JMCB published version was not read. The report is the reader's own, unedited; it is model output, not the author's view. Suggested sentences marked [author to verify] or [inference] are unchecked.

# Density and readability read of `fci_paper.pdf` ("Reading Financial Conditions in Units of Monetary Policy")

Page numbers are the printed ones (PDF page = printed page + 1). No file was edited and no code was run, apart from text extraction and word counts in the scratchpad.

## Step 1: what I could and could not read

- **FEDS 2024-032 (natural rate paper):** read. WebFetch returned binary; I extracted the saved PDF with `pdftotext` and read the abstract, the introduction and Section 2 through the corollary (about the first ten pages). For Sections 3-4 I relied on `ev_jmcb.md`. Equations are garbled in extraction; the prose is clean.
- **JMCB 2026 published version:** not read. Everything below is about the working paper.
- **FEDS 2020-095 (machine-learning FCI):** read in full by the same route (abstract through conclusion). The figures were not viewed; the working paper has "INSERT FIGURE" placeholders.
- **`WRITING_GUIDE.md`:** read.
- **The draft:** printed pages i-19 read in full; appendices A to D.4 (to printed page 38) skimmed; Appendix E and the last pages not read.

What the two style papers do, concretely:

- **Motivation.** 2020-095 opens with the economics: "Equity prices influence household consumption through wealth effects; interest rates shape mortgage borrowing...". 2024-032 opens with the answer, then "Recent research and practice at central banks motivates the analysis."
- **Explanation per result.** Each result gets the same sequence: what the figure shows, why, and how it sits against the literature. Example: "The cyclical contrast owes to the latter difference... as is intuitive"; "consistent with research emphasizing the slope of the yield curve... such as Engstrom and Sharpe (2019)".
- **Numbers in prose.** The results sections of 2020-095 give almost no statistics in prose; the figures carry them.
- **Sentences.** Long, 27 to 32 words on average, held together by connectives.
- **Literature.** Cited at the point of use throughout, about 75 citations in each paper, as "in contrast to", "consistent with", "as in", "generalizes a result in".
- **What the reader is learning.** Said explicitly: "Three lessons... emerge"; "This result is the central new result"; "These results may inform discussions of monetary policy in several ways. First...".
- **Caveats.** One flat sentence where it arises, or a late section ("Robustness", "Additional considerations"), each with the direction of the effect. None in the abstract.
- **Repetition.** Abstract, first paragraph of the introduction and conclusion restate one another. Within the body, a result is stated once and referred back to by number or with "Recall".

## 1. Overall verdict on density

The draft is denser than both style papers, but not through long sentences: its sentences are shorter than his. The density has three sources:

- statistics in the prose of Sections 3-5;
- almost no connective words, so short declaratives stack and the reader must supply the logic;
- an abstract vocabulary ("reading", "calibration", "portfolio", "remainder") that carries the argument without being fixed.

It is also thinner than his papers on why each exercise is done and on the literature after page 4.

| Measure | Draft | 2020-095 | 2024-032 |
|---|---|---|---|
| Average sentence length (words) | intro 20; Sec. 2 22; Sec. 3 25; Sec. 4 24; Sec. 5 22 | intro 31; results 29; robustness and conclusion 27 | intro 32 |
| Numerals per 100 words | intro 4.0; Sec. 2 1.9; Sec. 3 8.3; Sec. 4 10.9; Sec. 5 13.3 | 3.0 to 4.5, nearly all citation years and figure numbers | intro 4.0, nearly all citation years |
| "As a result" | 0 | 3 | 6 |
| "In contrast" | 0 | 8 | 5 |
| "For example" / "e.g." | 0 | 31 | 23 |
| "That is" / "i.e." | 1 | 11 | 16 |
| "However" | 0 | 7 | 3 |
| "Recall" / "Note that" | 0 | 8 | 3 |
| Citations in the text | about 45 in Sec. 1.1; 7 in Secs. 2-5 (four distinct works) | about 75 throughout | about 72 throughout |

The draft's main text is about 9,300 words; the two style papers are 6,700 and 5,700.

Paragraph openings are not the problem. In Sections 4.2-4.5, 12 of 15 paragraphs open with the idea, not a number. The load comes in sentences two to five: seven of those 15 paragraphs carry seven or more statistics. Examples are "One asset dominated the movement" (10), "The sign of the reading then depends on the weights" (10) and "Direction." (13).

## 2. The densest passages

1. **p. 1, Sec. 1, "Figure 1 states the puzzle."** Thirteen sentences define four calibrations, two sizes in "log points", the design of the figure and the result. "Equity valuation" and "log point" are undefined here.
 - Split into two paragraphs: what the four calibrations are, then what the figure shows.
 - Replace "a 5 log point fall in equity valuation and a 3.9 log point appreciation of the dollar" with "a 5 percent fall in stock prices and a 4 percent appreciation of the dollar".
 - Add after the result: "Two indexes that both claim to measure financial conditions in units of policy can therefore differ by a factor of two on which of these movements is the larger tightening."

2. **pp. 1-3, Sec. 1, "The second answer has two parts that the data can trace."** The sentence "the part of the two-year yield change that the futures factor misses moves long yields and the dollar and leaves equities unchanged, so a market index built to recover the two-year yield gives equities about half the weight" skips the step that makes it true.
 - Add: "An asset earns weight in a market-based index by tracking policy news closely. Equities track the news in near-term futures closely. They do not respond to the rest of the two-year yield change, so they track the two-year yield less well and receive about half the weight."
 - Cut "That resemblance is a finding of the paper. Its cause is open." here; Section 3.3 says it.

3. **p. 4, Sec. 2.1, "I work with three asset prices throughout".** Five definitions in six sentences. "Equity valuation is the gap between the cyclically adjusted earnings yield and r*, expressed in log points of the price-earnings ratio" cannot be parsed on first reading. The paragraph does not say why these three assets and not credit spreads.
 - Add first: "I use these three because all four calibrations assign them a weight and their responses to policy announcements can be measured in narrow windows." [author to verify this is the reason]
 - Add after the equity sentence: "In practice a one log point fall is a fall of about one percent in stock prices at given earnings, and I describe it that way below."
 - Add one clause on r*: "that is, relative to an estimate of the real rate consistent with output at potential".

4. **pp. 5-6, Sec. 2.2, "The weights answer the question."** "Generalized least squares weights" arrive without intuition. "The right-hand side... The left-hand side" refers to a condition that is only inline (g_h proportional to Σ⁻¹ψ). "Common scale" is used two pages before Section 2.4 defines it.
 - Display the condition as an equation.
 - Add before equation (3): "The market weights are those of a regression that recovers the surprise from the three prices. An asset receives more weight the more it responds to policy news and the less it moves for other reasons."
 - Fix the last sentence of 2.2 (see section 5, item 3).

5. **pp. 6-7, Sec. 2.3, equations (4)-(5) and "Three cases follow."** The key step is one clause ("because both read one on ψ"). The three cases run in one nine-sentence paragraph.
 - Add after (5): "Every set of weights reads the usual policy pattern as one point. Two sets of weights can therefore differ only on the part of a movement that departs from that pattern."
 - Give each case its own short paragraph and label it with the episode that illustrates it.

6. **p. 7, Sec. 2.4, "Comparing weights requires one scale, and I use the first."** A result is buried in a units paragraph ("0.954 funds-rate points (90 percent interval 0.86 to 1.08)... With a half-life of four quarters... 0.82"). It uses "persistent asset paths" and "half-life" before the FRB/US experiment is described (Sec. 3.2) and leans on Appendix D.4.
 - Keep one sentence here: "The two units turn out to be nearly the same size: FRB/US reads the usual asset response to a one-point surprise in the two-year yield as about one point on the funds rate. The choice of common scale therefore matters little."
 - Move 0.954, 0.82 and the interval to Section 3.2, where persistence is discussed and the numbers are repeated anyway.

7. **p. 8, Sec. 3.1, "Two measures are natural" and "Figure 2 shows what the remainder moves."** Eight statistics, three of them an interval for a null result. No sentence says why the reader should care which measure is used.
 - Add before "Two measures are natural": "The choice looks like a technical detail. It turns out to move the weight on equities by half."
 - Replace the numbers paragraph with: "Figure 2 shows that the two parts move different assets. The futures factor moves all three: yields up, stock prices down, the dollar up. The residual moves the 10-year yield and the dollar about as much as the factor does, and it does not move stock prices."

8. **p. 10, Sec. 3.1, "That observation explains the weights through equation (3)."** The logic is correct and compressed. "Both the response vector ψ and the covariance Σ change, and each accounts for about half of the change in the equity weight" and "a 90 percent interval for the change from 0.98 to 5.47 times" are for the appendix or a table note.
 - Add first: "The same movement in yields and the dollar is noise under one definition of policy news and signal under the other."
 - Keep one number: the equity weight falls from −0.051 to −0.027.

9. **pp. 10-11, Sec. 3.2, "The equity decline works through domestic demand" and "Duration belongs in a spending calculation".** The economics is clear; the paragraph ends on a 45-word sentence restating sizes. The duration paragraph repeats 0.954 and 0.82 and adds 2.55 against 2.51.
 - End the first paragraph: "In the model, trade responds to the dollar faster than consumption responds to wealth. That is why FRB/US counts the dollar for more."
 - Keep one sentence on duration: "Persistence matters for how much tightening a movement represents and little for which asset counts more (Appendix D.4)."

10. **pp. 11-12, Sec. 3.3, "If FRB/US were the only spending calibration".** Five published weights (4.4, 45.1, 39.6, 4.9, 6.0), an example (20 percent, 17 percent), then six common-scale weights already in Table 1. The reader cannot see how 4.9 and 6.0 become −0.056 and 0.069.
 - Cut the five published weights to a footnote and cut the six Table 1 numbers.
 - Add: "The published weights apply to variables in different units. Table 1 converts them to the units used here and to the common scale."
 - State the point once: "On the common scale the Goldman Sachs weights are close to the futures-factor market weights on all three assets (Table 1)."

11. **pp. 12-13, Sec. 4.2, "One asset dominated the movement" and "The month-by-month readings".** Nineteen statistics in two paragraphs, including four weights already given twice.
 - Replace with: "One asset dominated the movement, so one difference in weights dominates equation (6). The futures-factor and Goldman Sachs weights on equities are about twice the other two (Table 1). They read the episode as about 2 points of tightening a year, and the other two as about 1.4 (Table 2)."
 - Keep the peak range (2.00 points) and the correlation (0.93 to 1.00); drop the four peak values and "22 of the 24 months".

12. **p. 14, Sec. 4.3, "The sign of the reading then depends on the weights" and "An analyst watching household wealth".** Ten statistics forming a three-by-two accounting; this is a table.
 - Put the six contributions in a three-row table, or cut to: "Under the futures-factor weights the appreciation adds 0.8 point and the other two movements subtract 1.3, a net easing of half a point. Under FRB/US the appreciation adds 1.3 and the others subtract 1.0, a net tightening of a quarter point."
 - The next paragraph covers 1998, 2015 and 1998-2001 averages in one run. Move 2015 and the 1998-2001 averages to the appendix or a footnote.
 - The section is titled "1997-98" and the introduction says "In 1997-98", but the middle panel of Figure 4 is labeled "1998-2001". Make them one episode.

13. **pp. 15-16, Sec. 4.5, "Distances." through "Size."** About 35 statistics in four paragraphs, with intervals quoted in the prose against the guide's "verdicts in words, intervals in tables". Sections 4.2-4.4 are in points; this subsection is in basis points.
 - Use one unit.
 - Open: "The three episodes were chosen to illustrate. Table 2 asks how often each case occurs across all 369 months."
 - One finding per run-in paragraph with one or two numbers (7 against 26 to 28 basis points; 81.6 percent; 8 months; 70.5 percent). Intervals go into Table 2 as a column. The note now says "Intervals for the first column are in the text", which is the wrong way round.

14. **p. 17, Sec. 5.1-5.2, equation (7) and "Table 3 reports the two restrictions."** D_t is defined in a subordinate clause and then called "composition" without the name being given. The two paragraphs of 5.2 carry 17 statistics across three samples and two outcomes and end in three verdicts that pull against each other.
 - Add after (7): "I call D_t the composition of the tightening. It is positive when the dollar accounts for more of a given tightening and equities for less."
 - Suggested 5.2 is in section 5, item 13.

## 3. Where the reader is not told what they are learning or why it matters

- **Abstract.** It ends on a caveat. The best sentence in the paper, the first of the last paragraph of 6.2, is not in it. End the abstract: "A reported tightening in points of policy should therefore name the calibration that produced it and the asset prices that moved."
- **Introduction, paragraph 2.** The Powell quotations motivate; the stake is not stated. Add: "The stakes are not small. In 2008-09 the calibrations compared here differ by more than half a percentage point of policy on the size of the same tightening."
- **Section 2 has no opening.** Add: "This section defines the two ways of converting asset-price movements into points of policy and shows when they give the same answer. The result is a simple accounting identity that organizes the rest of the paper: two indexes can disagree only about movements that depart from the usual response to policy."
- **Section 2.4 (units) comes too late.** Its first paragraph belongs at the end of 2.1, before the scale is used in 2.2 and 2.3.
- **Section 3 opening** reads the table before stating the idea. Open: "The four sets of weights differ mainly on one question: how much a movement in the dollar counts relative to a movement in equity prices. This section traces that difference to two sources, the definition of policy news on the market side and the channels of spending on the spending side."
- **Section 3 has no close.** Section 3.1 ends on a caution, 3.2 on a data-matching caveat and 3.3 on "What can be said is...". Add at the end of 3.3: "The four calibrations thus differ for three reasons. The market weights depend on what counts as policy news. The FRB/US weights reflect a trade channel that acts faster than the wealth channel. The Goldman Sachs weights reflect a different, undocumented balance between the two."
- **Section 4.1** opens on mechanics. Open: "Differences in weights matter only if asset prices move in ways that expose them. This section asks how often they have, and whether the differences affect the direction of the reading or only its size."
- **Section 4.5, "What the input series change."** Not motivated. Add: "Published indexes use nominal or real series and do not adjust for the neutral rate. The last two columns of Table 2 ask whether the conclusions depend on that choice." The column heads "Real, 100 ln CAPE" and "Nominal, 100 ln CAPE, nominal dollar" need plain labels ("Real, no r* adjustment"; "Nominal").
- **Section 5.2 close.** "The outcome evidence therefore bounds the claim of the paper and does not extend it" is opaque. Replace the last paragraph with: "Realized activity does not show that one translation of financial movements into points of policy is right. A policymaker chooses a calibration knowing that the data will not adjudicate."
- **No contribution paragraph.** His habit is "These results may inform discussions of monetary policy in several ways. First... Second... Finally" (2024-032) or "Three lessons... emerge" (2020-095). The draft's three questions and three answers do part of this. A short "what a user of these indexes should take away" paragraph before the roadmap would do the rest; the material is the last paragraph of 6.2.

## 4. Repetition

| Idea or number | Where it appears | Keep |
|---|---|---|
| "Switching between two implementations of the same method changes the reading about as much as switching from market responses to spending effects, and the two closest readings come from different methods" | Abstract; p. 3 (near verbatim); end of 2.2 as a preview ("the answer in these data is that it is not"); 4.5 "Distances."; 6.2 par. 3 | Abstract, one intro sentence, 4.5 (the proof), conclusion. Cut the preview in 2.2. |
| Direction agrees, opposing readings rare, size more sensitive | Abstract; p. 3; 4.5 "Direction." and "Size."; 6.2 par. 4 | Same four; in 4.5 state it once, not in both paragraphs. |
| "GDP growth provides little evidence for choosing... and the unemployment comparison is sensitive to the sample" | Abstract; p. 3 (verbatim); 5.2; 6.2 | Shorten to one clause in the abstract and introduction (section 5, item 1). |
| What the four calibrations are | Abstract; intro par. 3; end of 2.1; opening of Sec. 3; 6.2 par. 1; notes to Figure 1 and Table 1 | Intro and 2.1 (with citations). Section 3 can say "the four calibrations". |
| The two questions (policy surprise against spending effect) | Abstract; intro par. 1; 2.1 par. 3-4; 2.1 par. 6 ("One equation describes how policy moves markets. The other describes how markets move spending."); 6.2 par. 1-2 | Cut the two sentences in 2.1 par. 6; they restate what the equations just showed. |
| Signal quality against transmission; agreement is a coincidence | Intro par. 5; 2.2 after (3); 2.2 examples paragraph ("Complete transmission... imposes no requirement that signal quality line up"); 6.2 par. 2 | In 2.2 keep the two examples; cut the abstract restatement around them. |
| Different weights agree by offsetting | Intro par. 5 last sentence; p. 3 (2022-24); 2.3 "Third..." and "The third case has a consequence"; 4.4 "They agree for a reason that has nothing to do with similar weights" and "Near-equality of two readings is not evidence that the indexes embody the same economics"; 6.2 twice | 2.3 (theory), 4.4 once (evidence), conclusion once. "Without embodying the same economics" (2.3) and "embody the same economics" (4.4) are one sentence twice; keep 4.4. |
| Direction agrees and size differs in 2008-09 | p. 13, three consecutive statements: "High correlation is a statement about direction and timing. It is compatible with large differences in level."; "Every calibration says... They differ by more than half a point"; "This is the case in which agreement on direction conceals a large difference in magnitude" | The middle one, with the policymaker example. |
| "More than half a point" | p. 3; 4.2 twice; 4.4; 6.2 | p. 3, 4.2 once, 6.2. |
| Dollar-to-equity ratios 1.00, 0.96, 2.06, 2.51 | Figure 1 labels; intro ("more than twice"); opening of Sec. 3 (all four); 3.2 (2.55 against 2.51); 3.3 ("two and a half times") | Figure 1 and words. Cut the list in Sec. 3. |
| Equity weights −0.051, −0.056, −0.027, −0.032 | Table 1; 3.1; 3.3; 4.2 | Table 1 and the one change in 3.1. |
| Responses to policy news | 2.3 ("about half a point... about 8 percent... about 4 percent"); 3.1 (0.53, 7.78, 4.22) | 2.3 in round numbers; 3.1 points to Figure 2. |
| 0.954 falling to 0.82 | 2.4; 3.2 | 3.2. |
| The accounting identity | Equation (5), p. 6; equation (6), p. 12, introduced afresh as "elementary accounting"; 4.4 cites both | One equation. Keep (5), add the by-asset sum as a second line, and refer back in 4.1. |
| Spreads held fixed; GS weights are not the GS index | 3.3; 4.1; 6.1; notes to Figure 1, Table 1, Figure 4, Table 2 | Text of 3.3 and 4.1 once each; notes. |
| Only the market weights are estimated | 4.5 "Size."; 6.1; Table 1 notes | 6.1 and the notes. |
| The readings are not claims about causes | 2.1 ("Neither reading is a claim about what caused the movement"); 2.3 ("Computing it does not require knowing what moved markets"; "whatever caused the movement"); 3.1 ("One caution...") | 2.1. |
| "A distance cannot be negative..." | 4.5; Appendix C.3 | Appendix only. |

## 5. Hedging and caveats

**Needed by the reader; keep once, state flatly:**

1. **Abstract and p. 3:** "and the unemployment comparison is sensitive to the sample". This is the "in some cases but not others" the guide rules out of the abstract and introduction. Reword both to: "Subsequent activity does not say which calibration to prefer." The sample dependence stays in 5.2.
2. **p. 3 and 3.3:** "Its cause is open." and "the paper cannot explain it as it explains the other two. What can be said is that...". Say it once, in 3.3: "The published documentation does not identify the source of the difference. It lies where Figure 3 would put it: in how much a movement in the dollar does to GDP within a year relative to a movement in equity prices."
3. **p. 6, end of 2.2:** "That is an empirical matter, and the answer in these data is that it is not." It is ambiguous and previews a result. Replace with: "Whether differences between methods exceed differences within them is an empirical question, taken up in Section 4."
4. **p. 10, 3.1:** "The data do not say which measure is right." The paragraph says "Each reading has a different implication for which index a policymaker should prefer" and never gives the implications. Rewrite as interpretation: "The residual has three possible readings. If it is policy news about horizons beyond the futures, the two-year-yield weights are the better measure of policy. If it is a movement in term premiums or measurement error in one yield, the futures-factor weights are. The announcement responses cannot distinguish them." [inference; author to confirm the mapping]
5. **p. 12, 4.1:** "so the readings are not complete measures of financial conditions in a period such as 2008". Needed once. Shorten to: "Corporate spreads are held fixed, so the readings understate the tightening of 2008."
6. **p. 18, 5.2:** "Three features of the problem limit what such a test can establish." This is useful economics presented as an excuse after the results. Move the first feature to 5.1 as design: "The test is demanding. The readings differ only when asset prices move in unusual proportions, so composition varies little once the market reading is held fixed: its independent variation is a fifth of that of the reading itself." Cut the other statistics (1.66, 0.43, −0.66). Keep the forward-looking-prices point as one sentence. Drop the recession point or move it to 6.1.
7. **p. 18, 6.1:** the expanding-window sentence on the equity weight (2011 to early 2015) and the sentence on policy targeting financial conditions. Keep both.

**Defensive; cut, shorten or move:**

8. **p. 8, opening of Sec. 3:** "This section explains what the data can explain about those differences". Replace with "This section traces those differences to two sources."
9. **p. 10, 3.1:** "One caution applies to both market calibrations..." (five sentences). The cause point is already in 2.1. Move the information-effect sentence there as one sentence with the Nakamura and Steinsson (2018) citation; cut the rest.
10. **p. 11, 3.2, last paragraph:** "The experiment requires matching the market series to the model's variables, and the matches are approximate...". A data-matching caveat closes the section, and Appendix C.2 already has it. Replace with a footnote: "The market weights are estimated on the S&P 500 and DXY and applied to equity valuation and the real broad dollar; Appendix C.2 gives the mapping."
11. **pp. 14-15, 4.4:** the draft headlines "differ by one hundredth of a point" and then retracts it twice ("The cancellation is a property of the averages..." and "Equality to the second decimal belongs to one pair of calibrations..."). State the finding at the precision that holds: "The four readings average about 1 point, and the futures-factor and FRB/US readings are nearly identical." Keep one sentence on the monthly range (−0.32 to 0.40). Cut "Equality to the second decimal..." and "The episode carries two lessons".
12. **pp. 15-16, 4.5:**
 - "These are rankings of point estimates..." (six sentences): keep "The data cannot rank the within-method and between-method distances"; the rest goes to the table and Appendix C.3.
 - "What counts as a meaningful disagreement is the policymaker's choice, and the conclusion that opposition is rare holds for thresholds a policymaker would care about": replace with "At a threshold of 10 basis points the share is 10 percent."
 - "The first statement is less precise than the second... conditional on the observed history...": move to Table 2 notes and 6.1.
13. **p. 17, 5.1 and 5.2:**
 - "The test compares two of the four calibrations. The other two readings are close... and a test among four would have less power still": footnote.
 - The unemployment paragraph gives three samples and then "I do not read the rejection as evidence for the market weights. It treats the market weights as known, it is one of twelve restrictions in the table, and it does not appear for the outcome that the spending weights are built to explain." Suggested whole of 5.2 after the first sentence: "For GDP growth, neither restriction is rejected in any sample. The intervals are wide in economic terms: moving composition from its 5th to its 95th percentile changes predicted growth by about 1 percentage point, with an interval that spans zero and effects of nearly 3 points. For unemployment, neither restriction is rejected over 1976-2026; the FRB/US restriction is rejected at the 10 percent level from 1996 and not in the other two samples. One rejection among twelve restrictions, for the outcome the spending weights are not built to explain, is not evidence for either reading."
14. **pp. 18-19, 6.1:** the heading "What Is Held Fixed, What Is Estimated and What the Intervals Cover" reads like documentation, and the subsection sits between the results and the conclusion. Retitle it "Scope" and state each item with the direction it would move the result (the pattern of Section 3 of 2024-032). The interval caveats moved from 4.5 land here.

**Fine as they are:** "Agreement of the four portfolios along ψ then follows from the units and is not evidence of anything" (p. 7); "It is not the Goldman Sachs index, whose series and transformations differ" (p. 12); the Table 3 note.

## 6. Literature

**Section 1.1 is list-like in two of its four blocks.**

- "Weights and their meaning" opens with a taxonomy of nine citations. Its last two sentences (Eika, Ericsson and Nymoen 1996; "I quantify that difficulty") are the real connection and should lead.
- "Information about activity" is six "X show / build" sentences. Only the clause "I measure the inputs relative to r*" touches this paper. Cut it to two sentences tied to Section 5, or move the citations to where they are used.
- "The closest comparisons" does state the difference ("My design holds the assets, the transformations and the policy unit fixed"). Make that the first sentence.
- "Why the meaning of a point matters." is the best-connected block. Its run-in heading is typeset in the middle of the previous paragraph (p. 4); it needs a paragraph break.

**After page 4 the results are almost never tied to the literature.** This is the largest gap against both style papers. Using only works already in the references:

- **Sec. 2.2:** cite Eika, Ericsson and Nymoen (1996) at the proportionality condition; it is the modern form of their point that such weights depend on the shock.
- **Sec. 3.1:** the residual that moves long yields and the dollar and not equities needs placing against multi-dimensional policy surprises: Gürkaynak, Sack and Swanson (2005), Boehm and Kroner (2025), Bauer and Swanson (2023). One sentence saying whether the finding is consistent with or differs from each. [I have not checked how the residual maps to their factors; author to verify.]
- **Sec. 3.2:** Brayton, Laubach and Reifschneider (2014) is cited for the model only. A reference is needed for the size and speed of the wealth and trade channels. Ajello et al. (2023) is the natural comparison: Appendix C.2 already has the FCI-G dollar-to-equity multiplier ratio (2.25 against 3.22). Bring one sentence of that into the main text.
- **Sec. 3.3:** Hatzius and Stehn (2018) and Dudley and Hatzius (2000) for how the Goldman Sachs weights are derived. The text now leans only on Caballero and Simsek (2026) as a secondary source.
- **Secs. 4.2-4.4:** Bletzinger, Martorana and Mistak (2026) report divergences "driven by equities and the strongest tightening in 2022-24" (p. 3). Say at 4.2 and 4.4 whether this agrees. Arnaut and Bauer (2024) and Sack and Swanson (2023) belong at 4.4.
- **Sec. 4.5:** Aramonte, Rosen and Schindler (2013), on comparisons depending on the crisis in the sample, fits the 2008-09 result and the "input series" paragraph.
- **Sec. 5:** Hatzius et al. (2010), Adrian, Boyarchenko and Giannone (2019) and Lombardi, Manea and Schrimpf (2025) concern prediction of activity, and none is cited in Section 5. The author's own FEDS 2020-095 finds that an index built to predict unemployment weights equity prices heavily. It is directly relevant and not in the reference list; a reference is needed here.
- **Sec. 6.2, last paragraph:** tie the practical recommendation to Caballero, Caravello and Simsek (2024) and Caballero and Simsek (2026) in one clause, as the introduction does.

## 7. Terms and notation before definition; dependence on the appendix

**Terms:**

- **Calibration / portfolio / set of weights / index / reading / method / implementation.** "Calibration" (40 uses) and "portfolio" (23) name the same object, and "portfolio" is never defined (first on p. 5). "Implementations of the same method" appears only in the abstract and on p. 3. Fix a hierarchy: two methods, four calibrations, each produces a reading. Drop "portfolio" and "implementation".
- **Policy news / policy surprise / surprise / announcement.** Thirty against six uses; pick one. The same goes for "usual response", "usual proportions" and "conventional pattern".
- **"Remainder" names two objects.** One is r_t in equation (4), the part of an asset movement the usual response cannot reproduce. The other is in 3.1, the part of the two-year change not in the futures factor, which Figure 2 labels "Residual". Call the second "residual" throughout. The symbol r_t also sits beside r*.
- **"Common scale" / "two-year-yield scale".** In the Figure 1 axis and notes (p. 2) and in 2.2 (p. 5); defined in 2.4 (p. 7).
- **r\*, "equity valuation", "log points".** In the introduction and the Figure 1 notes before 2.1.
- **"Composition".** In 5.2 and the title of Table 3; never introduced as the name of D_t.
- **"Persistent" paths and "half-life".** In 2.4, before the experiment in 3.2. "A specified path" (2.1) is not specified until 3.2.
- **Smaller items.** "GS" is used without being spelled out. "DXY" first appears in Figure 2 and the last paragraph of 3.2. The S&P 500 is used in 3.1 where 2.1 defined "equity valuation", and the link comes only at the end of 3.2. The subscript B in w_{B,h} is unexplained. The "···" in equation (7) is explained after the equation. "One of twelve restrictions" requires the reader to count cells in Table 3. FCI-G and FCI\* in 1.1 get no gloss on first use.
- **Units.** Points in 4.2-4.4 and basis points in 4.5 and Table 2.
- **Figure 1.** The "ratio" labels overprint the legend.

**Dependence on the appendix:**

- **Sec. 2.1 to Appendix B.** The equity-valuation gap cannot be understood from the main text alone. Fix in the text (section 2, item 3).
- **Sec. 2.4 to Appendix D.4.** The persistence claim rests on it. Acceptable once the claim moves to 3.2.
- **Sec. 4.5 to Table C.4.** The intervals for Table 2 are in the text and the appendix, not in the table.
- **Sec. 6.1 to Appendix E.2.** The expanding-window result. Acceptable.
- **The appendix uses a different vocabulary.** It says "market-implied reading", "spending-equivalent reading", "the model", "the event study", "baseline signal" and "D", where the main text says "market reading", "FRB/US reading" and "composition". A reader who follows a pointer lands in another vocabulary.
- **Cross-reference slips.** C.1 cites "Table D.7" and C.2 cites "Table D.9" (in D.5, which is empty on p. 38 as far as I read). C.4 cites "Section 3.1" for "the lower-bound years", which Section 3.1 does not discuss. C.2 has "futures factors".
- **Balance.** The main text is 19 pages and the appendices about 23. The guide asks for the reverse. The added explanation recommended here moves in that direction.

## 8. The five changes that would most improve readability

1. **Take the statistics out of the prose in Sections 3.1, 3.3, 4.2-4.5 and 5.2.** One idea and at most two numbers per paragraph; intervals into Tables 2 and 3; the 1997-98 accounting into a small table. This is the largest gap with his published papers.
2. **Add an opening and a closing to Sections 2, 3, 4 and 5, and one "why this exercise" sentence to each subsection** (wording in section 3). Put the practical conclusion (name the calibration, name the assets that moved) in the abstract and the introduction.
3. **State each idea once in the body.** Merge equations (5) and (6). Cut the restatements listed in section 4, above all the "implementations... different methods" sentence (five places), the offsetting point (eight places) and the three consecutive direction-against-size statements on p. 13. Abstract, introduction and conclusion may echo each other; the body should not.
4. **Collect caveats.** One flat sentence where the reader needs it, the rest in a retitled "Scope" subsection or the table notes. Fix the three places where a caveat closes a section (3.1, 3.2, 5.2) and the abstract's last sentence. Stop retracting the 2022-24 result after headlining it.
5. **Fix the vocabulary and add connective tissue.** One name for each object; define "common scale" in 2.1 and "composition" in 5.1. Link sentences with his own connectives ("As a result", "In contrast", "For example", "That is"), and tie each main result to a cited paper at the point of the result.
