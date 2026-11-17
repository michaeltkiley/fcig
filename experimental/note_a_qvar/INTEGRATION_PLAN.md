# Note A integration plan: new results and a new framing (draft, 17 Nov 2026)

Read with `FRAMING_SKETCH.md` (this folder). Decisions are recorded as N-A entries in `../../fci_paper/FP_QA.md` once taken. Nothing in `fci_paper/paper/` has been changed. Three parts: what we found (Part 1), the decisions the author takes one at a time (Part 2), and the steps once they are taken (Part 3).

**Guiding idea (author, 16 Nov 2026).** The near-identity of an index built only from announcement-window co-movement with indexes built from spending effects (FRB/US) and calibrated to GDP growth (GS) is the finding, not an artifact. It holds because policy moves equity prices strongly in the windows and in FRB/US, and equity prices are the largest single channel through which policy reaches financial conditions. Many macro models have no equity channel.

## Part 1. What we found (16-17 Nov 2026)

1. **The current activity test is ambiguous.** Section 6 of the paper (composition test by local projection) rejects neither restriction for GDP; for unemployment the verdict changes with the sample. The author judges that Note A "is not working" with this as its activity evidence.
2. **Quarterly VAR** (CBO output gap, one index; 4 lags; 1973Q1-2026Q3; shock = one point on the index; r* step; 90 percent block-bootstrap percentile intervals) [verified, `results/irf_full_indexes.csv`]:
   - GDP lagged (gap ordered first), 4/8/12 quarters: market -0.75/-0.43/-0.19, GS -0.86/-0.50/-0.24, FRB/US -0.77/-0.39/-0.11, FCI-G 1-year -1.27/-0.86/-0.28. All exclude zero at 4 quarters.
   - Generalized response (identical to the index ordered first): -1.04, -1.17, -1.10, -1.54 at 4 quarters.
   - 2020 dummies change 4-quarter responses by 0.1 or less. Nominal and real steps similar. The VAR does not separate the weightings.
3. **FRB/US benchmark** [verified, `results/frbus_match.csv`]: the funds-rate path that moves the FRB/US index along its VAR path gives FRB/US GDP -1.00/-1.41/-1.50 (lagged ordering; VAR -0.77/-0.39/-0.11). One year out the VAR and the model agree; after that the VAR effect fades and the model's builds. A persistent 1 pp hike reads as 0.74 point on impact and 0.80 at 4 quarters of the FRB/US index.
4. **Equity channel** [verified]: in FRB/US a persistent hike works almost entirely through asset prices (funds-rate own weight 0.009); equities are 60/53/55 percent of the index reading at quarters 1/4/8. In the windows, equities supply 0.40 of a one-point market reading (10-year 0.33, dollar 0.28).
5. **Co-movement** [verified]: level correlations 1973-2026, r* step: market-GS 0.994, market-FRB/US 0.942, GS-FRB/US 0.936; 12-month changes 0.96-0.98. Equity valuation is about three-quarters of the level variance of the market and GS indexes and half of FRB/US.
6. **Housekeeping** [verified]: the Note B integration plan does not touch Note A. NFCI/ANFCI switched to monthly means in `03_indexes.py` (17 Nov); package rerun in progress; changes to be recorded in FP-A62.

## Part 2. Decisions for the author (one at a time; recommendation first)

| # | Decision | Options | Recommendation |
|---|---|---|---|
| N1 | Headline claim | (a) "Policy reaches financial conditions mainly through equity valuations and long rates; markets and the macro model agree on this"; (b) "Market, model and GDP-calibrated indexes agree", with equities as the reason; (c) keep the current two-choices framing | (a): it is the economic finding; (b) follows from it |
| N2 | Title | e.g. "Monetary Policy, Equity Prices and Financial Conditions"; "What Moves When Policy Moves: Financial Conditions in Units of Policy"; keep current | decide after N1 |
| N3 | The four-calibration comparison | (a) keep as the body; (b) shrink to one section on where the indexes part (the dollar; January 1998, 1998-2001, 2022-24); (c) appendix | (b) |
| N4 | Activity evidence | (a) the VAR replaces the composition test; (b) both; (c) composition test only | (a), composition test (and its net-export result) to the appendix |
| N5 | VAR specification for the main exhibit | ordering (GDP lagged main, generalized as the other bound); 2020 dummies (main) vs none (robustness); step (r* main; nominal, real in the appendix); quarterly averages | as listed; author confirms |
| N6 | Indexes in the VAR exhibit | market, GS, FRB/US, FCI-G (1-year); FCI-G at the nominal step (closest to the published series) or r*; add NFCI/ANFCI? | the four; FCI-G nominal in the main table, r* in the appendix; NFCI/ANFCI appendix only |
| N7 | Benchmark for "one point of policy" | FRB/US matched funds-rate path for (a) the FRB/US index only; (b) all three policy-unit indexes (their FRB/US readings of a hike can be computed from the model's asset responses) | (b) |
| N8 | Equity-channel exhibit | one table or figure: share of a policy move's reading carried by each asset, (i) in the windows, with announcement-bootstrap intervals, (ii) in FRB/US at 1, 4 and 8 quarters | yes; compute the FRB/US side at the r* step (now read off nominal model changes) |
| N9 | Neutral level (r*) section | keep; shrink to the 2008-09 example and FCI*; appendix | shrink |
| N10 | Literature to verify before writing | equity responses to policy news (Bernanke-Kuttner 2005; Gurkaynak-Sack-Swanson; Bauer-Swanson); equity and wealth channels in FRB/US (Brayton et al.); models with and without an equity channel | verify all before citing (CLAUDE.md) |
| N11 | Text execution | (a) a full new copy of the paper for the author to merge by diff (as Note B); (b) edit `fci_paper.tex` directly | (a): the reframing is large |
| N12 | Long-run divergence (VAR fades, FRB/US builds) | report as a finding; robustness only | report it in one paragraph |

## Part 3. Steps once N1-N12 are taken

**Phase 0. Housekeeping.** Finish the NFCI/ANFCI rerun; record FP-A62 with the files and macros that changed; run `10_check_sync.py`; rerun the NFCI/ANFCI rows of the VAR.

**Phase 1. Package** (`fci_paper/replication/`, new self-contained steps; this folder stays the exploration record):
1. `32_qvar.py`: the VAR (N5, N6); CBO gap data (GDPC1, GDPPOT) into `data/` with `SOURCES.md` entries; results `32_*.csv`, `scalars_32_qvar.csv`.
2. `33_frbus_match.py`: matched funds-rate paths and FRB/US GDP for the indexes chosen in N7.
3. `34_equity_channel.py`: the decomposition of N8, with intervals.
4. `07_report.py`: tables, figure (paths of the VAR responses beside the FRB/US benchmark), macros, claim checks (`chk`).
5. `run_all.py` and `10_check_sync.py` gain the new steps.

**Phase 2. Text** (per N11): abstract, introduction (question, result, approach as First/Second/Finally; literature after), new sections in the order of `FRAMING_SKETCH.md`; four-calibration and neutral-level material per N3 and N9; follow `experimental/WRITING_GUIDE.md` and its checklist.

**Phase 3. Checks.** Sync check passes; every macro resolves; claim checks hold; PDF builds.

**Phase 4. Close.** FP_QA entries; `PROJECT_MEMORY.md` section 9; README; merge to `main` with the author's approval.
