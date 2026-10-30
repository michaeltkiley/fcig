# Plan: dynamics in financial conditions indexes (distributed-lag macro index; financial response profiles) and integration of the ECB Macro-Finance FCI

Status: steps 1a-1c, 2a-2b, C1 and C2 implemented 27 Oct 2026 (results at the end); 2c and C3 not done.

Motivation: the gap test (`fci_compare/gap_test.py`) shows the macro-minus-market gap does not respond to policy surprises in the announcement window or in the same month, but does respond 6-12 months later (+0.6 to +0.9 pp per pp of surprise, se 0.3-0.5). The weighting note (`weighting_note/weighting_note.tex`, section 7) and the tutorial the user shared (sections 4-6) say why this matters:
- **Output-side lags.** If output depends on past financial conditions, the right index in levels is a distributed lag, sum_m Phi_m' dx_{t-m} / G. A static levels index is right only if the current configuration has persisted.
- **Financial-side profiles.** If policy moves financial variables with different time profiles (psi_h not proportional to psi_0), static market weights misread old shocks: m'psi_h differs from the GDP-relevant ratio.
- **What the gap can show.** Both indexes are static in current x, so the gap reveals only the second channel: (s - w)'psi_h differs from 0 for h > 0. The first channel needs a dynamic index.

---

## Step 1. A distributed-lag macro-model index (FRB/US)

**Question.** How different is a levels index that respects FRB/US's output dynamics from the static macro-model levels index? When are the differences large (after fast moves in financial variables)?

**1a. FRB/US quarterly paths.**
- Rerun `ms_fci/frbus_sensitivities.py` and `frbus_sensitivities_ext.py` (Python 3.9 venv, same exogenized lists) saving the full GDP path for quarters 1-24 for each experiment.
  - Persistent experiments: rff (yardstick), rg10, rbbbp, req, fpxr, rme, rshort_direct, phouse.
  - Add one-quarter (temporary) versions of each experiment as a check on linearity: the persistent-shift response should equal the cumulated one-period responses, Phi_k = sum_{i<=k} phi_i.
- Output: `ms_fci/frbus_paths.csv` (variable x quarter, GDP effect per unit).
- Resolve open item 4 at the same time: one definition of expectations for all partials (VAR expectations held fixed throughout, matching rshort_direct), with the free-expectations version as a sensitivity.
- Check already visible: the q4 / q8 / q12 funds-rate equivalents are not proportional across variables. Per unit, rg10 is 0.57 / 0.52 / 0.46, the BBB spread 0.13 / 0.18 / 0.19, equities 0.032 / 0.030 / 0.028 and the dollar 0.100 / 0.098 / 0.082. So FRB/US output dynamics are not common across variables. This is what the ECB paper's Assumption 1 rules out (see Part C).

**1b. Index construction (monthly; quarterly paths interpolated to months, or the index built quarterly first).** Three objects, all in pp of funds rate:

| Object | Formula | Meaning |
|---|---|---|
| Static levels index (current) | Phi_4' x_t / G_4 | gap pressure if the configuration had held for 4 quarters |
| Distributed-lag gap index (new) | [sum_m Phi_m' dx_{t-m}] / G_K | output-gap effect now of the whole financial history, in units of the long-horizon (K = 12 or 24 quarters) effect of a persistent 1 pp hike |
| Growth-impulse index (FCI-G form) | [sum_m (Phi_{m+4} - Phi_m)' dx_{t-m}] / (G_4 normalization) | same structure as FCI-G, from the FRB/US partials |

- Identity to verify numerically: distributed-lag index = static index at horizon K minus sum_m (Phi_K - Phi_m)' dx_{t-m} / G_K. The second term is the "not yet transmitted" part.
- Normalization choices to report: G_K for K = 4, 8, 12 (long-horizon K is the natural "level" unit). Also report a sensitivity where each horizon's index uses its own yardstick G_h. The note's Proposition 5 says these differ only through recent changes.

**1c. Outputs and comparisons.**
- Chart: static vs distributed-lag macro index; the "not yet transmitted" term by variable.
- Comparison of the growth-impulse version with the official FCI-G and our replication. FCI-G uses FRB/US-based weights, so this is a consistency check, and it tells us whether differences between FCI-G and the macro-model index are weights or construction.
- Recompute the gap test with the distributed-lag index in place of the static one. Hypothesis: output-side dynamics do not remove the delayed gap response, because that response comes from the financial side (Step 2).
- Correlation table (levels and 12-month changes) with MKT, GS, ANFCI, and FCI-G at matched horizons, as in `common_unit_v2.py`.

**Risks.**
- FRB/US paths beyond q12 depend on the model's policy and expectations settings, so the long-K normalization is sensitive.
- Monthly interpolation of quarterly responses.
- House prices respond slowly, so their dynamic weight may differ most from the static one.

---

## Step 2. Financial-side response profiles to policy (psi_h) and the bias of static market weights

**Question.** After a policy surprise, do the 10-year, equities and the dollar keep their impact proportions? If not, how large is the bias of static market weights for shocks of different ages, and which variables drive it?

**2a. Responses by horizon.**
- Local projections of each financial variable (10-year, 100 ln CAPE, 100 ln real dollar, plus mortgage and BBB spreads and house prices for the macro-only variables) on the NS surprise (funds-rate pp).
  - Horizons h = 0..24 months, monthly sums of surprises, controls: lags of the variable and of the surprise.
  - Also at daily frequency for h = 0..60 trading days, to see where the drift starts.
- Standard errors from Driscoll-Kraay / HAC. Joint inference across variables by stacking (seemingly-unrelated LPs) so that the covariance across variables at a horizon is available.
- Robustness:
  - GSS path factor instead of NS.
  - Jarocinski-Karadi poor-man's split (pure policy vs information shocks, from the sign of the co-movement of the surprise and equities). This matters because information effects could produce the drift.
  - Excluding 2008-09 and 2020.
  - Smooth LPs or a small VAR with the surprise as an external instrument (Gertler-Karadi style) for efficiency at long horizons.
- Output: `path_fci/psi_by_horizon.csv`, chart of psi_h / psi_0 by variable.

**2b. Tests.**
- Proportionality: H0 psi_h = a_h psi_0 for all h (a Wald test of the rank-one restriction on the stacked response matrix [psi_0 ... psi_H]).
- Bias of static market weights: bias_h = w' psi_h - lambda_h, where lambda_h is the GDP-relevant ratio for a shock of age h.
  - Under the FRB/US output model: lambda_h = s' psi_h, the macro reading.
  - Directly from data: the GDP response ratio g_h / g_0 from an LP of output on the same surprise (noisy; report with bands).
- The note's prediction to verify: (s - w)' psi_h equals the LP response of the gap at h. That is an accounting check that links Step 2 to the gap-test result.
- Under the tutorial's section 6.2: stacking B_h' theta = g_h over horizons identifies theta (the GDP weights) when the psi_h are not proportional. Report whether the rank condition holds in the data and, if so, the implied theta with bands. Expected to be imprecise; framed as an exploratory check of the FRB/US weights.

**2c. A dynamic market-based index (only if 2b rejects proportionality with economically meaningful size).**
- A Kalman filter on x_t = sum_h psi_h eps_{t-h} + u_t (a moving average truncated at H, or an AR(2) approximation of the profile) gives the filtered "policy state." Compare it with the static market index.
- Only the impact responses are precise, so this is a robustness exercise.

**Risks.**
- Monthly surprise sums are a weak instrument at long horizons (first-stage power, and our h = 6-12 standard errors are 0.3-0.5).
- Post-announcement drift and information effects.
- Overlapping-sample inference.
- The surprise series changes contracts in 2022 (Eurodollar to SOFR).

---

## Part C. The ECB Macro-Finance FCI: comparison and integration

**Sources.**
- Bletzinger, Martorana and Mistak, "Looser, tighter, clearer: a new Financial Conditions Index for the euro area," ECB Working Paper 3193 (February 2026).
- "The evolution of financial conditions in the euro area and the United States: a Macro-Finance FCI perspective," ECB Economic Bulletin 6/2026, box (same authors).
- Notes in `path_fci/lit/lit_ecb_mffci.md`.

**What it is.**
- A VAR in inflation gap, output gap and one index F_t = alpha'Z_t of financial variables. The weights alpha and the VAR are estimated jointly by maximum likelihood, with ||alpha||_2 = 1 and a generalized ridge penalty (alpha' C^-1 alpha, C = Cov(Z), lambda = 77). Variables are selected by the conditional likelihood of the macro block.
- Monthly; levels with minimal transformation (rates in percent; CAPE and exchange rate as % deviations from mean).
- Claimed to be in a unit "comparable to a policy rate"; neutral level = VAR unconditional mean.
- Euro area 2007-2025. In the box: a US version 1999-2025 with the effective funds rate, the 10-year yield, a real 2-year forward 1 year ahead, a real 5-year, a mortgage spread (over the 30-year), an A-rated corporate spread, CAPE and the nominal effective dollar.
- Reported US weights (sum of squares = 1): funds rate 0.63; two real rates about 0.45 each; 10-year about 0.40; mortgage and corporate spreads about 0.11 each; CAPE negative; dollar smallest.
- The box regresses daily changes in the indexes on Jarocinski-Karadi high-frequency shocks, as an outcome check of spillovers, not to set weights.

**Where it is similar to this project.**
1. A levels index with weights that are effects on the macroeconomy, not variance shares. It sits with the macro-model levels index (and GS / FCI-G in the "elasticity" family), not with NFCI-type factor indexes. The paper's argument against PCA mirrors our grouping.
2. Same variable families as our macro-model index: policy rate, 10-year, mortgage spread, corporate spread, CAPE, dollar. It also adds real rates, which we handle through real versions and r* adjustments.
3. Policy-rate units as a goal, and a "neutral" level (their VAR mean, analogous to our zero = sample average and r*-adjusted versions; related to Caballero et al. FCI*).
4. Uses high-frequency monetary policy surprises (Jarocinski-Karadi) with daily index changes, like our event-window work. They use them to describe spillovers; we use them to build weights.
5. Comparison with GS and FCI-G (US box) and with principal components.

**Where it differs, and what is new in this project.**
1. **The unit.** Their scale comes from ||alpha|| = 1, not from a policy experiment. In the US box a parallel 1 pp move in nominal rates (funds rate and 10-year, real rates unchanged) moves the index by about 0.63 + 0.40 = 1.0. That is close to one only by coincidence of the normalization, and a move in real rates adds up to about 0.9 more. So their "policy-rate scale" is not a funds-rate equivalent in either of our senses (output yardstick or transmission). Our project defines the unit explicitly and converts every index into it. **New:** a common funds-rate unit across methods; an MF-FCI can be converted into it (Step C2).
2. **Source of weights.** Theirs: in-sample fit of the macro VAR (a reduced-rank / multivariate autoregressive index model). Ours: (a) a structural model's partial effects (FRB/US), and (b) announcement-window responses (market weights, one-factor GLS). **New:** weights identified from policy surprises; formal conditions (weighting note) under which model and market weights agree; the gap decomposition; and its test.
3. **Dynamics.** Their Assumption 1 (linearity) requires every financial variable to have the same dynamic effect on the macro variables once scaled by alpha, at every lag, and the same scaled feedback among financial variables. In our notation: phi_i proportional to alpha for all lags i (common output-side dynamics), plus a common financial-side profile. That is exactly the restriction under which a static levels index needs no distributed lag. **New:**
   - We test that restriction. The FRB/US horizon profiles already differ across variables (Step 1a), and the gap test suggests that financial-side profiles differ (Step 2).
   - Step 1 builds the index that drops the restriction.
   - Their framework can serve as a statistical benchmark for whether the restriction costs fit.
4. **Purpose.** Theirs: forecasting and a broader stance or shadow rate for one economy. Ours: understanding how widely used indexes relate in a common unit, with no ground truth and no ranking.
5. **Identification.** Their weights reflect all sources of comovement in the sample (policy, demand, supply, financial shocks) through the VAR fit. Their structural shocks come afterwards (sign restrictions). Ours separate the policy-equivalent and output-equivalent targets explicitly.

**Integration steps (after Steps 1-2).**
- **C1. Literature.** Add WP 3193 and the box to `NOTE_PLAN.md` section 7 (closest work on policy-rate-unit FCIs; contrast on unit and dynamics). Add one paragraph to the weighting note: the MF-FCI's Assumption 1 is the common-dynamics condition, and when it holds the static index is valid.
- **C2. US MF-FCI in our comparison.**
  - (i) Approximate: apply the box's reported US weights (read off its Chart A) to our US data, building the real 2y1y-forward and 5-year real rates from Treasury yields less Cleveland Fed expected inflation (or TIPS), the A-rated spread from ICE, and the nominal broad dollar.
  - (ii) Convert to funds-rate units by the same two rules we use for the others: transmission (h = 0 response to a parallel surprise) and alpha'psi from the event window (the funds-rate content of an NS unit).
  - Add the result to `common_unit_v2.py`, and to the weights-by-group and variance tables.
  - Ask the authors (or check ECB data portals) for the exact US weights; until then, label it as an approximation.
- **C3. Re-estimate an MF-FCI-style index on US data ourselves (optional).** A three-variable VAR (PCE inflation gap, output gap, F = alpha'Z) by maximum likelihood with the norm constraint and ridge penalty, on our variable set.
  - Compare its relative weights with FRB/US s and market w: a third weighting principle in the same unit.
  - Relax Assumption 1 by letting alpha differ by lag (two index lags with separate weight vectors). The likelihood test of equal lag weights is the statistical counterpart of Step 1a.
  - Medium effort; only if C2 shows it is worth it.
- **C4. Policy-surprise check of the MF-FCI.** Its h = 0 response to NS and GSS surprises (as the box does with Jarocinski-Karadi). Its gap to the market index, decomposed as in `gap_test.py`.

**Positioning sentence for the note (draft).** "Recent work estimates the weights of a policy-rate-scaled FCI jointly with a macro VAR (Bletzinger, Martorana and Mistak 2026). That approach, like the impulse-response weights in FCI-G and our macro-model index, assumes that every financial variable affects the economy with the same dynamics once scaled. We show that this assumption is what makes a static levels index valid, test it with policy surprises and FRB/US, and place model-based, market-based and statistical indexes in a common funds-rate unit."

---

## Order and effort
1. Step 1a (FRB/US paths; about half a day of compute and code). This also settles open item 4.
2. Step 2a-2b (local projections and tests; one day).
3. Step 1b-1c (distributed-lag index and comparisons).
4. C1, then C2 (approximate US MF-FCI).
5. Step 2c and C3 only if the earlier results justify them.

Deliverables are added to `PROJECT_MEMORY.md` and `NOTE_PLAN.md` as they are completed.

---

## Results (27 Oct 2026)

**1a. FRB/US paths** (`ms_fci/frbus_paths.py`, `frbus_paths.csv`, `frbus_hike_paths.csv`).
- *Linearity.* Persistent responses equal the cumulated one-quarter responses: max difference 0.001-0.004 with z fixed, up to 0.02 with z free.
- *Profiles differ by variable.* Funds-rate equivalents per unit, q4 / q12 / q24:

| Variable | q4 | q12 | q24 |
|---|---|---|---|
| 10-year | 0.57 | 0.46 | 0.37 |
| mortgage spread | 0.42 | 0.20 | 0.11 |
| BBB spread | 0.13 | 0.19 | 0.19 |
| equities (per 1%) | -0.032 | -0.028 | -0.022 |
| dollar (per 1%) | 0.100 | 0.082 | 0.051 |
| house prices (per 1%) | -0.029 | -0.019 | -0.011 |

  So FRB/US violates common output-side dynamics: the spreads and the 10-year differ most.
- *One definition of expectations* (z fixed for all variables, open item 4): q4 weights 10-year 0.52, BBB spread 0.10, equities -0.026, dollar 0.099, mortgage spread 0.40, house prices -0.023 (small changes).
- *Full-hike spillovers keep growing.* Stocks -13% at q4 and -23% at q12; the dollar +1.6% and +2.5%. The 10-year spillover rises from 0.37 to 0.57.

**1b. Distributed-lag macro index** (`ms_fci/macro_model_dl.py`, `macro_model_dl_monthly.csv`, charts `macro_model_dl.png`, `macro_model_dl_fcig.png`).
- *Check.* The static q4 index reproduces `macro_model_levels.py` (max difference 4e-5).
- *Comparison with the static index, from 1998.* The distributed-lag index with effects complete after 12 quarters (DL_12) is much smoother: sd 0.74 against 1.16 for the static q4 index. Levels correlate 0.61; 12-month changes do not correlate (it lags).
- *Effect of recent moves not yet transmitted* (static q12 minus DL_12): sd 0.76 pp; peaks of 2.8 pp in Sep 2022 (10-year and dollar) and about 2.5 pp in early 2009 (equities, BBB); latest +0.16.
- *Growth-impulse form against the official FCI-G* (1999-2026): correlation 0.87 with the 1-year lookback and 0.83 with the 3-year lookback. This confirms FCI-G's structure is the growth-impulse form of the same FRB/US partials. Its 1-year version is essentially the 12-month change of the static index (correlation 1.00).

**2a-2b. Financial response profiles** (`path_fci/psi_by_horizon.py`, `psi_by_horizon.csv`, `psi_dl_implied.csv`, charts `psi_by_horizon.png`, `psi_daily.png`).
- *Same-month responses to a 1 pp NS surprise.* 10-year +0.63 (0.49), equities -10.9% (4.9), dollar +6.8% (1.8). The market and FRB/US readings agree: 1.36 vs 1.38; gap +0.02 (0.11).
- *Later the profiles drift apart.* Equities rebound (ratio to impact turns negative after 9 months); the dollar and the 10-year keep rising (ratios about 2-3 at 18-24 months). Proportionality is not rejected at any horizon (p = 0.17-0.84): the bands are wide.
- *Delayed gap.* The macro-minus-market gap implied by the profiles is +0.38 (0.27) at 6 months, +0.75 (0.46) at 12 and +1.83 (0.65) at 24. About 60% of it is the common variables, weighted by s - w (FRB/US gives the dollar more weight and equities less, while the dollar keeps rising and equities rebound). The rest is the mortgage and BBB spreads. The implied gap matches the direct LP of the gap index (h = 12: 0.74 vs 0.89; h = 24: 1.83 vs 1.76), closing the accounting loop with `gap_test.py`.
- *Robustness.* Same pattern with the GSS path factor (gap +0.45 at 12, +1.16 at 24), with pure-policy events only, and excluding 2008-09 and 2020.
- *Daily event-day projections* (60 trading days). The common-variable gap stays between -0.2 and 0, so the drift is a 6-24 month phenomenon. Equities fall further over the first month (-15% at 20 days).
- *GDP weights from responses at several horizons* (tutorial 6.2) are not informative. Industrial production *rises* after hawkish surprises (+3 to +9 per unit; the information effect or Fed response to news). The bootstrap bands on relative weights span zero widely.

**1c. Gap with the distributed-lag index.**
- *Implied responses* (estimated profiles x FRB/US lags; the market index passed through the hike's own lag profile; K = 4 quarters):

| Months after surprise | Macro (distributed lag) | Market (distributed lag) | Gap |
|---|---|---|---|
| 12 | 1.01 | 0.69 | 0.32 (0.25) |
| 24 | 1.83 | 0.65 | 1.19 (0.51) |

  The gap is zero on impact and up to 6 months. Output-side lags do not remove the delayed gap, as expected: it comes from the financial side.
- *Direct local projection of the distributed-lag index.* It is dominated by pre-trends (it falls after hawkish surprises), so it is not used.

**C1-C2. ECB Macro-Finance FCI** (`fci_compare/mffci_us.py`, `mffci_us_monthly.csv`, `mffci_us.png`; `lit/lit_ecb_mffci.md`; paragraph added to the weighting note; NOTE_PLAN 7.4).
- *Approximate US version* (the box's reported weights; CAPE and dollar weights bracketed by two variants; the BBB spread stands in for the A spread). It moves about 1.93 index units per parallel 1 pp move in all rates, and 1.95 (0.41) per parallel surprise in the same month. So its "policy-rate scale" is about twice a funds-rate equivalent.
- *In funds-rate units, 1999-2026.*
  - Correlation with the macro-model index 0.85 / 0.79 (variants A / B). With the market-based index 0.59 / 0.86 and GS 0.36 / 0.71 in levels.
  - 12-month changes correlate 0.62-0.86.
  - FCI-G (1-year lookback) against its 12-month change: 0.63 / 0.75.
  - The results depend on the unreported CAPE weight.
- *Policy surprises.* Same-month response to an NS surprise +1.32 (0.33); gap to the market index +0.01 (0.18). Like the macro-model index, it reads pure policy moves the same as the market index.
- *Latest* (Oct 2026, demeaned 1999-2026): variant A +1.25, B +0.01 (macro +1.02, market -0.11, GS -0.62).
- *Exact US weights* are needed before using this in the note: contact the authors or take them from the chart.
