# Project memory: financial conditions indexes in funds-rate equivalents (state as of 22 Oct 2026)

Purpose of this file: a compact record of what was decided, built and found, so the work can be picked up later. Detail lives in the files named below. Branch history: `ccr-3a1fbe39-so6omu`.

## 1. The project
A short note (plan: `experimental/path_fci/NOTE_PLAN.md`) that expresses widely used financial conditions indexes (FCI-G, GS replication, NFCI/ANFCI, others) in **federal funds rate equivalents**, compares them (levels as base, 12-month changes as check; by group: rates incl. policy rate and corporate rates, equities, dollar, other; by episode chosen with a pre-specified metric), and adds simple alternatives. Aim: understanding how indexes relate (no ground truth; not a ranking). Source-agnostic unit ("tightening equivalent"); zero = 1990-2026 average; parallel 1 pp funds-rate move as the unit.

## 2. Decisions (from the conceptual walk-through; full list in NOTE_PLAN.md section 2)
- Two lenses, both in funds-rate units: output-equivalent (FCI-G / FRB/US yardstick: a 1 pp full-transmission hike lowers GDP 0.45% at q4, 0.95% q8, 1.43% q12) and transmission-equivalent (response to a policy surprise).
- Market-based lens uses raw surprises from USMPD (information effects acknowledged in one paragraph, set aside); **NS policy news is the base** (not orthogonalized to MP1; a tilted level shock), GSS path is robustness; weights from one-factor model with full error covariance (diagonal as sensitivity).
- A priori transmission variables (Boivin-Kiley-Mishkin; the user wrote that chapter): rates broadly (incl. corporate), equities, exchange rate. Event-window data cover 10-year, S&P 500, dollar only; BBB/oil/house prices are outside it (state openly).
- MS-style index renamed **macro-model levels index** (FRB/US-weighted; our own construction, no direct source for the MS index); oil dropped; two versions, without and with house prices (as price-to-rent ratio); real versions use real policy rate and real 10-year (mortgage and BBB enter as spreads over the 10-year).
- GS is a **replication** (published weights 4.4/45.1/39.6/4.9/6.0), not the proprietary series: label as such.

## 3. Key results
- Market-based weights (event window, 253 events, units per pp of factor): GSS path: 10-year 0.97, equities -0.059 per 1%, dollar 0.098 per 1%; NS: 0.61, -0.051, 0.065. Shares of the unit response about a third each. Real/nominal/r*-gap versions apply the same weights.
- BBB spread narrows after hawkish path surprises (IV on the 10-year, -0.4 to -0.5 per 1 pp; not a Moody's timing artifact) so it is dropped from the market lens; grouping corporate yields with rates removes the presentational puzzle.
- FRB/US additional partials (q4, funds-rate pp per unit): short end **direct** 0.009 per pp (0.24 if the funds rate's role in the VAR expectations is allowed: the effect is almost entirely the expectations channel), mortgage spread 0.416 per pp, house prices -0.029 per 1% (house prices do not respond to policy in FRB/US). Sum of partials -0.36 vs full hike -0.45 at q4 with the direct short end (gap = expectations channel).
- GS in funds-rate units: 0.95 pp per index point via NS shock (two-day window, average of MP1 and ED4 as the funds-rate content of an NS unit; range 0.69-1.20), 1.27 via monthly parallel-surprise LP, Goldman's secondhand rule 0.69. FCI-G: 2.2 pp per unit by the yardstick (3.3 by monthly surprise response at h=0, se large).
- Comparison (monthly, funds-rate pp): GS, market-based and macro-model indexes co-move (12-month-change correlations 0.85-0.96; level correlations 0.44-0.97); FCI-G the outlier in levels (it is built from past changes). Real versions raise agreement between GS and market-based (0.97 level corr). Latest (20 Oct 2026): FCI-G -0.8, GS -1.1 (nominal; -1.3 real), market-based -0.7 (-0.9 real), macro-model +0.67 (+0.49 real) without house prices, +0.19 (+0.01) with.
- GS minus macro-model difference: mostly weights (dollar and equities weight gaps matter most because those variables swing widely), data (nominal vs real) in the early 1990s, coverage (mortgage spread, house prices) 8-18% (`experimental/fci_compare/gs_vs_macro_decomp.py`).
- Changes since 27 Feb / 27 Aug 2026 (funds-rate pp): GSS nominal +1.13/+0.73; NS +0.65/+0.47; macro-model +0.92/+0.66 (without HP); all tighter, mostly 10-year and dollar, equities offset since Feb.

## 4. Literature state (details in NOTE_PLAN.md section 7 and `experimental/path_fci/lit/`)
No source found that converts FCI-G, NFCI and GS to funds-rate equivalents and compares them. Closest: Arnaut-Bauer (FRBSF EL 2024-07), Sack-Swanson (Brookings, Oct 2023; FCI-G vs 2-year yield), Beaton-Lalonde-Luu (2009), Aramonte-Rosen-Schindler (2013), Chicago Fed Letter 498 (Aug 2024). Verified FOMC quotes (62) in `lit/lit_fomc_quotes.md`. Still unread: BKM Handbook text (author covers), NBER WP 34325, FCI-star and multi-asset papers, Goldman 2015 original.

## 5. Where things are
- `experimental/path_fci/`: market-based construction and robustness (ASSESSMENT.md = what was learned; README.md chronology; `path_fci_gss_ns.py`, `path_fci_rates_variants.py`, `path_fci_changes.py`, `path_fci_levelmap.py`); `NOTE_PLAN.md`; `lit/`.
- `experimental/ms_fci/`: FRB/US sensitivities (`frbus_sensitivities.py`, `_ext.py`; run with a Python 3.9 venv, see docstring), `macro_model_levels.py`, MS-style notes (NOTES.md).
- `experimental/fci_compare/`: `METRIC.md` (pre-specified metric and deviation log), `common_unit.py`, `gs_via_ns.py`, `corr_table.py`, `gs_vs_macro_decomp.py`.
- Main repo files used as inputs: `fcig_gs_daily.csv`, `fcig_replication_daily.csv` and `_monthly.csv`, `raw/fed_monthly_*.csv` (official FCI-G, to 2026-08), `history/`.
- USMPD workbook is read from the path set in `experimental/path_fci/path_fci.py` (download from the SF Fed if missing).
- The local-projection work (analysis/) was deleted at the user's request; it exists in git history (commits b36b910..a17ee11) if ever needed.

## 6. Open items / next steps
1. NFCI feasibility: download the Chicago Fed weekly contributions and indicator weights; group mapping; weekly-window conversion; vintages (ALFRED).
2. Swap the macro-model levels index into `common_unit.py` (replacing the MS-style series) and re-run the metrics, episodes and group table; add ANFCI, SF Fed proxy funds rate, OFR FSI.
3. Decide treatment of corporate yields in the market-based lens (intraday data search) and of the pre-specified episode metric.
4. Consistency of the FRB/US partials (VAR expectations free in some experiments, fixed in the short-rate one): rerun all with one definition.
5. Real/r*-gap versions and GSS/NS/diagonal sensitivities in a box; weight bands carried into readings.
6. Replication script with fixed seeds and a documented data vintage before any submission.
