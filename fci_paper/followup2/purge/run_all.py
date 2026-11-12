"""Run the purge analysis in order (about 8 minutes; FCI_REPS sets bootstrap draws, default 500)."""
import runpy
for s in ("01_build", "02_corr_lp", "03_var"):
    print(f"\n===== {s} ====="); runpy.run_path(f"{s}.py", run_name="__main__")
