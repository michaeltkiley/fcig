# Advisor B: Is "Do the Indexes Agree?" the Right Question?

Tags: [verified] = read in the draft or notes; [inference] = my judgment; literature from memory is [secondhand] and should be checked.

## 1. Verdict

**The question is a measurement-note question, not yet an economic one.** "Do indexes agree once on a common basis?" has no stopping rule. Agreement is not accuracy: two indexes can agree and both be uninformative, or disagree because one is better. The draft says so itself ("there is no ground truth", Section 7) [verified]. Its answer is a hedge: they agree on direction, disagree on level by about a point, and the market index is "one estimate among several". Note B ends with a number and a policy reading (0.6 point more unemployment; a sacrifice ratio). Note A ends with "give a range". That is the gap between the two papers.

**The evidence answers a different question from the one asked.** The agreement tables (correlations, ranges) are mostly built to agree. They share variables, use the same real dollar, and put each index in the market index's units. Referee 2 made the same point about levels and persistence [verified]. The two findings with economic content are buried:
- the neutral-rate step moves readings by more than any weighting choice, and reverses the post-2008 picture;
- flows carry information about unemployment and levels do not.
Neither is tested against an outcome well enough. The paper calls the activity regressions "the only evidence" that the r* step helps, and the gains are not significant [verified]. The largest effect in the paper has no validation.

**What it adds relative to the literature.** The new object is an event-study-weighted index in policy units, plus the nominal/real/r* ladder. Arnaut-Bauer and Aramonte et al. compare indexes by correlation; Hatzius et al. (2010) discuss weights; the NFCI uses principal components; FCI-G uses model weights. The paper is not engaged with the literature on what an index should deliver, which asks about the distribution of outcomes: Adrian-Boyarchenko-Giannone (2019) on growth-at-risk [secondhand], Gilchrist-Zakrajsek (2012) on the excess bond premium [secondhand], Koop-Korobilis (2014) on time-varying weights [secondhand]. Nor does it test the conceptual point at its centre. The market weights say how variables move when policy moves. An index is used to say what they imply for activity. Nothing shows these are the same weights. Section 2.3 admits that earnings-driven equity moves are treated as policy-equivalent, and the disagreement with FRB/US is concentrated in exactly the equity weight [verified]. That is an economic question the paper identifies and does not answer.

**One reframing that fits all three suggestions** [inference]: *What should a financial conditions index be measured against, and does the construction (basis, weights, level or flow) change what it says about the economy ahead?* Agreement among indexes becomes a descriptive first exhibit. The outcome tests become the result.

## 2. Suggestions

### S1. Does measuring relative to the neutral rate improve what an index says about the economy? (priority)
- **Question.** Is the r* step a better measurement, or only a different one?
- **Why it matters.** It is the paper's largest effect and the link to Note B, which shows r* matters for transmission. The 2009-2016 and 2022-24 episodes are natural tests: nominal indexes read easy, r* versions read tight, and the 2022-23 tightening was not followed by higher unemployment [verified, in the draft].
- **Work.** For every index and each step, run a paired comparison of nominal, real and r* versions. Use several outcomes (unemployment, payroll or GDP growth, core inflation, recession probability) at 6-, 12- and 24-month horizons. Use local projections with HAC intervals, and report Diebold-Mariano or Clark-West tests on differences between steps rather than against zero. Add subsample stability (pre- and post-2008, 2020-25), and show which episodes drive the result. Sample size will limit power; a null is a finding, stated as a fact.
- **Support.** All three steps exist for every index (`replication/` steps 03-06, activity step 07). New work is outcome series (GDP, payrolls, core PCE, NBER dates) and the test harness. About a week.
- **Framing.** Title and abstract: "Do financial conditions indexes need to be measured relative to neutral?" The Chair quotation motivates it; the answer is a yes or a no with horizons attached. The current Sections 3-5 shorten, and agreement becomes the first exhibit.

### S2. Do financial variables affect activity in proportion to how they respond to policy?
- **Question.** Are policy-response weights also activity weights? Where the 10-year yield, equities and the dollar move for reasons other than policy, do they matter as much for unemployment?
- **Why it matters.** It is the core assumption of any event-study index, and it explains the market-versus-FRB/US gap (equity 0.07x versus the model [verified]). It is also what separates "policy-equivalent tightening" from "conditions that matter for activity". Note B (Section 3.7, "Which Financial Variables Carry the Response") has the components machinery [verified].
- **Work.** Estimate activity weights directly: the VAR or local projection with the three components entered separately (and with identified policy-news components versus the residual), and the implied weights with bootstrap intervals. Compare three weight vectors (policy-response, activity-implied, FRB/US), with PCA weights (NFCI-style) as a fourth, and test proportionality. Report the index each implies and its out-of-sample content.
- **Support.** Components, bootstrap and VAR code exist. New work is the constrained-versus-free test and the PCA benchmark on the same three variables. Caveat: three variables over 50 years is thin, and multicollinearity may make the activity weights imprecise [inference].
- **Framing.** Replaces "weights are the source of disagreement" with a testable claim. If proportionality holds, the market index earns the claim to be a general measure. If not, the paper says what policy-based indexes cannot do.

### S3. Level, flow and the lower tail
- **Question.** Do levels or flows of financial conditions predict the distribution of outcomes, and does the answer differ on the r* basis?
- **Why it matters.** The paper says flows predict and levels do not, but that rests on regressions of a persistent gap on its own level plus a flow, and the Granger test on 12 lags of the level contradicts it. Growth-at-risk shows conditions matter most in the lower tail, which a mean regression misses [secondhand].
- **Work.** Quantile or local-projection estimates of the 12-month change in unemployment (5th, 50th, 95th percentiles), with level, flow and both, for each index, including the NFCI and ANFCI that appear only as correlations now. Test whether the r* basis shifts the tail. Resolve the level-versus-flow contradiction by regressing the change, not the level, of the gap.
- **Support.** Index series and unemployment are in place; add quantile regressions and a tail-loss score. Short sample for tails (about five recessions) is the limit [inference].
- **Framing.** A second main result: "flows carry the signal, the tails carry the risk".

## 3. Recommendation

Pick S1 as the question and use S2 as the mechanism section. Keep S3 for a later version unless S1 fails to separate the bases. Drop the agreement tests from the abstract's lead. Move the main agreement and bootstrap results to one early exhibit, since they remain the paper's distinctive contribution, but do not make them the question.

Do not add further robustness. The existing robustness table suffices.

## 4. Risks
- S1 may return nulls (the r* gains are not significant in the draft). A null with intervals is still an answer, and it would make a sharper paper than "the indexes agree within a point".
- S1 and Note B share the r* adjustment. State the division: B asks about transmission of a surprise, A about measurement of conditions. Do not cite B's estimates in A.
- All "better" claims need out-of-sample evidence; the draft's own OOS results reverse after 2021 [verified].

## Round 2: priorities

**Comparison.** A.A (stance, policy versus remainder) and my S1 (does r* improve content) are complementary: A is a decomposition and a stance statement, S1 is an outcome test. A.B and my S2 are the same question and merge. A.C is a presentation of A.A with r* uncertainty, not a separate analysis. My S3 (tails, level versus flow) stands alone and ranks last. I agree with A that "agree?" should not be the question. I would add one caution: A.A alone is descriptive (a split of an index into pieces), and it earns its place only if the pieces behave differently for activity, which is B.

**Ranked follow-ups**

1. **Does the source of a financial move matter for unemployment? (merges my S2 and A.B)**
- *Question.* Does a one-point rise in the index that policy news explains raise unemployment by the same amount as a one-point rise from the remainder (equities, dollar, term premium)?
- *Minimal analysis.* Split each month's change in the index into the part projected on cumulated window news (Nakamura-Steinsson series, 1996 on, in `02_weights.py` output) and the residual. Enter both in the `04_var.py` VAR (unemployment first, 12 lags), then test equal responses at month 12 with the paired bootstrap already in the package. Add a second version with the three components entered freely, using Note B's `09_weights_test.py` as a template. No identification of non-policy shocks is needed for a first pass; Jarocinski-Karadi sign restrictions would be a later check.
- *Series.* None new.
- *Worth it if* the responses are statistically equal (the index is a valid single measure of the stance, and the weight dispute is shown not to matter), or clearly unequal (policy-news pieces act more, or less; the index must carry the split). *Not worth it if* the 90 percent intervals are too wide to separate either case. State that plainly and drop it.

2. **How restrictive was policy in the 1994, 2004-06, 2015-19 and 2022-24 tightenings, and how much of that was policy? (A.A, with A.C as its summary)**
- *Question.* Policy-equivalent funds rate relative to r*, with the split from item 1, and how much financial conditions amplified or offset the funds-rate path.
- *Minimal analysis.* Express the index in funds-rate units, add the split, and draw bootstrap intervals that include r* alternatives (Laubach-Williams, Kiley, Holston et al.). Output: one figure and one table for the four episodes plus September 2026.
- *Series.* None new.
- *Worth it if* the stance differs materially from the funds rate alone, or the 2022-24 reading is clearly tight or loose with the intervals. *Not worth it if* the intervals cover both "tight" and "neutral"; then it only restates the paper's present result.

3. **Does the r* step improve what indexes say about the economy ahead? (my S1)**
- *Question.* Do r*-adjusted versions predict outcomes better than nominal and real versions of the same index?
- *Minimal analysis.* The paired comparison across the three steps in `06_activity.py` (extend the horizons, add Diebold-Mariano on the step differences).
- *Series.* Public series to add: real GDP growth, payrolls, core PCE, NBER recession dates (all FRED).
- *Worth it if* r* versions beat the others at one to two years, with the episodes 2009-16 and 2022-24 contributing. *Not worth it if* nulls. Then say so and keep r* as a measurement step.

4. **Do levels or flows predict the lower tail? (my S3)**
- Quantile regressions of the 12-month change in unemployment on level and flow, including NFCI/ANFCI. Same FRED series. Worth it only if the tail result differs from the mean result. Lowest priority; leave out unless items 1 and 3 leave room.

**Organizing question if 1 and 2 succeed.** *When financial conditions move with or against policy, how restrictive is policy, and does the source of the movement change what it does to unemployment?* If 1 returns equality, the paper reads: one index measures the stance whatever moves it; if 2 shows large episodes of offset, the stance differs from the funds rate by amounts of that size. The comparison with GS, FCI-G and FRB/US becomes the validation section.
