# Survey measures of long-run interest-rate expectations (search of 18 Nov 2026)

Purpose: a survey-based r* for Note B's r* exploration, with as long a history as possible. Tags: [verified] = read in the source; [secondhand] = from a paper's description of another source.

| Survey | Long-run rate question | Inflation counterpart | Frequency | Start (long-run question) | Access |
|---|---|---|---|---|---|
| Blue Chip Economic Indicators (BCEI) | 3-month T-bill, average 6-10 years ahead (also years 3-6, 7-11) | CPI 6-10 years ahead (from 1984) | twice a year (March, October) | T-bill 1983, CPI 1984, real GDP 1979 [secondhand: Crump, Eusepi, Moench, NY Fed SR 775, Table 1] | subscription (Wolters Kluwer) |
| Blue Chip Financial Forecasts (BCFF) | 3-month T-bill, fed funds and 10-year Treasury, each year 1-5 and average 6-10 years ahead | CPI / GDP price index, same horizons | twice a year (June, December) | T-bill 1983 [secondhand: SR 775]; Bauer-Rudebusch say the earliest long-run rate forecasts are a biannual BCFF series that starts in 1986, and that BCFF has asked for long-range forecasts twice a year since 1988 [verified, their fn. 13 and Sec. 6] | subscription |
| Survey of Professional Forecasters (Philadelphia Fed) | BILL10: average 3-month bill rate over the current and next 9 years; BOND10: same for the 10-year Treasury | CPI10 (10-year average CPI inflation) | annual (Q1 survey) for BILL10/BOND10; CPI10 quarterly | 1992 [verified: files downloaded, 1992-2026, 35 Q1 observations; CPI10 from 1991Q4] | free: `survey_data/Median_*_Level.xlsx` |
| Consensus Economics | 3-month rate and 10-year yield, years 3-10 | CPI years 3-10 | quarterly (long-run) | T-bill 1998, CPI 1989 [secondhand: SR 775] | subscription |
| Survey of Primary Dealers / Market Participants (NY Fed) | longer-run fed funds | longer-run PCE (from 2011) | 8 per year | 2011 [secondhand: SR 775] | free |
| FOMC Summary of Economic Projections | longer-run fed funds (median) | longer-run PCE inflation 2 | 4 per year | 2012 (fed funds dots) [inference: standard knowledge, not re-checked] | free |

Findings:
* No survey of long-run interest-rate expectations goes back to 1973. The earliest are the two Blue Chip surveys (long-run T-bill from 1983; BCFF rate forecasts 1986-88 by Bauer and Rudebusch's account). Both are proprietary; I have no access. Crump-Eusepi-Moench combine nine surveys into a term structure of expectations from 1983 (their sample March 1983 to September 2016); whether their estimates are posted was not checked.
* The only free long series is the SPF: BILL10 less CPI10, annual from 1992, which covers the 1996 baseline but not 1973. It is a 10-year average including the current year, so it mixes near-term policy expectations into the "long run" (it fell below zero in 2020-22).
* SPF real bill (BILL10 - CPI10) against LW (February value), 1992-2026: correlation 0.74; it lies below LW throughout (about 1.7 vs 2.9 in 1996-2007; 0.3 vs 1.0 in 2009-2019; -0.3 in 2020-22 against LW 1.7-2.0).
* Bauer and Rudebusch (2020) avoid survey r* for two reasons they state: the short history of interest-rate forecasts and the poor forecasting record of long-range yield surveys [verified, fn. 13]. Cho and Williams (Liberty Street Economics, Aug 2025) build a Blue Chip r* as the BCFF fed funds projection minus GDP-price inflation for the five-year period furthest out (twice a year) [verified]; their chart window is 1995Q4-2025Q1.

Sources: Bauer and Rudebusch, "Interest Rates Under Falling Stars" (AEA 2018 preliminary version, aeaweb.org); Crump, Eusepi and Moench, "The Term Structure of Expectations and Bond Yields", NY Fed Staff Report 775; Liberty Street Economics, 25 Aug 2025; Philadelphia Fed SPF data files (BILL10, BOND10, CPI10).
