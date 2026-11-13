# fin_shocks_kf/: Note B by a Kalman-filter (state-space) mixed-frequency model

Started 13 Nov 2026. Experimental. **Completely separate code from `../fin_shocks/`** (no imports from `fin_shocks/baseline/lib/` or `legacy/`; the user's instruction, 13 Nov 2026). The aim:
1. **Replicate Note B** (`../fin_shocks/paper/mp_transmission.tex`, package `../fin_shocks/baseline/`) with a state-space model estimated through the Kalman filter, using the same form and restrictions as the MIDAS-style model where possible.
2. **Then relax, one at a time, the restrictions that the MIDAS form needs and the state-space form does not.**

| File | What it is |
|---|---|
| `KF_PLAN.md` | The Note B model in equations, its restrictions, its state-space form, the replication test, and the candidate relaxations |
| `KF_QA.md` | Decisions, taken one at a time (KF-Q / KF-A numbering) |

Code and data folders will be added once KF-Q1 to KF-Q3 are answered.

Not to be confused with the earlier state-space attempt `../fin_shocks/legacy/route_b.py` (31 Oct 2026: a daily VAR(1) in four variables, a different form from Note B, judged misspecified in `../fin_shocks/MF_DEVELOPMENT.md`). Nothing here reuses it.
