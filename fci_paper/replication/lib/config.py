"""Paths, sample and settings shared by every script. Set FCI_RESULTS to write results somewhere else (the sync check does)."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]                 # fci_paper/replication
DATA = ROOT / "data"
RES = Path(os.environ.get("FCI_RESULTS", ROOT / "results"))
REP = Path(os.environ.get("FCI_REPORT", ROOT / "report"))
START, END = "1973-01", "2026-09"                          # sample; each variable is demeaned over it
SEED = 20261111
REPS = int(os.environ.get("FCI_REPS", 500))                # bootstrap draws (VAR, block bootstraps of outcome regressions)
REPS_W = int(os.environ.get("FCI_REPS_W", 5000))           # announcement-bootstrap draws for the policy-news weights (step 02 and every step that reads weights_boot.csv; 12 Nov 2026: 500 -> 5,000)
BLOCK = 12                                                  # block length (months) of the VAR bootstrap
for d in (RES, REP):
    d.mkdir(parents=True, exist_ok=True)
