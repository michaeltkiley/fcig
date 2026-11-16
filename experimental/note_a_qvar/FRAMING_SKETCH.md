# Note A reframed: equity prices at the center of policy transmission (scratch sketch, 16 Nov 2026)

Status: a sketch for the author to return to. Not paper text; nothing in `fci_paper/` or `fci_note/` changed. Tags: [verified] = computed or read in this repo in the 16 Nov session; [secondhand] = from memory or a cited source not re-read; [inference] = interpretation.

## Why reframe

The author (16 Nov 2026): Note A "is not working"; the local projections used to assess the weights give ambiguous results. A quarterly VAR (this folder) does not separate the weightings either. What does stand out, and what the author judged "super interesting": an index built only from co-movement in 30-minute FOMC windows is nearly identical to the index built from FRB/US spending effects and to the GDP-calibrated GS index. The reason is substantive: in both the windows and FRB/US, monetary policy moves equity prices a lot, and equity prices are the largest single channel by which policy reaches financial conditions. Many macro models have no equity channel.

## The story in five steps (proposed)

1. **Question.** How does monetary policy reach spending through financial markets, and which asset prices carry it?
2. **Two independent answers on the same scale.**
   - Markets: in FOMC windows, one point of policy news (+1 pp on the 2-year yield) moves the 10-year yield +0.53 pp, equities -7.8 percent, the real dollar +4.2 percent [verified, `fci_paper/replication/results/market_weights.csv`]. Weighted by the market index, equities supply 0.40 of the one-point reading, the 10-year yield 0.33, the dollar 0.28 [verified, arithmetic on those weights and responses].
   - FRB/US: a persistent +1 pp funds-rate hike moves the FRB/US index 0.74 on impact and 0.80 at four quarters; equities supply 60 and 53 percent of it (0.44 and 0.42), the 10-year yield 0.19-0.21, the dollar 0.11-0.15, the funds rate itself 0.01 (weight 0.009 with asset prices held fixed). Stocks fall about 14 percent on impact [verified, `data/frbus_hike_paths.csv` with `lib.indexes` weights].
   - So policy works in the model almost entirely through asset prices, and equities carry more than half; the market windows say the same, with a somewhat larger dollar share.
3. **The weights agree.** Market vs FRB/US weights: 10-year 0.61 vs 0.56; equities -0.051 vs -0.031; dollar 0.065 vs 0.098 [verified, `frbus_weights.csv`]. Published GS weights (calibrated to GDP growth; Caballero-Simsek 2026, Table 1) give a dollar-to-equity trade-off of 0.96 against 1.00 for the market index and 2.51 for FRB/US [verified in the package, FP-A44/FP_QA]. Level correlations 1973-2026, r* step: market-GS 0.994, market-FRB/US 0.942, GS-FRB/US 0.936; real step 0.994/0.950/0.944; 12-month changes 0.96-0.98 [verified]. Equity valuation is 77-79 percent of the level variance of the market and GS indexes and 49 percent of FRB/US (house-price version) [verified, `groups_rstar.csv`].
4. **The indexes matter for activity in units of policy.** Quarterly VAR, CBO output gap and each index, 4 lags, 1973Q1-2026Q3, shock = 1 point on the index (r* step):
   - GDP lagged (gap ordered first): market / GS / FRB/US -0.75 / -0.86 / -0.77 at 4 quarters; about -0.4 to -0.5 at 8; -0.1 to -0.24 at 12 [verified, `results/irf_full_indexes.csv`].
   - Generalized (= index ordered first): -1.04 / -1.17 / -1.10 at 4 quarters [verified].
   - FRB/US benchmark: the funds-rate path that moves the FRB/US index along its VAR path gives GDP -1.00 at 4 quarters (lagged ordering; -0.96 generalized) [verified, `results/frbus_match.csv`]. One year out the VAR and FRB/US agree; after that the VAR effect fades while FRB/US keeps building (-1.4 to -1.5 at 12 quarters).
   - FCI-G (1-year, GDP-growth units): -1.27 (lagged) and -1.54 (generalized) at 4 quarters, r* step; -1.17 / -1.26 nominal (closest to the published series); 90 percent intervals include -1 [verified].
5. **Where the indexes part: the dollar.** The calibrations differ mainly in the weight on the dollar relative to equities; that matters in dollar-driven episodes (January 1998: three calibrations ease 0.41-0.49, FRB/US tightens 0.28; 1998-2001; 2022-24) [verified in the paper's step 26 results, as reported in FP_QA FP-A60]. The paper's existing results (highest vs lowest differ by at least a quarter point in about seven-tenths of months) become the secondary finding, not the headline.

## What it would take (not done)

- Literature to verify before writing: equity response to policy surprises (Bernanke-Kuttner 2005; Gurkaynak-Sack-Swanson; Bauer-Swanson) [secondhand]; equity and wealth channels in FRB/US documentation (Brayton-Laubach-Reifschneider) [secondhand]; which DSGE models lack an equity channel and which have one (Smets-Wouters via Tobin's q) [secondhand]; Caballero-Simsek on the equity channel [verified p. 6 in an earlier session].
- An equity-share decomposition for the market and GS index readings of the window shock, with intervals (announcement bootstrap), alongside FRB/US over horizons.
- Decide the role of the VAR in this folder: a supporting exhibit (activity in units of policy at one year), with the lagged ordering as the main case.
- Check the FRB/US decomposition for the r* step (here read off nominal model changes; expected inflation and r* held as in the model) [inference].
- Decide whether the local-projection weight tests stay (appendix) or go.

## Open questions for the author

1. Is the headline "equities carry most of the policy signal in both markets and the model", or "market and model indexes agree", with equities as the reason?
2. Keep the four-calibration comparison as the body, or shrink it to the dollar section?
3. Main ordering for the VAR exhibit: lagged GDP (author's stated preference, 16 Nov) with the generalized response as a bound?
