# Morgan Stanley financial conditions indexes: what is known, and how to replicate

Research note, 21 Oct 2026 (updated the same day with the policy-rate-equivalent index). Web research only; no Morgan Stanley
client research or Bloomberg data was accessible. Claims are tagged **[verified]** (read on a primary page), **[secondhand]**
(reported by a third party) or **[inference]** (my reading).

## Bottom line
Morgan Stanley appears to use **at least two** financial conditions indexes, and the more recent one is much easier to replicate:

1. **A current, policy-rate-equivalent index (Martin Tobias, Morgan Stanley Research, 2026).** 12 market variables, built on the
   framework of the Federal Reserve Bank of San Francisco and expressed as an equivalent federal funds rate. The SF Fed framework
   is its public **Proxy Funds Rate**, which is downloadable weekly through 2026-10-09 and whose method is public (principal
   components of 12 rates and spreads, mapped to the funds rate with pre-2008 correlations). Morgan Stanley's own index is not
   published, but it is "modeled on" this, so the public series is a close stand-in and the method can be reproduced.
2. **The older "MS FCI"** (a daily z-score weighted average of equities, short rates, long rates and the dollar, on Bloomberg since
   1995). Weights not public; replication needs the Bloomberg history.

A third description (five daily variables aggregated with FRB/US growth sensitivities) was reported by a third-party summary and could
not be checked; see "Unverified" below. It conflicts with the SF Fed description if it refers to the same index. Section C builds a
reconstruction of it from the Fed's public FRB/US model.

## A. The 2026 policy-rate-equivalent index
**[verified]** From Morgan Stanley's article ["Fed Rate Pause: What It Could Mean for Fixed Income Market"](https://www.morganstanley.com/insights/articles/fed-rate-pause-fixed-income-market-impact-2026):
Martin Tobias, U.S. Interest Rate Strategist, Morgan Stanley Research, "and his team developed a financial conditions index modeled on a
framework used by the Federal Reserve Bank of San Francisco. The index incorporates 12 market variables, including Treasury yields,
mortgage rates and corporate borrowing spreads, to estimate the effective level of monetary policy implied by financial conditions.
Since the start of the Iran conflict, the index suggests financial conditions have tightened by an amount equivalent to four
25-basis-point rate increases." (The page carries the surrounding July 2026 context: Warsh as Fed chair, a "will not hike in July" call.)

**[verified]** The SF Fed's [Proxy Funds Rate](https://www.frbsf.org/research-and-insights/data-and-indicators/proxy-funds-rate/) (updated 14 Oct 2026),
following Doh and Choi (2016, FRB Kansas City *Economic Review* 101(3)), Choi, Doh, Foerster and Martinez (2022, FRBSF Economic Letter
2022-30) and Foerster and Martinez (2024, Economic Letter 2024-16):
- Uses 12 financial variables, "including Treasury rates, mortgage rates, and borrowing spreads"; the 2024 letter lists "several Treasury
  rates, mortgage rates, municipal bond rates, corporate borrowing rates, and interest rate spreads". Sources: Federal Reserve Board,
  Freddie Mac, The Bond Buyer, Moody's. I could not read the paper that lists all 12 series, so the exact list is still open.
- Extracts common movements by **principal components**, then maps the first three components to **levels of the federal funds rate**
  using the **pre-2008 correlations**. Until the week of 12 Dec 2008 the proxy matches the funds rate by construction; afterwards it
  diverges, showing the effect of forward guidance and the balance sheet.
- Interpreted as "what federal funds rate would typically be associated with prevailing financial market conditions if these conditions
  were driven solely by the funds rate". Weekly and monthly data, back to 1976, as an Excel file linked from that page
  (`https://www.frbsf.org/wp-content/uploads/proxy-funds-rate-data.xlsx`).
- Equities and the dollar are **not** among the variables the SF Fed describes. Whether Morgan Stanley's 12 variables include them is unknown.

**Consistency check on the "four hikes" figure (my calculation, [inference]).** The SF Fed proxy funds rate was about 3.55 at the end of
February 2026, 4.5 in early July, 5.11 on 9 Oct 2026 (the effective funds rate 3.63 to 3.88). From the end of February to early/mid-July
that is about +0.95 pp, roughly four 25 bp steps, which matches Morgan Stanley's statement **if the Iran conflict began around late
February or March** (I did not establish the start date; the proxy begins rising in mid-March). Since the end of February it is now +1.56 pp,
about six 25 bp steps. This only shows the two indexes are on a comparable scale; Morgan Stanley's own 12 variables and weights may differ.

## B. The older MS FCI (1995 to 2012 documented)
- **[verified]** Morgan Stanley's glossary (Wealth Management Investment Resources definitions): a "weighted index comprised of changes in
  equities, short-term interest rates, long-term interest rates & USD currency". No credit spreads listed, unlike the GS index and FCI-G.
- **[verified]** Aramonte, Rosen and Schindler (2013), Fed FEDS 2013-39, Table 1: daily, weighted average, starts 1995, data from Bloomberg,
  no reference. The paper's indexes are z-scores. Sample July 1995 to June 2012: mean 0.075, median -0.139, 10th/90th percentile -1.14/1.72,
  September 2008 value 0.76 (other daily indexes 2.6 to 7.7); it deteriorated mainly into October 2008; monthly correlation with the St. Louis
  Fed stress index 39.7% (with the other indexes 22% to 49%, the lowest in the table); AR(1) root interval 0.83 to 0.95, lower than the others
  (about 0.92 to 1.00). A less persistent index is what a construction on changes or deviations would give **[inference]**.
- Weights, series, normalization window and ticker: not found.

## C. Five-variable reconstruction (built here, 21 Oct 2026)
The unverified description (10-year yield, S&P 500, BBB spreads, dollar, oil, aggregated into a funds-rate equivalent with FRB/US growth
sensitivities) is implementable from public pieces, so I built it. **It is a reconstruction of the described method, not Morgan Stanley's
index**; the weights are mine and the original is unverified.

**Step 1: FRB/US sensitivities** (`analysis/frbus_sensitivities.py`, output `analysis/frbus_sensitivities.csv`). The Board's public FRB/US model
and Python package run here (the package pins old libraries, so it needs an isolated Python 3.9 environment; setup is in the script's docstring).
In the steady-state baseline, make one persistent shock to one variable with the funds rate and every other financial variable held at baseline,
and compare the effect on real GDP with that of a 1 pp funds-rate shock. Funds-rate equivalent (pp of funds rate) at the q4 / q8 / q12 horizon:

| Variable (unit) | q4 | q8 | q12 |
|---|---|---|---|
| 10-year yield, +1 pp (mortgage rate and BBB yield follow, spread fixed) | 1.27 | 0.99 | 0.79 |
| BBB spread, +1 pp | 0.40 | 0.60 | 0.68 |
| Stock prices, 1% fall | 0.099 | 0.104 | 0.100 |
| Broad dollar, 1% rise (real exchange rate) | 0.315 | 0.336 | 0.296 |
| Oil, 1% rise | 0.026 | 0.018 | 0.015 |

GDP effect of the 1 pp funds-rate shock itself: -0.14% (q4), -0.27% (q8), -0.39% (q12).

**Levels versus spreads, and what is held fixed (checked, with one correction).**
- The 10-year shock moves the BBB *yield* one-for-one (BBB spread held fixed) and the mortgage rate by 0.88 pp at impact; the spread shock moves only the
  spread over the 10-year. The index uses the 10-year *level* and the BBB *spread*, so the BBB yield change is exactly the sum of the two pieces: no double
  counting of corporate bonds. The 10-year coefficient therefore includes the mortgage and corporate-yield pass-through, which is appropriate only if the
  index has no separate mortgage or corporate-yield term. Residual mismatch: the model's spread is over the 10-year Treasury, the ICE OAS used in the
  index is over the matched-maturity Treasury curve.
- First version of the experiments held the funds rate, 10-year, BBB spread, equity premium, dollar and oil fixed but **left household stock wealth free**,
  which fell 5.7% on a 1 pp funds-rate rise, 2.3% on a 1 pp 10-year rise and 1.2% on a 1 pp spread widening. That put an equity channel inside the rate and
  spread coefficients (double counting the equity variable). It is now held fixed in those experiments, which raised the 10-year, BBB, dollar and oil
  equivalents (the funds-rate shock alone is weaker once the stock-wealth fall is removed). The equity experiment still lets stock wealth respond: it
  shocks the required return on equity, so both the wealth effect and the cost-of-capital channel operate.

Choices that matter and are mine: the horizon (q4 is the first-year growth effect), persistent shocks, policy held fixed, the 10-year's pass-through,
stock price proxied by household stock wealth, real rather than nominal exchange rate, VAR expectations, steady-state starting point. The Fed's own FCI-G
multipliers (this repo's `multipliers.csv`) imply larger relative weights for equities and the dollar (about 1.5 to 2 times these), so the sensitivities
are uncertain by that order.

**Step 2: daily index** (`analysis/ms5_index.py`, output `analysis/ms5_index_daily.csv` and `analysis/ms5_index.png`): FFR equivalent = sum of
sensitivity times the change since a base date in the 10-year (DGS10), BBB OAS (FRED), S&P 500, broad dollar (DTWEXBGS extended with DXY) and WTI.
Positive = tighter; divide by 0.25 for 25 bp hikes.

**What it shows (base 27 Feb 2026).** The date of the Iran conflict is not established here, so the base date is a guess. Oil went from $67 to $91-101
in March and stocks fell, then equities recovered to new highs while the 10-year rose.

| Date | q4 sensitivities | q8 sensitivities |
|---|---|---|
| 1 April | +2.60 pp (10.4 hikes) | +2.23 pp (8.9) |
| 10 July | +0.66 pp (2.6 hikes): 10-yr +0.75, dollar +0.71, oil +0.20, equities -0.96, BBB -0.04 | +0.41 pp (1.7) |
| 16 Oct | **+2.31 pp (9.3 hikes)**: 10-yr +1.43, dollar +0.88, oil +1.07, equities -1.07 | +1.68 pp (6.7) |

- The result depends on the base date: bases after the March oil spike (from 6 March) give negative changes by July (not re-run after the correction).
- Against the SF Fed proxy funds rate (+0.94 pp by 10 July and +1.56 pp by 9 Oct from the same base) the stand-in has a similar order of magnitude and
  broadly similar movement, but is larger by October and moves more on oil and the dollar.
- It does **not** reproduce "four 25 bp hikes by July" (2.6 hikes on 10 July, 5.1 on 20 July at q4). That statement belongs to the 12-variable index
  (section A), not to the five-variable one, so it is not a validation target for this.

**Cannot be validated.** No published observations of a five-variable Morgan Stanley index were found, so nothing here shows it matches.

## Next steps for the five-variable version
1. Find the original Morgan Stanley note behind the third-party summary: exact variables, the horizon, whether the equivalence is on growth or on a
   broader objective, and any quoted levels (even a few dated readings would give validation points).
2. Settle the unit conventions: S&P 500 as a return over what window; the dollar index used; WTI or Brent; whether 10-year pass-through to mortgage rates
   and BBB yields is included; the horizon.
3. Check sensitivity to the model state: the same shocks from a 2026-like state with the funds rate at 3.6 to 3.9% and the current baseline, rather than
   the model's steady state, and with model-consistent (MCE) expectations.
4. Decide whether to fold the equivalents into the daily page next to the GS and FCI-G versions.

## Unverified claims (do not rely on them yet)
- **Five-variable index with FRB/US weights.** A third-party research summary (xxquant / "Hilo Research", July 2026) reportedly describes a
  Morgan Stanley FCI built from the 10-year yield, S&P 500 returns, BBB spreads, the dollar and oil, aggregated into a funds-rate equivalent
  using FRB/US growth sensitivities. I could not open the page (access check) and have not seen the Morgan Stanley report. It does not match the
  official article's description (12 variables, SF Fed framework), so it may be a different index (for example from the economics team) or a
  paraphrase error. If it exists, it would be the GS-style growth-weighted design and the closest to what this repo already replicates.
- **October 2023: "about three 25 bp hikes since the September FOMC"** (Vishy Tirupattur, *Thoughts on the Market*, 25 Oct 2023, "Implications of
  the Treasury Market Selloff"). The episode exists, but the summaries I found do not mention the three-hike figure or the exogenous/endogenous
  distinction. Not confirmed.
- **October 2026: an index of rates, dollar and energy at its tightest since 2022** (Mike Wilson coverage). Oil is not in the 2026 article's
  description or the older definition, so this may be a different composite.

## What is still missing
The 12 series in the Morgan Stanley (and SF Fed) index and whether they match; Morgan Stanley's weights or mapping; whether a Morgan Stanley
index series exists outside client research (no ticker confirmed); the original July 2026 notes.

## How the three approaches compare
| | GS FCI | Fed FCI-G | SF Fed proxy funds rate (MS 2026 is "modeled on" it) | Older MS FCI |
|---|---|---|---|---|
| Variables | FFR, 10-yr, BBB, CAPE, dollar | FFR, 10-yr, mortgage, BBB, stocks, house prices, dollar | 12 rates and spreads (Treasuries, mortgage, municipal, corporate, spreads) | equities, short rate, long rate, dollar |
| Weights from | published estimates of growth effects | Fed multipliers (growth effects) | principal components mapped to the funds rate (pre-2008 correlations) | not published |
| Units | index points | pp of GDP growth | percent (an equivalent funds-rate level) | z-score |
| Frequency | daily | monthly | weekly and monthly | daily |
| Public data | formula and data | code and weights | series and method | Bloomberg only |

## Replication plan
1. **Start with the SF Fed proxy funds rate.** Download the weekly and monthly series (public). Express its changes in 25 bp units and compare
   with Morgan Stanley's "four hikes" statement once the conflict start date is pinned down.
2. **Reproduce the method.** Recover the 12 input series (Federal Reserve Board H.15 Treasuries, Freddie Mac PMMS mortgage rate, Moody's Aaa and Baa
   corporate yields, Bond Buyer municipal index, the listed spreads; the exact list needs the Doh-Choi paper, which I could not download from this
   container), take principal components, map the first three to the funds rate on the pre-2008 sample, and extend. Validate against the SF Fed series
   (which should match closely) before trying anything Morgan Stanley-specific. Then make it daily from the daily series.
3. **Test equities and the dollar.** Add them to the 12 and see whether the mapping changes materially; this is a place Morgan Stanley's index might differ.
4. **Older MS FCI:** needs the Bloomberg history. Fit it to the S&P 500, a short rate, the 10-year and the dollar, in levels and in daily changes
   (if "changes in" is literal the changes fit should be near exact); check weight stability.
5. **If the FRB/US five-variable description turns out to be real:** it is a growth-weighted design like this repo's GS and FCI-G versions, and the
   FRB/US sensitivities would play the role the Fed's published multipliers play for the FCI-G.

## Sources
- Morgan Stanley, Fed Rate Pause: What It Could Mean for Fixed Income Market (July 2026): https://www.morganstanley.com/insights/articles/fed-rate-pause-fixed-income-market-impact-2026
- SF Fed, Proxy Funds Rate (data and method): https://www.frbsf.org/research-and-insights/data-and-indicators/proxy-funds-rate/
- Choi, Doh, Foerster, Martinez (2022), Monetary Policy Stance Is Tighter than Federal Funds Rate, FRBSF Economic Letter 2022-30: https://www.frbsf.org/research-and-insights/publications/economic-letter/2022/11/monetary-policy-stance-is-tighter-than-federal-funds-rate/
- Foerster and Martinez (2024), The Anatomy of the Post-Pandemic Monetary Tightening Cycle, FRBSF Economic Letter 2024-16: https://www.frbsf.org/research-and-insights/publications/economic-letter/2024/06/anatomy-of-post-pandemic-monetary-tightening-cycle/
- Doh and Choi (2016), Measuring the Stance of Monetary Policy on and off the Zero Lower Bound, FRB Kansas City Economic Review 101(3): https://www.kansascityfed.org/research/economic-review/3q16-dohchoi-monetary-policy-zero-lower-bound/
- Morgan Stanley Wealth Management, Index, Indicator and Survey Definitions: https://www.morganstanley.com/wealth-investmentsolutions/wmir-definitions
- Aramonte, Rosen, Schindler (2013), Assessing and Combining Financial Conditions Indexes, FEDS 2013-39: https://www.federalreserve.gov/pubs/feds/2013/201339/201339pap.pdf
- Seeking Alpha, Tighter financial conditions doing part of Fed's work - Morgan Stanley (12 Oct 2026, truncated): https://seekingalpha.com/news/4652159-tighter-financial-conditions-doing-part-of-feds-work---morgan-stanley
- Morgan Stanley, Thoughts on the Market, Implications of the Treasury Market Selloff (25 Oct 2023, aggregator page only): https://podwise.ai/episodes/45938
