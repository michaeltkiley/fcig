# EXPERIMENTAL: funds-rate-equivalent weights from path-surprise responses

Status: exploratory; not used by the daily workflow. Builds on `experimental/ms_fci` (variable definitions, FRB/US weights for comparison).
Script: `path_fci.py` (needs statsmodels, matplotlib, openpyxl; USMPD path is set in the script).  Outputs: `path_fci_betas_*.csv`,
`path_fci_weights_*.csv`, `path_fci_daily_*.csv` (indexes, daily), `path_fci_*.png`, `output_*.txt` (full run logs). `--sample full|nonzlb`.

## Path surprise: what 100 bp means
USMPD holds raw futures surprises. The path surprise here = the part of the ED4 surprise not explained by MP1 (current-meeting funds rate surprise).
ED4 = fourth quarterly Eurodollar future (SOFR future from 2022): the expected 3-month rate for a quarter beginning about 9 months ahead
(roughly 9-12 months ahead). So **+1.00 = +100 bp in the expected short-term rate about a year ahead, with the current funds rate unchanged**.
Slope of ED4 on MP1 is 0.37. Sample sd: path 0.07 pp, target 0.07 pp (270 events 1994-2026, ex Mar-Apr 2020; 201 outside the ZLB eras).
The surprise dashboard repo has no path factor of its own (it uses a first PC of ED1/UST2Y/UST5Y/UST30Y as an instrument and the raw 2-year); this definition is from the earlier LP work.

## Method
1. For each variable (the daily levels of the GS / MS-style indexes): `dx = a + b*path + c*target + u` on event days (close-to-close; the Fed's broad dollar is a noon index, so the dollar
   uses t-1 to t+1). HC1 errors. Intraday USMPD responses (10-year, S&P, DXY) are printed as a check and agree.
2. Each variable alone gives an equivalent `1/b` (pp of path rate per unit of x); summing those would count one surprise several times. The weights are
   one-factor (Bartlett / GLS) weights `w_j = (b_j/s_j^2) / sum_k(b_k^2/s_k^2)`, so `sum_j w_j b_j = 1`: a 1 pp path surprise moves the index 1 pp.
   Noisy variables get small weights. This is my reading of the request (forward regressions, coefficients as the basis for weights); reverse regression of the surprise on the changes would be biased toward zero by non-FOMC news in daily changes.
3. Index = `sum_j w_j (x_j - mean_j)`, same daily levels as ms_fci / GS, mean over 1990-2026; higher = tighter. Sets: GS (fed funds, 10-year, BBB, CAPE, dollar), MS (10-year, BBB, CAPE, real dollar, real oil), Core (10-year, CAPE, dollar only).

## Results (full sample; non-ZLB in brackets)
Response to +1 pp path (event day): 10-year +0.47 pp (+0.43), BBB spread -0.20 pp (-0.15), S&P/ln CAPE -5.2% (-5.2), dollar +3.5% (+3.2), oil -2.0% (-2.9, insignificant), fed funds +0.05 (target controlled).
Weights (pp of funds-rate per unit) MS set: 10-year 0.82 (0.98); BBB -0.73 (-0.57); CAPE -0.027 per 1% (-0.026); dollar 0.091 per 1% (0.109); oil -0.003. FRB/US: 0.57, +0.13, -0.032, 0.10, +0.008.
- Equities and dollar weights match FRB/US closely; the 10-year weight is 1.4-1.7x higher.
- BBB spread has the wrong sign (spreads narrow when path surprises are hawkish; the same in the pre-1997 Baa series and the ICE OAS era, and the 10-year/BBB responses are strongly collinear), so the GLS weights net BBB against the 10-year (0.82 vs -0.73), i.e. mostly weight a corporate yield rather than a spread. Treat with caution: wider spreads read as looser. Oil is not identified (t of -1).
- Correlation with the GS FCI: levels 0.45 (MS set), 0.65 (Core), vs 0.80 for the FRB/US-weighted MS index; daily changes 0.63 / 0.77 vs 0.81. Today (20 Oct 2026): GS set +1.6 pp, MS set +1.5, Core +1.0, FRB/US-weighted MS +0.8 (full sample; non-ZLB betas give higher readings).
- Path-weighted indexes are much more extreme in 2009-2015 (to -3.5 pp), because the large 10-year and BBB weights offset only partly.

## Caveats and follow-ups
Few events (270) and daily event-day changes contain other news; oil and fed funds responses are noise. Path surprise in the ZLB era is partly QE/forward guidance, and ED4 switched from Eurodollar to SOFR futures in 2022.
Equal-weight or constrained alternatives (e.g. fix BBB at FRB/US weight, or use BBB yield instead of the spread), intraday-only weights for 10-year/equities/dollar, and the target surprise as a second set of weights are natural next steps.

## Without the BBB spread (`path_fci_nobbb.py`)
BBB dropped after the IV check (`path_fci_iv_bbb.py`: spread falls ~0.4-0.5 pp per 1 pp path-driven 10-year rise, first-stage F > 50, same in Baa and ICE data).
Weights re-estimated (full sample): 10-year 0.96, dollar 0.107 per 1%, CAPE -0.031 per 1%, fed funds 0.01, oil -0.003 (FRB/US q4: 0.57, 0.10, -0.032, 0, +0.008).
Correlation with the GS FCI, 1990-2026: levels 0.63-0.64 (FRB/US-weighted 0.76), daily changes 0.77 (0.80). Today: GS-style +1.05 pp, MS-style +0.90 (FRB/US weights +0.91); non-ZLB betas +1.45 / +1.27.
Path-weighted indexes still run well below FRB/US-weighted ones in 2009-2021 (about -3 pp vs -1.6) because the 10-year weight is 1.7x higher.
