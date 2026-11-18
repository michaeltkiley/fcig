"""Part A tables (markdown) from results_core/: Note B's model from 1973 and 1996 (matched comparison with paired differences, path B decomposition, lags),
and the monthly VAR benchmarks.   python3 C_core_tables.py -> results_core/tables_core.md"""
import numpy as np, pandas as pd
from pathlib import Path
RES = Path(__file__).resolve().parent / "results_core"
STEP = {"nom": "Nominal", "real": "Real", "rstar": "r*-gap"}
def cid(form, fci, start): return f"{form}_{fci}_upi_{start}_all_in"
def load(form, fci, start, L=12): return np.load(RES / "draws" / f"{cid(form, fci, start)}_L{L}.npz", allow_pickle=True)
def star(d): lo, hi = np.percentile(d, [5, 95]); lo2, hi2 = np.percentile(d, [2.5, 97.5]); return "**" if lo2 * hi2 > 0 else ("*" if lo * hi > 0 else "")
def cell(p, d): return f"{p:+.2f}{star(d)} [{np.percentile(d, 5):+.2f}, {np.percentile(d, 95):+.2f}]"
J = {"u": 0, "P": 1}
out = []

for L in (12, 6, 3):
    rows = []
    for start in ("1973-01", "1996-01"):
        for f in ("nom", "real", "rstar"):
            A, C = load(f, f, start, L), load(f, 0, start, L)
            for h in ((12, 24, 36) if L == 12 else (24,)):
                r = {"sample": start[:4], "yield": STEP[f], "h": h}
                for v in ("u", "P"):
                    j = J[v]
                    r[f"{v}: yield alone"] = cell(C["s0"][h, j], C["sd"][:, h, j]); r[f"{v}: yield + FCI"] = cell(A["s0"][h, j], A["sd"][:, h, j])
                    r[f"{v}: difference"] = cell(A["s0"][h, j] - C["s0"][h, j], A["sd"][:, h, j] - C["sd"][:, h, j])
                rows.append(r)
    out.append(f"### A1 ({L} lags). Note B's model: responses without and with the FCI, monthly equations from 1973 and from 1996 (u: unemployment gap, pp; P: price level, %; "
               "per +1 pp window surprise; paired differences; 90% intervals; ** and * 5 and 10 percent)\n\n" + pd.DataFrame(rows).to_markdown(index=False))

rows = []
for start in ("1973-01", "1996-01"):
    for f in ("nom", "real", "rstar"):
        A, C = load(f, f, start), load(f, 0, start); r = {"sample": start[:4], "yield": STEP[f], "ordinary FCI loading": f"{float(A['ord0']):.2f}"}
        for v in ("u", "P"):
            j = J[v]; h = 24
            r[f"{v}24: A-B (extra initial FCI move)"] = cell(A["s0"][h, j] - A["s0B"][h, j], A["sd"][:, h, j] - A["sdB"][:, h, j])
            r[f"{v}24: B-C (FCI as ordinarily)"] = cell(A["s0B"][h, j] - C["s0"][h, j], A["sdB"][:, h, j] - C["sd"][:, h, j])
        rows.append(r)
out.append("### A1b. Decomposition of the FCI effect at 24 months (path A = with FCI, B = FCI started at its ordinary co-movement with the yield, C = yield alone; 12 lags)\n\n" + pd.DataFrame(rows).to_markdown(index=False))

M = pd.read_csv(RES / "monthly_benchmarks.csv"); M = M[M.L == 12]
M["cell"] = M.apply(lambda r: (f"{r.r:+.2f} [unbounded]" if r.unbounded else f"{r.r:+.2f} [{r.lo:+.2f}, {r.hi:+.2f}]") + ("*" if (not r.unbounded and r.lo * r.hi > 0) else ""), axis=1)
M["sample"] = M.kind.map({"avg": "monthly avg", "eom": "end of month"}) + " " + M.start.str[:4]
rows = []
for (step, fci, ident, sample), g in M.groupby(["step", "fci", "ident", "sample"], sort=False):
    rows.append({"yield": STEP[step], "FCI": "yes" if str(fci) != "0" else "no", "method": {"P1": "proxy VAR", "WE": "window-impact VAR", "CH": "Cholesky"}[ident], "data": sample,
                 "F": f"{g.F.iloc[0]:.1f}", **{f"{v}{h}": g[(g["var"] == v) & (g.h == h)].cell.iloc[0] for v, h in (("u", 12), ("u", 24), ("P", 24), ("P", 36))}})
R = pd.DataFrame(rows).sort_values(["FCI", "yield", "method", "data"])
out.append("### A2. Monthly VAR benchmarks (Note B Tables 2 and 4) from 1973 in monthly averages, from 1990 at the end of the month, and the paper's end-of-month 1996 versions "
           "(12 lags; per +1 pp window surprise for proxy and window-impact VARs, per +1 pp yield innovation for Cholesky; 90% intervals: Anderson-Rubin for the proxy VAR, "
           "block bootstrap otherwise; * = excludes zero)\n\n" + R.to_markdown(index=False))
(RES / "tables_core.md").write_text("\n\n".join(out) + "\n"); print("\n\n".join(out)[:6000])
