# MP-shock VAR project: decisions (one at a time, as in INDEX_QA / REAL_QA / RSTAR_QA)

Rule from the project: propose, then ask; no consequential choice without your guidance. Answers go in this file as MP-A1, MP-A2, ...

## Project (my understanding of your request, 30 Oct; please correct)
Extend the two-variable VAR (unemployment gap, market index) with core PCE inflation and the policy rate; identify monetary policy shocks by (a) Cholesky ordering, (b) Nakamura-Steinsson external instrument, (c) Bauer-Swanson external instrument;
ask whether adding the market index makes the impulse responses more robust to the identification scheme, larger, less subsample-dependent and less dependent on the information effect. Read `CONTEXT.md` first.

## Hypotheses and tests (proposal; fixed after your answers)
| Claim | Test |
|---|---|
| Robust to identification | distance between unemployment/inflation IRFs across Cholesky / NS-IV / BS-IV, system with vs without M |
| Larger | peak and cumulative responses per 25 bp of the policy indicator; compare with E7 (-0.63% output at 12 months) and FRB/US (-0.45%) |
| Less subsample-dependent | Cholesky 1973-2026 vs 1994-2019; pre-2008 / post-2008; nominal vs real vs r*-gap M (`PROJECT_MEMORY` says r* matters a lot over 1990-2026: real vs r* corr about 0.6) |
| Less information-effect dependent | sign of the unemployment response to raw NS vs BS-purged instruments (E2 vs E6); M's own response to each instrument; first-stage strength with and without M |
| CH counterpart | policy-rate reaction to M; effect of omitting M |

## Questions, in the order I would take them
**MP-Q1 [answered, see MP-A1]. Policy indicator.** M is in pp of the 2-year yield per NS unit. Options: (a) the federal funds rate (Cholesky across the full 1973-2026 sample, ZLB problem for 2009-15), (b) the 2-year Treasury yield (units match M; instrument first stage strong), (c) the 1-year yield (as GK), (d) run (a) for Cholesky and (b) or (c) for the proxy-SVARs. I would suggest (d), with the unit conversion stated. Which?

**MP-Q2. Where do the instruments come from?** NS: the factor already built in `path_fci/path_fci.py` from the USMPD workbook. BS: the Bauer-Swanson (2023) orthogonalized surprises (public) or my own purge on the USMPD data as in E6. Use the published BS series, my E6-style purge, or both?

**MP-Q3. Samples.** Cholesky: 1973-01..2026-09 with 2020 dummied (as the VAR). Instruments: 1994-2019, or 1994-2025 with 2020 dummied? Whether 2021-2025 (inflation surge, anticipated hikes with small surprises) belongs in the proxy-SVARs.

**MP-Q4. Which index cases.** The note's baseline is r*-gap (LW); nominal and real are the earlier steps. Run all three, with the baseline reported first?

**MP-Q5. Inflation variable.** Core PCE gap as in `lp_weights`, or core PCE 12-month rate?

**MP-Q6. Comparators.** Run the same system with the real GS index and the all-real FCI-G (open item R14 in the memory), or only the market index at first?

## Answers
**MP-A1 (30 Oct 2026). Policy indicator and scaling.** [decided] Main case: the **funds rate** is the policy variable in the four-variable VAR (unemployment gap, core PCE, funds rate, market index) for all three schemes, and the monetary policy shock is **scaled on the market index** (a shock that moves the index by one unit, i.e. a 2-year-yield pp),
with the funds-rate response reported as a variable. Robustness: the **2-year yield** replaces the funds rate as the policy variable and the shock is scaled on it (needs a monthly 2-year series, FRED GS2 from 1976). Not chosen: funds-rate scaling as main, 1-year yield.
Reasoning recorded: a proxy-SVAR needs no ordering, so two fast variables (policy rate, index) are fine and Cholesky is the scheme that needs an arbitrary order; scaling on the funds rate has a weak first stage (NS is path-heavy; ZLB), so it is avoided in the main case.
Cautions: the index's first stage on the NS instrument is strong by construction (weights estimated from NS responses); the Bauer-Swanson first stage on the index is the non-circular test; the funds-rate equation is misspecified at the ZLB, so report an ex-ZLB check.
