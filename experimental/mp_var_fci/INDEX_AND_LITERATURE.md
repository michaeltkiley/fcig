# What the index is, and how it compares with Gertler-Karadi and Caldara-Herbst

30 Oct 2026. Part 1 is read from this repo's code, docs and data (`fcig_replicate.py`, `fcig_gs.py`, `multipliers.csv`, `fcig_replication_monthly.csv`,
`index.html`, the removed `analysis/` LP scripts in git history at `2ff91cf^`). Part 2 uses the cited sources; items marked **[not verified]** I could not confirm.

## 1. The index as built

**Two daily indexes, same page** (live at michaeltkiley.github.io/fcig):

| | Fed FCI-G replication | Goldman-style FCI |
|---|---|---|
| Source method | Ajello, Cavallo, Favara, Peterman, Schindler, Sinha (2023), FEDS Notes; Fed's published weights (`multipliers.csv`) | Goldman's published weights |
| Object | **Growth impulse**: pp of real GDP growth over the next year; positive = headwind | **Levels** index, mean 100 over 2000-2025; higher = tighter |
| Formula | sum over variables j and quarters i = 0..11 of w_i^j x (3-month change in X^j, i quarters ago); 1-year version uses i = 0..3 | 100 + 0.044 FFR + 0.451 10y + 0.396 BBB spread - 0.049 CAPE + 0.060 dollar (deviations from 2000-2025 means) |
| Variables | FFR, 10y Treasury, 30y mortgage, BBB yield, stocks (DJ Total Market), house prices (Zillow ZHVI), broad dollar | FFR, 10y, BBB-Treasury spread, CAPE (S&P 500 / E10), dollar |
| Frequency | daily (monthly published by Fed 1990-) | daily from 1990 |
| Checks | RMSE vs Fed monthly 0.086 since 1990 (0.05 since 2024) | monthly changes correlate 0.99 with Goldman's digitized series, level about 0.35 high |

Also on the page: "next year if conditions hold" (the Fed's row i+4 weights applied to the same changes), which gives the impulse still to come.

**Facts that matter for a VAR** (computed from the files):
- FCI-G is a **12-quarter distributed lag of 3-month changes**, so it is a filter, not a state variable. Monthly AR(1) is 0.97. A 36-month MA of changes
  cannot be summarised by 12 monthly VAR lags of itself without treating the filter as data.
- **Composition of monthly changes** (share of variance, 3-year version, since 2000): stocks 0.67, dollar 0.20, mortgage 0.06, BBB 0.05, house 0.02, FFR 0.00,
  10y 0.00. It is mostly an **equity-and-dollar** variable month to month, with slow-moving credit and rate parts.
- **The funds rate is almost not in it** in practice (cumulative weight 0.34, about 0% of variance), so the mechanical link to the policy instrument is small.
  The 10-year has a *negative* weight (-0.25 cumulative) because the mortgage rate (0.77) and BBB yield (1.06) already carry the level; read the three as one
  long-rate package, net +1.58 pp of growth impulse per sustained +1 pp, and the "pure spread" is not a separate component.
- Earlier **LP work on this index** (USMPD surprises, 1994-, monthly, removed in #7; recoverable with `git show 2ff91cf^:analysis/README.md`): path/forward-guidance
  surprises tighten both indexes on impact; the target effect is small; the 12-month build-up is a ZLB-era result; equity then dollar then BBB drive responses; LP-IV was weak
  (first-stage F about 12 full, 6 ex-ZLB); Swanson LSAP gave the largest effects. "Not done": Jarocinski-Karadi split, Bauer-Swanson orthogonalisation to lagged FCI components.

## 2. Gertler-Karadi (2015) and Caldara-Herbst (2019)

**Gertler-Karadi (AEJ: Macro 2015).** Proxy-SVAR; surprises in federal funds futures in a short window around FOMC announcements as external instruments; policy indicator is the
**one-year government bond rate** (used partly to avoid weak instruments; a two-year rate gives similar results); variables include industrial production, CPI, the Baa spread and the
**Gilchrist-Zakrajsek excess bond premium (EBP)**; sample 1979:09-2012:06 (slides). A policy-rate rise of about 20 bp raises the EBP about 8 bp on impact for roughly eight months. Sources:
[BIS slides](https://www.bis.org/events/conf150310/gertler_karadi_presentation.pdf), [VoxEU column](https://voxeu.org/article/monetary-policy-and-credit-costs). A later paper attributes
larger real effects in GK to the Volcker-disinflation years in the sample ([Adelaide](https://digital.library.adelaide.edu.au/dspace/bitstream/2440/140971/2/hdl_140971.pdf)).

**Caldara-Herbst (AEJ: Macro 2019).** Bayesian proxy-SVAR using high-frequency surprises; mainly 1994-2007; policy shocks cause a lasting output fall and tighter financial conditions; the central result is
that the **Fed's policy rule responds directly to credit spreads**, and ignoring that endogenous response **biases all responses to monetary shocks toward zero**; monetary shocks explain about 20% of the volatility
of industrial output and spreads. Sources: [FEDS working paper](https://www.federalreserve.gov/econres/feds/monetary-policy-real-activity-and-credit-spreads-evidence-from-bayesian-proxy-svars.htm),
[AEJ page](https://www.aeaweb.org/doi/10.1257/mac.20170294). Which spread series CH use **[not verified]**.

### Side by side
| | GK 2015 | CH 2019 | This repo's index |
|---|---|---|---|
| Financial variable | EBP (spread net of expected default; a risk-premium measure) and Baa spread | credit spread(s) | composite of rates, mortgage, BBB, equities, houses, dollar, weighted by Fed model-implied growth effects |
| What it isolates | credit-supply / risk-premium channel | the Fed's reaction to credit conditions | broad conditions in **growth units**; not a risk premium (BBB is a yield; the long-rate package mixes level and spread) |
| Dynamics | observed monthly state variable | observed state variable | FCI-G: 3-year filter of changes (not a state variable). GS-style: a level (state-like) |
| Dominant movement | credit | credit | equities and dollar (FCI-G); rates and BBB spread (GS-style, 0.45 + 0.40 weights) |
| Policy indicator | 1-year rate | funds rate (and shadow-rate-type options) **[not verified]** | FFR enters weakly |
| Sample | 1979-2012 | 1994-2007 | 1990-2026 (inputs), surprises 1994- |
| Frequency edge | monthly | monthly | **daily**, so event-window responses are possible |

## 3. What the comparison implies for the project

1. **Which variable to put in the VAR.** Use the **GS-style level** (state-like, contains an explicit BBB-Treasury spread, so closest to GK/CH) and, separately, the **FCI-G components** (the
   3-month-change contributions, which are not filtered) or the unfiltered stock/dollar/long-rate pieces. Use FCI-G itself as an *outcome* of a policy shock (growth impulse) as in the earlier LPs, not as a lagged regressor.
   My earlier proposal (MS-style baseline) is dropped: it is unverified and not the repo's main index.
2. **A horse race that already has a literature to cite.** Run the GK/CH setup (IP or unemployment, core PCE, policy indicator, credit variable) with (a) EBP/Baa spread only, (b) GS-style FCI, (c) FCI-G components, (d) both.
   The finding that matters: does the broader index add anything to a credit spread, given it is mostly equities and the dollar?
3. **CH's mechanism has a direct test here.** Does the policy indicator respond to the FCI (systematically) beyond the spread, and does omitting it bias the responses toward zero? That is a cleaner contribution than "FCI is more robust".
4. **Information effect.** Equities and the dollar are the main movers of the index and are exactly the Jarocinski-Karadi sign-restriction variables, so FCI components give an internal information-effect diagnostic and a Bauer-Swanson-style
   orthogonalisation (surprise on lagged FCI components, listed as "not done" in the old LP note). This is the most distinctive angle relative to GK and CH.
5. **Instrument strength is a known problem here**: earlier LP-IV had F of 6-12 with 2-year-based policy indicators; use the one-year rate, as GK do, rather than the funds rate, and report weak-instrument-robust bands.
6. **Overlap risk is real.** Adding spreads to a proxy-SVAR is GK/CH. The defensible contributions are (i) composite and daily-frequency measure beyond credit, (ii) the three-scheme comparison, (iii) the information-effect diagnostics using equities/dollar components.

## 4. Corrections to the first design note (NOTES.md)
- Section 4 said the Goldman-style index "partly mechanically responds to policy" through the funds rate and proposed an MS-style baseline. The funds rate has weight 0.044 (GS) and about 0% of FCI-G variance, so that concern is minor; the real
  issues are the FCI-G filter and the equity/dollar dominance. Baseline changed as in item 1 above.
- The note did not know about the earlier LP analysis, the USMPD surprise data, or the companion repo `michaeltkiley/monetary_policy_surprises`; NS and BS instruments should come from there / the USMPD workbook
  (check whether BS and NS shocks are available in that repo before rebuilding them).
