# Q&A: the static and dynamic indexes, and the choices behind them (draft, 28 Oct 2026)

Purpose: walk through every index slowly, say plainly what each one is, list every choice that was made, and mark which choices were **my assumptions** (made without your instruction) and need your decision. Nothing new gets built until the open questions are answered. Earlier results (`DYNAMICS_PLAN.md`, Results) stay as exploratory and get revised once the choices are settled.

Labels: **[yours]** = you decided it earlier in the project; **[assumed]** = I chose it; **[open]** = a question for you.

---

## Part A. What every index is trying to measure

**Q1. What is the common unit?**
A. Percentage points of the federal funds rate: "today's financial conditions are as tight as an X pp higher funds rate." **[yours]**
That sentence can mean two different things:
- *Output equivalent:* the funds-rate move with the same effect on GDP.
- *Policy (transmission) equivalent:* the funds-rate move that markets would read as the same amount of tightening.

Both lenses are in the project. **[yours]**

**Q2. What is "1 pp of funds rate"?**
- In the macro model: a persistent 1 pp rise in the funds rate, with everything else (curve, spreads, stocks, dollar) responding as FRB/US implies. Its GDP effect is -0.45% at 4 quarters, -0.95% at 8 and -1.43% at 12. **[assumed: persistent and full transmission]**
- In the market lens: an announcement surprise worth 1 pp on the funds-rate path (NS factor; 1 NS unit = 1 pp on the 2-year yield, about 0.98 pp of funds-rate content). **[yours: NS base]**
- **[open] Q2a.** Is a *persistent* 1 pp hike the yardstick you want for the output lens, or a typical policy path (a hike that is later reversed)?

**Q3. What is zero?** The 1990-2026 sample average of each index. **[yours]** The r*-adjusted versions are alternatives. **[yours]**

**Q4. Static versus dynamic: what is the difference?**
- A *static* index applies one fixed weight to each variable's *current level*.
- A *dynamic* index also uses *past* values, because effects take time (output side) or because financial variables respond to policy at different speeds (financial side).

Part D lists the dynamic versions.

**[open] Q4a. Which question should a dynamic index in levels answer?** Options:
1. "How much is the whole history of financial conditions holding back output *now*?" (current pressure)
2. "How much would today's conditions hold back output *eventually*, if they stayed where they are?" (steady-state pressure; this is what a static index with long-horizon weights gives)
3. "How much will financial conditions subtract from growth over the *next year*, given what has already happened?" (growth impulse, FCI-G's question)
4. "How much policy-like tightening is in place?" (policy state; market lens)

The static macro-model index answers a version of question 2 at 4 quarters. FCI-G answers question 3. The distributed-lag index I built answers question 1. **I chose these without asking.**

---

## Part B. Static indexes

### B1. Macro-model levels index (FRB/US weights)

**What it is.** A weighted sum of current levels, each relative to its 1990-2026 mean. The weight on a variable is the GDP effect at 4 quarters of a persistent 1-unit move in that variable alone (others held fixed in FRB/US), divided by the GDP effect at 4 quarters of the 1 pp hike.

| Variable | Data | Weight (pp of funds rate per unit) | Status |
|---|---|---|---|
| Policy rate | effective funds rate | 0.009 per pp (direct effect; expectations held fixed) | [yours: "should be tiny"] |
| 10-year yield | nominal 10-year Treasury | 0.57 per pp (5-, 10- and 30-year moved together; mortgage and car-loan rates follow) | [assumed: parallel long end] |
| Mortgage spread | 30-year mortgage less 10-year | 0.42 per pp | [yours: added] |
| BBB spread | ICE BBB / Baa over the 10-year | 0.13 per pp | [yours] |
| Equities | 100 ln CAPE | -0.032 per 1% | [assumed: CAPE as the level; FRB/US shock is to the required return, unit = % fall in stock wealth] |
| Dollar | 100 ln real broad dollar | 0.10 per 1% | [yours: real] |
| House prices (version 2) | 100 ln price-to-rent | -0.029 per 1% | [yours: two versions; ratio was my fix for trend] |

**Choices to confirm.**
- **[open] B1a.** Horizon of the weights: 4 quarters [assumed]. Alternatives: 8 or 12. They differ by variable (10-year 0.57 / 0.52 / 0.46; BBB 0.13 / 0.18 / 0.19; mortgage 0.42 / 0.28 / 0.20).
- **[open] B1b.** Expectations in the FRB/US partials. They are now mixed: free for most variables, fixed for the policy rate. Options: all free; all fixed (10-year becomes 0.52, BBB 0.10); or keep as is.
- **[open] B1c.** Does the policy rate belong in the index at all, given its direct weight is 0.009?

### B2. Market-based index (announcement-window weights)

**What it is.** A weighted sum of current levels of the 10-year, equities and the dollar, with weights chosen so that (i) a 1-unit policy surprise moves the index by 1, and (ii) the index has the smallest noise. It is a one-factor GLS estimate of the policy factor.

**Data for the weights:** 253 FOMC announcements (USMPD, 1994-2026), intraday moves in the 10-year, S&P 500 and dollar index (DXY), regressed on the NS factor. **[yours]**

**Data for the index:** daily levels of the nominal 10-year, 100 ln CAPE and 100 ln real broad dollar. **[yours: same weights, different data]**

**Weights per funds-rate pp:** 10-year 0.60, equities -0.050 per 1%, dollar 0.064 per 1%. **[full covariance yours; diagonal as sensitivity]**

**Choices to confirm.**
- **[open] B2a.** The weights are estimated on S&P 500 and DXY moves but applied to CAPE and the real broad dollar levels. Acceptable?
- **[open] B2b.** The scale from NS units (2-year pp) to funds-rate pp: 0.98, the average of MP1 and ED4 loadings [assumed]. Alternatives: MP1 only (0.72), ED4 only (1.25), or leave in 2-year units.
- **[open] B2c.** Only three variables (no spreads, no house prices) because event-window data are limited [yours]. Keep?

### B3. GS (replication)

**What it is.** Our replication of the Goldman Sachs FCI (published weights 4.4 / 45.1 / 39.6 / 4.9 / 6.0 on the funds rate, 10-year, BBB, equities and dollar), converted at 0.945 pp of funds rate per index point. The conversion is the GS response to an NS surprise over a two-day window. **[yours: "try gs conversion via ns shocks"]**
- **[open] B3a.** Keep the single conversion, or report the range (0.69-1.27) alongside it?

### B4. FCI-G (official)

**What it is.** The Fed's index of the drag on GDP growth over the next year from past changes in financial conditions (1-year and 3-year lookbacks). Converted by dividing by 0.4525, the 4-quarter GDP effect of the 1 pp hike. **[yours: "divide by .45"]**
- It is a *flow* measure. Its level lines up with 12-month *changes* of level indexes, so it is compared on that basis [proposed; agreed implicitly in METRIC.md].
- **[open] B4a.** Confirm: compare FCI-G only with matched-horizon changes, not levels.

### B5. NFCI / ANFCI / OFR FSI

**What they are.** Statistical (factor) indexes in their own units. Converted by dividing by their same-month response to a parallel policy surprise (monthly regression on MP1 + ED4 surprises). **[assumed]** ANFCI: 0.38 index units per pp (se 0.16); OFR FSI imprecise.
- **[open] B5a.** Is this conversion acceptable, or should NFCI-type indexes be converted differently (for example by the NS factor, or with a weekly window), or be shown in their own units?

### B6. SF Fed proxy funds rate

**What it is.** Already a funds-rate level, but informative only from 2009 (equal to the funds rate before). Compared in 12-month changes. **[assumed]**

### B7. ECB Macro-Finance FCI (approximate US version)

**What it is.** My approximation of the ECB index for the US: the box's reported weights, plus **guesses** for the CAPE and dollar weights (not reported), plus the BBB spread standing in for the A-rated spread. **[assumed throughout]**
- **[open] B7a.** Should this be in the comparison at all before we have the exact weights? Options: drop it; keep it, labelled; or seek the exact weights first.

---

## Part C. How the static indexes are compared (for reference)
Levels and 12-month changes, correlations, cross-index range, episodes by the pre-specified metric, groups (rates, equities, dollar, other). **[yours]** No change proposed here.

---

## Part D. Dynamic indexes

Two separate reasons for dynamics. These are easy to mix up, and I did not separate them clearly before.

### D1. Output-side lags (macro model)

Financial conditions affect GDP with a lag, so today's GDP depends on past financial conditions too. In FRB/US the lags differ by variable: the 10-year's effect peaks early, the BBB spread's builds slowly.

**What I built (macro distributed-lag index).** Every past *change* in a variable counts with the FRB/US effect for its age. A change 6 months ago counts with the 6-month cumulative response; a change 3 years ago with the full response. **Choices I made without asking:**
1. Normalization: divide by the hike's GDP effect at K quarters (K = 4, 8 or 12), and treat effects as complete after K quarters (no further build-up or decay). **[assumed]**
2. Months mapped to quarters by interpolation; a change in month m is treated as in place for (m+1)/3 quarters. **[assumed]**
3. History before 1990 treated as one old change, so the series is reliable only from 1998. **[assumed]**
4. FRB/US paths from the existing partial experiments (persistent shifts). **[assumed]**

**[open] D1a.** Which question in Q4a should the output-side dynamic index answer? Each needs a different formula:
- Q4a-1 (current pressure): the distributed-lag index.
- Q4a-2 (eventual pressure): a static index with long-horizon weights, so no lags are needed.
- Q4a-3 (growth over the next year): the FCI-G form built from FRB/US paths. This one correlates 0.87 with official FCI-G.

**[open] D1b.** Normalization. "1 pp of funds rate" in a dynamic index could mean:
- (i) the hike's GDP effect at the same horizon;
- (ii) the effect of a hike that has been in place as long as the financial changes;
- (iii) a fixed horizon such as 4 quarters for all.

### D2. Financial-side dynamics (how markets respond to policy over time)

After a policy surprise, the 10-year, equities and dollar do not keep their initial proportions (equities rebound, the dollar keeps rising). A static index with weights from the *initial* response reads *old* policy shocks differently from new ones.

**What I did:** estimated those response paths (monthly, 0-24 months) and showed that they explain the delayed gap between the macro and market indexes. **No dynamic market index was built.**

**[open] D2a.** Do you want a dynamic market index at all? Options:
- (i) none: the static market index is a measure of *new* policy-like moves, with the caveat stated;
- (ii) a filtered "policy state" using the response paths (imprecise beyond impact);
- (iii) something else you have in mind.

### D3. The market index passed through the hike's lags (only used inside a test)

To compare the market index with the macro distributed-lag index on equal terms, I treated the market index as a funds-rate path and applied the hike's own GDP lag profile. **[assumed; built only inside the test]**
- **[open] D3a.** Is that a sensible object for you, or should the two lenses not be put on a common dynamic basis?

---

## Part E. Order of decisions proposed
1. Q2a and Q4a (what the dynamic index answers, and the yardstick): these drive everything in Part D.
2. B1a-B1c (macro static weights: horizon, expectations, policy rate).
3. B2a-B2c (market static weights).
4. B3a, B4a, B5a, B7a (conversions of the others).
5. D1b, D2a, D3a.

Once these are answered, I will restate each index as a one-line definition for you to approve, then rebuild.

---

## Answers (recorded as given)

**A1 (Q4a, 28 Oct).** Build both current pressure (1) and eventual pressure (2) as separate macro-model indexes. Also build the growth-over-next-year form (3), as a comparison for the FCI-G discussion.

**A2 (Q2a, 28 Oct).** The output-lens yardstick must be model-consistent: the reference move is the same model's persistent 1 pp hike with full transmission. For FRB/US that is the current yardstick. A VAR-based index would use the VAR's own multiplier. For now this applies to the macro-model index (which replaced the MS-style index) and its dynamic versions. To confirm: FCI-G divided by the FRB/US multiplier, since its weights are FRB/US-based. Market and GS conversions use the transmission lens, so no multiplier is involved.

**A3 (B1a, 28 Oct).** Eventual pressure: the main index uses 4-quarter weights. 8 and 12 quarters are robustness checks, reported separately, not side by side throughout.

**A4 (28 Oct).** FCI-G is divided by the same FRB/US multiplier as the macro-model index (0.4525, the 4-quarter GDP effect of the hike).

**A5-A7 (B1b, 28 Oct).** The user asked for a model-consistent-expectations experiment:
- funds rate under the inertial Taylor (1999) rule;
- 1-unit shifts held for 4 quarters, then no shocks;
- other financial variables held at baseline throughout (answer 6);
- at least 200 quarters.

Results: `ms_fci/frbus_mce.py`, `frbus_mce.csv`. Convergence was checked at 240 and 300 quarters (`frbus_mce_check.py`). Model-consistent expectations raise most weights 2-3x because the temporary hike's GDP effect is smaller (-0.18% vs -0.45% at q4).
Decision (answer 7): **use the VAR-expectations weights for FRB/US-based computations.** Model-consistent weights are not the base.

**A8 (28 Oct).** FRB/US-based computations use the old design: VAR expectations, persistent shifts, funds rate fixed in the partial experiments, policy rate at its direct effect (0.009). The focus is mostly on the 4-quarter horizon.

**A9 (B1c, 28 Oct).** Keep the policy rate in the macro-model index (weight 0.009). The note will say its direct effect is tiny and that the funds rate works through the other financial variables.

**A10 (B2a, 28 Oct).** Market weights estimated on announcement-window moves in the S&P 500 and DXY are applied to daily levels of 100 ln CAPE and 100 ln real broad dollar, as now.

**A11 (B2b, 28 Oct).** The market index stays in NS units (pp of the 2-year yield), with no rescaling to funds-rate pp, and this is stated.

**A12-A13 (B2c, 28 Oct).** Base market index: three variables (10-year, equities, dollar). Robustness version: add the Moody's Baa yield (daily DBAA), with the weights from event-day changes and the index on levels. Not usable: ICE BBB (FRED only from 2023), mortgage rate (weekly), house prices (monthly).

**A14 (B3a, 28 Oct).** GS is converted by its response to NS surprises, in 2-year-yield units (about 0.96 per index point; 0.945 / 0.98), the same unit as the market index.

**A15 (B4a, 28 Oct).** FCI-G enters the comparison both ways: its level against the level indexes, and against their 12-month changes. Both lookbacks (1-year and 3-year) are compared with 12-month changes; there is no 24-month comparison for the 3-year lookback (my reading of "both with 12 month changes").

**A16 (B5a, 28 Oct).** NFCI and ANFCI are converted by their weekly response to NS surprises (2-year-yield units). For the OFR FSI (daily), my reading is the same weekly window, for consistency (to confirm).

**A17 (B7a, 28 Oct).** Drop the approximate ECB US index. Instead, implement the ECB Macro-Finance FCI method (Bletzinger, Martorana and Mistak 2026; cited as the method) on our preferred data: an index inspired by theirs that differs because the data differ. Its specification choices are asked one by one (questions 18 onward).

**A18 (28 Oct).** Our version of the ECB method uses the macro-model index variables: policy rate, 10-year, mortgage spread, Baa/BBB spread, CAPE, real broad dollar; house prices (price-to-rent) in a second version.

**A19 (28 Oct, corrected).** Macro block: PCE inflation gap and unemployment gap (unemployment less CBO's natural rate). No output gap, since the data are monthly. (My option 3 had read as including both gaps.)

**A20 (28 Oct).** Inflation gap: core PCE (12-month, less 2%) is the main version; headline PCE is the robustness check.

**A21 (28 Oct).** Estimation sample 1990-2025, with all of 2020 dropped from the likelihood.

**A22 (28 Oct).** Lag length chosen by BIC on our data.

**A23 (28 Oct).** No ridge penalty to start, with standard errors reported. Reconsider only if the weights show problems; with spreads (rather than many rate levels) and fewer rate series, collinearity may matter less.

**A24-A25 (28 Oct).** Model for our version of the ECB method:
- a VAR in the core PCE inflation gap, the unemployment gap and every financial variable separately;
- in the inflation-gap and unemployment-gap equations, lagged financial variables enter only through the index F = alpha'Z (same alpha at every lag);
- the financial-variable equations are unrestricted;
- alpha is estimated jointly with the VAR by maximum likelihood.

Unit: the funds rate held +100 bp for 12 months in the VAR. Within-month effects are generalized impulse responses; lags work through the VAR. The yardstick is that experiment's effect.

**A26 (28 Oct).** The yardstick and weights in this VAR use the unemployment gap, converted to output terms with an Okun's-law factor of 2 (output gap = -2 x unemployment gap). The factor cancels in the weights but makes the yardstick comparable with FRB/US's GDP effect.
