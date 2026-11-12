# Check of step 22 (FRB/US expenditure channels of the equity and dollar experiments)

Run: `<venv>/bin/python 22_channels.py` (Python 3.11 venv under the scratchpad: pandas<3, sympy==1.3, symengine, scipy, networkx, multiprocess, lxml, typing_extensions; pyfrbus and LONGBASE downloaded from federalreserve.gov to `raw/frbus/`, gitignored). Runtime 8 s [verified]. Deterministic (no random draws).

Verification [verified]:
- GDP object: `xgdp` (real GDP, chain-weighted 2012 dollars), 100 x log(shocked/baseline); quarter 1 = quarter of impact; "four-quarter" = quarter 4.
- Component accounting: FRB/US approximates xgdp by dlog xgdp = y1 dlog xfs + y2 dlog ki + y3 dlog ki(-1) and dlog xfs = sum w_i dlog e_i (coefficients read from model.xml; ecnia .6849, eh .0386, ebfi .1324, egfe .0429, egfl .0223, egse .0395, egsl .0691, ex .1203, emo -.1399, emp -.0101). Contributions telescope into log-level differences. Components sum to GDP with residual <= 1.3e-8 percentage points over quarters 1-16, all experiments and paths (`22_paths.csv`, column Residual).
- Reproduction of stored responses (`22_verify.csv`): the partial experiments match `data/frbus_paths.csv` (zfree, persistent) to 2e-4 at quarter 4 for equities (0.01410 vs 0.01431 per unit, 1.5 percent) and 3e-5 for the dollar (-0.04542 vs -0.04545); the yardstick hike is -0.4616 vs -0.4525 stored at quarter 4 (2 percent). Not due to the simulation horizon (identical results with end = start+23 and +39). Cause [inference]: the Board's LONGBASE downloaded today (file dated 2026-10-06) is a newer vintage than the one behind the stored paths. Consequence: funds-rate points of Figure 1 are 0.153 (equity) and 0.384 (dollar) here against 0.158 and 0.392 in the stored weights; use the stored numbers for the paper's weights and use this step for SHARES and shapes (shares are stable to the second digit).
- Hike spillovers at quarter 1-4 are within 5 percent of `data/frbus_hike_paths.csv` (stocks -14.5 percent vs -13.6, dollar 1.09 vs 1.10) [verified].

Limits [inference]:
- Policy rule inactive: in the partial experiments the funds rate, bill, Treasury curve, mortgage and car-loan rates, BBB spread, oil and the other index variable are held at baseline (as in the stored runs); the hike is the only experiment with the rule's variables endogenous.
- Stock wealth is the equity variable: the 5 log points of CAPE are mapped one-to-one to a 5 percent fall in household stock wealth at impact (as Figure 1 does); the wealth path then moves with the required-return shock.
- The half-life-4 path is priced by linearity from temporary shocks (same method as step 18), not by a direct simulation.
- The "replay" of the usual announcement response uses per-unit persistent effects times psi (equity and dollar mapped as above); the comparison with the hike's own spillovers prices the quarter-4 spillovers only, so within-year paths and the policy-rate channel are in the remainder. No new policy experiment was run: delivering a given two-year-yield change in FRB/US needs the policy rule's expectations path, which the model does not identify without further assumptions.
- Component contributions are of the fixed-weight aggregation and follow the model's own definitions; "domestic" = consumption + residential + business fixed investment.

## Update (reproducible set, same vintage as the weights)
Step 22 now runs through `lib/frbus_env.ensure_runtime()` (self re-run in `raw/frbus_venv`), reads the regenerated `data/frbus_paths.csv` from step 00 (same LONGBASE of 2026-10-06) and the weights from the results directory, and is part of `run_all.py` and the sync check (runtime 12 s). The comparison with the stored package responses now agrees to 1e-6 at every checked quarter (`22_verify.csv`), and the funds-rate points of Figure 1 equal the weights of step 02: 0.152707 and 0.383787 from the channels run against 0.152710 and 0.383790 from `frbus_weights.csv` [verified]. The earlier statement that the stored paths come from an older vintage no longer applies: the stored paths were regenerated.

## Policy-rate experiment (`22_policy_shock.py`, 5 s) and weights by persistence (`22_weights_persist.py`)
Defined and reported in `fci_paper/followup4/frbus_RESULT.md`.
