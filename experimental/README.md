# experimental/: folder index

Entry point: `PROJECT_MEMORY.md` (section 9 = where we are). Glossary of index names: root `CLAUDE.md`. Two notes use the market index: Note A, the FCI note and replication package, `../fci_note/`; Note B, the transmission note, `fin_shocks/paper/`.

Note A as a paper (clean package, separate from this folder): `../fci_paper/` (`README.md`, decisions in `FP_QA.md`).

| Item | What it is | Status |
|---|---|---|
| `PROJECT_MEMORY.md` | Decisions, results, where things are, next steps | current |
| `INDEX_QA.md` | Q&A that settled the index definitions (answers 1-56) | current |
| `DYNAMICS_PLAN.md` | Plan and results for the dynamic (flow) indexes | results in PROJECT_MEMORY 3c; the adopted VAR is in `market_macro/` (3f) |
| `path_fci/` | Market index construction: weights from policy-news responses; `NOTE_PLAN.md`, `ASSESSMENT.md`, `lit/` | current |
| `market_macro/` | Two-variable VAR (unemployment gap, market index), Phi, forward impetus, significance | current |
| `note_a_qvar/` | Experiment (16 Nov 2026): quarterly VAR of the CBO output gap and each FCI (F, Y, B, G at three steps; FCI-G, NFCI, ANFCI; 2-year and funds-rate benchmarks), 4 lags, both Cholesky orderings | experiment, not in the paper |
| `fci_compare/` | Common-unit comparison of GS, FCI-G, NFCI/ANFCI, macro-model and market indexes; `METRIC.md`; ECB-method exploration | current |
| `real_case/` | Real-rate case, decisions in `REAL_QA.md` | closed, written up |
| `rstar_case/` | r*-gap case (baseline of the note), decisions in `RSTAR_QA.md` | current |
| `lp_weights/` | Local-projection routes to weights; wrong-sign activity response to NS surprises (`RESULTS.md`) | exploration, informs `mp_var_fci/` |
| `ms_fci/` | FRB/US sensitivities and the **macro-model levels index** (earlier "MS-style five-variable" index) | reference for the macro-model comparator |
| `weighting_note/` | LaTeX weighting note and review | current |
| `note_draft/` | Draft of note section 3 (market index) | full draft is in `../fci_note/paper/` |
| `mp_var_fci/` | Monetary policy shocks in a VAR with the market index (Cholesky, Nakamura-Steinsson, Bauer-Swanson, Greenbook purge, Bayesian proxy-SVAR). Start with `SUMMARY_REPORT.md`; decisions in `MP_QA.md` | **closed 31 Oct 2026** (negative result: credit, not the index, fixes post-1994 identification) |
| `fin_shocks/` | Transmission note (Note B): window-identified surprises traced through the FCI and r* | Author's text `fin_shocks/paper/mp_transmission.tex`; current text `fin_shocks/paper/mp_transmission_real.tex` (+ `.pdf`, 19 Nov 2026, after the research review); earlier copy `fin_shocks/paper/mp_transmission_session_integration.tex` with `paper/CHANGES_FOR_MERGE.md` and `paper/check_paper.py`. Clean, self-contained package `fin_shocks/baseline/` (steps 01-13, reports 07/07b/07c/07d; `README.md` there); decisions `fin_shocks/FS_QA.md`; experimental code in `fin_shocks/legacy/` |
| `fin_shocks/explore_decomp/` | Exploratory (17 Nov 2026; its integration plan is executed and on `main`, 18 Nov): Note B from 1973 (model and benchmark monthly VARs, monthly averages vs end of month, regime split, Brennan et al. sample, 2020), extensions (IP, funds rate, 1-year yield), historical and variance decompositions (Route 1, Route 2 monthly and daily) | **`INTEGRATION_PLAN.md`** first; `REPORT.md`; decisions `DECOMP_QA.md`; reads `fin_shocks/baseline/lib/` only |
| `fin_shocks/baseline_real/` | Note B rebuilt with the real version as the baseline (18 Nov 2026, FS-A85/FS-A86): 2-year yield, funds rate and FCI; nominal and real; 1996 and 1973; six robustness tests; final-section panels (LW r*-gap, spline). `fin_shocks/baseline/` is frozen as the r*-gap record | `README.md` there; sign-off documents `report/results_real.pdf`, `report/WHAT_MOVED.md`; claims `claims_real.py`; plan `fin_shocks/PLAN_REAL_BASELINE.md` |
| `fin_shocks/explore_review/` | Exploratory (19 Nov 2026): review items 23-24 (Laubach-Williams two-sided, Holston-Laubach-Williams and Lubik-Matthes r*; FRB/US and GS weights); the HLW, LM and GS cases are in the package | `run_items_23_24.py`; data downloaded 19 Nov 2026 (New York Fed, Richmond Fed); FS_QA FS-A113 |
| `fin_shocks/explore_rstar/` | Exploratory (18 Nov 2026): Note B under alternative r* measures, trends (quadratic, spline, peak-to-peak, level jumps, daily-equation spline), one-sided filters tracking LW, a random-walk r* inside the VAR, NFCI, 1985 start, real version as baseline, 2-year + funds rate (model and monthly VARs), nominal rates with real FCI; survey measures of long-run rates | one `.md` per script (`summary.md`, `real_as_baseline.md`, `ff_baseline.md`, ...); FS_QA FS-A83, FS-A84; reads `fin_shocks/baseline/lib/` only |

- `WRITING_GUIDE.md`: the author's writing and working preferences for all papers (read before editing text); evidence from earlier papers in `fin_shocks/paper/STYLE_GUIDE_DRAFT.md`.
