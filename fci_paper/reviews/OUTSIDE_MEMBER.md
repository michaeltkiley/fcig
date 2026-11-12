# Outside committee member: synthesis (11 Nov 2026)

Read the files listed in the brief; nothing re-run. [verified] = in the files; [inference] = my judgment.

## 1. What the project is, and the question

A market index weights the 10-year yield, equity valuation and the real dollar by their responses to policy news (unit: a 2-year-yield move), with a level, a VAR flow, and a nominal -> real -> r* ladder. Note B uses it as the channel from a surprise to unemployment and prices; Note A builds it and compares it with GS, FCI-G, FRB/US and NFCI. [verified]

"Do indexes agree on a common basis?" yields "direction yes, level within about a point, the size of the sampling error". No reader acts on that. The advisors' "can the index be trusted as a channel?" serves Note B but is not an economic question.

**Proposed question: once financial conditions are in policy-rate units and measured relative to neutral, how much tighter or looser do they make the stance than the policy rate alone, and does that wedge say anything about activity?** [inference]

It is the first purpose in Hatzius et al. (2010) (an index as a Taylor-rule counterpart: the 2004-06 conundrum, the zero bound) and in Dudley (2010) (equities and the equilibrium rate). Ajello et al. supply units and the flow form; Caballero-Simsek the neutral-level idea that the r* step applies to inputs; Brave-Butters and Adrian et al. the benchmark carrying stress and the lower tail. No one has put them in one unit and one neutral reference. `stance/` already answers it: the index adds to the funds-rate gap for unemployment (adjusted R2 +0.105 to +0.119, t 5.5 to 6.2), the gap adds nothing given the index, and the 2004-06 and 2022-24 wedges are -1.29 [-1.86, -0.65] and -1.40 [-2.22, -0.39]. [verified]

## 2. Strengths

- A clean policy-equivalent unit, a like-for-like ladder, and imprecision reported (weights bootstrap, 4- versus 12-lag yardstick). [verified]
- Pre-specified follow-ups that count tests and report nulls. Worth keeping: flows, not levels, carry the rate-based indexes while NFCI levels carry theirs (sum-versus-differences removes the Granger tension); the index complements the NFCI at 6 to 12 months (joint t 3.1 to 4.3); the index adds to the funds-rate gap. [verified]
- Purge: Phi(12) 0.57 [0.22, 0.84] falls to 0.32 [0.10, 0.51] (full) and 0.19 [0.11, 0.33] (recursive), all above zero. The flow is not only activity reflected back. [verified]

## 3. Weaknesses

- **Shared inputs.** All indexes are sums of the same yield, equity valuation, dollar and, at the r* step, the same r*. Agreement in changes is partly by construction; only disagreement is informative. The range mixes units (sd ratio 1.28) and each index is demeaned on one sample (Review 2). Level correlations are inflated by the 1970s (0.94 versus 0.79 since 1990). [verified]
- **Power and shared data in the follow-ups.** One monthly series, five recessions (two out of sample), overlapping 12-month outcomes, roughly 50 independent years. `rstar_test`: 69 of 91, nothing after Holm, gains 2 to 5 percent of RMSE, concentrated in 2008-16 where nominal and r* differ mechanically at the lower bound. `levelflow`: "r* raises the flow t" (3.9, 4.3, 5.2) is untested. `rstar_basis`: about 130 statistics; the unit restriction (-1.52 on r*) is indistinguishable from no adjustment (p 0.42, 0.14) because r* barely moves at 12 months. `stance`: 1 of 9 primary tests survives Holm. Counts across indexes, steps and horizons are not independent. [verified]
- **r* is not neutral to outcomes.** Laubach-Williams uses output, inflation and unemployment and full-sample parameters; the gap uses ex-post CBO NROU. r* gains and the recursive purge are not real time, and r* uncertainty is in no interval. [inference]
- **The sample splits Note A from Note B.** Weights come from 1996+, Note A applies them from 1973 and estimates the VAR from 1973; Note B starts in 1996. `rstar_basis` finds Phi(12) of 0.65, 0.39, -0.01 for 1976-89, 1990-2007, 2009-19 (equality rejected at every step). The headline yardstick (0.65 [0.39, 0.83]) is a pre-1990 number. This is the most consequential weakness for the foundation role. [verified/inference]
- **Stance is confounded.** Equities carry the increment (gain 0.134; dollar nothing) and equities lead the cycle; a third to a half of the flow is activity. Out-of-sample RMSE falls 5 to 8 percent; the zero bound is indistinguishable. [verified]
- **Overstatements.** The range fall from 2.8 to 1.1 is mostly the 1970s (1.15 to 0.88 since 1990). NFCI is dismissed as "a different object" though it beats the market index at 24 months and for recessions (t 4.2 versus 1.3). [verified]
- **Redundancy and inconsistency with Note B.** Note B's Section 2.2 re-derives the index, the GS comparison and the ladder with figures. Note B uses the index level as a state variable; Note A finds the level has no significant independent effect (sum of lags p = 0.17) and the flow carries the content. Note B's 0.6 pp rests on a 1996+ link that Note A finds near zero in 2009-19 [inference]. The weights, and so the unit, rest on windows; Note A should say so. [inference]

## 4. Questions for the author

1. What one statement about policy should a central banker take from Note A, and what number would change it?
2. Note B's sample starts in 1996. Why should a VAR from 1973, with a response near zero in 2009-19, support the link Note B uses?
3. Is the index a level or a flow? What does a permanent level shift do to unemployment in each paper?
4. What stops the r* step importing outcome information from output and inflation? Why do Laubach-Williams and Kiley give different neutrality (+0.88 versus +0.03)?
5. With equities carrying both the stance increment and the activity content, how do you separate policy-equivalent tightening from equities anticipating a slowdown without window surprises?
6. Why are 30-minute policy responses since 1996 the right weights for persistent levels of CAPE and the dollar over 1973-95?
7. NFCI wins at long horizons and for recessions. Is the market index better at anything out of sample?

## 5. Next steps

1. **Adopt the stance question and restructure.** Order: stance and units; one ladder; the wedge against the funds-rate gap (`stance/`, 2004-06, 2022-24); why indexes differ (agreement becomes one exhibit, with the shared-input caveat and a unit-adjusted range); validity (purge, NFCI, level versus flow). NFCI, in a plain paragraph: it carries long horizons and recession risk; the market index carries a 6- to 12-month rate-channel flow.
2. **Fix the sample.** Re-estimate VAR, flows and stance on 1996-2026 (and 1990-), keep 1973 as the long-sample case, and say in the main text that the yardstick is pre-1990 and weaker after. This is the step that buttresses Note B. [inference]
3. **Include** `levelflow` (mean; tail in sample, one sentence on two recessions), `stance`, `purge` (the Phi(12) table), `nfci` (one paragraph), and the neutrality shift (nominal -2.1, real -1.4, r* LW +0.9, Kiley 0.0), shown with both r*. **Drop or shrink:** the 69-of-91 and dispersion counts, "r* raises t", activity-fitted weights (one sentence: outcomes cannot rank weights), the unit restriction (one sentence: untestable), most Section 5.5 tables.
4. **Carry r* uncertainty** (LW, Kiley, Holston) with the weights bootstrap into the stance statement for today and 2022-24. Justify the r* step by Dudley and FCI*; say outcomes give only a lean.
5. **Rewrite abstract and introduction** to the WRITING_GUIDE: question, the finding that travels (wedge, flow, purge), qualifications as facts. Correct base periods, "closest", scale and "only evidence".
6. **Divide with Note B.** Note A owns construction, units, ladder, level versus flow, purge, NFCI, stance. Note B cuts Section 2.2 to a paragraph, keeps source-of-move, proportionality, decomposition and the sacrifice ratio, and adds: the index carries channel and anticipation; unemployment, not payrolls or inflation, is the claim; r* does not stabilize the response. No window-surprise material goes into Note A.

## 6. Verdict

With this plan Note A can stand as a co-equal contribution, but not under its present framing: a paper asking whether indexes agree has a modest result a referee will say so about. A paper asking how much financial conditions add to the stance beyond the policy rate, in common units and relative to neutral, has an economic question, a direct answer (an increment for unemployment in flow form, none for inflation), validity checks and an honest account of limits (power, five recessions, shared data, equities as the carrier). Its value to Note B is a defined object and a list of what may and may not be claimed. Two conditions decide it: the results must hold on the 1996+ sample, and, because out-of-sample evidence is thin, it must be written as a measurement-and-stance paper, not a forecasting paper. [inference]
