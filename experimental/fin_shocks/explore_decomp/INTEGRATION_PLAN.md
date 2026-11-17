# Note B: Findings of the November 2026 Explorations and a Plan to Integrate Them

Written 17 Nov 2026 at the end of the exploration session. Branch `claude/sharp-goodall-wffoqw`; it contains the FS-A75 weights branch (`claude/fci-note-b-weights-dcfgbi`) and nothing of it is on `main` yet. All exploration code and results are in `experimental/fin_shocks/explore_decomp/`; decisions are in `DECOMP_QA.md` (D-A1 to D-A24). Note B's package (`baseline/`) and paper (`paper/`) were not changed. This file has three parts: what we found (Part 1), the decisions the author has to take before integration (Part 2), and the steps to execute once they are taken (Part 3).

**Guiding principle (author, 17 Nov 2026): one data type throughout the paper.** The paper currently mixes two: Note B's model uses monthly averages of the daily financial variables, while the benchmark monthly VARs (and the standard-methods estimators) use end-of-month values since FS-A48 (10 Nov). That switch was a mistake: it put a second data convention into the paper, and because no end-of-month FCI exists before 1990 it removed the 1973 versions of the benchmarks without this being made clear to the author. The fix is to use monthly averages everywhere (the only type available from 1973, and the one Note B's model already uses) and to remove end-of-month series from the code and the paper (Phase 2 below). The end-of-month results in this folder are kept only as a record.

Conventions used below: r*-gap = the 2-year yield and FCI relative to r*; "with the FCI" = Note B's model with the 2-year yield and the FCI; responses per +1 pp window surprise on the 2-year yield; 12 lags; 90 percent intervals unless stated; `**`/`*` = 5/10 percent.

---

## Part 1. What we found

### 1.1 Data and samples

* **Two different kinds of model.** Note B's baseline is the mixed-frequency model: a daily block (2-year yield, FCI) and monthly equations (unemployment gap, core PCE inflation) on lagged monthly averages of the daily variables. Its monthly equations can start in 1973 (monthly series before the daily data start in 1990). The paper's *benchmark* monthly VARs (proxy VAR, window-impact VAR, Cholesky; Sections 3.1 and 4.4) are purely monthly.
* **Two data types in the paper: the error to remove.** The benchmark VARs were switched to end-of-month values on 10 Nov (FS-A48) while Note B's model kept monthly averages. The end-of-month FCI and the real and r*-gap 2-year yields exist only from 1990 (nominal 2-year from 1976), so the switch also removed the benchmarks' 1973 versions. The 1973 benchmark runs before the switch (FS-A43) were in monthly averages. Every current end-of-month exhibit runs on its full stated sample (1996-2026: 369 months; Cholesky 1984-2026: 513), so the error is the mixing of data types and the lost 1973 versions, not a truncated sample. I also misdescribed this in this session (I first said the 1973 runs had started in 1990; corrected in DECOMP_QA).
* **The unemployment gap** is the unemployment rate less the CBO natural rate (UNRATE minus NROU, quarterly NROU interpolated to months; October 2025 interpolated) [verified in `baseline/lib/noteA.py`].

### 1.2 Note B's model from 1973 (A1, A4-A7, G, H; `results_core/`, `results_ip/`, `results_ff/`, `results_1y/`, `results_bjmw/`)

* **Reproduction.** Run from 1996, the exploration code reproduces every stored baseline and R1 result to the last digit [verified].
* **All versions from 1973, 2020 in** (Table A1 in REPORT.md): prices fall in the real and r*-gap versions with and without the FCI (r*-gap with FCI -0.63** at 24 m); the nominal version has no price fall. The unemployment rise with the FCI is significant at 12 m in two versions but not at 24 m (r*-gap +0.14 against +0.49* from 1996).
* **2020.** Dropping March-December 2020 (= month dummies; robustness R1b/R1c) strengthens the 1973 results: r*-gap with FCI, unemployment +0.33** / +0.24 / +0.15 at 12/24/36 m, price level -0.76** at 24 m, -1.14** at 36 m.
* **Regime split** (G, point estimates). Monthly equations on 1973-1995 alone: conventional and strong in every version, even the nominal yield alone (unemployment +0.23/+0.35 at 12/24 m; price level -0.71 at 24 m). On 1996-2026 alone: the paper's results (puzzles without the FCI, fixed by the FCI). Pooled 1973-2026 is weaker than either half. The puzzles are a post-1996 phenomenon.
* **Brennan, Jacobson, Matthes and Walker (FEDS 2024-011r1, read, D-A19).** Their proxy VAR (log CPI, log IP, EBP, end-of-month 2-year; 1973-Feb 2020; shocks 1995-2019 summed by month; 8 lags; Bayesian; 68 percent bands) finds IP and CPI falling for all main shock series. Note B's model on their sample (1973-2019, announcements through 2019; A7): conventional signs throughout; unemployment significant at 12 m, positive at 24 m (significant with 68 percent bands without the FCI); prices fall significantly in the real and r*-gap versions; the FCI adds little on this sample. With monthly equations from 1996 to 2019 the puzzles are strong without the FCI and the FCI removes them without significance: Note B's significant 1996 results need 2020-2026.
* **Extensions** (D-A15 to D-A17). Industrial production as a third monthly variable: unemployment and prices as before; IP rises after a tightening with the yield alone from 1996 (+2.1** nominal) and falls with the FCI (not significant). The funds rate as a third financial variable (daily and monthly; impact from the MP1 window move, 0.72; DFF check 0.89; point estimates): responses change little; the funds rate rises to about +0.95 by 12 months. The 1-year yield in place of the 2-year (window move = 0.78 x the 2-year's; point estimates): the same responses for the same-size surprise.
* **Proposed baselines** (D-A21; `figures/H_baseline_irfs.png`): r*-gap, 12 lags, March-December 2020 dropped, from 1996 and from 1973. With the FCI: unemployment +0.41**/+0.45**/+0.40 (1996) and +0.33**/+0.24/+0.15 (1973); price level -0.69**/-0.94** (1996) and -0.76**/-1.14** (1973) at 24/36 m.

### 1.3 The benchmark monthly VARs (A2, A3; `results_core/monthly_benchmarks.csv`, `avg_vs_eom.csv`)

* The exploration code reproduces the paper's end-of-month 1996 proxy and window-impact VARs exactly [verified].
* From 1973 in monthly averages: the window-impact VAR with the FCI (r*-gap) gives unemployment +0.29** at 12 m and price level -0.30* at 24 m; the proxy VAR with the FCI is uninformative (first-stage F 0.9); without the FCI the nominal proxy VAR still has unemployment falling (-0.25*).
* **What moving the benchmarks to monthly averages will change** (A3; same samples, both data types; for the record, not for the paper): the benchmark price responses are about half as large in monthly averages (r*-gap with FCI, window-impact VAR, 24 m: -0.71 end of month 1991, -0.37 averages 1991, -0.30 averages 1973), because an announcement moves this month's average by only 0.47 and a monthly VAR does not reproduce the further rise the next month. This is the temporal aggregation that Section 4.6 of the draft already discusses; with one data type it becomes part of the case for the mixed-frequency model rather than a footnote on units. The proxy VAR's weakness from 1973 is the sample (F 4.0 from 1991, 0.9 from 1973). Note B's own model is unaffected (it simulates the daily path).

### 1.4 Historical and variance decompositions (REPORT.md Part B; B1-B5)

* **Route 1** (measured window surprises through Note B's model, 1996 on): identified with no extra assumption; tiny variance shares (under 1 percent of unemployment and core inflation).
* **Route 2 from monthly VAR innovations** (shock = b'Σ⁻¹u / b'Σ⁻¹b): invertibility fails. The surprises' R² on the month's innovations is 0.4-4 percent, the recovered shock correlates 0.02-0.19 with them, and simulations with Note B's model as the true process reproduce these values: the failure is a property of the paper's own model.
* **Route 2 from daily innovations** (Note B's daily block; shock = the yield-and-FCI movement in the window direction b = (1, b_F) on every day): on announcement days it correlates 0.66 with the measured surprise. Before 1990: monthly-recovered shocks scaled (0.52) to the daily shocks' size over the overlap (correlation 0.56).
* **With the proposed baselines** (B5; 2020 decomposed with the estimated coefficients; shares exclude March-December 2020; D-A22 to D-A24), r*-gap with FCI, 24-month shares: 1990-2026 daily-recovered shocks 8.9 percent of the unemployment gap and 7.8 percent of core inflation (model from 1973; 18.0 and 9.4 from 1996), 62 percent of the 2-year yield and 42 percent of the FCI; 1974-89: 11.9 and 10.1 percent. Almost all from days without an announcement; measured surprises under 1 percent. History: easing 1979-80, tightening 1982-84, easing 2001-03 and 2020-21 (core inflation about +1 pp by 2021-22), tightening 2022-24.

### 1.5 Alignment issues found (not yet acted on)

1. Section 5.1 of the draft says that "with 2020 dropped or the start moved to 1973, the results are those of the baseline". This holds for prices; for unemployment at 24 m from 1973 with 2020 in, it does not (+0.14, not significant).
2. Root `CLAUDE.md` glossary: Note B's monthly block is described with a "quadratic trend"; the package has no trend.
3. `PROJECT_MEMORY.md` section 9: the 16 Nov line says `claude/jolly-gates-bocjse` is not merged; it is on `main`.
4. The FS-A75 weights branch and this branch are not merged to `main`.

---

## Part 2. Decisions for the author (in order; each changes what Part 3 does)

| # | Decision | Options | My recommendation |
|---|---|---|---|
| D1 | Treatment of 2020 in the baseline | (a) keep 2020 in (current draft); (b) drop March-December 2020 in every case | (b): the same treatment in all samples; the 2020 unemployment spike otherwise dominates the long-sample estimates and the variance shares; Note A's VAR already dummies 2020 |
| D2 | Role of the 1973 sample | (a) robustness only (r*-gap, Section 5.1); (b) a second baseline, all versions, next to 1996 | (b) for the r*-gap baseline figure and table; all versions in the appendix |
| D3 | Regime split (1973-1995 vs 1996-2026) | (a) not reported; (b) reported in Section 5.1 with a formal break test | (b): it explains why the long sample is weaker and that the puzzles are a post-1996 phenomenon |
| D4 | Brennan et al. comparison | (a) none; (b) a robustness row on their sample (1973-2019), noting their 68 percent bands | (b), short, in Section 5.1 |
| D5 | Data type | Decided by the author (17 Nov): one data type throughout | Monthly averages everywhere (the only type back to 1973; the model's own); end-of-month series removed from code and paper (Phase 2). To confirm. |
| D6 | Decompositions in the paper | (a) none; (b) Route 1 only; (c) Route 1 and Route 2 (daily, with the monthly splice) as a new subsection, the monthly-invertibility diagnostic in the appendix | (c), as a subsection of Results after the tradeoff, with Route 2 framed as policy-direction shocks |
| D7 | Propagation model for Route 2 | 1973 model, 1996 model, or both | the 1973 model (covers the whole period), the 1996 model as a check |
| D8 | 2020 in the decomposition | (a) inferred with the estimated coefficients (D-A23 main); (b) absorbed by the dummies | (a), with (b) as robustness; shares exclude 2020 (D-A24) |
| D9 | Splice before 1990 | scaled (sd ratio, 0.52), unscaled, or projection slope | scaled; unscaled reported |
| D10 | Extensions | IP, funds rate, 1-year yield: robustness rows, appendix only, or not reported | IP and funds rate as robustness rows in Section 5; the 1-year yield in the appendix |
| D11 | Intervals | 90 percent throughout (current convention) | keep 90; give 68 only where comparing with Brennan et al. |

---

## Part 3. Execution plan (after Part 2 is decided)

Each phase ends with its checks passing and a commit. Work on a short branch from `main` after merging (Phase 0). Estimated run times assume 4 cores.

### Phase 0. Housekeeping (no new results)

1. Merge the FS-A75 weights branch and this branch to `main` once the author has merged the text of `paper/mp_transmission_session_weights.tex` (FS-A75 open item).
2. Fix the stale text in 1.5 (2) and (3).
3. Record Part 2's answers in `fin_shocks/FS_QA.md` as a new FS-A entry that points to DECOMP_QA D-A1 to D-A24.

### Phase 1. The model and the case list (`baseline/lib/model.py`, `baseline/cases.py`, `03_estimate.py`)

1. If D1(b): make `t2020="out"` the default in `cases.py` (`panel()` base) and keep a robustness panel with 2020 in. Rerun everything (about 70 minutes); every macro in `report/numbers*.tex` changes.
2. If D2(b): a panel "B73" with all three versions, without and with the FCI, monthly equations from 1973 (the code exists; A1 shows it runs).
3. If D3(b): allow the monthly equations to end before the daily block (a separate monthly end date in `macro_data` and `estimate`, so a 1973-1995 monthly sample can use the daily block from 1996); add panels for 1973-1995 and 1996-2026 splits; add a break test (financial-coefficient interactions with a post-1996 dummy in the monthly equations; Wald test with the block bootstrap).
4. If D4(b): an announcement-end option in the case definition (the A7 approach: restrict `event_index` to announcements through 2019) and a panel "R1f" on 1973-2019.
5. If D10: macro option `u,pi,ip` (IP = 100 log INDPRO; copy `INDPRO.csv` into `baseline/data/` and record it in `SOURCES.md`); an `fci` option that adds the funds rate to the daily block with the MP1 window impact (the A5 wrapper becomes code in `model.py`: `daily_frame`, `fin_monthly`, `impact`, `irf_b`); a policy-rate option for the 1-year yield (the A6 construction: `DGS1.csv`, `EXPINF1YR`, the 0.78 window ratio, in `daily.py` and `model.py`).
6. Checks: the existing panels reproduce their stored results exactly when their options are unchanged; the new panels reproduce the exploration numbers (`results_core/`, `results_ip/`, `results_bjmw/`) to the rounding of the stored files.

### Phase 2. One data type: remove end-of-month series from the code and the paper

Inventory of end-of-month use (checked 17 Nov 2026):

| Where | What | Change |
|---|---|---|
| `baseline/lib/monthly.py` (`run_case`), `04_monthly_var.py`, `cases.py` (`MONTHLY`, `MONTHLY_START`, and the comment that a 1973 start is not offered) | benchmark proxy VAR (P1) and window-impact VAR (WE) on `fin_eom`; window column from `e0` | `fin_monthly`; window column from `f0[0]` (month-average response); proxy VAR in the window unit; starts 1996 and 1973; bootstrap drawing pre- and post-1996 rows separately (as `A2_monthly.py`) |
| `baseline/lib/litstyle.py`, `08_literature_style.py` | Cholesky (2-year from `fin_eom`; funds rate last weekday) and proxy VAR without the FCI | monthly averages of both; add 1973 starts |
| `baseline/lib/simulate.py`, `06_proxy_simulation.py` | the simulated proxy VAR and its "truth" in the end-of-month unit (`e0`) | simulate and estimate in monthly averages; truth per +1 pp in the window |
| `baseline/lib/model.py` | `fin_eom`; `path_rows` writes `kind="fin_eom"` | remove (or keep only for the record outside the package) |
| `07_report.py` (lines near 168 and 227-230), `07b_report_extensions.py` (near 122) | macros `bl:eom:*`; first-stage diagnostics on end-of-month data | monthly averages; remove the `eom` macros |
| `paper/mp_transmission.tex` Section 3.1 (line ~277), 3.2 (~292), 3.3 (~308), Section 4.4, Appendix "Relation to a Monthly VAR and a Proxy VAR", Appendix "Construction and Estimation Details" | "end-of-month two-year yield"; the 0.95-0.99 unit statement | one statement of the data: monthly averages throughout; the unit is +1 pp in the window |
| `fin_shocks/FS_QA.md` FS-A48 | the decision to use end of month | a new FS-A entry that reverses it and says why |

Steps:
1. Add a guard: every case stops with an error if its requested start precedes the first month with data (no silent truncation).
2. Make the code changes in the table; remove `fin_eom` from every path that feeds the paper.
3. Rerun steps 04, 06, 08 and the report scripts; every benchmark and standard-methods number in the paper changes.
4. Checks: no exhibit or macro uses end-of-month data (grep for `fin_eom`, `e0`, `eom` in the package and for "end of the month" / "end-of-month" in the paper); the 1996 monthly-average benchmarks reproduce `explore_decomp/results_core/avg_vs_eom.csv` (avg 1996 rows) and the 1973 ones `monthly_benchmarks.csv` (avg 1973 rows); Note B's model results unchanged.

### Phase 3. Decompositions (new `baseline/lib/decomp.py` and `13_decomposition.py`)

1. Port, in this order: the daily shock recovery (`B1`/`B5.daily_shocks`), the monthly-VAR recovery and the splice (`lib_r2.run`, `B5`), Note B's position-specific responses (`B5.NoteB`), contributions and variance shares with the two 2020 treatments (`B5.contributions`, D-A23/D-A24), the bootstrap bands from `model.estimate` draws, Route 1.
2. Port the diagnostics: the monthly invertibility table and the simulation with Note B's model as the truth (`01_run.py`, `05_sim_invertibility.py`; the simulation belongs next to `06_proxy_simulation.py`).
3. Outputs: `results/decomp_shares.csv`, `results/decomp_hd_*.csv`, `results/decomp_diagnostics.csv`.
4. Check: the B5 tables (`results_route2_base/tables_infer.md`, `tables_absorb.md`) to the rounding of the stored files; the diagnostics against `results/summary.csv` and `results/sim_invertibility.csv`.
5. Run time: about 30 minutes (four bootstrap estimations and the share bands).

### Phase 4. Report scripts (`07d_report_decomp.py`, and changes to 07/07b/07c)

1. New exhibits: the two-baseline IRF figure (as `H_baseline_irfs.png`); a 1973 table for all versions; the regime-split table; the Brennan et al. sample row; the benchmark VARs in monthly averages from 1996 and 1973; the decomposition figure (as `B5_hd_rstar_infer.png`), the shares table, and the invertibility table (appendix).
2. Macros in `report/numbers_decomp.tex`; every qualitative claim asserted with `chk(...)`, as in 07b/07c.
3. House style via `lib/latex_style.py`.

### Phase 5. Paper text (read `experimental/WRITING_GUIDE.md` first; one section at a time, each approved by the author)

1. Section 2.5 (A Mixed-Frequency VAR) and Appendix "Relation to a Monthly VAR and a Proxy VAR": one paragraph on why the window identification does not need invertibility, with the monthly diagnostic (D6).
2. Section 3.2 (Baseline): the two baselines if D2(b), and the 2020 treatment if D1(b).
3. New Section 3.5, "How Much Do Policy Shocks Explain?": Route 1 and Route 2, the shares and the history (D6-D9).
4. Sections 3.1 and 4.4 and the appendices: one data type (monthly averages) everywhere; the benchmarks from 1996 and 1973; the temporal-aggregation point stated once (Section 4.6) (D5, Phase 2).
5. Section 5.1 (The Sample): the corrected sentence on 1973 (1.5 (1)), the regime split (D3), the Brennan et al. sample (D4).
6. Section 4 or 5 rows for IP and the funds rate (D10).
7. Abstract, introduction and conclusion last, only if the decomposition becomes a headline result.
8. Bibliography: Brennan et al. is in `references.bib`; add Plagborg-Moller and Wolf (2022, variance decompositions with IV) only after reading it [not read in this session].

### Phase 6. Verification and wrap-up

1. Full package run from raw data; all `chk(...)` claims pass; the paper builds with no undefined references.
2. Sync check: every number in the text is a macro; the exploration numbers quoted in DECOMP_QA match the package to rounding.
3. Update `PROJECT_MEMORY.md` section 9 and `experimental/README.md`; merge to `main`.

---

## Part 4. Caveats to carry into the paper (stated as facts in the robustness section)

* Route 2 assumes that within a day the policy shock is recoverable from the yield and FCI innovations; on days without an announcement the recovered shock includes any news that moves the two in the window proportion.
* The daily block is estimated from 1996 and applied from 1990; before 1990 the shocks come from the monthly VAR, scaled.
* In the 1973 runs the shock size and the daily dynamics are the post-1996 ones; only the monthly equations use the long sample.
* The 1-year window move and the funds-rate impact are constructed (no intraday 1-year series in USMPD; MP1 for the funds rate).
* Unverified here: Plagborg-Moller and Wolf (2022) on IV variance decompositions; Kuttner and Gurkaynak-Sack-Swanson start dates for futures-based surprises; Romer-Romer and Cook-Hahn data for pre-1990 measured shocks.

## Part 5. Where everything is

| Topic | Scripts (explore_decomp/) | Results | Decisions |
|---|---|---|---|
| Route 2 first round (monthly), diagnostics, simulation | `lib_r2.py`, `01`-`08` | `results/` | D-A1 to D-A10 |
| Note B's model from 1973, all versions | `A1_core.py`, `C_core_tables.py` | `results_core/` | D-A11 |
| Benchmark monthly VARs; data type vs sample | `A2_monthly.py`, `A3_avg_vs_eom.py` | `results_core/monthly_benchmarks.csv`, `avg_vs_eom.csv` | D-A11 |
| Route 2 daily (2020 in) | `B1`-`B4`, `D_figures.py`, `E_tables.py` | `results_route2/` | D-A12 to D-A14 |
| IP, funds rate, 1-year yield | `A4_ip.py`, `A5_ff.py`, `A6_1y.py`, `F_*.py` | `results_ip/`, `results_ff/`, `results_1y/` | D-A15 to D-A17 |
| 1973 puzzle, regime split; Brennan et al. | `G_1973_puzzle.py`, `A7_bjmw.py` | `results_core/puzzle_1973.csv`, `results_bjmw/` | D-A18 to D-A20 |
| Proposed baselines; Route 2 with them | `H_baseline_irfs.py`, `B5_route2_baseline.py`, `F_route2_base.py` | `results_core/baseline_irfs.md`, `results_route2_base/` | D-A21 to D-A24 |

`REPORT.md` covers Parts A and B of the second round (through Route 2 with 2020 in); the later results (IP, funds rate, 1-year, Brennan et al., the proposed baselines and Route 2 with them) are in the tables named above and summarized in Part 1 here.
