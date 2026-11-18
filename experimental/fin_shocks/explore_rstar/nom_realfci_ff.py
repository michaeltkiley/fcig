"""Note B's model (mixed-frequency) with the nominal 2-year and the nominal funds rate in the daily block and the REAL FCI (author, 18 Nov 2026): rates nominal, FCI real.
From 1996 and from 1973, 12 lags, March-December 2020 dropped, no trend, 500 draws (the package's scheme; case key ext = "ff"). Compared with the stored R8 cases
(nominal 2-year + funds + nominal FCI; real 2-year + funds + real FCI). Writes results/nomrealff_<start>.csv and nom_realfci_ff.md."""
import os, sys, time
os.environ.setdefault("OMP_NUM_THREADS", "1"); os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
from pathlib import Path
HERE = Path(__file__).resolve().parent; BASE = HERE.parent / "baseline"; sys.path.insert(0, str(BASE)); os.chdir(BASE)
import pandas as pd
from lib import model as M
RES = HERE / "results"; RES.mkdir(exist_ok=True)
def work(s):
    M.use_variant("ff"); t0 = time.time(); sp = dict(form="nom", fci="real", macro="u,pi", start=s, end="", t2020="out", trend="none", shock="ns", ext="ff")
    est = next(M.estimate("nom", "real", "u,pi", s, None, "out", "none", 500, lags=(12,)))
    pd.DataFrame(M.summary_rows(sp, est)).to_csv(RES / f"nomrealff_{s}.csv", index=False, float_format="%.4f"); return f"{s} {time.time() - t0:.0f}s"
if __name__ == "__main__":
    from multiprocessing import Pool
    with Pool(2) as p:
        for m in p.imap_unordered(work, [s for s in ("1996-01", "1973-01") if not (RES / f"nomrealff_{s}.csv").exists()]): print(m, flush=True)
    def cell(d, v, h):
        r = d.loc[v]; s = "**" if r[f"lo95_{h}"] * r[f"hi95_{h}"] > 0 else "*" if r[f"lo{h}"] * r[f"hi{h}"] > 0 else ""; return f"{r[f'r{h}']:+.2f}{s} [{r[f'lo{h}']:+.2f}, {r[f'hi{h}']:+.2f}]"
    md = ["# Nominal 2-year and funds rate with the real FCI (Note B's model, 12 lags, 500 draws)", "",
          "Per +1 pp on the 2-year in the window: u = unemployment gap (pp), P = price level (percent). `**` / `*`: 95 / 90 percent interval excludes zero; 90 percent intervals in brackets. 2020 (March-December) dropped.", ""]
    for s in ("1996-01", "1973-01"):
        md += [f"## From {s[:4]}", "", "| rates | FCI | u 12m | u 24m | u 36m | P 12m | P 24m | P 36m |", "|---|---|---|---|---|---|---|---|"]
        for lab, fci, path in (("nominal 2-year + funds", "nominal", BASE / "results" / f"nom_nom_upi_{s}_all_out_ff.csv"), ("nominal 2-year + funds", "real", RES / f"nomrealff_{s}.csv"),
                               ("real 2-year + funds", "real", BASE / "results" / f"real_real_upi_{s}_all_out_ff.csv")):
            d = pd.read_csv(path); d = d[d.lags == 12].set_index("var")
            md.append(f"| {lab} | {fci} | " + " | ".join(cell(d, v, h) for v in ("u", "P") for h in (12, 24, 36)) + " |")
        md.append("")
    (HERE / "nom_realfci_ff.md").write_text("\n".join(md)); print("\n".join(md))
