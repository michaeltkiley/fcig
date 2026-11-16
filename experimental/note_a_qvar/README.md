# Quarterly VAR: output gap and each FCI (experiment, 16 Nov 2026)

Not part of the paper. `fci_paper/` and `fci_note/` are read, not changed.

**Question (user, 16 Nov 2026).** The local projections that test the weights give ambiguous answers. Try a two-variable VAR instead: the CBO output gap and one FCI, quarterly (quarterly average, or end of quarter), 4 lags, Cholesky in both orderings. Report the gap response at 4, 8 and 12 quarters to a one-point FCI shock. Which are close to 1, which far?

**Run.** `python3 qvar.py` (about 1 minute; needs `fci_paper/replication/requirements.txt`). FRED files (GDPC1, GDPPOT, GS2, FEDFUNDS, downloaded 16 Nov 2026) are in `data/`.

**Specification.** Output gap = 100 (GDPC1/GDPPOT - 1). 1973Q1-2026Q3, constant, dummies 2020Q1-2021Q1 (the paper's 2020-01..2021-03 convention). FCI shock scaled to raise the FCI 1 point on impact. "Gap first": no same-quarter effect of the FCI shock on the gap; "FCI first": allowed. Bands: moving-block bootstrap of residual pairs (4-quarter blocks), 1,000 draws, 90 percent.
FCIs: the paper's four calibrations F (futures factor), Y (two-year yield), B (FRB/US), G (published GS weights) on the three common assets, common scale w'psi_F = 1 (as `26_four_way.py`), at each step (nominal, real, r*). Benchmarks: the 2-year yield and the funds rate in the same VAR. Others (different units): FCI-G 1-year (GDP growth points), NFCI, ANFCI (standard deviations).

## Results (quarterly average; [verified] = printed by `qvar.py`)

Output-gap response (percent of potential) to a 1-point FCI shock, r*-step indexes:

| FCI | gap first h4 / h8 / h12 | FCI first h4 / h8 / h12 |
|---|---|---|
| F | -0.75 / -0.43 / -0.19 | -1.04 / -0.53 / -0.20 |
| Y | -0.62 / -0.33 / -0.06 | -0.92 / -0.45 / -0.10 |
| B | -0.70 / -0.36 / -0.08 | -1.04 / -0.50 / -0.12 |
| G | -0.75 / -0.43 / -0.20 | -1.03 / -0.52 / -0.20 |
| 2-year yield | -0.25 / -0.34 / -0.26 | +0.15 / -0.12 / -0.17 |
| Funds rate | -0.14 / -0.23 / -0.22 | +0.10 / -0.13 / -0.21 |
| FCI-G 1-yr (GDP-growth units) | -1.27 / -0.86 / -0.28 | -1.54 / -0.98 / -0.34 |
| NFCI (1 s.d.) | -0.10 / -0.09 / -0.05 | -0.10 / -0.09 / -0.05 |
| ANFCI (1 s.d.) | -0.18 / -0.15 / -0.08 | -0.19 / -0.15 / -0.08 |

Full table with bands, nominal and real steps, own FCI paths: `results/summary.md`; all numbers `results/irf.csv` (also end-of-quarter), checks `results/irf_checks.csv`, FRB/US benchmark `results/frbus_implied.csv`.

1. **The four calibrations are hard to tell apart.** At 4 quarters the r*-step responses span -0.62 to -0.75 (gap first) and -0.92 to -1.04 (FCI first); the 90 percent bands overlap almost entirely. Y is a little weaker throughout. The ordering moves the 4-quarter number by about 0.3, more than the choice of weights does. Same pattern at the nominal and real steps and from 1976Q3 or to 2019Q4 [verified].
2. **Against "1": about 1 at 4 quarters, well under 1 at 8 and 12.** Benchmark: treat the index's own VAR path (which stays near 1-1.3 points for two years) as a funds-rate path and read FRB/US GDP off it. Ratio VAR / FRB/US, r* step: 0.8-1.4 at 4 quarters, 0.25-0.41 at 8, 0.04-0.12 at 12. Nominal and real steps: 0.6-1.3, 0.3-0.5, 0.1. The VAR effect peaks early and fades; FRB/US builds over three years [verified; the shape difference is the finding, the levels depend on the benchmark].
3. **Against the 2-year yield in the same VAR: FCIs hit 2.5-3.5 times harder at 4 quarters**, 1.0-1.8 times at 8, 0.2-1.0 at 12 (gap first). The policy-rate VARs themselves are weak (FCI-first: wrong sign at 4 quarters; 0.2-0.4 of FRB/US), so the 2-year yield is not a clean "one point of policy" here [verified].
4. **FCI-G is the one index with a built-in target** (1 point = 1 pp of GDP growth over the year, so about -1 on the gap at 4 quarters): -1.27 to -1.54, close to 1 and somewhat larger [verified].
5. NFCI and ANFCI: a 1 s.d. shock moves the gap by -0.10 and -0.18 at 4 quarters (no policy-unit target).

**Reading [inference].** A two-variable Cholesky VAR does not identify a financial shock: FCI-first attributes all common news (about growth, from equities) to the FCI, and gap-first attributes none. Both orderings give 4-quarter effects of the right order of magnitude (about one point of policy), but the VAR, like the local projections, does not separate the weightings: the four indexes share most of their variation and differ in the months where they differ, which a 50-year VAR barely weighs. A sharper test would need a sample or shock where the calibrations disagree (e.g. dollar-driven episodes: 1998-2001, 2022-24), or a VAR with the three assets separately and the weights imposed vs free.

## Second run: Note A's four full indexes (16 Nov 2026; `qvar_full.py`)

User: use the four indexes as published by the package (`fci_paper/replication/results/indexes_<step>.csv`): market, GS replication (all five GS variables), FRB/US (headline, no house prices), FCI-G 1-year. Shock = 1 point on the FCI on impact; with and without 2020Q1-2021Q1 dummies; from 1973Q1 (FCI-G from 1974Q1, its first quarter). Table with 90 percent bands for all three steps: `results/summary_full_indexes.md`; numbers `results/irf_full_indexes.csv`. Check: the market index at the r* step reproduces F of the first run (same series) [verified].

## Third run: FRB/US funds-rate path matched to the VAR path of the FRB/US index (16 Nov 2026; `frbus_match.py`)

User: scale the FRB/US funds-rate shock so that the FRB/US index follows its VAR path (FCI first, r* step) at each horizon, and read GDP off FRB/US. Superposition of the persistent 1 pp hike (VAR expectations, full transmission). Result (with dummies; without is within 0.1): matched funds rate +1.36 pp on impact, +2.05 next quarter, +1.29 at 4 quarters, +0.43 at 8, +0.13 at 12. FRB/US GDP -0.96 / -1.32 / -1.40 at 4 / 8 / 12 quarters; VAR gap -1.10 / -0.54 / -0.15 [verified]. The index reads a persistent hike as 0.74 point on impact and 0.80 at 4 quarters (not 1: the variable-by-variable weights do not add up exactly to the full hike) [verified]. Approximations: r*-step index read off nominal model changes; stocks % for CAPE [inference]. `results/frbus_match.csv`.
