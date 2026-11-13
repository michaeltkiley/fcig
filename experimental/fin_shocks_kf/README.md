# fin_shocks_kf/: Note B by a Kalman-filter (state-space) mixed-frequency model

Started 13 Nov 2026. Experimental. **Completely separate code from `../fin_shocks/`** (no imports from `fin_shocks/baseline/lib/` or `legacy/`; the user's instruction, 13 Nov 2026). The aim:
1. **Replicate Note B** (`../fin_shocks/paper/mp_transmission.tex`, package `../fin_shocks/baseline/`) with a state-space model estimated through the Kalman filter, using the same form and restrictions as the MIDAS-style model where possible.
2. **Then relax, one at a time, the restrictions that the MIDAS form needs and the state-space form does not.**

| File | What it is |
|---|---|
| `KF_PLAN.md` | The Note B model in equations, its restrictions, its state-space form, the replication test, and the candidate relaxations |
| `KF_QA.md` | Decisions, taken one at a time (KF-Q / KF-A numbering) |
| `data/` | Raw inputs copied from Note B and frozen Note A inputs (`frozen/`); `SOURCES.md` with checksums |
| `kf/inputs.py` | Data, calendar, announcements, window impact, event-position bins |
| `kf/ssm.py` | General Kalman filter (missing data, time-varying matrices, exogenous inputs) and RTS smoother |
| `kf/noteb.py` | Note B as a state space on a daily clock: EM estimation, responses from the full daily state, Note B's block bootstrap |
| `01_data.py` | Step 1: builds the inputs, checks them against Note B's files; writes `output/` |
| `02_stage1.py` | Step 2: stage 1 (panel B, 3/6/12 lags, 500 draws) and the comparison with Note B; writes `results/stage1_*` |

**Status 13 Nov 2026:** stage 1 reproduces Note B exactly (`KF_PLAN.md` section 6). Stage 2 (relaxations) waits for KF-Q4.
Run: `python 01_data.py && python 02_stage1.py` (about 10 minutes on 4 cores; `python 02_stage1.py 20` for a quick run).

Not to be confused with the earlier state-space attempt `../fin_shocks/legacy/route_b.py` (31 Oct 2026: a daily VAR(1) in four variables, a different form from Note B, judged misspecified in `../fin_shocks/MF_DEVELOPMENT.md`). Nothing here reuses it.
