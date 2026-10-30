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

**MP-Q2 [answered, see MP-A2]. Where do the instruments come from?** NS: the factor already built in `path_fci/path_fci.py` from the USMPD workbook. BS: the Bauer-Swanson (2023) orthogonalized surprises (public) or my own purge on the USMPD data as in E6. Use the published BS series, my E6-style purge, or both?

**MP-Q3 [answered, see MP-A3]. Samples.** Cholesky: 1973-01..2026-09 with 2020 dummied (as the VAR). Instruments: 1994-2019, or 1994-2025 with 2020 dummied? Whether 2021-2025 (inflation surge, anticipated hikes with small surprises) belongs in the proxy-SVARs.

**MP-Q4. Which index cases.** The note's baseline is r*-gap (LW); nominal and real are the earlier steps. Run all three, with the baseline reported first?

**MP-Q5. Inflation variable.** How should inflation enter the VAR: core PCE 12-month rate, core PCE price level (log), or another measure? [answered, see MP-A5]

**MP-Q6. Comparators.** Run the same system with the real GS index and the all-real FCI-G (open item R14 in the memory), or only the market index at first? [answered, see MP-A6]

## Answers
**MP-A1 (30 Oct 2026). Policy indicator and scaling.** [decided] Main case: the **funds rate** is the policy variable in the four-variable VAR (unemployment gap, core PCE, funds rate, market index) for all three schemes, and the monetary policy shock is **scaled on the market index** (a shock that moves the index by one unit, i.e. a 2-year-yield pp),
with the funds-rate response reported as a variable. Robustness: the **2-year yield** replaces the funds rate as the policy variable and the shock is scaled on it (needs a monthly 2-year series, FRED GS2 from 1976). Not chosen: funds-rate scaling as main, 1-year yield.
Reasoning recorded: a proxy-SVAR needs no ordering, so two fast variables (policy rate, index) are fine and Cholesky is the scheme that needs an arbitrary order; scaling on the funds rate has a weak first stage (NS is path-heavy; ZLB), so it is avoided in the main case.
Cautions: the index's first stage on the NS instrument is strong by construction (weights estimated from NS responses); the Bauer-Swanson first stage on the index is the non-circular test; the funds-rate equation is misspecified at the ZLB, so report an ex-ZLB check.

**MP-A2 (30 Oct 2026). Instruments.** [decided] NS: the policy-news factor already built in `path_fci` from USMPD (279 events, Feb 1994-Sep 2026). Bauer-Swanson: **my own purge now** (E6 style: NS surprises regressed on pre-announcement news, residual = instrument; same events as NS so NS vs BS differ only in the purge),
**published Bauer-Swanson series later** if the user provides the file, then report both. Location of the published series not confirmed (paper: NBER w29939); do not guess a URL.

**MP-A3 (30 Oct 2026). Sample.** [decided] Proxy-SVARs (NS and BS): **1994-01 to 2026-09 with 2020 monthly dummies**, the same treatment as the preferred 1973-2026 VAR; pre-COVID 1994-2019 reported as a check.
Cholesky: **1973-01 to 2026-09, 2020 dummied** (as the VAR) **and** on the proxy window 1994-2026-09, so the schemes can be compared on the same sample and the sample effect is separate.
Facts used (USMPD, 279 events): 1994-2007 119 events; 2008-15 68; 2016-19 33; 2020 13 (6 unscheduled, mostly March emergency cuts); 2021-26 46. Surprise mix shifts to path after 2020 (sd ED4 10.1 bp, sd MP1 2.4 bp). 213 of 311 months in 1994-2019 contain an event (the monthly instrument is zero otherwise).
Earlier results show the sample can change the finding (lp_weights E2 used 1994-2025 excluding 2020; E6 flipped sign when 2008-09 was dropped), so sample checks are part of the tests, not an afterthought. Open detail: how the 2020 event months enter the instrument (zero them, or keep with dummies) - to decide when building the dataset.

**MP-A3 amendment (30 Oct 2026, user).** [decided] The instrument sample and the VAR-dynamics sample need not coincide (as in Gertler-Karadi, from memory, not checked): the reduced-form VAR can be estimated on the **long sample 1973-01..2026-09** (2020 dummied) while the instrument identifies the impact vector over its own window (1994-). So the proxy-SVARs run in **two sample cases**, both reported:
(S1) short: VAR and instrument both 1994-2026; (S2) long: VAR 1973-2026, instrument identification from 1994. Cholesky runs on both windows (long and matched). The headline comparison "does the index make responses similar across samples" is S1 vs S2 vs Cholesky, with and without the index.
Assumption in S2, to be tested and reported: the impact responses (the residual covariance structure of the four variables) are stable between 1973-93 and 1994-; diagnostic = compare residual covariances before and after 1994 (and note the 1979-82 operating regime).

**MP-A4 (30 Oct 2026). Index cases.** [decided, exploratory] Run all three index cases, **nominal, real and r*-gap**, with the **r*-gap (real, relative to r*) case as the main one**. We are in exploratory mode: choices may be revisited, so every run is labelled with its case, sample (S1/S2/Cholesky window), instrument and policy-variable setup.

**MP-A5 (30 Oct 2026). Inflation variable.** [decided, exploratory] Core PCE **monthly rate, annualized** (one-month log change of the core PCE price index x 1200); no gap, no target subtraction. It is noisy, so the details are open: whether to use the raw monthly rate or a 3-month average (a noisy variable lowers the signal in the inflation equation),
and how to treat the 2020 months and the 2021-22 spike. Headline PCE not run unless asked. To settle when building the dataset; will be reported as a robustness item.

**MP-A6 (30 Oct 2026). Comparators.** [decided, exploratory] Order of runs: **market index first**, then **real GS** (also a level), then **FCI-G** last, entering as its flow form (it is built from past changes, so it is not a level). Same four-variable system and the same schemes at each stage; like-for-like cases (nominal GS with nominal market, real with real, r* with r*).

## Status of decisions (exploratory; revisit freely)
| ID | Decision | Status |
|---|---|---|
| MP-A1 | Funds rate in VAR, shock scaled on the market index; 2-year yield as robustness | exploratory |
| MP-A2 | NS from path_fci; BS = own purge now, published series later | exploratory |
| MP-A3 | Proxy-SVAR samples S1 (1994-2026) and S2 (VAR 1973-2026, instrument from 1994); Cholesky long and matched; 2020 dummied | exploratory |
| MP-A4 | Nominal, real, r*-gap index; r*-gap main | exploratory |
| MP-A5 | Inflation = core PCE monthly rate, annualized | exploratory |
| MP-A6 | Comparators: market index first, then GS, then FCI-G (flow form) | exploratory |

All six questions answered (30 Oct 2026). Next: build the dataset and the Cholesky baseline, then the proxy-SVARs; see the plan below.

## Build plan (proposal, 30 Oct 2026; nothing built until approved)
Code goes in this folder; inputs come from `fci_note/replication/` (data snapshot, index series `output/indexes_{nominal,real,rstar}.csv`) and the USMPD events. Each step ends with a log and a short note here.
1. **Dataset** (`01_data.py`): monthly 1973-01..2026-09 with unemployment gap (as in the existing VAR), core PCE monthly annualized (raw and 3-month average), funds rate, the market index (three cases), GS (real), FCI-G flow; monthly NS instrument (sum of event-window NS factor, from `path_fci`) and the own-purge BS instrument; 2020 dummies. Checks: ranges, sample start dates, instrument months.
2. **Cholesky baseline** (`02_cholesky.py`): four-variable VAR, the market index ordered before and after the funds rate, 12 lags (4 as check), with and without the index; long and matched windows; IRFs of unemployment and inflation to a unit shock scaled on the index, with bootstrap bands.
3. **Instruments** (`03_instruments.py`): NS and own-purge BS series; first stage of each on the funds rate and on the index residual (the BS first stage on the index is the non-circular test); the information-effect diagnostics (sign of the index response to raw vs purged).
4. **Proxy-SVARs** (`04_proxy.py`): S1 and S2 samples, with and without the index; IRFs against Cholesky; residual-covariance stability check across 1994 for S2.
5. **Comparison table**: robustness to identification, size, subsample, information effect (hypotheses above), by index case (nominal, real, r*-gap) and policy-variable setup (funds rate main; 2-year yield robustness).
6. Then GS, then FCI-G (MP-A6).
