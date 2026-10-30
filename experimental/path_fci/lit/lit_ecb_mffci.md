# ECB Macro-Finance FCI (read 27 Oct 2026)

**Working paper.** Bletzinger, T., Martorana, G. and Mistak, J. (2026), "Looser, tighter, clearer: a new Financial Conditions Index for the euro area," ECB Working Paper No 3193, February. https://www.ecb.europa.eu/pub/pdf/scpwps/ecb.wp3193~9db57822d4.de.pdf

**Box.** "The evolution of financial conditions in the euro area and the United States: a Macro-Finance FCI perspective," ECB Economic Bulletin 6/2026 (same authors). https://www.ecb.europa.eu/press/economic-bulletin/focus/2026/html/ecb.ebbox202606_05~26c3018e11.en.html

## Method (WP sections 3.1-3.2)
- **Model.** The full VAR is Y_t = (M_t', Z_t')' = mu + Phi Y_{t-1} + Sigma e_t. It is collapsed with Gamma = [I 0; 0 alpha'] to a small VAR in (M_t, F_t), where F_t = alpha'Z_t.
- **Assumption 1 (linearity).** The macro rows load on each Z_i in proportion to alpha_i, at every lag and in the shocks. The financial rows aggregate the same way. In words, all financial variables "share the same impact on macroeconomic variables, once scaled by the relevant weight."
- **Assumption 2 (orthonormality).** ||alpha||_2 = 1. So squared weights are closer to variance shares, and weights do not sum to one.
- **Estimation.**
  - Maximum likelihood of the reduced VAR (two lags) with the norm constraint and a generalized ridge penalty lambda alpha' C^-1 alpha, with C = Cov(Z) and lambda = 77.
  - Variables are selected by the conditional likelihood of M given F, because the joint likelihood is not comparable across sets of Z.
- **Neutral level.** The VAR unconditional mean, F converging there as inflation is at target and output at potential. Compared with the FCI* of Caballero et al. (2025).
- **Units.** Rates in percent untransformed; CAPE and NEER as % deviations from mean. The index has a "unit and scale similar to a policy rate." The textbook VAR (inflation, output, policy rate) is the nested case alpha = e_policy rate.

## Euro area results (monthly 2007-2025; HICP gap, Hamilton-filtered output gap)
- **Weights** (point estimates, normalization ||alpha|| = 1):

| Variable | Weight |
|---|---|
| eSTR | 0.631 |
| OIS 10-year | 0.520 |
| real OIS 1y1y | 0.287 |
| real OIS 5-year | 0.351 |
| sovereign spread 2-year | 0.151 |
| sovereign spread 10-year | 0.212 |
| corporate spread | 0.227 |
| CAPE | -0.038 |
| NEER | 0.075 |

- **Full term structure.** Bimodal weights (overnight and 10-year).
- **Benchmarks.** Correlation with the GS euro area FCI 0.83 and the WA-FCI 0.93 in levels, about 0.7 in daily changes. The MF-FCI spans the first three principal components (0.67, 0.64, 0.43).
- **Forecasts.** Beats GS, WA-FCI, the PCs and eSTR in out-of-sample forecasts of inflation and the output gap (1-4 months).
- **Structural VAR** (sign/zero restrictions, supply, demand and financial shocks). Financial conditions transmit to activity within about one year and to inflation within almost two.

## US version (Bulletin box)
- **Data.** Monthly 1999-2025; PCE inflation gap; output gap.
- **Variables.** Effective funds rate, 10-year Treasury, real 2-year forward 1 year ahead, real 5-year, mortgage spread (30-year mortgage less 30-year Treasury), A-rated corporate spread, CAPE, nominal effective dollar.
- **Weights.** Funds rate 0.63; real rates about 0.45 each; 10-year about 0.40; spreads about 0.11 each; CAPE negative; dollar smallest. The small dollar weight is attributed to low US trade openness and the dollar's global role.
- **Results.**
  - Co-moves with GS, WA-FCI and FCI-G, especially in stress. It diverges when the others weight equities more heavily.
  - US-euro area index correlation is positive and higher in stress, mainly through risk assets.
  - Daily index changes are regressed on Jarocinski-Karadi shocks: a Fed tightening raises the US index and, less, the euro area index, through risk assets, partly offset by the exchange rate.

## Relevance to this project
See `experimental/DYNAMICS_PLAN.md`, Part C.
- **Closest prior work on a policy-rate-scaled FCI.** But its scale comes from the norm constraint, not from a funds-rate experiment.
- **Dynamics.** Its Assumption 1 is the common-dynamics restriction that makes a static levels index valid; we propose to test it.
- **Weights.** They come from in-sample VAR fit, a third principle next to model partials (FRB/US) and announcement-window responses (market).
