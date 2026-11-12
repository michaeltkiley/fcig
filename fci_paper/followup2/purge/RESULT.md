# Purging the index of activity (Hatzius et al. 2010 style)

**Question.** Is the flow's content just activity reflected back? [Note B treats the index as a channel moving before activity.]

**Design (fixed in `common.py` before estimation).** Each input (market: 10-year yield, equity valuation, real dollar; GS: policy rate, 10-year, BBB spread, equities, dollar), in its own form at each step (nominal, real, r*-gap with the earnings-yield gap), regressed on a constant, the unemployment gap and 12-month core PCE inflation, current and 12 lags. Core PCE, not CPI: it is Note B's inflation measure and the package has no core CPI. Residuals rebuild the index with unchanged weights. Full-sample purge, and recursive purge (expanding window, first residual 1983-01: 120 observations, 27 coefficients). LPs as `followup/levelflow` (level and flow jointly, HAC 18); VAR as `lib/var.py` (12 lags, 500 block-bootstrap draws). Primary: market r*, unemployment gap. Counts: 60 LPs, 30 VARs; shared data, descriptive. Samples: LP 1976-03 (n=556, five recessions) or 1983-03 (n=472, 462 recursive; three recessions); VAR 1973-01 (n=645) or 1983-01 (n=525).

**(a) Correlations, purged vs unpurged** [verified, `out/corr.csv`, 1984+]. Level 0.73-0.89 (full) and 0.25-0.65 (recursive); 12-month change 0.70-0.79 (full) and 0.53-0.65 (recursive). Market r*: level 0.76, flow 0.75 (full); 0.25 and 0.53 (recursive). Activity explains (R2) equities 0.74-0.79, the 10-year 0.30-0.61, the dollar 0.09.

**(b) Local projections** [verified, `out/lp.csv`]. Unemployment gap, market r*, flow t (1983-03 sample): unpurged 4.7, full purge 3.4, recursive 1.7 (flow coefficient 0.29, 0.25, 0.11). The level stays near zero. Nominal and real: full 2.2, 2.4; recursive 1.6, 1.4. GS: full 3.0 to 3.7; recursive 1.8 to 2.5. On the 1976 sample, full purge: market 1.3 to 1.9; GS 2.0 to 2.6. Payroll growth: the flow vanishes under full purge for the market (t -0.1 to -1.7 on both samples), GS r* -0.6 (1976), -1.8 (1983); recursive -1.1 to -2.2 (market), -1.5 to -3.0 (GS). The recursive level turns negative on payrolls (t up to -3.4)[inference: residual noise].

**(c, d) VAR** [verified, `out/var.csv`]. Phi(12) in unemployment-gap points per unit of the index, 90% interval, 1983-01 sample:

| | unpurged | full purge | recursive |
|---|---|---|---|
| market r* | 0.57 [0.22, 0.84] | 0.32 [0.10, 0.51] | 0.19 [0.11, 0.33] |
| GS r* | 0.71 [0.31, 0.96] | 0.43 [0.17, 0.63] | 0.25 [0.15, 0.43] |

All 30 intervals exclude zero; the 1973 sample: market r* 0.65 [0.39, 0.83] against 0.41 [0.21, 0.57]; nominal and real steps in `out/var.csv`. Granger p below 0.01 at r* in every version. Phi(12) falls 35-45 percent under full purge and about 65 percent under recursive purge. Forward impetus correlation with the unpurged: 0.64-0.78 (full), 0.47-0.62 (recursive).

**Verdict: partly buttresses.** The flow is not only activity reflected back: a purged flow still predicts the unemployment gap and the VAR response keeps its sign and a 90 percent interval above zero in every version, for the market and GS alike. But a third to a half of the in-sample content is activity (Phi(12) 0.57 to 0.32 full, 0.19 recursive), and the payroll-growth result does not survive a full purge. Recursive purge is the noisiest version (short first window). Nothing here separates anticipation of activity from a causal channel [inference].

**Recommendation.** One paragraph in Section 5.2 (robustness): the purged unemployment results and the Phi(12) table, stated plainly, with the Hatzius et al. point that purging is not identification and over-removes (asset prices rightly respond to expected activity). In Note B add one sentence that the index carries both a channel and an anticipation component and that the unemployment response is the claim, not payrolls.

**Limits.** The unemployment gap uses ex-post CBO NROU and r* is ex-post Laubach-Williams, so the recursive purge is not real time in those inputs. LP t-statistics use HAC(18); no bootstrap of the purge step itself, so intervals omit its estimation error.
