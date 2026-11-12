"""Download ALFRED vintages (one call per series x vintage date, 1st of month), window = vintage minus 5 years. Cached in raw/ (gitignored)."""
import subprocess, pathlib, sys
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
RAW = pathlib.Path(__file__).resolve().parent / "raw"; RAW.mkdir(exist_ok=True)
A = "https://alfred.stlouisfed.org/graph/alfredgraph.csv"
SPEC = {"UNRATE": "1977-01", "PAYEMS": "1977-01", "PCEPILFE": "2001-06", "NROU": "2011-02", "GDPC1": "1992-06"}
def job(a):
    sid, v = a; f = RAW / f"{sid}_{v:%Y%m}.csv"
    if f.exists() and f.stat().st_size > 30: return sid, v, "cached"
    cosd = (v - pd.DateOffset(years=5)).strftime("%Y-%m-%d") if sid != "NROU" else "1985-01-01"
    r = subprocess.run(["curl", "-sS", "--http1.1", "-m", "60", "-o", str(f), "-w", "%{http_code}", f"{A}?id={sid}&vintage_date={v:%Y-%m-%d}&cosd={cosd}"], capture_output=True, text=True)
    if r.stdout != "200": f.unlink(missing_ok=True); return sid, v, r.stdout or r.stderr[:40]
    return sid, v, "ok"
jobs = [(s, v) for s, a in SPEC.items() for v in pd.date_range(a + "-01", "2026-11-01", freq="MS")]
bad = []
with ThreadPoolExecutor(6) as ex:
    for sid, v, st in ex.map(job, jobs):
        if st not in ("ok", "cached"): bad.append((sid, f"{v:%Y-%m}", st))
print(len(jobs), "jobs;", len(bad), "failed"); print(bad[:20])
