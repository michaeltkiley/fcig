"""More one-sided filters tracking one-sided LW r* (continues filters_lw.py; items 1-3 of the author's list, 18 Nov 2026):
 1. Butterworth low-pass (causal IIR, scipy.signal.butter + lfilter), orders 1-4, cutoff period 60-480 months; initialized at the first value (lfilter_zi) to avoid a start transient.
 2. Double exponential smoothing: EWMA of an EWMA (smoother) and Brown's DEMA, 2 EWMA - EWMA(EWMA) (less lag), half-lives 24-360 months.
 3. Kalman filters (one-sided filtered state): local level and local linear trend, variances by maximum likelihood on the full sample of the rate (as LW's parameters are).
Rates: real 2-year, real funds rate, real 10-year (nominal rates do not track e2 + LW: filters_lw.md). Target LW; RMSE of the level, 1973-2026 and 1996-2026; mean error by decade.
Writes filters_lw2.csv, filters_lw2.md, fig_filters_lw2.png."""
import sys, os
from pathlib import Path
HERE = Path(__file__).resolve().parent; BASE = HERE.parent / "baseline"; sys.path.insert(0, str(BASE)); os.chdir(BASE)
import numpy as np, pandas as pd
from scipy import signal
import statsmodels.api as sm
from lib import model as M, noteA
D0 = M.D0; idx = D0.index; lw = D0["rstar LW"]
ff = noteA.fred("DFF").reindex(idx)
REAL = {"2-year": (M.Y2M.reindex(idx) - M._e2m.reindex(idx)), "funds rate": ff - D0.einf_1y, "10-year": D0.y10 - D0.einf_10y}
S1, S2 = ("1973-01", "2026-09"), ("1996-01", "2026-09")
BURN = 36
def wrap(v, x): out = pd.Series(v, index=x.index); out.iloc[:BURN] = np.nan; return out.reindex(idx)
def butter(x, order, period):
    x = x.dropna(); b, a = signal.butter(order, 2.0 / period); zi = signal.lfilter_zi(b, a) * x.iloc[0]
    return wrap(signal.lfilter(b, a, x.values, zi=zi)[0], x)
def ew(x, h): return x.ewm(alpha=1 - 0.5 ** (1 / h), adjust=False).mean()
def dewma(x, h, kind):
    x = x.dropna(); e1 = ew(x, h); e2 = ew(e1, h); return wrap((e2 if kind == "EWMA2" else 2 * e1 - e2).values, x)
def kalman(x, level):
    x = x.dropna(); m = sm.tsa.UnobservedComponents(x.values, level=level); r = m.fit(disp=False)
    st = r.filtered_state[0]; return wrap(st, x), dict(zip(m.param_names, np.round(r.params, 5)))
def stats(f, s):
    d = pd.concat([f, lw], axis=1).loc[s[0]:s[1]].dropna()
    if len(d) < 0.95 * len(pd.period_range(*s, freq="M")): return dict(n=len(d))
    e = d.iloc[:, 0] - d.iloc[:, 1]
    out = dict(n=len(d), rmse=float(np.sqrt((e ** 2).mean())), bias=float(e.mean()), corr=float(d.corr().iloc[0, 1]))
    if s == S1: out.update({f"err_{k}s": float(v) for k, v in e.groupby(e.index.year // 10 * 10).mean().items()})
    return out
rows, SER, KP = [], {}, {}
for rate, x in REAL.items():
    x = x.loc["1958-01":]
    for o in (1, 2, 3, 4):
        for P in (60, 96, 120, 180, 240, 300, 360, 480, 600, 720, 960, 1200):
            SER[(rate, f"Butterworth {o}", P)] = butter(x, o, P)
    for h in (24, 36, 60, 84, 120, 180, 240, 360, 480, 720):
        for k in ("EWMA2", "DEMA"): SER[(rate, k, h)] = dewma(x, h, k)
    SER[(rate, "EWMA", 180)] = wrap(ew(x.dropna(), 180).values, x.dropna())
    for lev, lab in (("llevel", "Kalman local level"), ("lltrend", "Kalman local linear trend")):
        f, p = kalman(x, lev); SER[(rate, lab, 0)] = f; KP[(rate, lab)] = p
for (rate, fam, p), f in SER.items():
    for s in (S1, S2): rows.append(dict(rate=rate, filter=fam, param=p, sample=f"{s[0][:4]}-{s[1][:4]}", **stats(f, s)))
R = pd.DataFrame(rows); R.to_csv(HERE / "filters_lw2.csv", index=False, float_format="%.4f")
md = ["# More one-sided filters tracking one-sided LW r* (Butterworth, double exponential, Kalman)", "",
      "RMSE of the level against LW, pp; param = cutoff period (Butterworth, months), half-life (EWMA2, DEMA, EWMA; months); Kalman variances by maximum likelihood. Data from 1958 (2-year from June 1961); 36-month burn-in. EWMA 180 = the best filter of filters_lw.md, for reference.", ""]
for smp in ("1973-2026", "1996-2026"):
    T = R[(R["sample"] == smp) & R.rmse.notna()]; B = T.loc[T.groupby(["rate", "filter"]).rmse.idxmin()].sort_values("rmse")
    md += [f"## Best setting per rate and filter, fit {smp}", "", "| rate | filter | best param | RMSE | bias | corr |" + (" err 1970s | 1980s | 1990s | 2000s | 2010s | 2020s |" if smp == "1973-2026" else ""),
           "|---|---|---|---|---|---|" + ("---|" * 6 if smp == "1973-2026" else "")]
    for _, r in B.iterrows():
        md.append(f"| {r.rate} | {r['filter']} | {int(r.param) if r.param else 'MLE'} | {r.rmse:.2f} | {r.bias:+.2f} | {r['corr']:.2f} |" +
                  ("".join(f" {r[f'err_{d}s']:+.2f} |" for d in (1970, 1980, 1990, 2000, 2010, 2020)) if smp == "1973-2026" else ""))
    md.append("")
G = R[(R["sample"] == "1973-2026") & (R.rate == "2-year") & R["filter"].str.startswith("Butterworth")].pivot_table(index="filter", columns="param", values="rmse").round(2)
md += ["## Butterworth, real 2-year, RMSE by order and cutoff period (1973-2026)", "", G.to_markdown(), ""]
md += ["## Kalman parameters (MLE)", ""] + [f"* {r}, {l}: {p}" for (r, l), p in KP.items()] + [""]
(HERE / "filters_lw2.md").write_text("\n".join(md)); print("\n".join(md))
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
T = R[(R["sample"] == "1973-2026") & R.rmse.notna() & (R.rate == "2-year")]
fig, ax = plt.subplots(figsize=(9, 4.5)); t = lw.loc["1970-01":]; ax.plot(t.index.to_timestamp(), t.values, "k", lw=2, label="LW r*")
for fam in ("EWMA", "Butterworth 2", "DEMA", "Kalman local linear trend"):
    b = T[T["filter"] == fam].sort_values("rmse").iloc[0]; f = SER[("2-year", fam, b.param)].loc["1970-01":]
    ax.plot(f.index.to_timestamp(), f.values, lw=1.2, label=f"{fam} {int(b.param) if b.param else ''} (RMSE {b.rmse:.2f})")
ax.axhline(0, color="0.8", lw=0.7); ax.legend(frameon=False, fontsize=7); ax.set_title("Real 2-year: one-sided filters against one-sided LW r*", fontsize=9)
fig.tight_layout(); fig.savefig(HERE / "fig_filters_lw2.png", dpi=150)
