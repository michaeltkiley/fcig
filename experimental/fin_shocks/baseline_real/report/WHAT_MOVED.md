# What moved: the real baseline with the funds rate against the r*-gap version (18 Nov 2026)

Old: `fin_shocks/baseline/` (r*-gap headline, 2-year yield only). New: `fin_shocks/baseline_real/` (real headline; 2-year yield, funds rate and FCI; two steps).

All numbers are at 12 lags, per +1 pp on the 2-year yield in the window. u is the unemployment gap (pp), P the core PCE price level (%). `**` and `*` mark the 5 and 10 percent levels.

## Headline responses

| | u 12 m | u 24 m | P 24 m | P 36 m |
|---|---|---|---|---|
| **1996, old headline: r*-gap with FCI** | +0.41** | +0.45** | −0.69** | −0.94** |
| **1996, new headline: real with FCI** | +0.33** | +0.40** | −0.49** | −0.61* |
| 1996, old real with FCI (no funds rate) | +0.17* | +0.23* | −0.38** | −0.50* |
| 1996, new nominal with FCI | +0.27* | +0.40** | −0.49* | −0.68 |
| **1973, old headline: r*-gap with FCI** | +0.33** | +0.24 | −0.76** | −1.14** |
| **1973, new headline: real with FCI** | +0.19** | +0.19 | −0.56** | −0.73** |
| 1973, new nominal with FCI | +0.13 | +0.12 | −0.22 | −0.32 |

* **Size.** The new headline is smaller than the r*-gap headline. From 1996, unemployment is about 0.05 to 0.10 smaller and the price fall about a third smaller. From 1973, both are about a third smaller.
* **The funds rate.** Its effect on the real version is large. Unemployment roughly doubles at 12 and 24 months and the price fall grows by about a quarter. It is significant at the same or higher levels.
* **Nominal version.**
  * From 1996, with the funds rate, the nominal version with the FCI is now significant (u at 12 and 24 months, P at 24 months). Before, it was not significant at all. Nominal and real are almost identical from 1996.
  * From 1973 the nominal version is not significant with the FCI.
* **Rates alone.** From 1996, without the FCI, both versions show the puzzle: unemployment falls significantly and prices do not move. From 1973 the real rates alone already give a significant price fall (−0.53**), with unemployment near zero.

## Sacrifice ratio (real with FCI, 24 months)

* From 1996: multiplier −0.85, 90% set [−1.61, −0.26], so a sacrifice ratio of 1.2 (0.6 to 3.8). Old r*-gap: −0.95 [−1.99, −0.32], a ratio of 1.1.
* From 1973: multiplier −1.85 [−5.36, −0.77], a ratio of 0.5 (0.2 to 1.3). Old r*-gap: −1.49 [−2.92, −0.72].
* The nominal set from 1973 is unbounded.

## Monthly VARs (now with the funds rate)

* **Proxy VAR with the FCI:** first-stage F is 1.4 to 1.6 from 1996 and 0.2 from 1973. All sets are unbounded.
* **Proxy VAR without the FCI from 1996:** F is about 5, and unemployment falls significantly (−0.39 to −0.43).
* **Window-impact VAR, real with FCI:**
  * From 1996 it is about half the main model's responses and not significant (u +0.17, P −0.23).
  * From 1973 it is significant (u +0.23*, P −0.35*).
* **Simulation, with the real model as the true process:** the proxy VAR with the FCI is centred below the truth (median 0.17 against 0.33). Its range covers zero. Without the FCI its median has the wrong sign. The data are ordinary draws.

## Decomposition (Section 3.5)

Shares are of the 24-month variance, real model.

* **Policy-direction shocks, 1990–2026:**
  * model from 1996: u 12%, inflation 6%;
  * model from 1973: u 3%, inflation 4%.
  * The old r*-gap figures were u 18% / 9% and u 9% / 8%. All shares are smaller in the new model.
* **Measured surprises:** under 1 percent (as before).

## Robustness (12 months, real with FCI)

* **Signs:** in every test and both samples, unemployment rises and the price level falls.
* **Price level:** significant in every test from 1973. From 1996 it is significant except at 6 lags (−0.19) and with the 1985 start.
* **Unemployment:** significant except with 2020 left in (both samples), at 6 lags from 1973, and with the 1985 start.
* **Weakest test:** the 1985 start (u +0.12, P −0.07 at 12 months; nothing significant at 24 months).
* **Gone with the new list:** Kiley r* and the components. These were the old weak tests.
* **Nominal version:** much weaker in the tests, especially from 1973.

## Final section (slow-moving rates)

* **The r*-gap step** (with the funds rate) gives the largest responses: from 1996, u24 +0.49** and P24 −0.81**; from 1973, +0.39** and −0.75**.
* **The spline trend** removes significance from 1996 (u24 +0.32, P24 −0.20). From 1973 it keeps it (+0.37**, −0.50**).
* **Variance fitted by the spline** (percent; from 1996 / from 1973):
  * real FCI 32 / 92;
  * real 2-year 63 / 75;
  * real funds rate 51 / 58;
  * u gap 55 / 37;
  * inflation 20 / 63.
  * For the r*-gap FCI: 56 / 79.

## Appendix tests (real with FCI)

* **Ends 2019:** from 1996 the price level does not fall (+0.16); from 1973 it falls significantly (−0.42**).
* **Baa spread:** from 1996, P −0.61**; from 1973 nothing is significant.
* **Jarocinski–Karadi surprise:** close to the baseline in both samples.
* **1-year yield:** larger responses per +1 pp on the 1-year yield.

## Dropped from Note B in this rebuild

* the components and weights tests (D10);
* Kiley r* (D5);
* the ordinary-day figure and path B (FS-A86, FS-A81);
* the four calibrations and the Jarocinski–Karadi weights (not rebuilt in the real form; open);
* 3 lags (D9).
