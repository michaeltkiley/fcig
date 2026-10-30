# Project memory: financial conditions indexes in funds-rate equivalents (state as of 29 Oct 2026)

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

- **SF Fed Proxy Funds Rate** (weekly; equals the funds rate until Dec 2008 by construction, so compare from 2009, in changes): 52-week changes correlate 0.74-0.78 with our indexes, 13-week 0.44-0.52; its changes are about 1.5x larger (sd 1.58 vs about 1.0-1.1 pp); since 27 Feb 2026 to 9 Oct it is +1.56 pp (ours +0.4 to +0.97), since 27 Aug +0.72 (ours +0.33 to +0.65); proxy minus funds rate now +1.23 pp. It is a third conversion lens (level mapping on pre-2008 relationships) and the natural anchor (`experimental/fci_compare/proxy_compare.py`).
- **FCI-G is a flow measure.** Its level correlates only 0.43 with the macro-model level, but with the macro-model 12-month change it correlates 0.84 (1-year lookback; 0.90 with the real index including house prices; 0.93 from 1998) and with the 24-month change 0.72-0.84 for the 3-year lookback (0.56 at 12 months): the best-matching horizon equals FCI-G's lookback, and FCI-G lags the levels index by about 3 months (`macro12m_vs_fcig.py`, `--1yr`). Most of the FCI-G level disagreement is construction, not weights.

## 3b. 27 Oct 2026: weighting note, second-pass comparison, gap test
- **Weighting note** (`experimental/weighting_note/weighting_note.tex`, not compiled here): one-factor representation; IR (macro-model) weights measure the output equivalent when financial conditions are causal and transmission is complete; market (GLS) weights are BLUE for the policy equivalent and right for output when non-policy movements are noise; the two agree on pure policy moves, the gap is (s - w)'u (non-policy movements only); full equivalence iff g proportional to Sigma^-1 psi; mixed-case projection formula; levels need persistence/common dynamics; FCI-G is the growth-impulse form. `REVIEW_building_blocks.md` reviews the user's uploaded tutorial (consistent; output target only; adds PCA and identification of theta).
- **Second-pass comparison** (`fci_compare/common_unit_v2.py`; METRIC.md deviation log): macro-model index (no oil) replaces MS-FRB (corr 0.96 levels; oil explained 0.90 of the old difference, sd 0.37 pp). Level corr: MACRO/MKT 0.86, MACRO/GS 0.75, MKT/GS 0.86; 12m changes 0.93-0.95. ANFCI/NFCI/OFR FSI correlate weakly with the level indexes (levels 0.15-0.68; 12m 0.43-0.64) and spike in 2008 (ANFCI about +9 pp); ANFCI conversion 0.38 index units per pp (se 0.16), OFR FSI imprecise. FCI-G (1yr) vs 12m change: GS 0.90, MACRO+HP 0.89, MACRO 0.84, MKT 0.81. Proxy funds rate 12m changes from 2009: 0.74-0.79 with MACRO/MKT/GS, about 0.4 with ANFCI/NFCI/OFR. Latest (Oct 2026): MACRO +0.67, MACRO+HP +0.19, MKT -0.71, GS -0.81, ANFCI -0.49, OFR -0.44.
- **Gap test** (`fci_compare/gap_test.py`): event window: common-variable gap does not respond to NS surprises (-0.005, se 0.025; s'psi = 0.995). Monthly h=0: indexes +1.36 each, gap -0.01 (0.12). But at h=6-12 the gap responds (+0.6 to +0.9, se 0.3-0.5): the later financial responses to policy do not keep the impact pattern (common-dynamics assumption fails: equities and dollar). Gap 12m-change variance mostly equities (own share 0.80), dollar 0.35, mortgage spread 0.29; gap level trends with equity valuations (macro gives equities about 0.019 pp per % less weight). Gap correlates with EBP (0.32) and oil (-0.31). Pre-chosen episodes: mean |gap change| 0.46 pp in non-policy episodes vs 0.17 in policy ones (2022 tightening gap 0.33, mostly the mortgage spread; 2022 surprises small because hikes were anticipated).

## 3c. 27 Oct 2026 (later): dynamics and the ECB Macro-Finance FCI (details in `experimental/DYNAMICS_PLAN.md`, Results)
- FRB/US quarterly paths (`ms_fci/frbus_paths.py`): output-side profiles differ by variable (10-year 0.57 -> 0.46 q4 -> q12; BBB 0.13 -> 0.19; mortgage 0.42 -> 0.20); linear (persistent = cumulated temporary).
- Distributed-lag macro index (`ms_fci/macro_model_dl.py`): smoother, lags the static index; "not yet transmitted" peaked 2.8 pp in Sep 2022; growth-impulse form correlates 0.87 / 0.83 with official FCI-G 1yr / 3yr.
- Response profiles (`path_fci/psi_by_horizon.py`): impact readings agree (gap 0.02); delayed gap +0.75 at 12 months, +1.83 at 24 (implied by profiles; equals the gap LP); equities rebound, dollar and 10-year keep rising; proportionality not rejected (low power); robust to GSS, pure-policy events, excluding crises. IP rises after hawkish surprises, so theta from responses is uninformative.
- Approximate US ECB MF-FCI (`fci_compare/mffci_us.py`): about 1.9 index units per 1 pp parallel move (its "policy-rate scale" is not a funds-rate equivalent); reads policy surprises like the market index (gap 0.01); correlations depend on unreported CAPE/dollar weights.

## 3d. 28-29 Oct 2026: index definitions settled by Q&A (`experimental/INDEX_QA.md`, answers 1-45; read this first)
- **Approved specification:** INDEX_QA "Specification for approval", with current pressure restated in demeaned levels.
  - *Output lens* (funds-rate pp; FRB/US old design: VAR expectations, persistent shifts, policy rate direct 0.009 with its small effect emphasized):
    - eventual pressure EP_4 (main), robustness EP_8 and EP_12;
    - current pressure CP_K, a distributed lag on demeaned levels (K = 4 main; 8 and 12 over G(K));
    - growth over the next year (FCI-G form, 1- and 3-year lookbacks);
    - FCI-G / 0.4525, compared in levels and with 12-month changes.
  - *Transmission lens* (pp of the 2-year per NS unit, not rescaled):
    - market index (NS GLS weights, S&P/DXY window moves applied to CAPE and real broad dollar levels; static only);
    - robustness with the Baa yield, full and diagonal covariance;
    - GS x 0.945/0.98;
    - NFCI/ANFCI by weekly NS response; OFR FSI by event-day response (failed: response not different from zero).
  - Cross-lens comparisons are made as is, with units stated.
- **Built:** `ms_fci/macro_model_v3.py`, `fci_compare/transmission_v3.py`, `fci_compare/compare_v3.py` (+ `.log`).
- **FRB/US with model-consistent expectations** (`ms_fci/frbus_mce.py`, converged at 240/300 quarters): weights 2-3x larger. The user chose VAR-expectations weights.
- **ECB-method index on our data** (`fci_compare/mf_var_us*.py`, `VAR_SPEC_RESEARCH.md`):
  - Funds-rate yardsticks fail on 1990-2025: wrong sign, weak NS instruments.
  - The 1973 recursive VAR works, but the index is Baa-spread dominated (a credit-stress index).
  - Decision: text only, for now.
- **LP exploration** (`lp_weights/RESULTS.md`):
  - One-at-a-time LP-IV = inverse-response (market-type) weights.
  - Unemployment falls after hawkish NS surprises in 1994-2025 monthly data.
  - The long-sample recursive LP yardstick: -0.63% output at 12 months (FRB/US -0.45%).

## 3e. 29 Oct 2026: comparison results on the v3 indexes (`fci_compare/metric_v3.py`, `episodes_v3.py`, `nfci_groups.py`; logs alongside)
Units: output lens in funds-rate pp (EP_4, EP_4+HP, CP_4, FCI-G / 0.4525); transmission lens in pp of the 2-year per NS unit (MKT, GS, NFCI, ANFCI). Demeaned 1990-2026.
- **NFCI by group** (Chicago Fed contributions of 105 indicators, `raw/nfci_contributions.xlsx`; they sum to the index within 0.005):
  - Almost entirely spreads (sd 3.6) and "other" (volatility, quantities, leverage, surveys; sd 1.4).
  - Policy/Treasury rates 0.06, equities 0.4, dollar about 0.
  - A different object from the macro, market and GS indexes.
- **Correlations, levels / 12-month changes:**

| Pair | Levels | 12-month changes |
|---|---|---|
| EP_4 / MKT | 0.86 | 0.95 |
| EP_4 / MKT+Baa diag | 0.94 | 0.97 |
| EP_4 / GS | 0.75 | 0.93 |
| MKT / GS | 0.86 | 0.94 |
| EP_4 / CP_4 | 0.84 | 0.37 |
| NFCI or ANFCI with the others | 0.1-0.45 | 0.3-0.6 |

  FCI-G (1-year lookback) against 12-month changes of EP_4, GS, MKT: 0.84-0.90, slopes about 1; against their levels: 0.3-0.6.
- **Latest groups (Oct 2026):**
  - EP_4+HP: rates +0.6, equities -1.4, dollar +1.4 (total +0.2).
  - MKT: +0.5, -2.2, +0.9 (-0.7).
  - GS: +0.1, -2.0, +1.1 (-0.8).
  - NFCI: total -0.9, from narrow spreads.
  - Since Feb 2026: all tighter. EP_4+HP +1.0, MKT +0.65, FCI-G 1yr +1.4 (rates and dollar); GS +0.4; NFCI +0.2.
- **Episodes from 1993** (1990-92 treated as a special case; 6-month non-overlapping windows):
  - *Levels without ANFCI* (EP_4, EP_4+HP, MKT, GS): range mean 1.05, 90th percentile 1.5, latest 1.5.
    - Closest: 2002-2005 (range down to 0.16 in late 2003; all move from tight after the equity bust to neutral through the 2004 tightening) and 2016-2018 (gradual hikes, low volatility; all 0.5-1.9 loose).
    - Widest (group split of highest minus lowest):
      - 1998-2001 equity boom: macro about neutral or tight vs MKT/GS 0.4-1.4 loose; equities 0.7-0.9, plus house prices.
      - 2008-09: GS +3.2 vs macro +1.3; rates incl. BBB 0.7, equities 0.9.
      - 2010-2013: macro 1.0-2.1 loose vs GS near neutral; dollar 0.65-0.87, then rates and equities.
      - Late 2024-early 2025: macro +1.1 vs MKT/GS about -0.35; equities 0.62, dollar 0.64.
    - Theme: outside crises, the macro/market/GS gaps come from equity and dollar weights. In the macro model, rich valuations loosen less and a strong dollar tightens more. Gaps are widest when valuations or the dollar are far from normal.
  - *Levels with ANFCI:* ANFCI is the outlier in every wide window.
    - 1993-95: loose (-4 to -0.6) while the others are tight (narrow spreads, high rates).
    - 1999-2000: tight (+3), spreads widening in the equity boom.
    - 2007-09: +8 to +19.
    - Closest windows add 2005-07, 2014-15 and 2019.
  - *12-month changes with the FCI-G 1yr level:* range mean 0.73, latest 0.48.
    - Close: 2006-07, 2014, 2017-19, mid-2025 (0.2-0.4).
    - Widest:
      - 2008-09: FCI-G +3.6 to +3.8 vs +1.4 to +3.5.
      - 2003-04 and 2021: FCI-G loosens more (-1.9 to -2.6 vs about -1 to -1.4; likely house prices and its lags).
      - Late 2021-early 2022: FCI-G lags the turn (-0.3 vs macro +1.0).
      - 1995 and 1998: about 1 pp apart (the market index reacts most to the 1998 equity and dollar moves).

## 3f. 29 Oct 2026: a second macro lens from the market index (`experimental/market_macro/`)
Motivation (user): the macro-model lens hinges on FRB/US, an idiosyncratic model in academic work; the ECB-method VAR did not give a usable alternative.

**Discarded attempt** (`mkt_output*.py`): the market index split into policy and non-policy parts in a predictive output equation. In levels it does not predict unemployment; in real-10y 12-month flows (1973-2025) it does, and non-policy equity moves matter. The user said this was not what was wanted; kept for the record only.

**Adopted direction: two-variable VAR** (`var2_mkt_u.py`, `var2_mkt_u_long.py`).
- Setup: unemployment gap and the full market index M (2-year pp per NS unit; weights 0.6089 / -0.0512 / 0.0654 applied to monthly 10-year, CAPE, real dollar from 1973). Cholesky with unemployment first (it reacts with a lag).
- *Granger causality, M -> u:*

| Sample | Lags | p |
|---|---|---|
| 1973-2019 | 4 (BIC) | 0.001 |
| 1973-2019 | 12 | <0.001 |
| 1990-2019 | 1 (BIC) | <0.0001 |
| 1973-2025, 2020 dummied | 5 (BIC) | 0.0002 |
| 1973-2025, 2020 dummied | 12 | 0.0002 |
| 1973-2025 with 2020 as is | 2 (BIC) | 0.07 |

  Reverse causality (u -> M) is weaker (p about 0.01-0.03).
- *Unemployment response at 24 months to a 1-unit shock in M* (M stays about 1 unit higher in the long sample):

| Sample | Response (pp) |
|---|---|
| 1973-2019, 4 lags | +0.25 [0.12, 0.37] |
| 1973-2025, 2020 dummied, 5 lags | +0.31 [0.17, 0.45] |
| 1973-2025, 2020 dummied, 12 lags | +0.58 |
| 1990-2019, 1 lag | +0.35 |
| 1973-2025 incl. 2020 | +0.15 |

**Market-index output lens** (`mkt_dynamic.py`; user's spec: 1973-2019, 4 lags; interest-rate (market) units; the market index itself is eventual pressure by analogy).
- Phi(m) = u response (months 0, 3, 6, 12, 18, 24: 0, .13, .21, .25, .25, .25). Holding M at exactly 1 gives nearly the same path. Yardstick Phi(12) = 0.254 u pp per unit (output -0.51%). Effects are realized within about a year, then plateau (unlike FRB/US, where they keep building for years).
- *Current pressure* (1-year lookback) = sum_{m=0..12} [Phi(m) - Phi(m-1)] / Phi(12) * M(t-m) (weights sum to 1, mostly months 1-5).
  - Corr 0.94 with M, 0.85 with FRB/US CP_4.
  - Latest -1.04 vs M -0.74.
- *Two "impetus" concepts, choice open (question 49; user unsure):*
  - Forward impetus (FCI-G's stated definition): sum_{m<12} [Phi(m+12) - Phi(m)] / Phi(12) * dM(t-m). With effects complete within 12 months this is identically EP - CP (corr 1.00). Small (sd 0.51), loads on recent months; corr 0.49 with FCI-G 1yr; latest +0.31.
  - Realized impetus: CP(t) - CP(t-12). Sd 0.91; corr 0.66 with FCI-G 1yr; latest -0.31 (FCI-G -0.34).
  - For reference: M's 12-month change has corr 0.82 with FCI-G; FRB/US growth form 0.89.
  - The two concepts coincide approximately under FRB/US's slow transmission (which is why FCI-G looks like a 12-month change) and separate under the VAR's fast transmission. So FCI-G's large, persistent impulses partly reflect FRB/US lag structure.
- Sample: the VAR is estimated 1973-01..2019-12 (2020 excluded by ending in 2019); its weights are applied to the project MKT 1990-2026; comparisons are over 1991-2026.
- 12-lag check (`mkt_dynamic_lags.py`/`.log`):
  - Unemployment response 0.10 / 0.30 / 0.56 / 0.68 / 0.66 / 0.44 at 3 / 6 / 12 / 18 / 24 / 36 months; yardstick Phi(12) 0.56 (output -1.1%). The effect keeps building to about 18 months.
  - Current pressure is almost unchanged (corr 0.99 with the 4-lag version).
  - Forward impetus now weights older changes more (0.25-1.06): corr with FCI-G 0.74 (4 lags: 0.50); latest +0.48.
  - Realized impetus: corr with FCI-G 0.44 (4 lags: 0.66); latest -0.62.
  - Which impetus resembles FCI-G depends on how long effects keep building.
- **Decision (user, 30 Oct):** keep both the BIC 4-lag and the 12-lag cases.
- **Significance** (`mkt_irf_significance.py`/`.log`): the unemployment response is significant from month 3 to 36 in both cases (bootstrap 95%, 1000 replications, above zero in 34 of 36 months).
  - t about 3-3.5 over 3-24 months with 4 lags; 4-5.5 with 12 lags.
  - Month 1 is insignificant (unemployment ordered first).
  - The 36-month lower bound is near zero (0.017; 0.005).
- **Through data end, excluding 2020** (`mkt_dynamic_full.py`/`.log`; 1973-01..2026-09, 2020 monthly dummies, 2021+ kept; BIC chooses 5 lags):
  - Results are very close to 1973-2019; all significant from month 3 to 36 (bootstrap 95%).

| Lags | Phi(12) (output) | Granger p | Corr with FCI-G: forward / realized impetus |
|---|---|---|---|
| 4 | 0.227 (-0.45%) | 0.002 | 0.56 / 0.64 |
| 5 (BIC) | 0.322 (-0.64%) | 0.0002 | 0.58 / 0.57 |
| 12 | 0.507 (-1.01%) | 0.0001 | 0.73 / 0.44 |

  - Current pressure corr with M 0.90-0.94.
  - Latest: CP -1.06 to -1.16; forward +0.33 to +0.49; realized -0.34 to -0.62.
  - Chart for the 12-lag full-sample version: eventual pressure, current pressure, forward impetus (`mkt_dynamic_full_chart.py`, `mkt_dynamic_full_12lag.png`).
    - Sd 1.46 / 1.53 / 0.76; latest -0.74 / -1.16 / +0.49.
    - Forward impetus peaks in 2008-09 and 2022 (+3).
- **Current vs eventual pressure (30 Oct):**
  - The user questioned the long gaps between current and eventual pressure. Checked: current pressure is a 12-month weighted average of M (weights sum to 1; mean lag 6.5 months with 12 lags, 4.5 with 4).
  - Gaps persist while M trends (1991-93 -0.6, 2009-10 -0.5, 2021-22 +1.0). |gap| > 0.5 in 38% of months, runs up to 12 months.
  - The gap equals the forward impetus (corr 0.99). Not a bug; presentation choice open (question 50).
- **With GS** (`mkt_cp_gs_chart.py`, `mkt_cp_gs.png`): GS tracks eventual pressure (corr 0.85 levels, 0.94 12-month changes), not current pressure (0.66, 0.39). Like the market index, GS is a no-lag levels index.
- **User verdict (30 Oct): "Love the 1973-2026 estimation results."** The 1973-01..2026-09 VAR with 2020 dummied is the preferred basis for the market-index output lens.
- **Working specification for the market output lens:** estimated through data end with 2020 dummied, with the 4-lag (the earlier BIC choice; BIC now 5) and 12-lag cases both kept. The impetus concept (forward vs realized) is still open (question 49).
- Possible checks not yet done: 12 lags was checked (above); or 1973-2025 with 2020 dummied (the impetus weights depend on it); adding inflation (3-variable VAR).

## 3g. 30 Oct 2026: base nominal case CLOSED; real case started
The user closed the base nominal case. Next: the real case, which systematically uses real interest rates for all indexes, in a separate folder `experimental/real_case/` (decisions in `real_case/REAL_QA.md`, one at a time; no consequential choices without the user's guidance).

- Real case progress (30 Oct; REAL_QA R1-R8):
  - expected inflation: Cleveland from 1982, Livingston before, level-adjusted and blended over 1982; matched horizons;
  - long data back to 1973 (level-matched splices);
  - zero = 1973-2026 mean (1990-2026 as a check);
  - house prices as the deviation from a trailing 15-year average.
  - **Possible later change to the nominal case:** detrended house-price ratio (R8).
- Real case progress (30 Oct; REAL_QA R9-R17; all agenda items done):
  - real market index (existing weights on the real 10-year, CAPE, real dollar), real GS (Goldman weights, real rates, real dollar), FCI-G replication from 1973
    (main "all real": rates, stocks, house prices, dollar all real; rates-only real as check; nominal monthly version matches the published FCI-G at corr 0.99),
    NFCI/ANFCI unchanged (shown from 1990 in comparisons; converted 1970s values are huge), conversions unchanged;
  - market output VAR on the real market index: almost identical to nominal (Phi(12) 0.235 at 4 lags, 0.501 at 12). **Revisit later** (user's emphasis): the same VAR
    with the real GS index and the all-real FCI-G;
  - r*: a separate, later set of cases;
  - comparison (`compare_real.py`, 1974-2026 main, 1990-2026 check): real EP_4, EP_4+HP, MKT, GS correlate 0.94-0.99 in levels over 1974-2026 (0.75-0.96 over 1990-2026);
    the 12-month changes correlate 0.94-0.99. Cross-index range over 1990-2026 is smaller with real rates (mean 0.95 against 1.16 nominal). Widest windows: 1977-81 (market and GS
    tighter than FRB/US, mostly equities: low CAPE gets a larger weight in the market index), 2000 and 2024-26 (equities and dollar). ANFCI is the outlier in crises, as in nominal.
- Real case written up (NOTE_PLAN 4f; weighting note paragraph on real rates). **Next: r* cases** (separate folder), Kiley and Laubach-Williams one-sided estimates from the full-sample estimation.

## 4. Literature state (details in NOTE_PLAN.md section 7 and `experimental/path_fci/lit/`)
No source found that converts FCI-G, NFCI and GS to funds-rate equivalents and compares them. Closest: Arnaut-Bauer (FRBSF EL 2024-07), Sack-Swanson (Brookings, Oct 2023; FCI-G vs 2-year yield), Beaton-Lalonde-Luu (2009), Aramonte-Rosen-Schindler (2013), Chicago Fed Letter 498 (Aug 2024). Verified FOMC quotes (62) in `lit/lit_fomc_quotes.md`. Still unread: BKM Handbook text (author covers), NBER WP 34325, FCI-star and multi-asset papers, Goldman 2015 original.

## 5. Where things are
- `experimental/path_fci/`: market-based construction and robustness (ASSESSMENT.md = what was learned; README.md chronology; `path_fci_gss_ns.py`, `path_fci_rates_variants.py`, `path_fci_changes.py`, `path_fci_levelmap.py`); `NOTE_PLAN.md`; `lit/`.
- `experimental/ms_fci/`: FRB/US sensitivities (`frbus_sensitivities.py`, `_ext.py`; run with a Python 3.9 venv, see docstring), `macro_model_levels.py`, MS-style notes (NOTES.md).
- `experimental/fci_compare/`: `METRIC.md` (pre-specified metric and deviation log), `common_unit.py`, `gs_via_ns.py`, `corr_table.py`, `gs_vs_macro_decomp.py`.
- Main repo files used as inputs: `fcig_gs_daily.csv`, `fcig_replication_daily.csv` and `_monthly.csv`, `raw/fed_monthly_*.csv` (official FCI-G, to 2026-08), `history/`.
- USMPD workbook is read from the path set in `experimental/path_fci/path_fci.py` (download from the SF Fed if missing).
- The local-projection work (analysis/) was deleted at the user's request; it exists in git history (commits b36b910..a17ee11) if ever needed.

## 6. Open items / next steps (updated 29 Oct 2026; the full list is in NOTE_PLAN.md 4d)
1. DONE 29 Oct: pre-specified metric, episodes and groups on v3 (`metric_v3.py`, `episodes_v3.py`); see 3e.
2. DONE 29 Oct: NFCI/ANFCI groups from indicator contributions (`nfci_groups.py`).
3. Draft note sections on lenses/units and static/dynamic indexes; ECB method in the text only (may be reconsidered).
4. Corporate yields: Baa robustness done (full and diagonal); intraday corporate data not pursued.
5. FRB/US: VAR-expectations old design is the base (answer 8); model-consistent results kept as an alternative (`ms_fci/frbus_mce.csv`).
6. Market-index output lens (3f): decide the impetus concept (question 49); check lag-profile sensitivity; decide its role in the note (second macro lens beside FRB/US).
7. Replication script and data vintage; raw/ inputs (FRED, OFR, EBP, Shiller CAPE, USMPD, FRB/US package) are not in git.
