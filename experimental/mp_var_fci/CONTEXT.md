# Context: the market index and what has already been learned (read before MP_QA.md)

30 Oct 2026. Source: `experimental/PROJECT_MEMORY.md` (esp. section 9, "Where we are"), `INDEX_QA.md` A49-A56, `lp_weights/RESULTS.md`, `fci_note/` (paper and replication package), all on branch
**`ccr-3a1fbe39-so6omu`** (not on `main` or on this branch). Earlier versions of this folder's notes were built on the wrong index (the five-variable Morgan Stanley-style one) and on a guess about your VAR; they are replaced.

## 1. The market index (MKT), as in the note
- **Weights from policy news.** Regress the event-window changes in the 10-year yield, equity valuation (100 ln CAPE) and real broad dollar (100 ln) on the **Nakamura-Steinsson (NS) policy-news factor** from the SF Fed USMPD
  (253 FOMC events, 1994 on); one-factor model with full error covariance (GLS; diagonal as sensitivity). Nominal weights per unit: 10-year 0.61, equities -0.051 per 1%, dollar 0.065 per 1% (GSS path: 0.97, -0.059, 0.098).
  Each variable carries about a third of a policy move. **Unit = a policy move that raises the 2-year yield by 1 pp.**
- **No FRB/US.** Independent of the Fed's model; BBB spread dropped because it narrows after hawkish path surprises (IV on the 10-year: -0.4 to -0.5 per 1 pp; not a Moody's timing artifact); corporate yields shown with rates.
- **Three steps**, like for like with existing indexes: nominal -> real -> **r*-gap (baseline: Laubach-Williams one-sided, full sample; Kiley as check)**, zero = 1973-2026 mean.
- **Dynamics: a two-variable VAR** in the unemployment gap and M, Cholesky with unemployment first, 1973-01..2026-09, 2020 months dummied, **12 lags (main), 4 lags (check)**. Phi(h) = unemployment response to a shock moving M by 1 on impact;
  yardstick Phi(12) (r*: 0.65 at 12 lags). Granger M -> u p about 0.0001-0.002. Unemployment response significant months 1-33 (r*, 1973-2026).
- **Level and flow.** Level = M. Flow = **forward impetus** (FCI-G form): sum over k < 12 of [Phi(k+12) - Phi(k)] / Phi(12) x dM(t-k). Correlates 0.84 with FCI-G (1-year, r* version); market-GS 0.99; market-FRB/US 0.94. Current pressure is appendix only.
- Latest (r*, Oct 2026): market -0.93, GS -1.23, FRB/US +0.27.
- The existing VAR's shock to M is a **financial-conditions shock** (u ordered first), not an identified monetary policy shock.

## 2. What has already been learned that bears on this project
1. **Activity's response to NS surprises has the wrong sign** in 1994-2025 monthly data (`lp_weights` E2): after a hawkish NS surprise unemployment falls (-2.2 pp per unit at 12 months, se 1.0; -2.7 for pure-policy events), core inflation rises a little.
2. **Bauer-Swanson-style purging** (E6): NS surprises regressed on pre-announcement news (12-month payroll growth, 3-month stock and oil changes, 3-month curve slope change; R2 0.13, stocks t 3.6); with purged surprises the unemployment response turns conventional (+0.46 at 12 months, +1.0 with more controls) but se are 1.3-1.6 and excluding 2008-09 flips the sign.
3. **Recursive funds-rate shock, 1973-2025** (E7): works: unemployment +0.32 (se 0.10) at 12 months per 1 pp, i.e. output -0.63% (FRB/US -0.45%).
4. **One instrument identifies one combination** (E1): one-at-a-time LP-IV yields market-type (inverse-response) weights; several instruments gave weak first stages (F 2.4-5.7).
5. **Gap test** (`fci_compare/gap_test.py`, memory 3b/3c): on impact the market and macro-model indexes agree (gap 0.02) but the delayed gap grows (+0.75 at 12 months, +1.83 at 24): later responses of equities and the dollar do not keep the impact pattern, so the common-dynamics assumption fails.
6. Information effects: acknowledged in one paragraph and set aside in the note (memory section 2). This project is where they get examined.
7. Memory 3f: IP rises after hawkish surprises, so theta from responses is uninformative.

## 3. Consequences for the design (proposals; decisions go through MP_QA.md)
- **The weights come from NS responses, so under the NS instrument M's impact response is 1 by construction.** NS-IV therefore cannot independently validate M on impact; the informative comparisons are (i) BS vs NS with the same M, (ii) M's responses after impact (dynamics), (iii) Cholesky, which uses no surprise data.
- **Sample mismatch is built in:** Cholesky can use 1973-2026 (as the VAR does), the instruments only 1994-2019 (2020+ questionable). Comparing Cholesky on both samples is the subsample test; the proxy-SVARs live in the short one.
- **The two-variable VAR is the base case** (u, M). The extension adds core PCE and the policy rate, giving a four-variable system and a defined monetary policy shock.
- **Units:** M is in pp of the 2-year yield, so the natural policy indicator for M-comparisons is the 2-year (or 1-year, as in GK), with the funds rate as the Cholesky/ZLB-limited alternative.

## 4. Comparison with Gertler-Karadi (2015) and Caldara-Herbst (2019)
**GK** (AEJ: Macro 2015): proxy-SVAR; policy indicator the **one-year government bond rate**; variables industrial production, CPI, Baa spread and the Gilchrist-Zakrajsek excess bond premium (EBP); sample 1979:09-2012:06; a 20 bp rise in the one-year rate raises the EBP about 8 bp on impact
([BIS slides](https://www.bis.org/events/conf150310/gertler_karadi_presentation.pdf), [VoxEU](https://voxeu.org/article/monetary-policy-and-credit-costs)). A later paper links GK's larger real effects to the Volcker years ([Adelaide](https://digital.library.adelaide.edu.au/dspace/bitstream/2440/140971/2/hdl_140971.pdf)).
**CH** (AEJ: Macro 2019): Bayesian proxy-SVAR, mainly 1994-2007; the policy rule responds directly to credit spreads and ignoring that biases all responses toward zero; monetary shocks explain about 20% of the variance of output and spreads
([FEDS](https://www.federalreserve.gov/econres/feds/monetary-policy-real-activity-and-credit-spreads-evidence-from-bayesian-proxy-svars.htm), [AEJ](https://www.aeaweb.org/doi/10.1257/mac.20170294)). Which spread series CH use: **not verified**.

| | GK / CH | Market index |
|---|---|---|
| Financial variable | one credit variable (EBP, Baa spread) in spread units | three prices (10-year, equities, dollar) combined with weights estimated from the policy-news response; unit = 1 pp of the 2-year |
| Where the weights come from | none (one series) | the same kind of surprise data used as the instrument |
| Credit | the whole financial block | dropped from the index: BBB narrows after hawkish path surprises |
| Long samples | 1979-2012 / 1994-2007 | 1973-2026 (VAR), 1994- (surprises) |
| Neutral rate | not addressed | r*-gap baseline |

Two observations to check, not conclusions: (1) GK find the EBP **rises** after a policy tightening, while the project found the BBB spread **narrows** after hawkish path surprises in USMPD; the series (EBP vs ICE BBB OAS), surprises (federal funds futures vs NS/GSS path) and samples differ, and a path surprise carries information-effect content, so this is exactly where the
information effect would show up. (2) CH's systematic-response argument has a direct counterpart: does the policy rate respond to M in the four-variable system, and does leaving M out bias the responses toward zero?
