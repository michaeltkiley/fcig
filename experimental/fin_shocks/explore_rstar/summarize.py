"""Summary of the r* exploration: responses of the unemployment gap (pp) and the price level (percent) per +1 pp on the 2-year yield in the window,
at 12 and 24 months, under four r* measures (LW baseline and Kiley from baseline/results; MA8 and forward from results/), both baselines, without and with the FCI.
** / * : 95 / 90 percent interval excludes zero (5 / 10 percent level). Writes summary.csv, summary.md, fig_rstar.pdf, fig_paths.pdf."""
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = Path(__file__).resolve().parent; BR = HERE.parent / "baseline" / "results"
FORMS = [("rstar", "LW (baseline)", BR), ("kiley", "Kiley", BR), ("ma8", "MA8 real 2-year", HERE / "results"), ("fwd", "Forward 9-10y less e10", HERE / "results"), ("nma8", "MA8 nominal 2-year", HERE / "results")]
STARTS = [("1996-01", "1996"), ("1973-01", "1973")]
def star(lo, hi, lo95, hi95): return "**" if lo95 > 0 or hi95 < 0 else "*" if lo > 0 or hi < 0 else ""
rows = []
for f, lab, d in FORMS:
    for s, sl in STARTS:
        for fci in (0, f):
            p = d / f"{f}_{fci}_upi_{s}_all_out.csv"
            if not p.exists(): continue
            R = pd.read_csv(p)
            for _, r in R.iterrows():
                for h in (12, 24, 36):
                    rows.append(dict(rstar=lab, start=sl, fci="with FCI" if fci else "no FCI", lags=int(r.lags), var=r["var"], h=h, est=r[f"r{h}"],
                                     lo90=r[f"lo{h}"], hi90=r[f"hi{h}"], lo68=r[f"lo68_{h}"], hi68=r[f"hi68_{h}"], sig=star(r[f"lo{h}"], r[f"hi{h}"], r[f"lo95_{h}"], r[f"hi95_{h}"])))
S = pd.DataFrame(rows); S.to_csv(HERE / "summary.csv", index=False, float_format="%.4f")

def table(lags):
    T = S[(S.lags == lags) & S.h.isin([12, 24])].copy(); T["cell"] = T.est.map("{:+.2f}".format) + T.sig
    T["col"] = T["var"].map({"u": "u", "P": "P"}) + T.h.astype(str)
    P = T.pivot_table(index=["start", "fci", "rstar"], columns="col", values="cell", aggfunc="first")[["u12", "u24", "P12", "P24"]]
    order = [l for _, l, _ in FORMS]
    P = P.reindex(pd.MultiIndex.from_product([["1996", "1973"], ["no FCI", "with FCI"], order]))
    out = ["| Start | FCI | r* measure | u 12m | u 24m | P 12m | P 24m |", "|---|---|---|---|---|---|---|"]
    for (s, fc, r), v in P.iterrows(): out.append(f"| {s} | {fc} | {r} | " + " | ".join(str(x) for x in v.values) + " |")
    return "\n".join(out)
md = ["# r* exploration: Note B's two baselines under four r* measures", "",
      "Responses per +1 pp on the 2-year yield in the window: unemployment gap (pp) and price level (percent). `**`/`*`: 95/90 percent interval excludes zero. 500 draws; 2020 (March-December) dropped; no trend. LW and Kiley rows are the package's stored results (`baseline/results`).", ""]
for L in (12, 6, 3): md += [f"## {L} lags" + (" (main)" if L == 12 else ""), "", table(L), ""]
(HERE / "summary.md").write_text("\n".join(md))
print("\n".join(md))

RS = pd.read_csv(HERE / "rstar_measures.csv", index_col=0); RS.index = pd.PeriodIndex(RS.index, freq="M").to_timestamp()
fig, ax = plt.subplots(figsize=(8, 4))
for c, col in zip([c for c in RS.columns if not c.startswith("e2")], ["k", "0.55", "tab:blue", "tab:red", "tab:green"]): ax.plot(RS.index, RS[c], color=col, lw=1.3, label=c)
ax.axhline(0, color="0.8", lw=0.8); ax.set_ylabel("percent"); ax.legend(frameon=False, fontsize=8); ax.set_xlim(pd.Timestamp("1970-01-01"), RS.index[-1])
ax.set_title("r* measures (monthly)", fontsize=10); fig.tight_layout(); fig.savefig(HERE / "fig_rstar.pdf"); fig.savefig(HERE / "fig_rstar.png", dpi=150)

# response paths, 12 lags, with FCI, both starts
fig, axs = plt.subplots(2, 2, figsize=(9, 6), sharex=True)
for j, (s, sl) in enumerate(STARTS):
    for f, lab, d in FORMS:
        p = d / f"{f}_{f}_upi_{s}_all_out_paths.csv"
        if not p.exists(): continue
        Pth = pd.read_csv(p); Pth = Pth[(Pth.lags == 12) & (Pth.kind == "macro")]
        for i, v in enumerate(["u", "P"]):
            q = Pth[Pth["var"] == v]
            if q.empty: continue
            ax = axs[i, j]; ax.plot(q.h, q.r, lw=1.4, label=lab)
            if f == "rstar": ax.fill_between(q.h, q.lo68, q.hi68, color="0.85", lw=0)
            ax.axhline(0, color="0.6", lw=0.7); ax.set_title(f"{'Unemployment gap (pp)' if v == 'u' else 'Price level (%)'}, from {sl}", fontsize=9)
axs[0, 0].legend(frameon=False, fontsize=7); [a.set_xlabel("months") for a in axs[1]]
fig.tight_layout(); fig.savefig(HERE / "fig_paths.pdf"); fig.savefig(HERE / "fig_paths.png", dpi=150)
