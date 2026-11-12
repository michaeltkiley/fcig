# 18_agreement: design and check

Step 18 reads `results/market_weights.csv`, `weights_boot.csv` (first REPS draws), `indexes_*.csv`, `groups_*.csv`, `data/frbus_paths.csv`, `frbus_hike_paths.csv`, `gs_daily.csv`, `usmpd_monetary_events.csv`; it writes `results/18_*.csv` and `scalars_18_agreement.csv`. Run time about 16 s at REPS=500; two runs are byte-identical (md5). Descriptive; no tests, so no multiplicity adjustment. Intervals are 5th-95th percentiles.

Checks [verified]:
- b_4 equals the package's `phi_at(P,4)/G[4]` (assert); b_4'psi = 0.9747 reproduces `spsi_market` in `scalars_weights.csv`.
- The fast numpy policy-news fit reproduces `market_weights.csv` (max difference 9e-16). D_h(psi) = 4e-16 (zero by construction).
- Linearity: persistent response = cumulated temporary responses. Max absolute GDP difference 1e-5 (h=2), 2.5e-4 (h=4), 2.1e-3 (h=8); it grows to 0.02 (15 percent for the dollar) by quarter 32, so the matched-path exercise is limited to h <= 8. Asset paths are priced as GDP(h) = sum_s x_s Tmp(h-s+1), x_s = 0.5^((s-1)/HL), divided by G(h).
- Bridge stage terms sum to `frbus_hp - market` of `indexes_<case>.csv` (max difference 1e-5, the file's rounding).

Conventions and limits [inference]:
- Persistence estimates identify different things: AR(1) half-lives are of LEVELS (monthly, post-1996: 20, 21, 26 quarters; they are near unit roots, intervals wide); the daily equity half-life (14 quarters, interval 0.5 to infinity) is fitted to the CAPE response to NS news at 0-120 trading days with the factor held fixed in the bootstrap; no daily 10-year or dollar data exist in the package, so those two have only the monthly local projection (uninformative: standard errors as large as the responses).
- Window changes of SP500 and DXY (percent) stand in for 100 ln CAPE and the 100 ln real dollar. Monthly D uses the nominal and r* inputs of `cases.inputs`.
- b_h is FRB/US (VAR expectations, zfree) and treated as fixed; intervals therefore understate total uncertainty. The market-weight draws are wide (10-year weight 0.13 to 1.13), which drives most interval width.
- Block bootstrap of months: blocks 12 (monthly changes), 24 (12-month changes, variance shares); runs are broken at block joints.
