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

**A27 (28 Oct).** VAR numerator: variable j held 1 unit above baseline for 12 months, with all other financial variables held at baseline (the same partial design as FRB/US). Its effect runs only through the index.

**A28 (D1b, 28 Oct).** The current-pressure (distributed-lag) index is divided by the persistent hike's GDP effect at 4 quarters (-0.45%), the same yardstick as the static index.

**A29 (28 Oct).** The user asked to see caps of 4, 8 and 12 quarters before deciding (`ms_fci/macro_model_dl_caps.py`, `macro_model_dl_caps.png`). Decision: 4 quarters is the main version; 8 and 12 are robustness checks, possibly with a different normalization (question 30).

**A30 (28 Oct).** The 8- and 12-quarter current-pressure robustness versions are divided by the hike's effect at the same horizon (-0.95%, -1.43%). Each then pairs with the static (eventual-pressure) index at the same horizon. Timing note recorded: current pressure capped at K equals the K-quarter static index minus the not-yet-transmitted part of changes in the last K quarters. A 1-quarter cap would be close to zero, not the eventual-pressure index.

**A31 (D2a, 28 Oct).** Keep the static market index (option A) as is. There is no dynamic market index; the caveat about older policy moves is stated.

**A32 (D3a, 28 Oct).** Gap test: static macro index against static market index only. The market index is not fed through the hike's lags. The current-pressure index is described separately.

**A33 (28 Oct).** Growth-over-next-year index: both lookbacks (1-year and 3-year), as FCI-G publishes, built from our macro-model variables and the FRB/US paths and divided by 0.4525.

**A34 (28 Oct).** OFR FSI is converted by its event-day response to NS surprises (daily data), unlike the weekly window for NFCI/ANFCI.

---

## Specification for approval (one line per index, from answers 1-34)

Output lens (funds-rate pp; FRB/US old design: VAR expectations, persistent shifts, funds rate fixed in partials):
1. **Macro-model, eventual pressure (main):**
   - Index: Phi(4)'x_t / G(4) on levels demeaned 1990-2026.
   - Weights: policy rate 0.009 (small effect emphasized), 10-year 0.57, mortgage spread 0.42, BBB spread 0.13, CAPE -0.032/%, real dollar 0.10/%.
   - Second version adds house prices (-0.029/%).
   - Robustness: 8- and 12-quarter weights over G(8) and G(12), reported separately.
2. **Macro-model, current pressure:**
   - A distributed lag on demeaned levels: sum_i phi_i' x~_{t-i} / G(K), where phi_i is the FRB/US one-period effect at lag i (the change in the cumulative effect), for lags up to K quarters.
   - The lag weights sum to the static K-quarter weights. This is the same calculation as summing past changes with the effect for their age, restated in levels at the user's request (29 Oct).
   - K = 4 is main; K = 8 and 12 are robustness (each over G(K)).
   - Both house-price versions.
3. **Growth over the next year (FCI-G form):** from the FRB/US paths and our variables, 1-year and 3-year lookbacks, divided by 0.4525.
4. **FCI-G (official):** 1-year and 3-year lookbacks, divided by 0.4525. Compared in levels and against 12-month changes (both lookbacks).
5. **ECB-method index on our data:**
   - VAR: core PCE inflation gap (headline as robustness), unemployment gap, and each financial variable from item 1.
   - Restriction: the macro equations see financial variables only through F = alpha'Z.
   - Estimation: alpha by maximum likelihood; lags by BIC; sample 1990-2025 excluding 2020; no ridge at first.
   - Yardstick: funds rate +100 bp for 12 months (generalized impulse responses on impact, VAR dynamics after); unemployment-gap effect at month 12 x (-2).
   - Weights: variable j held +1 for 12 months, others at baseline.

Transmission lens (pp of the 2-year yield per NS unit):
6. **Market index:**
   - Weights: NS one-factor GLS (full covariance) on the 10-year, 100 ln CAPE and 100 ln real broad dollar, estimated from S&P 500 / DXY window moves.
   - Static only, with the caveat about older policy moves.
   - Robustness version adds the Baa yield (event-day changes).
7. **GS replication:** about 0.96 per index point (NS response).
8. **NFCI and ANFCI:** divided by their weekly response to NS surprises. **OFR FSI:** event-day response.

Other:
9. **SF Fed proxy funds rate:** 12-month changes from 2009.
10. **Gap test:** static macro index against static market index only.

**A35 (29 Oct).** Cross-lens comparisons are made as is, with the two units stated: funds-rate pp for the output lens, 2-year-yield pp for the transmission lens. Correlations do not depend on scale.

---

## Rebuild status (29 Oct)
- Built: macro-model indexes (`ms_fci/macro_model_v3.py`), transmission-lens indexes (`fci_compare/transmission_v3.py`), comparison (`fci_compare/compare_v3.py`).
- ECB-method VAR (`fci_compare/mf_var_us.py`): estimated (BIC chooses 1 lag; the index loads mainly on the mortgage and BBB spreads). **The yardstick fails:** the funds rate held +1 pp for 12 months lowers unemployment in the VAR, because the funds-rate innovation is followed by narrowing spreads (the reduced form mixes systematic policy with the cycle). Its funds-rate weights are not usable. Decision needed (question 37).
- OFR FSI conversion fails: event-day response -0.09 (se 0.57).

**A36 (29 Oct).** Baa robustness market index: report both the full-covariance version (Baa yield weight -0.25; the covariance term subtracts shared non-policy noise) and the diagonal version (all weights take the sign of their policy response; Baa +0.12). Run the ECB-method VAR with 6 lags.
- **6-lag VAR (29 Oct, `mf_var_us_p6.py`/`.log`).**
  - The index is almost unchanged: mortgage spread 0.86, BBB spread 0.49, 10-year 0.09, policy rate 0.07, equities -0.015.
  - The yardstick still fails. With the funds rate held +1 pp, by month 12 equities are +6.5%, the BBB spread -0.24 and the dollar -1.3%, so the index loosens and unemployment falls (-0.05 at 12 months, -0.16 at 24).
  - The partial effects have the right sign: mortgage spread +1.0 pp unemployment at month 12, BBB spread +0.57.
- **Identified by NS surprises (answer 37, `mf_var_us_iv.py`/`.log`).**
  - Weak instrument: first-stage F is 1.9 (1 lag) and 4.8 (6 lags).
  - 1 lag: the yardstick is still wrong-signed (unemployment -0.21 at month 12).
  - 6 lags: the right sign at month 12 (unemployment +0.09; output -0.18%), giving weights 10-year 1.10, mortgage spread 10.9, BBB 6.2, equities -0.19/%, dollar -0.10/%. But unemployment falls after month 18, and the index itself loosens by month 12 because spreads narrow.
  - Not reliable. Decision needed (question 38).
- **Long samples, recursive yardstick (answer 39, `mf_var_us_long.py`/`.log`).**
  - *1960, 4 variables:* degenerate. The index is essentially the Baa spread alone, the yardstick is near zero (-0.01% / -0.06% output at month 12), and the weights are unusable.
  - *1973, 6 variables, BIC 2 lags:* the yardstick has the right sign throughout. Unemployment +0.11 pp at month 12 (output -0.21%; FRB/US -0.45%), rising to 0.16 at 24, and the index tightens.
    - Weights: policy rate 0.29, 10-year 0.56, mortgage spread 4.1, Baa spread 9.3, equities -0.023/%, dollar -0.27/% (negative).
  - *1973, 6 lags:* similar yardstick (-0.23%). Weights: 10-year 0.19, mortgage 5.2, Baa 5.3, equities -0.12/%, dollar -0.18/%.
  - The sign of alpha is not identified (it is absorbed by the macro coefficients); the weights are unaffected.

**A41-A42 (29 Oct).** Try the Gertler-Karadi-style specification only (option A):
- the 2-year Treasury yield as the policy indicator, outside the index, entering only the financial equations;
- raw NS surprises (monthly sums) as the instrument;
- yardstick: the 2-year held +1 pp for 12 months, in NS units;
- sample 1990-2025 excluding 2020; lags by BIC, 6 as a check.

Script: `fci_compare/mf_var_us_gk.py`.
- **2-year indicator, NS instrument (`mf_var_us_gk.log`).**
  - Weak instrument again: first-stage F 4.3 (1 lag), 2.2 (6 lags).
  - 1 lag: wrong sign (unemployment -0.14 at month 12).
  - 6 lags: the right sign only at month 12 (+0.10), reversing after.
  - Same-month unemployment falls after a tightening (an information-effect pattern).
  - Not usable.
- **LP exploration (29 Oct, user away; `lp_weights/RESULTS.md`).**
  - One-at-a-time LP-IV reproduces inverse-response (market-type) weights.
  - Unemployment *falls* after hawkish NS surprises in 1994-2025 monthly data. Orthogonalized surprises turn it conventional, but it is imprecise and fragile.
  - Multi-horizon and multi-instrument LPs are unusable.
  - A long-sample (1973-2025) recursive LP gives a conventional yardstick: u +0.32 (se 0.10) at 12 months, output -0.63%. Predictive per-variable effects remain imprecise.
  - Decision pending.
- **Option 3 tried (answer 44; `fci_compare/mf_var_long_compare.py`/`.log`/`.png`).**
  - The 1973 recursive ECB-method index behaves like a credit-stress index: the Baa spread dominates (contribution sd 6.6 pp; +35 pp in late 2008); index sd 7.2 pp.
  - Correlations, levels / 12-month changes: EP_4 0.04 / 0.44, MKT 0.20 / 0.37, GS 0.54 / 0.62, ANFCI 0.67 / 0.76.
  - Same-month response to an NS tightening: -3.1 (se 2.4), i.e. it reads tightening as loosening, because the Baa spread narrows and the dollar has a negative weight.
  - The 6-lag version is similar.
  - Decision pending.

**A45 (29 Oct).** For now the ECB-method index is discussed in the text only (literature section), not in the comparison; to be reconsidered later. `compare_v3.py` updated: ECB-method index removed; Baa diagonal market version added.

**A46 (29 Oct).** Try option (b): the market index in an empirical output equation, in raw market-index units, with the non-policy part split out (`market_macro/`).
- Levels (nominal or real 10-year): the market index does not predict unemployment (a about 0, wrong sign at 24 months), so the weights explode.
- Real 10-year, 12-month flows, 1973-2025:
  - a = 0.11 (t 2.6) at 6 months and 0.19 (t 1.9) at 12; output equivalent -0.2 to -0.4% per market unit.
  - Non-policy equity moves matter (b_eq t -2.6 / -1.7; b = 0 rejected at 6 months, p 0.03); the dollar residual is insignificant.
  - Output-lens weights (h = 12): 10-year 0.32, equities -0.13/%, dollar -0.04/% (market weights: 0.61, -0.051, 0.065).
  - The flow index correlates 0.74 with FCI-G 1yr and 0.83 with the market index's 12-month change.
- 1990-2025 alone: a is wrong-signed in every variant.
- Decision pending.

**A47 (29 Oct).** The user redirected: a two-variable VAR in the market index (full index) and the unemployment gap; Cholesky with unemployment first (`market_macro/var2_mkt_u.py`/`.log`).
- The market index Granger-causes unemployment: long sample 1973-2019 p = 0.001 (BIC 4 lags), 1990-2019 p < 0.0001 (BIC 1 lag).
- Unemployment response to a 1-unit index shock at 24 months: +0.25 (long, 4 lags) to +0.66 (12 lags); +0.35 (1990-2019).
- Including 2020 weakens the Granger tests (p 0.07).

**A48 (29 Oct).** User: use the 2-variable VAR impulse response (1973-2019, 4 lags, unemployment first) for a market-index output lens in interest-rate (market) units: eventual pressure = the market index; current pressure (1-year lookback); growth impetus (FCI-G form, 1-year lookback). Built in `market_macro/mkt_dynamic.py`.
- Phi(12) = +0.254 u pp per unit (output -0.51%). Effects build within about a year, then plateau.
- So the growth impetus loads on the last few months of changes: sd 0.52; corr 0.50 with FCI-G 1yr, 0.72 with M's 12-month change.
- Current pressure: corr 0.94 with M, 0.85 with FRB/US CP_4.

**A49 (30 Oct).** Growth impetus: **forward impetus only** (FCI-G's definition: the unemployment / growth effect over the next 12 months of the past year's financial changes).
Realized impetus (12-month change of current pressure) is dropped from the note. Evidence at the time (RSTAR_QA S8c): forward impetus correlates 0.69-0.83 with FCI-G (realized
0.59-0.76) and predicts unemployment (in-sample gain 0.07-0.11, out-of-sample RMSE ratio 0.89-0.95; realized 0.04-0.06 and 0.97-1.01). Applies to the nominal, real and r* cases.

**A50 (30 Oct).** Current pressure is dropped from the note; it appears only in an appendix. The note features eventual pressure (level) and forward impetus (flow).
(Background: eventual = current + forward impetus when effects stop building after 12 months; current pressure lags eventual by about 6.5 months and has no predictive content
for unemployment, RSTAR_QA S8c.)
