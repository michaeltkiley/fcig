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
| `fci_compare/` | Common-unit comparison of GS, FCI-G, NFCI/ANFCI, macro-model and market indexes; `METRIC.md`; ECB-method exploration | current |
| `real_case/` | Real-rate case, decisions in `REAL_QA.md` | closed, written up |
| `rstar_case/` | r*-gap case (baseline of the note), decisions in `RSTAR_QA.md` | current |
| `lp_weights/` | Local-projection routes to weights; wrong-sign activity response to NS surprises (`RESULTS.md`) | exploration, informs `mp_var_fci/` |
| `ms_fci/` | FRB/US sensitivities and the **macro-model levels index** (earlier "MS-style five-variable" index) | reference for the macro-model comparator |
| `weighting_note/` | LaTeX weighting note and review | current |
| `note_draft/` | Draft of note section 3 (market index) | full draft is in `../fci_note/paper/` |
| `mp_var_fci/` | Monetary policy shocks in a VAR with the market index (Cholesky, Nakamura-Steinsson, Bauer-Swanson, Greenbook purge, Bayesian proxy-SVAR). Start with `SUMMARY_REPORT.md`; decisions in `MP_QA.md` | **closed 31 Oct 2026** (negative result: credit, not the index, fixes post-1994 identification) |
| `fin_shocks/` | Transmission note (Note B): window-identified surprises traced through the FCI and r* | LaTeX note `fin_shocks/paper/mp_transmission.tex` (1 Nov 2026); uses the FCI of `../fci_note/` (Note A). Clean, self-contained baseline and robustness package: `fin_shocks/baseline/` (10 Nov 2026; `README.md` there); experimental code and outputs moved to `fin_shocks/legacy/` |
| `fin_shocks_kf/` | Note B by a Kalman-filter (state-space) mixed-frequency model; completely separate code from `fin_shocks/` | started 13 Nov 2026: plan `KF_PLAN.md`, decisions `KF_QA.md` (KF-Q1 to Q3 open); no code yet |

- `WRITING_GUIDE.md`: the author's writing and working preferences for all papers (read before editing text); evidence from earlier papers in `fin_shocks/paper/STYLE_GUIDE_DRAFT.md`.
