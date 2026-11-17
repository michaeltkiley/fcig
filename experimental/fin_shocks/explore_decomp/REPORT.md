# Note B from 1973, and Policy Shocks Recovered from Daily and Monthly Innovations (Route 2)

Exploratory report, second version, 17 Nov 2026. It replaces the first version. Folder `experimental/fin_shocks/explore_decomp/`; decisions in `DECOMP_QA.md` (D-A1 to D-A14). Note B's package and paper were not changed; Note B's code is used read-only. Every number below is in `results_core/` or `results_route2/`, and every table is written by a script (`C_core_tables.py`, `E_tables.py`, `07_tables.py`). Tags: [verified] = checked in this work; [inference] = my reasoning; [recall] = from memory, not checked here.

## Summary

**Part A, the core paper results from 1973.** Note B's model with the monthly equations from 1973 gives the paper's price result in the real and r*-gap versions: the price level falls 0.63 percent after two years in the r*-gap version with the FCI (90 percent interval -0.89 to -0.22), against 0.80 from 1996. It does not give the paper's unemployment result at two years. From 1973 the FCI raises the unemployment response at 12 months (by 0.31, 0.26 and 0.23 pp in the three versions; the first two significant at 5 percent), but at 24 months the rise is 0.06 to 0.14 pp and not significant; from 1996 it is 0.56 to 0.65 pp and significant. With 3 and 6 lags from 1973 the FCI's effect on unemployment at 24 months is between -0.11 and +0.03 and never significant. The paper's monthly window-impact VAR in monthly averages from 1973 has unemployment rising significantly with the FCI (r*-gap: +0.29 at 12 months, +0.18 at 24) and prices falling (-0.30 at 24, -0.41 at 36). The proxy VAR with the FCI is uninformative from 1973 (first-stage F 0.9). Without the FCI, the nominal version from 1973 still has the unemployment puzzle (Note B's model: -0.33 pp at 12 months; proxy VAR: -0.25), and the r*-gap version does not (-0.05).

**Part B, Route 2.** The policy shock is recovered on every weekday from 1990 from Note B's daily innovations (the 2-year yield and FCI innovations projected on the window direction), and in every month of 1974-1989 from the monthly VAR's innovations, and traced through Note B's model.
* The daily shocks are informative: on announcement days they correlate 0.66 with the measured window surprises (slope 0.82).
* **The measured surprises have a tiny variance share,** as expected: 0.1 percent of the unemployment gap's 24-month forecast-error variance, 0.2 percent of core inflation's, 3 percent of the 2-year yield's and 2 percent of the FCI's (r*-gap with FCI, 1990-2026).
* **The recovered policy-direction shocks matter much more, and almost all of it comes from days without an announcement.** With Note B's model from 1973 they account for 1.3 percent of unemployment [0.1, 5.8], 4.6 percent of core inflation [1.0, 9.1], 64 percent of the 2-year yield [33, 88] and 45 percent of the FCI [18, 70] over 1990-2026; with Note B's baseline model (from 1996), for 8.6 percent of unemployment and 9.5 percent of core inflation. Announcement days account for 0.1 and 0.2 percent of those.
* **In 1974-1989** (monthly-recovered shocks, scaled to the daily shocks' size over the overlap): 4.6 percent of unemployment [0.4, 21.6], 7.8 percent of core inflation [2.1, 15.8], 56 percent of the 2-year yield and 37 percent of the FCI with the 1973 model.
* **History (r*-gap with FCI):** policy-direction shocks were easing on net in 1979-80 (r*-gap yield -1.0 pp; 12-month core inflation +1.3 pp by end-1980), tightening in 1982-84 (yield +3.7 pp in mid-1982), easing in 2001-03 and 2019-21 (core inflation +0.8 pp by mid-2021 and +1.0 by end-2022), and tightening in 2022-24 (yield +1.0 pp by end-2023). With the baseline model the 2020-21 easing lowered the unemployment gap by 1.1 pp in mid-2021 and the 2022-24 tightening raised it by 0.7 pp by end-2024 and lowered core inflation by 0.7 pp.

## Part A. The core paper results from 1973

### A.1 Why this was needed

The paper's monthly VAR benchmarks use end-of-month series, and the end-of-month r*-gap and real yields and the FCI exist only from 1990 (the daily FCI starts in 1990; the nominal end-of-month yield exists from 1976). Earlier monthly VAR runs from 1973 (FS-A43 addendum, 10 Nov) did start in 1973: at that time the monthly VARs used monthly averages; FS-A48 (same day) switched them to end-of-month values and dropped the 1973 version because no end-of-month FCI exists before 1990 [verified in FS_QA.md; correcting my earlier inference that they started in 1990]. The A2 monthly-average 1973 results below reproduce those earlier results (Section A.4). Note B's own model already allowed a 1973 start (monthly averages, months before 1990 from monthly series), but only the r*-gap pair had been run (robustness R1a). Here: (A1) Note B's model from 1973 in all three versions, with and without the FCI, next to the 1996 baseline, 3/6/12 lags, 500 paired block-bootstrap draws; (A2) the paper's monthly VAR benchmarks (proxy VAR, window-impact VAR, Cholesky) from 1973 in monthly averages and from 1990 at the end of the month, next to the paper's 1996 versions.

**Reproduction.** The 1996 runs of A1 reproduce the paper's stored results to the last digit in all six cases, and the existing 1973 r*-gap pair too [verified: maximum absolute difference 0.0000]. The 1996 end-of-month monthly VARs of A2 reproduce the paper's stored values exactly (proxy VAR F 4.4378, unemployment at 12 months 0.9457; window-impact VAR 0.3276) [verified].

### A.2 Note B's model from 1973 (Table A1, Figure A1)

| r*-gap, 12 lags | from 1996 | from 1973 |
|---|---|---|
| Unemployment at 24 m, yield alone | -0.07 | -0.01 |
| Unemployment at 24 m, yield + FCI | +0.49* | +0.14 |
| Difference (paired) | +0.56** [0.10, 1.05] | +0.14 [-0.13, 0.37] |
| Price level at 24 m, yield alone | -0.44** | -0.50** |
| Price level at 24 m, yield + FCI | -0.80** | -0.63** |
| Difference (paired) | -0.37** [-0.77, -0.07] | -0.13 [-0.27, 0.04] |

* **Prices.** From 1973 the price level falls in the real and r*-gap versions with and without the FCI, significantly; the FCI adds a further fall that is not significant. In the nominal version prices do not fall from 1973 (+0.11 with the FCI at 24 months).
* **Unemployment.** From 1973 the FCI raises the unemployment response at 12 months in every version (+0.31**, +0.26**, +0.23 [-0.01, 0.43]); at 24 and 36 months the difference is small and not significant. The response with the FCI is never significantly positive from 1973. With 6 and 3 lags the FCI's effect on unemployment at 24 months is between -0.11 and +0.03 in the three versions and never significant (r*-gap: +0.03 and -0.04).
* **Puzzle without the FCI.** From 1973 the nominal version alone still has unemployment falling (-0.33** at 12 months); the real version less (-0.15*); the r*-gap version not at all (-0.05).
* **Where the FCI effect comes from (Table A1b).** The extra initial movement of the FCI (path A minus B) raises unemployment at 24 months by +0.20 to +0.24, significant from 1973 as from 1996 (+0.44 to +0.46). From 1973 the FCI as it ordinarily moves with the yield (B minus C) lowers it (-0.10 to -0.14), which offsets part of the first effect; from 1996 it raises it. The ordinary loading is the same in both (0.27-0.28; it comes from the daily block, estimated from 1996).
* **Alignment with the draft.** Section 4.1 of the draft says that "with 2020 dropped or the start moved to 1973, the results are those of the baseline". For prices this holds. For the unemployment result of the abstract and introduction (adding the FCI raises unemployment after 24 months), it does not: from 1973 the shift is 0.14 and not significant at 24 months, though significant at 12. **This is for you to decide;** I changed nothing.

### A.3 The monthly VAR benchmarks from 1973 (Table A2)

* **Window-impact VAR, r*-gap with FCI.** Monthly averages from 1973: unemployment +0.29 [0.13, 0.41] at 12 months and +0.18 [0.02, 0.28] at 24; price level -0.30 [-0.51, -0.07] at 24 and -0.41 at 36. End of month from 1991: +0.23 and +0.28 (not significant), price level -0.71 [-1.08, -0.17]. The paper's 1996 version: +0.33, +0.30, -0.77. All three agree in sign with the paper. In monthly averages the VAR's yield path falls back faster than Note B's (0.60 in the month after the announcement against 1.00), so the monthly-average version understates the size [verified, first-round Table T4].
* **Proxy VAR with the FCI.** From 1973 in monthly averages the first stage has F = 0.9 and the 90 percent sets are unbounded. At the end of the month from 1991, F = 5.1; unemployment +0.76 at 12 months (set -0.10 to 4.20) and price level -1.09 at 24 (-3.27 to -0.12).
* **Without the FCI.** The nominal proxy VAR from 1973 has unemployment falling, significantly (-0.25 [-0.58, -0.07] at 12 months); the Cholesky VAR -0.34 [-0.63, 0.04]. The puzzle is in the long sample too, smaller than from 1990 (-0.76, -0.81). r*-gap without the FCI from 1973: unemployment about zero, price level -0.30 to -0.65 at 24 months.
* Units: per +1 pp in the window (proxy VAR rescaled from the yield measure by the window column; Cholesky per +1 pp yield innovation).

### A.4 Monthly averages against end of month: data type or sample? (Table A3)

The earlier 1973 monthly VARs (FS-A43) were genuine 1973 runs in **monthly averages**; FS-A48 then moved the monthly VARs to end-of-month values (Bauer and Swanson's convention) and dropped 1973, because an end-of-month FCI exists only from 1990. Two things therefore differ between the paper's monthly VARs and the 1973 ones: the data type and the sample. Table A3 runs both data types on the same samples (from 1991 and from 1996) and monthly averages from 1973. The monthly-average 1973 results reproduce the FS-A43 numbers (proxy VAR with FCI F 0.8-0.9; without the FCI, unemployment -0.57, -0.56, -0.46 per pp of the monthly-average yield = -0.25, -0.26, -0.21 per pp in the window here; window-impact r*-gap price level -0.30 at 24 months) [verified against FS_QA FS-A43 addendum].

* **Prices: mostly the data type.** r*-gap with FCI, window-impact VAR, 24 months: end of month from 1991 -0.71, monthly averages from 1991 -0.37, monthly averages from 1973 -0.30. Averaging halves the response on the same sample; the longer sample changes little.
* **The proxy VAR's collapse from 1973: mostly the sample.** First-stage F with the FCI: 5.1 (end of month, 1991), 4.0 (monthly averages, 1991), 0.9 (monthly averages, 1973). The instrument has no months before 1996, and the longer sample's innovations dilute it.
* **The unemployment puzzle without the FCI: both.** Nominal, proxy VAR, 12 months: -0.80 (end of month, 1991), -0.51 (averages, 1991), -0.25 (averages, 1973); Cholesky -0.84, -1.08, -0.34. The long sample weakens the puzzle most.
* **Why averaging shrinks the effects.** In monthly averages the announcement moves this month's average yield by only 0.47 (the rest of the month), and the monthly VAR does not reproduce the further rise next month (0.60 against Note B's 1.00), so the policy move it propagates is about half as large (FS-A48 (2) found the same on 1996 data).
* **Note B's own model is not affected by this.** It simulates the daily path and averages it into its monthly equations, so its 1973 and 1996 results (Part A.2) use the same data type; the weaker unemployment result from 1973 is a sample effect.

### Table A3. Monthly VAR benchmarks by data type and sample (12 lags; per +1 pp window surprise; 90% intervals)

| yield         | method            | data                   |   F | u12                   | u24                   | P24                   | P36                   |
|:--------------|:------------------|:-----------------------|----:|:----------------------|:----------------------|:----------------------|:----------------------|
| nominal       | proxy VAR         | monthly avg from 1974  | 5.5 | -0.25 [-0.58, -0.07]  | -0.13 [-0.30, -0.04]  | +0.04 [-1.22, +1.16]  | +0.04 [-1.63, +1.52]  |
| nominal       | window-impact VAR | monthly avg from 1974  | 5.5 | -0.15 [-0.28, +0.02]  | -0.08 [-0.16, +0.05]  | +0.09 [-0.10, +0.28]  | +0.11 [-0.18, +0.42]  |
| nominal       | Cholesky          | monthly avg from 1974  | 5.5 | -0.34 [-0.63, +0.04]  | -0.17 [-0.36, +0.11]  | +0.20 [-0.23, +0.64]  | +0.25 [-0.41, +0.95]  |
| nominal       | proxy VAR         | monthly avg from 1991  | 5   | -0.51 [-0.80, -0.29]  | -0.32 [-0.55, -0.12]  | -0.02 [-0.83, +0.71]  | -0.11 [-1.07, +0.73]  |
| nominal       | window-impact VAR | monthly avg from 1991  | 5   | -0.48 [-0.70, -0.19]  | -0.30 [-0.46, -0.01]  | +0.01 [-0.19, +0.22]  | -0.07 [-0.37, +0.25]  |
| nominal       | Cholesky          | monthly avg from 1991  | 5   | -1.08 [-1.60, -0.42]  | -0.69 [-1.04, -0.01]  | +0.02 [-0.44, +0.50]  | -0.17 [-0.83, +0.56]  |
| nominal       | proxy VAR         | end of month from 1991 | 4.3 | -0.80 [-1.24, -0.44]  | -0.50 [-0.89, -0.12]  | -0.06 [-1.67, +1.23]  | -0.22 [-2.12, +1.28]  |
| nominal       | window-impact VAR | end of month from 1991 | 4.3 | -0.80 [-1.17, -0.32]  | -0.52 [-0.79, -0.05]  | +0.02 [-0.30, +0.38]  | -0.12 [-0.58, +0.40]  |
| nominal       | Cholesky          | end of month from 1991 | 4.3 | -0.84 [-1.23, -0.33]  | -0.54 [-0.83, -0.05]  | +0.02 [-0.32, +0.40]  | -0.12 [-0.61, +0.42]  |
| nominal       | proxy VAR         | monthly avg from 1996  | 5.1 | -0.56 [-0.85, -0.30]  | -0.37 [-0.63, -0.11]  | -0.03 [-0.90, +0.70]  | -0.14 [-1.14, +0.69]  |
| nominal       | window-impact VAR | monthly avg from 1996  | 5.1 | -0.54 [-0.84, -0.24]  | -0.37 [-0.61, -0.02]  | +0.02 [-0.25, +0.29]  | -0.08 [-0.48, +0.29]  |
| nominal       | Cholesky          | monthly avg from 1996  | 5.1 | -1.23 [-1.91, -0.55]  | -0.84 [-1.38, -0.05]  | +0.04 [-0.58, +0.66]  | -0.18 [-1.09, +0.65]  |
| nominal       | proxy VAR         | end of month from 1996 | 4.5 | -0.86 [-1.31, -0.40]  | -0.58 [-1.03, -0.05]  | -0.07 [-1.75, +1.20]  | -0.25 [-2.17, +1.20]  |
| nominal       | window-impact VAR | end of month from 1996 | 4.5 | -0.90 [-1.41, -0.35]  | -0.63 [-0.99, -0.08]  | +0.06 [-0.39, +0.49]  | -0.09 [-0.70, +0.53]  |
| nominal       | Cholesky          | end of month from 1996 | 4.5 | -0.95 [-1.48, -0.37]  | -0.66 [-1.04, -0.09]  | +0.07 [-0.41, +0.52]  | -0.10 [-0.74, +0.56]  |
| nominal + FCI | proxy VAR         | monthly avg from 1974  | 0.8 | +0.14 [unbounded]     | +0.09 [unbounded]     | -0.40 [unbounded]     | -0.57 [unbounded]     |
| nominal + FCI | window-impact VAR | monthly avg from 1974  | 0.8 | +0.19 [+0.06, +0.35]  | +0.13 [+0.01, +0.24]  | +0.03 [-0.27, +0.19]  | +0.06 [-0.37, +0.29]  |
| nominal + FCI | proxy VAR         | monthly avg from 1991  | 2.1 | -0.34 [unbounded]     | -0.33 [unbounded]     | -0.18 [unbounded]     | -0.21 [unbounded]     |
| nominal + FCI | window-impact VAR | monthly avg from 1991  | 2.1 | -0.09 [-0.32, +0.15]  | -0.07 [-0.27, +0.16]  | -0.13 [-0.33, +0.11]  | -0.20 [-0.49, +0.14]  |
| nominal + FCI | proxy VAR         | end of month from 1991 | 1.9 | +0.47 [unbounded]     | +0.32 [unbounded]     | -0.65 [unbounded]     | -0.71 [unbounded]     |
| nominal + FCI | window-impact VAR | end of month from 1991 | 1.9 | -0.19 [-0.56, +0.16]  | -0.13 [-0.45, +0.23]  | -0.21 [-0.54, +0.20]  | -0.33 [-0.77, +0.23]  |
| nominal + FCI | proxy VAR         | monthly avg from 1996  | 1.9 | -0.38 [unbounded]     | -0.35 [unbounded]     | -0.20 [unbounded]     | -0.22 [unbounded]     |
| nominal + FCI | window-impact VAR | monthly avg from 1996  | 1.9 | -0.09 [-0.41, +0.20]  | -0.04 [-0.33, +0.29]  | -0.22 [-0.53, +0.11]  | -0.35 [-0.78, +0.10]  |
| nominal + FCI | proxy VAR         | end of month from 1996 | 1.6 | +0.65 [unbounded]     | +0.46 [unbounded]     | -0.93 [unbounded]     | -1.06 [unbounded]     |
| nominal + FCI | window-impact VAR | end of month from 1996 | 1.6 | -0.14 [-0.62, +0.40]  | -0.09 [-0.54, +0.47]  | -0.36 [-0.88, +0.09]  | -0.57 [-1.25, +0.12]  |
| real          | proxy VAR         | monthly avg from 1974  | 4.6 | -0.26 [-0.97, -0.05]  | -0.13 [-0.52, -0.03]  | -0.23 [-1.98, +1.31]  | -0.34 [-2.65, +1.69]  |
| real          | window-impact VAR | monthly avg from 1974  | 4.6 | -0.10 [-0.21, +0.04]  | -0.05 [-0.15, +0.08]  | -0.20 [-0.34, +0.03]  | -0.30 [-0.51, +0.05]  |
| real          | Cholesky          | monthly avg from 1974  | 4.6 | -0.22 [-0.47, +0.09]  | -0.12 [-0.32, +0.17]  | -0.45 [-0.75, +0.07]  | -0.66 [-1.12, +0.12]  |
| real          | proxy VAR         | monthly avg from 1991  | 5.7 | -0.41 [-0.78, -0.21]  | -0.22 [-0.52, +0.00]  | -0.20 [-1.08, +0.50]  | -0.31 [-1.34, +0.48]  |
| real          | window-impact VAR | monthly avg from 1991  | 5.7 | -0.36 [-0.56, -0.12]  | -0.21 [-0.39, +0.05]  | -0.10 [-0.29, +0.14]  | -0.17 [-0.45, +0.14]  |
| real          | Cholesky          | monthly avg from 1991  | 5.7 | -0.79 [-1.24, -0.27]  | -0.46 [-0.85, +0.11]  | -0.21 [-0.63, +0.30]  | -0.38 [-0.99, +0.30]  |
| real          | proxy VAR         | end of month from 1991 | 7.2 | -0.68 [-1.18, -0.40]  | -0.42 [-0.84, -0.13]  | -0.25 [-1.29, +0.79]  | -0.41 [-1.64, +0.76]  |
| real          | window-impact VAR | end of month from 1991 | 7.2 | -0.59 [-1.03, -0.17]  | -0.37 [-0.73, +0.11]  | -0.20 [-0.60, +0.19]  | -0.34 [-0.90, +0.23]  |
| real          | Cholesky          | end of month from 1991 | 7.2 | -0.61 [-1.05, -0.18]  | -0.38 [-0.74, +0.11]  | -0.21 [-0.62, +0.19]  | -0.35 [-0.91, +0.24]  |
| real          | proxy VAR         | monthly avg from 1996  | 5.2 | -0.40 [-0.80, -0.14]  | -0.22 [-0.56, +0.11]  | -0.26 [-1.37, +0.48]  | -0.38 [-1.67, +0.45]  |
| real          | window-impact VAR | monthly avg from 1996  | 5.2 | -0.39 [-0.67, -0.14]  | -0.25 [-0.51, +0.02]  | -0.07 [-0.34, +0.19]  | -0.15 [-0.49, +0.20]  |
| real          | Cholesky          | monthly avg from 1996  | 5.2 | -0.85 [-1.47, -0.31]  | -0.55 [-1.13, +0.04]  | -0.17 [-0.74, +0.42]  | -0.33 [-1.08, +0.45]  |
| real          | proxy VAR         | end of month from 1996 | 6.9 | -0.71 [-1.26, -0.35]  | -0.47 [-0.97, -0.07]  | -0.28 [-1.47, +0.84]  | -0.45 [-1.81, +0.79]  |
| real          | window-impact VAR | end of month from 1996 | 6.9 | -0.65 [-1.15, -0.16]  | -0.46 [-0.92, +0.02]  | -0.16 [-0.66, +0.32]  | -0.29 [-0.96, +0.36]  |
| real          | Cholesky          | end of month from 1996 | 6.9 | -0.66 [-1.17, -0.17]  | -0.47 [-0.94, +0.02]  | -0.16 [-0.67, +0.33]  | -0.30 [-0.98, +0.37]  |
| real + FCI    | proxy VAR         | monthly avg from 1974  | 0.8 | +0.16 [unbounded]     | +0.07 [unbounded]     | -0.78 [unbounded]     | -1.10 [unbounded]     |
| real + FCI    | window-impact VAR | monthly avg from 1974  | 0.8 | +0.24 [+0.07, +0.37]  | +0.16 [-0.01, +0.26]  | -0.25 [-0.45, +0.00]  | -0.33 [-0.63, +0.05]  |
| real + FCI    | proxy VAR         | monthly avg from 1991  | 3.1 | -0.19 [-0.84, +3.17]  | -0.20 [-0.84, +2.20]  | -0.33 [-4.69, +0.80]  | -0.35 [-4.85, +1.07]  |
| real + FCI    | window-impact VAR | monthly avg from 1991  | 3.1 | -0.04 [-0.28, +0.19]  | -0.03 [-0.26, +0.18]  | -0.21 [-0.41, +0.05]  | -0.26 [-0.57, +0.08]  |
| real + FCI    | proxy VAR         | end of month from 1991 | 3.9 | +0.43 [-0.30, +6.19]  | +0.28 [-0.36, +4.99]  | -0.72 [-4.31, +0.44]  | -0.77 [-4.53, +0.64]  |
| real + FCI    | window-impact VAR | end of month from 1991 | 3.9 | -0.12 [-0.57, +0.24]  | -0.10 [-0.50, +0.27]  | -0.38 [-0.73, +0.09]  | -0.48 [-0.97, +0.14]  |
| real + FCI    | proxy VAR         | monthly avg from 1996  | 2.4 | -0.17 [unbounded]     | -0.21 [unbounded]     | -0.39 [unbounded]     | -0.36 [unbounded]     |
| real + FCI    | window-impact VAR | monthly avg from 1996  | 2.4 | +0.00 [-0.31, +0.24]  | +0.02 [-0.28, +0.27]  | -0.26 [-0.58, +0.01]  | -0.34 [-0.75, +0.04]  |
| real + FCI    | proxy VAR         | end of month from 1996 | 3   | +0.69 [-0.21, +23.91] | +0.47 [-0.32, +19.42] | -1.01 [-15.78, +0.22] | -1.07 [-16.27, +0.33] |
| real + FCI    | window-impact VAR | end of month from 1996 | 3   | -0.02 [-0.57, +0.53]  | -0.04 [-0.57, +0.46]  | -0.49 [-1.05, -0.00]  | -0.63 [-1.33, +0.02]  |
| r*-gap        | proxy VAR         | monthly avg from 1974  | 5   | -0.21 [-0.93, -0.00]  | -0.09 [-0.45, +0.01]  | -0.33 [-1.73, +1.17]  | -0.51 [-2.36, +1.46]  |
| r*-gap        | window-impact VAR | monthly avg from 1974  | 5   | -0.03 [-0.15, +0.10]  | -0.00 [-0.08, +0.11]  | -0.30 [-0.44, -0.05]  | -0.45 [-0.68, -0.06]  |
| r*-gap        | Cholesky          | monthly avg from 1974  | 5   | -0.07 [-0.32, +0.22]  | -0.00 [-0.18, +0.25]  | -0.65 [-0.97, -0.11]  | -0.98 [-1.48, -0.12]  |
| r*-gap        | proxy VAR         | monthly avg from 1991  | 6.1 | -0.27 [-0.73, -0.05]  | -0.06 [-0.40, +0.14]  | -0.36 [-1.14, +0.29]  | -0.50 [-1.42, +0.21]  |
| r*-gap        | window-impact VAR | monthly avg from 1991  | 6.1 | -0.17 [-0.41, +0.05]  | -0.02 [-0.24, +0.18]  | -0.24 [-0.44, -0.01]  | -0.35 [-0.63, -0.06]  |
| r*-gap        | Cholesky          | monthly avg from 1991  | 6.1 | -0.36 [-0.90, +0.12]  | -0.03 [-0.52, +0.40]  | -0.53 [-0.95, -0.03]  | -0.77 [-1.38, -0.13]  |
| r*-gap        | proxy VAR         | end of month from 1991 | 8.2 | -0.40 [-1.00, -0.09]  | -0.12 [-0.58, +0.16]  | -0.52 [-1.40, +0.47]  | -0.75 [-1.76, +0.34]  |
| r*-gap        | window-impact VAR | end of month from 1991 | 8.2 | -0.24 [-0.68, +0.16]  | -0.02 [-0.45, +0.37]  | -0.51 [-0.93, -0.09]  | -0.71 [-1.25, -0.13]  |
| r*-gap        | Cholesky          | end of month from 1991 | 8.2 | -0.24 [-0.68, +0.16]  | -0.02 [-0.45, +0.37]  | -0.51 [-0.93, -0.09]  | -0.71 [-1.25, -0.13]  |
| r*-gap        | proxy VAR         | monthly avg from 1996  | 5.7 | -0.22 [-0.70, +0.04]  | -0.03 [-0.39, +0.24]  | -0.41 [-1.33, +0.25]  | -0.55 [-1.59, +0.16]  |
| r*-gap        | window-impact VAR | monthly avg from 1996  | 5.7 | -0.15 [-0.44, +0.09]  | -0.02 [-0.26, +0.18]  | -0.24 [-0.47, +0.00]  | -0.34 [-0.65, -0.02]  |
| r*-gap        | Cholesky          | monthly avg from 1996  | 5.7 | -0.32 [-0.96, +0.19]  | -0.04 [-0.57, +0.40]  | -0.52 [-1.02, +0.00]  | -0.74 [-1.41, -0.04]  |
| r*-gap        | proxy VAR         | end of month from 1996 | 8   | -0.33 [-0.98, +0.02]  | -0.10 [-0.64, +0.24]  | -0.56 [-1.51, +0.48]  | -0.78 [-1.82, +0.31]  |
| r*-gap        | window-impact VAR | end of month from 1996 | 8   | -0.19 [-0.80, +0.31]  | -0.03 [-0.55, +0.36]  | -0.51 [-0.97, -0.04]  | -0.69 [-1.28, -0.11]  |
| r*-gap        | Cholesky          | end of month from 1996 | 8   | -0.19 [-0.81, +0.31]  | -0.03 [-0.55, +0.36]  | -0.51 [-0.97, -0.05]  | -0.70 [-1.29, -0.11]  |
| r*-gap + FCI  | proxy VAR         | monthly avg from 1974  | 0.9 | +0.17 [unbounded]     | +0.10 [unbounded]     | -0.71 [unbounded]     | -0.97 [unbounded]     |
| r*-gap + FCI  | window-impact VAR | monthly avg from 1974  | 0.9 | +0.29 [+0.13, +0.41]  | +0.18 [+0.02, +0.28]  | -0.30 [-0.51, -0.07]  | -0.41 [-0.75, -0.05]  |
| r*-gap + FCI  | proxy VAR         | monthly avg from 1991  | 4   | -0.07 [-0.83, +1.54]  | -0.03 [-0.68, +1.21]  | -0.53 [-2.73, +0.22]  | -0.62 [-2.99, +0.24]  |
| r*-gap + FCI  | window-impact VAR | monthly avg from 1991  | 4   | +0.15 [-0.12, +0.39]  | +0.17 [-0.07, +0.38]  | -0.37 [-0.61, -0.10]  | -0.46 [-0.79, -0.11]  |
| r*-gap + FCI  | proxy VAR         | end of month from 1991 | 5.1 | +0.76 [-0.10, +4.20]  | +0.64 [-0.08, +3.40]  | -1.09 [-3.27, -0.12]  | -1.22 [-3.50, -0.10]  |
| r*-gap + FCI  | window-impact VAR | end of month from 1991 | 5.1 | +0.23 [-0.23, +0.64]  | +0.28 [-0.22, +0.65]  | -0.71 [-1.11, -0.22]  | -0.88 [-1.43, -0.22]  |
| r*-gap + FCI  | proxy VAR         | monthly avg from 1996  | 3.5 | -0.03 [-0.85, +2.43]  | -0.03 [-0.74, +1.79]  | -0.60 [-4.31, +0.20]  | -0.66 [-4.48, +0.23]  |
| r*-gap + FCI  | window-impact VAR | monthly avg from 1996  | 3.5 | +0.18 [-0.13, +0.46]  | +0.18 [-0.13, +0.39]  | -0.38 [-0.64, -0.10]  | -0.46 [-0.81, -0.08]  |
| r*-gap + FCI  | proxy VAR         | end of month from 1996 | 4.4 | +0.96 [+0.00, +5.96]  | +0.73 [-0.05, +4.62]  | -1.25 [-4.45, -0.24]  | -1.36 [-4.57, -0.23]  |
| r*-gap + FCI  | window-impact VAR | end of month from 1996 | 4.4 | +0.33 [-0.27, +0.77]  | +0.30 [-0.28, +0.70]  | -0.77 [-1.26, -0.24]  | -0.94 [-1.57, -0.23]  |

## Part B. Route 2: policy shocks recovered from daily and monthly innovations

### B.1 Method

* **Daily, from April 1990.** Note B's daily block (HAR regressions of the 2-year yield and the FCI on their 1/5/22/66-day averages and the monthly macro variables; Note B's coefficients, estimated from 1996) gives innovations eps_d on every weekday. With b = (1, b_F) the window impact (b_F = 1.00 for all three versions after FS-A75) and Omega their covariance (1990-2026), the policy shock of day d is s_d = b'Omega^-1 eps_d / (b'Omega^-1 b), in units of +1 pp on the 2-year yield in the window. This assumes that within a day the policy shock is recoverable from the two innovations (invertibility in the daily block): the shock is the yield-and-FCI movement in the window proportion, on any day. Re-estimating the daily block on 1990-2026 changes nothing beyond the third decimal.
* **Monthly, 1974 to April 1990.** The monthly VAR in monthly averages (12 lags, from 1973) with the window column, e_t = b'Sigma^-1 u_t / (b'Sigma^-1 b).
* **Splice (D-A13).** Over May 1990 to September 2026 the monthly-VAR shock correlates 0.58 with the month's sum of daily shocks (R2 0.34 with this and next month's), but its standard deviation is about twice as large (0.41 against 0.21). Unscaled, it implies variance shares above 100 percent for the yield when passed through Note B's model. Main version: the 1974-89 monthly shocks are scaled by the ratio of standard deviations over the overlap (0.52 for r*-gap with FCI; 0.48-0.53 in the other versions); the unscaled version is reported too.
* **Propagation.** Note B's model, point estimates (main: monthly equations from 1973, 12 lags; check: the 1996 baseline). A daily shock enters on its own day of the month (responses simulated for each day position and month length, 120 months); a monthly shock enters with the response averaged over announcement positions. Reproduces Note B's responses exactly [verified].
* **Variance share** at h: the variance over the period of the contribution of the shocks of the last h months, divided by the data's h-month forecast-error variance (monthly VAR in monthly averages from 1973, innovation covariance of the period). Bands: Note B's 500 bootstrap draws of its responses, with month-aggregated shocks and 36-month responses (the shocks and the data's forecast-error variance held fixed).

### B.2 The daily shocks (Table B1, Figure B1)

The recovered daily shock has a standard deviation of 0.049 pp a day: 0.067 on announcement days and 0.048 on other days. On announcement days it correlates 0.66 with the measured surprise (slope 0.82): most of the announcement-day policy shock is the window surprise. On ordinary days the FCI innovation moves 0.35 per pp of the yield innovation (the window moves it 1.00), so the window direction is distinct from ordinary co-movement and the projection is informative. Summed over a month, the recovered shocks have a standard deviation of 0.21 pp, against 0.046 for the measured surprises: there are about 21 weekdays a month and a policy announcement on about 8 days a year.

### B.3 Variance shares (Tables B3, B3b, B3c; Figure B3)

r*-gap with FCI, 24 months, Note B's model from 1973 (90 percent bands):

| Period, shocks | Unemployment gap | Core inflation | 2-year yield | FCI |
|---|---|---|---|---|
| 1974-89, monthly-recovered (scaled) | 4.6 [0.4, 21.6] | 7.8 [2.1, 15.8] | 56 [29, 75] | 37 [16, 58] |
| 1990-2026, daily-recovered, all days | 1.3 [0.1, 5.8] | 4.6 [1.0, 9.1] | 64 [33, 88] | 45 [18, 70] |
| of which non-announcement days | 1.3 | 4.9 | 68 | 48 |
| of which announcement days | 0.1 | 0.2 | 2.7 | 1.9 |
| measured surprises | 0.1 [0.0, 0.3] | 0.2 [0.0, 0.4] | 3.1 [1.5, 4.2] | 2.1 [0.8, 3.3] |

* With Note B's baseline model (monthly equations from 1996) the macro shares are larger, because the baseline's unemployment response is larger: 1990-2026, 8.6 percent of unemployment and 9.5 percent of core inflation; 1974-89 (scaled), 31.7 and 14.1 percent (Table B3c).
* Nominal and real versions with the FCI: smaller shares for unemployment (0.2-0.3 percent from 1990) and inflation (0.6-2.4 percent); the yield 38 percent and the FCI 31-35 percent (Table B3).
* **Without the FCI** the daily shock is every yield innovation, and the shares for the yield exceed 100 percent (108-116 percent from 1990): Note B's yield-only model makes the yield response more persistent than the data's forecast errors allow. These versions are reported but not interpretable as shares.
* At 12 and 36 months the pattern is the same (Table B3b).

### B.4 Historical decomposition (Table B4, Figure B2)

Figure B2 shows, for the r*-gap version with the FCI, the contribution of the policy-direction shocks (daily from 1990, monthly scaled before), the part from announcement days, and the measured surprises, next to the data's deviation from the monthly VAR's deterministic path. With Note B's model from 1973:
* 1979-80: easing on net (r*-gap yield -1.0 pp, FCI -1.0 to -1.2 points; 12-month core inflation +1.3 pp by end-1980).
* 1982-84: tightening (yield +3.7 pp in mid-1982 and +3.0 in mid-1984; FCI +3.7 and +2.5); core inflation -0.4 by mid-1984 and -1.0 by end-1986.
* 2001-03: easing (yield -1.1 to -1.8 pp); 2008: a financial-conditions tightening (FCI +1.3 at end-2008) despite the cuts; 2019-21: easing (yield -1.7 in mid-2021; core inflation +0.8 by mid-2021 and +1.0 by end-2022).
* 2022-24: tightening (yield +0.7 to +1.0 pp, FCI +0.6 to +0.8).
* Unemployment contributions are within +-0.65 pp with the 1973 model. With the baseline model they are larger: the 2001-03 easing lowered unemployment by 0.8 pp by mid-2003, the 2019-21 easing by 1.1 pp in mid-2021, and the 2022-24 tightening raised it by 0.7 pp by end-2024 (and lowered core inflation by 0.7 pp).
* The measured surprises' contribution is small throughout: at most about 0.5 pp of unemployment (2003, baseline model) and 0.4 pp of core inflation.

### B.5 What the shocks are, stated as facts

* The recovered shock is the yield-and-FCI movement in the window's proportion on every day. On announcement days it is mostly the policy surprise (correlation 0.66). On other days it includes policy news outside the windows (speeches, testimony, minutes, data that change the expected path of policy) and any other news that moves the 2-year yield and the FCI in that proportion; the projection cannot separate them [inference].
* The monthly recovery (first round, Appendix) shows the limit of monthly data: monthly innovations span the measured surprises poorly (R2 0.4-4 percent), and simulations from Note B's model reproduce that, so a monthly VAR cannot identify the announcement shock itself. The daily recovery does much better on announcement days (0.66). Before 1990 only the monthly recovery is available.

## Choices I made (full list in DECOMP_QA.md)

D-A11/12 follow your instructions. Mine: D-A13 the splice scaling (sd ratio over the overlap; unscaled reported); D-A14 Note B's daily coefficients applied from 1990, Omega over 1990-2026, variance shares relative to the data's monthly-VAR forecast errors; Note B's model from 1973 as the main propagation model for Route 2 (it is the model that covers the whole period), the 1996 baseline as the check; responses to 120 months for the point estimates; bands from Note B's draws with month-aggregated shocks.

## Corrections to the first report

* The first report's "1996" rows lost 1996 (no pre-sample lags) and the proxy VAR used instrument months to September 2026; fixed and rerun (Appendix tables are the corrected ones).
* I said earlier that the paper's "Cholesky 1984-2026" might be affected by the 1990 start of the end-of-month series; it is not (nominal end-of-month yield from 1976; 513 months).

## Open for you

1. The draft's sentence on the 1973 start (Section 4.1) and the unemployment result at 24 months from 1973 (Part A.2).
2. Whether the daily Route 2 decomposition (B.3, B.4) belongs in Note B, and with which propagation model (1973 or the 1996 baseline).
3. The splice scaling before 1990.

## Figures

* `figures/A1_core_paths.png`: Note B's responses from 1973 (solid, 90 percent bands) and from 1996 (dashed), three versions, without and with the FCI.
* `figures/B1_shocks.png`: daily-recovered shocks (monthly sums) and measured surprises; the spliced series 1974-2026.
* `figures/B2_hd_rstar.png`: historical decomposition, r*-gap with FCI.
* `figures/B3_shares.png`: variance shares at 24 months by source.
* `figures/B4_hd_nom_nofci.png`: nominal without the FCI.
* First round (Appendix): `figures/fig1_shocks.png` to `fig7_*.png`.

# Tables, Part A

### A1 (12 lags). Note B's model: responses without and with the FCI, monthly equations from 1973 and from 1996 (u: unemployment gap, pp; P: price level, %; per +1 pp window surprise; paired differences; 90% intervals; ** and * 5 and 10 percent)

|   sample | yield   |   h | u: yield alone         | u: yield + FCI        | u: difference          | P: yield alone         | P: yield + FCI         | P: difference          |
|---------:|:--------|----:|:-----------------------|:----------------------|:-----------------------|:-----------------------|:-----------------------|:-----------------------|
|     1973 | Nominal |  12 | -0.33** [-0.50, -0.17] | -0.02 [-0.31, +0.21]  | +0.31** [+0.09, +0.49] | +0.10 [-0.02, +0.28]   | +0.08 [-0.05, +0.24]   | -0.03 [-0.11, +0.05]   |
|     1973 | Nominal |  24 | -0.17** [-0.34, -0.01] | -0.12 [-0.42, +0.12]  | +0.06 [-0.20, +0.25]   | +0.19 [-0.03, +0.59]   | +0.11 [-0.10, +0.46]   | -0.08 [-0.26, +0.05]   |
|     1973 | Nominal |  36 | -0.09 [-0.27, +0.08]   | -0.13 [-0.45, +0.10]  | -0.04 [-0.31, +0.13]   | +0.25 [-0.07, +0.91]   | +0.12 [-0.15, +0.65]   | -0.12 [-0.44, +0.05]   |
|     1973 | Real    |  12 | -0.15* [-0.27, -0.01]  | +0.10 [-0.08, +0.27]  | +0.26** [+0.08, +0.41] | -0.15* [-0.25, -0.02]  | -0.18** [-0.29, -0.05] | -0.04 [-0.11, +0.04]   |
|     1973 | Real    |  24 | -0.08 [-0.22, +0.04]   | +0.00 [-0.24, +0.17]  | +0.09 [-0.11, +0.26]   | -0.31* [-0.52, -0.02]  | -0.39** [-0.57, -0.12] | -0.07 [-0.23, +0.06]   |
|     1973 | Real    |  36 | -0.05 [-0.20, +0.07]   | -0.02 [-0.25, +0.13]  | +0.03 [-0.16, +0.21]   | -0.47 [-0.79, +0.01]   | -0.55** [-0.85, -0.13] | -0.08 [-0.32, +0.13]   |
|     1973 | r*-gap  |  12 | -0.05 [-0.20, +0.08]   | +0.18 [-0.07, +0.38]  | +0.23 [-0.01, +0.43]   | -0.22** [-0.33, -0.08] | -0.27** [-0.41, -0.10] | -0.05 [-0.13, +0.02]   |
|     1973 | r*-gap  |  24 | -0.01 [-0.17, +0.16]   | +0.14 [-0.17, +0.36]  | +0.14 [-0.13, +0.37]   | -0.50** [-0.73, -0.17] | -0.63** [-0.89, -0.22] | -0.13 [-0.27, +0.04]   |
|     1973 | r*-gap  |  36 | -0.00 [-0.16, +0.17]   | +0.13 [-0.19, +0.35]  | +0.13 [-0.18, +0.37]   | -0.79** [-1.17, -0.21] | -0.98** [-1.42, -0.26] | -0.19 [-0.39, +0.09]   |
|     1996 | Nominal |  12 | -0.81** [-1.20, -0.38] | -0.05 [-0.50, +0.35]  | +0.76** [+0.34, +1.12] | +0.09 [-0.11, +0.28]   | -0.13 [-0.33, +0.09]   | -0.22* [-0.41, -0.02]  |
|     1996 | Nominal |  24 | -0.49** [-0.82, -0.13] | +0.16 [-0.24, +0.55]  | +0.65** [+0.21, +1.08] | +0.02 [-0.33, +0.42]   | -0.42 [-0.80, +0.02]   | -0.44* [-0.84, -0.04]  |
|     1996 | Nominal |  36 | -0.31 [-0.69, +0.06]   | +0.22 [-0.20, +0.67]  | +0.53** [+0.06, +1.04] | -0.12 [-0.61, +0.46]   | -0.71 [-1.22, +0.00]   | -0.59 [-1.14, +0.00]   |
|     1996 | Real    |  12 | -0.61** [-0.96, -0.27] | +0.09 [-0.37, +0.43]  | +0.69** [+0.37, +0.98] | -0.03 [-0.18, +0.14]   | -0.23** [-0.40, -0.06] | -0.20** [-0.35, -0.05] |
|     1996 | Real    |  24 | -0.33* [-0.64, -0.07]  | +0.23 [-0.11, +0.60]  | +0.57** [+0.18, +0.98] | -0.11 [-0.37, +0.21]   | -0.48** [-0.84, -0.12] | -0.37** [-0.71, -0.07] |
|     1996 | Real    |  36 | -0.22 [-0.55, +0.05]   | +0.21 [-0.14, +0.62]  | +0.43* [+0.03, +0.94]  | -0.21 [-0.61, +0.28]   | -0.66** [-1.24, -0.10] | -0.45 [-1.02, +0.03]   |
|     1996 | r*-gap  |  12 | -0.29 [-0.60, +0.11]   | +0.33 [-0.06, +0.76]  | +0.62** [+0.24, +1.00] | -0.21** [-0.35, -0.05] | -0.42** [-0.60, -0.20] | -0.20** [-0.38, -0.07] |
|     1996 | r*-gap  |  24 | -0.07 [-0.42, +0.24]   | +0.49* [+0.01, +0.95] | +0.56** [+0.10, +1.05] | -0.44** [-0.73, -0.05] | -0.80** [-1.22, -0.33] | -0.37** [-0.77, -0.07] |
|     1996 | r*-gap  |  36 | +0.03 [-0.35, +0.36]   | +0.43 [-0.07, +0.98]  | +0.40 [-0.12, +1.01]   | -0.69** [-1.13, -0.10] | -1.11** [-1.90, -0.35] | -0.42 [-1.08, +0.08]   |

### A1 (6 lags). Note B's model: responses without and with the FCI, monthly equations from 1973 and from 1996 (u: unemployment gap, pp; P: price level, %; per +1 pp window surprise; paired differences; 90% intervals; ** and * 5 and 10 percent)

|   sample | yield   |   h | u: yield alone         | u: yield + FCI       | u: difference          | P: yield alone         | P: yield + FCI         | P: difference          |
|---------:|:--------|----:|:-----------------------|:---------------------|:-----------------------|:-----------------------|:-----------------------|:-----------------------|
|     1973 | Nominal |  24 | -0.09 [-0.22, +0.07]   | -0.14 [-0.39, +0.05] | -0.05 [-0.27, +0.10]   | +0.33** [+0.17, +0.76] | +0.27** [+0.10, +0.56] | -0.06 [-0.27, +0.04]   |
|     1973 | Real    |  24 | -0.03 [-0.17, +0.09]   | -0.05 [-0.28, +0.06] | -0.01 [-0.21, +0.09]   | -0.11 [-0.25, +0.30]   | -0.16 [-0.30, +0.17]   | -0.05 [-0.22, +0.04]   |
|     1973 | r*-gap  |  24 | +0.03 [-0.11, +0.19]   | +0.05 [-0.22, +0.22] | +0.03 [-0.22, +0.18]   | -0.31 [-0.49, +0.08]   | -0.35 [-0.56, +0.08]   | -0.05 [-0.17, +0.09]   |
|     1996 | Nominal |  24 | -0.42** [-0.67, -0.10] | +0.17 [-0.19, +0.54] | +0.59** [+0.18, +0.96] | +0.01 [-0.31, +0.32]   | -0.39 [-0.77, +0.01]   | -0.40* [-0.70, -0.03]  |
|     1996 | Real    |  24 | -0.29* [-0.55, -0.03]  | +0.19 [-0.13, +0.55] | +0.48** [+0.16, +0.82] | -0.09 [-0.39, +0.20]   | -0.42** [-0.80, -0.08] | -0.34** [-0.63, -0.05] |
|     1996 | r*-gap  |  24 | -0.06 [-0.43, +0.25]   | +0.36 [-0.12, +0.71] | +0.42 [-0.02, +0.87]   | -0.35* [-0.68, -0.00]  | -0.63** [-1.01, -0.16] | -0.28 [-0.58, +0.06]   |

### A1 (3 lags). Note B's model: responses without and with the FCI, monthly equations from 1973 and from 1996 (u: unemployment gap, pp; P: price level, %; per +1 pp window surprise; paired differences; 90% intervals; ** and * 5 and 10 percent)

|   sample | yield   |   h | u: yield alone         | u: yield + FCI       | u: difference          | P: yield alone         | P: yield + FCI         | P: difference          |
|---------:|:--------|----:|:-----------------------|:---------------------|:-----------------------|:-----------------------|:-----------------------|:-----------------------|
|     1973 | Nominal |  24 | -0.05 [-0.16, +0.09]   | -0.16 [-0.40, +0.04] | -0.11 [-0.34, +0.06]   | +0.50** [+0.39, +0.93] | +0.36** [+0.23, +0.62] | -0.14** [-0.44, -0.07] |
|     1973 | Real    |  24 | -0.01 [-0.13, +0.12]   | -0.08 [-0.30, +0.02] | -0.07 [-0.27, +0.01]   | +0.06** [+0.10, +0.61] | -0.02 [-0.16, +0.30]   | -0.09** [-0.52, -0.08] |
|     1973 | r*-gap  |  24 | +0.05 [-0.09, +0.21]   | +0.00 [-0.29, +0.12] | -0.04 [-0.32, +0.04]   | -0.15 [-0.17, +0.46]   | -0.16 [-0.29, +0.37]   | -0.01 [-0.36, +0.16]   |
|     1996 | Nominal |  24 | -0.45** [-0.72, -0.13] | +0.07 [-0.32, +0.38] | +0.52** [+0.12, +0.85] | +0.08 [-0.18, +0.35]   | -0.27 [-0.60, +0.08]   | -0.35* [-0.65, -0.02]  |
|     1996 | Real    |  24 | -0.33** [-0.58, -0.08] | +0.06 [-0.26, +0.35] | +0.39** [+0.08, +0.68] | -0.07 [-0.27, +0.21]   | -0.31 [-0.59, +0.01]   | -0.24 [-0.53, +0.01]   |
|     1996 | r*-gap  |  24 | -0.16 [-0.45, +0.16]   | +0.13 [-0.28, +0.49] | +0.30 [-0.13, +0.64]   | -0.15 [-0.43, +0.14]   | -0.25 [-0.61, +0.16]   | -0.11 [-0.35, +0.16]   |

### A1b. Decomposition of the FCI effect at 24 months (path A = with FCI, B = FCI started at its ordinary co-movement with the yield, C = yield alone; 12 lags)

|   sample | yield   |   ordinary FCI loading | u24: A-B (extra initial FCI move)   | u24: B-C (FCI as ordinarily)   | P24: A-B (extra initial FCI move)   | P24: B-C (FCI as ordinarily)   |
|---------:|:--------|-----------------------:|:------------------------------------|:-------------------------------|:------------------------------------|:-------------------------------|
|     1973 | Nominal |                   0.27 | +0.20* [+0.02, +0.45]               | -0.14 [-0.40, +0.02]           | -0.02 [-0.22, +0.23]                | -0.06 [-0.29, +0.11]           |
|     1973 | Real    |                   0.27 | +0.20** [+0.02, +0.39]              | -0.12 [-0.29, +0.05]           | -0.08 [-0.28, +0.16]                | +0.00 [-0.21, +0.13]           |
|     1973 | r*-gap  |                   0.28 | +0.24** [+0.07, +0.39]              | -0.10 [-0.33, +0.13]           | -0.16 [-0.33, +0.07]                | +0.03 [-0.13, +0.17]           |
|     1996 | Nominal |                   0.27 | +0.44** [+0.17, +0.82]              | +0.21 [-0.10, +0.44]           | -0.30** [-0.63, -0.08]              | -0.15 [-0.35, +0.12]           |
|     1996 | Real    |                   0.27 | +0.45** [+0.19, +0.83]              | +0.12 [-0.17, +0.35]           | -0.29** [-0.62, -0.07]              | -0.08 [-0.26, +0.11]           |
|     1996 | r*-gap  |                   0.28 | +0.46** [+0.22, +0.93]              | +0.10 [-0.30, +0.38]           | -0.33** [-0.71, -0.09]              | -0.04 [-0.21, +0.20]           |

### A2. Monthly VAR benchmarks (Note B Tables 2 and 4) from 1973 in monthly averages, from 1990 at the end of the month, and the paper's end-of-month 1996 versions (12 lags; per +1 pp window surprise for proxy and window-impact VARs, per +1 pp yield innovation for Cholesky; 90% intervals: Anderson-Rubin for the proxy VAR, block bootstrap otherwise; * = excludes zero)

| yield   | FCI   | method            | data              |   F | u12                   | u24                   | P24                   | P36                   |
|:--------|:------|:------------------|:------------------|----:|:----------------------|:----------------------|:----------------------|:----------------------|
| Nominal | no    | Cholesky          | end of month 1990 | 4.4 | -0.81 [-1.28, -0.30]* | -0.49 [-0.79, +0.00]  | +0.05 [-0.34, +0.35]  | -0.06 [-0.63, +0.38]  |
| Nominal | no    | Cholesky          | end of month 1996 | 4.5 | -0.95 [-1.48, -0.37]* | -0.66 [-1.04, -0.09]* | +0.07 [-0.41, +0.52]  | -0.10 [-0.74, +0.56]  |
| Nominal | no    | Cholesky          | monthly avg 1974  | 5.5 | -0.34 [-0.63, +0.04]  | -0.17 [-0.36, +0.11]  | +0.20 [-0.23, +0.64]  | +0.25 [-0.41, +0.95]  |
| Nominal | no    | proxy VAR         | end of month 1990 | 4.4 | -0.76 [-1.16, -0.40]* | -0.45 [-0.78, -0.11]* | -0.04 [-1.65, +1.29]  | -0.17 [-2.07, +1.39]  |
| Nominal | no    | proxy VAR         | end of month 1996 | 4.5 | -0.86 [-1.31, -0.40]* | -0.58 [-1.03, -0.05]* | -0.07 [-1.75, +1.20]  | -0.25 [-2.17, +1.20]  |
| Nominal | no    | proxy VAR         | monthly avg 1974  | 5.5 | -0.25 [-0.58, -0.07]* | -0.13 [-0.30, -0.04]* | +0.04 [-1.22, +1.16]  | +0.04 [-1.63, +1.52]  |
| Nominal | no    | window-impact VAR | end of month 1990 | 4.4 | -0.77 [-1.22, -0.28]* | -0.47 [-0.75, +0.00]  | +0.05 [-0.32, +0.34]  | -0.06 [-0.60, +0.36]  |
| Nominal | no    | window-impact VAR | end of month 1996 | 4.5 | -0.90 [-1.41, -0.35]* | -0.63 [-0.99, -0.08]* | +0.06 [-0.39, +0.49]  | -0.09 [-0.70, +0.53]  |
| Nominal | no    | window-impact VAR | monthly avg 1974  | 5.5 | -0.15 [-0.28, +0.02]  | -0.08 [-0.16, +0.05]  | +0.09 [-0.10, +0.28]  | +0.11 [-0.18, +0.42]  |
| Real    | no    | Cholesky          | end of month 1990 | 6.9 | -0.61 [-0.99, -0.18]* | -0.34 [-0.69, +0.13]  | -0.14 [-0.57, +0.23]  | -0.23 [-0.83, +0.28]  |
| Real    | no    | Cholesky          | end of month 1996 | 6.9 | -0.66 [-1.17, -0.17]* | -0.47 [-0.94, +0.02]  | -0.16 [-0.67, +0.33]  | -0.30 [-0.98, +0.37]  |
| Real    | no    | Cholesky          | monthly avg 1974  | 4.6 | -0.22 [-0.47, +0.09]  | -0.12 [-0.32, +0.17]  | -0.45 [-0.75, +0.07]  | -0.66 [-1.12, +0.12]  |
| Real    | no    | proxy VAR         | end of month 1990 | 6.9 | -0.69 [-1.19, -0.41]* | -0.39 [-0.78, -0.13]* | -0.16 [-1.25, +0.96]  | -0.27 [-1.56, +1.00]  |
| Real    | no    | proxy VAR         | end of month 1996 | 6.9 | -0.71 [-1.26, -0.35]* | -0.47 [-0.97, -0.07]* | -0.28 [-1.47, +0.84]  | -0.45 [-1.81, +0.79]  |
| Real    | no    | proxy VAR         | monthly avg 1974  | 4.6 | -0.26 [-0.97, -0.05]* | -0.13 [-0.52, -0.03]* | -0.23 [-1.98, +1.31]  | -0.34 [-2.65, +1.69]  |
| Real    | no    | window-impact VAR | end of month 1990 | 6.9 | -0.59 [-0.96, -0.17]* | -0.33 [-0.67, +0.13]  | -0.13 [-0.56, +0.22]  | -0.23 [-0.81, +0.28]  |
| Real    | no    | window-impact VAR | end of month 1996 | 6.9 | -0.65 [-1.15, -0.16]* | -0.46 [-0.92, +0.02]  | -0.16 [-0.66, +0.32]  | -0.29 [-0.96, +0.36]  |
| Real    | no    | window-impact VAR | monthly avg 1974  | 4.6 | -0.10 [-0.21, +0.04]  | -0.05 [-0.15, +0.08]  | -0.20 [-0.34, +0.03]  | -0.30 [-0.51, +0.05]  |
| r*-gap  | no    | Cholesky          | end of month 1990 | 8.1 | -0.24 [-0.62, +0.13]  | -0.01 [-0.38, +0.41]  | -0.45 [-0.85, -0.03]* | -0.60 [-1.13, -0.03]* |
| r*-gap  | no    | Cholesky          | end of month 1996 | 8   | -0.19 [-0.81, +0.31]  | -0.03 [-0.55, +0.36]  | -0.51 [-0.97, -0.05]* | -0.70 [-1.29, -0.11]* |
| r*-gap  | no    | Cholesky          | monthly avg 1974  | 5   | -0.07 [-0.32, +0.22]  | -0.00 [-0.18, +0.25]  | -0.65 [-0.97, -0.11]* | -0.98 [-1.48, -0.12]* |
| r*-gap  | no    | proxy VAR         | end of month 1990 | 8.1 | -0.42 [-1.01, -0.11]* | -0.12 [-0.55, +0.13]  | -0.42 [-1.35, +0.65]  | -0.59 [-1.67, +0.61]  |
| r*-gap  | no    | proxy VAR         | end of month 1996 | 8   | -0.33 [-0.98, +0.02]  | -0.10 [-0.64, +0.24]  | -0.56 [-1.51, +0.48]  | -0.78 [-1.82, +0.31]  |
| r*-gap  | no    | proxy VAR         | monthly avg 1974  | 5   | -0.21 [-0.93, -0.00]* | -0.09 [-0.45, +0.01]  | -0.33 [-1.73, +1.17]  | -0.51 [-2.36, +1.46]  |
| r*-gap  | no    | window-impact VAR | end of month 1990 | 8.1 | -0.24 [-0.62, +0.13]  | -0.01 [-0.38, +0.41]  | -0.45 [-0.84, -0.03]* | -0.59 [-1.13, -0.03]* |
| r*-gap  | no    | window-impact VAR | end of month 1996 | 8   | -0.19 [-0.80, +0.31]  | -0.03 [-0.55, +0.36]  | -0.51 [-0.97, -0.04]* | -0.69 [-1.28, -0.11]* |
| r*-gap  | no    | window-impact VAR | monthly avg 1974  | 5   | -0.03 [-0.15, +0.10]  | -0.00 [-0.08, +0.11]  | -0.30 [-0.44, -0.05]* | -0.45 [-0.68, -0.06]* |
| Nominal | yes   | proxy VAR         | end of month 1991 | 1.9 | +0.47 [unbounded]     | +0.32 [unbounded]     | -0.65 [unbounded]     | -0.71 [unbounded]     |
| Nominal | yes   | proxy VAR         | end of month 1996 | 1.6 | +0.65 [unbounded]     | +0.46 [unbounded]     | -0.93 [unbounded]     | -1.06 [unbounded]     |
| Nominal | yes   | proxy VAR         | monthly avg 1974  | 0.8 | +0.14 [unbounded]     | +0.09 [unbounded]     | -0.40 [unbounded]     | -0.57 [unbounded]     |
| Nominal | yes   | window-impact VAR | end of month 1991 | 1.9 | -0.19 [-0.62, +0.19]  | -0.13 [-0.47, +0.24]  | -0.21 [-0.56, +0.20]  | -0.33 [-0.81, +0.23]  |
| Nominal | yes   | window-impact VAR | end of month 1996 | 1.6 | -0.14 [-0.62, +0.40]  | -0.09 [-0.54, +0.47]  | -0.36 [-0.88, +0.09]  | -0.57 [-1.25, +0.12]  |
| Nominal | yes   | window-impact VAR | monthly avg 1974  | 0.8 | +0.19 [+0.06, +0.35]* | +0.13 [+0.01, +0.24]* | +0.03 [-0.27, +0.19]  | +0.06 [-0.37, +0.29]  |
| Real    | yes   | proxy VAR         | end of month 1991 | 3.9 | +0.43 [-0.30, +6.19]  | +0.28 [-0.36, +4.99]  | -0.72 [-4.31, +0.44]  | -0.77 [-4.53, +0.64]  |
| Real    | yes   | proxy VAR         | end of month 1996 | 3   | +0.69 [-0.21, +23.91] | +0.47 [-0.32, +19.42] | -1.01 [-15.78, +0.22] | -1.07 [-16.27, +0.33] |
| Real    | yes   | proxy VAR         | monthly avg 1974  | 0.8 | +0.16 [unbounded]     | +0.07 [unbounded]     | -0.78 [unbounded]     | -1.10 [unbounded]     |
| Real    | yes   | window-impact VAR | end of month 1991 | 3.9 | -0.12 [-0.57, +0.26]  | -0.10 [-0.49, +0.27]  | -0.38 [-0.76, +0.10]  | -0.48 [-1.05, +0.16]  |
| Real    | yes   | window-impact VAR | end of month 1996 | 3   | -0.02 [-0.57, +0.53]  | -0.04 [-0.57, +0.46]  | -0.49 [-1.05, -0.00]* | -0.63 [-1.33, +0.02]  |
| Real    | yes   | window-impact VAR | monthly avg 1974  | 0.8 | +0.24 [+0.07, +0.37]* | +0.16 [-0.01, +0.26]  | -0.25 [-0.45, +0.00]  | -0.33 [-0.63, +0.05]  |
| r*-gap  | yes   | proxy VAR         | end of month 1991 | 5.1 | +0.76 [-0.10, +4.20]  | +0.64 [-0.08, +3.40]  | -1.09 [-3.27, -0.12]* | -1.22 [-3.50, -0.10]* |
| r*-gap  | yes   | proxy VAR         | end of month 1996 | 4.4 | +0.96 [+0.00, +5.96]* | +0.73 [-0.05, +4.62]  | -1.25 [-4.45, -0.24]* | -1.36 [-4.57, -0.23]* |
| r*-gap  | yes   | proxy VAR         | monthly avg 1974  | 0.9 | +0.17 [unbounded]     | +0.10 [unbounded]     | -0.71 [unbounded]     | -0.97 [unbounded]     |
| r*-gap  | yes   | window-impact VAR | end of month 1991 | 5.1 | +0.23 [-0.30, +0.66]  | +0.28 [-0.23, +0.67]  | -0.71 [-1.08, -0.17]* | -0.88 [-1.40, -0.16]* |
| r*-gap  | yes   | window-impact VAR | end of month 1996 | 4.4 | +0.33 [-0.27, +0.77]  | +0.30 [-0.28, +0.70]  | -0.77 [-1.26, -0.24]* | -0.94 [-1.57, -0.23]* |
| r*-gap  | yes   | window-impact VAR | monthly avg 1974  | 0.9 | +0.29 [+0.13, +0.41]* | +0.18 [+0.02, +0.28]* | -0.30 [-0.51, -0.07]* | -0.41 [-0.75, -0.05]* |

# Tables, Part B

### B1. Policy shocks recovered from daily innovations, 1990-2026 (Note B's daily block; s_d = b'Omega^-1 eps_d / b'Omega^-1 b)

| case          | first day   |   days |   window loading b_F |   ordinary-day FCI loading |   corr of innovations |   sd shock, all days |   sd, announcement days |   sd, other days |   sd measured surprise |   corr with measured, announcement days |   slope on measured |
|:--------------|:------------|-------:|---------------------:|---------------------------:|----------------------:|---------------------:|------------------------:|-----------------:|-----------------------:|----------------------------------------:|--------------------:|
| nominal       | 1990-04-04  |   9521 |                      |                            |                       |                0.055 |                   0.072 |            0.054 |                  0.054 |                                    0.64 |                0.86 |
| nominal + FCI | 1990-04-17  |   9512 |                    1 |                       0.34 |                  0.28 |                0.048 |                   0.066 |            0.048 |                  0.054 |                                    0.66 |                0.8  |
| real          | 1990-04-04  |   9521 |                      |                            |                       |                0.055 |                   0.074 |            0.054 |                  0.054 |                                    0.64 |                0.88 |
| real + FCI    | 1990-04-17  |   9512 |                    1 |                       0.34 |                  0.28 |                0.048 |                   0.067 |            0.048 |                  0.054 |                                    0.66 |                0.82 |
| r*-gap        | 1990-04-04  |   9521 |                      |                            |                       |                0.055 |                   0.074 |            0.055 |                  0.054 |                                    0.64 |                0.88 |
| r*-gap + FCI  | 1990-04-17  |   9512 |                    1 |                       0.35 |                  0.29 |                0.049 |                   0.067 |            0.048 |                  0.054 |                                    0.66 |                0.82 |

### B2. Monthly-VAR shocks against the month's sum of daily shocks, May 1990 - September 2026 (the splice)

| case          |   corr, same month |   R2 on same and next month |   sd monthly-VAR shock |   sd daily sum |   scale used before 1990 (sd ratio) |   sd monthly-VAR shock 1974-89 (unscaled) |
|:--------------|-------------------:|----------------------------:|-----------------------:|---------------:|------------------------------------:|------------------------------------------:|
| r*-gap + FCI  |               0.58 |                        0.33 |                   0.41 |           0.21 |                                0.52 |                                      0.8  |
| r*-gap        |               0.61 |                        0.38 |                   0.48 |           0.23 |                                0.48 |                                      1    |
| nominal + FCI |               0.57 |                        0.33 |                   0.44 |           0.23 |                                0.52 |                                      0.7  |
| nominal       |               0.65 |                        0.43 |                   0.48 |           0.25 |                                0.53 |                                      1.09 |
| real + FCI    |               0.57 |                        0.32 |                   0.43 |           0.22 |                                0.5  |                                      0.7  |
| real          |               0.62 |                        0.38 |                   0.49 |           0.24 |                                0.48 |                                      1.02 |

### B3 (r*-gap + FCI). Share of the 24-month forecast-error variance, percent (Note B's model from 1973; exact day-of-month responses, 120 months; 90% band from Note B's bootstrap with month-aggregated shocks and 36-month responses)

| period    | shocks                       | unemployment gap   | core inflation   | 2-year yield         | FCI                 |
|:----------|:-----------------------------|:-------------------|:-----------------|:---------------------|:--------------------|
| 1974-1989 | monthly-recovered (scaled)   | 4.6 [0.4, 21.6]    | 7.8 [2.1, 15.8]  | 55.6 [29.4, 75.2]    | 37.1 [15.7, 58.1]   |
| 1974-1989 | monthly-recovered (unscaled) | 16.8 [1.3, 79.1]   | 28.7 [7.7, 58.0] | 204.0 [107.9, 275.9] | 135.9 [57.5, 213.1] |
| 1990-2026 | daily-recovered, all days    | 1.3 [0.1, 5.8]     | 4.6 [1.0, 9.1]   | 64.2 [33.4, 87.9]    | 44.8 [17.6, 70.2]   |
| 1990-2026 | non-announcement days        | 1.3 [0.1, 6.1]     | 4.9 [1.0, 9.5]   | 68.3 [35.4, 93.6]    | 47.5 [18.6, 74.7]   |
| 1990-2026 | announcement days            | 0.1 [0.0, 0.2]     | 0.2 [0.1, 0.4]   | 2.7 [1.4, 3.6]       | 1.9 [0.7, 2.9]      |
| 1990-2026 | measured surprises (Route 1) | 0.1 [0.0, 0.3]     | 0.2 [0.0, 0.4]   | 3.1 [1.5, 4.2]       | 2.1 [0.8, 3.3]      |
| 1996-2026 | daily-recovered, all days    | 1.0 [0.1, 4.9]     | 4.2 [1.0, 8.3]   | 56.9 [29.8, 78.6]    | 40.9 [16.3, 64.3]   |
| 1996-2026 | measured surprises (Route 1) | 0.1 [0.0, 0.3]     | 0.2 [0.1, 0.5]   | 3.3 [1.7, 4.6]       | 2.4 [0.9, 3.7]      |

### B3 (nominal + FCI). Share of the 24-month forecast-error variance, percent (Note B's model from 1973; exact day-of-month responses, 120 months; 90% band from Note B's bootstrap with month-aggregated shocks and 36-month responses)

| period    | shocks                       | unemployment gap   | core inflation   | 2-year yield       | FCI                |
|:----------|:-----------------------------|:-------------------|:-----------------|:-------------------|:-------------------|
| 1974-1989 | monthly-recovered (scaled)   | 1.4 [0.7, 20.6]    | 0.7 [0.6, 3.9]   | 24.4 [11.1, 37.1]  | 26.1 [14.5, 35.2]  |
| 1974-1989 | monthly-recovered (unscaled) | 5.3 [2.5, 76.4]    | 2.7 [2.3, 14.6]  | 90.3 [41.1, 137.4] | 96.6 [53.8, 130.4] |
| 1990-2026 | daily-recovered, all days    | 0.3 [0.2, 5.1]     | 0.6 [0.4, 2.9]   | 37.9 [16.9, 57.9]  | 34.7 [19.0, 46.3]  |
| 1990-2026 | non-announcement days        | 0.3 [0.1, 5.1]     | 0.6 [0.4, 2.9]   | 38.0 [17.0, 57.8]  | 34.9 [19.3, 46.6]  |
| 1990-2026 | announcement days            | 0.0 [0.0, 0.2]     | 0.0 [0.0, 0.1]   | 1.8 [0.8, 2.8]     | 1.7 [0.9, 2.2]     |
| 1990-2026 | measured surprises (Route 1) | 0.0 [0.0, 0.3]     | 0.0 [0.0, 0.1]   | 2.1 [0.9, 3.2]     | 1.9 [1.0, 2.5]     |
| 1996-2026 | daily-recovered, all days    | 0.3 [0.1, 3.6]     | 0.5 [0.4, 2.3]   | 28.9 [12.8, 44.7]  | 28.4 [15.6, 37.8]  |
| 1996-2026 | measured surprises (Route 1) | 0.0 [0.0, 0.3]     | 0.0 [0.0, 0.1]   | 2.3 [1.0, 3.4]     | 2.2 [1.1, 2.9]     |

### B3 (real + FCI). Share of the 24-month forecast-error variance, percent (Note B's model from 1973; exact day-of-month responses, 120 months; 90% band from Note B's bootstrap with month-aggregated shocks and 36-month responses)

| period    | shocks                       | unemployment gap   | core inflation   | 2-year yield       | FCI                |
|:----------|:-----------------------------|:-------------------|:-----------------|:-------------------|:-------------------|
| 1974-1989 | monthly-recovered (scaled)   | 1.0 [0.6, 10.4]    | 2.7 [0.9, 5.9]   | 22.8 [12.8, 32.3]  | 25.0 [13.7, 37.7]  |
| 1974-1989 | monthly-recovered (unscaled) | 3.8 [2.2, 41.0]    | 10.4 [3.7, 23.2] | 89.5 [50.3, 126.7] | 98.0 [53.6, 147.9] |
| 1990-2026 | daily-recovered, all days    | 0.2 [0.1, 2.5]     | 2.4 [0.7, 5.1]   | 37.8 [20.4, 53.9]  | 31.0 [16.1, 47.2]  |
| 1990-2026 | non-announcement days        | 0.2 [0.1, 2.5]     | 2.4 [0.7, 5.1]   | 37.9 [20.5, 54.0]  | 31.1 [16.3, 47.4]  |
| 1990-2026 | announcement days            | 0.0 [0.0, 0.1]     | 0.1 [0.0, 0.2]   | 1.4 [0.7, 1.9]     | 1.1 [0.6, 1.7]     |
| 1990-2026 | measured surprises (Route 1) | 0.0 [0.0, 0.1]     | 0.1 [0.0, 0.2]   | 1.5 [0.8, 2.2]     | 1.2 [0.6, 1.9]     |
| 1996-2026 | daily-recovered, all days    | 0.2 [0.1, 1.9]     | 1.9 [0.6, 4.2]   | 30.0 [16.2, 43.1]  | 25.7 [13.5, 39.4]  |
| 1996-2026 | measured surprises (Route 1) | 0.0 [0.0, 0.1]     | 0.1 [0.0, 0.2]   | 1.6 [0.8, 2.3]     | 1.4 [0.7, 2.1]     |

### B3 (r*-gap). Share of the 24-month forecast-error variance, percent (Note B's model from 1973; exact day-of-month responses, 120 months; 90% band from Note B's bootstrap with month-aggregated shocks and 36-month responses)

| period    | shocks                       | unemployment gap   | core inflation   | 2-year yield         |
|:----------|:-----------------------------|:-------------------|:-----------------|:---------------------|
| 1974-1989 | monthly-recovered (scaled)   | 2.1 [1.2, 26.9]    | 6.8 [1.4, 15.2]  | 67.1 [40.2, 86.7]    |
| 1974-1989 | monthly-recovered (unscaled) | 9.3 [5.1, 116.8]   | 29.5 [6.0, 65.7] | 290.8 [174.3, 375.9] |
| 1990-2026 | daily-recovered, all days    | 0.2 [0.1, 2.2]     | 4.9 [0.8, 10.7]  | 108.3 [63.1, 139.7]  |
| 1990-2026 | non-announcement days        | 0.2 [0.1, 2.2]     | 4.9 [0.8, 10.7]  | 108.6 [63.1, 140.0]  |
| 1990-2026 | announcement days            | 0.0 [0.0, 0.1]     | 0.1 [0.0, 0.3]   | 3.2 [1.9, 4.0]       |
| 1990-2026 | measured surprises (Route 1) | 0.0 [0.0, 0.1]     | 0.1 [0.0, 0.3]   | 2.8 [1.6, 3.6]       |
| 1996-2026 | daily-recovered, all days    | 0.1 [0.1, 1.7]     | 4.3 [0.7, 9.5]   | 92.4 [53.8, 119.6]   |
| 1996-2026 | measured surprises (Route 1) | 0.0 [0.0, 0.1]     | 0.1 [0.0, 0.3]   | 3.0 [1.8, 3.9]       |

### B3 (nominal). Share of the 24-month forecast-error variance, percent (Note B's model from 1973; exact day-of-month responses, 120 months; 90% band from Note B's bootstrap with month-aggregated shocks and 36-month responses)

| period    | shocks                       | unemployment gap    | core inflation   | 2-year yield         |
|:----------|:-----------------------------|:--------------------|:-----------------|:---------------------|
| 1974-1989 | monthly-recovered (scaled)   | 32.3 [11.9, 75.3]   | 1.2 [0.8, 9.8]   | 67.3 [38.2, 90.4]    |
| 1974-1989 | monthly-recovered (unscaled) | 115.9 [42.8, 270.8] | 4.2 [2.7, 35.1]  | 241.8 [137.1, 324.9] |
| 1990-2026 | daily-recovered, all days    | 6.5 [2.3, 14.9]     | 0.8 [0.3, 6.6]   | 115.9 [64.6, 155.0]  |
| 1990-2026 | non-announcement days        | 6.2 [2.2, 14.2]     | 0.7 [0.3, 6.2]   | 109.7 [61.3, 146.6]  |
| 1990-2026 | announcement days            | 0.2 [0.1, 0.5]      | 0.0 [0.0, 0.2]   | 3.9 [2.2, 5.1]       |
| 1990-2026 | measured surprises (Route 1) | 0.2 [0.1, 0.4]      | 0.0 [0.0, 0.2]   | 3.3 [1.8, 4.4]       |
| 1996-2026 | daily-recovered, all days    | 4.5 [1.6, 10.3]     | 0.6 [0.2, 5.3]   | 95.4 [52.7, 128.3]   |
| 1996-2026 | measured surprises (Route 1) | 0.2 [0.1, 0.4]      | 0.0 [0.0, 0.2]   | 3.7 [2.1, 4.9]       |

### B3 (real). Share of the 24-month forecast-error variance, percent (Note B's model from 1973; exact day-of-month responses, 120 months; 90% band from Note B's bootstrap with month-aggregated shocks and 36-month responses)

| period    | shocks                       | unemployment gap   | core inflation   | 2-year yield         |
|:----------|:-----------------------------|:-------------------|:-----------------|:---------------------|
| 1974-1989 | monthly-recovered (scaled)   | 10.7 [2.3, 31.4]   | 2.8 [0.6, 8.0]   | 48.5 [31.7, 60.9]    |
| 1974-1989 | monthly-recovered (unscaled) | 46.4 [9.8, 136.2]  | 12.0 [2.8, 34.6] | 210.3 [137.5, 264.3] |
| 1990-2026 | daily-recovered, all days    | 1.7 [0.3, 4.9]     | 2.4 [0.3, 6.5]   | 95.9 [60.3, 121.5]   |
| 1990-2026 | non-announcement days        | 1.6 [0.2, 4.7]     | 2.3 [0.3, 6.3]   | 92.3 [58.1, 116.8]   |
| 1990-2026 | announcement days            | 0.0 [0.0, 0.1]     | 0.1 [0.0, 0.2]   | 2.5 [1.6, 3.1]       |
| 1990-2026 | measured surprises (Route 1) | 0.0 [0.0, 0.1]     | 0.1 [0.0, 0.1]   | 2.1 [1.3, 2.6]       |
| 1996-2026 | daily-recovered, all days    | 1.3 [0.2, 3.7]     | 2.1 [0.3, 5.6]   | 81.0 [50.9, 103.2]   |
| 1996-2026 | measured surprises (Route 1) | 0.0 [0.0, 0.1]     | 0.1 [0.0, 0.2]   | 2.3 [1.4, 2.9]       |

### B3b. r*-gap with FCI: shares at 12, 24 and 36 months, percent

|   h | period    | shocks                       |   unemployment gap |   core inflation |   2-year yield |   FCI |
|----:|:----------|:-----------------------------|-------------------:|-----------------:|---------------:|------:|
|  12 | 1974-1989 | monthly-recovered (scaled)   |                3.6 |              5   |           60.1 |  47.4 |
|  12 | 1974-1989 | monthly-recovered (unscaled) |               13.1 |             18.2 |          220.5 | 173.8 |
|  12 | 1990-2026 | daily-recovered, all days    |                0.7 |              2.7 |           71.3 |  58   |
|  12 | 1990-2026 | non-announcement days        |                0.7 |              2.7 |           74.1 |  60.2 |
|  12 | 1990-2026 | announcement days            |                0   |              0.1 |            2.8 |   2.3 |
|  12 | 1990-2026 | measured surprises (Route 1) |                0   |              0.1 |            2.7 |   2.2 |
|  12 | 1996-2026 | daily-recovered, all days    |                0.6 |              2.4 |           65.6 |  53.7 |
|  12 | 1996-2026 | measured surprises (Route 1) |                0   |              0.1 |            3.1 |   2.5 |
|  24 | 1974-1989 | monthly-recovered (scaled)   |                4.6 |              7.8 |           55.6 |  37.1 |
|  24 | 1974-1989 | monthly-recovered (unscaled) |               16.8 |             28.7 |          204   | 135.9 |
|  24 | 1990-2026 | daily-recovered, all days    |                1.3 |              4.6 |           64.2 |  44.8 |
|  24 | 1990-2026 | non-announcement days        |                1.3 |              4.9 |           68.3 |  47.5 |
|  24 | 1990-2026 | announcement days            |                0.1 |              0.2 |            2.7 |   1.9 |
|  24 | 1990-2026 | measured surprises (Route 1) |                0.1 |              0.2 |            3.1 |   2.1 |
|  24 | 1996-2026 | daily-recovered, all days    |                1   |              4.2 |           56.9 |  40.9 |
|  24 | 1996-2026 | measured surprises (Route 1) |                0.1 |              0.2 |            3.3 |   2.4 |
|  36 | 1974-1989 | monthly-recovered (scaled)   |                5.1 |              9.4 |           55   |  30.6 |
|  36 | 1974-1989 | monthly-recovered (unscaled) |               18.6 |             34.4 |          201.9 | 112.1 |
|  36 | 1990-2026 | daily-recovered, all days    |                1.5 |              5.8 |           56.9 |  31.2 |
|  36 | 1990-2026 | non-announcement days        |                1.7 |              6.1 |           60.8 |  33.3 |
|  36 | 1990-2026 | announcement days            |                0.1 |              0.2 |            2.4 |   1.3 |
|  36 | 1990-2026 | measured surprises (Route 1) |                0.1 |              0.3 |            2.8 |   1.5 |
|  36 | 1996-2026 | daily-recovered, all days    |                1.4 |              5.6 |           51.8 |  29.6 |
|  36 | 1996-2026 | measured surprises (Route 1) |                0.1 |              0.3 |            2.9 |   1.6 |

### B3c. r*-gap with FCI, responses from Note B's baseline model (monthly equations from 1996): shares at 24 months, percent

| period    | shocks                       |   unemployment gap |   core inflation |   2-year yield |   FCI |
|:----------|:-----------------------------|-------------------:|-----------------:|---------------:|------:|
| 1974-1989 | monthly-recovered (scaled)   |               31.7 |             14.1 |           48.9 |  35.4 |
| 1974-1989 | monthly-recovered (unscaled) |              116.3 |             51.6 |          179.6 | 129.9 |
| 1990-2026 | daily-recovered, all days    |                8.6 |              9.5 |           56   |  42.3 |
| 1990-2026 | non-announcement days        |                9.1 |              9.6 |           59.5 |  44.9 |
| 1990-2026 | announcement days            |                0.3 |              0.4 |            2.4 |   1.8 |
| 1990-2026 | measured surprises (Route 1) |                0.4 |              0.4 |            2.6 |   2   |
| 1996-2026 | daily-recovered, all days    |                7.2 |              8.8 |           49.5 |  38.7 |
| 1996-2026 | measured surprises (Route 1) |                0.4 |              0.4 |            2.9 |   2.2 |

### B4. Historical decomposition at selected months, r*-gap with FCI (Note B's model from 1973; Route 2 = policy-direction shocks, daily from May 1990, monthly scaled before; measured = window surprises; all shocks = the data's deviation from the monthly VAR's deterministic path)

| month   |   u: all shocks |   u: Route 2 |   u: measured |   core infl. 12m: all shocks |   core infl. 12m: Route 2 |   core infl. 12m: measured |   2-yr yield: all shocks |   2-yr yield: Route 2 |   2-yr yield: measured |   FCI: all shocks |   FCI: Route 2 |   FCI: measured |
|:--------|----------------:|-------------:|--------------:|-----------------------------:|--------------------------:|---------------------------:|-------------------------:|----------------------:|-----------------------:|------------------:|---------------:|----------------:|
| 1975-06 |            2.09 |         0.1  |          0    |                         2.73 |                     -0.16 |                       0    |                    -0.56 |                 -0.47 |                   0    |              1.27 |          -0.53 |            0    |
| 1979-12 |           -1.22 |        -0.55 |          0    |                         3.89 |                      1.29 |                       0    |                    -1.4  |                 -1.01 |                   0    |              1.04 |          -1.01 |            0    |
| 1980-12 |            0.05 |        -0.63 |          0    |                         5.59 |                      1.32 |                       0    |                     0.56 |                 -0.95 |                   0    |              1.5  |          -1.19 |            0    |
| 1982-06 |            2.56 |         0.03 |          0    |                         2.9  |                      0.38 |                       0    |                     6.02 |                  3.74 |                   0    |             11.57 |           3.66 |            0    |
| 1982-12 |            3.8  |         0.04 |          0    |                         2.27 |                     -0.19 |                       0    |                     2.38 |                  1.54 |                   0    |              7.05 |           0.83 |            0    |
| 1984-06 |            0.3  |        -0.02 |          0    |                         1.08 |                     -0.4  |                       0    |                     4.18 |                  2.99 |                   0    |              7.58 |           2.46 |            0    |
| 1986-12 |           -0.14 |         0.27 |          0    |                         0.01 |                     -0.99 |                       0    |                     0.21 |                 -0.09 |                   0    |              1.39 |          -0.12 |            0    |
| 1989-06 |           -1.26 |         0.64 |          0    |                         1.07 |                     -0.8  |                       0    |                     1.46 |                 -0.91 |                   0    |              0.07 |          -0.16 |            0    |
| 1992-06 |            1.45 |        -0.18 |          0    |                        -0.03 |                      0.17 |                       0    |                    -0.32 |                 -0.83 |                   0    |             -0.47 |          -0.83 |            0    |
| 1995-06 |           -0.5  |         0.11 |          0    |                        -0.89 |                     -0.15 |                       0    |                     1.26 |                  1.19 |                   0    |             -0.94 |           0.92 |            0    |
| 1998-12 |           -1.49 |         0.07 |         -0.03 |                        -1.59 |                     -0.47 |                       0.05 |                    -0.39 |                 -0.51 |                  -0.2  |             -3.95 |          -0.79 |           -0.22 |
| 2001-12 |           -0.1  |         0.19 |         -0.13 |                        -1.21 |                     -0.2  |                       0.13 |                    -1.7  |                 -1.08 |                  -0.71 |             -1.99 |          -0.8  |           -0.79 |
| 2003-06 |            0.53 |         0.01 |         -0.2  |                        -1.41 |                      0.25 |                       0.42 |                    -2.5  |                 -1.84 |                  -0.54 |             -1.79 |          -1.45 |           -0.55 |
| 2008-12 |            1.53 |        -0.15 |         -0.2  |                        -1.79 |                      0.28 |                       0.24 |                    -0.19 |                  1.25 |                  -0.26 |              2.35 |           1.29 |           -0.44 |
| 2009-10 |            4.24 |         0.03 |         -0.23 |                        -1.69 |                     -0.13 |                       0.3  |                    -0.99 |                  0.49 |                  -0.32 |              0.8  |           0.14 |           -0.5  |
| 2013-12 |            1.14 |         0.47 |         -0.08 |                        -1.38 |                     -0.81 |                       0.17 |                    -1.23 |                  0.33 |                   0.02 |             -0.08 |           0.55 |           -0.03 |
| 2016-12 |           -0.62 |         0.17 |         -0.15 |                        -1.16 |                     -0.29 |                       0.17 |                    -1.15 |                 -0.66 |                  -0.07 |             -0.24 |          -0.44 |           -0.23 |
| 2019-12 |           -1.59 |         0.02 |         -0.04 |                        -1.38 |                      0.2  |                       0.09 |                    -0.91 |                 -1.24 |                  -0.02 |             -1.66 |          -0.97 |           -0.03 |
| 2021-06 |            0.73 |        -0.35 |         -0.04 |                         0.8  |                      0.81 |                       0.07 |                    -2.63 |                 -1.72 |                  -0    |             -2.85 |          -1.67 |           -0.02 |
| 2022-12 |           -1.66 |        -0.31 |         -0.05 |                         2.03 |                      1    |                       0.04 |                     0.86 |                  0.68 |                   0.02 |             -0.15 |           0.78 |           -0.04 |
| 2023-12 |           -1.35 |        -0.1  |         -0.07 |                         0.26 |                      0.35 |                       0.09 |                     1.27 |                  0.96 |                  -0.15 |              0.1  |           0.79 |           -0.2  |
| 2024-12 |           -1.03 |        -0.15 |         -0.1  |                        -0.05 |                      0.02 |                       0.13 |                     1.21 |                  0.97 |                  -0.17 |              0.25 |           0.58 |           -0.24 |
| 2026-09 |           -0.91 |        -0.23 |         -0.03 |                         0.16 |                      0.09 |                       0.1  |                     1.21 |                  0.55 |                   0.04 |             -0.5  |           0.3  |            0.06 |

# Appendix: first round (Route 2 from monthly VAR innovations alone; corrected rerun)

The tables below are the first report's, rerun after the correction. T1-T2: invertibility diagnostics for shocks recovered from monthly VAR innovations (the surprises' R2 on the month's innovations is 0.4-4 percent; simulations with Note B's model as the true process reproduce that). T3: variance-share bounds within the monthly VAR. T4: the monthly VAR's responses against Note B's. T6: Route 1 and monthly Route 2 at selected months.

### T1. Invertibility diagnostics (12 lags, 2020 in, window column)

| case          | data     |   first-stage F |   R2 of z on u_t (%) |   corr(recovered, z) |   sd recovered (inv.) |   sd z |   variance ratio |   leads p |   lags p |
|:--------------|:---------|----------------:|---------------------:|---------------------:|----------------------:|-------:|-----------------:|----------:|---------:|
| nominal       | avg 1973 |             5.5 |                  2.4 |                 0.14 |                 0.467 |  0.046 |              102 |      0.09 |     0.55 |
| nominal       | avg 1996 |             5.1 |                  2.6 |                 0.16 |                 0.41  |  0.046 |               79 |      0.03 |     0.88 |
| nominal       | eom 1990 |             4.4 |                  2.9 |                 0.17 |                 0.242 |  0.046 |               27 |      0.14 |     0.9  |
| nominal       | eom 1996 |             4.5 |                  2.9 |                 0.17 |                 0.24  |  0.046 |               27 |      0.12 |     0.89 |
| nominal + FCI | avg 1973 |             0.8 |                  0.5 |                 0.03 |                 0.387 |  0.046 |               70 |      0.04 |     0.04 |
| nominal + FCI | avg 1996 |             1.9 |                  1.2 |                 0.07 |                 0.34  |  0.046 |               54 |      0.02 |     0.21 |
| nominal + FCI | eom 1990 |             1.9 |                  3.2 |                 0.16 |                 0.21  |  0.046 |               21 |      0.26 |     0.25 |
| nominal + FCI | eom 1996 |             1.6 |                  3.1 |                 0.15 |                 0.207 |  0.046 |               20 |      0.28 |     0.27 |
| real          | avg 1973 |             4.6 |                  1.6 |                 0.11 |                 0.498 |  0.046 |              116 |      0.1  |     0.46 |
| real          | avg 1996 |             5.2 |                  2.2 |                 0.14 |                 0.421 |  0.046 |               83 |      0.18 |     0.62 |
| real          | eom 1990 |             6.9 |                  3.5 |                 0.19 |                 0.223 |  0.046 |               23 |      0.1  |     0.79 |
| real          | eom 1996 |             6.9 |                  3.5 |                 0.18 |                 0.221 |  0.046 |               23 |      0.11 |     0.81 |
| real + FCI    | avg 1973 |             0.8 |                  0.4 |                 0.02 |                 0.404 |  0.046 |               76 |      0.06 |     0.16 |
| real + FCI    | avg 1996 |             2.4 |                  1.4 |                 0.07 |                 0.338 |  0.046 |               54 |      0.28 |     0.28 |
| real + FCI    | eom 1990 |             3.9 |                  3.5 |                 0.17 |                 0.196 |  0.046 |               18 |      0.34 |     0.31 |
| real + FCI    | eom 1996 |             3   |                  3.2 |                 0.16 |                 0.193 |  0.046 |               17 |      0.37 |     0.28 |
| r*-gap        | avg 1973 |             5   |                  1.7 |                 0.11 |                 0.491 |  0.046 |              113 |      0.13 |     0.53 |
| r*-gap        | avg 1996 |             5.7 |                  2.3 |                 0.14 |                 0.419 |  0.046 |               82 |      0.16 |     0.66 |
| r*-gap        | eom 1990 |             8.1 |                  3.8 |                 0.19 |                 0.22  |  0.046 |               23 |      0.13 |     0.81 |
| r*-gap        | eom 1996 |             8   |                  3.7 |                 0.19 |                 0.218 |  0.046 |               22 |      0.12 |     0.83 |
| r*-gap + FCI  | avg 1973 |             0.9 |                  0.4 |                 0.05 |                 0.408 |  0.046 |               78 |      0.07 |     0.21 |
| r*-gap + FCI  | avg 1996 |             3.5 |                  1.7 |                 0.09 |                 0.34  |  0.046 |               54 |      0.19 |     0.5  |
| r*-gap + FCI  | eom 1990 |             5.1 |                  3.5 |                 0.18 |                 0.196 |  0.046 |               18 |      0.2  |     0.48 |
| r*-gap + FCI  | eom 1996 |             4.4 |                  3.5 |                 0.17 |                 0.193 |  0.046 |               17 |      0.19 |     0.5  |

### T1b. Bootstrap distribution of the diagnostics (500 draws)

| case          | data     | R2 (%), median [5, 95]   | corr, median [5, 95]   |
|:--------------|:---------|:-------------------------|:-----------------------|
| nominal       | avg 1973 | 2.4 [0.7, 5.3]           | 0.13 [0.04, 0.21]      |
| nominal       | eom 1990 | 3.0 [0.7, 7.6]           | 0.16 [0.07, 0.27]      |
| nominal + FCI | avg 1973 | 1.1 [0.2, 3.7]           | 0.03 [-0.04, 0.13]     |
| nominal + FCI | eom 1990 | 3.5 [1.3, 7.6]           | 0.15 [0.04, 0.25]      |
| real          | avg 1973 | 1.7 [0.5, 3.9]           | 0.10 [0.01, 0.17]      |
| real          | eom 1990 | 3.8 [1.2, 7.4]           | 0.18 [0.09, 0.26]      |
| real + FCI    | avg 1973 | 1.0 [0.2, 2.9]           | 0.02 [-0.05, 0.10]     |
| real + FCI    | eom 1990 | 3.8 [1.6, 7.8]           | 0.16 [0.08, 0.25]      |
| r*-gap        | avg 1973 | 1.8 [0.6, 4.0]           | 0.11 [0.02, 0.17]      |
| r*-gap        | eom 1990 | 4.0 [1.4, 8.1]           | 0.18 [0.10, 0.27]      |
| r*-gap + FCI  | avg 1973 | 0.9 [0.2, 2.8]           | 0.05 [-0.03, 0.12]     |
| r*-gap + FCI  | eom 1990 | 4.0 [2.0, 7.4]           | 0.17 [0.09, 0.25]      |

### T2. Note B's model as the true process (200 simulated samples, 1996-2026) against the data

| data   | statistic              | Note B as truth: median [5, 95]   |   data 1996-2026 |
|:-------|:-----------------------|:----------------------------------|-----------------:|
| avg    | R2 of z on u_t         | 0.022 [0.005, 0.050]              |            0.017 |
| avg    | corr(recovered, z)     | 0.110 [0.027, 0.201]              |            0.091 |
| avg    | variance ratio         | 73.509 [50.803, 101.895]          |           54.2   |
| avg    | u share at 24 m, upper | 0.078 [0.012, 0.246]              |            0.036 |
| avg    | u share at 24 m, lower | 0.001 [0.000, 0.004]              |            0.001 |
| eom    | R2 of z on u_t         | 0.046 [0.017, 0.087]              |            0.035 |
| eom    | corr(recovered, z)     | 0.189 [0.099, 0.278]              |            0.169 |
| eom    | variance ratio         | 24.514 [17.088, 33.512]           |           17.5   |
| eom    | u share at 24 m, upper | 0.074 [0.013, 0.248]              |            0.033 |
| eom    | u share at 24 m, lower | 0.003 [0.001, 0.011]              |            0.002 |

### T3. Share of the 24-month forecast-error variance due to policy shocks, percent (12 lags, 2020 in)

| data     | case          |   u: lower (VAR) |   u: lower (Note B model) |   u: upper 1996- |   u: upper full | u: upper full, 90% band   |   u: upper full, P1 |   pi: lower |   pi: upper full |   yield: lower |   yield: upper full |
|:---------|:--------------|-----------------:|--------------------------:|-----------------:|----------------:|:--------------------------|--------------------:|------------:|-----------------:|---------------:|--------------------:|
| avg 1973 | nominal       |              0   |                       0.7 |              2.9 |             9.6 | [0.3, 19.6]               |                29.9 |         0   |              1   |            0.6 |                76.4 |
| avg 1973 | nominal + FCI |              0   |                       0   |              2.5 |             6.5 | [0.9, 28.0]               |                13.6 |         0   |              0.6 |            0.2 |                17.2 |
| avg 1973 | real          |              0   |                       0.3 |              1.2 |             3.5 | [0.3, 10.9]               |                26.4 |         0   |              3.4 |            0.7 |                88.6 |
| avg 1973 | real + FCI    |              0.1 |                       0   |              4.5 |            10.4 | [1.5, 31.3]               |                17.2 |         0   |              3.4 |            0.3 |                24.5 |
| avg 1973 | r*-gap        |              0   |                       0   |              0.1 |             0.4 | [0.3, 8.9]                |                19.7 |         0   |              6.4 |            0.8 |                91.6 |
| avg 1973 | r*-gap + FCI  |              0.1 |                       0.3 |              7.7 |            17.6 | [3.8, 43.7]               |                10   |         0   |              5.1 |            0.4 |                33.7 |
| eom 1990 | nominal       |              0.7 |                           |             18.8 |            21.6 | [6.2, 38.8]               |                20   |         0.1 |              2.1 |            3.3 |                88.8 |
| eom 1990 | nominal + FCI |              0.1 |                           |              1   |             1.2 | [0.4, 8.8]                |                12.1 |         0.1 |              3.4 |            1.9 |                41.9 |
| eom 1990 | real          |              0.4 |                           |              9   |            10.3 | [1.7, 26.2]               |                14.7 |         0.1 |              1.4 |            3.6 |                82.5 |
| eom 1990 | real + FCI    |              0   |                           |              0.4 |             0.5 | [0.3, 8.0]                |                 9.9 |         0.2 |              4.5 |            2.5 |                48.3 |
| eom 1990 | r*-gap        |              0.1 |                           |              1   |             1.2 | [0.5, 13.0]               |                 5.5 |         0.2 |              4.4 |            3.5 |                78   |
| eom 1990 | r*-gap + FCI  |              0.1 |                           |              2.1 |             2.4 | [0.5, 14.1]               |                18.5 |         0.5 |              9.8 |            2.8 |                52.1 |

### T4. Responses per +1 pp window surprise: the monthly VAR with the window column against Note B's model (same step; Note B from 1973 for avg 1973, else from 1996)

| case          | data     |   u12 VAR |   u12 Note B |   u24 VAR |   u24 Note B |   P24 VAR |   P24 Note B |   yield h=1 VAR |
|:--------------|:---------|----------:|-------------:|----------:|-------------:|----------:|-------------:|----------------:|
| nominal       | avg 1973 |     -0.15 |        -0.33 |     -0.08 |        -0.17 |      0.09 |         0.19 |            0.63 |
| nominal       | avg 1996 |     -0.54 |        -0.81 |     -0.37 |        -0.49 |      0.02 |         0.02 |            0.6  |
| nominal       | eom 1990 |     -0.77 |        -0.81 |     -0.47 |        -0.49 |      0.05 |         0.02 |            1.12 |
| nominal       | eom 1996 |     -0.9  |        -0.81 |     -0.63 |        -0.49 |      0.06 |         0.02 |            1.07 |
| nominal + FCI | avg 1973 |      0.19 |        -0.02 |      0.13 |        -0.12 |      0.03 |         0.11 |            0.59 |
| nominal + FCI | avg 1996 |     -0.09 |        -0.05 |     -0.04 |         0.16 |     -0.22 |        -0.42 |            0.55 |
| nominal + FCI | eom 1990 |     -0.19 |        -0.05 |     -0.13 |         0.16 |     -0.21 |        -0.42 |            0.98 |
| nominal + FCI | eom 1996 |     -0.14 |        -0.05 |     -0.09 |         0.16 |     -0.36 |        -0.42 |            0.92 |
| real          | avg 1973 |     -0.1  |        -0.15 |     -0.05 |        -0.08 |     -0.2  |        -0.31 |            0.61 |
| real          | avg 1996 |     -0.39 |        -0.6  |     -0.25 |        -0.33 |     -0.07 |        -0.11 |            0.46 |
| real          | eom 1990 |     -0.59 |        -0.6  |     -0.33 |        -0.33 |     -0.13 |        -0.11 |            0.97 |
| real          | eom 1996 |     -0.65 |        -0.6  |     -0.46 |        -0.33 |     -0.16 |        -0.11 |            0.92 |
| real + FCI    | avg 1973 |      0.24 |         0.1  |      0.16 |         0    |     -0.25 |        -0.39 |            0.59 |
| real + FCI    | avg 1996 |      0    |         0.09 |      0.02 |         0.23 |     -0.26 |        -0.48 |            0.45 |
| real + FCI    | eom 1990 |     -0.12 |         0.09 |     -0.1  |         0.23 |     -0.38 |        -0.48 |            0.89 |
| real + FCI    | eom 1996 |     -0.02 |         0.09 |     -0.04 |         0.23 |     -0.49 |        -0.48 |            0.84 |
| r*-gap        | avg 1973 |     -0.03 |        -0.05 |     -0    |        -0.01 |     -0.3  |        -0.5  |            0.6  |
| r*-gap        | avg 1996 |     -0.15 |        -0.29 |     -0.02 |        -0.07 |     -0.24 |        -0.44 |            0.46 |
| r*-gap        | eom 1990 |     -0.24 |        -0.29 |     -0.01 |        -0.07 |     -0.45 |        -0.44 |            0.98 |
| r*-gap        | eom 1996 |     -0.19 |        -0.29 |     -0.03 |        -0.07 |     -0.51 |        -0.44 |            0.94 |
| r*-gap + FCI  | avg 1973 |      0.29 |         0.18 |      0.18 |         0.14 |     -0.3  |        -0.63 |            0.6  |
| r*-gap + FCI  | avg 1996 |      0.18 |         0.33 |      0.18 |         0.49 |     -0.38 |        -0.8  |            0.49 |
| r*-gap + FCI  | eom 1990 |      0.23 |         0.33 |      0.28 |         0.49 |     -0.71 |        -0.8  |            0.96 |
| r*-gap + FCI  | eom 1996 |      0.33 |         0.33 |      0.3  |         0.49 |     -0.77 |        -0.8  |            0.94 |

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
| avg 1973 |     12 | dummy  | P1       |      0.4 |   0.06 |               60 | 11.1                      |
| avg 1973 |     12 | in     | WE2      |      0.4 |   0.08 |               46 | n.a.                      |
| avg 1973 |     12 | dummy  | WE2      |      0.4 |   0.06 |               44 | n.a.                      |
| avg 1996 |      3 | in     | WE       |      2.6 |   0.12 |               67 | 2.2                       |
| avg 1996 |      3 | in     | P1       |      2.6 |   0.16 |               90 | 2.1                       |
| avg 1996 |      3 | in     | WE2      |      2.6 |   0.17 |               35 | n.a.                      |
| avg 1996 |      6 | in     | WE       |      2.2 |   0.12 |               60 | 4.7                       |
| avg 1996 |      6 | in     | P1       |      2.2 |   0.15 |               80 | 0.3                       |
| avg 1996 |      6 | in     | WE2      |      2.2 |   0.16 |               31 | n.a.                      |
| avg 1996 |     12 | in     | WE       |      1.7 |   0.09 |               54 | 3.6                       |
| avg 1996 |     12 | dummy  | WE       |      1.5 |   0.1  |               50 | 5.6                       |
| avg 1996 |     12 | in     | P1       |      1.7 |   0.13 |               60 | 1.7                       |
| avg 1996 |     12 | dummy  | P1       |      1.5 |   0.12 |               52 | 1.5                       |
| avg 1996 |     12 | in     | WE2      |      1.7 |   0.14 |               27 | n.a.                      |
| avg 1996 |     12 | dummy  | WE2      |      1.5 |   0.17 |               25 | n.a.                      |
| eom 1990 |      3 | in     | WE       |      4.2 |   0.2  |               21 | 1.4                       |
| eom 1990 |      3 | in     | P1       |      4.2 |   0.2  |               19 | 6.0                       |
| eom 1990 |      6 | in     | WE       |      3.9 |   0.19 |               20 | 2.5                       |
| eom 1990 |      6 | in     | P1       |      3.9 |   0.19 |               17 | 11.4                      |
| eom 1990 |     12 | in     | WE       |      3.5 |   0.18 |               18 | 2.4                       |
| eom 1990 |     12 | dummy  | WE       |      4   |   0.18 |               17 | 5.1                       |
| eom 1990 |     12 | in     | P1       |      3.5 |   0.18 |               14 | 18.5                      |
| eom 1990 |     12 | dummy  | P1       |      4   |   0.2  |               11 | 4.2                       |
| eom 1996 |      3 | in     | WE       |      4.2 |   0.2  |               21 | 1.1                       |
| eom 1996 |      3 | in     | P1       |      4.2 |   0.2  |               20 | 5.1                       |
| eom 1996 |      6 | in     | WE       |      3.8 |   0.19 |               19 | 3.2                       |
| eom 1996 |      6 | in     | P1       |      3.8 |   0.19 |               17 | 13.1                      |
| eom 1996 |     12 | in     | WE       |      3.5 |   0.17 |               17 | 3.3                       |
| eom 1996 |     12 | dummy  | WE       |      4.2 |   0.19 |               16 | 5.5                       |
| eom 1996 |     12 | in     | P1       |      3.5 |   0.18 |               13 | 21.9                      |
| eom 1996 |     12 | dummy  | P1       |      4.2 |   0.2  |               10 | 6.8                       |

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
