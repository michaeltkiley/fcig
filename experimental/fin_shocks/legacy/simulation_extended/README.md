# Extended simulation (archived; not in the paper)

The estimated r*-gap model as the true process, with 1,000 simulated samples of 369 months, analysed with (i) the monthly proxy VAR and the window-impact monthly VAR and (ii) the full daily-block model, with the
2-year yield and FCI in r*-gap, nominal and real form (nominal and real = the r*-gap series plus the actual expected-inflation and r* terms), and with independent or block-bootstrapped innovations.
Results are in `results/` (summaries `*_sim_summary*.csv`, one row per sample `proxy_sim_*.csv`, `daily_sim*.csv`); decisions and numbers in `../../FS_QA.md` (FS-A44 and addenda).
Main findings: with the FCI the nominal and real daily-block estimates lie inside the simulated 90% bands; without the FCI the nominal and real unemployment responses lie outside them (not explained by block resampling); the
monthly proxy VAR's simulated bands are wide enough to contain both the true response and the data puzzles. The paper reports only the monthly proxy VAR under the r*-gap truth (`../../baseline/06_proxy_simulation.py`).
Code: `simulate_extended.py`, `run_simulation_extended.py` (import `lib` from `../../baseline`; run from this folder with `PYTHONPATH=../../baseline`).
