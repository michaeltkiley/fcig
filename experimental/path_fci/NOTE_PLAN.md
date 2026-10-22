# Plan for a short note: how different financial conditions indexes relate, in funds-rate units (revised 22 Oct 2026)

Status: planning document. Revised after a conceptual walk-through of the weaknesses of the first plan; the decisions below supersede the earlier version (which framed the note around a new market-weighted FCI and a "level-vs-event" validation against policy-path proxies; that framing was dropped). Literature was checked by web search on 22 Oct 2026 (abstracts and a few fetched pages, not full texts); flags in Appendix A: V = verified, P = partly, U = unverified. No numbers are quoted from sources not seen.

## 1. The question and the idea
**Question.** Many financial conditions indexes exist and are discussed in the monetary policy context (FOMC minutes and communications; to be quoted, see section 6), but how they relate to one another is unclear. What do they have in common, how and why do they differ, and what do we learn from comparing them in a common unit?

**Approach.** Convert all indexes to **federal funds rate equivalents** (the policy stance is a natural common denominator, and "equivalent to a X pp hike" is a catchy and widely understood framing), compare them in levels (base case) and changes (check), by group of variable and by episode, and add one new simple alternative built from financial-market responses to monetary policy surprises. The aim is **understanding, not ranking**: all approaches are valuable, there is no ground truth for "financial conditions", and the takeaway will be whatever the answer to the question turns out to be (it is not fixed in advance).

Motivation for the macro-model angle: there is controversy over macro models and the identification of macro effects. Alternative approaches triangulate part of the problem: a market-based lens measures how strongly policy moves financial variables (the financial block of a model) without relying on estimated output effects.

## 2. Decisions from the walk-through
1. **Purpose and ground truth.** No ground truth; the note compares and contrasts. Sensitivity is mainly *across indexes*; sensitivity inside the market-based index (GSS versus NS factor, full versus diagonal error covariance) goes in a box or appendix.
2. **Scope.** FCI-G, the GS FCI (**replicated, not the proprietary original; label clearly and report how closely the replication matches published weights and the digitized chart**), and the Chicago Fed NFCI (and its adjusted version ANFCI). Open to: SF Fed Proxy Funds Rate (already in funds-rate units; an anchor needing no conversion), one stress index (St. Louis Fed, Kansas City Fed or OFR) as a contrast between stress and stance, and the Morgan Stanley-style five-variable index in `experimental/ms_fci` (FRB/US weights). Exclude indexes with undisclosed weights. Inclusion rule: public or replicable, long history, a different aggregation philosophy.
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

## 3. Proposed structure (about 6-7 pages, 4-5 figures, 2-3 tables)
1. **Introduction**: the question, motivation from policy communication (FOMC quotes), preview of the answer.
2. **What the indexes purport to do**: Table 1 (variables, weights, units, sign, horizon, frequency, revisions, source of weights) for FCI-G, GS (replicated), NFCI, SF Fed proxy, market-based; assumptions table.
3. **Common unit**: conversion of each index to funds-rate equivalents (FCI-G by model yardstick, others by response to policy surprises; NFCI weekly), parallel unit, and what the unit means (source-agnostic).
4. **The simple alternative**: event-window responses of rates, equities and dollar to NS policy news; weights; comparison with model-implied spillovers (Table 2); GSS and covariance variants in a box.
5. **Comparison**: levels on a common reference (figure), slopes and correlations, by-group contributions (figure), changes as a check, episodes of closest alignment and largest divergence (figure and short stories), what the current readings and recent changes say.
6. **Caveats and conclusion**: no ground truth, GS replication, information effects, data coverage, unit definition.
Code and data to bring: `path_fci_gss_ns.py`, `path_fci_rates_variants.py`, `path_fci_changes.py`, `ms5_level.py`, `ms5_vs_gs.py`, `fcig_gs.py` and `fcig_replicate.py`, FRB/US sensitivities, the USMPD workbook, NFCI/ANFCI from FRED. Consolidate into one replication script with fixed seeds and a documented data vintage before submission.

## 4. Work items (in rough order)
1. Read Arnaut-Bauer (2024) and Aramonte-Rosen-Schindler (2013) in full and confirm what the common-unit, by-group comparison adds; read the Boivin-Kiley-Mishkin chapter for the variable set; check which FCI Caballero-Simsek use.
2. Collect FOMC minutes and communication quotes on financial conditions indexes (motivation), verified from federalreserve.gov.
3. Settle the series: the official FCI-G (compare with the repo replication), the GS replication and how well it matches, NFCI and ANFCI (weekly, revisions: real-time versus latest vintage).
4. Build the conversions: FCI-G (model yardstick, horizon q4/q8/q12), GS and NFCI by response to policy surprises (NFCI needs weekly windows or reconstruction from its components); market-based index in the parallel unit from NS (rescaled) and from the two GSS factors.
5. Variable-group mapping for each index; by-group contributions in common units.
6. Pre-specify the agreement metric and the common reference window, then run the level, change and episode comparisons; carry sampling bands.
7. Model-implied versus event-window responses (financial block) table.
8. Intraday corporate yield data search; decide the treatment of corporate rates.
Effort: about 3-5 weeks part time (the NFCI conversion and the series settlement are the uncertain parts).

## 5. Assessment of the contribution (revised)
**What the note would add.** (a) A common funds-rate unit across several widely used indexes, with comparison by group and by episode: shared understanding for communication. (b) A triangulation of the financial block of macro-model-based indexes with event-window evidence. (c) A funds-rate-unit version of FCI-G (the agent found no Fed source that provides one). (d) One more simple, transparent construction, offered as an alternative and not as a competitor.
**What is already known or close.** Arnaut-Bauer (the closest: four FCIs and an event-study of the GS FCI on surprises), Aramonte-Rosen-Schindler (comparing FCIs), the SF Fed proxy funds rate and Beaton-Lalonde-Luu (policy-rate equivalents), the high-frequency identification literature, critiques of model-based weights. The narrow contribution is the combination of a common funds-rate unit, several index families, group and episode decomposition, and a market-based benchmark.
**Likely objections.** No ground truth, so "what do we learn" needs a pre-specified metric and an explicit takeaway; the unit depends on a defined path shape and on the conversion (reported as part of the comparison); the GS series is a replication; the market-based lens covers only rates, equities and the dollar; information effects are set aside; credit is outside the event-window set.
**Weakest parts.** Conversion of NFCI (weekly, standard-deviation units, many unresponsive variables); the reach of the market-based benchmark to levels; the risk that the comparison reads as a catalogue without a clear takeaway.
**Recommendation.** Proceed as a question-driven exploratory note; decide the headline only after items 1, 3 and 6 are done. Stop or narrow if Arnaut-Bauer or other work already contains the common-unit comparison, or if the NFCI conversion cannot be done credibly.

## 6. Venue, audience, abstract outline
Venue: FEDS Note, FRBSF Economic Letter or Liberty Street style; otherwise a short working paper or a column. Audience: monetary policy economists, central bank staff, market strategists, communicators.
Abstract outline: (1) many financial conditions indexes are used in the policy context but their relationship is unclear; (2) we express FCI-G, the GS index (replicated), NFCI and a simple market-based alternative in federal funds rate equivalents; (3) compare levels and changes by group of variable and by episode; (4) show where the indexes agree and where they differ and trace the differences to variables, weights and normalization; (5) the market-based alternative uses responses of rates, equities and the dollar to monetary policy surprises as a check on model-based weights; (6) caveats: no ground truth, source-agnostic unit, data coverage.

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
