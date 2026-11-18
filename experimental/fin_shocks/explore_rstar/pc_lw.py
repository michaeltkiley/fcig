"""One-sided filters of the first principal component (level factor) of the 2-, 5- and 10-year yields, nominal and real, against one-sided LW r* (author, 18 Nov 2026).
Yields (monthly averages): 2-year = Note B's Y2M (DGS2, GSW before 1976-06), 5-year = FRED GS5, 10-year = FRED GS10. Real = less expected inflation at the matching horizon:
2-year e2 (Note B), 10-year e10 (Note A), 5-year Cleveland Fed EXPINF5YR from 1982 and, before, interpolated by maturity between e2 and e10 (e2 + 3/8 (e10 - e2)) shifted by the 1982-84 mean gap.
PC1: (a) full-sample loadings (1961-06 to 2026-09, covariance PCA of levels); (b) one-sided: expanding-window loadings, re-estimated each month from 1961-06 to t (from 1971-06, 10 years minimum).
Loadings scaled to sum to 1, so PC1 is a weighted average yield in percent. Filters (one-sided): none, EWMA half-life, trailing MA, one-sided HP (monthly lambda), Butterworth order 1-2.
Targets: LW (real) and e2 + LW (nominal). RMSE of the level 1973-2026 and 1996-2026. Writes pc_lw.csv, pc_lw.md, fig_pc_lw.png."""
import sys, os
from pathlib import Path
HERE = Path(__file__).resolve().parent; BASE = HERE.parent / "baseline"; sys.path.insert(0, str(BASE)); os.chdir(BASE)
import numpy as np, pandas as pd
from scipy import signal
from statsmodels.tsa.filters.hp_filter import hpfilter
from lib import model as M
D0 = M.D0; idx = D0.index; lw = D0["rstar LW"]
def fredm(name):
    d = pd.read_csv(HERE / "data_extra" / f"{name}.csv"); return pd.Series(pd.to_numeric(d.iloc[:, 1], errors="coerce").values, index=pd.PeriodIndex(d.iloc[:, 0], freq="M")).reindex(idx)
y2, y5, y10 = M.Y2M.reindex(idx), fredm("GS5"), D0.y10
e2, e10 = M._e2m.reindex(idx), D0.einf_10y
c5 = fredm("EXPINF5YR"); i5 = e2 + 3 / 8 * (e10 - e2); k = float((c5 - i5).loc["1982-01":"1984-12"].mean())
e5 = c5.combine_first(i5 + k)
chk = pd.concat([c5, i5 + k], axis=1).loc["1985":].dropna(); E5INFO = f"interpolated e5 vs Cleveland 5-year, 1985-2026: RMSE {np.sqrt(((chk.iloc[:,0]-chk.iloc[:,1])**2).mean()):.2f}, corr {chk.corr().iloc[0,1]:.2f}"
Y = {"nominal": pd.DataFrame({"2y": y2, "5y": y5, "10y": y10}), "real": pd.DataFrame({"2y": y2 - e2, "5y": y5 - e5, "10y": y10 - e10})}
TARGET = {"real": lw, "nominal": e2 + lw}
S1, S2 = ("1973-01", "2026-09"), ("1996-01", "2026-09")
def load(X):
    C = np.cov(X.values.T); v, V = np.linalg.eigh(C); w = V[:, -1]; w = w / w.sum(); return w, v[-1] / v.sum()
def pc_full(X): X = X.loc["1961-06":"2026-09"].dropna(); w, sh = load(X); return pd.Series(X.values @ w, index=X.index).reindex(idx), w, sh
def pc_onesided(X, minm=120):
    X = X.loc["1961-06":"2026-09"].dropna(); out = pd.Series(np.nan, index=X.index); W = {}
    for i in range(minm, len(X)):
        w, _ = load(X.iloc[:i + 1]); out.iloc[i] = X.values[i] @ w; W[X.index[i]] = w
    return out.reindex(idx), pd.DataFrame(W, index=X.columns).T
def ewma(x, h): x = x.dropna(); return x.ewm(alpha=1 - 0.5 ** (1 / h), adjust=False).mean().where(np.arange(len(x)) >= 36).reindex(idx)
def ma(x, n): return x.rolling(n, min_periods=n).mean()
def hp1s(x, lam):
    x = x.dropna(); v = x.values; o = np.full(len(v), np.nan)
    for i in range(36, len(v)): o[i] = hpfilter(v[:i + 1], lam)[1][-1]
    return pd.Series(o, index=x.index).reindex(idx)
def butter(x, order, P):
    x = x.dropna(); b, a = signal.butter(order, 2.0 / P); zi = signal.lfilter_zi(b, a) * x.iloc[0]; o = signal.lfilter(b, a, x.values, zi=zi)[0]; o[:36] = np.nan
    return pd.Series(o, index=x.index).reindex(idx)
def stats(f, tgt, s):
    d = pd.concat([f, tgt], axis=1).loc[s[0]:s[1]].dropna()
    if len(d) < 0.95 * len(pd.period_range(*s, freq="M")): return dict(n=len(d))
    e = d.iloc[:, 0] - d.iloc[:, 1]; o = dict(n=len(d), rmse=float(np.sqrt((e ** 2).mean())), bias=float(e.mean()), corr=float(d.corr().iloc[0, 1]))
    if s == S1: o.update({f"err_{k}s": float(v) for k, v in e.groupby(e.index.year // 10 * 10).mean().items()})
    return o
FILT = [("none", 0, lambda x, p: x)] + [("EWMA", h, ewma) for h in (12, 24, 36, 60, 84, 120, 180, 240, 360)] + [("MA", n, ma) for n in (12, 24, 36, 60, 96, 120, 144)] + \
       [("HP", l, hp1s) for l in (129600, 1296000, 12960000, 129600000, 1296000000)] + [(f"Butterworth {o}", P, (lambda o: lambda x, p: butter(x, o, p))(o)) for o in (1, 2) for P in (120, 240, 480, 720, 960, 1200)]
rows, SER, INFO = [], {}, []
for kind, X in Y.items():
    srcs = {"2-year alone": X["2y"]}
    pf, w, sh = pc_full(X); srcs["PC1, full-sample loadings"] = pf; INFO.append(f"{kind}: full-sample PC1 loadings (2y, 5y, 10y) = {np.round(w, 3).tolist()}, share of variance {sh:.3f}")
    po, W = pc_onesided(X); srcs["PC1, one-sided loadings"] = po
    INFO.append(f"{kind}: one-sided loadings range 2y {W['2y'].min():.2f}-{W['2y'].max():.2f}, 5y {W['5y'].min():.2f}-{W['5y'].max():.2f}, 10y {W['10y'].min():.2f}-{W['10y'].max():.2f}")
    srcs["simple average of 2y, 5y, 10y"] = X.mean(axis=1, skipna=False)
    for sl, x in srcs.items():
        for fam, p, fn in FILT:
            f = fn(x, p); SER[(kind, sl, fam, p)] = f
            for s in (S1, S2): rows.append(dict(kind=kind, source=sl, filter=fam, param=p, sample=f"{s[0][:4]}-{s[1][:4]}", **stats(f, TARGET[kind], s)))
R = pd.DataFrame(rows); R.to_csv(HERE / "pc_lw.csv", index=False, float_format="%.4f")
md = ["# One-sided filters of the level factor of the yield curve against one-sided LW r*", "", "Target: LW (real yields) and 2-year expected inflation + LW (nominal yields). RMSE of the level, pp. " + E5INFO + ".", ""] + [f"* {i}" for i in INFO] + [""]
for smp in ("1973-2026", "1996-2026"):
    T = R[(R["sample"] == smp) & R.rmse.notna()]
    B = T.loc[T.groupby(["kind", "source", "filter"]).rmse.idxmin()]
    B = B[B["filter"].isin(["none", "EWMA", "MA", "HP", "Butterworth 1", "Butterworth 2"])].sort_values(["kind", "rmse"])
    md += [f"## Best setting per source and filter, fit {smp}", "", "| kind | source | filter | param | RMSE | bias | corr |" + (" err 1970s | 80s | 90s | 00s | 10s | 20s |" if smp == "1973-2026" else ""),
           "|---|---|---|---|---|---|---|" + ("---|" * 6 if smp == "1973-2026" else "")]
    for _, r in B.iterrows():
        md.append(f"| {r.kind} | {r.source} | {r['filter']} | {int(r.param)} | {r.rmse:.2f} | {r.bias:+.2f} | {r['corr']:.2f} |" + ("".join(f" {r.get(f'err_{d}s', np.nan):+.2f} |" for d in (1970, 1980, 1990, 2000, 2010, 2020)) if smp == "1973-2026" else ""))
    md.append("")
(HERE / "pc_lw.md").write_text("\n".join(md)); print("\n".join(md))
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(9, 4.5)); t = lw.loc["1970-01":]; ax.plot(t.index.to_timestamp(), t.values, "k", lw=2, label="LW r*")
T = R[(R["sample"] == "1973-2026") & R.rmse.notna() & (R.kind == "real") & (R["filter"] == "EWMA")]
for sl in ("2-year alone", "PC1, one-sided loadings"):
    b = T[T.source == sl].sort_values("rmse").iloc[0]; f = SER[("real", sl, "EWMA", b.param)].loc["1970-01":]
    ax.plot(f.index.to_timestamp(), f.values, lw=1.2, label=f"{sl}, EWMA {int(b.param)} (RMSE {b.rmse:.2f})")
f = SER[("real", "PC1, one-sided loadings", "none", 0)].loc["1970-01":]; ax.plot(f.index.to_timestamp(), f.values, lw=0.6, color="0.6", label="real PC1, unfiltered")
ax.axhline(0, color="0.8", lw=0.7); ax.legend(frameon=False, fontsize=7); ax.set_title("Real yield level factor (2, 5, 10 years): one-sided filters against LW r*", fontsize=9)
fig.tight_layout(); fig.savefig(HERE / "fig_pc_lw.png", dpi=150)
