# legacy: experimental code and outputs of Note B (superseded)

Everything here was produced while the design of Note B was explored (Oct to Nov 2026): the window-identified mixed-frequency VAR in many variants, routes A and B,
direct regressions, robustness grids, and the run logs and CSV outputs behind the draft note `../paper/mp_transmission.tex`. It is kept for the record and because
`../paper/make_tables.py` still builds the draft note's tables from `midas_core_*.csv`, `prop_test.csv` and `tradeoff_*.csv` here.

**The replication package for new results is `../baseline/`** (self-contained, one script per step). Nothing in `baseline/` imports from this folder.

Running a script here: `cd experimental/fin_shocks/legacy && python3 midas_core.py 200 rstar-1 trend` (the scripts use paths relative to this folder and to `../../mp_var_fci`).
Results in this folder were not reproduced when the folder was moved, except that `midas_core.py` runs and `../paper/make_tables.py` regenerates the draft note's tables unchanged.
