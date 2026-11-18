"""Bai-Perron breaks in place of a trend (author, 18 Nov 2026): Note B's model, no trend, with intercept shifts in the monthly equations at estimated dates.
Partial structural change (Bai and Perron 1998, 2003): only the constants of the u and pi equations shift; lag coefficients are common to all segments. One set of break dates for the
two equations (they are estimated jointly; Qu and Perron 2007 system form, here with each equation standardized by its no-break residual sd so the criterion is additive).
Dates: global minimization of the standardized SSR by dynamic programming over segments, alternating with OLS of the full regression given the dates, until the dates stop changing.
Number of breaks m = 0..5 by BIC (Yao 1988: T ln(SSR/T) summed over equations + (2 m + m) ln T, i.e. each break adds a date and a mean shift in each equation); minimum segment
10 percent of the sample (36 months from 1996, 62 from 1973). Versions: nominal, real, r*-gap (LW), without and with the FCI, 12 lags, March-December 2020 dropped.
Point estimates (the bootstrap would have to re-estimate the dates in each draw). Writes bp_breaks.md, bp_breaks.csv."""
import os, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; BASE = HERE.parent / "baseline"; sys.path.insert(0, str(BASE)); os.chdir(BASE)
import numpy as np, pandas as pd
from lib import model as M
_orig = M.macro_data; MAXB = 5; TRIM = 0.10; L = 12

def dp_breaks(z, m, h):
    """Exact global minimum of sum over segments of the squared deviations of the rows of z (T x k) from their segment means, m breaks, minimum segment length h (Bai-Perron DP)."""
    T = len(z); cs = np.vstack([np.zeros(z.shape[1]), np.cumsum(z, 0)]); cs2 = np.r_[0, np.cumsum((z ** 2).sum(1))]
    def cost(i, j): s = cs[j] - cs[i]; return cs2[j] - cs2[i] - (s @ s) / (j - i)          # segment rows i..j-1
    INF = np.inf; best = {1: np.array([cost(0, j) if j >= h else INF for j in range(T + 1)])}; arg = {}
    for k in range(2, m + 2):
        b = np.full(T + 1, INF); a = np.zeros(T + 1, int)
        for j in range(k * h, T + 1):
            cand = [(best[k - 1][i] + cost(i, j), i) for i in range((k - 1) * h, j - h + 1) if best[k - 1][i] < INF]
            if cand: b[j], a[j] = min(cand)
        best[k], arg[k] = b, a
    br, j = [], T
    for k in range(m + 1, 1, -1): j = arg[k][j]; br.append(j)
    return sorted(br), best[m + 1][T]

def fit_breaks(X0, Y, m):
    """Partial-change estimate with m common intercept breaks: alternate DP on the standardized partial residuals and OLS given the dates."""
    T = len(Y); h = int(np.ceil(TRIM * T)); sd = (Y - X0 @ np.linalg.lstsq(X0, Y, rcond=None)[0]).std(0)
    if m == 0: e = Y - X0 @ np.linalg.lstsq(X0, Y, rcond=None)[0]; return [], e
    B = np.linalg.lstsq(X0, Y, rcond=None)[0]; br = None
    for _ in range(50):
        z = (Y - X0[:, 1:] @ B[1:]) / sd                                                           # partial residual: data less the lag terms (constants free per segment)
        nb, _ = dp_breaks(z, m, h)
        if nb == br: break
        br = nb; D = np.column_stack([(np.arange(T) >= b).astype(float) for b in br]); B = np.linalg.lstsq(np.c_[X0, D], Y, rcond=None)[0][:X0.shape[1]]
    D = np.column_stack([(np.arange(T) >= b).astype(float) for b in br]); e = Y - np.c_[X0, D] @ np.linalg.lstsq(np.c_[X0, D], Y, rcond=None)[0]
    return br, e

BREAKS = {}
def choose(form, fci, start):
    X0, Y, P = _orig(form, fci, ["u", "pi"], L, start, None, "out", "none", periods=True); T = len(Y); out = []
    for m in range(MAXB + 1):
        br, e = fit_breaks(X0, Y, m); ssr = (e ** 2).sum(0)
        bic = sum(T * np.log(s / T) for s in ssr) + 3 * m * np.log(T); out.append((bic, m, br))
    bic, m, br = min(out); BREAKS[(form, fci, start)] = (m, [str(P[b]) for b in br], out); return br
def macro_data(form, fci, mvars, Lg, start, end, t2020, trend, periods=False):
    if trend != "bp": return _orig(form, fci, mvars, Lg, start, end, t2020, trend, periods)
    X, Y, P = _orig(form, fci, mvars, Lg, start, end, t2020, "none", periods=True)
    key = (form, fci, start)
    if key not in BREAKS: choose(form, fci, start)
    dates = [pd.Period(d, "M") for d in BREAKS[key][1]]
    if dates: X = np.c_[X, np.column_stack([np.array([p >= d for p in P], float) for d in dates])]
    return (X, Y, P) if periods else (X, Y)
M.macro_data = macro_data
HS = (12, 24, 36); rows = []
for start in ("1996-01", "1973-01"):
    for f, lab in (("nom", "Nominal"), ("real", "Real"), ("rstar", "r*-gap (LW)")):
        for fci in (0, f):
            for tr in ("none", "bp"):
                est = next(M.estimate(f, fci, "u,pi", start, None, "out", tr, 2, lags=(L,)))
                m, dates = (BREAKS[(f, fci, start)][:2]) if tr == "bp" else (0, [])
                for j, v in enumerate(est["names"]): rows.append(dict(start=start[:4], version=lab, fci="with FCI" if fci else "no FCI", trend="Bai-Perron breaks" if tr == "bp" else "no trend",
                                                                     breaks=m, dates=", ".join(dates), var=v, **{f"r{h}": est["s0"][h, j] for h in HS}))
            print(start, lab, fci, BREAKS[(f, fci, start)][:2], flush=True)
R = pd.DataFrame(rows); R.to_csv(HERE / "bp_breaks.csv", index=False, float_format="%.4f")
md = ["# No-trend versions with Bai-Perron intercept breaks (Note B's model, 12 lags, point estimates)", "",
      "Per +1 pp on the 2-year in the window: u = unemployment gap (pp), P = price level (percent). Breaks: common intercept shifts in the u and pi equations, dates estimated (global SSR, BIC, at most 5, minimum segment 10 percent). 2020 (March-December) dropped.", ""]
for fc in ("with FCI", "no FCI"):
    md += [f"## {fc}", "", "| start | version | trend | breaks (dates) | u 12m | u 24m | u 36m | P 12m | P 24m | P 36m |", "|---|---|---|---|---|---|---|---|---|---|"]
    for (s, v, tr), g in R[R.fci == fc].groupby(["start", "version", "trend"], sort=False):
        q = g.set_index("var"); md.append(f"| {s} | {v} | {tr} | {q.breaks.iloc[0]} ({q.dates.iloc[0] or '-'}) | " + " | ".join(f"{q.loc['u', f'r{h}']:+.2f}" for h in HS) + " | " + " | ".join(f"{q.loc['P', f'r{h}']:+.2f}" for h in HS) + " |")
    md.append("")
md += ["## BIC by number of breaks", ""] + [f"* {k[2][:4]} {k[0]} FCI={k[1]}: " + ", ".join(f"m={m}: {b:.1f}" for b, m, _ in v[2]) for k, v in BREAKS.items()]
(HERE / "bp_breaks.md").write_text("\n".join(md)); print("\n".join(md))
