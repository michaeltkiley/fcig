# Literature verification (12 Nov 2026)

Sources read directly (ECB, NBER, BIS, FRBSF, Fed, Crossref) [verified] unless tagged. Bib: `new_refs.bib`.

## (1) Bletzinger, Martorana, Mistak: [verified, with a correction]
- **Correction:** the US result is an ECB Economic Bulletin box, Issue 6/2026, "The evolution of financial conditions in the euro area and the United States: a Macro-Finance FCI perspective". It is not a working paper. The page shows no publication date; its last data point is 28 Aug 2026. URL: ecb.europa.eu/press/economic-bulletin/focus/2026/html/ecb.ebbox202606_05~26c3018e11.en.html. A September date is plausible but [not confirmed].
- Method paper: ECB WP No 3193 (Feb 2026), "Looser, tighter, clearer" (euro area; joint VAR and weights estimation; model-implied neutral level).
- Box: the US index is "expressed in units and a scale comparable to those of a policy rate". It is compared with the Goldman Sachs FCI, a weighted-average FCI and FCI-G. It tracks them in stress but "diverges at times owing to the benchmarks' heavier reliance on equity prices". The funds rate has the largest weight, then real rates and the 10-year yield; the CAPE coefficient is negative. "The most pronounced tightening in the sample was the 2022-24 hiking cycle." A Fed tightening shock raises the US FCI; risk assets drive most of the euro area response.
- Bearing on our question: policy shocks move the index through rates and risk assets, and equity-heavy benchmarks diverge from a rate-dominated index.
- Author's claims: policy-rate-comparable units, comparison with GS and FCI-G, equity-driven divergences, 2022-24 strongest tightening: **confirmed**. "Weaker activity signal at elevated equity valuations": **not found** in the box. [Not found] in the WP text either (a grep of CAPE hits only the weights and the euro-area history). The author should give the source or drop it.

## (2) Caballero, Caravello, Simsek, "FCI-star" [verified]
- NBER WP 33952 (2025; doi 10.3386/w33952); CEPR DP 20362; MIT version dated **12 January 2026** (read in full text).
- It defines FCI* as the neutral FCI consistent with output at potential, estimated by a Kalman filter on FCI-G (Ajello et al. 2023). r* absorbs asset-price fluctuations; FCI* does not; r* co-moves with the equity premium and FCI* does not.
- Real-time: the abstract says "FCI gaps provide useful real-time guidance on policy stance". The text: r* "is difficult to estimate in real time"; "In 2022, [gaps] captured the rapid tightening at a time when interest rate gaps still suggested accommodation." The evidence is the 2022 episode and more stable estimates. It does **not** run a vintage-by-vintage real-time evaluation [inference from text searched for "real time", "vintage", "rolling"; I did not read every section].
- Claim attributed: "high bar for neutral financial conditions; our r* adjustment is different": partly confirmed. The "different adjustment" is true (FCI* is a neutral level, not an r* correction). "High bar" is not stated in the abstract or introduction [not found]. The author's own vintage result (0.065 to 0.019) is theirs, not this paper's.

## (3) Lombardi, Manea, Schrimpf [verified]
- "Financial conditions and the macroeconomy: a two-factor view", BIS Working Paper No 1272, 16 June 2025 (JEL C38, E52, G10). URL: bis.org/publ/work1272.pdf.
- A dynamic factor model on a broad set of prices gives a safe-yields factor and a risk factor. Abstract: "relative to the safe interest rates factor, the risk-related factor exhibits stronger predictive power for economic activity" (GDP, investment, inflation). Both are significantly affected by monetary policy; "shocks to the Safe Yields Factor mimic standard monetary policy shocks"; policy transmits through both.
- Bearing: the safe-yield part moves like policy; the risk part carries more of the activity signal.
- Claim (safe yields vs priced risk; risk predicts activity better): **confirmed**.

## (4) Boehm and Kroner [verified, title correction]
- "Monetary Policy without Moving Interest Rates: The Fed Non-Yield Shock", NBER WP 32636 (June 2024; revised Sept 2025); IFDP 1392 (Fed Board). No journal outlet found.
- Standard high-frequency shocks explain most of the yield-curve movement but little of the stock and exchange-rate movement in FOMC windows. A heteroskedasticity-based "non-yield shock", uncorrelated with yields, raises US and foreign stocks, weakens the dollar and raises commodity prices, with global yields unchanged. It works through risk premia.
- Claim (equities and exchange rates move along a dimension orthogonal to yields): **confirmed**. Directly relevant: it says the equity/dollar part of FOMC windows is not captured by the yield-based surprise, which bears on the author's market weights.

## (5) Monetary conditions index literature [verified]
Best two for the invariance/endogeneity problem:
1. **Eika, Ericsson, Nymoen (1996)**, "Hazards in Implementing a Monetary Conditions Index", Oxford Bulletin of Economics and Statistics 58(4): 765-790 (doi 10.1111/j.1468-0084.1996.mp58004009.x); IFDP 568 (doi 10.17016/ifdp.1996.568). The abstract says an MCI assumes an underlying model whose "empirical constancy, cointegration, exogeneity, dynamics" are in question. This is the clearest statement.
2. **Batini and Turnbull (2002)**, "A Dynamic Monetary Conditions Index for the UK", Journal of Policy Modeling 24(3): 257-281 (doi 10.1016/s0161-8938(02)00104-7). I confirmed the citation only; the abstract was not retrieved, so the content is [secondhand] (it is a model-based dynamic MCI).
- Freedman: "The role of monetary conditions and the monetary conditions index in the conduct of policy" (speech), Bank of Canada Review, Autumn 1995, 53-59 [verified]. The 1994 item, "The use of indicators and of the monetary conditions index in Canada" (in Baliño and Cottarelli, eds., *Frameworks for Monetary Stability*, IMF) [secondhand; not confirmed in the IMF volume].
- Mayes and Virén, Bank of Finland DP 17/2001 [verified by listing; not read for invariance]. Use Eika et al. and Batini-Turnbull; others as background only.

## (6) Claim checks
- **Arnaut and Bauer 2024** (FRBSF Economic Letter 2024-07, 4 Mar 2024; "Arnaut-Hull" on EconPapers): FCI-G weights come from FRB/US effects on output growth: **confirmed**. Event study: a surprise tightening produces "significant and persistent tightening in financial conditions"; a 0.1 pp surprise moves the GS FCI about 0.07 on the day: confirmed. Macro news moves conditions through policy expectations: confirmed. Weights compared across shock types: **not found**; the letter does not do this.
- **Ajello et al. 2023** (FEDS Notes, 30 Jun 2023; page updated 30 Oct 2026): seven variables; weights from FRB/US multipliers of permanent changes on four-quarter GDP growth; past changes get declining weights: **confirmed**. It calls the index a "rule-of-thumb approximation" treating changes as exogenous.
- **Hatzius et al. 2010** (NBER WP 16150, July 2010): the index controls for past GDP growth and inflation: **confirmed** (the abstract's wording; "conditional on" is the author's gloss).
- **Aramonte, Rosen, Schindler** (FEDS 2013-39, 30 May 2013; IJCB 13(1): 1-52, 2017): most FCIs predict returns and macro innovations only if the 2008 crisis period is included: **confirmed** (rankings depend on the crisis).

Not checked: full text of Batini-Turnbull, Mayes-Viren.
