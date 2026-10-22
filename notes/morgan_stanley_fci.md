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

**Concept.** The yardstick is a funds-rate hike with *full* transmission: raise the funds rate 1 pp and let every other financial variable respond as FRB/US
implies. Each index variable's *partial* effect on GDP (no spillovers to the other variables) is then expressed as a fraction of that hike's effect. The
equivalent of a combined move is the sum of its partial equivalents, so it also matters that the partials roughly add up to the full hike (checked below).

**Step 1: FRB/US sensitivities** (`analysis/frbus_sensitivities.py`, output `analysis/frbus_sensitivities.csv`). The Board's public FRB/US model and Python
package run here (the package pins old libraries, so it needs an isolated Python 3.9 environment; setup is in the script's docstring). Steady-state baseline,
VAR expectations, persistent shocks. In the partial experiments stocks (required return and stock wealth), the dollar, oil and the BBB spread are held at
baseline except the shocked variable, and the funds rate is held fixed. The long-rate shock is a parallel +1 pp in the 5-, 10- and 30-year yields (the
10-year stands for the long end; the mortgage rate and BBB yield follow, spread unchanged). Funds-rate equivalents (pp of funds rate) at q4 / q8 / q12:

| Variable (unit) | q4 | q8 | q12 |
|---|---|---|---|
| Long rates, parallel +1 pp | 0.57 | 0.52 | 0.47 |
| (alternative: the 10-year alone +1 pp, 5- and 30-year unchanged) | 0.40 | 0.29 | 0.22 |
| BBB spread, +1 pp | 0.13 | 0.17 | 0.19 |
| Stock prices, 1% fall | 0.031 | 0.030 | 0.028 |
| Broad dollar, 1% rise (real exchange rate) | 0.099 | 0.097 | 0.082 |
| Oil, 1% rise | 0.008 | 0.005 | 0.004 |

Yardstick: a 1 pp funds-rate hike with full transmission cuts GDP by 0.45% (q4), 0.95% (q8), 1.43% (q12). At q4 it moves the 5-, 10- and 30-year yields by
+0.49, +0.37, +0.27 pp, the mortgage rate +0.36, the BBB yield +0.42, stock wealth -13.2%, the real dollar +1.6%, the BBB spread +0.05 pp, oil +0.06%.

**Do the partials add up to the full hike?** Policy rate and curve alone (stocks, dollar, spread, oil fixed) cut GDP by 0.21 / 0.39 / 0.54% (q4/q8/q12); adding
the partial effects of the stock, dollar and spread spillovers (at their q4 sizes) gives -0.47 / -0.92 / -1.27 against the full hike's -0.45 / -0.95 / -1.43, so
within about 4%, 3% and 11%. Stocks are the largest spillover (-0.19 at q4), then the dollar (-0.07).

**Review history (three corrections).** (1) Household stock wealth had been left free, so equity effects leaked into the rate and spread coefficients
(wealth fell 5.7%, 2.3% and 1.2% on 1 pp funds-rate, 10-year and spread shocks); it is now held fixed in non-equity experiments. (2) The curve was inconsistent: the
10-year had been shocked alone (equity valuation depends on the 30-year yield, so a 10-year-only move cut stocks by 2.3%, against 27% for a parallel
long-rate move and 13% for a funds-rate hike), and the funds-rate shock had held the 10-year fixed while the 5- and 30-year moved. (3) The yardstick was
the partial hike (curve responding, stocks, dollar and spreads fixed: -0.21% at q4), not a real hike with its financial spillovers (-0.45%); against the
partial yardstick every equivalent was about 2.1 to 2.6 times too large (the alternative column `ffr_eq_curve_*` in the CSV keeps that version).
Other points: corporate bonds are not double counted (the long-rate shock moves the BBB yield with the spread unchanged; the spread shock moves only the spread; the index
uses the 10-year level and the BBB spread); the model's spread is over the 10-year Treasury while the ICE OAS used in the index is over the matched-maturity curve.

Choices that matter and are mine: horizon (q4 is first-year growth), persistent shocks, 10-year as a proxy for the long end, stock price proxied by household
stock wealth, real rather than nominal exchange rate, VAR expectations rather than model-consistent, steady-state starting point rather than 2026 conditions.
The Fed's own FCI-G multipliers (this repo's `multipliers.csv`) imply larger relative weights for equities and the dollar.

**Step 2: daily index** (`analysis/ms5_index.py`, output `analysis/ms5_index_daily.csv` and `analysis/ms5_index.png`): FFR equivalent = sum of
sensitivity times the change since a base date in the 10-year (DGS10), BBB OAS (FRED), S&P 500, broad dollar (DTWEXBGS extended with DXY) and WTI.
Positive = tighter; divide by 0.25 for 25 bp hikes. Options: `--horizon q4|q8|q12`, `--tenyear alone`.

**What it shows.**

| Window | q4 | q8 | q4, 10-year alone |
|---|---|---|---|
| Since 27 Feb 2026 to 1 April (assumed conflict start) | +0.88 pp (3.5 hikes) | +0.73 (2.9) | +0.82 (3.3) |
| ... to 10 July | +0.31 pp (1.2) | +0.26 (1.0) | +0.21 (0.8) |
| ... to 20 July | +0.51 pp (2.1) | +0.41 (1.7) | +0.41 (1.6) |
| ... to 16 Oct | **+0.93 pp (3.7)**: 10-yr +0.64, dollar +0.28, oil +0.34, equities -0.34 | +0.75 (3.0) | +0.74 (2.9) |
| Since 27 Aug 2026 to 16 Oct | **+0.67 pp (2.7)**: 10-yr +0.24, dollar +0.23, oil +0.15, equities +0.03, BBB +0.01 | +0.59 (2.4) | +0.59 (2.4) |

- The 27 Feb base date is a guess (the conflict start is not established here); bases after the March oil spike give negative changes by July.
- Against the SF Fed proxy funds rate (+0.94 pp by 10 July and +1.56 pp by 9 Oct from 27 Feb; +0.72 pp from 27 Aug to 9 Oct) the stand-in is now smaller, by
  about half; rates alone (10-year plus spread) are close to the proxy and the dollar and oil are what the proxy lacks.
- It does not speak to "four 25 bp hikes by July": that belongs to the 12-variable index (section A), and the July readings here (1.2 to 2.1 hikes) are not
  a validation target for it.

**Cannot be validated.** No published observations of a five-variable Morgan Stanley index were found, so nothing here shows it matches.

## D. Level version of the five-variable index (21 Oct 2026)
`analysis/ms5_level.py`: deviation of each variable from its 1990 to latest average times the sensitivities in section C; positive = tighter than average,
in pp of funds rate (q4). Stationary transforms: 10-year yield (nominal, real, or the real gap to r*), BBB spread, stock valuation (CAPE from the GS file),
real dollar (the FRB/US real exchange rate fpxr, put on a daily footing with the nominal broad dollar), real oil (WTI over the FRB/US PCE price level).
Everything except daily WTI comes from this repo's GS file and the Fed's FRB/US history, so FRED is not needed (FRED was down when this was built).
`--rstar` measures the 10-year as the real yield gap to Kiley's r* (`history/kiley_rstar.csv`, from the r* repo; one-sided estimate, 1.67% in 2026Q2).

| 16 Oct 2026 vs 1990-2026 average | Total | 10-yr | BBB | Equities | Dollar | Oil | Percentile |
|---|---|---|---|---|---|---|---|
| Nominal 10-year (default) | +0.96 | +0.48 | -0.12 | -1.33 | +1.58 | +0.35 | 81% |
| Real 10-year | +1.03 | +0.55 | -0.12 | -1.33 | +1.58 | +0.35 | 85% |
| Real 10-year gap to r* (`--rstar`) | **+1.13** | +0.65 | -0.12 | -1.33 | +1.58 | +0.35 | 88% |

Adjusting for real rates raises the 10-year term (+0.48 to +0.65) because r* has fallen from about 2.5% to 1.7%, so the same real yield is further above neutral;
it also makes the 2012 and 2021 readings less negative (10-year term -1.41 to -1.08 and -1.56 to -1.45).
**Equities are not adjusted for real rates**: the FRB/US stock equation implies 25% on the price per pp of real rates, but the valuation shows no stable relation
with the real 10-year yield in the data (slope -1.2% per pp, s.e. 2.7; monthly changes about zero; -17% to +24% across sub-periods), and applying the model's
mapping (`--erp`) puts the 2009-2012 equity term at +2.4 to +3.1 pp, which contradicts the policy stance. Kept as a flag for comparison only.
Validation is weak before 2008 because the funds rate is not one of the five variables (correlation with the effective funds rate +0.17 for 1990-2008; with the
SF Fed proxy +0.94 for 2020-2026; with the real policy rate gap, EFFR less expected inflation less r*, +0.32 for 1990-2026 and +0.54 for 2022-2026 in the `--rstar`
version). This is an index of conditions relative to the sample average, not a proxy for the policy rate, and the linear extrapolation of local sensitivities over
36 years and the averaging window drive its level.

## E. Refresh with FRED data and correlation with the GS FCI (22 Oct 2026)
FRED was back; all series were re-downloaded and the daily GS file was brought up to 20 Oct from `main`. The level index now takes its real dollar from FRED's
RTWEXBGS (2006 on; the old real broad series `RTWEXB` does not exist on FRED, so before 2006 the FRB/US real exchange rate is level-matched on), real oil from
CPIAUCSL and the real 10-year from the Cleveland Fed's EXPINF10YR (`--source frbus` keeps the earlier FRB/US-based version).

**Change windows to 20 Oct 2026 (q4 sensitivities; q8 in brackets).**
| Window | Total | 10-yr | BBB | Equities | Dollar | Oil |
|---|---|---|---|---|---|---|
| Since 27 Feb (S&P +11.4%, dollar +3.0%, oil +48%, 10-yr 3.97 to 5.12) | +0.98 pp, 3.9 hikes (+0.79, 3.2) | +0.65 | 0.00 | -0.36 | +0.30 | +0.39 |
| Since 27 Aug (S&P -0.2%, dollar +2.5%, oil +24%, 10-yr 4.67 to 5.12) | +0.72 pp, 2.9 hikes (+0.63, 2.5) | +0.26 | +0.01 | +0.01 | +0.25 | +0.20 |

**Level index vs 1990-2026 average, 20 Oct 2026 (pp of funds rate, q4).** Real gap to r* (`--rstar`): +0.73 (10-yr +0.44, BBB -0.12, equities -1.35, dollar +1.43, oil +0.34), 81st
percentile; nominal 10-year: +0.80 (77th); real 10-year (Cleveland expected inflation): +0.63 (76th). With the FRB/US-based inputs the r* version reads +1.21: the
real-rate and real-dollar construction moves the level by up to half a point, a source uncertainty on top of the sensitivities.

**Correlation of daily changes with the GS FCI** (`analysis/ms5_vs_gs.py`, `analysis/ms5_vs_gs.csv`; same trading days, 1990 to 20 Oct 2026, n about 9,200).
| Variant of the MS-style index | 1990-2026 | 1990-99 | 2000-08 | 2009-19 | 2020-26 | last 12 months |
|---|---|---|---|---|---|---|
| q4 sensitivities (all 10-year versions identical in daily changes) | **0.81** | 0.83 | 0.81 | 0.83 | 0.79 | 0.91 |
| q4 without oil | 0.90 | 0.89 | 0.87 | 0.91 | 0.93 | 0.97 |
| q8 sensitivities | 0.87 | 0.87 | 0.86 | 0.89 | 0.87 | 0.94 |
| q12 sensitivities | 0.89 | 0.89 | 0.89 | 0.90 | 0.89 | 0.95 |
Weekly changes (q4): 0.86; monthly changes: 0.87 to 0.90. The matching components (10-year, BBB spread, equity valuation, dollar) are correlated 0.99 to 1.00 with the GS
contributions in daily changes, so the gap from 1 is the weights, oil and the missing funds-rate term. Regression: the GS FCI moves 0.87 index points per pp of the
MS-style funds-rate equivalent (R-squared 0.66). Against the Fed FCI-G in daily changes since 2020 the MS-style index correlates +0.54 (3-year) and +0.47 (1-year),
the GS FCI +0.84 and +0.70. The correlation rises with the horizon because longer-horizon sensitivities put more weight on the BBB spread (0.13 at q4, 0.19 at q12) and
less on the dollar, closer to GS.

## F. Check of the oil simulation, and what drives the oil contribution (22 Oct 2026)
**Specification.** The oil price (poil, price of imported oil) is made exogenous and raised 10% for 24 quarters; the funds rate, stocks, dollar and BBB spread are held at
baseline. In FRB/US poil enters only the petroleum import price (pmp), which feeds consumer energy prices (headline PCE inflation, real income) and petroleum import volumes; core
inflation has no oil term, and the model's relative oil price (poilr) only feeds poil, so exogenizing poil cuts it out correctly. Outcome: a one-time step in headline inflation
(+0.38 pp annualized in the first quarter, then none), no change in core inflation, the funds rate or long rates, unemployment +0.02 pp; GDP -0.035 / -0.046 / -0.058% at q4 / q8 / q12.
**The funds-rate treatment does not matter for oil**: with the rule on and stocks, dollar and spread fixed the GDP effect is -0.034 / -0.041 / -0.046%; with everything endogenous
-0.031 / -0.036 / -0.039%. Funds-rate equivalent of oil per 1%: 0.0081 (q4), 0.0051 (q8), 0.0043 (q12) as built; 0.0079, 0.0045, 0.0034 with the rule on; 0.0072, 0.0040, 0.0029 fully endogenous.
**State dependence.** From the model's 2026Q2 baseline (oil $67, funds rate 3.7%) rather than the 2040 steady state: oil GDP effect -0.033 / -0.043 / -0.053% (nearly unchanged) but the
1 pp hike yardstick is stronger (-0.52 / -1.09 / -1.65%), so the oil equivalent is 0.0066 / 0.0041 / 0.0034 (about 18% lower at q4), and every other equivalent would also fall by about 13%.
The first-order size is plausible: net petroleum imports are about 0.7% of GDP in the model, so a 10% price rise costs about 0.07% of GDP before offsets.

**Why oil contributes so much in the recent windows: the price moves were large, not the sensitivity.** 10% on oil is only 0.08 pp of funds rate (0.3 of a 25 bp hike); 48% is 0.39 pp.
| Date | WTI | Brent | WTI % since 27 Feb | Oil contribution since 27 Feb |
|---|---|---|---|---|
| 27 Feb | $67.0 | $71.3 | 0 | 0 |
| 6 Mar | $90.8 | $95.7 | +30% | +0.25 pp |
| 20 Mar | $98.7 | $118.4 | +39% | +0.32 |
| 7 Apr (peak) | $114.6 | | | |
| 30 Apr | $108.6 | $124.2 | +48% | +0.39 |
| 30 Jun | $70.6 | $70.5 | +5% | +0.04 |
| 27 Aug | $84.8 | $90.2 | +24% | +0.19 |
| 30 Sep | $97.2 | $115.9 | +37% | +0.30 |
| 14 Oct | $96.3 | $126.6 | +36% | +0.30 |
| 20 Oct | $107.9 | $115.2 | +48% | +0.39 |
Since 27 Feb: WTI +47.7% (Brent +48.0%), +0.39 pp or 1.6 hikes. Since 27 Aug: WTI +24.1% (Brent +24.5%), +0.20 pp or 0.8 hikes. The window ends on a one-week jump in WTI ($96 to $108);
Brent and WTI gave the same percentage change over both windows, although their spread varied between $4 and $11 during the year, so the choice of benchmark matters on individual days (14 Oct: WTI $96, Brent $127) but not for these two windows.

## Next steps for the five-variable version
1. Find the original Morgan Stanley note behind the third-party summary: exact variables, the horizon, whether the equivalence is on growth or on a
   broader objective, and any quoted levels (even a few dated readings would give validation points).
2. Settle the unit conventions: S&P 500 as a return over what window; the dollar index used; WTI or Brent; whether 10-year pass-through to mortgage rates
   and BBB yields is included; the horizon.
3. Check sensitivity to the model state: the same shocks from a 2026-like state with the funds rate at 3.6 to 3.9% and the current baseline, rather than
   the model's steady state, and with model-consistent (MCE) expectations.
4. Decide whether to fold the equivalents into the daily page next to the GS and FCI-G versions.

## What Morgan Stanley's own notes say about effects (all I could find; mostly secondhand)
- **Policy-rate equivalence of the financial conditions index** [verified, Morgan Stanley article, July 2026]: the Tobias index shows tightening
  equal to four 25 bp hikes since the start of the Iran conflict; "markets have already priced in the persistent inflation risks identified by the
  FOMC by pushing the implied Fed funds rate path higher"; "The Fed doesn't need to deliver on the tightening in financial conditions in response to
  backward-looking data to retain credibility." Gapen (Morgan Stanley economics, as quoted) in the same article: "patience will win the day and the Fed will not hike in July".
  No growth numbers or weights are given.
- **October 2026, Mike Wilson (equity strategy)** [secondhand, ChainCatcher/WSJ and Seeking Alpha, both short]: an index built from interest rates, the dollar
  and energy prices is at its tightest since 2022; since mid-August equal-weighted financials, materials, consumer discretionary and industrials
  "have significantly underperformed the market"; the key variable is how Chair Warsh characterizes the tightening (if he acknowledges the market has done
  some of the Fed's tightening, pressure on rate-sensitive assets may ease); Morgan Stanley economists expect a hold in October. No growth effects quoted.
  An earlier Wilson note, undated, quoted via a news summary: each 1% move in the Dollar Index has about a -0.5% effect on profits.
- **BBB spreads and growth** [secondhand, Bloomberg, 16 Nov 2018, economists including Robert Rosener]: a sustained 10 bp widening in BBB spreads would
  cut growth by 0.3 pp and raise unemployment by 0.15 pp; a sustained 100 bp rise in BBB premiums over a year equals a 62 bp funds-rate hike. These two
  figures do not sit comfortably together as reported (10 bp to 0.3 pp implies 3 pp for 100 bp, which is far more than a 62 bp hike would do in FRB/US
  or the Fed's weights), so one is probably a different horizon or scaling; I could not read the original. The 62 bp figure compares with 0.27 to 0.50
  pp per 100 bp in the FRB/US reconstruction in section C.
- **October 2023** [Morgan Stanley Wealth Management, article on tighter financial conditions, 2023, read in part]: general statement that loosening
  conditions tend to lift asset prices and the reverse in 2022; no weights. The Tirupattur podcast "three 25 bp hikes" figure is unconfirmed.
- Nothing I found from Morgan Stanley gives the effect of the 10-year, the S&P 500, the dollar or oil on growth in funds-rate terms, other than the 2018 BBB item.

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
