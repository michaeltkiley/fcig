"""Run every step in order (about 4 minutes with 500 bootstrap draws). Results go to results/, exhibits to report/; the paper (../paper/fci_paper.tex) reads report/.
FCI_REPS sets the number of bootstrap draws (default 500); FCI_RESULTS and FCI_REPORT redirect the outputs (the sync check uses them)."""
import runpy, sys
STEPS = ("01_data", "02_weights", "03_indexes", "04_var", "05_compare", "06_activity", "08_stance", "09_levelflow", "10_nfci", "11_purge", "12_checks1996", "13_neutrality", "14_ladder_outcomes", "15_weights_outcomes", "16_weights_drift", "17_realtime", "07_report")
only = sys.argv[1:] or STEPS
for s in only:
    print(f"\n========== {s} =========="); runpy.run_path(f"{s}.py", run_name="__main__")
