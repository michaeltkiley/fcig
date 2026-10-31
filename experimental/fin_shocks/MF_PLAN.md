# Window-identified mixed-frequency VAR: stage-0 result and plan

31 Oct 2026, written for the user's return. Status: **superseded by `MF_REPORT.md` (31 Oct, evening): stage 0, route A, route B and the Monte Carlo are done.** The text below is the plan as written before those runs; note the later decisions FS-A5 and FS-A6 (no credit spread in the baseline; window impact vector from the 30-minute windows). Files: `stage0_window_var.py`, `stage0_window_var.log`, `stage0_window_var.csv`; background in `MIXED_FREQUENCY_NOTES.md`; decisions in `FS_QA.md`.

## 1. The idea in one paragraph
The monetary shock is observed only in announcement windows (minutes, about eight a year). In a window the shock is the only news, so the financial variables' moves in the window reveal the **impact vector** `b` (policy rate and index move; macro variables do not). Everything after the window is propagated by a VAR whose financial block is daily and whose macro block is monthly. The impulse response is `Theta_h b` (Theta = the model's moving-average matrices), with no ordering and no weak monthly first stage. Closest precedent: Faust, Swanson and Wright (2004) [abstract only], who impose futures-based funds-rate responses on a VAR.

## 2. Stage 0: what was run
A monthly VAR (12 lags, 2020 dummied) whose impact vector comes from the windows, macro entries zero. Window shock in three versions: NS (policy-news factor, 252 events), MP1 (current-meeting surprise, scaled on the funds rate), and NS purged of Greenbook forecasts (NS-GB, 205 events). Daily financial responses by local projection (close before the event to k trading days after, k = 0 to 63) for the 2-year, funds rate, 10-year, the market index (daily changes from the 10-year, CAPE and the dollar with the note's weights), equities, dollar and the Baa-10y spread. A monthly-average exposure turns the daily path into the event-month impact. Samples: long (1973- with the funds rate; 1976-06- with the 2-year, since the 2-year starts then) and USMPD-matched (1994-). Bootstrap over events and VAR residuals (80 draws).
**Pre-registered criteria** (written before running): GO if for NS and NS-GB, in at least one sample with the credit spread, the median unemployment response is positive at 12 and 24 months with the 90% interval not entirely below zero, and the VAR-implied financial paths at months 1 and 2 are within the direct daily-LP intervals. NO-GO if the interval is entirely below zero everywhere or too wide to sign.

## 3. Stage-0 results (unemployment gap, pp, per +1 pp rise in the 2-year yield on the event day; median [90% interval])
| Shock / sample | EVENT timing, 12m | EVENT, 24m | START timing, 12m | START, 24m |
|---|---|---|---|---|
| NS, long 1973- (funds rate) | +0.39 [+0.23, +0.52] | +0.25 [+0.04, +0.37] | +0.90 [+0.53, +1.20] | +0.59 [+0.10, +0.83] |
| NS, long 1976- (2-year) + Baa | +0.40 [+0.22, +0.59] | +0.29 [+0.10, +0.46] | +1.00 [+0.54, +1.44] | +0.75 [+0.27, +1.14] |
| NS, 1994- (2-year) | +0.27 [+0.05, +0.47] | +0.20 [-0.06, +0.45] | +0.67 [+0.14, +1.09] | +0.53 [-0.11, +1.00] |
| NS, 1994- (2-year) + Baa | +0.28 [+0.03, +0.48] | +0.20 [-0.05, +0.44] | +0.76 [+0.16, +1.23] | +0.58 [-0.04, +1.14] |
| NS-GB, long 1973- | +0.46 [+0.28, +0.71] | +0.30 [+0.04, +0.54] | +1.14 [+0.74, +1.63] | +0.73 [+0.11, +1.20] |
| NS-GB, long 1976- + Baa | +0.50 [+0.24, +0.81] | +0.37 [+0.09, +0.56] | +1.37 [+0.70, +2.21] | +1.00 [+0.23, +1.55] |
| NS-GB, 1994- | +0.40 [+0.19, +0.74] | +0.34 [+0.04, +0.63] | +1.19 [+0.59, +2.10] | +1.05 [+0.27, +1.80] |
| NS-GB, 1994- + Baa | +0.42 [+0.09, +0.74] | +0.34 [-0.04, +0.60] | +1.30 [+0.36, +2.20] | +1.12 [+0.08, +1.85] |
| MP1 (+1 pp funds rate), long 1973- | +0.23 [+0.09, +0.62] | +0.26 [+0.11, +0.65] | +0.55 [+0.24, +1.75] | +0.59 [+0.24, +1.69] |
Per +25 bp in the 2-year, EVENT timing: about +0.07 to +0.13 at 12 months (START: +0.17 to +0.34). For comparison, the long-sample recursive local projection of `lp_weights` E7 found +0.32 per +1 pp funds rate at 12 months (+0.08 per 25 bp).
Direct daily responses per +1 pp 2-year move on the event day (NS): 10-year +0.49; the index +0.81 on the day, +1.31 after 5 days, +1.35 after 21 days; equities -9% on the day, -15% after 21 days; dollar +0.5% on the day, +4.3% after 21 days; Baa-10y spread -0.28 on the day, +0.58 after 21 days (the spread narrows in the window and then widens).

## 4. Reading
1. **Verdict against the criteria: GO.** Criterion (i) holds for NS and NS-GB in every sample: positive medians at 12 and 24 months, intervals never entirely below zero; at 12 months the interval excludes zero in every case; at 24 months it includes zero only in two 1994- cells. Criterion (ii) holds formally (the VAR-implied medians lie inside or at the edge of the direct 90% intervals) but with a **systematic pattern**: the monthly VAR carries only about half of the policy-rate response in months 1 and 2 (NS, long + Baa: VAR 0.48 and 0.24 against direct 0.96 and 1.19), because the event month's average contains only the post-event days and a monthly VAR with an average-exposure impact cannot represent the full-month level shift that follows.
2. **Timing is not second-order, contrary to what I said in discussion.** Moving from exposure-weighted (EVENT) to first-day-of-month (START) timing raises the 12-month unemployment effect by a factor of 2 to 3. The sign is robust to this; the magnitude is not. The true answer lies between the two columns, which is exactly what a mixed-frequency model resolves. This is the case for the state-space build.
3. **The sign is conventional in all three shock versions**, including the Greenbook-purged one and the target-only MP1. This contrasts with the monthly proxy-SVAR of `mp_var_fci`, which gave a significantly wrong-signed response. A candidate explanation was that the monthly instrument is correlated with same-month macro news, contaminating the monthly impact vector's macro entries. **Tested later the same day (`followups.log`) and not supported:** the difference comes from the financial entries (index and credit spread loadings), not the macro entries. See `MF_REPORT.md`.
4. **What drives the unemployment response.** The impact vector is mostly financial (index +0.63 and the policy rate +0.43 in the event month), and the VAR's index-to-unemployment link does the rest: the response is roughly Phi(12) of the note's two-variable VAR times the index impact. So the exercise says what the note's mechanism implies once the **policy component of index moves** is pinned down from windows. It does not provide independent evidence about the financial-to-activity link, which comes from all financial variation (and so carries Stock and Watson's caveat that financial innovations include news about activity).
5. **What stage 0 cannot tell us:** the weights of the macro entries (set to zero by assumption); the effect of omitted financial variables (only the Baa-10y spread is added, and it changes little); whether the VAR's propagation of a policy-induced financial move equals its propagation of other moves (the common-dynamics assumption, tested only indirectly by the diagnostic).

## 5. The build (what to decide tomorrow)
**Frequencies (the user's): minutes (windows) -> daily (financial block) -> monthly (macro).**
- **Windows:** the shock enters only on event dates; `b` is estimated from the windows (financial entries) with macro entries zero; uncertainty carried through. Optional heteroskedasticity version (other shocks allowed in windows with smaller variance), which relaxes "only the monetary shock occurs in windows" (this is P4 combined).
- **Daily block:** 2-year, funds rate, 10-year, equities (CAPE), dollar, credit spread (Baa-10y from 1986, ICE BBB from 1997 for robustness). Daily data exist from 1976 (2-year), 1986 (Baa), 1990 (equity and dollar from the project's daily GS file). Pre-1990 daily values are treated as missing, so the long sample 1973- is possible in a state-space model (missing data are natural there) and not in a pure MIDAS regression.
- **Monthly block:** unemployment gap, core PCE (raw monthly annualised), optionally EBP and NFCI; latent daily values with a known aggregation (average for unemployment; flow for inflation).
**Two estimation routes**
- **A. Block-recursive MIDAS-VAR (cheap; build first):** a daily VAR for the financial block, monthly macro equations driven by MIDAS-weighted daily financial lags and macro lags, macro feeding back into the financial block through predetermined monthly values. No latent states; IRFs by simulation from the window impact vector. Limitation: ignores within-month macro-to-finance feedback.
- **B. State-space mixed-frequency VAR (Schorfheide-Song style; the full model):** latent daily macro, Kalman filter and Gibbs sampler, Minnesota-type priors; the window shock enters through the impact vector; the main computational cost is the daily dimension (about 6,000 days since 1990; a weekly base would be lighter but weakens the within-week zero restriction).
**Validation before using real data (important):** a Monte Carlo with a known daily DGP, sparse window shocks, aggregation to monthly, to check that route A or B recovers the true impulse responses and to measure the bias from timing misspecification; the stage-0 START and EVENT columns show the size of that bias.
**Samples:** long from 1973 (daily financial data from 1976 or 1990) and 1994- to match USMPD; 1997- with the daily ICE credit spread as robustness or if needed.
**Shock versions to carry through:** NS, MP1 and NS-GB, as in stage 0.

## 6. Stage-0 follow-ups worth doing first (about half a day)
1. Replace `b` by the **monthly proxy-SVAR impact vector** (from `mp_var_fci/04_proxy.py`) inside the same VAR to see whether the earlier wrong sign comes from the macro entries of the monthly `b` or from the financial ratios (tests the contamination hypothesis of reading 3).
2. Allow **small non-zero macro entries** (a prior around zero) to see how sensitive the sign is to the zero restriction.
3. Add **EBP and NFCI** to the VAR (with window responses from the daily Baa spread as proxy for the EBP's response) and report the sensitivity.
4. Report the **window F-statistics** next to every shock version, and the bootstrap with more draws (80 now).

## 7. How this fits P1 to P4
Everything in `PROPOSALS.md` stands. Suggested order [proposal]: (1) stage-0 follow-ups above and the route-A build, which now looks the most promising use of the index; (2) P1 (recursive financial shock, index versus credit) in parallel because it is quick; (3) route B and the Monte Carlo; (4) P2 and P3; (5) P4 only as the heteroskedasticity extension inside the mixed-frequency model. The user decides.

## 8. Questions for tomorrow
1. Route A first, or go straight to route B?
2. Is "macro entries zero in the window" the restriction you want in the baseline, with the prior-around-zero version as a robustness check?
3. Daily credit spread: Baa-10y (from 1986) in the baseline, ICE BBB from 1997 as robustness?
4. Which shock version is the baseline: NS, with NS-GB and MP1 as robustness?
5. Run P1 in parallel, or finish the mixed-frequency line first?
