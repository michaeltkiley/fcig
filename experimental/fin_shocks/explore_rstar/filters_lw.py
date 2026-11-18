"""Which backward-looking (one-sided) trend of a market rate best tracks one-sided Laubach-Williams r*?
Targets: LW (for real rates) and 2-year expected inflation + LW (for nominal rates: the nominal neutral 2-year, the adjustment the baseline subtracts from the 2-year).
Rates (monthly averages): 2-year (Note B's Y2M), 10-year (GS10), federal funds (DFF); real = less the matching expected inflation (2-year: e2; 10-year: e10; funds: e1).
Filters, each one-sided (uses months <= t only): trailing moving average (N months), exponentially weighted average (half-life H months), one-sided HP (lambda).
Fit: RMSE of the level (no rescaling), also mean error and correlation, over 1973-01..2026-09 (the 1973 sample) and 1996-01..2026-09; best by RMSE 1973-2026.
Also the best affine version a + b * filter (in-sample OLS; flatters, reported for information).
Writes filters_lw.csv, filters_lw.md, fig_filters_lw.pdf/png."""
import sys, os
from pathlib import Path
HERE = Path(__file__).resolve().parent; BASE = HERE.parent / "baseline"; sys.path.insert(0, str(BASE)); os.chdir(BASE)
import numpy as np, pandas as pd
from statsmodels.tsa.filters.hp_filter import hpfilter
from lib import model as M, noteA
D0 = M.D0; idx = D0.index
lw = D0["rstar LW"]; e2 = M._e2m.reindex(idx); e10 = D0.einf_10y; e1 = D0.einf_1y
ff = noteA.fred("DFF").reindex(idx)
NOM = {"2-year": M.Y2M.reindex(idx), "10-year": D0.y10, "funds rate": ff}
EI = {"2-year": e2, "10-year": e10, "funds rate": e1}
TARGET = {"real": lw, "nominal": e2 + lw}
S1, S2 = ("1973-01", "2026-09"), ("1996-01", "2026-09")

def ma(x, n): return x.rolling(n, min_periods=n).mean()
def ewma(x, h):
    a = 1 - 0.5 ** (1 / h); x = x.dropna(); return x.ewm(alpha=a, adjust=False).mean().where(np.arange(len(x)) >= 36).reindex(idx)
def hp1s(x, lam, burn=36):
    x = x.dropna(); v = x.values; out = np.full(len(v), np.nan)
    for i in range(burn, len(v)): out[i] = hpfilter(v[:i + 1], lam)[1][-1]
    return pd.Series(out, index=x.index).reindex(idx)
def stats(f, tgt, s):
    d = pd.concat([f, tgt], axis=1).loc[s[0]:s[1]].dropna()
    if len(d) < 0.95 * len(pd.period_range(*s, freq="M")): return dict(n=len(d))
    e = d.iloc[:, 0] - d.iloc[:, 1]; b = np.polyfit(d.iloc[:, 0], d.iloc[:, 1], 1); ea = d.iloc[:, 1] - np.polyval(b, d.iloc[:, 0])
    oos = np.nan
    if s == S2:
        d1 = pd.concat([f, tgt], axis=1).loc["1973-01":"1995-12"].dropna()
        if len(d1) > 200:
            b1 = np.polyfit(d1.iloc[:, 0], d1.iloc[:, 1], 1); oos = float(np.sqrt(((d.iloc[:, 1] - np.polyval(b1, d.iloc[:, 0])) ** 2).mean()))
    return dict(n=len(d), rmse_oos_aff=oos, rmse=float(np.sqrt((e ** 2).mean())), bias=float(e.mean()), corr=float(d.corr().iloc[0, 1]), rmse_aff=float(np.sqrt((ea ** 2).mean())), a=b[1], b=b[0],
                err_0815=float(e.loc["2008-01":"2015-12"].mean()) if s == S1 else np.nan, err_16=float(e.loc["2016-01":].mean()) if s == S1 else np.nan)

rows = []; SER = {}
GRID = {"MA": [6, 12, 24, 36, 48, 60, 72, 84, 96, 120, 144, 180, 240, 300], "EWMA": [3, 6, 12, 18, 24, 36, 48, 60, 84, 120, 180, 240, 360, 480, 720],
        "HP": [1440, 14400, 129600, 1296000, 12960000, 129600000, 1296000000, 12960000000]}
for kind in ("real", "nominal"):
    for rate, x in NOM.items():
        z = (x - EI[rate]) if kind == "real" else x
        z = z.loc["1958-01":]
        for fam, grid in GRID.items():
            for p in grid:
                f = ma(z, p) if fam == "MA" else ewma(z, p) if fam == "EWMA" else hp1s(z, p)
                key = (kind, rate, fam, p); SER[key] = f
                for s in (S1, S2):
                    rows.append(dict(kind=kind, rate=rate, filter=fam, param=p, sample=f"{s[0][:4]}-{s[1][:4]}", **stats(f, TARGET[kind], s)))
R = pd.DataFrame(rows); R.to_csv(HERE / "filters_lw.csv", index=False, float_format="%.4f")

# references: the measures already tried
REF = {"Kiley r* (real)": ("real", D0["rstar Kiley"]), "forward 9-10y less e10 (real)": ("real", D0.y10 * np.nan)}
md = ["# One-sided trends that track one-sided Laubach-Williams r*", "",
      "Target: LW r* (real filters) and 2-year expected inflation + LW (nominal filters; the nominal neutral 2-year that the baseline subtracts). One-sided filters of monthly averages. "
      "RMSE of the level in pp (no rescaling); bias = mean(filter - target); errors 2008-15 and 2016-26 = mean error in those years. Burn-in 36 months for EWMA and HP; HP lambda is monthly (quarterly x 81).", ""]
def best_table(sample, by="rmse", n=1):
    T = R[(R["sample"] == sample) & R.rmse.notna()]
    B = T.loc[T.groupby(["kind", "rate", "filter"])[by].idxmin()].sort_values(["kind", "rmse"])
    out = ["| kind | rate | filter | best parameter | RMSE | bias | corr | RMSE affine in-sample (a, b) | " + ("error 2008-15 | error 2016-26 |" if sample == "1973-2026" else "RMSE affine fit 1973-95, out of sample |"), "|---|---|---|---|---|---|---|---|---|" + ("---|" if sample == "1973-2026" else "")]
    for _, r in B.iterrows():
        out.append(f"| {r.kind} | {r.rate} | {r['filter']} | {int(r.param)} | {r.rmse:.2f} | {r.bias:+.2f} | {r['corr']:.2f} | {r.rmse_aff:.2f} ({r.a:+.2f}, {r.b:.2f}) | " +
                   (f"{r.err_0815:+.2f} | {r.err_16:+.2f} |" if sample == "1973-2026" else f"{r.rmse_oos_aff:.2f} |"))
    return out
md += ["## Best parameter per rate and filter, fit over 1973-2026", ""] + best_table("1973-2026") + [""]
md += ["## Best parameter per rate and filter, fit over 1996-2026", ""] + best_table("1996-2026") + [""]
md += ["## Full grid, 2-year, fit over 1973-2026 (RMSE)", ""]
G = R[(R["sample"] == "1973-2026") & (R.rate == "2-year")].pivot_table(index=["kind", "filter", "param"], values=["rmse", "bias", "corr"]).round(2)
md += ["| kind | filter | param | RMSE | bias | corr |", "|---|---|---|---|---|---|"] + [f"| {k} | {f} | {p} | {r.rmse:.2f} | {r.bias:+.2f} | {r['corr']:.2f} |" for (k, f, p), r in G.iterrows()] + [""]
# references
for lab, ser, kind in (("Kiley r*", D0["rstar Kiley"], "real"),):
    s = stats(ser, TARGET[kind], S1); md += [f"Reference, {lab} vs LW, 1973-2026: RMSE {s['rmse']:.2f}, bias {s['bias']:+.2f}, corr {s['corr']:.2f}.", ""]
(HERE / "filters_lw.md").write_text("\n".join(md)); print("\n".join(md[:40]))

# figure: target and the best filter of each family, 2-year, real and nominal
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, axs = plt.subplots(2, 1, figsize=(9, 7), sharex=True)
T = R[(R["sample"] == "1973-2026") & R.rmse.notna() & (R.rate == "2-year")]
for ax, kind in zip(axs, ("real", "nominal")):
    t = TARGET[kind].loc["1970-01":]; ax.plot(t.index.to_timestamp(), t.values, "k", lw=2, label="LW" if kind == "real" else "e2 + LW")
    for fam, col in (("MA", "tab:blue"), ("EWMA", "tab:red"), ("HP", "tab:green")):
        b = T[(T.kind == kind) & (T["filter"] == fam)].sort_values("rmse").iloc[0]; f = SER[(kind, "2-year", fam, b.param)].loc["1970-01":]
        ax.plot(f.index.to_timestamp(), f.values, color=col, lw=1.2, label=f"{fam} {int(b.param)} (RMSE {b.rmse:.2f})")
    ax.set_title(f"{kind.capitalize()} 2-year: one-sided trends against {'LW r*' if kind == 'real' else '2-year expected inflation + LW r*'}", fontsize=9); ax.legend(frameon=False, fontsize=7); ax.axhline(0, color="0.8", lw=0.7)
fig.tight_layout(); fig.savefig(HERE / "fig_filters_lw.pdf"); fig.savefig(HERE / "fig_filters_lw.png", dpi=150)
