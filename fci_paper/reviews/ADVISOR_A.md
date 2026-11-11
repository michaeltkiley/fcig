# Advisor A: is "do the indexes agree?" the right question?

Perspective: senior monetary economist, central-bank policy experience. Based on the paper, Note B's introduction and headings, the writing guide, the two prior reviews and the project memory. [verified: read; not re-run]

## 1. Blunt assessment

**The question is not the right one.** "Do the indexes agree once measured alike?" is a measurement question whose answer cannot matter to a policymaker whichever way it comes out. The paper's own answer is "on direction yes, on level no, and the disagreement is about the size of the sampling error." That is a non-answer. A reader cannot act on it, and the abstract needs about ten numbers to state it. Note B asks something whose answer changes what we believe (does the measured effect of policy depend on how its financial consequences are measured?) and answers it in one sentence. Note A has no such sentence.

**It does not answer directly.** Three of the paper's results undercut its own question.
- The correlations are partly built to agree: same variables, same base period, units rescaled by the same policy news. Referee 2 made this point.
- The one test that could say which index is better (the unemployment regressions) shows no significant out-of-sample gain, and the published FCI-G effect of 0.13 rejects its own claimed 0.5. That finding is more interesting than the main one and is buried in Section 5.5.
- The weights are too imprecise to adjudicate between indexes (10-year weight 0.13 to 1.13). The paper cannot say whose weights are right, so the comparison has no verdict.

**What it adds.** Against the literature the novelty is real but thin.
- Aramonte et al. (2013) already compare many indexes by correlation. Arnaut-Bauer (2024) already convert GS into policy-response units. Sack-Swanson (2023) already tie FCI-G to the two-year yield.
- Hatzius et al. (2010) already classify indexes by the source of their weights. The paper's "weights from policy news" is the event-study variant of that classification.
- The nominal, real, r* ladder is new as a systematic comparison, and it is the idea that connects to Dudley (2010) and Caballero et al. (FCI-star). The weights are Rigobon-style identification from FOMC windows (Gürkaynak-Sack-Swanson, Nakamura-Steinsson).
- What is **not** in the literature, and is what Note B shows by implication, is an index whose unit is a *policy equivalent* and which is stated relative to r*. That makes the index a measure of the **stance of policy, including its financial transmission**, rather than yet another FCI.

**Diagnosis.** The paper's best asset (policy-equivalent units plus the r* gap) is treated as a technical device for making comparisons. It should be the subject. The paper currently compares indexes with each other. The question a central bank cares about is whether policy is restrictive and how it is being offset or amplified by what markets do.

## 2. Suggestions

I rank them. Suggestion A is my recommendation for the paper's frame. B supplies its test. C is the cheapest route to a fully answerable version.

### A. Reframe around the stance: "How restrictive is policy once financial conditions are counted, and how much of it is policy?"

**Question.** Over 1990-2026 (and in the 1994, 2004-06, 2015-19 and 2022-24 tightening episodes), how much of the movement in financial conditions was what policy news explains, and how much came from other sources (equity valuation, dollar, term premium)? What is the policy-equivalent rate (r* plus the index, in funds-rate units)? When did financial conditions amplify or offset the funds-rate path?

**Why it matters.** This is the stance-of-policy debate: the 2022-24 tightening that "did not bite", the Chair's remark that indicators give different answers, and the 2010s case in which the funds rate was at zero and conditions were tight or loose. Policy-equivalent units and r* are exactly the tools. The conclusion would be a statement like "In 2022-23 X of Y points of tightening was policy-news-driven and Z was other; the stance relative to r* was ... with interval ...".

**Work.** True new analysis, though small.
1. Split each month's index change into the part projected on cumulated FOMC-window policy news and the remainder, using the existing NS series (1996+) and daily data.
2. Express the index as a policy-equivalent funds rate relative to r*.
3. Add r* and weight uncertainty (the bootstrap already exists) to each stance statement.

**Existing data and code.** Yes: the NS surprises, the weights, the daily block from Note B (`baseline/`), the bootstrap and the r* series are all in hand.

**Framing change.** The title becomes about the stance (for example "The Stance of Policy through Financial Conditions"). The comparison with GS, FCI-G and FRB/US becomes the validation section, not the paper. The abstract's sentence is about the decomposition. The three-step ladder is the argument for why r* is required.

### B. Test the identifying assumption every FCI makes: does a point of non-policy tightening do what a point of policy tightening does?

**Question.** All the indexes, including this one, add up variables as if the source of a move does not matter. Does the unemployment response differ between policy-news-driven and other movements of the same index?

**Why it matters.** This is the real disagreement between market weights, model weights and PCA weights, and it is the one place the paper can discriminate between indexes economically rather than by correlation. It also fills the gap the weights-imprecision finding leaves open. Weights matter if and only if the source matters. It connects directly to Hatzius et al. (2010), Arnaut-Bauer and Caballero et al. (does FCI-star depend on shock type?).

**Work.** New. Estimate unemployment responses to (i) the policy-news component and (ii) the non-policy residual of the index in the VAR. Note B's components tests and proportionality tests are the template. Identify non-policy moves by the HFI literature's stock-yield co-movement (Jarociński-Karadi) or by the orthogonalized Bauer-Swanson surprises. The existing results (price fall requires proportional weights from 1996) are a warning that this will be fragile; the paper should report it plainly.

**Existing data and code.** Mostly. Note B's `baseline/` machinery supports it with limited changes. It needs a non-policy shock identification that is not yet in the package.

**Framing change.** The paper's question becomes "does the source of a financial-conditions move matter for activity?" Indexes are compared by whether their weights imply the right answer.

### C. If A and B are too much: make "Are financial conditions restrictive today?" the single question, with intervals that include weights and r*

**Question.** Is the September 2026 reading tight, neutral or loose, and with what confidence?

**Why it matters.** It is the question the Chair's quote poses. The paper already has the pieces: GS -1.23, FRB/US +0.27, market -0.93 [-2.0, +0.2]. At present the paper uses the interval only to say the indexes cannot be told apart. Turned around, the answer is "conditions are not restrictive relative to r* with high probability under any weights; the disagreement is about how loose".

**Work.** Add r* uncertainty (LW, Kiley, Holston et al.) to the bootstrap and give a probability statement for each period; repeat for 2022-24. This is a small extension of the bootstrap.

**Existing data and code.** Yes (replication steps 04-06).

**Framing change.** The paper has one headline claim and the comparison becomes its evidence. Weaker than A, but it is feasible within the existing package.

## 3. Recommended path

Choose A as the frame and use B as the one new analysis. Drop robustness expansion. The sentence the author should be able to write is: *"A monetary tightening works through financial conditions; I measure how much of the movement in conditions is what policy news explains, and show that counting the rest changes how restrictive policy looked in X and Y."* If the author cannot yet write such a sentence from existing results, the first step is the decomposition in A.1 to find out what the data say.

[inference] on the claim that B will be fragile; [verified] on the paper's own numbers; the Referee 2 points are from `reviews/REVIEW_2.md`. I could not check the literature claims in section 1 against the papers themselves in this review.
