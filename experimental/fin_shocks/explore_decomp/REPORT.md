# Historical and Variance Decompositions with Window-Identified Policy Shocks (Route 2)

Exploratory report, 17 Nov 2026. Folder `experimental/fin_shocks/explore_decomp/`; decisions in `DECOMP_QA.md`; every number below is in `results/` and every table is written by `07_tables.py`. Nothing in Note B's package or paper was changed. Tags: [verified] = checked in this work; [inference] = my reasoning; [recall] = from memory, not checked here.

## 1. Answers in brief

1. **Is a historical decomposition possible with window-identified surprises?** Yes, from 1996 on, by treating the measured surprises as the shock and passing them through Note B's model (Route 1). This needs no assumption beyond Note B's own. It is a lower bound on the role of policy if policy news also arrives outside the windows, and it is the full answer under Note B's premise that it does not.
2. **Do the window surprises identify how to build policy shocks from VAR innovations in other periods, back to 1973 (Route 2)?** The algebra does: the window column b and the innovation covariance Sigma give e_t = b'Sigma^-1 u_t / (b'Sigma^-1 b) in every month, daily data or not. **But the condition that makes the recipe valid, invertibility, fails in this data, and Note B's own model predicts that it fails.** The surprises explain 0.4 to 4 percent of the variance of the VAR innovations (it would be close to 100 percent under invertibility), and the recovered "policy shock" correlates 0.02 to 0.19 with the surprises in 1996-2026. The recovered series is mostly other shocks that move the 2-year yield and the FCI together: it puts a 2.5 pp tightening shock in October 2008.
3. **Variance decompositions.** Only bounds are identified. Lower bound (the shock is the measured surprise): policy surprises account for under 1 percent of the 24-month forecast-error variance of the unemployment gap and of core inflation, and 0.2 to 4 percent of the 2-year yield's, in every case. Upper bound (invertibility): 0.4 to 23 percent for unemployment, up to 10 percent for inflation; 17.6 percent [3.8, 43.7] for the r*-gap case with the FCI in the 1973 VAR. The upper bound is 17 to 116 times the lower in shock variance, so it carries little information.
4. **Daily data or monthly back to 1973?** Route 2 needs no daily data, which is why it can reach 1973. The reason it fails is not the frequency. It is that a 4-variable monthly VAR cannot separate the policy news from the much larger flow of other news that moves the same two financial variables in the same month.

## 2. Method

**System.** Note B's monthly benchmark system: unemployment gap, core PCE inflation (monthly, annual rate), the 2-year yield and the FCI in the same step (nominal, real, r*-gap; FS-A75 weights), 12 lags (3 and 6 as checks), all data in (March-December 2020 removed as a check). Three steps, each without and with the FCI.

**Data versions (D-A2).** Monthly averages from 1973: the series of Note B's own monthly equations (months before 1990 from monthly series, as in Note B's R1a). End-of-month values from 1990 (the daily FCI starts in 1990): the check. Both also from 1996.

**Impact column (D-A3, D-A5).** Window column (main): the macro entries are zero (Note B's restriction) and the yield and FCI entries are Note B's model's response in the month of the announcement per +1 pp window surprise: 0.465 and 0.489 for the month's average (r*-gap with FCI), 1.013 and 1.056 at the month's end. Proxy column P1 (comparison): Cov(z_t, u_t) over 1996-2026 months, z_t = the month's sum of Nakamura-Steinsson policy news (slope 1.000 on the 2-year window move after FS-A75).

**Recovering the shock.** Under invertibility the policy shock is a combination of the month's innovations. With Sigma = BB' and b the policy column, the policy row of B^-1 is proportional to b'Sigma^-1, so
  e_t = b'Sigma^-1 u_t / (b'Sigma^-1 b),  Var(e_t) = 1/(b'Sigma^-1 b)   (shock in units of +1 pp in the window).
Without invertibility e_t is the projection of the shock on u_t, and 1/(b'Sigma^-1 b) is an upper bound on the shock's variance [inference; Plagborg-Moller and Wolf (2022, JPE) develop the bounds formally, recall].

**Historical decomposition.** H_t = sum_{j=0}^{t-t0} Theta_j b e_{t-j} from the first month of the sample. Route 1 replaces e by the measured surprises z and, in the main version, Theta_j b by Note B's own responses (h = 0..36).

**Variance shares (D-A8).** sigma^2 sum_{j<h}(Theta_j b)_k^2 / sum_{j<h}(Theta_j Sigma Theta_j')_kk, with sigma^2 = 1/(b'Sigma^-1 b) (upper) or the mean squared monthly surprise (lower).

**Diagnostics.** (i) R^2 of z_t on the month's innovations u_t. If the policy shock is the surprise and is recoverable from u_t, this R^2 is close to 1; if u_t carried no information about z, its expected value would be about K/n = 1 percent. (ii) Correlation of the recovered shock with z. (iii) Ratio of the two shock variances. (iv) Do future innovations predict z (leads; rejection = non-invertibility, or time aggregation), and do past ones (lags; rejection = predictable surprises)? (v) The same statistics on samples simulated from Note B's estimated model, in which the policy shock is the window surprise by construction (D-A10).

**Inference.** 500 draws, moving blocks of 12 months (pre- and post-1996 drawn separately, as in Note B); the window column is held fixed (D-A7). Route 1 bands from Note B's own 500-draw block bootstrap.

## 3. Results

### 3.1 Invertibility fails, and Note B's model says it should

T1 shows the diagnostics for all 24 combinations (12 lags). In every one, the surprises' R^2 on the month's innovations is 0.4 to 3.8 percent, the recovered shock correlates 0.02 to 0.19 with the surprises, and the variance that invertibility attributes to the policy shock is 17 to 116 times the variance of the measured surprises. The bootstrap (T1b) puts the 95th percentile of the R^2 at 7.8 percent at most. Lag length and 2020 do not matter (T5). Adding the federal funds rate and the excess bond premium to the VAR raises the R^2 only to 1.5 percent (averages) and 4.9 percent (end of month) [verified, run in this session; not in the tables].

The leads test rejects at 10 percent in 6 of 24 cases, all in monthly averages (p 0.03 to 0.09), which is what time aggregation predicts (a late-month announcement shows up in next month's innovation); it does not reject for end-of-month data (p 0.11 to 0.37). It has little power here, because the surprises are small relative to the innovations. The lags test does not reject except in one case (nominal with FCI, monthly averages from 1973, p = 0.04), so the surprises are not predicted by past innovations, as Note B assumes.

T2 is the decisive check. With Note B's estimated r*-gap model with the FCI as the true process, where the policy shock is the window surprise by construction, Route 2 gives a median R^2 of 2.2 percent (averages) and 4.6 percent (end of month), a correlation of 0.11 and 0.19, and a variance ratio of 74 and 25. The data's values (1.7 and 3.5 percent; 0.10 and 0.17; 51 and 17) lie inside the simulated 90 percent ranges. **So the failure is a property of the paper's model, not a misspecification found by the test.** In Note B's model the policy news is a small share of the monthly news that moves the 2-year yield and the FCI (window surprises have a standard deviation of 0.046 pp per month; the month's 2-year yield innovation has a standard deviation of 0.23 pp at the month's end and 0.32 pp in monthly averages), and a monthly VAR in four variables cannot separate it. [inference from T2]

### 3.2 What the recovered series is

Figure 1 plots the recovered shock (r*-gap with FCI) against the measured surprises. Its largest values are in 1979-82 (plausible for policy). But it also has +2.5 in October 2008 in monthly averages (+0.83 at the month's end), a tightening in the month the Fed cut rates and financial conditions collapsed; and at the month's end -0.65 in March 2023, the month of the SVB failure. The window column says "the yield and FCI move together and the macro variables do not move within the month", and that signature is shared by risk-appetite, term-premium and crisis shocks. The proxy column (P1) does not help: its first-stage F is 0.8 to 8, and it gives the same low correlation.

### 3.3 Historical decomposition

Figure 2 (r*-gap with FCI; VAR in monthly averages from 1973) and T6. **Route 2** attributes large movements to policy: +2.1 pp of the unemployment gap at the end of 1982 (90 percent band 0.6 to 3.7, against 3.8 pp of all shocks), and +1.7 pp in October 2009 (0.8 to 2.6, against 4.2). For inflation it gives +0.6 pp at end-1980, with a band that includes zero (-0.5 to 1.9). The 2009 attribution comes from the October 2008 "tightening" shock above, so it is not a reading of monetary policy.

**Route 1** (Note B's model and the measured surprises, 1996 on) is small and episodic. The 2001-03 easing surprises lowered the unemployment gap by 0.56 pp by mid-2003 (band -1.05 to -0.05) and raised 12-month core inflation by 0.41 pp (0.13 to 0.68). The 2008 surprises lowered unemployment by about 0.3 pp in 2009. Over the 2022-24 tightening, the surprises' contribution is close to zero: -0.03 to -0.16 pp for unemployment and a 2-year yield contribution of -0.16 pp by end-2023. **The tightening of 2022-23 was not a surprise in the windows, on net. It came through the anticipated, systematic part of policy, which no shock decomposition attributes to policy shocks.** [inference from T6]

Figures 4 to 7 show the same for end-of-month data from 1990, the nominal case without the FCI, the two-month recovery (WE2) and the proxy column. All have the same pattern: Route 2 large and crisis-driven, Route 1 small.

### 3.4 Variance decomposition

T3 and Figure 3 (24 months). Lower bound: 0.0 to 0.7 percent for the unemployment gap; 0.0 to 0.5 percent for core inflation; 0.2 to 3.6 percent for the 2-year yield. With Note B's own responses rather than the VAR's, the share for unemployment in the r*-gap case with the FCI is 0.3 percent at 24 months and 0.4 percent at 36 (`results/noteb_shares.csv`). Upper bound (full sample): 0.4 to 23 percent for unemployment, 0.6 to 10 percent for inflation, 17 to 92 percent for the yield. **The policy surprises explain little of the variance of unemployment and inflation.** Small shares for identified monetary shocks are the common finding in the literature [recall; e.g. the surveys of Ramey (2016) and the high-frequency literature], and they are consistent with Note B's large responses per unit of shock: the shocks are small.

### 3.5 Alignment of intention and execution

* `note_b()` reproduces Note B's stored baseline exactly (u +0.335/+0.493/+0.431, price level -0.805 at 24 months) [verified].
* The monthly VAR with the window column does not reproduce Note B's responses (T4): in monthly averages its yield path falls to 0.60 in month 1 where Note B's rises to 1.00 (the rest of the month after the announcement), and its responses differ by up to half. Any Route 2 decomposition therefore runs on dynamics other than the paper's. The two-month variant (WE2) fixes the month-1 yield response but gives variance "shares" above 1, so its implied shock is inconsistent with the VAR's covariance (D-A6).
* End-of-month data are the cleaner version: they match Note B's units (0.92 to 1.01 of the window move) and responses more closely, but they start in 1990.
* The FS-A43 addendum's monthly VARs "from 1973" most likely started in 1990 (the end-of-month series begin then) [inference]; they are not in the paper.
* Stale text noticed, not changed: the CLAUDE.md glossary says Note B's monthly block has a "quadratic trend" (the package has none); PROJECT_MEMORY section 9 says the Note A quarterly-VAR branch is not merged (it is on `main`).

## 4. What this means for Note B, and what could be done next

* **Note B's identification does not need invertibility, and that is a strength.** The window surprise is the shock, so Note B's responses are identified whether or not a monthly VAR could recover the shock. Route 2 shows what a standard proxy VAR would need and cannot have. A sentence on this could go in the section on the monthly proxy VAR. **Your call.**
* **A Route 1 historical decomposition (1996-2026) could go in as an exhibit** (Figure 2's orange lines, or T6). Its message is that policy surprises mattered in 2001-03 and 2008 and hardly at all in 2022-24. **Your call;** it is a new result for the paper.
* **Back to 1973 needs a measured shock rather than a recovered one.** Options, each a decision:
  (a) Futures-based surprises from about 1988-90 (Kuttner; Gurkaynak-Sack-Swanson) would extend Route 1 by six to eight years [recall: start dates not checked].
  (b) Narrative shocks (Romer and Romer, extended by Wieland and Yang, about 1969-2007) as the measured shock in Note B's monthly equations before 1996. Different identification and units; they would need scaling to the 2-year yield [recall; data not in the repository].
  (c) Daily Treasury responses to target changes in 1974-79 (Cook and Hahn 1989) [recall].
* **Possible formal step:** the identified-set bounds of Plagborg-Moller and Wolf (2022) for the variance shares, to replace the two bounds here [recall; paper not read in this session].

## 5. Choices I made (the user asked me to choose and report; full list in DECOMP_QA.md)

D-A4 cases and lags; D-A5 the window column from Note B's daily model; D-A6 the two-month variant for time aggregation; D-A7 the bootstrap, with the window column fixed; D-A8 variance shares as bounds; D-A9 Route 1 with Note B's own model and bootstrap; D-A10 the simulation check. Not done: the federal funds rate and EBP extension is a quick diagnostic only (not tabulated); no new data downloaded.

## Figures

* `figures/fig1_shocks.png`: recovered shock against measured surprises.
* `figures/fig2_hd_rstar_avg.png`: historical decomposition, r*-gap with FCI, monthly averages from 1973.
* `figures/fig3_fevd.png`: variance-share bounds.
* `figures/fig4_hd_rstar_eom.png`, `fig5_hd_nom_avg.png`, `fig6_hd_rstar_avg_WE2.png`, `fig7_hd_rstar_avg_P1.png`: other versions.

## Tables
### T1. Invertibility diagnostics (12 lags, 2020 in, window column)

| case          | data     |   first-stage F |   R2 of z on u_t (%) |   corr(recovered, z) |   sd recovered (inv.) |   sd z |   variance ratio |   leads p |   lags p |
|:--------------|:---------|----------------:|---------------------:|---------------------:|----------------------:|-------:|-----------------:|----------:|---------:|
| nominal       | avg 1973 |             5.6 |                  2.4 |                 0.14 |                 0.467 |  0.046 |              102 |      0.09 |     0.55 |
| nominal       | avg 1996 |             5.2 |                  2.7 |                 0.16 |                 0.4   |  0.047 |               74 |      0.04 |     0.89 |
| nominal       | eom 1990 |             4.4 |                  2.8 |                 0.16 |                 0.241 |  0.046 |               27 |      0.12 |     0.93 |
| nominal       | eom 1996 |             4   |                  2.7 |                 0.16 |                 0.237 |  0.047 |               26 |      0.16 |     0.87 |
| nominal + FCI | avg 1973 |             0.8 |                  0.5 |                 0.03 |                 0.387 |  0.046 |               70 |      0.04 |     0.04 |
| nominal + FCI | avg 1996 |             2   |                  1.2 |                 0.07 |                 0.329 |  0.047 |               50 |      0.03 |     0.26 |
| nominal + FCI | eom 1990 |             1.9 |                  3.2 |                 0.16 |                 0.21  |  0.046 |               21 |      0.26 |     0.25 |
| nominal + FCI | eom 1996 |             1.4 |                  3.1 |                 0.14 |                 0.204 |  0.047 |               19 |      0.32 |     0.27 |
| real          | avg 1973 |             4.6 |                  1.6 |                 0.11 |                 0.498 |  0.046 |              116 |      0.1  |     0.46 |
| real          | avg 1996 |             5.2 |                  2.3 |                 0.14 |                 0.415 |  0.047 |               79 |      0.2  |     0.56 |
| real          | eom 1990 |             7.2 |                  3.6 |                 0.19 |                 0.223 |  0.046 |               23 |      0.11 |     0.87 |
| real          | eom 1996 |             6.3 |                  3.4 |                 0.18 |                 0.218 |  0.047 |               22 |      0.14 |     0.78 |
| real + FCI    | avg 1973 |             0.8 |                  0.4 |                 0.02 |                 0.404 |  0.046 |               76 |      0.06 |     0.16 |
| real + FCI    | avg 1996 |             2.4 |                  1.3 |                 0.07 |                 0.33  |  0.047 |               50 |      0.29 |     0.31 |
| real + FCI    | eom 1990 |             3.9 |                  3.5 |                 0.17 |                 0.196 |  0.046 |               18 |      0.34 |     0.31 |
| real + FCI    | eom 1996 |             2.7 |                  3.2 |                 0.15 |                 0.19  |  0.047 |               17 |      0.37 |     0.26 |
| r*-gap        | avg 1973 |             5   |                  1.7 |                 0.11 |                 0.491 |  0.046 |              113 |      0.13 |     0.53 |
| r*-gap        | avg 1996 |             5.9 |                  2.4 |                 0.14 |                 0.414 |  0.047 |               79 |      0.18 |     0.62 |
| r*-gap        | eom 1990 |             8.3 |                  3.8 |                 0.19 |                 0.22  |  0.046 |               23 |      0.12 |     0.88 |
| r*-gap        | eom 1996 |             7.5 |                  3.6 |                 0.19 |                 0.216 |  0.047 |               21 |      0.14 |     0.83 |
| r*-gap + FCI  | avg 1973 |             0.9 |                  0.4 |                 0.05 |                 0.408 |  0.046 |               78 |      0.07 |     0.21 |
| r*-gap + FCI  | avg 1996 |             3.8 |                  1.7 |                 0.1  |                 0.334 |  0.047 |               51 |      0.19 |     0.51 |
| r*-gap + FCI  | eom 1990 |             5.2 |                  3.5 |                 0.18 |                 0.196 |  0.046 |               18 |      0.2  |     0.48 |
| r*-gap + FCI  | eom 1996 |             4.2 |                  3.5 |                 0.17 |                 0.192 |  0.047 |               17 |      0.21 |     0.49 |

### T1b. Bootstrap distribution of the diagnostics (500 draws)

| case          | data     | R2 (%), median [5, 95]   | corr, median [5, 95]   |
|:--------------|:---------|:-------------------------|:-----------------------|
| nominal       | avg 1973 | 2.4 [0.7, 5.3]           | 0.13 [0.04, 0.21]      |
| nominal       | eom 1990 | 3.0 [0.7, 7.4]           | 0.16 [0.06, 0.26]      |
| nominal + FCI | avg 1973 | 1.1 [0.2, 3.7]           | 0.03 [-0.04, 0.13]     |
| nominal + FCI | eom 1990 | 3.5 [1.3, 7.6]           | 0.15 [0.04, 0.25]      |
| real          | avg 1973 | 1.7 [0.5, 3.9]           | 0.10 [0.01, 0.17]      |
| real          | eom 1990 | 3.9 [1.2, 7.8]           | 0.18 [0.09, 0.27]      |
| real + FCI    | avg 1973 | 1.0 [0.2, 2.9]           | 0.02 [-0.05, 0.10]     |
| real + FCI    | eom 1990 | 3.8 [1.6, 7.8]           | 0.16 [0.08, 0.25]      |
| r*-gap        | avg 1973 | 1.8 [0.6, 4.0]           | 0.11 [0.02, 0.17]      |
| r*-gap        | eom 1990 | 4.0 [1.5, 7.8]           | 0.18 [0.10, 0.27]      |
| r*-gap + FCI  | avg 1973 | 0.9 [0.2, 2.8]           | 0.05 [-0.03, 0.12]     |
| r*-gap + FCI  | eom 1990 | 4.0 [2.0, 7.4]           | 0.17 [0.09, 0.25]      |

### T2. Note B's model as the true process (200 simulated samples, 1996-2026) against the data

| data   | statistic              | Note B as truth: median [5, 95]   |   data 1996-2026 |
|:-------|:-----------------------|:----------------------------------|-----------------:|
| avg    | R2 of z on u_t         | 0.022 [0.005, 0.050]              |            0.017 |
| avg    | corr(recovered, z)     | 0.110 [0.027, 0.201]              |            0.097 |
| avg    | variance ratio         | 73.509 [50.803, 101.895]          |           51.1   |
| avg    | u share at 24 m, upper | 0.078 [0.012, 0.246]              |            0.039 |
| avg    | u share at 24 m, lower | 0.001 [0.000, 0.004]              |            0.001 |
| eom    | R2 of z on u_t         | 0.046 [0.017, 0.087]              |            0.035 |
| eom    | corr(recovered, z)     | 0.189 [0.099, 0.278]              |            0.167 |
| eom    | variance ratio         | 24.514 [17.088, 33.512]           |           16.8   |
| eom    | u share at 24 m, upper | 0.074 [0.013, 0.248]              |            0.038 |
| eom    | u share at 24 m, lower | 0.003 [0.001, 0.011]              |            0.002 |

### T3. Share of the 24-month forecast-error variance due to policy shocks, percent (12 lags, 2020 in)

| data     | case          |   u: lower (VAR) |   u: lower (Note B model) |   u: upper 1996- |   u: upper full | u: upper full, 90% band   |   u: upper full, P1 |   pi: lower |   pi: upper full |   yield: lower |   yield: upper full |
|:---------|:--------------|-----------------:|--------------------------:|-----------------:|----------------:|:--------------------------|--------------------:|------------:|-----------------:|---------------:|--------------------:|
| avg 1973 | nominal       |              0   |                       0.7 |              2.9 |             9.6 | [0.3, 19.6]               |                29.8 |         0   |              1   |            0.6 |                76.4 |
| avg 1973 | nominal + FCI |              0   |                       0   |              2.5 |             6.5 | [0.9, 28.0]               |                13.5 |         0   |              0.6 |            0.2 |                17.2 |
| avg 1973 | real          |              0   |                       0.3 |              1.2 |             3.5 | [0.3, 10.9]               |                26.4 |         0   |              3.4 |            0.7 |                88.6 |
| avg 1973 | real + FCI    |              0.1 |                       0   |              4.5 |            10.4 | [1.5, 31.3]               |                17.3 |         0   |              3.4 |            0.3 |                24.5 |
| avg 1973 | r*-gap        |              0   |                       0   |              0.1 |             0.4 | [0.3, 8.9]                |                19.6 |         0   |              6.4 |            0.8 |                91.6 |
| avg 1973 | r*-gap + FCI  |              0.1 |                       0.3 |              7.7 |            17.6 | [3.8, 43.7]               |                10   |         0   |              5.1 |            0.4 |                33.7 |
| eom 1990 | nominal       |              0.7 |                           |             20.3 |            23   | [6.6, 42.6]               |                22   |         0.1 |              2.1 |            3.3 |                90.1 |
| eom 1990 | nominal + FCI |              0.1 |                           |              1   |             1.2 | [0.4, 8.8]                |                12   |         0.1 |              3.4 |            1.9 |                41.9 |
| eom 1990 | real          |              0.4 |                           |              9.3 |            10.5 | [1.9, 28.9]               |                14.5 |         0.1 |              2.3 |            3.6 |                82.7 |
| eom 1990 | real + FCI    |              0   |                           |              0.4 |             0.5 | [0.3, 8.0]                |                 9.9 |         0.2 |              4.5 |            2.5 |                48.3 |
| eom 1990 | r*-gap        |              0   |                           |              1   |             1.1 | [0.5, 14.7]               |                 5.1 |         0.2 |              6   |            3.5 |                79   |
| eom 1990 | r*-gap + FCI  |              0.1 |                           |              2.1 |             2.4 | [0.5, 14.1]               |                18.4 |         0.5 |              9.8 |            2.8 |                52.1 |

### T4. Responses per +1 pp window surprise: the monthly VAR with the window column against Note B's model (same step; Note B from 1973 for avg 1973, else from 1996)

| case          | data     |   u12 VAR |   u12 Note B |   u24 VAR |   u24 Note B |   P24 VAR |   P24 Note B |   yield h=1 VAR |
|:--------------|:---------|----------:|-------------:|----------:|-------------:|----------:|-------------:|----------------:|
| nominal       | avg 1973 |     -0.15 |        -0.33 |     -0.08 |        -0.17 |      0.09 |         0.19 |            0.63 |
| nominal       | avg 1996 |     -0.56 |        -0.81 |     -0.37 |        -0.49 |      0.02 |         0.02 |            0.6  |
| nominal       | eom 1990 |     -0.8  |        -0.81 |     -0.52 |        -0.49 |      0.02 |         0.02 |            1.11 |
| nominal       | eom 1996 |     -0.91 |        -0.81 |     -0.61 |        -0.49 |      0.05 |         0.02 |            1.05 |
| nominal + FCI | avg 1973 |      0.19 |        -0.02 |      0.13 |        -0.12 |      0.03 |         0.11 |            0.59 |
| nominal + FCI | avg 1996 |     -0.11 |        -0.05 |     -0.02 |         0.16 |     -0.23 |        -0.42 |            0.56 |
| nominal + FCI | eom 1990 |     -0.19 |        -0.05 |     -0.13 |         0.16 |     -0.21 |        -0.42 |            0.98 |
| nominal + FCI | eom 1996 |     -0.14 |        -0.05 |     -0.04 |         0.16 |     -0.41 |        -0.42 |            0.89 |
| real          | avg 1973 |     -0.1  |        -0.15 |     -0.05 |        -0.08 |     -0.2  |        -0.31 |            0.61 |
| real          | avg 1996 |     -0.39 |        -0.6  |     -0.24 |        -0.33 |     -0.08 |        -0.11 |            0.46 |
| real          | eom 1990 |     -0.59 |        -0.6  |     -0.37 |        -0.33 |     -0.2  |        -0.11 |            0.96 |
| real          | eom 1996 |     -0.65 |        -0.6  |     -0.44 |        -0.33 |     -0.18 |        -0.11 |            0.91 |
| real + FCI    | avg 1973 |      0.24 |         0.1  |      0.16 |         0    |     -0.25 |        -0.39 |            0.59 |
| real + FCI    | avg 1996 |      0    |         0.09 |      0.04 |         0.23 |     -0.29 |        -0.48 |            0.46 |
| real + FCI    | eom 1990 |     -0.12 |         0.09 |     -0.1  |         0.23 |     -0.38 |        -0.48 |            0.89 |
| real + FCI    | eom 1996 |     -0.01 |         0.09 |      0.01 |         0.23 |     -0.55 |        -0.48 |            0.82 |
| r*-gap        | avg 1973 |     -0.03 |        -0.05 |     -0    |        -0.01 |     -0.3  |        -0.5  |            0.6  |
| r*-gap        | avg 1996 |     -0.14 |        -0.29 |      0.01 |        -0.07 |     -0.26 |        -0.44 |            0.47 |
| r*-gap        | eom 1990 |     -0.24 |        -0.29 |     -0.02 |        -0.07 |     -0.51 |        -0.44 |            0.97 |
| r*-gap        | eom 1996 |     -0.17 |        -0.29 |      0.03 |        -0.07 |     -0.57 |        -0.44 |            0.93 |
| r*-gap + FCI  | avg 1973 |      0.29 |         0.18 |      0.18 |         0.14 |     -0.3  |        -0.63 |            0.6  |
| r*-gap + FCI  | avg 1996 |      0.19 |         0.33 |      0.21 |         0.49 |     -0.41 |        -0.8  |            0.51 |
| r*-gap + FCI  | eom 1990 |      0.23 |         0.33 |      0.28 |         0.49 |     -0.71 |        -0.8  |            0.96 |
| r*-gap + FCI  | eom 1996 |      0.36 |         0.33 |      0.36 |         0.49 |     -0.84 |        -0.8  |            0.93 |

### T5. r*-gap with FCI: all versions

| data     |   lags | 2020   | column   |   R2 (%) |   corr |   variance ratio | u share 24 m, upper (%)   |
|:---------|-------:|:-------|:---------|---------:|-------:|-----------------:|:--------------------------|
| avg 1973 |      3 | in     | WE       |      0.8 |   0.05 |               75 | 5.2                       |
| avg 1973 |      3 | in     | P1       |      0.8 |   0.08 |              100 | 3.5                       |
| avg 1973 |      3 | in     | WE2      |      0.8 |   0.07 |               42 | n.a.                      |
| avg 1973 |      6 | in     | WE       |      0.4 |   0.03 |               75 | 11.0                      |
| avg 1973 |      6 | in     | P1       |      0.4 |   0.05 |              102 | 0.8                       |
| avg 1973 |      6 | in     | WE2      |      0.4 |   0.07 |               43 | n.a.                      |
| avg 1973 |     12 | in     | WE       |      0.4 |   0.05 |               78 | 17.6                      |
| avg 1973 |     12 | dummy  | WE       |      0.4 |   0.04 |               75 | 33.1                      |
| avg 1973 |     12 | in     | P1       |      0.4 |   0.05 |              101 | 10.0                      |
| avg 1973 |     12 | dummy  | P1       |      0.4 |   0.06 |               61 | 10.8                      |
| avg 1973 |     12 | in     | WE2      |      0.4 |   0.08 |               46 | n.a.                      |
| avg 1973 |     12 | dummy  | WE2      |      0.4 |   0.06 |               44 | n.a.                      |
| avg 1996 |      3 | in     | WE       |      2.4 |   0.12 |               66 | 2.1                       |
| avg 1996 |      3 | in     | P1       |      2.4 |   0.15 |               88 | 1.9                       |
| avg 1996 |      3 | in     | WE2      |      2.4 |   0.16 |               35 | n.a.                      |
| avg 1996 |      6 | in     | WE       |      2.1 |   0.11 |               58 | 4.6                       |
| avg 1996 |      6 | in     | P1       |      2.1 |   0.14 |               76 | 0.3                       |
| avg 1996 |      6 | in     | WE2      |      2.1 |   0.16 |               30 | n.a.                      |
| avg 1996 |     12 | in     | WE       |      1.7 |   0.1  |               51 | 3.9                       |
| avg 1996 |     12 | dummy  | WE       |      1.6 |   0.11 |               47 | 5.7                       |
| avg 1996 |     12 | in     | P1       |      1.7 |   0.13 |               59 | 2.2                       |
| avg 1996 |     12 | dummy  | P1       |      1.6 |   0.13 |               49 | 1.1                       |
| avg 1996 |     12 | in     | WE2      |      1.7 |   0.14 |               26 | n.a.                      |
| avg 1996 |     12 | dummy  | WE2      |      1.6 |   0.17 |               24 | n.a.                      |
| eom 1990 |      3 | in     | WE       |      4.2 |   0.2  |               21 | 1.4                       |
| eom 1990 |      3 | in     | P1       |      4.2 |   0.2  |               19 | 5.9                       |
| eom 1990 |      6 | in     | WE       |      3.9 |   0.19 |               20 | 2.5                       |
| eom 1990 |      6 | in     | P1       |      3.9 |   0.19 |               17 | 11.3                      |
| eom 1990 |     12 | in     | WE       |      3.5 |   0.18 |               18 | 2.4                       |
| eom 1990 |     12 | dummy  | WE       |      4   |   0.18 |               17 | 5.1                       |
| eom 1990 |     12 | in     | P1       |      3.5 |   0.18 |               14 | 18.4                      |
| eom 1990 |     12 | dummy  | P1       |      4   |   0.2  |               11 | 4.3                       |
| eom 1996 |      3 | in     | WE       |      4.1 |   0.2  |               21 | 1.2                       |
| eom 1996 |      3 | in     | P1       |      4.1 |   0.2  |               19 | 5.9                       |
| eom 1996 |      6 | in     | WE       |      3.7 |   0.18 |               19 | 3.3                       |
| eom 1996 |      6 | in     | P1       |      3.7 |   0.19 |               16 | 14.5                      |
| eom 1996 |     12 | in     | WE       |      3.5 |   0.17 |               17 | 3.8                       |
| eom 1996 |     12 | dummy  | WE       |      4.2 |   0.19 |               16 | 6.2                       |
| eom 1996 |     12 | in     | P1       |      3.5 |   0.18 |               12 | 24.3                      |
| eom 1996 |     12 | dummy  | P1       |      4.2 |   0.2  |                9 | 9.1                       |

### T6. Historical decomposition at selected months, r*-gap with FCI (Route 2: VAR in monthly averages from 1973; Route 1: Note B's model from 1996 and the measured surprises; 90% bands)

| month   |   u: all shocks | u: Route 2          | u: Route 1           |   infl. 12m: all | infl.: Route 2      | infl.: Route 1       |
|:--------|----------------:|:--------------------|:---------------------|-----------------:|:--------------------|:---------------------|
| 1975-05 |            2.35 | 0.37 [-0.23, 1.30]  |                      |             3.18 | -0.12 [-0.55, 0.14] |                      |
| 1980-12 |            0.05 | -0.61 [-1.61, 0.80] |                      |             5.59 | 0.64 [-0.45, 1.91]  |                      |
| 1982-12 |            3.8  | 2.08 [0.60, 3.70]   |                      |             2.27 | -0.95 [-2.21, 0.52] |                      |
| 1987-12 |           -0.97 | -0.17 [-1.01, 0.91] |                      |             0.45 | -0.03 [-1.83, 1.00] |                      |
| 1992-06 |            1.45 | -0.47 [-1.15, 0.19] |                      |            -0.03 | 0.23 [-0.77, 1.04]  |                      |
| 2001-12 |           -0.1  | -0.20 [-1.08, 0.44] | -0.17 [-0.42, 0.06]  |            -1.21 | 0.32 [-0.38, 1.39]  | 0.19 [0.10, 0.27]    |
| 2003-06 |            0.53 | 0.40 [-0.41, 1.16]  | -0.56 [-1.05, -0.05] |            -1.41 | -0.07 [-0.83, 0.92] | 0.41 [0.13, 0.68]    |
| 2009-10 |            4.24 | 1.71 [0.75, 2.63]   | -0.31 [-0.57, -0.06] |            -1.69 | -0.69 [-1.44, 0.15] | 0.26 [0.11, 0.39]    |
| 2014-12 |            0.12 | -0.08 [-0.94, 0.54] | 0.02 [0.00, 0.04]    |            -1.57 | -0.14 [-1.26, 0.74] | -0.03 [-0.05, -0.01] |
| 2019-12 |           -1.59 | 0.24 [-0.39, 0.99]  | 0.01 [-0.03, 0.04]   |            -1.38 | -0.31 [-1.18, 0.46] | 0.02 [0.00, 0.03]    |
| 2022-12 |           -1.66 | -0.57 [-1.57, 0.15] | -0.03 [-0.12, 0.06]  |             2.03 | 0.39 [-0.29, 1.15]  | 0.01 [-0.00, 0.03]   |
| 2023-12 |           -1.35 | -0.30 [-1.07, 0.46] | -0.07 [-0.14, -0.00] |             0.26 | 0.29 [-0.31, 1.04]  | 0.03 [-0.00, 0.05]   |
| 2024-12 |           -1.03 | -0.25 [-0.89, 0.43] | -0.16 [-0.30, -0.03] |            -0.05 | 0.26 [-0.29, 1.06]  | 0.15 [0.07, 0.21]    |
| 2026-09 |           -0.91 | -0.19 [-0.74, 0.41] | -0.05 [-0.14, 0.07]  |             0.16 | 0.15 [-0.40, 0.80]  | 0.03 [-0.05, 0.11]   |
