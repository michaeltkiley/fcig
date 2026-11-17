# Decision N1: three headline options sketched (17 Nov 2026)

For the author's choice; see `INTEGRATION_PLAN.md` Part 2. Each option: the claim, a draft abstract (no numbers, per the house style), the introduction's arc, the sections, the main exhibits, what happens to the current paper's material, and what a referee will push on. Numbers in brackets are the ones the text would use [verified unless tagged].

---

## Option (a): the equity channel

**Claim.** Monetary policy reaches financial conditions mainly through equity valuations and long-term yields. High-frequency market evidence and the Federal Reserve's main macro model agree on this, and on how much each asset should count.

**Draft abstract.** When monetary policy changes, which asset prices carry the change to spending? I answer with two independent sources on one scale: the movements of asset prices in the minutes around FOMC announcements, and the spending effects of asset prices in the FRB/US model. Both put equity valuation at the center. In the announcement windows, stock prices supply the largest share of a policy move's reading; in FRB/US, the funds rate affects spending almost entirely through asset prices, and stock prices carry more than half. As a result, an index weighted by window co-movement nearly coincides with indexes weighted by model spending effects and by GDP growth. One point of such an index is associated with a fall in output over the following year of about the size the model assigns to one point of policy. The indexes part only when the dollar moves against stocks.

**Introduction arc.**
1. Question: through which asset prices does policy reach spending? Many macro models answer "the short rate and the term structure"; equity prices are absent or minor [secondhand: to verify which models, N10].
2. Result: markets and FRB/US both say equities and long rates, in similar proportions. Equities are 0.40 of a one-point market reading [window]; 53-60 percent of the FRB/US reading of a hike, whose own funds-rate weight is 0.009 [model].
3. Approach: First, weights from window co-movement (policy-news factor). Second, the same assets weighted by FRB/US spending effects, and GS. Finally, a quarterly VAR with the output gap, benchmarked against FRB/US under the matched funds-rate path.
4. Literature after: equity responses to policy news (Bernanke-Kuttner; Gurkaynak-Sack-Swanson; Bauer-Swanson) [secondhand]; wealth and cost-of-capital channels; FCI literature (Hatzius et al.; Ajello et al.; Caballero-Simsek).

**Sections.**
1. Introduction.
2. What policy moves: window responses (+0.53 pp 10-year, -7.8 percent equities, +4.2 percent dollar per point) and the market weights; the share of each asset in a one-point reading, with intervals.
3. What moves spending: FRB/US. A hike works through asset prices; the share of each asset in the index reading at 1, 4, 8 quarters; the funds rate's own weight.
4. The two agree: weights side by side (0.61/0.56; -0.051/-0.031; 0.065/0.098), GS alongside; history 1973-2026 (correlations 0.94-0.99); equity valuation's share of the variance.
5. Effects on activity: the VAR (GDP lagged; generalized response as the other bound); FRB/US under the matched funds-rate path; agreement at one year, the VAR fading after.
6. Where they part: the dollar (Figure 1 of the current paper; January 1998; 1998-2001; 2022-24).
7. The neutral level, short (2008-09; FCI*).
8. Conclusion.

**Main exhibits.** (i) Equity-channel table: asset shares of a policy move's reading, windows and FRB/US. (ii) Weights table (market, FRB/US, GS). (iii) Figure: the three level indexes 1973-2026. (iv) VAR table and figure with the FRB/US matched path. (v) Current Figure 1 (dollar vs equities).

**Current material.** Kept: weights, units, Figure 1, the episode analysis (shortened), r* section (shortened), FCI*. Moved to appendix: the composition test (Section 6) and its net-export result; the distance matrix and month counts. The Y calibration becomes a robustness row (the policy-news measure).

**Referee pressure.** (1) Is the window equity response policy or information effect? (Bauer-Swanson orthogonalized surprises already give similar weights: step 28.) (2) Is the FRB/US equity channel too large? FRB/US is one model; the claim is that markets and this model agree, not that the model is right. (3) The VAR is not identified; the claim rests on both orderings and on the FRB/US benchmark. (4) The equity share depends on the r* transformation of equities (CAPE earnings-yield gap); need the share at the nominal step too.

**Evidence still needed.** Window shares with intervals; FRB/US shares at the r* step; the literature check on models without an equity channel; the VAR moved into the package.

**Risk.** Highest payoff and the most new claims. The "many models omit equities" sentence must be backed by citations.

---

## Option (b): the agreement

**Claim.** Three ways of building an FCI in units of policy, from market co-movement around announcements, from a macro model's spending effects, and from published GDP-calibrated weights, give nearly the same index. They agree because equity valuation dominates both the policy response and the spending effect.

**Draft abstract.** Financial conditions indexes are built in two ways: by asking how asset prices respond to policy news, or by asking how asset prices move spending. I build both on the same three asset prices and the same policy unit, and add the published Goldman Sachs weights. The three indexes nearly coincide over five decades, and one point of each is associated with a fall in output over the following year of about the size a macro model assigns to one point of policy. They coincide because policy news and spending effects both give equity valuation and the 10-year yield most of the weight. They differ when the dollar moves against stocks, which is rare but not negligible.

**Introduction arc.**
1. Question: do market-based and model-based FCIs measure the same thing?
2. Result: yes, closely, in history and in effects on activity; the reason is the equity channel; the dollar is the exception.
3. Approach: First, the two methods on a common scale. Second, history and the VAR. Finally, where and why they part.
4. Literature after.

**Sections.**
1. Introduction.
2. Two methods, one scale (current Section 2.1-2.2, compressed; the identity: calibrations agree on movements in the usual proportions).
3. The indexes in history: correlations, figure, and why (variance shares, equity channel in brief).
4. Effects on activity: VAR and FRB/US benchmark.
5. Where they part: the dollar; the four-calibration distances and episodes.
6. The neutral level.
7. Conclusion.

**Main exhibits.** Weights table; history figure with correlations; VAR table/figure; Figure 1; episode table.

**Current material.** Most of the current paper stays, reorganized: Sections 2 and 5 become the core; Section 4 (why weights differ) shortened; Section 6 replaced by the VAR, composition test to the appendix.

**Referee pressure.** (1) "High correlation of positive-weighted composites of the same assets is mechanical" (Wilks): must answer with the window-vs-model weights themselves and the equity channel, which leads back toward (a). (2) Same VAR identification point. (3) Contribution may read as descriptive.

**Evidence still needed.** The VAR moved into the package; FRB/US benchmark for the market and GS indexes (N7). Less new evidence than (a).

**Risk.** Lower: closest to what is already built. The headline invites the mechanical-correlation objection.

---

## Option (c): keep the current framing (two choices: the weights and the neutral level)

**Claim (current abstract).** A reading in points of policy rests on two choices, the weights and the neutral level. Four calibrations usually agree on direction and often disagree on size; r* adds about a point to the 2008-09 tightening.

**Changes under (c).** Section 6: the VAR replaces or joins the composition test as the evidence on activity (the four indexes have similar effects at one year, about the size FRB/US assigns to one point of policy; activity does not choose among them). Equity channel as a paragraph in Section 4 ("why the market and FRB/US weights are close on equities"). Everything else as is.

**Referee pressure.** The paper's own reviewers already found the activity section weak; the VAR helps but does not settle which calibration is right, and the headline remains "they disagree about size", which the new evidence on co-movement partly undercuts.

**Evidence still needed.** VAR into the package only.

**Risk.** Lowest effort; the author's judgment (16 Nov) is that this version "is not working".

---

## Comparison

| | (a) Equity channel | (b) Agreement | (c) Current |
|---|---|---|---|
| Core claim | economics of transmission | measurement | measurement choices |
| New evidence needed | most (shares with intervals, literature) | VAR, FRB/US benchmark for three indexes | VAR |
| Current material reused | about half | most | nearly all |
| Main objection | identification of equity response; one model | mechanical correlation | headline undercut by co-movement |
| Fits JME | best [inference] | middle | as now |
