"""Directories of the Note B replication package."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DATA, OUT, RESULTS, REPORT = ROOT / "data", ROOT / "output", ROOT / "results", ROOT / "report"
for _d in (OUT, RESULTS, REPORT): _d.mkdir(exist_ok=True)
