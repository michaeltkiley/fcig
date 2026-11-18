"""Note B's model with the monthly equations from January 1985 (author, 18 Nov 2026): nominal and real versions, no trend and the package's cubic spline (knots: 1985-01, the NBER peaks
1990-07, 2001-03, 2007-12, 2020-02, and 2026-09; the first knot is the first estimation month), without and with the FCI (8 cases). 12 lags, March-December 2020 dropped,
500 bootstrap draws (the package's scheme). Writes results/s85_<case>.csv, _paths.csv and start85.md. ** / *: 95 / 90 percent interval excludes zero."""
import os, sys, time
os.environ.setdefault("OMP_NUM_THREADS", "1"); os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
from pathlib import Path
HERE = Path(__file__).resolve().parent; BASE = HERE.parent / "baseline"; sys.path.insert(0, str(BASE)); os.chdir(BASE)
import numpy as np, pandas as pd
from lib import model as M
RES = HERE / "results"; RES.mkdir(exist_ok=True); START = "1985-01"
CASES = [(f, fci, tr) for f in ("nom", "real") for tr in ("none", "spline") for fci in (0, f)]
def cid(c): return f"s85_{c[0]}_{c[1]}_{c[2]}"
def work(c):
    f, fci, tr = c; t0 = time.time(); sp = dict(form=f, fci=fci, macro="u,pi", start=START, end="", t2020="out", trend=tr, shock="ns")
    est = next(M.estimate(f, fci, "u,pi", START, None, "out", tr, 500, lags=(12,)))
    pd.DataFrame(M.summary_rows(sp, est)).to_csv(RES / f"{cid(c)}.csv", index=False, float_format="%.4f")
    M.path_rows(sp, est).to_csv(RES / f"{cid(c)}_paths.csv", index=False, float_format="%.4f"); return f"{cid(c)} nobs {est['nobs']} {time.time() - t0:.0f}s"
if __name__ == "__main__":
    jobs = [c for c in CASES if not (RES / f"{cid(c)}.csv").exists()]
    from multiprocessing import Pool
    if jobs:
        with Pool(4) as p:
            for m in p.imap_unordered(work, jobs): print(m, flush=True)
    def star(r, h): return "**" if r[f"lo95_{h}"] > 0 or r[f"hi95_{h}"] < 0 else "*" if r[f"lo{h}"] > 0 or r[f"hi{h}"] < 0 else ""
    md = ["# Note B's model from 1985: nominal and real, no trend and cubic spline, without and with the FCI (12 lags, 500 draws)", "",
          "Per +1 pp on the 2-year in the window: u = unemployment gap (pp), P = price level (percent). `**` / `*`: 95 / 90 percent interval excludes zero; 90 percent intervals in brackets. "
          "Monthly equations from 1985-01; spline knots 1985-01, 1990-07, 2001-03, 2007-12, 2020-02, 2026-09. March-December 2020 dropped.", ""]
    for f, lab in (("nom", "Nominal"), ("real", "Real")):
        md += [f"## {lab}", "", "| FCI | trend | u 12m | u 24m | u 36m | P 12m | P 24m | P 36m |", "|---|---|---|---|---|---|---|---|"]
        for fci in (0, f):
            for tr in ("none", "spline"):
                R = pd.read_csv(RES / f"{cid((f, fci, tr))}.csv"); R = R[R.lags == 12].set_index("var")
                cells = [f"{R.loc[v, f'r{h}']:+.2f}{star(R.loc[v], h)} [{R.loc[v, f'lo{h}']:+.2f}, {R.loc[v, f'hi{h}']:+.2f}]" for v in ("u", "P") for h in (12, 24, 36)]
                md.append(f"| {'with FCI' if fci else 'no FCI'} | {'cubic spline' if tr == 'spline' else 'no trend'} | " + " | ".join(cells) + " |")
        md.append("")
    (HERE / "start85.md").write_text("\n".join(md)); print("\n".join(md))
