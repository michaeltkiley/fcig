# Literature deep dive 2: DSGE models with a stock-market channel, and the policy models (subagent, 17 Nov 2026)

Reviewer read the PDFs cited (saved in the session scratchpad). Tags: [verified: p. X]; [fig-read] approximate (about +-10 percent); [secondhand]; [inference].

## 1. Castelnuovo and Nistico (2010, JEDC 34(9), 1700-31)
- **Model** [verified pp. 1701-1707]: small NK model; a constant fraction xi of traders replaced each period by newcomers with no wealth (discrete Blanchard-Yaari), so financial wealth enters the aggregate Euler equation (eq. 29, p. 1707); equity = claim on monopolistic dividends; sticky wages make dividends procyclical; no physical capital (p. 1723).
- **Quote for the blind spot** (p. 1701): the standard NK model "typically considers stock prices as redundant for the computation of the equilibrium values of inflation, output, and the policy rate".
- **Estimation** [verified pp. 1710-13]: Bayesian 1954Q3-2007Q2; S&P 500 growth observable with white-noise measurement error (about 65 percent of real stock-price forecast-error variance; model explains about 35 percent, p. 1723).
- **Wealth effect** [Table 1 p. 1712]: xi = 0.129 [0.080, 0.183]; setting xi = 0 lowers log marginal likelihood by about 34 (Table 2 p. 1713): "overwhelming support".
- **Fed response to stocks**: phi_s = 0.118 [0.072, 0.166]; phi_s = 0 costs about 21 log points.
- **25 bp monetary shock** (Fig. 8 p. 1720): stock-price gap about -0.2 percent on impact [verified p. 1719] (gap vs frictionless price, not S&P level); output gap trough about -0.06 at q3, -0.055 at q4, -0.03 at q8 [fig-read]; inflation about -0.05 pp on impact; policy rate back by q6.
- **Wealth channel share**: output trough about -0.06 baseline vs -0.05 standard model, so wealth adds about 15-20 percent to the peak [fig-read/inference]; financial shock explains 2-3 percent of output-gap variance, 25-35 percent of policy-rate variance (Table 5 p. 1722).
- **Authors' caveat** (pp. 1719, 1723): stock response "more moderate" than VARs (Bernanke-Kuttner about 1 percent per 25 bp; Bjornland-Leitemo almost 4 percent per 25 bp).
- **Citations**: Semantic Scholar 143, OpenAlex 149 (17 Nov 2026); EconPapers about 96.
- **Follow-ups**: Nistico (2016, JEEA 14(5)) optimal policy and financial stability in a non-Ricardian economy [secondhand]; Airaudo-Nistico-Zanna (2015) learning and asset prices [secondhand]; Milani (2017, IREF) direct wealth effect small, expectational effect of stock prices large [secondhand; C-N p. 1702 calls Milani's direct effect "negligible", verified]; Funke-Paetz-Pytlarczyk (2011, Hong Kong), Paetz-Gupta (2016, South Africa), Hoshino-Ida (2025, Japan) "substantial" wealth effects [secondhand]; Ifrim (2023) [secondhand]; Hollander-Liu (below).
- **Hollander-Liu** (Stellenbosch WP 2013/2014; Econ. Modelling 2016): savers, borrowers, entrepreneurs hold equity; wealth effect plus collateral and bank capital; US 1982-2012 with S&P 500 observable [verified WP pp. 2-4, 12, 15-17]. Monetary shock (Fig. 4, fig-read): equity about -6 percent on impact (units of the rate unclear: about -2 to -8 per pp), output trough about -0.6 at q2 vs -0.4 without equity (equity about one-third of peak).
- **Christiano-Motto-Rostagno (2014 AER)**: Wilshire 5000 identified with entrepreneurial net worth (pp. 28, 42) [verified]; BGG accelerator, no household stock-wealth effect [inference].

## 2. Policy models: equity price or household stock wealth? [verified unless noted]

| Model | Equity price | Household stock-wealth effect | Asset prices it does contain | Source |
|---|---|---|---|---|
| Smets-Wouters 2007 | No | No | Tobin's q (value of installed capital); exogenous risk-premium wedge; no asset-price observables | ECB WP 722 pp. 11-12 |
| CEE 2005 | No | No | shadow price of installed capital (Tobin's q) | JPE pp. 10, 12, 19 |
| EDO (Chung-Kiley-Laforte 2010) | No | No | implicit capital values; exogenous risk premia; no asset-price observables | FEDS 2010-29 pp. 1-3, 7, 13, 17 |
| SIGMA (Erceg-Guerrieri-Gust) | No | No (hand-to-mouth instead) | UIP/intermediation premium; "omission of other potentially important financial channels" | IFDP 835 pp. 8, 15, 17, 35 |
| NY Fed DSGE (SR 647, 2013) | No | No | price of capital, entrepreneurial net worth, Baa-10y spread (BGG) | SR 647 pp. 2, 5, 13, 17; DGS 2015 [secondhand] |
| FRB/US | Yes (Gordon model, endogenous equity premium) | Yes (household stock wealth wps in desired consumption; elasticity 0.187 on total property wealth) and equity cost in business cost of capital (weight 0.5 in rbfi) | 10- and 30-year yields, BBB, mortgage, equity, house prices, dollar | FEDS Note 2014; pyfrbus model.xml |
| BoE COMPASS | no detailed financial sector | not stated | - | Bernanke 2024 p. 22 |

## 3. Bernanke (2024) review of the Bank of England [verified, report of 12 April 2024]
- p. 6: COMPASS "has significant shortcomings".
- p. 22: COMPASS "itself does not include detailed representations of the financial sector or the energy sector"; cannot "capture fully some key channels of monetary transmission"; "no longer used to predict the effects of changes in interest rates or asset prices on the economy"; staff use a semi-structural model for asset prices and spreads.
- p. 52: points to semi-structural models "like the Federal Reserve's FRBUS".
- Recommendation 4 (pp. 7-8, 53-54): "rich and institutionally realistic representations of the monetary transmission mechanism" and "detailed models of the financial sector".
- Does not mention equities specifically: cite for "financial sector / asset-price transmission missing".

## Research models table

| Model | Stock response | Per 1 pp [inference] | Output | Inflation | Wealth channel |
|---|---|---|---|---|---|
| Castelnuovo-Nistico 2010 | -0.2 percent per 25 bp (gap) | ~-0.8 per pp funds; ~-2 per pp of 2-year (short-lived shock) | ~-0.22 (q4), -0.12 (q8) per pp funds; ~-0.6 at q4 per pp 2-year | ~-0.05 pp impact | xi 0.13; +34 log ML; ~15-20 percent of peak output |
| Hollander-Liu 2016 | ~-6 percent impact | -2 to -8 (units unclear) | trough -0.6 at q2 vs -0.4 without equity | ~-0.3 to -0.4 | ~1/3 of peak output |
| Milani 2017 | - | - | - | - | direct small; expectations large |
| CMR 2014 | Wilshire = net worth | - | - | - | accelerator, not household wealth |

## Assessment (reviewer)
1. The blind-spot claim holds: SW, CEE, EDO, SIGMA, NY Fed DSGE have no equity price and no household stock-wealth term; FRB/US is the exception (which the paper uses). Cite C-N p. 1701 and Bernanke 2024 p. 22 (financial sector and asset prices, not equities specifically).
2. Estimated non-Ricardian DSGEs have much smaller stock responses (C-N about 1-2 percent per pp; Hollander-Liu 2-8) than the paper's 7.7 percent per pp of the 2-year yield and FRB/US's 14.5; the VAR estimates C-N cite (4-16 percent per pp) bracket 7.7.
3. C-N output about 0.6 percent at q4 per pp of the 2-year yield, same range as the paper's VAR (0.75-1.1) and FRB/US (0.46) [rough inference]; wealth channel 15-20 percent (C-N) to one-third (Hollander-Liu) of output, below the paper's 40 percent equity share of the FCI reading (different concepts).
4. Not checked: Google Scholar counts; full texts of Ifrim, Nistico 2016, Airaudo-Nistico-Zanna, Funke et al., Gilchrist-Leahy; current NY Fed DSGE vintage; Hollander-Liu rate units; EDO 2020s vintages.
