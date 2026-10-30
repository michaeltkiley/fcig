# 3. The market index (draft, 30 Oct 2026)

*Draft for review. Numbers are from the nominal construction (section 4 refines it to real rates and gaps to r\*). Items marked [check] are to verify before circulation.*

The index we propose is built entirely from observed data. Its weights come from how financial markets respond to monetary policy news, measured in narrow windows around
FOMC announcements. Its dynamics come from a small, transparent vector autoregression (VAR) with unemployment. Neither step relies on a large structural model. By contrast, the
weights of FCI-G, and of the macro-model index we use for comparison (section 5), come from FRB/US, a model that is a black box to most readers and is not widely used in research.
Everything in our index can be replicated from public data in a few lines of code. The price of this transparency is coverage: the index uses three variables (the 10-year Treasury
yield, equity valuations and the dollar) instead of the seven or more in FCI-G. Section 6 shows that this price is small.

## 3.1 Weights from the response to policy news

**Policy news.** We measure policy news at each FOMC announcement with the Nakamura-Steinsson (2018) factor: the first principal component of intraday moves in five
short-term interest-rate futures (current- and next-meeting federal funds futures and the second to fourth eurodollar futures), scaled so that one unit moves the 2-year
Treasury yield by 1 percentage point. The announcement-window data are from the San Francisco Fed's U.S. Monetary Policy Event-Study Database (USMPD), 253 announcements
from January 1996 to September 2026 [check: event coverage and window length as defined in USMPD].

**Responses.** In the same windows, a one-unit tightening of policy news raises the 10-year yield by 0.54 pp (se 0.06), lowers the S&P 500 by 7.8 percent (0.9) and raises the
dollar by 4.2 percent (0.5). These are the policy responses of the three variables, the column vector $\psi$.

**Weights.** We treat each variable's window move as the policy response times the news plus a non-policy disturbance, and choose weights $w$ that recover the policy
component as precisely as possible: $w \propto \Sigma^{-1}\psi$, normalized so that $w'\psi = 1$, where $\Sigma$ is the covariance of the non-policy disturbances (one-factor
generalized least squares). The normalization means a policy move that raises the 2-year yield by 1 pp raises the index by exactly 1. The weights are:

| Variable (level) | Weight | Contribution of a policy move |
|---|---|---|
| 10-year Treasury yield (pp) | 0.609 | 0.33 |
| Equity valuation (100 x ln CAPE, percent) | -0.051 | 0.40 |
| Real broad dollar (100 x ln, percent) | 0.065 | 0.28 |

The contributions ($w_j \psi_j$) sum to 1: all three variables matter, and equities matter most. Applied to the levels of the three variables, demeaned, the weights give the
index: financial conditions measured as the tightening of the 2-year yield that a policy move would need to produce the same configuration of the three variables.

**What the weights mean.** If every movement in the three variables came from policy, the index would equal the cumulated policy-induced change in the 2-year yield. Movements
not caused by policy also enter, with the same weights. The index treats them as if they were policy-equivalent: a fall in equity valuations unrelated to policy tightens the
index by as much as a policy-driven fall of the same size. Whether that is right depends on whether non-policy movements affect the economy like policy-driven ones; section 5
discusses the alternative, model-based view.

**Robustness (appendix).** Adding the Baa corporate yield changes little; with the full covariance its weight is negative (it moves with the 10-year on policy days, so the index
uses the difference), with a diagonal covariance every weight takes the sign of its policy response. [Figure: index with and without Baa.]

## 3.2 Dynamics from a transparent VAR: the flow

FCI-G measures a flow: the effect of recent changes in financial conditions on GDP growth over the next year. To give the market index a counterpart, we estimate how
unemployment responds to it.

**The VAR.** A two-variable monthly VAR in the unemployment gap (the unemployment rate less CBO's natural rate) and the market index, 1973-2026, with 12 lags and the months of 2020
treated with dummies; unemployment is ordered first, so it responds to the index only with a lag. Before 1990 the index is built from monthly averages of the same variables
(10-year Treasury, Shiller CAPE, Federal Reserve real dollar), matched to the daily-based series at the overlap.

**Results.** The market index helps predict unemployment (Granger F 3.3, p = 0.0001), and a one-unit tightening raises the unemployment gap significantly from month 3 to month 36
(bootstrap 95 percent bands). The response builds over about a year and then fades slowly; at 12 months it is 0.51 pp, about 1 percent of output by Okun's law. This 12-month
response is the index's yardstick, $\Phi(12)$. [Figure: unemployment response with bands; 4-lag version as a check.]

**Forward impetus.** Using the VAR's response profile $\Phi(m)$, we compute, as FCI-G does with FRB/US multipliers, the effect over the next 12 months of the index changes of
the past year:
$$ \text{FI}(t) = \sum_{m=0}^{11} \frac{\Phi(m+12)-\Phi(m)}{\Phi(12)}\, \Delta M(t-m), $$
in units of the index (a value of 1 means the past year's changes will raise unemployment over the next year by as much as a one-unit permanent tightening does in its first year).
Over 1991-2026, forward impetus correlates 0.73 with the published FCI-G (1-year lookback); the market index level correlates 0.31. The level and the flow answer different
questions: where conditions stand, and what they imply for growth ahead. We report both, as FCI-G (flow) and GS (level) each report one.

**Why the flow matters.** In local projections of unemployment a year ahead (section 7), levels of financial conditions add no information once the recent path of unemployment is
known; recent changes do. The forward impetus carries that information, and its estimated effect matches its yardstick (coefficient 0.50 against $\Phi(12)$ of 0.50-0.57).

[Figure 3: market index (level) and forward impetus, 1974-2026, r* baseline, with FCI-G (1-year) for reference.]
