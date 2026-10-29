# VAR specifications for the ECB-method index: why ours failed, and what the literature suggests (29 Oct 2026)

## What went wrong in our runs
- **1990-2025 sample, generalized impulse responses or NS-surprise identification:** a funds-rate rise held for 12 months lowered unemployment. Spreads narrowed after funds-rate rises, so the spread-heavy index loosened. NS surprises summed by month were a weak instrument (first-stage F 1.9-4.8).
- **1960 sample, 4 variables:** degenerate (the index is essentially the Baa spread alone; near-zero yardstick).
- **1973 sample, 6 variables, recursive:** the yardstick has the right sign (-0.21% output at month 12), but the index is spread-dominated (Baa spread 5-9 pp of funds rate per pp) and the dollar enters with a negative sign.

## Likely causes, with literature
1. **The funds rate is a poor policy indicator after 2008.** It sat at the lower bound in 2009-15 and 2020-22, while policy worked through forward guidance and asset purchases. Gertler and Karadi (2015) use the **1-year Treasury rate** as the policy indicator in a monthly VAR (IP, CPI, 1-year rate, Baa spread, excess bond premium), instrumented by high-frequency futures surprises. Output and inflation respond conventionally, and credit costs move much more than the short rate. ([VoxEU summary](https://cepr.org/voxeu/columns/monetary-policy-and-credit-costs); [BIS slides](https://www.bis.org/events/conf150310/gertler_karadi_presentation.pdf))
2. **Policy reacts to credit spreads.** Caldara and Herbst (2019, AEJ: Macro) find, with Bayesian proxy SVARs, that the systematic part of policy responds directly to corporate spreads. Omitting that feedback attenuates the estimated effects of policy shocks, including with Romer-Romer identification. Our recursive ordering put the funds rate *before* spreads, assuming no within-month response to them. ([FEDS 2016-049](https://www.federalreserve.gov/econres/feds/monetary-policy-real-activity-and-credit-spreads-evidence-from-bayesian-proxy-svars.htm); [AEJ](https://www.aeaweb.org/doi/10.1257/mac.20170294))
3. **Sample instability.** Recursive and narrative identifications give responses at odds with theory in post-1980s samples. Ramey (2016, Handbook of Macroeconomics, ch. 2) documents this, as do Aruoba and Drechsel (NBER WP 32417), who find that Romer-Romer shocks show no significant effect on activity in recent samples. Our 1973 sample works largely because it includes the Volcker period. ([Ramey](https://ideas.repec.org/h/eee/macchp/v2-71.html); [Aruoba-Drechsel](https://www.nber.org/papers/w32417))
4. **Surprises are predictable and information-laden.**
   - Bauer and Swanson (2023, AER) show surprises respond to public news ("Fed response to news"), and recommend orthogonalizing them to pre-announcement data. ([paper](https://sites.socsci.uci.edu/~swanson2/papers/fedinfo.pdf))
   - Miranda-Agrippino and Ricco (2021) build an "informationally robust" instrument and find a tightening is "unequivocally contractionary," with no price or output puzzles; they also stress model misspecification. ([BoE WP](https://www.bankofengland.co.uk/-/media/boe/files/working-paper/2017/the-transmission-of-monetary-policy-shocks))
   - Our NS surprises are raw (a project decision), so the information effect is in them.
5. **Many parameters.** With 8-9 variables and up to 6 lags (300-450 coefficients), the dynamics are imprecise. Bayesian shrinkage (Minnesota prior) is the standard remedy; the ECB used a ridge penalty on the weights.
6. **The index itself.** The method picks whatever best predicts inflation and unemployment. In US data that is credit spreads (consistent with the Gilchrist-Zakrajsek literature), which is a finding, not a bug. It makes the funds-rate conversion depend on how spreads respond to policy.

## Promising specifications (ranked by expected payoff for our purpose)
- **A. Gertler-Karadi policy indicator.**
  - The 1-year (or 2-year) Treasury as the policy variable in the yardstick, held +1 pp for 12 months, instrumented by high-frequency surprises.
  - The first stage is typically strong for the 1-year rate.
  - Works through the lower bound.
  - Sample 1990-2025.
  - The yardstick becomes "a 1 pp rise in the 1-year rate" (the expected funds-rate path); the funds rate stays in the index.
- **B. Funds rate ordered after the financial variables** (recursive). Policy can respond within the month to spreads, equities and the dollar (the Caldara-Herbst point). Cheap to run on the 1973 and 1990 samples.
- **C. Orthogonalized surprises** (Bauer-Swanson style: NS surprises purged of pre-announcement macro and financial news) as the instrument in A. This departs from the project's raw-surprise choice, but only inside this VAR.
- **D. Romer-Romer shocks as the instrument** for a 1969/1973-2007 sample, avoiding the lower bound. The narrative series ends in 2007 in the standard extensions.
- **E. Bayesian shrinkage** (Minnesota prior) on the VAR coefficients, allowing 6-12 lags without overfitting; combinable with A or B.
- **F. Excluding lower-bound months** (2009-15, 2020-22) from the funds-rate equation or the sample.
