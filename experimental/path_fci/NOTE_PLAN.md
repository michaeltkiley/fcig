# Plan for a short note: how different financial conditions indexes relate, in funds-rate units (revised 22 Oct 2026)

Status: planning document. Revised after a conceptual walk-through of the weaknesses of the first plan; the decisions below supersede the earlier version (which framed the note around a new market-weighted FCI and a "level-vs-event" validation against policy-path proxies; that framing was dropped). Literature was checked by web search on 22 Oct 2026 (abstracts and a few fetched pages, not full texts); flags in Appendix A: V = verified, P = partly, U = unverified. No numbers are quoted from sources not seen.

## 1. The question and the idea
**Question.** Many financial conditions indexes exist and are discussed in the monetary policy context (FOMC minutes and communications; to be quoted, see section 6), but how they relate to one another is unclear. What do they have in common, how and why do they differ, and what do we learn from comparing them in a common unit?

**Approach.** Convert all indexes to **federal funds rate equivalents** (the policy stance is a natural common denominator, and "equivalent to a X pp hike" is a catchy and widely understood framing), compare them in levels (base case) and changes (check), by group of variable and by episode, and add one new simple alternative built from financial-market responses to monetary policy surprises. The aim is **understanding, not ranking**: all approaches are valuable, there is no ground truth for "financial conditions", and the takeaway will be whatever the answer to the question turns out to be (it is not fixed in advance).

Motivation for the macro-model angle: there is controversy over macro models and the identification of macro effects. Alternative approaches triangulate part of the problem: a market-based lens measures how strongly policy moves financial variables (the financial block of a model) without relying on estimated output effects.

## 2. Decisions from the walk-through
1. **Purpose and ground truth.** No ground truth; the note compares and contrasts. Sensitivity is mainly *across indexes*; sensitivity inside the market-based index (GSS versus NS factor, full versus diagonal error covariance) goes in a box or appendix.
2. **Scope.** FCI-G, the GS FCI (**replicated, not the proprietary original; label clearly and report how closely the replication matches published weights and the digitized chart**), and the Chicago Fed NFCI (and its adjusted version ANFCI). Also include: the SF Fed Proxy Funds Rate (already in funds-rate units; an anchor needing no conversion) and, as the stress-versus-stance contrast, the OFR Financial Stress Index (daily, weights documented, past values never revised; replicability still to be confirmed). The Morgan Stanley-style five-variable index in `experimental/ms_fci` (FRB/US weights) is a possible extra. After the reading: exclude Bloomberg (undisclosed weights, changing variable count) and the Kansas City FSI (monthly, weights not seen); the St. Louis FSI is awkward (negative loadings on rate levels make a funds-rate equivalent ill-defined). Inclusion rule: public or replicable, long history, a different aggregation philosophy.
3. **Two lenses, both reported, both in funds-rate equivalents.**
   - *Output-equivalent*: the funds-rate move that would have the same effect on growth (FCI-G by rescaling with the model yardstick; the FRB/US full-transmission hike lowers GDP about 0.45 / 0.95 / 1.43% at 4 / 8 / 12 quarters).
   - *Transmission-equivalent*: the funds-rate move that would produce this configuration of rates, equities and the dollar (market-based).
   They are two factors of one product, (how much a hike moves variable j) x (how much j moves output); event-window data measure the first well; models supply the second, where the controversy lies. Comparing model-implied spillovers with event-window responses tests the model's financial block.
4. **A priori transmission variables** (Boivin, Kiley and Mishkin, Handbook of Monetary Economics chapter): interest rates broadly construed (including corporate rates), equity prices, exchange rates. Focus on these because they are the transmission channels and the event-window data cover them. Other channels (credit supply, house prices) are acknowledged.
5. **Source-agnostic unit.** The equivalent is a "tightening equivalent": it does not claim that the stance changed or that policy caused the move. A sentence says so.
6. **Variable groups for the by-group comparison:** rates (**including the policy rate itself, Treasury and mortgage rates, and corporate yields and spreads**), equities, dollar, other (volatility, leverage, housing, oil, etc.). Each index's variables are mapped to groups a priori (NFCI via its published loadings; volatility goes to other). This also removes the BBB sign puzzle as a presentational issue (it arises only when corporate yields are split into a Treasury piece and a spread piece); corporate rates in the market-based lens are TBD on data availability, results and storytelling needs.
7. **Unit and base lens.** The unit is a *parallel* 1 pp shift in the policy rate path. **NS policy news is the base lens** (not orthogonalized to MP1, so it contains target news and acts like a tilted level shock: near-term futures move about 60% as much as the year-ahead rate; scaled to the 2-year yield, so a rescaling to the parallel unit is needed); **GSS path factor is robustness** (orthogonal to MP1 by construction: a pure forward-guidance twist). The parallel unit can be built from the two GSS factors (target plus enough path) or by rescaling NS; NS and GSS correlate 0.98 in the sample, but their weights differ (10-year about 0.6 versus 0.97).
8. **Raw surprises as announced.** Information effects and the 2022 Eurodollar-to-SOFR change in ED4 are acknowledged in one paragraph with the literature (Nakamura-Steinsson; Jarocinski-Karadi; Bauer-Swanson; Miranda-Agrippino-Ricco, to be verified) and set aside for this analysis.
9. **Levels as the base comparison, changes as a check; zero = the sample average, on a common reference window.** Report correlations and slopes in the common unit (slopes carry amplitude information that correlation does not), and look at weekly frequency for NFCI. Shared trends can inflate level correlations, so changes are the companion check.
10. **Episodes chosen from the data:** periods of closest alignment and largest differences, with the metric pre-specified before looking (gap in funds-rate equivalents in levels and in 1-year changes; direction as well as size). Each divergence is mapped to a taxonomy entry: variables included, weights, units and normalization, frequency and revisions, horizon. Policy-versus-other decomposition of index movements is **out of scope** (one-line extension).
11. **Honest labeling.** The market-based weights are "less dependent on a macro model, more on a statistical model", not model-free; include an assumptions table by approach (FCI-G: macro model output effects with partial effects; GS: regression weights; NFCI: statistical factor model; market-based: surprise measure, event-window identification, noise structure).
12. **Data constraints stated openly.** Credit spreads, housing and oil are not in the event-window set; look for intraday corporate yield or bond-ETF/CDS data; otherwise say so. About 250 events: carry sampling bands and treat gaps inside them as non-findings.

## 3. Proposed structure (revised 29 Oct 2026; about 8 pages, 5-6 figures, 2-3 tables)
1. **Introduction:** the question, motivation from policy communication (FOMC quotes), preview of the answer.
2. **What the indexes purport to do:** Table 1 (variables, weights, units, sign, horizon, frequency, revisions, source of weights) for FCI-G, GS (replicated), NFCI/ANFCI, the SF Fed proxy, the macro-model index and the market-based index.
3. **Two lenses and a common unit** (from the weighting note, `weighting_note/weighting_note.tex`):
   - *Output lens:* funds-rate pp with a model-consistent yardstick (FRB/US: persistent 1 pp hike, VAR expectations, 4 quarters).
   - *Transmission lens:* pp of the 2-year yield per NS policy-news unit.
   - When impulse-response and market weights agree; the gap between them is non-policy movement.
4. **Static and dynamic indexes:**
   - eventual pressure (static levels index, main);
   - current pressure (distributed lag on demeaned levels): appendix only (answer 50, 30 Oct);
   - growth over the next year (the FCI-G form, matching official FCI-G at 0.87/0.85);
   - FCI-G as a flow measure.
5. **The simple alternative:** event-window responses of rates, equities and the dollar to NS policy news; one-factor GLS weights; Baa robustness (full and diagonal covariance); comparison with FRB/US weights.
6. **Comparison:**
   - levels and 12-month changes;
   - FCI-G against levels and changes;
   - the proxy funds rate;
   - groups;
   - episodes;
   - the gap test (no gap on impact, a gap after 6-24 months, traced to financial response profiles).
7. **What the data can and cannot identify (box or section):**
   - policy surprises identify financial responses, not activity responses, in post-1994 monthly data;
   - one-at-a-time LP-IV gives market-type weights;
   - the ECB-method index (estimated on our data) is predictive and spread-dominated, discussed in the text only;
   - the long-sample recursive yardstick cross-checks FRB/US.
8. **Caveats and conclusion:** no ground truth, GS replication, information effects, data coverage, units, FRB/US expectations (model-consistent weights 2-3x larger).

## 3b. Structure after answer 51 (30 Oct 2026): r* case is the baseline [section outline is a proposal; the baseline and the walk-through are the user's decision]
1. **Introduction:** question, motivation (FOMC quotes), preview: the main index is the market index (our new idea; a simple, transparent benchmark), measured relative to r*
   in the baseline; it is compared with other approaches: macro-model indexes (FCI-G and our FRB/US levels version) and GS (answer 52).
   The market index comes as a level and a flow (its VAR forward impetus, 12-lag VAR; 4 lags as check), paralleling FCI-G (answers 53-54).
2. **What the existing indexes do:** Table 1 (FCI-G, GS, NFCI/ANFCI, SF Fed proxy); all are nominal-rate based.
3. **Two lenses and a common unit:** output lens (FRB/US yardstick; market VAR as a model-independent check) and transmission lens (NS policy-news units).
4. **Construction, step by step:**
   - 4.1 nominal: macro-model (FRB/US) and market-based indexes; eventual pressure and forward impetus;
   - 4.2 why nominal is not enough: valid only with low, stable inflation and expectations and a constant r*; neither holds over 1973-2026;
   - 4.3 real: matched-horizon expected inflation (Cleveland, Livingston before 1982), back to 1973;
   - 4.4 r* (baseline): every implicit real rate (policy rate, 10-year, BBB and mortgage yields, earnings yield) as a gap to r* (Laubach-Williams one-sided; Kiley check);
   - what each step changes (little for real since 1990, more in the 1970s; a lot for r* after 2008), and the cross-index agreement at each step (range 1.16 -> 0.95 -> 0.87).
5. **The market alternative:** event-window weights, one-factor GLS; comparison with FRB/US weights.
6. **Where our indexes sit relative to existing ones, like for like at each step (building-block approach; user correction to answer 51):**
   - nominal: ours against the existing nominal indexes (published FCI-G, GS, NFCI/ANFCI, proxy funds rate);
   - real: ours against real versions of the others (GS and FCI-G replications with real rates);
   - r* (baseline): ours against r*-adjusted versions of the others (GS and FCI-G replications with r* gaps; NFCI/ANFCI unchanged);
   - each step: levels, 12-month changes, groups, episodes; FCI-G against forward impetus.
7. **What the data can identify (box):** policy surprises identify financial responses, not activity responses; unemployment local projections (changes, not levels; scales consistent;
   FCI-G scale holds 1974-2026, not 1990-2026; small out-of-sample gains; r* versions predict better).
8. **Caveats and conclusion:** r* uncertainty (LW vs Kiley), expected-inflation measurement before 1982, GS and FCI-G replications, FRB/US expectations, no ground truth.
Appendix: current pressure (answer 50); model-consistent-expectations weights; nominal and real versions of every table.
Work implied: none new for section 6; the nominal (metric_v3), real (compare_real) and r* (compare_rstar) comparisons are already like for like. The published FCI-G enters the nominal step only.

## 3c. Outline adopted for now (answer 55, 30 Oct 2026; supersedes the section order in 3b)
1. **Introduction:** question, FOMC motivation, preview: a simple, transparent market index (level and flow), measured relative to r*.
2. **Existing indexes:** FCI-G, GS, NFCI/ANFCI, proxy funds rate (Table 1).
3. **The market index:** 3.1 weights from announcement-window responses to NS policy news (rates, equities, dollar; one-factor GLS; 2-year-yield units);
   3.2 the flow: 12-lag VAR with unemployment, yardstick, forward impetus (FCI-G's form).
4. **From nominal to real to r*:** why nominal is not enough; matched-horizon expected inflation back to 1973; gaps to r* (LW main, Kiley check); what each step changes.
5. **A macro-model comparison index:** our FRB/US levels version; when market and model weights agree and why they differ (non-policy movements; weighting note).
6. **Comparison, like for like at each step** (nominal, real, r*): market index and forward impetus against FCI-G, the FRB/US index, GS and ANFCI; levels, 12-month changes,
   groups, episodes.
7. **What the data identify (box):** NS surprises identify financial, not activity, responses; unemployment local projections (4h).
8. **Caveats and conclusion.**
Appendix: current pressure; model-consistent-expectations weights; full tables at each step.

## 3d. Headline message (answer 56, 30 Oct 2026)
- A simple market index, built from how markets respond to policy news, tracks the main published indexes once all are measured on the same basis.
- Measuring rates relative to r* matters for long time spans.
- The market index is more data-driven and less model-dependent than FCI-G, at the cost of less rich data (rates, equities, dollar); the cost appears worth it.
- Approaches still differ enough to create policy uncertainty; no one measure is likely best.
- Problems to highlight: FCI-G has no level (flow only); GS is nominal and proprietary.
- The market index is closer to GS than to the macro-model indexes (level correlations: market-GS 0.96-0.99, market-FRB/US 0.79-0.95, depending on sample and zero point).

## 4. Work items (in rough order)
1. **Done (22 Oct):** read Arnaut-Bauer (2024) and Aramonte-Rosen-Schindler (2013) in full (neither converts any index to funds-rate equivalents; see section 7); read the Boivin-Kiley-Mishkin working paper version (the Handbook text itself is still unread); established which FCI Caballero-Simsek use (FCI-G). Notes: `lit/` folder.
2. **Done (22 Oct):** collected and verified 62 quotes from FOMC minutes, transcripts, press conferences, speeches and Fed publications (`lit/lit_fomc_quotes.md`; strongest listed in section 7.1; page numbers and three attributions still to confirm).
3. Settle the series: the official FCI-G (compare with the repo replication), the GS replication and how well it matches, NFCI and ANFCI (weekly; the Chicago Fed publishes an indicator-weight list and a weekly contributions file; history is re-estimated weekly, so record the vintage or use ALFRED real-time vintages), the SF Fed proxy funds rate, the OFR FSI.
4. Build the conversions: FCI-G (model yardstick, horizon q4/q8/q12), GS and NFCI by response to policy surprises (NFCI needs weekly windows or reconstruction from its components); market-based index in the parallel unit from NS (rescaled) and from the two GSS factors.
5. Variable-group mapping for each index; by-group contributions in common units.
6. Pre-specify the agreement metric and the common reference window, then run the level, change and episode comparisons; carry sampling bands.
7. Model-implied versus event-window responses (financial block) table.
8. Intraday corporate yield data search; decide the treatment of corporate rates.
Effort: about 3-5 weeks part time (the NFCI conversion and the series settlement are the uncertain parts).

## 4b. Progress and results so far (22 Oct 2026; details in `experimental/PROJECT_MEMORY.md`)
Built (experimental folders `path_fci`, `ms_fci`, `fci_compare`): the market-based index (NS base, GSS robustness), the macro-model levels index (FRB/US weights; policy rate, 10-year, mortgage spread, BBB spread, equities, real dollar, with and without house prices; nominal and real), GS conversion to funds-rate units via the NS shock (0.95 pp per point; range 0.69-1.20), a first common-unit comparison with a pre-specified metric (`METRIC.md`, with a logged deviation: the h=0 same-month conversion replaces the unusable 3-month one), correlation tables by start year, a decomposition of the GS versus macro-model difference (weights 78-96% of variance against real data, data and coverage smaller; dollar and equity weights matter most because those variables swing widely), a comparison with the SF Fed proxy funds rate, and the finding that FCI-G is a flow measure whose level matches the macro-model *change* over its own lookback horizon (correlation 0.84-0.93 for the 1-year lookback). Implications for the note: compare FCI-G with level indexes through matched-horizon changes, report the conversion range for GS, and treat the proxy funds rate as the anchor from 2009. Remaining: NFCI conversion, adding ANFCI, the proxy and the OFR FSI to the comparison, the corporate-yield treatment, and consistent FRB/US partials.

## 4c. Progress 23-29 Oct 2026 (details in `experimental/PROJECT_MEMORY.md` 3b-3d and `experimental/INDEX_QA.md`)
- **Weighting note** (LaTeX) and review of the user's tutorial.
- **Index definitions settled** by a one-question-at-a-time Q&A (answers 1-45) and rebuilt (`ms_fci/macro_model_v3.py`, `fci_compare/transmission_v3.py`, `fci_compare/compare_v3.py`).
- **Work items:**
  - Done: item 3 (series settled: official FCI-G, GS replication, NFCI/ANFCI, proxy, OFR, which failed conversion); item 4 (conversions); item 7 (model vs event-window table, in `gap_test`/`psi_by_horizon`).
  - Partly done: the FRB/US consistency item (one design, VAR expectations; model-consistent expectations as a reported alternative).
  - Open: item 5 (groups for NFCI); item 6 (re-run the pre-specified metric and episodes on the v3 indexes); item 8 (corporate yields; Baa robustness added instead).
- **Findings for the note:**
  - FCI-G matches the growth-impulse form of the FRB/US partials (0.87/0.85).
  - Eventual pressure and the market index agree in 12-month changes (0.95), less in levels (0.86).
  - NFCI/ANFCI are close to the others in neither levels nor changes.
  - The macro-market gap is zero on impact and grows over 6-24 months (financial response profiles differ).
  - Surprise-identified activity responses are wrong-signed or imprecise.
  - The ECB-method index is spread-dominated.

## 4d. Next steps (29 Oct 2026)
1. Re-run the pre-specified metric (range, episodes) and the group table on the v3 indexes; produce the comparison figures.
2. NFCI groups (Chicago Fed contributions) for the by-group comparison, or state that NFCI is compared only in total.
3. Draft sections 3-4 (lenses, units, static and dynamic indexes) from the weighting note and the Q&A; add a short paragraph on the ECB method (text only).
4. ~~Decide whether the current-pressure index and the growth-over-next-year index appear in figures or only in a table~~ (done: forward impetus only, answer 49; current pressure appendix only, answer 50).
5. Compile the weighting note PDF (needs a TeX engine) and fold its propositions into the note's section 3.
6. Replication script with a documented data vintage (raw/ inputs are not in git).

## 4e. Second macro lens (29-30 Oct 2026; PROJECT_MEMORY 3f)
- **Model:** a two-variable VAR (unemployment gap, market index; Cholesky with unemployment first). Working version estimated 1973-01..2026-09 with 2020 dummied; 4 and 12 lags both kept (BIC 5 shown too).
- **Evidence:**
  - The market index Granger-causes unemployment (p 0.0001-0.002).
  - The unemployment response to a 1-unit tightening is significant from month 3 to 36 (bootstrap 95%).
  - Yardstick at 12 months: 0.23 (4 lags) to 0.51 (12 lags) u pp, i.e. -0.45% to -1.0% of output per market unit.
- **Indexes, in market (interest-rate) units:**
  - eventual pressure = the market index;
  - current pressure (1-year lookback; corr 0.90-0.94 with the index);
  - growth impetus: forward (FCI-G's definition) only (answer 49, 30 Oct); realized impetus dropped.
  - Correlation with FCI-G: forward 0.56-0.73, realized 0.44-0.64; the ranking depends on how long effects keep building (lag length).
- **Role in the note:** a model-independent output lens beside FRB/US for the comparison with FCI-G; FRB/US's slower transmission explains why FCI-G looks like a 12-month change. Goes in section 4 (static/dynamic) and section 7 (identification).
- **Next:**
  - ~~decide the impetus concept~~ (done: forward, answer 49);
  - consider adding inflation (3-variable VAR);
  - put the market lens and FRB/US side by side in output space (current pressure and impetus vs FCI-G);
  - draft the corresponding note text.

## 4f. Real-rate case (30 Oct 2026; `experimental/real_case/REAL_QA.md` R1-R17, PROJECT_MEMORY 3g)
- **What changes:** every index uses real interest rates and runs from 1973-74 (long data level-matched to the project series at 1990-92).
  - Expected inflation: Cleveland Fed model from 1982, Livingston before (level-adjusted, blended over 1982); matched horizons (policy rate - 1-year, long rates - 10-year).
  - FRB/US indexes: real policy rate and real 10-year; FRB/US weights and yardstick unchanged; house prices as the deviation from a trailing 15-year average.
  - Market index: existing announcement-window weights applied to the real 10-year (implicit assumption: announcement-window moves in the nominal 10-year are real-rate moves).
  - GS replication: Goldman weights on real rates and the real dollar.
  - FCI-G: published series kept as benchmark; a monthly replication from 1973 with all variables real is the real-case FCI-G (nominal monthly version matches the published series at 0.99).
  - NFCI/ANFCI unchanged; conversions unchanged; NFCI/ANFCI shown from 1990 in comparisons.
  - Zero point: 1973-2026 mean (1990-2026 as a check).
- **Results:**
  - Over 1990-2026 each real index correlates 0.94-0.98 with its nominal counterpart (levels), 0.98 in 12-month changes: the real-rate switch is a robustness result, not a new picture.
  - The indexes agree more with real rates: cross-index range 0.95 on average over 1990-2026 (1.16 nominal).
  - 1974-2026: FRB/US, market and GS indexes correlate 0.94-0.99 in levels; the widest gaps are 1977-81 and 2000 / 2024-26, both mainly equity valuation (the market and GS indexes weight CAPE more than FRB/US).
  - FCI-G (all real) tracks 12-month changes of the level indexes (0.90-0.95), not their levels (about 0.3), as in the nominal case.
  - Market output VAR on the real market index: almost identical to nominal (yardstick 0.235 at 4 lags, 0.501 at 12; significant months 2-36).
  - The 1970s: nominal FCI-G shows tightening in 1974 and 1979 that the real version does not (rate increases matched expected inflation).
- **Proposed role in the note [proposal, to be confirmed]:** a robustness subsection of section 6 (comparison) plus the long-history figure (`real_case/compare_real_levels.png`); the 1970s episodes as an illustration of why real rates matter for FCI-G.
- **Open:** the market output VAR with the real GS index and the all-real FCI-G (R14, user's emphasis).
- **Next case, r\*:** a separate set of cases building on the real case: rates as gaps to r\*, using the Kiley and the Laubach-Williams **one-sided** estimates from the **full-sample** (latest-vintage) estimation (user, 30 Oct).

## 4g. r* cases (30 Oct 2026; `experimental/rstar_case/RSTAR_QA.md` S1-S6, PROJECT_MEMORY 3g)
- **What changes relative to the real case:** every implicit real rate is measured as a gap to the natural rate r*.
  - r*: Laubach-Williams one-sided, full-sample estimates (main); Kiley one-sided (check). Quarterly, interpolated to months.
  - Gaps: real policy rate, real 10-year, real BBB and mortgage yields (where FCI-G uses yields; spreads over the 10-year are unchanged since r* cancels), and equities as the
    earnings-yield gap E/P - r* (E/P = 1/CAPE), with each index's CAPE weight converted at the average E/P (1 pp of E/P = 17.7 log points of CAPE).
  - Zero point: still the 1973-2026 mean of each variable, so r* matters through its movements over time, not its level.
  - FCI-G: r* applied to changes as well (a fall in r* with real rates unchanged counts as tightening).
  - Weights, conversions, VAR design and metric unchanged; NFCI/ANFCI unchanged.
- **Results:**
  - 1974-2026: close to the real case (levels corr 0.92-0.95 with LW, 0.96-0.97 with Kiley); same widest episodes (1975-82, 2000-01; equities).
  - 1990-2026: r* changes the picture much more than real rates did (levels corr real vs r* about 0.6; nominal vs real 0.94-0.98): LW r* falls from about 3.5 before 2008 to
    under 1 in 2009-16, so 2009-16 looks tighter and 1990-2007 easier.
  - The indexes agree more at each step: mean cross-index range 1.16 (nominal), 0.95 (real), 0.87 (r*, LW), 0.78 (r*, Kiley), 1990-2026.
  - Output lens: the r*-gap market index predicts unemployment better than the real one (Granger F 9.3 vs 4.5; yardstick 0.33 vs 0.24 at 4 lags; responses significant in months 1-36).
  - FCI-G picks up the 2008 fall in r* as tightening (1-year +2.75 against +1.84 in December 2008).
  - Latest (2026-09, zero 1990-2026, LW): FRB/US EP_4 +1.4, market +0.7, GS +0.1 (real case +0.4, -0.7, -1.1): against r*, conditions are tighter than their 1990-2026 average.
- **Proposed role in the note [proposal, to be confirmed]:** with the real case, a robustness section showing the chain nominal -> real -> r*: what each step changes (little for
  real rates; a lot for r* after 2008), the increasing agreement across indexes, and the better unemployment fit. Caveat: r* is estimated with wide uncertainty bands, and the
  conclusions for 2009-16 and today depend on it (LW vs Kiley differ most there).

## 4h. What the indexes say about unemployment (30 Oct 2026; RSTAR_QA S8-S8c, PROJECT_MEMORY 3g)
- **Design:** local projections, u(t+12) on current and lagged u and the current (and lagged) index, 1974/76-2026, 2020-2021Q1 dropped; recursive out-of-sample forecasts from 1995.
  Indexes: levels (FRB/US eventual pressure, market, GS), smoothed levels (current pressure), growth-impetus forms (FCI-G 1yr/3yr, FRB/US GI, market-VAR forward/realized impetus),
  ANFCI (1990 on); real and r*-gap versions.
- **Findings to report (modest; user: "not sure these tell us a ton, but we should report what we learned"):**
  1. Changes, not levels: unemployment responds to recent changes in financial conditions; level indexes and current pressure add nothing once lags of u are included.
  2. Growth-impetus forms carry the information and agree in scale once units are matched (FCI-G vs FRB/US GI via the 0.4525 yardstick; the 12-lag VAR's forward impetus vs its own
     yardstick); r* versions beat real versions.
  3. FCI-G's scale (about 0.5 on the unemployment gap per +1) holds over 1974-2026 but not over 1990-2026 for the published series.
  4. Out-of-sample gains are small (best 12% lower RMSE, r* FCI-G) and not significant; they come from before 2008 and reverse after 2021.
- **Place in the note [proposal]:** a short box or subsection in section 7 (what the data can identify), with one table (in-sample gain and out-of-sample ratio by index family)
  and one figure (FCI-G response profile, 1974-2026 vs 1990-2026).
- **Possible extension (not started):** a common experiment (a permanent change in the underlying variables pushed through every index, responses from VARs with the path held).

## 5. Assessment of the contribution (revised)
**What the note would add.** (a) A common funds-rate unit across several widely used indexes, with comparison by group and by episode: shared understanding for communication. (b) A triangulation of the financial block of macro-model-based indexes with event-window evidence. (c) A funds-rate-unit version of FCI-G (the agent found no Fed source that provides one). (d) One more simple, transparent construction, offered as an alternative and not as a competitor.
**What is already known or close (after reading).** Arnaut-Bauer (2024): four FCIs overlaid, a decomposition of the GS FCI only, and an event study of the GS FCI only; no common unit, no cross-index comparison. Aramonte-Rosen-Schindler (2013): twelve indexes in z-scores, correlations 22-96%, predictability only with 2008 in the sample, no policy-rate unit, no event study; stance: no index is uniquely accurate. Beaton-Lalonde-Luu (2009): the one FCI expressed in funds-rate terms (about 300 bp tightening since 2007; 625 bp with another model's multiplier), so the answer is very model-sensitive. Sack-Swanson (2023): FCI response to policy-induced 2-year yield moves (units of the 2-year yield). SF Fed proxy funds rate (policy-rate units from market variables). Chicago Fed Letter (Aug 2024) discusses FCI-G versus NFCI differences qualitatively via weights. Novelty risk assessed as low to moderate: the funds-rate-equivalent, by-group, episode and model-versus-market comparison were not found in any source read, and a targeted follow-up search for conversions (sell-side, staff, central bank blogs) found only single-index or asset-price-unit versions (section 7.4); Sack-Swanson's closing paragraph is the closest published statement of the idea. The narrow contribution is the combination of a common funds-rate unit, several index families, group and episode decomposition, and a market-based benchmark.
**Likely objections.** No ground truth, so "what do we learn" needs a pre-specified metric and an explicit takeaway; the unit depends on a defined path shape and on the conversion (reported as part of the comparison); the GS series is a replication; the market-based lens covers only rates, equities and the dollar; information effects are set aside; credit is outside the event-window set.
**Weakest parts.** Conversion of NFCI (weekly, standard-deviation units, many unresponsive variables); the reach of the market-based benchmark to levels; the risk that the comparison reads as a catalogue without a clear takeaway.
**Recommendation.** Proceed as a question-driven exploratory note (novelty risk low to moderate; the targeted follow-up search is done: nothing found that compares indexes in funds-rate units); decide the headline only after items 1, 3 and 6 are done. Stop or narrow if Arnaut-Bauer or other work already contains the common-unit comparison, or if the NFCI conversion cannot be done credibly.

## 6. Venue, audience, abstract outline
Venue: FEDS Note, FRBSF Economic Letter or Liberty Street style; otherwise a short working paper or a column. Audience: monetary policy economists, central bank staff, market strategists, communicators.
Abstract outline: (1) many financial conditions indexes are used in the policy context but their relationship is unclear; (2) we express FCI-G, the GS index (replicated), NFCI and a simple market-based alternative in federal funds rate equivalents; (3) compare levels and changes by group of variable and by episode; (4) show where the indexes agree and where they differ and trace the differences to variables, weights and normalization; (5) the market-based alternative uses responses of rates, equities and the dollar to monetary policy surprises as a check on model-based weights; (6) caveats: no ground truth, source-agnostic unit, data coverage.

---

## 7. Literature review (expanded 22 Oct 2026 after reading; sources in `lit/`)
Read status: R = full text read; A = abstract or search summary only; U = unverified. Details, quotes and URLs are in `lit/lit_fci_comparisons.md`, `lit/lit_transmission_caballero_simsek.md`, `lit/lit_nfci_indexes_weights.md` and `lit/lit_fomc_quotes.md`.

### 7.1 Motivation: indexes in policy discussion (R: documents downloaded and quotes copied programmatically)
- **Different indexes give different answers.** Powell, press conference, 20 Mar 2024: "there are many different financial conditions indicators, and you can kind of, you know, see different answers to that question." FOMC minutes, 31 Jan 2024: "Indicators of broad financial conditions eased over the period, but the staff's Financial Conditions Impulse on Growth index remained restrictive." Chicago Fed Letter 498 (Aug 2024): FCI-G says conditions are "considerably tighter than the model-based expectations ... while the Chicago NFCI indicates that they have been much looser", explained through weights (a Fed publication, not an FOMC source). Bullard (2017 transcripts; 2023 article) questions the GS weights and notes that indexes use different components and weights; Yellen (28 Apr 2010) and Dudley (2017) note divergences between FCIs or the policy rate and conditions.
- **Indexes enter the narrative.** FOMC minutes, 4 May 2022: "financial conditions, as measured by many financial conditions indexes, had tightened by historically large amounts since the beginning of the year." Minutes use "financial conditions indexes" generically (May 2022, Mar 2023, Jun 2023, Sep 2023) and name the staff FCI-G (Jan 2024); FCI-G is named by Governors Kugler (2024, 2025) and Cook (2025).
- **Conditions as a policy target or stance.** Powell, Dec 2022 and Feb 2023: "it is important that overall financial conditions continue to reflect the policy restraint that we're putting in place." Dudley (2010): "monetary policy works its magic through its effect on financial conditions."
- **Closest FOMC-room precedent for a funds-rate equivalent.** Laubach (staff), transcript 31 Jan 2018: the GS and Chicago Fed indexes "give the same message", and easing "would call for raising the federal funds rate at a somewhat faster pace."
- Which indexes are named: GS (Dudley 2010; transcripts 2017-2018), Chicago Fed indexes (transcripts 2013, 2018), Bloomberg (2018), St. Louis and Kansas City stress indexes (2015-2018), FCI-G (2024-2025). Minutes for 2022-2026 and the Monetary Policy Reports never name GS or NFCI; NFCI is named in Fed sources only by the Chicago Fed itself. Caveats: page numbers not given; three Bernanke attributions to be confirmed.

### 7.2 What the indexes purport to do (primary sources)
- **FCI-G (R: Ajello et al. 2023 FEDS Note).** The contribution of financial conditions to next-year GDP growth, positive = headwind, in pp of growth; seven indicators, FRB/US multipliers for rates and equities and other models for house prices and the dollar. The note says statistical indexes "do not necessarily have a straightforward economic interpretation"; no funds-rate equivalent.
- **GS FCI (R: Hatzius 2019 slides; Hatzius et al. 2010; Arnaut-Bauer).** Levels index: funds rate 4.4, 10-year 45.1, BBB spread 39.6, equities 4.9, dollar 6.0 percent. Hatzius et al. (2010) state: "The Federal Reserve Board's macroeconomic model (the FRB/US model), together with Goldman Sachs modeling, were used to determine the weights." (the same paper builds a separate unbalanced-panel PCA index purged of growth and inflation, which excludes the funds rate and uses growth prediction only to evaluate). The Goldman rule-of-thumb claims (145 bp per 100 bp; three hikes) are secondhand only (U).
- **NFCI and ANFCI (R: Chicago Fed pages, Indicators List, Brave-Butters 2012 appendix).** 105 indicators (46 weekly, 33 monthly, 26 quarterly) in a mixed-frequency dynamic factor model, standard-deviation units (zero mean, unit SD since 1971), positive = tighter, weekly (FRED id NFCI). Weights are published for all indicators; rate levels have almost no weight (funds rate -0.08, 10-year -0.04, dollar 0.12) and the largest weights are spreads, loan-survey indicators, volatility and leverage (risk a bit over half of absolute contributions). A weekly file gives indicator and category contributions that sum to the index. History is re-estimated each week and revised, ANFCI more (ALFRED vintages unverified); the last weeks include nowcasts. ANFCI removes variation tied to activity and inflation (answers a different, conditional question).
- **Stress indexes.** OFR FSI: 33 daily variables, dynamic factor model, weights re-estimated daily but past values never revised, downloadable data (R). St. Louis FSI: 18 weekly series, PCA; rate levels enter with negative loadings (R, current coefficients unverified). Kansas City FSI: monthly (A). Bloomberg FCI: 8 or 10 variables, public weights not found (U).

### 7.3 Comparisons of indexes
- **Arnaut and Bauer (2024), FRBSF Economic Letter 2024-07 (R).** Overlays NFCI, Bloomberg, GS and FCI-G over Nov 2021-Dec 2023 (sign flip and level shift only; no common unit; frequencies left as they are; zero "not necessarily a level that is 'neutral'"). Decomposes the GS FCI by component: the funds-rate increase "made only a small contribution" to the Nov 2021-Nov 2022 tightening, which came from long rates, equities and the dollar; about a third reversed by Dec 2023. Event study (Bauer-Swanson 30-minute surprises) on the GS FCI only: a 0.1 pp surprise raises it about 0.07 index points on the day, with further increases over two weeks. The letter omits sample dates, event count, the instrument and the meaning of an index point. Closest existing work: the question and the HFI idea overlap; the funds-rate unit, levels/changes comparison, by-group and episode comparison, event studies of the other indexes, a market-based alternative and a model-versus-market comparison are not in it.
- **Aramonte, Rosen and Schindler (2013), FEDS 2013-39 (R).** Twelve US FCIs and stress indexes (including NFCI, ANFCI, Bloomberg, Morgan Stanley, St. Louis, Kansas City, Cleveland, Citi, IMF; not GS or FCI-G), all in z-scores; monthly correlations 22-96%, mostly above 70%, Morgan Stanley the outlier (22-47% with most); predictability for returns and macro variables only when 2008 is in the sample; composite from the first principal component. "None of the indexes is likely to contain uniquely accurate information" matches the note's no-ground-truth stance; the split between levels (prediction) and changes (combining) parallels the levels-base, changes-check design. No event-study evidence, no policy-rate unit.
- Other: Kliesen, Owyang and Vermann (2012), St. Louis Fed Review (A: correlations among stress indexes "high but not as high as might be expected"); Atlanta Fed macroblog (Aug 2026, R: uses FCI-G and GS alongside a policy index, no funds-rate conversion); St. Louis Fed Regional Economist, 28 Mar 2023 (R: stress indexes versus tight/loose indexes; check attribution).

### 7.4 Policy-rate and funds-rate equivalents
- **Beaton, Lalonde and Luu (2009), Bank of Canada DP 2009-11, section 6 (R).** Weights = GDP effect averaged over 4-8 quarters, normalized by the GDP effect of the funds rate: about 300 bp of tightening since 2007Q2 (350 bp on a VECM-based index), 625 bp if the VECM shocks are valued with the macro model's funds-rate multiplier. The template for the output-equivalent lens; shows large model sensitivity (so the FCI-G conversion should report the multiplier sensitivity).
- **Sack and Swanson (2023), Brookings (R through an extract; check that it names FCI-G).** VAR with high-frequency identification: a 25 bp policy-induced rise in the 2-year yield tightens the Fed's FCI by about 20 bp on impact, about 33 bp at peak (units of the 2-year yield, not funds-rate units). A transmission-lens precedent.
- **SF Fed Proxy Funds Rate (Doh and Choi 2016; Choi et al. 2022; Foerster and Martinez 2024) (R: SF Fed page).** PCA of 12 variables mapped to funds-rate levels using pre-2008 relationships; weekly. **Wu and Zhang (NBER WP 22856)** (A): the shadow rate "resembles an overall financial conditions index". Morgan Stanley (2026) policy-rate-equivalent claims: U.
- **Single-index or partial conversions found by the follow-up search (`lit/lit_followup.md`; no source converts FCI-G, NFCI and GS to funds-rate equivalents and compares them across indexes: a search-based verdict, not proof of absence):**
  - *PIMCO (Wilding and Scott, 30 Sep 2026; R on pimco.com):* FCI-G was -0.9 in 2Q 2026; with the Caballero-Caravello-Simsek FCI-star method conditions were "around 50 bp too easy", described as "illustrative equivalents" of a 70 bp rise in the 10-year yield, a 9% equity fall or a 4% dollar rise. Equivalents in asset-price units for FCI-G only, not funds-rate units.
  - *Goldman 2015 (secondhand through a Business Standard/Bloomberg article; original unseen):* an average 145 bp change in the GS FCI equated to 100 bp of funds rate (six estimates, including the Fed staff model, with "very large" uncertainty; "roughly equivalent to three 25 bp hikes"). For comparison, our GS replication and Arnaut-Bauer give about 0.7-0.8 index points per 1 pp surprise, a different concept (surprise versus persistent funds-rate change); treat only as a cross-check.
  - *Morgan Stanley (17 Jul 2026; R):* an index on the SF Fed proxy-funds-rate framework (12 variables), saying conditions tightened by "four 25 bp hikes"; one index, a different construct.
  - *CaixaBank (about 2018; R):* NFCI points per 100 bp of funds rate (about 0.10-0.13): the only NFCI-to-funds-rate ratio found.
  - *Sack and Swanson (Brookings commentary, 18 Oct 2023; R):* uses the Board FCI (FCI-G; NFCI, Bloomberg and GS in a footnote only); two-variable monthly VAR of the FCI and the 2-year yield with policy-induced 2-year-yield moves from high-frequency data as the instrument; a 25 bp policy-induced rise in the 2-year yield tightens the FCI by 20 bp on impact and 33 bp at the peak a quarter later; for 2021-23 the model implies a peak FCI rise of 3.75 pp against 2.5 pp actual. Inverting (our arithmetic): one unit of FCI-G is about 1.25 pp (impact) or 0.76 pp (peak) of policy-induced 2-year yield. Their last paragraph says the exercise "could be used to determine the policy response ... necessary to offset" an FCI tightening: the closest published statement of the note's idea, not carried out and limited to FCI-G.
  - *Chicago Fed Letter 498 (Gillet and King, Aug 2024; R, figures not seen):* regresses financial variables, FCI-G and NFCI on the funds-rate path in past tightening cycles and compares projected with actual 2022-24 values: FCI-G considerably tighter than model-based expectations, NFCI much looser; attributed to weights (long rates versus credit and funding spreads), sample length (NFCI back to 1971) and purpose; each index in its own units, no common unit or funds-rate equivalent. A Chicago Fed Insights piece (June 2024, Gillet and Brave) finds NFCI leads FCI-G by 1-2 months and flags NFCI revisions and release lags.
  - *Brave and Butters (2011, 2012; R):* no mapping of NFCI to policy-rate changes; the 2011 note says the adjusted FCI is significantly correlated with monetary policy measures "though we have not documented this here" (citing Brave and Genay 2011).
  - *Funds-rate-equivalent precedents for other objects:* Chung et al. (FRBSF Economic Letter 2011-03; R: asset purchases lowered the 10-year about 0.5 pp, equivalent to about 2 pp of funds-rate cuts by historical patterns and about 3 pp by output support), Garcia-Skaperdas (FEDS 2017-106; A: unconventional policy up to a 4 pp cut), Hatzius et al. (2010; R: the OECD FCI normalized to the GDP effect of a 1 pp rise in the real long rate), Beaton et al. (above).
- **Bauer and Swanson (2023, NBER WP 29939; R):** surprises are predictable from pre-announcement macro and financial data (R-squared about 16%; 322 announcements, 1988-2019), read as a "Fed response to news" channel, not an information effect; orthogonalizing leaves high-frequency asset-price responses largely unchanged but matters for VAR and local-projection macro estimates. So raw surprises are fine for the note's event-study use (their data are the Swanson-Jayawickrema series; the USMPD construction was not checked).
- **Bletzinger, Martorana and Mistak (2026), ECB WP 3193, and ECB Economic Bulletin 6/2026 box (R; notes in `lit/lit_ecb_mffci.md`).** Macro-Finance FCI: one linear combination of financial variables estimated jointly with a VAR in the inflation and output gaps (ML, norm ||alpha|| = 1, generalized ridge); claimed "unit and scale comparable to a policy rate"; euro area and (box) US versions, compared with GS, WA-FCI and FCI-G; daily index changes regressed on Jarocinski-Karadi shocks. The closest work on a policy-rate-scaled FCI. Contrasts: (i) its scale comes from the norm, not a policy experiment (an approximate US version moves about 1.9 index units per parallel 1 pp move in all rates; `fci_compare/mffci_us.py`); (ii) its linearity assumption is the common-dynamics restriction that makes a static levels index valid, which FRB/US violates and our tests probe (`DYNAMICS_PLAN.md`); (iii) weights from in-sample VAR fit, a third principle beside model partials and announcement-window responses.
- **Not found:** Bloomberg Economics, Goldman, JPMorgan or Deutsche Bank conversions of an FCI into hikes in 2026; the original Morgan Stanley and Goldman 2015 reports.

### 7.5 Transmission and use in policy research
- **Boivin, Kiley and Mishkin (2010) (R: FEDS 2010-26 working paper; the Handbook text is unread).** Neoclassical channels (interest rate and user cost with long rates, Tobin's q and wealth through stocks and houses, intertemporal substitution, the exchange rate) and credit channels (bank lending, bank capital, balance sheet); no explicit variable list for a stance measure; corporate spreads appear in the credit block, so placing corporate rates in the "rates" group is the note's own choice and needs a sentence of justification; the exchange-rate channel is small in net effect for the US (footnote 13); opening paragraph: the funds rate can be low while policy is restrictive through other asset prices and quantities; output and price responses weaker since the 1980s, attributed to policy behaviour and expectations, with no evidence on high-frequency financial responses (so state a stable-weights assumption).
- **Caballero and co-authors (R).** "Financial Conditions Targeting" (Caballero, Caravello, Simsek, NBER WP 33206) and "FCI-plot" (Caballero and Simsek) use FCI-G (baseline three-year lookback, quarterly, from 1990) in a 12-variable BVAR; NFCI only to splice the pre-1990 sample; the GS FCI not used; the AER 2022 "opinionated markets" paper uses no FCI. No funds-rate equivalent or mapping from policy to index units. Claims: transmission runs through financial conditions dominated by risky-asset prices; the map from rates to conditions is "inherently incomplete" (financial noise explains up to 20% of the variance of the FCI and the output gap), which supports the source-agnostic "tightening equivalent". They cite Bernanke-Kuttner (2005), Boehm-Kroner (2024) and Bauer et al.; Nagel-Xu (2024) as the dissent.
- **High-frequency identification (Appendix A).** Bauer, Bernanke and Milstein (2023, JEP; A) show FOMC surprises move a risk-appetite index built from equity, bond, credit and currency indicators.

### 7.6 Implications for the note
1. Cite Arnaut-Bauer as the event-study precursor; use their 0.07 index points per 0.1 pp (after confirming the surprise measure) as a cross-check on the GS replication; their GS decomposition (small funds-rate contribution) is consistent with the by-group view.
2. Use Aramonte-Rosen-Schindler for the z-score precedent, the "no uniquely accurate index" stance and the levels-versus-changes split.
3. Use Beaton-Lalonde-Luu as the template for the output-equivalent conversion and report the model-multiplier sensitivity; use Sack-Swanson as a transmission-lens precedent.
4. NFCI conversion: rate levels have almost no weight, so NFCI's "rates" group is small and "other" large; most indicators will not respond in 30-minute windows, so a funds-rate equivalent needs weekly windows and wide bands; record vintages (ALFRED) and treat the last weeks as provisional; include ANFCI labelled as conditional on activity and inflation.
5. Chicago Fed Letter 498 already explains FCI-G versus NFCI differences through weights, qualitatively: position the note as quantifying such differences in a common unit.
6. Motivation can rest on the verified quotes (7.1), in particular the Chair's remark that different indicators give different answers.
7. Variable grouping: justify putting corporate rates in "rates" (BKM treat spreads under credit); the dollar is justified by the Caballero-Simsek emphasis on risky-asset prices even though BKM find a small net exchange-rate effect.
8. Still to read: Brave-Butters (2011) full text and the Chicago Fed technical report; the BKM Handbook text; NBER WP 34325 text; "FCI-star" and the multi-asset paper; Bauer-Swanson (2023); Sack-Swanson raw text; Chicago Fed Letter 498; Koop-Korobilis (2014); Arregui et al. (2018); ALFRED coverage; current STLFSI4 coefficients.

---

## Appendix A. Annotated bibliography

Flags: V = verified; P = partly verified; U = unverified.

**FCI construction and use**
- V. Ajello, Cavallo, Favara, Peterman, Schindler, Sinha (2023), "A New Index to Measure U.S. Financial Conditions," FEDS Notes, 30 June 2023 (page updated Sept 2026), DOI 10.17016/2380-7172.3281; https://www.federalreserve.gov/econres/notes/feds-notes/a-new-index-to-measure-us-financial-conditions-20230630.html . FCI-G definition; no funds-rate equivalent in the note. Must engage.
- P. Ajello, Favara, Marchal, Szoke (2024), "Financial Conditions and Risks to the Economic Outlook," FEDS Notes, 20 Sept 2024 (existence confirmed by search listing; contents not read). Follow-up use of FCI-G.
- V. Hatzius, Hooper, Mishkin, Schoenholtz, Watson (2010), "Financial Conditions Indexes: A Fresh Look after the Financial Crisis," NBER WP 16150 (also US Monetary Policy Forum 2010); https://www.nber.org/papers/w16150 . PCA-based index with growth-prediction criterion; the GS FCI's weight derivation is **not** documented there as I could see (the web summaries say weights reflect GDP impact; that wording is secondhand).
- V. Hatzius (2019), "The Case for a Financial Conditions Index," Goldman Sachs Global Investment Research, 22 Feb 2019 (slides hosted by the NY Fed): weights fed funds 4.4, 10-year 45.1, BBB 39.6, equities 4.9, dollar 6.0 percent. https://www.newyorkfed.org/medialibrary/media/research/conference/2019/quantitative_tools/Post_Hatzius_FCIPresentation . The slides do not state the weight derivation in the text I extracted.
- P. Goldman Sachs 2015 note, "145 bp of index per 100 bp of funds rate" and "three hikes" (Business Standard, 12 Sept 2015, secondhand; original not seen).
- V. Arnaut and Bauer (2024), "Monetary Policy and Financial Conditions," FRBSF Economic Letter 2024-07, 4 March 2024; https://www.frbsf.org/research-and-insights/publications/economic-letter/2024/03/monetary-policy-and-financial-conditions/ . Four FCIs; event-study of GS FCI on 30-minute surprises. Closest existing work.
- V. Caballero, Caravello, Simsek (2024), "Financial Conditions Targeting," NBER WP 33206; https://www.nber.org/papers/w33206 . Theory plus calibration; empirical FCI used: U (abstract does not say).
- V. Caballero and Simsek (2025/2026), "FCI-plot: Central Bank Communication Through Financial Conditions," NBER WP 34325, CEPR DP 20680; presented at the Fed's Laubach conference May 2025. FCI used empirically: U.
- P. Caballero and Simsek, "FCI-star" (Jan 2026) and "Financial Conditions Targeting in a Multi-Asset Open Economy" (Mar 2026): listed on the MIT faculty page only; U.
- V. Caballero and Simsek (2022), "Monetary Policy with Opinionated Markets," American Economic Review 112(7): 2353-2392 (NBER WP 27313, CEPR DP 14830). Content on FCIs: U. (Cited in the brief; only the publication record was checked.)
- P. Caballero and Simsek, VoxEU column "Financial conditions matter more than interest rates: A new framework for monetary policy" (CEPR; only snippet seen; mentions FCI-G loosening in 2024).
- V. Beaton, Lalonde, Luu (2009), "A Financial Conditions Index for the United States," Bank of Canada Discussion Paper 2009-11; funds-rate equivalent of about 300 bp tightening since mid-2007 per abstract.
- V. Aramonte, Rosen, Schindler (2013), "Assessing and Combining Financial Conditions Indexes," FEDS 2013-39 (verified in repo NOTES; includes the older Morgan Stanley FCI).

**Policy-rate equivalents and shadow rates**
- V (via repo NOTES and SF Fed page). Doh and Choi (2016), "Measuring the Stance of Monetary Policy on and off the Zero Lower Bound," FRB Kansas City Economic Review 101(3); Choi, Doh, Foerster, Martinez (2022), FRBSF Economic Letter 2022-30; Foerster and Martinez (2024), FRBSF Economic Letter 2024-16; SF Fed Proxy Funds Rate page. Not re-fetched today.
- V. Wu and Xia (2016), "Measuring the Macroeconomic Impact of Monetary Policy at the Zero Lower Bound," Journal of Money, Credit and Banking 48(2-3): 253-291 (NBER WP 20117).
- V (via repo NOTES). Morgan Stanley (Tobias, 2026) article "Fed Rate Pause: What It Could Mean for Fixed Income Market." Five-variable FRB/US version: U (third-party summary).

**High-frequency identification and asset-price responses**
- V. Kuttner (2001), "Monetary policy surprises and interest rates: Evidence from the Fed funds futures market," Journal of Monetary Economics 47(3): 523-544, DOI 10.1016/S0304-3932(01)00055-1.
- V. Gurkaynak, Sack, Swanson (2005), "Do Actions Speak Louder Than Words? The Response of Asset Prices to Monetary Policy Actions and Statements," International Journal of Central Banking 1(1): 55-93 (FEDS 2004-66).
- V. Rigobon and Sack (2004), "The impact of monetary policy on asset prices," Journal of Monetary Economics 51: 1553-1575, DOI 10.1016/j.jmoneco.2004.02.004 (DOI/pages from third-party index).
- V. Rigobon and Sack (2003), "Measuring the Reaction of Monetary Policy to the Stock Market," Quarterly Journal of Economics 118(2): 639-669. Relevant to the reverse question (Fed response to financial conditions).
- V. Bernanke and Kuttner (2005), "What Explains the Stock Market's Reaction to Federal Reserve Policy?" Journal of Finance 60(3): 1221-1257.
- V. Gertler and Karadi (2015), "Monetary Policy Surprises, Credit Costs, and Economic Activity," AEJ: Macroeconomics 7(1): 44-76.
- V. Hanson and Stein (2015), "Monetary policy and long-term real rates," Journal of Financial Economics 115: 429-448, DOI 10.1016/j.jfineco.2014.11.001.
- V. Nakamura and Steinsson (2018), "High-Frequency Identification of Monetary Non-Neutrality: The Information Effect," Quarterly Journal of Economics 133(3): 1283-1330, DOI 10.1093/qje/qjy004.
- V. Swanson (2021), "Measuring the effects of Federal Reserve forward guidance and asset purchases on financial markets," Journal of Monetary Economics 118: 32-53, DOI 10.1016/j.jmoneco.2020.09.003.
- V. Bauer and Swanson (2023), "A Reassessment of Monetary Policy Surprises and High-Frequency Identification," NBER Macroeconomics Annual 2022, vol. 37 (NBER WP 29939).
- V. Bu, Rogers, Wu (2021), "A unified measure of Fed monetary policy shocks," Journal of Monetary Economics 118: 331-349, DOI 10.1016/j.jmoneco.2020.11.002 (volume number is mine; search gave pages and year).
- U. Bauer and Swanson (2023), "An Alternative Explanation for the 'Fed Information Effect,'" AER (recalled, not checked). Jarocinski and Karadi (2020), "Deconstructing Monetary Policy Surprises," AEJ: Macro (recalled, not checked). The SF Fed USMPD database citation (Bauer-Swanson or SF Fed documentation) should be taken from the database page, not recalled.

**Critiques and alternative weights**
- V. Brave and Butters (2011), "Monitoring financial stability: a financial conditions index approach," Federal Reserve Bank of Chicago Economic Perspectives 35(1): 22-43 (the brief dated it 2010; sources give 2011).
- V. Koop and Korobilis (2014), "A new index of financial conditions," European Economic Review (time-varying weights; volume/pages not confirmed).
- P. Arregui, Elekdag, Lafarguette, Seneviratne (2018), "Can Countries Manage Their Financial Conditions Amid Globalization?" IMF Working Paper 2018/015, DOI 10.5089/9781484338612.001. My search listed these four authors; the brief lists Gelos too, so check the author list. Findings not read.
- P. A euro-area FCI-G study at Banque de France following Ajello et al. (2022 as cited there; "Measuring the financial conditions impulse for the euro area," Eco Notepad, 2025): authors and exact date not captured.

## Appendix B. Items I could not find
No Fed source translating FCI-G into funds-rate terms (the 2023 note does not; search of speeches found none). The original MS five-variable index and GS FCI weight derivation remain unverified. Whether Caballero-Simsek use FCI-G, the GS index or their own measure in their empirical sections.
- FOMC minutes and communications quoting financial conditions indexes (motivation for the note): not yet collected; to be found and verified from federalreserve.gov.
- Boivin, Kiley and Mishkin, Handbook of Monetary Economics chapter on the monetary transmission mechanism: cited by the user for the variable set; to be located and read (not checked here).
- Miranda-Agrippino and Ricco on information effects and the Fed information effect more broadly: to be verified.
- (Updated 22 Oct 2026) Found: FOMC and Fed quotes (see `lit/lit_fomc_quotes.md`), the GS weight statement in Hatzius et al. (2010), NFCI weights and contributions file, Caballero-Simsek's FCI choice (FCI-G). Still not found: any funds-rate-equivalent conversion of FCI-G, NFCI or GS; the original Goldman notes; Morgan Stanley five-variable index.
- (22 Oct 2026, follow-up reading) Added to the review in section 7.4: PIMCO 30 Sep 2026, Goldman 2015 (secondhand), Morgan Stanley 17 Jul 2026, CaixaBank (c. 2018), Sack-Swanson 2023, Chicago Fed Letter 498 and the Chicago Fed Insights piece (June 2024), Chung et al. (2011), Garcia-Skaperdas (2017), Bauer-Swanson (2023). Still unseen: Goldman's original 2015 report, Morgan Stanley's original, Engen-Laubach-Reifschneider (2015; no relevant passage found).
