"""Run every step in order (about 2 minutes). Outputs go to output/; the paper (../paper/fci_note.tex) reads output/figures, output/tables and output/numbers_*.tex."""
import runpy
for s in ("01_data", "02_weights", "03_indexes", "04_var", "05_compare", "06_unemployment", "07_appendix"):
    print(f"\n========== {s} =========="); runpy.run_path(f"{s}.py", run_name="__main__")
