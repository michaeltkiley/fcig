# Morgan Stanley Financial Conditions Index (MS FCI): what is known, and a plan to replicate

Research note, 21 Oct 2026. Web research only; no Morgan Stanley research report, methodology note or Bloomberg data was
accessible. Facts are marked **[source]** where a document supports them and **[inference]** where I am reading between lines.

## Bottom line
The weights, exact series and normalization are **not public**, unlike the Goldman Sachs index (formula and weights published
by Hatzius, 2019) and the Fed's FCI-G (weights released with the code). What is public is the family of inputs. A replication
therefore needs the published index history (Bloomberg) to **estimate** the weights; it cannot be built from a formula.

## What the sources say
1. **Components.** Morgan Stanley's own glossary defines it as a *"weighted index comprised of changes in equities, short-term
   interest rates, long-term interest rates & USD currency"* (Wealth Management Investment Resources definitions page).
   **[source]** Four groups. Credit spreads are **not** listed, unlike the GS index (rates, spreads, equity valuation, dollar) and
   the Fed FCI-G (which has a BBB yield). The wording "changes in" may mean the index is built from changes rather than levels;
   it may equally be loose wording. **[inference]**
2. **Frequency, aggregation, history.** Aramonte, Rosen and Schindler (Fed FEDS 2013-39), Table 1: daily, aggregated as a
   **weighted average**, starts **1995**, data source **Bloomberg**, no published reference or year established. **[source]**
   The same paper says all the indexes in its table except one are expressed as **z-scores**. **[source]**
3. **Behaviour (July 1995 to June 2012, daily, in z-score units).** Mean 0.075, median -0.139, 10th and 90th percentiles -1.14 and
   1.72, value in September 2008 0.76 (the other three daily indexes were at 2.6 to 7.7 then); it deteriorated mainly into October 2008
   rather than September. It is the index **least correlated** with the St. Louis Fed index (monthly correlation 39.7%; its correlations with the other
   indexes run from 22% to 49%, the lowest in the paper's table), and its AR(1) root is lower than the other daily indexes (confidence interval 0.83 to 0.95, versus about
   0.92 to 1.00 for Bloomberg's). **[source]** A less persistent index is what you would get from a construction on changes or
   deviations rather than levels, but that is my reading, not documented. **[inference]**
4. **Current use.** A July 2026 Morgan Stanley research note ("Watch Out for a Fed Pause", reported by news outlets, not read in
   the original) says the index shows conditions tightening by the equivalent of about **four 25 bp rate hikes** since the Iran
   conflict began. **[source, secondhand]** So the published index is, or can be translated into, rate-hike-equivalent units. In
   October 2026 Mike Wilson linked tighter conditions to higher Treasury yields, a stronger dollar and high oil prices
   (Seeking Alpha / WSJ coverage; the page is truncated). Oil is not in the definition above, so that may describe a different
   composite or just commentary. **[unverified]**

## What I could not find
Series and maturities used (S&P 500 or another equity measure; fed funds, 2-year or other short rate; 10-year or other long rate;
which dollar index), the weights and how they were chosen, whether they are fixed or re-estimated, the normalization window for
the z-score, the Bloomberg ticker (I could not confirm one; Bloomberg's own index is BFCIUS, which is a different index), and the
history since 2012. Morgan Stanley's FCI research notes are client-only.

## How it compares with the two we have
| | GS FCI | Fed FCI-G | MS FCI |
|---|---|---|---|
| Variables | FFR, 10-yr, BBB spread, CAPE, dollar | FFR, 10-yr, mortgage, BBB, stocks, house prices, dollar | equities, short rate, long rate, dollar |
| Weights | published (Hatzius 2019) | published (Fed multipliers) | not published |
| Frequency | daily | monthly weights on quarterly changes | daily |
| Units | index points (100 = average) | pp of GDP growth | z-score (per the Fed 2013 table); also quoted in rate-hike equivalents |
| Credit | yes | yes | no, per the definition |

## Replication plan
**With the series (preferred).** Pull the MS FCI history from Bloomberg (search the terminal for "MS FCI" / Morgan Stanley
Financial Conditions Index; the ticker is unconfirmed) and fit it to the four groups using this repo's data:
- Candidates: S&P 500 (log), a short rate (fed funds `DFF`, 2-year `DGS2`, or 3-month), the 10-year `DGS10`, and the dollar
  (broad `DTWEXBGS` or DXY, which this repo already stores).
- Estimate in **both** forms: the level of the z-scored index on the standardized variables, and its daily change on the daily
  changes. If "changes in" is literal, the second form should fit almost exactly (R-squared near one with four regressors),
  and the first should not. Check sign conventions (up = tighter?), whether the weights are stable (rolling regression), and
  whether the equity weight is on the level of the S&P 500 or on a valuation measure.
- Validation target: the "four 25 bp hikes" figure for the period since the Iran conflict began (needs the start date from the
  note), and the September/October 2008 shape from the Fed paper.

**Without the series.** Build an "MS-style" index from the same four groups with weights from the Fed FCI-G multipliers or the GS
weights and compare with the published statements above. It would be a stand-in, not a replication, and cannot be validated beyond
the one calibration point.

## Open questions for whoever can see the research
1. The ticker, and the history since 2012. 2. Is it built on levels or changes, and what is the z-score window? 3. Which equity,
rate and dollar series, and are weights fixed? 4. How is "equivalent to a 25 bp hike" computed?

## Sources
- Morgan Stanley Wealth Management, Index, Indicator and Survey Definitions: https://www.morganstanley.com/wealth-investmentsolutions/wmir-definitions
- Aramonte, Rosen, Schindler (2013), Assessing and Combining Financial Conditions Indexes, FEDS 2013-39: https://www.federalreserve.gov/pubs/feds/2013/201339/201339pap.pdf
- Hatzius, Hooper, Mishkin, Schoenholtz, Watson (2010), Financial Conditions Indexes: A Fresh Look after the Financial Crisis (context; contains no MS FCI description): https://www.princeton.edu/~mwatson/papers/USMPF-2010.pdf
- Seeking Alpha, "Tighter financial conditions doing part of Fed's work - Morgan Stanley" (12 Oct 2026; page truncated): https://seekingalpha.com/news/4652159-tighter-financial-conditions-doing-part-of-feds-work---morgan-stanley
- Press coverage of Morgan Stanley's July 2026 note (four 25 bp hikes equivalent), e.g. https://www.tribuneindia.com/news/business/morgan-stanley-sees-us-fed-holding-rates-steady-in-2026-as-easing-inflation-boosts-fixed-income-outlook/
