"""Sync check: re-run steps 1-6 into a scratch directory and compare every stored result (results/*.csv) with the fresh one. Steps are deterministic (fixed seeds), so the
difference should be zero up to floating-point noise. Then confirm that step 7 passes on the stored results (claims hold, macros resolve) and that report/numbers.tex is current.
Usage: python3 10_check_sync.py   (about 4 minutes)"""
import os, subprocess, sys, tempfile
from pathlib import Path
import numpy as np, pandas as pd

HERE = Path(__file__).resolve().parent
stored = HERE / "results"
tmp = Path(tempfile.mkdtemp(prefix="fci_sync_"))
env = dict(os.environ, FCI_RESULTS=str(tmp / "results"), FCI_REPORT=str(tmp / "report"))
for s in ("00_frbus", "01_data", "02_weights", "03_indexes", "04_var", "05_compare", "06_activity", "08_stance", "09_levelflow", "10_nfci", "11_purge", "12_checks1996", "13_neutrality", "14_ladder_outcomes", "15_weights_outcomes", "16_weights_drift", "17_realtime", "18_agreement", "19_composition", "20_daily", "21_signal", "22_channels", "22_policy_shock", "22_weights_persist", "23_expenditure", "24_signal_outcomes", "25_months", "26_four_way", "27_gs_inputs", "28_information", "29_credit", "30_fcistar", "31_examples"):
    r = subprocess.run([sys.executable, str(HERE / f"{s}.py")], cwd=HERE, env=env, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"{s} failed:\n{r.stderr[-2000:]}")
bad, n = [], 0
for f in sorted(stored.glob("*.csv")):
    g = tmp / "results" / f.name
    if not g.exists():
        bad.append(f"{f.name}: not produced"); continue
    a, b = pd.read_csv(f), pd.read_csv(g)
    n += 1
    if a.shape != b.shape:
        bad.append(f"{f.name}: shape {a.shape} vs {b.shape}"); continue
    num = a.select_dtypes("number").columns
    d = np.nanmax(np.abs(a[num].values - b[num].values)) if len(num) else 0.0
    if not d < 1e-8 or not a.drop(columns=num).equals(b.drop(columns=num)):
        bad.append(f"{f.name}: max difference {d:.2e}")
print(f"compared {n} result files")
if bad:
    raise SystemExit("OUT OF SYNC:\n  " + "\n  ".join(bad))
r = subprocess.run([sys.executable, str(HERE / "07_report.py")], cwd=HERE, capture_output=True, text=True)
print(r.stdout.strip().splitlines()[-1])
if r.returncode:
    raise SystemExit("step 7 failed:\n" + r.stderr[-2000:])
print("in sync: results reproduce, claims hold, macros resolve")
