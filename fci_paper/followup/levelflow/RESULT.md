# Level or flow? (Note A; no surprises used)

**Question.** Does the level or the 12-month change (flow) of an index carry the information about the economy a year ahead, in the mean and the lower tail, and does the nominal/real/r* basis matter?

**Design (fixed in advance, `common.py`).** 14 series: market, GS, FRB/US, FCI-G at each step; NFCI, ANFCI as given. Level x_t, flow x_t - x_{t-12}, standardised, own lags always. Outcomes at 12 months: change in unemployment gap, payroll growth, GDP growth (quarterly). Origins 1976-03 to 2025-10 (n=556/557), 2020-21 windows dropped. NBER recessions in sample: five (1980, 1981, 1990, 2001, 2008). Out of sample from 1995: n=331, two recessions. GDP: 186 quarters. The primary family is payroll growth, tau=0.1, out-of-sample pinball loss (42 tests, Holm and BH applied); everything else is secondary.

**(a) Mean** [verified, `out/mean_results.csv`]
- Unemployment change, level and flow together: for market, GS and FRB/US the flow has HAC t of 3.8 to 5.9 at every step; the level 0.0 to 1.0. Adjusted R2 gain: flow 0.12 to 0.15, level 0.01 to 0.05.
- The r* basis raises the flow t: market 3.9 (nominal), 4.3 (real), 5.2 (r*); GS 4.0, 4.5, 5.3; FRB/US 3.8, 4.1, 4.9. Differences between steps are not tested here.
- FCI-G (a flow by construction): its reading carries the signal (t 2.8 to 3.0); its change adds nothing. NFCI and ANFCI: the level (t 3.8, 3.0); the flow adds nothing.
- Payroll growth: same split (flow t -2.9 to -3.2).
- Out of sample, rate-based indexes gain nothing (RMSE ratios 0.94 to 1.05, |DM t| < 1.9). NFCI/ANFCI help unemployment a little (ratio 0.87 to 0.91, DM t -1.6 to -2.0).

**(c) The tension** [verified, `out/granger_results.csv`]. Write the 12 lags of the level as the current level (its coefficient is the sum of the lag coefficients) plus 11 differences. Market r*, VAR unemployment equation: all 12 lags p=6e-9; the sum (the level) p=0.17; the 11 differences p=2e-7. GS (sum p 0.15) and FRB/US (0.35) are the same, as are the nominal and real steps (sum p 0.08 to 0.37). The Granger result is the movement of the level within the year, not where it stands. For FCI-G, NFCI and ANFCI the sum is significant (p<0.001).

**(b) Lower tail** [verified, `out/quantile_results.csv`]
- In sample, payroll growth, tau=0.1: flow coefficients for market, GS and FRB/US are negative with 90% block-bootstrap intervals excluding zero at every step (market r* -0.63 [-0.99, -0.09]; GS r* -0.97 [-1.11, -0.37]); levels near zero. The median is the same, so the tail matches the mean. NFCI and ANFCI levels shift the 10th percentile (-1.14 [-2.07, -0.55]; -1.41 [-2.01, -0.77]).
- Out of sample the tail is untestable. Best pinball ratios 0.76 (ANFCI level), 0.91 (GS r* flow). Four of 42 raw one-sided p < 0.05 (two expected by chance); Holm minimum 1.0, BH 0.47. Two recessions.
- GDP, secondary: NFCI and ANFCI levels at tau=0.1 give ratios 0.62 and 0.56 (DM t -4.6, -4.7), resting on 2008 [inference]. Rate-based indexes: nothing. The positive 90th-percentile level coefficient for market and GS probably reflects the common fall in growth and rates [inference].

**Verdict.** Market, GS, FRB/US: **flows**, in the mean and the in-sample lower tail (tail same as mean); the r* basis strengthens the flow signal (untested). NFCI, ANFCI: **levels**. Out-of-sample content and the tail cannot be tested with two recessions.

**Recommendation.** Yes, in Section 5.2 in place of "levels add nothing". It answers one question, whether the signal sits in the level or the change, and the sum-versus-differences result removes the contradiction with the Granger test. Frame it on Adrian, Boyarchenko and Giannone: the NFCI level carries the tail; rate-based indexes carry it through changes. Claim the tail in sample only, with one sentence on two out-of-sample recessions.
