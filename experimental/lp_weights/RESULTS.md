# Local-projection routes to macro-relevant weights (exploration, 29 Oct 2026, while the user was away)

The question: can local projections (LPs), with NS policy surprises as the instrument, deliver either something like the ECB index or something like the FRB/US macro-model weights (each variable's effect on activity, normalized by a funds-rate yardstick)?

Data: monthly, 1994-2025 for the surprise-based work (2020 excluded), 1973-2025 for E7. Activity is the unemployment gap; inflation is the core PCE gap. The financial variables are the macro-model set (levels). Logs: `lp_explore.log`, `lp_orthogonal.log`, `lp_long_recursive.log`.

## Results

**E1. One variable at a time, LP-IV with NS as the instrument: not a new weighting (algebra).**
- With one instrument, the IV coefficient for variable j is (activity response) / (x_j response).
- Multiplied back by x_j's response, every variable gives the same number (here -2.24, the shock's total effect on unemployment).
- So the "effects" are just inverse responses to policy, the market-weight logic again, scaled by a common factor. They do not separate each variable's own effect.
- One instrument identifies one combination; separate effects need several instruments or several horizons (E3, E5).

**E2. The obstacle: activity's response to NS surprises has the wrong sign in 1994-2025 monthly data.**
- After a hawkish NS surprise, unemployment *falls*: -2.2 pp per NS unit at 12 months (se 1.0) for all events, -2.7 (se 1.0) for pure-policy events.
- Core inflation rises a little.
- Any method that needs activity's response to the surprise (E3, E5, the VAR yardsticks) inherits this.

**E3. Multi-horizon identification (the tutorial's g_h = theta' psi_h).**
- It "works" mechanically (condition number 47 with 3 variables), but because g_h is wrong-signed, the effects come out wrong-signed: 10-year -0.44 u pp per pp.
- Bootstrap bands span zero widely. Not usable.

**E4. Predictive LP weights normalized by the complete-transmission sum.**
- theta comes from regressing u(t+h) - u(t-1) on all financial levels, with macro controls; it is divided by theta'psi (psi = responses to a 1-unit NS surprise).
- This avoids activity's response to NS. Spreads and equities have the expected signs.
- But the 10-year comes out with the wrong sign, and theta'psi is near zero at 6 and 12 months: it changes sign between horizons (-0.011 at h = 6, +0.039 at h = 12, -0.43 at h = 24).
- So the weights explode and flip (mortgage spread -54.5 at h = 6, +15.6 at h = 12, -1.4 at h = 24). Not usable.

**E5. LP-IV with four instruments (pure-policy, information, MP1, GSS path) for the 10-year, equities and dollar together.**
- Weak: first-stage F 2.4-5.7.
- All three effects positive, including equities (wrong sign), with large standard errors. Not usable.

**E6. Orthogonalized surprises (Bauer-Swanson style).**
- NS surprises regressed on pre-announcement news (12-month payroll growth, 3-month stock and oil changes, 3-month curve-slope change): R2 0.13; stocks significant (t 3.6).
- With the purged surprises the unemployment response turns conventional (+0.46 at 12 months; +1.0 with more controls) and inflation falls.
- But standard errors are 1.3-1.6, and excluding 2008-09 flips the sign again.
- So the information/"Fed response to news" problem is real, but even after purging, monthly surprise data since 1994 cannot pin down activity's response.

**E7. Long-sample LP with a recursive funds-rate shock (1973-2025): the one design that works.**
- Shock: the funds-rate residual given current inflation and unemployment and 12 lags of everything.
- Unemployment response to a 1 pp shock: 0 at 3 months, +0.10 at 6, **+0.32 (se 0.10) at 12**, +0.43 at 18, +0.45 at 24 and 36.
  - That is an output equivalent of -0.63% at 12 months (FRB/US -0.45% at 4 quarters).
  - Conventional and precise. The funds rate itself fades to about +0.1 by 12 months (an impulse, not held).
- Weights (theta from the predictive LP at 12 months divided by this yardstick, pp of funds rate per unit):

| Variable | Weight |
|---|---|
| Policy rate | 1.05 |
| 10-year | -0.30 (theta not significant) |
| Mortgage spread | 0.45 |
| Baa spread | 0.80 |
| Equities (per 1%) | -0.155 |
| Dollar (per 1%) | 0.057 |

- *Policy rate check:* its weight is about 1. Its predictive coefficient (+0.33) matches the shock's effect (+0.32), so both measure "a funds-rate innovation with its usual aftermath."
- *What theta is:* only the policy rate and equities are precisely estimated. theta is a predictive association (each level's innovation given 12 lags of everything, with its typical aftermath), not a causal partial effect.
- *Equities dominate the index:* the equity weight (-0.155 per 1%, five times FRB/US) makes the index swing widely (sd 9.7 pp; latest -10.8).

## What we learn
1. Within the post-1994 surprise data, NS surprises identify **financial** responses well (the market lens) but not **activity** responses. Every LP or VAR route that needs activity's response to the surprise fails or is too imprecise. This matches the literature (Ramey 2016; Bauer and Swanson 2023; Miranda-Agrippino and Ricco 2021).
2. One-at-a-time LP-IV reproduces market-type (inverse-response) weights: a useful clarifying point for the weighting note.
3. A model-free output-lens yardstick is available from the long sample with recursive identification (E7). The per-variable effects remain the hard part: predictive LPs give imprecise and partly implausible effects (10-year negative, equities large).
4. A credible output lens still needs a structural model for the per-variable effects (FRB/US). The data can supply a cross-check on the yardstick: the long-sample LP's -0.63% is in the same range as FRB/US's -0.45%.

## Options for the user
- **(a)** Use E7's yardstick as an empirical cross-check on the FRB/US yardstick in the note. No new index.
- **(b)** Build an "LP macro index" from E7: the weights in the table above, flagged as predictive, not causal.
- **(c)** For the ECB-method index, keep the 1973 recursive VAR version, whose yardstick E7 corroborates (right sign, similar size).
- **(d)** Report the ECB-method index in its own units and use E2/E6 in the text to explain why surprise-identified conversions fail.
