"""Monthly VAR benchmarks (lib/monthly.py: P1 = standard proxy VAR with the NS surprise summed by month as instrument, 90% Anderson-Rubin sets; WE = window impact, 500 block-bootstrap draws)
with the federal funds rate added to the VAR next to the 2-year yield, in the same version (author, 18 Nov 2026): y = (u, pi, 2-year, [FCI,] funds rate). Nominal and real, without and with the FCI,
monthly equations from 1996 and from 1973 (8 cases), 12 lags, March-December 2020 dropped. Funds rate: monthly mean of DFF less the 2-year's adjustment (the package's variant "ff");
in WE its impact is the model's month-average response to the window surprise (B_FF = 0.72 on the day). Comparison: the stored benchmarks without the funds rate (results/monthly_*).
Writes results/monthlyff_<step>_<fci>_<start>.csv and monthly_ff.md."""
import os, sys
os.environ.setdefault("OMP_NUM_THREADS", "1")
from pathlib import Path
HERE = Path(__file__).resolve().parent; BASE = HERE.parent / "baseline"; sys.path.insert(0, str(BASE)); os.chdir(BASE)
import numpy as np, pandas as pd
from lib import model as M, monthly as MV
RES = HERE / "results"; RES.mkdir(exist_ok=True)
CASES = [(f, fci, s) for s in ("1996-01", "1973-01") for f in ("nom", "real") for fci in (0, f)]
def work(c):
    f, fci, s = c; M.use_variant("ff"); out = RES / f"monthlyff_{f}_{fci}_{s}.csv"
    if not out.exists(): pd.DataFrame(MV.run_case(f, fci, s, B=500, lags=(12,), t2020="out")).to_csv(out, index=False, float_format="%.4f")
    return c
if __name__ == "__main__":
    from multiprocessing import Pool
    with Pool(4) as p: list(p.imap_unordered(work, CASES))
    def cell(d, ident, v, h):
        r = d[(d.ident == ident) & (d["var"] == v) & (d.h == h)].iloc[0]; sig = "*" if (r.lo > 0 or r.hi < 0) and not r.unbounded else ""
        iv = "unbounded" if r.unbounded else f"[{r.lo:+.2f}, {r.hi:+.2f}]"; return f"{r.r:+.2f}{sig} {iv}"
    md = ["# Monthly VAR benchmarks with the funds rate added (12 lags)", "",
          "P1 = proxy VAR (instrument: NS surprise summed by month; 90% Anderson-Rubin set); WE = window-impact VAR (90% block-bootstrap interval). Per +1 pp on the 2-year in the window. "
          "`*` = 90 percent set excludes zero. u = unemployment gap (pp), P = price level (percent). F = robust first-stage F of the 2-year residual on the instrument.", ""]
    for ident in ("P1", "WE"):
        md += [f"## {ident}", "", "| start | version | FCI | VAR | F | u 12m | u 24m | P 24m | P 36m |", "|---|---|---|---|---|---|---|---|---|"]
        for f, fci, s in CASES:
            for lab, path in (("2-year only (stored)", BASE / "results" / f"monthly_{f}_{fci}_{s}.csv"), ("2-year + funds rate", RES / f"monthlyff_{f}_{fci}_{s}.csv")):
                d = pd.read_csv(path); d = d[d.lags == 12]; F = d.F.iloc[0]
                md.append(f"| {s[:4]} | {f} | {'yes' if fci else 'no'} | {lab} | {F:.1f} | {cell(d, ident, 'u', 12)} | {cell(d, ident, 'u', 24)} | {cell(d, ident, 'P', 24)} | {cell(d, ident, 'P', 36)} |")
        md.append("")
    (HERE / "monthly_ff.md").write_text("\n".join(md)); print("\n".join(md))
