"""Bootstrap (500 draws, the package's scheme) for the real case with the FCI, 12 lags, 1996 and 1973: quadratic trend and level jumps at NBER peaks (the two trends the package lacks);
no trend and the cubic spline are read from the package's stored results (baseline/results: real_real_..._all_out[_spline]). Writes results/real_<trend>_<start>.csv and real_trends_sig.md.
** / *: 95 / 90 percent interval excludes zero."""
import os, sys, time
os.environ.setdefault("OMP_NUM_THREADS", "1"); os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
from pathlib import Path
HERE = Path(__file__).resolve().parent; BASE = HERE.parent / "baseline"
exec(open(HERE / "real_trends.py").read().split("HS = (6, 12")[0])            # the model with the quad and lvl trend options
RES = HERE / "results"; RES.mkdir(exist_ok=True)
def work(job):
    tr, start = job; t0 = time.time(); sp = dict(form="real", fci="real", macro="u,pi", start=start, end="", t2020="out", trend=tr, shock="ns")
    est = next(M.estimate("real", "real", "u,pi", start, None, "out", tr, 500, lags=(12,)))
    pd.DataFrame(M.summary_rows(sp, est)).to_csv(RES / f"real_{tr}_{start}.csv", index=False, float_format="%.4f")
    M.path_rows(sp, est).to_csv(RES / f"real_{tr}_{start}_paths.csv", index=False, float_format="%.4f"); return f"{tr} {start} {time.time() - t0:.0f}s"
if __name__ == "__main__":
    jobs = [(t, s) for t in ("quad", "lvl") for s in ("1996-01", "1973-01")] + [("spl74", "1973-01")]
    jobs = [j for j in jobs if not (RES / f"real_{j[0]}_{j[1]}.csv").exists()]
    from multiprocessing import Pool
    if jobs:
        with Pool(4) as p:
            for m in p.imap_unordered(work, jobs): print(m, flush=True)
    def star(r, h): return "**" if r[f"lo95_{h}"] > 0 or r[f"hi95_{h}"] < 0 else "*" if r[f"lo{h}"] > 0 or r[f"hi{h}"] < 0 else ""
    src = {"no trend": lambda s: BASE / "results" / f"real_real_upi_{s}_all_out.csv", "quadratic": lambda s: RES / f"real_quad_{s}.csv",
           "cubic spline": lambda s: BASE / "results" / f"real_real_upi_{s}_all_out_spline.csv",
           "cubic spline, first knot 1974-01": lambda s: RES / f"real_spl74_{s}.csv" if s == "1973-01" else BASE / "results" / f"real_real_upi_{s}_all_out_spline.csv", "level jumps at peaks": lambda s: RES / f"real_lvl_{s}.csv"}
    md = ["# Real case with the FCI under four trends, with significance (Note B's model, 12 lags, 500 draws)", "",
          "Per +1 pp on the 2-year in the window: u = unemployment gap (pp), P = price level (percent). `**` / `*`: 95 / 90 percent interval excludes zero. 90 percent intervals in brackets. 2020 (March-December) dropped.", ""]
    for s in ("1996-01", "1973-01"):
        md += [f"## From {s[:4]}", "", "| trend | u 12m | u 24m | u 36m | P 12m | P 24m | P 36m |", "|---|---|---|---|---|---|---|"]
        for lab, f in src.items():
            R = pd.read_csv(f(s)); R = R[R.lags == 12].set_index("var"); cells = []
            for v in ("u", "P"):
                for h in (12, 24, 36): r = R.loc[v]; cells.append(f"{r[f'r{h}']:+.2f}{star(r, h)} [{r[f'lo{h}']:+.2f}, {r[f'hi{h}']:+.2f}]")
            md.append(f"| {lab} | " + " | ".join(cells) + " |")
        md.append("")
    (HERE / "real_trends_sig.md").write_text("\n".join(md)); print("\n".join(md))
