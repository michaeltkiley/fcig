# Plan for a short note: financial conditions indexes in funds-rate units (22 Oct 2026)

Status: planning document only. Literature was checked by web search on 22 Oct 2026 (search-result abstracts and a few fetched pages, not full texts). Items are flagged VERIFIED (title, authors, year, venue confirmed on at least one primary or repository page), PARTLY (existence confirmed, some detail not) or UNVERIFIED. No numbers are quoted from sources I did not see.

## 1. Pitch and central claims

FCI-G (Federal Reserve Board) and the Goldman Sachs FCI both tell us how financial conditions matter for the economy, but their weights come from macro-model or regression estimates of effects on output. The note asks a different question that needs no growth model: **what would a policy surprise have to be to move core financial variables by the observed amounts?** Event-window responses of the 10-year yield, equities and the dollar to FOMC path/news surprises give weights; combined by a one-factor estimator they yield an index in policy-path units (pp of a year-ahead rate path) and, for FCI-G, a model-based conversion into funds-rate units (growth units divided by the FRB/US GDP effect of a funds-rate hike).

Claims the note can defend (each needs the checks in section 4):
1. FCI-G converts to funds-rate units with a one-line rescaling, but the result depends on a stated yardstick (full-transmission hike, FRB/US, horizon).
2. Market-implied weights roughly agree with FRB/US weights for equities and the dollar and are larger for the 10-year (about 0.6-1.0 vs 0.57 per pp), with a wide band. Each of the three carries about a third of the policy signal.
3. The GS FCI's published weights (about 85% on the 10-year and BBB spread, per the 2019 Hatzius slide) are very far from the market-implied split, even though the indexes correlate 0.88-0.92 in levels. High correlation hides large weight differences.
4. Credit spreads cannot be put in the market-based index (they narrow after hawkish path surprises), which is itself a finding about what policy-driven conditions look like.

## 2. Literature review plan (full annotated list in Appendix A)

- **Primary sources on what the indexes purport to do.** Ajello et al. 2023 FEDS Note (FCI-G: FCI-G_t = log GDP_{t+4} - log GDP_t contribution, positive = headwind, units pp of next-year GDP growth, seven variables, FRB/US multipliers for rates and equities, other models for house prices and dollar, 3-year lag window; the note gives **no funds-rate equivalent**). Hatzius et al. 2010 (NBER 16150) and Hatzius 2019 slides (GS weights: funds rate 4.4, 10-year 45.1, BBB 39.6, equities 4.9, dollar 6.0 percent).
- **Users in monetary policy research.** Caballero-Simsek-Caravello, "Financial Conditions Targeting" (NBER 33206, 2024); Caballero-Simsek "FCI-plot" (NBER 34325); their VoxEU column (cites FCI-G loosening in 2024). I could not establish which empirical FCI the 2024 paper uses (abstract does not say) and could not read the AER 2022 paper's content: **must read before the note says anything about them**. Arnaut-Bauer (FRBSF EL 2024-07) is the closest use: it compares four FCIs and regresses the GS FCI on high-frequency policy surprises.
- **Closest work on policy-rate equivalents.** SF Fed Proxy Funds Rate (Doh-Choi 2016; Choi-Doh-Foerster-Martinez 2022; Foerster-Martinez 2024), Wu-Xia shadow rate, Beaton-Lalonde-Luu 2009 (Bank of Canada; FCI in funds-rate terms, about 300 bp tightening since mid-2007), Goldman's 2015 rule of thumb (145 bp of index per 100 bp of funds rate, secondhand), Morgan Stanley (Tobias, 2026, 12 variables, SF Fed framework; verified via repo NOTES).
- **Identification of surprises and asset-price responses.** Kuttner 2001, GSS 2005, Rigobon-Sack 2004, Bernanke-Kuttner 2005, Gertler-Karadi 2015, Hanson-Stein 2015, Nakamura-Steinsson 2018, Swanson 2021, Bauer-Swanson 2023 (NBER Macro Annual), Bu-Rogers-Wu 2021. Must engage: Swanson 2021 (forward guidance moves short yields, asset purchases long yields; effects on stocks, corporate yields and exchange rates), Hanson-Stein (long real rates respond to policy, via term premia), Gertler-Karadi (credit costs respond more than the policy rate, via term and credit premia), and the information-effect literature (Nakamura-Steinsson; Jarocinski-Karadi UNVERIFIED), since the BBB sign puzzle is probably an information/risk-premium effect.
- **Critiques of model-based weights.** Brave-Butters 2011, Hatzius et al. 2010 (principal components with a growth-prediction criterion), Koop-Korobilis 2014 (time-varying weights), Arregui et al. IMF WP 2018/015. Aramonte-Rosen-Schindler 2013 (FEDS 2013-39) compares FCIs. I did not read the substance of the critiques beyond abstracts.

Results the note must engage: Arnaut-Bauer (event-study response of GS FCI to surprises: 0.1 pp tightening raises GS FCI by about 0.07 on the day, per the web summary); Beaton et al. (prior funds-rate-equivalent of an FCI); Doh-Choi (prior policy-rate equivalent of market conditions, off ZLB, without macro model); Goldman 2015 rule of thumb.

## 3. Proposed structure (about 6-7 pages, 4 figures, 2 tables)

1. **Introduction and motivation** (0.75 page): index weights come from models; what is a policy-rate equivalent; contribution.
2. **How FCI-G and GS are built** (0.75 page). Table 1: variables, weights, units, sign, horizon, source of weights, for FCI-G, GS, SF Fed proxy, MS-style (repo `experimental/ms_fci/NOTES.md` has the comparison table).
3. **Route 1: model-based conversion** (1 page). FCI-G (pp GDP growth, headwind positive) divided by the GDP effect of a 1 pp full-transmission hike (FRB/US: 0.45 / 0.95 / 1.43 at 4 / 8 / 12 quarters) gives funds-rate equivalents; show the series since 2020 from the repo's FCI-G data and the sensitivity of the answer to horizon (the FCI-G is a one-year-ahead growth contribution, so the q4 yardstick is the natural match). Figure 1: FCI-G in funds-rate units against the actual real funds rate gap. Data: `experimental/ms_fci/frbus_sensitivities.csv`, FCI-G series in repo (`multipliers.csv` and daily files).
4. **Route 2: market-based weights** (1.5 pages). Event-window design (USMPD, 253 events, GSS path and NS news factors), one-factor weights. Table 2: weights with bootstrap bands for GSS, NS, diagonal variants, against FRB/US and GS weights (data in ASSESSMENT.md section 3; scripts `path_fci_gss_ns.py`). Figure 2: event-window scatter/betas for the three variables.
5. **Comparison and application** (1.5 pages). Figure 3: market-weighted index (GSS, NS) vs GS FCI vs FRB/US-weighted MS-style index, levels 1990-2026 (nominal, real, r*-gap 10-year). Figure 4: contributions to the change since 27 Feb and 27 Aug 2026 in funds-rate units, market- vs model-weights (GSS +1.13/+0.73 nominal; FRB/US-weighted +1.18/+0.74; GS FCI +0.45/+0.43 index points; from ASSESSMENT.md, rerun before use).
6. **Caveats and conclusion** (0.5 page): BBB, oil, level-vs-event mapping, transmission vs importance for output.

Code/data to bring: `path_fci_gss_ns.py`, `path_fci_rates_variants.py`, `path_fci_changes.py`, `path_fci_charts.py`, `ms5_level.py`, `ms5_vs_gs.py`, USMPD workbook, `fcig_gs_daily.csv`, FRB/US sensitivities. All of this should be consolidated into one replication script with fixed seeds and a documented data vintage before submission.

## 4. The research idea, stated precisely, and checks needed

**Definition.** Let f be a policy factor (GSS path, scaled so 1 unit = 1 pp on ED4; NS news, 1 unit = 1 pp on the 2-year). Event-window model: x_j = a_j + b_j f + e_j. Weights w = Psi^-1 b / (b' Psi^-1 b), so w'b = 1. Index_t = sum_j w_j (x_jt - mean_j). Interpretation: the policy surprise f whose expected impact on the variables best matches the observed configuration. Higher = tighter.

**Identification assumptions (state them in the note).**
(i) Event-window moves in the three variables are caused by the policy factor plus independent noise (one factor, errors uncorrelated with f in the window). (ii) Responses are stable across regimes and linear; level deviations from a 1990-2026 mean map into policy-equivalent units the same way surprises do. (iii) The policy factor is a clean policy shock (not information effects about the economy). (iv) Level moves due to non-policy shocks (oil, term premium, risk appetite) are read as if policy-driven: this is the definition of a funds-rate equivalent, but it is not a statement about output.

**Checks before writing (priority order).**
1. **Level-vs-event mapping.** Test whether the index built from event-window weights tracks policy at lower frequencies: regress the index (or its monthly change) on SF Fed proxy funds rate and on the expected-policy-rate path (e.g. 1-year-ahead OIS or futures) outside event days. This is the most important check; without it the level index is an assumption.
2. **Weight uncertainty.** Carry the bootstrap bands into the index (bands on the latest reading and on the change since February); report the 10-year weight band (0.35-1.56 GSS) honestly.
3. **Sample/ZLB.** Weights differ in non-ZLB sample (10-year intraday GLS weight 1.1-1.4 vs 0.96); report both, and split pre/post 2008. Note ED4 changed from Eurodollar to SOFR futures in 2022.
4. **BBB sign puzzle.** Test whether spreads fall because of information effects (Jarocinski-Karadi style sign restrictions or the Bauer-Swanson orthogonalised surprises) and whether it vanishes for target surprises or in the ZLB subsample. Either report it as a finding or leave credit out with an explicit limitation.
5. **Units.** Pin down GSS (ED4 pp) vs NS (2-year pp) units and show conversion between them; show the FCI-G conversion algebra including that the funds rate is itself one of FCI-G's seven inputs (so a hike's own contribution is in the yardstick).
6. **Real vs nominal vs r*-gap 10-year.** Weights estimated on nominal surprises; check that the real-yield response to surprises is the same (use TIPS or the 10-year real breakeven from USMPD-compatible data if available) before applying them to real or r*-gap levels. Daily changes are identical across versions; only levels differ.
7. **Factor choice.** GSS path vs NS news vs Bauer-Swanson-orthogonalised vs Bu-Rogers-Wu; show weights are stable (so far shares are 31-40% each).
8. **Yardstick sensitivity for Route 1.** Horizon q4/q8/q12; steady-state vs 2026 baseline (about 13% lower equivalents); VAR vs model-consistent expectations.
9. **Check what is already known.** Read Arnaut-Bauer 2024 in full and the Doh-Choi/Choi et al. papers; confirm that the market-weights comparison with FCI-G/GS weights is not in them.

**Effort.** About 3-4 weeks for a competent economist working part time: 1 week to consolidate code and rerun with intraday/real-yield checks (1, 6), 1 week for weight uncertainty, subsamples, BBB investigation (2-4, 7), 1 week for the FCI-G conversion and figures (Route 1), 1 week writing and review. Add 1-2 weeks if the BBB puzzle or the low-frequency mapping check requires new data.

## 5. Honest assessment

**What is new.** (a) A model-free, high-frequency cross-check of the relative weights in FCI-G and GS, for the three variables that can be identified. (b) A published funds-rate (policy-path) unit version of FCI-G and a transparent conversion. (c) The result that the GS weights and the market-implied shares differ greatly while the indexes still correlate 0.9. (d) The BBB spread finding.

**What is already known or close.** Policy-rate equivalents of conditions: SF Fed proxy funds rate (PCA mapped to pre-2008 funds rate), Beaton-Lalonde-Luu 2009, GS 2015 rule of thumb, Morgan Stanley 2026. High-frequency responses of Treasuries, stocks and the dollar to path/forward-guidance surprises: GSS 2005, Swanson 2021, Rigobon-Sack, Bernanke-Kuttner. Event studies of FCIs on surprises: Arnaut-Bauer 2024 (closest; uses the GS FCI itself on the left-hand side). Weight critiques: Hatzius et al. 2010, Koop-Korobilis 2014, Brave-Butters.

**Who would care.** Fed staff and policy economists who read FCI-G in the context of Caballero-Simsek style "financial conditions targeting" and the current debate about whether markets are tightening for the Fed; sell-side strategists; researchers using FCIs as policy-stance measures.

**Likely objections.** (1) A policy surprise moves markets by a policy-induced mixture, but most level variation in FCIs is not policy-driven; the mapping to levels is an assumption. (2) Transmission to markets is not importance for output: a variable with a large market response to policy may matter little for growth (equity/dollar response shares are not growth weights). (3) Only three variables identified, 253 events, and a 10-year weight with a wide band; two of the five common FCI variables are dropped. (4) Information effects (NS news mixes target and path; correlation 0.98 with GSS path) and ED4 contract change in 2022. (5) The unit (pp on ED4 or the 2-year) is a market rate path, not a funds rate in the model sense. (6) Arnaut-Bauer and Doh-Choi already do much of the idea.

**Weakest part.** The level-vs-event mapping and the identification gap between "policy transmission" and "importance for output". The 10-year weight is also poorly identified. The note cannot say which weights are right, only that model and market weights differ and where.

**Recommendation: write a narrower version.** Do not claim a new FCI or a replacement for FCI-G. Write a 5-6 page note titled around "How much of an FCI is policy? Funds-rate units for FCI-G and market-implied weights", with Route 1 (conversion, a clean and uncontroversial contribution) as the practical result and Route 2 as a model-free robustness check of the weights on equities, the dollar and the 10-year, with BBB and oil explicitly left out. Do not write the broad version (a new market-weighted FCI as headline) unless check 1 (low-frequency mapping) works. Do not write it at all if a read of Arnaut-Bauer and the SF Fed papers shows the weight comparison is already done.

**Single most valuable thing the note could add:** a transparent, reproducible funds-rate-unit translation of FCI-G and the GS FCI, together with evidence that market-implied weights for equities and the dollar agree with FRB/US while the 10-year weight is larger and the GS split (85% on rates and BBB) is far from the market split. This turns "which weights are right" into something measurable.

## 6. Venue, audience, abstract outline

Venue: FEDS Notes (if written by Board staff), FRBSF Economic Letter or Liberty Street Economics style; otherwise an SSRN/NBER-style short working paper or a CEPR VoxEU column version. Audience: monetary policy economists, central bank staff, market strategists.

Abstract outline (about 120 words): (1) Financial conditions indexes such as the Fed's FCI-G and the Goldman Sachs FCI combine financial variables with weights from macro models. (2) We ask how to express them in federal funds rate units. (3) For FCI-G, rescaling by the FRB/US GDP effect of a funds-rate hike gives funds-rate equivalents; we show how the answer depends on the horizon and yardstick. (4) As a model-free check, we estimate how the 10-year yield, equities and the dollar respond to FOMC path surprises and combine them with one-factor weights. (5) Equities and the dollar get weights close to FRB/US; the 10-year weight is larger but imprecise; credit spreads cannot be identified in the event window. (6) The indexes correlate 0.9 in levels with the GS FCI though the weights differ greatly. (7) Caveats: event-window to level mapping; transmission is not importance for output.

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
