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

**MP-A7 (30 Oct 2026). Details set at the start of step 1.** [decided, exploratory] (i) Inflation: the **raw monthly** annualized core PCE rate (no 3-month average); (ii) **enough lags**: the lag length is chosen from the data in step 2 (information criteria plus residual autocorrelation, not fixed at 12), with a long-lag check, because a noisy monthly inflation series needs more lags;
(iii) **Cholesky order: unemployment, inflation, funds rate, market index**, so the funds rate comes before the index and the index responds to the policy shock contemporaneously (the policy rate does not respond to the index within the month; the Caldara-Herbst concern about that restriction is reported, with the reverse order as a check).

## Status of decisions (exploratory; revisit freely)
| ID | Decision | Status |
|---|---|---|
| MP-A1 | Funds rate in VAR, shock scaled on the market index; 2-year yield as robustness | exploratory |
| MP-A2 | NS from path_fci; BS = own purge now, published series later | exploratory |
| MP-A3 | Proxy-SVAR samples S1 (1994-2026) and S2 (VAR 1973-2026, instrument from 1994); Cholesky long and matched; 2020 dummied | exploratory |
| MP-A4 | Nominal, real, r*-gap index; r*-gap main | exploratory |
| MP-A5 | Inflation = core PCE monthly rate, annualized | exploratory |
| MP-A7 | Raw monthly inflation; lags chosen from the data; Cholesky order u, inflation, funds rate, index | exploratory |
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

## Step 1 results (30 Oct 2026): dataset built (`01_data.py`, log `01_data.log`, output `data/mp_monthly.csv`)
645 months, 1973-01..2026-09, 22 columns: unemployment gap, raw monthly annualized core PCE (`pi_core`), funds rate (`ffr`, plus `ffr_nominal/real/rstar` per index case), 2-year yield (`gs2`, from 1976-06), market index, GS, FCI-G (1-year), market forward impetus per case,
monthly NS sum, event counts, 2020 flag. Inputs retrieved from FRED and saved in `data/`: PCEPILFE, GS2, PAYEMS, DTB3, DCOILWTICO (the last three are for the Bauer-Swanson-style purge in step 3). Events: 253 (as in the note); months with an event 1994-2026: 247 of 393 (the 2020 count is 6, since March-April 2020 events are dropped).
Core PCE monthly annualized: mean 3.3, sd 2.4, range -6.8 to 12.3 (noisy, as expected for the raw monthly rate).

**Finding that affects MP-A1 (correction of something I said).** In MP-A1 I wrote that the index's first stage on the NS instrument is "strong by construction". That holds in the event window, where the weights make a unit NS move the index by 1, but **not in monthly data**.
Rough monthly correlations of the NS sum with changes in each variable, 1994-2026 (n = 393, before any VAR controls; implied F = r^2 (n-2) / (1 - r^2)):
| Variable (monthly change) | same month | next month |
|---|---|---|
| market index (r*-gap) | r 0.03 (F about 0.3) | r 0.11 (F about 4.8) |
| funds rate | r 0.21 (F about 18) | r 0.18 (F about 13) |
| 2-year yield | r 0.22 (F about 20) | r 0.10 (F about 4) |
Why: the index's monthly change has sd 0.25 against an NS monthly sd of 0.045, so the event-window signal is small next to all other news in a monthly average; the index is a monthly average, so a mid-month surprise is spread over two months' changes.
Consequence: with the shock **scaled on the index**, the first stage is weak and the scaling unstable; the **funds rate and the 2-year yield have first stages around F 18-20**. This is the reverse of the ranking I assumed in MP-A1. Cholesky is unaffected (no instrument).
Options for the user: keep the index scaling but build a better-aligned monthly index (month-end values, or the event-window index change as the instrument's own scaling); switch the main scaling to the funds rate (2-year yield as the check); or report both and let the first stages decide. **Open: MP-Q7 below.**
Also flagged: (a) the 'policy variable' version per index case (nominal funds rate, real, or real gap to r*) is not yet decided, MP-Q8; (b) the purge inputs and the BS purge itself are step 3, not step 1.

**MP-Q7 [answered, see MP-A8]. Scaling of the monetary policy shock, given the monthly first stage.** **MP-Q8 [answered, see MP-A9].** Which funds-rate version enters the VAR for each index case: nominal in all cases, or matched to the case (nominal / real / real gap to r*)?

**MP-A8 (30 Oct 2026). Scaling.** [decided, exploratory] Report **both** scalings (funds rate and market index) in the proxy-SVARs and let the real first stages (step 3, with VAR controls) decide; flag the index scaling's weak monthly first stage in every table. **Cholesky first** (step 2), which needs no instrument.
**MP-A9 (30 Oct 2026). Funds rate version.** [decided, exploratory] The **nominal funds rate** in all index cases, so only the index changes across cases (column `ffr` in `data/mp_monthly.csv`).

## Step 2 results (30 Oct 2026): Cholesky baseline (`02a_lags.py`, `02_cholesky.py`, `02c_report.py`; logs `02*.log`; `irf_cholesky.csv`, `irf_cholesky_summary.csv`, figures `cholesky_*.png`)
Setup: u gap, raw monthly annualized core PCE, nominal funds rate, market index (order as listed, MP-A7); 2020 monthly dummies; 500-draw residual bootstrap. Shock = funds-rate innovation scaled to +1 pp on impact. Exploratory.

**Lags (my choice, change freely).** AIC picks 14 (long) and 9 (matched); BIC 2-3. A residual-autocorrelation (portmanteau) test rejects at every lag length up to 24, so more lags do not fix it: the cause is likely outliers and changing volatility (1970s-80s, ZLB, 2020-22), not too few lags.
Main case: **12 lags in both windows** (inside the AIC range, same as the note's VAR, keeps the windows comparable); 6 and 24 lags reported as checks.

**Findings (r*-gap index, 12 lags, per +1 pp funds-rate innovation; unemployment gap in pp, 95% bootstrap band).**
| Window | without index | with index |
|---|---|---|
| long 1973-2026 | h12 +0.16 (+0.01, +0.33); h24 +0.21 | h12 +0.19 (+0.01, +0.34); h24 +0.25 (+0.06, +0.42); h36 +0.27 |
| matched 1994-2026 | h12 -0.87 (-1.38, -0.32); h24 -0.97 | h12 -1.08 (-1.65, -0.39); h24 -1.14 (-1.90, +0.07) |
1. **Long window: conventional sign, small** (unemployment rises, peak about +0.3 after about 3 years). **Matched window: wrong sign and large** (unemployment falls about 1 pp), band excludes zero through about 18 months. Both with and without the index.
2. **The index does not make the responses similar across windows under Cholesky.** Mean |long - matched| over 0-36 months: 1.04 with the index (r*-gap; nominal 1.09, real 1.01) vs 0.85 without. Adding the index changes the response little within a window: mean |with - without| 0.04 (long), 0.15 (matched).
3. **The "shock" is not the same object in the two windows.** One-sd funds-rate innovation: 0.40 pp (long) vs 0.12 pp (matched, which contains 2009-15 and 2020-21 at the ZLB). Per one-sd shock the unemployment response is +0.07 (long) vs -0.12 (matched) at 12 months, so the +1 pp scaling inflates the matched window about 8 times; the wrong sign remains.
   The funds rate keeps rising after the shock in the matched window (+3.3 pp at 12 months vs +0.66 long): the innovation looks like the start of a hiking cycle that the Fed is executing in response to information about the economy. This is a hypothesis consistent with an information effect, not a test.
4. **The index after a funds-rate innovation:** long window small and positive on impact (+0.10 in all cases; r*-gap band includes zero); matched window negative (r*-gap -0.30 on impact, -1.44 at 12 months, band excludes zero): conditions loosen after a funds-rate surprise, again the opposite of a monetary tightening.
5. **Checks:** 6 and 24 lags and the reverse order (index before the funds rate; index impact is then zero by construction) leave the picture unchanged: long window small positive, matched window negative (-0.7 to -1.4 at 12 months). Price level: no price-level decline in either window (cumulative +0.1 to +0.2%, wide bands): a price puzzle typical of recursive funds-rate identification.
6. nominal, real and r*-gap index cases differ little under Cholesky (long u h12 +0.15, +0.15, +0.19; matched -1.14, -1.05, -1.08).

**What this means for the project question (provisional).** Cholesky on a short window reproduces the wrong-sign problem (as the NS-based LPs did), so any gain from the index has to show up in the identified (proxy-SVAR) responses; the Cholesky benchmark says adding the index alone does not rescue them.
**MP-Q9 answered: ex-ZLB check run (below), then step 3.**

## Step 2d results (30 Oct 2026): ex-ZLB check (`02d_exzlb.py`, `02d_exzlb.log`, `irf_exzlb.csv`, `cholesky_exzlb_u.png`)
Unemployment gap per +1 pp funds-rate innovation (r*-gap, 12 lags, 95% band); sd = one-sd innovation.
| Window | sd (pp) | u at 12m without index | with index | funds rate at 12m |
|---|---|---|---|---|
| 1973-2008m11 (pre-ZLB, long) | 0.48 | +0.11 (-0.01, +0.23) | +0.08 (-0.07, +0.23) | +0.25 / +0.36 |
| 1994-2008m11 (pre-ZLB, matched) | 0.14 | -0.85 (-1.24, -0.26) | -0.80 (-1.35, -0.11) | +2.7 |
| 1994-2019 (pre-COVID) | 0.12 | -1.07 (-1.56, -0.41) | -1.13 (-1.69, -0.41) | +3.4 |
| 1994-2026, ZLB months dummied | 0.13 | -0.63 (-0.96, -0.25) | -0.81 (-1.20, -0.30) | +2.7 / +3.1 |
**The wrong sign does not come from the ZLB:** it is already there on 1994-2008m11, before any ZLB, and survives dummying the ZLB months. The break is the start of the sample (1994), not the ZLB. In every 1994- window the funds-rate innovation is small (0.12-0.15 pp vs 0.48 pp) and followed by a sustained rise of the funds rate
(+2.7 to +3.4 pp at 12 months) with the index falling: consistent with post-1994 funds-rate moves being smoothed, largely anticipated hikes that respond to information about the economy. Hypothesis, not tested. The index again changes the response little.

## Step 3 results (30 Oct 2026): instruments and first stages (`03_instruments.py`, `03_instruments.log`, `data/mp_instruments.csv`)
**Bauer-Swanson-style purge (own, MP-A2).** Event-level regression of NS on pre-meeting information (253 events): R2 0.11 (joint p 0.008); only the 3-month stock change matters (+0.0021, t 3.5) and the curve-slope change weakly (t -1.9); payrolls and oil are not significant.
**The purged series is almost the same as NS: correlation 0.94 at the event level, 0.93 monthly.** So NS vs BS will differ little with this purge; a richer purge (the published Bauer-Swanson controls incl. payroll surprises and Treasury skewness) would be needed to separate them. This is where the published series matters.
**First stages (VAR residual on the monthly instrument, robust t; F = t^2), 12 lags.**
| Residual of | S1 NS / BS | S2 NS / BS |
|---|---|---|
| funds rate | F 4.7 / 4.0 (nominal index system 6.5 / 5.3) | F 0.3 / 0.3 |
| index, r*-gap | F 1.4 / 1.2 | F 1.0 / 2.5 |
| index, nominal | F 0.3 / 0.1 | F 0.5 / 1.1 |
| index, real | F 0.3 / 0.3 | F 0.4 / 1.3 |
| unemployment gap, core PCE | F below 1 | F below 1 |
(2-year yield as the policy variable: see the log, last two tables.) Signs are right: a hawkish instrument raises the funds rate and the index; the unemployment and inflation residuals are unrelated to it (as exogeneity requires).
**But the instruments are weak.** Conditional on a 12-lag, four-variable VAR the F-statistics are 0.1 to 6.5 (below the usual 10), and weakest for the index and for S2 (long-VAR residuals in the instrument window). The raw monthly correlation with funds-rate changes (F about 18) falls to about 5 once the VAR removes the predictable part. This matches the earlier LP-IV (F 6-12).
Consequence: proxy-SVAR impulse responses (step 4) will be imprecise and unstable under standard inference; weak-instrument-robust (Anderson-Rubin) bands are needed, and the choice of scaling variable (funds rate, 2-year, index) matters even more.

**MP-Q10 [open, for the user].** How to handle the weak first stage? (a) Proceed to step 4 and report Anderson-Rubin bands honestly, accepting wide bands; (b) first try to strengthen the instrument (accumulate the instrument over two or three months, use the lagged instrument, use event-window changes of the policy variable instead of monthly residuals), then step 4; (c) supply the published Bauer-Swanson series (and possibly the NS series as published) to replace my purge. Combinations are possible. My suggestion: (c) if you have the file, otherwise (a) with (b) as a variant.
**Optional input from the user:** the published Bauer-Swanson orthogonalized surprise series (a file or its location). Not required; nothing else is needed. FRED data are downloaded without a key (the CSV endpoint works); no credentials were found in the repo or environment, and none are needed.

## Step 3b-3c results (30 Oct 2026): does the 2-year yield, month-end data or a different instrument fix the weak first stage? (`03b_monthend.py`, `03c_alt_instruments.py`, logs)
User question: does the weak first stage mean the Gertler-Karadi approach (a short-yield policy indicator, here the 2-year) is needed?
**Policy indicator.** First stage of NS on the VAR residual (r*-gap index in the system), F: S1 funds rate 4.7, 2-year 3.5; S2 funds rate 0.3, 2-year 0.7. Month-end instead of monthly-average values: S1 funds rate 4.8, 2-year 3.4; S2 2.3 and 1.4. **Using the 2-year yield, averaged or month-end, does not raise F** (all between 0.3 and 4.8).
The raw correlation of NS with the monthly change in the 2-year (r 0.22, F about 20) falls to F about 3.5 once the VAR removes the predictable part: the surprise explains little of the unpredictable monthly movement.
**Other USMPD instruments (monthly sums, same events), first-stage F:**
| Instrument | S1 funds rate | S1 2-year | S1 index | S2 funds rate | S2 2-year | S2 index |
|---|---|---|---|---|---|---|
| NS | 4.7 | 3.5 | 1.4 | 0.3 | 0.7 | 1.0 |
| MP1 (current meeting) | **9.3** | 1.4 | 0.1 | **7.9** | 0.1 | 0.2 |
| MP2 (next meeting) | 7.2 | 0.6 | 0.4 | 1.8 | 0.0 | 0.0 |
| ED4 (about 9-12 months ahead) | 2.0 | **5.6** | 1.4 | 0.0 | 1.7 | 1.6 |
| path (ED4 net of MP1) | 0.1 | 3.5 | 2.8 | 0.7 | 1.3 | 3.8 |
| 2-year event-window change | 2.5 | 3.3 | 3.0 | 0.0 | 0.7 | 2.8 |
**Reading.** (1) Moving to the 2-year does not strengthen identification here; the best single first stage is the **funds rate with the current-meeting surprise MP1 (F about 8-9, near the usual 10)**, a different shock (target, not path/news) from NS. (2) For the 2-year, the best instrument is ED4 (F 5.6 in S1), only slightly above NS (3.5).
(3) No instrument gets F near 10 for the index; the best (path, own 2-year change) reach about 3-4. (4) S2 (long VAR) is weaker throughout. So weak-instrument-robust inference is needed whichever indicator is used. Whether to use the 2-year as the main policy variable is a choice of units and economic content (it matches the index's units), not something the first stage supports or rules out.
**MP-Q11 [answered, see MP-A10].** You said you prefer the 2-year yield: flip MP-A1 so the 2-year is the main policy variable (funds rate as robustness)? The evidence neither requires nor forbids it. If yes, the main instrument for the 2-year would be NS and ED4 (reported side by side); for the funds-rate version, NS and MP1.

**MP-A10 (30 Oct 2026). Policy variable flipped.** [decided, exploratory] The **2-year Treasury yield is the main policy variable** (monthly average `gs2`, FRED GS2, from 1976-06); the funds rate becomes the robustness case. Scaling of the shock: on the 2-year (units match the index) with the index-scaled version reported alongside (MP-A8).
Instruments: for the 2-year, NS and ED4 side by side; for the funds-rate robustness, NS and MP1. Long Cholesky window for the 2-year therefore starts 1976-06, not 1973-01. Supersedes MP-A1's main case; MP-A1's reasoning on scaling stays on record.

## Step 2e (Cholesky with the 2-year yield, MP-A10) (`02e_cholesky_gs2.py`, `02e_cholesky_gs2.log`, `irf_cholesky_gs2.csv`, `cholesky_gs2_u.png`)
Unemployment gap per +1 pp 2-year-yield innovation, 12 lags, r*-gap index, 95% bootstrap band (200 draws); sd = one-sd innovation.
| Window | sd (pp) | h12 without index | h12 with index |
|---|---|---|---|
| long 1976-06..2026 | 0.31 | +0.06 (-0.13, +0.26) | +0.16 (-0.04, +0.33) |
| matched 1994-2026 | 0.18 | -0.42 (-0.77, -0.05) | -0.39 (-0.78, -0.02) |
| pre-ZLB long 1976-2008m11 | 0.36 | +0.08 (-0.13, +0.27) | +0.18 (-0.01, +0.34) |
| pre-ZLB matched 1994-2008m11 | 0.21 | -0.44 (-0.70, -0.05) | -0.32 (-0.63, +0.07) |
| pre-COVID 1994-2019 | 0.18 | -0.50 (-0.83, -0.14) | -0.38 (-0.68, -0.02) |
Same pattern as with the funds rate, smaller in size (2-year innovations are larger, so a +1 pp scaling inflates less): long window small and positive, every 1994- window negative. The index leaves the picture much as it is; it rises on impact in the long window (+0.49) and less in the matched (+0.24).

## Step 4 / 4b (proxy-SVAR with the weak instruments; why others may not see weak instruments) (`04_proxy.py`, `04b_why_weak.py`, `mpcommon.py`, logs, `irf_proxy.csv`, `proxy_u.png`; `data/USMPD.xlsx` added for FF4)
**Proxy-SVAR, unemployment response at 12 months per +1 pp policy rise, with the 95% Anderson-Rubin (AR) set (conditional on the VAR coefficients), 12 lags:**
| Policy / instrument | S1 (1994-2026) F, h12, AR set | S2 (long VAR) F, h12, AR set |
|---|---|---|
| 2-year / NS | 3.5, +0.08, unbounded | 0.7, +0.23, unbounded |
| 2-year / ED4 | 5.6, -0.01, (-1.56, +3.11) | 1.7, +0.19, unbounded |
| 2-year / FF4 (Gertler-Karadi style) | 0.4, +1.52, unbounded | 0.1, -1.95, unbounded |
| funds rate / NS | 4.7, -0.49, unbounded | 0.3, +0.15, unbounded |
| funds rate / MP1 | 9.3, -1.26, (-2.06, +0.55) | 7.9, -0.29, (-2.56, +9.36) |
With 2 lags: 2-year / NS S1 F 5.9, -0.04 (-1.03, +1.08); 2-year / ED4 S1 F 9.3, -0.07 (-0.96, +0.58); funds rate / MP1 S1 F 10.6, -0.69 (-1.26, +0.59).
**Reading.** With the weak instruments the sets are unbounded or very wide, so the data neither confirm nor reject any sign. The 2-year point estimates are close to zero (not the large negative Cholesky value), the funds rate / MP1 point estimate is negative. **The index scaling is unbounded everywhere** (index first stage weak).
**Why others may report usable first stages from similar data (04b; robust F [homoskedastic F], 2-year yield unless stated).**
1. **Level of aggregation.** At the event level (253 events) the 2-year window change on NS has F 332, by construction (NS is built from yield surprises in the same window); monthly raw correlation with the monthly 2-year change, F 20; on the VAR residual, F 3.5. A reported 'first stage' can be any of these.
2. **Which F.** Homoskedastic F is about 1.5 to 2 times the robust F (NS 3.5 vs 6.4; ED4 5.6 vs 7.6; funds rate / MP1 9.3 vs 34.3).
3. **VAR lags.** 12 lags: NS 3.5, ED4 5.6; 6 lags: 4.1, 6.4; 2 lags: 5.9 [10.1], 9.3 [12.4].
4. **VAR size.** 2-year with only unemployment: NS 6.1 [11.9], ED4 8.9 [12.5]; with core PCE: 6.4 [11.2], 9.4 [12.0]; **adding the index drops it to 3.5 [6.4], 5.6 [7.6].** The index costs first-stage strength.
5. **Policy variable.** The 1-year (Gertler-Karadi's) gives NS 7.1 [12.4] and ED4 7.7 [10.6], about twice the 2-year's 3.5 and 5.6.
6. **Instrument.** FF4 (Gertler-Karadi's own futures surprise) is the weakest here for the 2-year (0.4 [0.7]); 2.4 [5.1] for the 1-year; 5.7 [9.8] for the funds rate. MP1 is the strongest for the funds rate (9.3; 12.2 on 1994-2007).
7. **Sample.** The 2-year first stage is no better before 2008 (0.1 to 1.3); funds rate / MP1 is (12.2 [26.1] on 1994-2007). So the post-2008 sample is not the cause for the funds rate, and the 2-year is simply poorly explained.
8. **Timing** (splitting a surprise between the event month and the next in proportion to days left, as a monthly average suggests) did not help (NS 3.5 to 2.9).
**What is and is not established.** With the choices closest to Gertler-Karadi (1-year indicator, small system, few lags, homoskedastic F) the first stage is about 10 to 12; with this project's choices (2-year, four variables incl. the index, 12 lags, robust F) it is 3 to 6. I could not find Gertler-Karadi's own reported first-stage F or how they compute it;
the literature does note that the proxy-on-VAR-error F depends on the specification and anchor variable (Lunsford 2015; [Colombo 2025](https://colombodaniele.github.io//files/COLOMBO_2025_Identification_or_propagation.pdf) on anchor dependence), and Känzig (2021) reports regular F 22.7 and robust F 10.6 for an oil proxy (a different application). So 'the literature has strong instruments' is not verified here; 'the reported F depends heavily on these choices' is.
**Open (user): MP-Q12.** Which first-stage convention to adopt for the project (robust F with 12 lags as now, or a smaller system / fewer lags / 1-year indicator for comparison with the literature), and whether the index should stay in the system when it lowers first-stage strength.

## Literature read: what the papers say about first-stage strength and how it relates to us (30 Oct 2026; `04c_gk_replication.py`, `04c_gk_replication.log`)
Texts read in full-text form (not summaries): Gertler-Karadi 2015 ([PDF](https://peterkaradi.github.io/website/Published/GertlerKaradiSurprise.pdf)), Lunsford 2015 ([PDF](https://webarchive.ucr.edu/economics.ucr.edu/wp-content/uploads/2019/10/Lunsford-paper-for-4-13-16-seminar.pdf)), Colombo 2025 ([PDF](https://colombodaniele.github.io//files/COLOMBO_2025_Identification_or_propagation.pdf)). The replication code of Gertler-Karadi sits behind an ICPSR login and was not read, so their lag length is unknown to me.

**Gertler-Karadi (2015) - what they say.**
1. The first-stage numbers I could not find earlier are in the paper: with the 4-variable VAR (log IP, log CPI, **1-year rate**, excess bond premium; monthly, 1979:07-2012:06 for the lag coefficients, **instruments from 1991:01**) and instrument **FF4**, the first-stage F is **21.5 (robust 17.5), R2 about 0.078** (Table 3 column 2: 17.50; T = 258).
2. **They found the 2-year weak in monthly VARs and said so:** "For the two year rate, none of the instrument combinations meets the threshold" (Table 3, 2-year columns: F 4.5, 5.2, 0.9, 3.8, 5.2). That is why the baseline is the **1-year rate with FF4** ("a setting where there is unlikely to be a weak instruments problem"); the 2-year, their "conceptually preferred" indicator, is a robustness exercise "despite the potential weak instruments problem", and they report similar responses.
3. They choose the indicator/instrument pair after looking at the first stage (Table 3 compares instrument sets); they use the Stock-Wright-Yogo threshold of 10.
4. Monthly construction (their footnote 11): surprises cumulated over the previous 31 days for each day of the month, then averaged over the days of the month, because the dependent variable is a monthly average (equivalent to the timing split I tested in 04b); the VAR is estimated over the longer sample and the instrument identifies only over its own window (as in my S2 structure).
5. In a later specification with Greenbook controls (sample limited) they say they "cannot confidently rule out" weak instruments (F 2.3 to 4.2 in the appendix figures).

**Lunsford (2015).** The proxy literature's F is not the single-equation first stage but the F from projecting the **proxy on all the VAR errors**; critical values for 10% asymptotic bias at 5% are about **7-9** for conventional VAR sizes. He notes weak proxies are common: only 5 of the 18 proxies in Montiel Olea-Stock-Watson/Stock-Watson (2012) exceed 7.81.
**Colombo (2025).** Relevance is usually tested on one anchor equation's residual (as GK do); this is anchor-dependent. A shock-based F (regress the recovered shock index on the instrument) is weakly larger and anchor-free. For GK's FF4 on the full 1979M7-2012M6 sample he finds the anchor-based F **fails 10 (4-variable VAR: 9.02)** while the shock-based F is **15.48** (trivariate: 10.27 and 11.13). The gain arises when the instrument loads on several variables (the 1-year rate and the excess bond premium).

**Our numbers on the same conventions (homoskedastic F, [robust]); Lunsford F; Colombo shock-based F, [robust].**
| Case | anchor F | Lunsford F | Colombo F |
|---|---|---|---|
| Approx. replication of GK's first stage (USMPD FF4, 1-year, 12 lags, 1994-02..2012-06, T = 221) | 6.6 [5.5] | 3.1 | 12.6 [9.6] |
| same, 6 lags | 10.3 [7.2] | 3.9 | 15.9 [9.1] |
| same, 2-year / FF4 (12 lags) | 1.2 [1.2] | 1.8 | 7.2 [4.7] |
| Project: 2-year / NS, S1 | 6.4 [3.5] | 2.1 | 8.5 [5.3] |
| Project: 2-year / ED4, S1 | 7.6 [5.6] | 2.4 | 9.6 [7.3] |
| Project: funds rate / MP1, S1 | 34.3 [9.3] | 9.1 | 36.7 [10.4] |
| Project: 2-year / NS, no index, S1 | 11.2 [6.4] | 3.9 | 11.9 [7.1] |
| Project: any instrument, S2 (long VAR) | 0.1 to 8.8 | 0.5 to 3.4 | 1.9 to 10.3 |
**Relating the papers to us.**
- **The 2-year problem is the same one Gertler-Karadi documented**, on their data (F 0.9-5.2); our 2-year numbers (0.8-7.6 across conventions) are in that range. This is not a feature of my construction.
- **The strong first stages in the literature come from a specific specification** chosen partly for strength: 1-year rate, FF4, instrument window from 1991, anchor F with their VAR. On our data and the closest approximation (1994-2012, 12 lags) the same pair gives anchor F 6.6 (robust 5.5), and 10.3 with 6 lags; an independent re-estimation (Colombo) of their own VAR on the full sample gives 9.02. So even GK's instrument is borderline outside its original window and conventions.
  Differences I cannot close from here: 1991-93 are missing in USMPD (GK's instruments start 1991-01); GK's lag length; vintage of the data.
- **By Lunsford's stricter test the weakness is widespread**, including the GK specification on our data (3-4 against critical values of 7-9); only funds rate / MP1 on S1 (9.1) clears it. This matches his observation that weak proxies are the norm.
- **Colombo's shock-based F is higher** and brings several S1 cases to 8.5-14 (funds rate / NS 13.9), but not S2. The index adds little loading, so the gain is modest; dropping the index raises the anchor F (11.2 vs 6.4).
- The monthly instrument sum with the timing split (GK's method) did not raise our F (04b).
**What this changes.** (1) My earlier statement that GK's reported F could not be found is replaced by the above. (2) The project's 2-year main choice (MP-A10) is the choice GK explicitly avoided for baseline because of weak instruments; it is defensible as in this project's units, but results should come with weak-instrument-robust sets (as in step 4) and a GK-style baseline (1-year indicator with FF4/MP1 instruments) for comparison. (3) Whether an F near 5-9 is acceptable depends on the convention: report anchor, Lunsford and Colombo F, with the thresholds.
**MP-Q12 [open, restated].** Report side by side (a) the 2-year main with robust sets and (b) a GK-style baseline (1-year, FF4 or MP1), and the three F statistics for each? The 1-year yield and FF4 are in the data; the 1-year index units would need a conversion from the 2-year.

## Bauer and Swanson (2023): what they do, from the paper (NBER WP 29939, [PDF](https://www.nber.org/system/files/working_papers/w29939/w29939.pdf)), and how it relates to us
**Problem they address.** (a) Exogeneity: high-frequency surprises are predictable from public data (R2 10-40% in earlier work; about 16% in their baseline), the "Fed response to news" channel, which biases VAR/LP estimates toward zero or reverses the sign (price and activity puzzles). (b) Relevance: Ramey (2016) finds effects poorly estimated in samples after about 1984 because the surprises are small and uninformative.
**What they do.**
1. **Exogeneity: orthogonalize.** Regress each announcement's surprise on six pre-announcement variables and keep the residual: nonfarm payroll *surprise* (Money Market Services survey), 12-month employment growth, S&P 500 3-month change, 3-month change in the yield-curve slope, 3-month change in commodity prices (Bloomberg), and Treasury skewness (Bauer-Chernov). Event-study (asset price) estimates are unchanged by this; macro estimates change a lot. They argue public-data orthogonalization is enough and that the Fed "information effect" of Nakamura-Steinsson and Miranda-Agrippino-Ricco is not needed (Greenbook and Blue Chip controls give almost identical results).
2. **Relevance: more events.** They add **Fed Chair speeches, testimony and press conferences** to FOMC announcements (Swanson-Jayawickrema 2021 show speeches matter at least as much), which "roughly doubles the explanatory power" of the instrument, and extend events back to **1988** (322 announcements 1988-2019 for FOMC alone).
3. **Instrument.** First principal component of the ED1-ED4 surprises (path over the next four quarters); monthly instrument = the **sum** of the month's announcement surprises (no 30-day moving average; they criticize Gertler-Karadi's moving average because it adds serial correlation, per Ramey).
4. **VAR.** log IP, log CPI, excess bond premium, and the **2-year Treasury yield, end-of-month, ordered last**; 12 lags; reduced form on **1973:1-2020:2**, impact vector from the IV regression on the **instrument window 1988-2019** (separate samples, as Stock-Watson). A 25 bp shock. They say Gertler-Karadi used the 1-year "only because they were unable to get a sufficiently large F-statistic"; with their instrument set the 2-year is feasible.
5. **First stage (their own numbers, anchor = 2-year residual on the instrument).** FOMC announcements only: **7.69 raw, 2.44 orthogonalized**; with Chair speeches: **15.83 raw, 10.23 orthogonalized**. Variants (FOMC only, raw): core CPI 7.38; **1-year month-average 13.58**; adding unemployment 7.73. They state the orthogonalization "does reduce the relevance of our instrument, to the point where weakness of the instrument may be a serious concern", and that their FOMC-only LP-IV results "should be treated very cautiously".
6. **Results.** With the expanded, orthogonalized instrument: no price or activity puzzle, responses up to four times larger than with raw surprises, more significant.
**How it relates to us.**
- **Our first stages match their FOMC-only numbers.** Their FOMC-only orthogonalized F is 2.44 (ours 2.1-6.4 depending on convention); their raw FOMC-only F is 7.69 (ours 5.6-7.6). Neither is surprising: the weakness is in the FOMC-only instrument, in their data too.
- **The fix in the literature is more events, not a different yield.** Chair speeches/testimony and the 1988-93 events are what lift their F to 10-16. We have neither: USMPD has statement windows (279 events, 1994 on, press-conference windows already inside), separate Minutes releases (206 events, 2001 on) and no speeches. **Adding the Minutes events did not help** (2-year / ED4 F 5.6 to 4.2 on 1994-; FF4 0.4 to 0.4; their surprises are small, ED4 sd 0.024 vs 0.065).
- **Our purge is weaker than theirs.** Four predictors vs six; no payroll surprise, no Treasury skewness; stocks drive it (R2 0.11 vs about 0.16); our purged instrument correlates 0.94 with NS, so in their terms it removes little of the predictability. Their payroll surprise needs survey data we do not have.
- **Ramey's (2016) point is the pattern we see:** the funds-rate innovations after 1994 are small and followed by sustained hikes; Cholesky gives the wrong sign in every 1994- window. Bauer-Swanson find the same attenuation/reversal with raw post-1984 surprises and correct it by orthogonalizing.
- **They use the 2-year, our preferred indicator, with end-of-month values, 12 lags, and the same separate-sample structure as our S2.** Our end-of-month test (03b) did not change F.
- **Their VAR differs from ours:** IP, CPI and excess bond premium (a credit variable) vs our unemployment gap, core inflation and the market index; they report no result on a composite index.
**What would be needed to follow them.** (1) The Fed Chair speech/testimony surprises and the 1988-93 FOMC events (Swanson-Jayawickrema/Bauer-Swanson data; I have not found where they are posted); (2) the payroll-surprise and skewness predictors for a six-variable purge. **User input welcome:** whether you have access to these series. Without them, expect first stages in the 2-10 range and wide robust sets, as in step 4.
