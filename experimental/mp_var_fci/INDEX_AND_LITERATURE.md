# The market FCI as the basis of the project, and how it compares with Gertler-Karadi and Caldara-Herbst

30 Oct 2026. Revised after reading `experimental/ms_fci/` (`README.md`, `NOTES.md` sections A-H, `frbus_sensitivities.py/.csv`, `ms5_level.py`, the daily outputs). An earlier version of this
file treated the Fed FCI-G and Goldman-style indexes as the "market index"; that was wrong. They are the sister indexes in the main repo, useful here only as robustness checks.
I have **not** seen the existing two-variable unemployment/market-FCI VAR (not in `fcig`, `Bvar`, `resource_utilization` or `output_gap/unemployment_risk`); assumptions about it are listed in section 4.

## 1. The market FCI as built

**Concept (NOTES section C).** Five daily variables, each expressed as the **federal funds rate change that would have the same effect on GDP**:

    level(t) = 0.569 (r10 - mean) + 0.127 (BBB spread - mean) - 0.032 * 100 ln(CAPE / mean) + 0.100 * 100 ln(real dollar / mean) + 0.0080 * 100 ln(real WTI / mean)   [q4 weights]

Positive = tighter than the 1990-2026 average, in **pp of funds rate**. The weights are FRB/US funds-rate equivalents: GDP effect of a partial shock to one variable (others held at baseline, funds rate fixed)
divided by the GDP effect of a **+1 pp funds-rate hike with full transmission** (q4: -0.45% GDP; q8 -0.95%; q12 -1.43%). That hike moves the 10-year +0.37, stock wealth -13.2%, real dollar +1.6%, BBB spread +0.05 pp, oil +0.06% at q4.
Horizons q4/q8/q12 are options.

**Why it is the right object for a monetary-policy VAR.**
1. **Same units as the policy instrument.** A funds-rate shock and the index move in the same pp. The model implies a built-in benchmark: after a +1 pp policy shock with full transmission, the index should rise by about 1
   (partials sum to the full hike within about 4% at q4, 3% at q8, 11% at q12; NOTES section C). Deviation from 1 measures under- or over-transmission, and the components say where.
2. **No funds-rate term.** The policy rate is not an input (NOTES section D, "weak validation before 2008": correlation with the effective funds rate +0.17 for 1990-2008; with the SF Fed proxy +0.94 for 2020-2026; with r*-gap real policy rate +0.54 for 2022-2026).
   Its response to a policy shock is therefore a pure market-transmission response, not a mechanical one, and it keeps moving at the zero lower bound when the funds rate does not.
3. **It maps back to growth.** Because the weights come from FRB/US, an index response can be turned into an implied GDP effect (index change x 0.45% per pp at q4) and compared with the unemployment response the VAR estimates.
4. **Variants in the repo:** nominal / real / **r*-gap** 10-year (`--rstar`, Kiley IJCB 2020 one-sided r*; the adjustment moves early-1990s readings by 1-1.5 pp and 2010-2021 by +0.5 to +1.0 pp); q4/q8/q12; `--twosided`; `--source frbus`.
   The `--erp` equity variant is explicitly **not recommended** (valuation has no stable relation with the real 10-year yield).

**Properties relevant to a VAR** (computed from `ms5_level_daily_rstar.csv`, monthly last observation, 1990-2026):
- Stationary by construction (deviation from mean); monthly AR(1) 0.94, sd 0.85 pp, sd of monthly change 0.28 pp.
- Share of variance of monthly changes: **dollar 0.39, equities 0.34, 10-year about 0.23, BBB spread 0.02, oil 0.02** (since 2009: dollar 0.44, equities 0.33, BBB 0.02, oil 0.00).
  The credit spread, the focus of Gertler-Karadi and Caldara-Herbst, is a **minor part** of this index.
- Latest (20 Oct 2026): +0.73 pp (r*-gap q4; 10-yr +0.44, BBB -0.12, equities -1.35, dollar +1.43, oil +0.34), 81st percentile; since 27 Feb +0.98 pp (3.9 hikes).
- Correlation of daily changes with the GS FCI 0.81 (0.90 without oil); with the Fed FCI-G since 2020: 0.54 (3-year), 0.47 (1-year).

**Known weak links (from the project's own notes, so the VAR should carry them as caveats):** sensitivities start from the 2040 steady state (a 2026 start would scale equivalents about 13% lower, oil about 18%); VAR expectations, not model-consistent;
the 10-year stands for the whole long end; the stock shock is valuation with earnings fixed; linear extrapolation over 36 years; real-dollar splice, CAPE E10 extrapolation and the filtered r* (high in the 1990s, 2020Q2 artifact) are the weakest data links;
the weights are FRB/US-implied, so the index embeds the Fed model's view of transmission. The Morgan Stanley five-variable index itself is unverified; this is a reconstruction of the described method, which is how it should be described.

## 2. Gertler-Karadi (2015) and Caldara-Herbst (2019)

**Gertler-Karadi, AEJ: Macro 2015.** Proxy-SVAR with federal-funds-futures surprises in a short window around FOMC announcements as external instruments; policy indicator the **one-year government bond rate** (chosen partly to avoid weak instruments;
two-year similar); variables include industrial production, CPI, the Baa spread and the **Gilchrist-Zakrajsek excess bond premium (EBP)**; sample 1979:09-2012:06 (authors' slides).
A 20 bp rise in the one-year rate raises the EBP about 8 bp on impact for about eight months. Sources: [BIS slides](https://www.bis.org/events/conf150310/gertler_karadi_presentation.pdf), [VoxEU](https://voxeu.org/article/monetary-policy-and-credit-costs).
A later paper attributes GK's larger real effects to the Volcker-disinflation years ([Adelaide](https://digital.library.adelaide.edu.au/dspace/bitstream/2440/140971/2/hdl_140971.pdf)).

**Caldara-Herbst, AEJ: Macro 2019.** Bayesian proxy-SVAR, mainly 1994-2007; monetary shocks lead to a lasting output fall and tighter financial conditions; the policy rule **responds directly to credit spreads**, and ignoring that biases all responses toward zero;
monetary shocks explain about 20% of the variance of industrial output and spreads. Sources: [FEDS paper](https://www.federalreserve.gov/econres/feds/monetary-policy-real-activity-and-credit-spreads-evidence-from-bayesian-proxy-svars.htm),
[AEJ](https://www.aeaweb.org/doi/10.1257/mac.20170294). Which spread series they use **[not verified]**.

### Side by side
| | GK 2015 | CH 2019 | Market FCI (this project) |
|---|---|---|---|
| Financial block | EBP + Baa spread: credit risk premium | credit spread(s) | five prices (10-yr, BBB, equity valuation, real dollar, oil) aggregated |
| Units of the financial variable | pp of spread | pp of spread | **pp of funds rate** (growth-equivalent) |
| Policy indicator | 1-year rate | funds rate **[not verified]** | funds rate or 1-year rate; index excludes it |
| What the response tells you | credit premium responds to policy | policy rule responds to credit | transmission relative to a **model benchmark of 1**; which channel carries it; policy reaction in funds-rate units |
| Credit's role | the whole financial block | the whole financial block | about 2% of monthly variance |
| Sample | 1979-2012 | 1994-2007 | 1990-2026 daily; surprises from 1994 |
| Real-rate neutral | not addressed | not addressed | r*-gap variant |

**Illustration of the unit point (rough, mixes a 1-year-rate shock with the funds-rate benchmark).** GK's EBP response is about 0.4 pp per pp of policy rate. At the index's BBB weight (0.127) that is 0.05 pp of funds-rate equivalent per pp of policy rate.
FRB/US's own spread response (+0.05 pp per 1 pp hike) is 0.006. The empirical credit response is perhaps 8 times the model's, yet both are a few percent of the roughly 1 pp the full-transmission hike should deliver.
So most of any market response to a policy shock must come through the 10-year, equities and the dollar; credit alone cannot make the transmission ratio close to 1.

## 3. What the comparison implies

1. **Transmission ratio.** Define the policy shock as a unit shock to the policy indicator and report the cumulative index IRF (pp) and each component's contribution. Test against the model value (about 1 at q4 for a funds-rate shock).
   GK and CH cannot do this because their financial variable is not in policy units.
2. **CH's mechanism in policy units.** Regress/estimate the policy indicator's systematic reaction to the index. The coefficient is interpretable: -1 means the Fed fully offsets the market's tightening; 0 means it ignores it.
   This is the Morgan Stanley framing in `NOTES.md` ("the Fed doesn't need to deliver the tightening the market already did") put into a VAR. Test CH's claim that omitting it biases responses toward zero, using a composite instead of a spread.
3. **Information effects.** Equities, the dollar and the 10-year (91% of the monthly variance) are the variables behind Jarocinski-Karadi sign restrictions and the information-effect critique. A "tightening" instrument that lowers the market index
   (equities up, dollar down) is information-contaminated. Test (i) the sign of the index response to the raw NS and BS instruments, (ii) Bauer-Swanson-style orthogonalisation to lagged index components, (iii) how the unemployment IRF changes.
4. **Subsample robustness.** The r*-gap variant removes the effect of a moving neutral rate on what "tight" means across 1990s / 2010s / 2020s. If IRFs are less subsample-dependent with the r*-gap index than with the nominal one, that is a direct, testable contribution.
5. **Oil as a control.** Oil is in the index with a small weight but big 2026 moves (0.39 pp of the 0.98 pp since 27 Feb). In a policy-shock VAR, oil is a supply-shock confounder: report with and without the oil term.
6. **Overlap risk.** Financial variables in proxy-SVARs are GK/CH. What is new here: the funds-rate-equivalent, FRB/US-anchored composite, the benchmark-1 transmission test, the policy-reaction coefficient in policy units, and the r*-gap variant. Whether the same exercise exists
   in the literature (e.g. SF Fed proxy funds rate in VARs, Bauer-Swanson-style work with broad FCIs) needs a literature search.

## 4. Assumptions about your existing 2-variable VAR (please correct)
Unemployment rate and the market FCI level, monthly or quarterly, probably the r*-gap or nominal q4 version. Unknown to me: frequency, lags, sample, which variant and horizon, Cholesky order, and what "impetus" refers to (my guess: the policy-rate-equivalent impulse of the index).
