"""Experiment (16 Nov 2026): two-variable quarterly VAR in the CBO output gap and one FCI; 4 lags; Cholesky in both orderings.

Question (user): if an FCI is in units of monetary policy, does a one-point FCI shock move the output gap by about as much as a one-point policy move?
Reported: response of the output gap (percent of potential) at 4, 8 and 12 quarters to an FCI shock scaled to raise the FCI by 1 point on impact.

Not part of the paper. Reads fci_paper/replication (lib, data, results) without changing it.

FCIs
  F, Y, B, G  the paper's four calibrations on the common assets (10-year yield, equity valuation, real broad dollar), common scale w'psi_F = 1
              (as in fci_paper/replication/26_four_way.py), at each step: nominal, real, rstar (baseline)
  Benchmarks  2-year Treasury yield (GS2, 1976Q3+), federal funds rate: the "one point of policy" the FCIs are scaled to
  Others      FCI-G (1-year, GDP growth units), NFCI, ANFCI (standard-deviation units): not in policy units, for sign and shape only
Specification: 1973Q1 (or first available) to 2026Q3; constant; dummies 2020Q1..2021Q1 (the paper's monthly convention, 2020-01..2021-03);
FCI as the quarterly average (main) or end-of-quarter month (check); output gap 100 (GDPC1 / GDPPOT - 1).
Ordering "gap first": the FCI shock has no same-quarter effect on the gap. "FCI first": it may.
Bands: moving-block bootstrap of residual pairs (blocks of 4 quarters), recursive, dummies fixed; 1000 draws; 68 and 90 percent.
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd

HERE = Path(__file__).resolve().parent
PKG = HERE.parents[1] / "fci_paper" / "replication"
sys.path.insert(0, str(PKG))
from lib import data, cases, indexes as I                      # noqa: E402
from lib.agree_core import MV, load_frbus, b_persist, ns_arr   # noqa: E402

OUT = HERE / "results"; OUT.mkdir(exist_ok=True)
P, H, REPS, BL, SEED = 4, 12, 1000, 4, 20261116
HZ = [4, 8, 12]
END_Q = pd.Period("2026Q3", "Q")
DUM = pd.period_range("2020Q1", "2021Q1", freq="Q")


# ------------------------------------------------------------------ weights (same algebra as 26_four_way.py)
raw = I.events_raw()
X5 = raw[["MP1", "MP2", "ED2", "ED3", "ED4"]].values; u2 = raw.UST2Y.values; Y3 = raw[["UST10Y", "SP500", "DXY"]].values
def fitg(f, Yv):
    fc = f - f.mean(); Yc = Yv - Yv.mean(0); psi = (fc @ Yc) / (fc @ fc); Rr = Yc - np.outer(fc, psi)
    Sg = Rr.T @ Rr / (len(f) - 2); w = np.linalg.solve(Sg, psi); return w / (psi @ w), psi
wF, pF = fitg(ns_arr(X5, u2), Y3); wY, pY = fitg(u2, Y3)
assert np.allclose(wF, pd.read_csv(PKG / "results" / "market_weights.csv", index_col=0).weight.values, atol=1e-8)
R_, Gq = load_frbus(); b = b_persist(R_, Gq, 4)
g = np.array([I.GS_W["y10"], I.GS_W["equities"], I.GS_W["dollar_gs"]])
W = {"F": wF, "Y": wY / (wY @ pF), "B": b / (b @ pF), "G": g / (g @ pF)}
pd.DataFrame(W, index=MV).to_csv(OUT / "weights.csv", float_format="%.6g")


# ------------------------------------------------------------------ series
def fred_q(name):
    s = pd.read_csv(HERE / "data" / f"{name}.csv", parse_dates=["observation_date"]).set_index("observation_date").iloc[:, 0]
    return pd.to_numeric(s, errors="coerce")
gdp, pot = fred_q("GDPC1"), fred_q("GDPPOT")
gap = (100 * (gdp / pot - 1)).dropna(); gap.index = gap.index.to_period("Q")

def to_q(m, how):
    q = m.groupby(m.index.asfreq("Q"))
    return q.mean() if how == "avg" else q.last()

D = data.load()
monthly = {}
for step in cases.CASES:
    X = cases.inputs(D, step)[MV]
    for k, w in W.items():
        monthly[f"{k}_{step}"] = X @ w
pub = pd.read_csv(PKG / "results" / "indexes_rstar.csv", index_col=0); pub.index = pd.PeriodIndex(pub.index, freq="M")
for c in ["fcig_1yr", "nfci", "anfci"]:
    monthly[c] = pub[c]
for name in ["GS2", "FEDFUNDS"]:
    s = fred_q(name); s.index = s.index.to_period("M"); monthly[name.lower()] = s


# ------------------------------------------------------------------ VAR
def build(y, x):
    df = pd.concat([y.rename("gap"), x.rename("fci")], axis=1).loc[:END_Q].dropna()
    df = df.loc[pd.Period("1973Q1", "Q"):]
    return df

def ols(Z, p, dums):
    T = len(Z); Yt = Z[p:]
    Xl = np.column_stack([np.ones(T - p)] + [Z[p - l:T - l] for l in range(1, p + 1)] + ([dums[p:]] if dums is not None else []))
    B = np.linalg.lstsq(Xl, Yt, rcond=None)[0]; U = Yt - Xl @ B
    return B, U, Xl

def irf(B, Sig, p, order, h=H):
    """Response of [gap, fci] to the FCI shock scaled to move the FCI 1 on impact. order 'gap' or 'fci' first."""
    A = [B[1 + 2 * (l - 1):1 + 2 * l].T for l in range(1, p + 1)]             # A_l (2x2): y_t = sum A_l y_{t-l}
    perm = [0, 1] if order == "gap" else [1, 0]
    Sp = Sig[np.ix_(perm, perm)]; Lp = np.linalg.cholesky(Sp)
    L = np.zeros((2, 2)); L[np.ix_(perm, perm)] = Lp
    j = 1                                                                     # the FCI shock column
    s0 = L[:, j] / L[1, j]
    Y = np.zeros((h + 1, 2)); Y[0] = s0
    for t in range(1, h + 1):
        Y[t] = sum(A[l - 1] @ Y[t - l] for l in range(1, p + 1) if t - l >= 0)
    return Y

def run(df, order, boot=True):
    Z = df.values; T = len(Z)
    dums = np.column_stack([(df.index == q).astype(float) for q in DUM if q in df.index]) if any(q in df.index for q in DUM) else None
    B, U, Xl = ols(Z, P, dums); Sig = U.T @ U / (len(U) - Xl.shape[1])
    pt = irf(B, Sig, P, order)
    if not boot: return pt, None
    rng = np.random.default_rng(SEED); n = len(U); nb = int(np.ceil(n / BL)); draws = []
    Uc = U - U.mean(0)
    for _ in range(REPS):
        st = rng.integers(0, n - BL + 1, nb); Ub = np.concatenate([Uc[s:s + BL] for s in st])[:n]
        Zb = Z.copy()
        for t in range(P, T):
            x = np.r_[1.0, np.concatenate([Zb[t - l] for l in range(1, P + 1)]), (dums[t] if dums is not None else [])]
            Zb[t] = x @ B + Ub[t - P]
        Bb, Ubb, Xb = ols(Zb, P, dums); Sb = Ubb.T @ Ubb / (len(Ubb) - Xb.shape[1])
        draws.append(irf(Bb, Sb, P, order))
    return pt, np.array(draws)


rows = []
for how in ["avg", "eoq"]:
    for name, m in monthly.items():
        df = build(gap, to_q(m, how))
        for order in ["gap", "fci"]:
            pt, dr = run(df, order, boot=(how == "avg"))
            r = dict(fci=name, quarterly=how, order=order + "_first", start=str(df.index[0]), end=str(df.index[-1]), n=len(df))
            for h in [0] + HZ:
                r[f"gap_h{h}"] = pt[h, 0]; r[f"fci_h{h}"] = pt[h, 1]
                if dr is not None:
                    for lo, hi, tag in [(5, 95, "90"), (16, 84, "68")]:
                        r[f"gap_h{h}_lo{tag}"], r[f"gap_h{h}_hi{tag}"] = np.percentile(dr[:, h, 0], [lo, hi])
            # cumulative FCI over the horizon (how persistent the 1-point shock is), quarters 0..h-1
            for h in HZ: r[f"fci_avg_0_{h-1}"] = pt[:h, 1].mean()
            rows.append(r)
            print(f"{name:16s} {how} {order:3s} gap h4 {pt[4,0]:+.2f} h8 {pt[8,0]:+.2f} h12 {pt[12,0]:+.2f} | fci h4 {pt[4,1]:+.2f} h8 {pt[8,1]:+.2f}", flush=True)
res = pd.DataFrame(rows); res.to_csv(OUT / "irf.csv", index=False, float_format="%.4f")

# FRB/US benchmark: GDP (percent) after a persistent 1 pp funds-rate rise (the yardstick the B index is scaled to)
fr = pd.DataFrame({"quarter": HZ, "frbus_gdp_persistent_ffr": [Gq[h] for h in HZ]})
fr.to_csv(OUT / "frbus_benchmark.csv", index=False, float_format="%.4f"); print(fr)


# ------------------------------------------------------------------ checks without bootstrap: the 2-year yield's sample (1976Q3+), and ending 2019Q4
chk = []
for tag, lo, hi in [("from1976Q3", "1976Q3", "2026Q3"), ("to2019Q4", "1973Q1", "2019Q4")]:
    for name, m in monthly.items():
        df = build(gap, to_q(m, "avg")).loc[pd.Period(lo, "Q"):pd.Period(hi, "Q")]
        for order in ["gap", "fci"]:
            pt, _ = run(df, order, boot=False)
            chk.append(dict(sample=tag, fci=name, order=order + "_first", n=len(df), **{f"gap_h{h}": pt[h, 0] for h in HZ}, **{f"fci_h{h}": pt[h, 1] for h in HZ}))
pd.DataFrame(chk).to_csv(OUT / "irf_checks.csv", index=False, float_format="%.4f")


# ------------------------------------------------------------------ summary table (markdown): quarterly average, both orderings, 90 percent bands; ratio to the 2-year yield
def fmt(r, h): return f"{r[f'gap_h{h}']:+.2f} [{r[f'gap_h{h}_lo90']:+.2f}, {r[f'gap_h{h}_hi90']:+.2f}]"
A = res[res.quarterly == "avg"].set_index(["fci", "order"])
lines = []
for order in ["gap_first", "fci_first"]:
    lines += [f"\n### Ordering: {order.replace('_', ' ')}\n", "| FCI | sample | gap h4 | gap h8 | gap h12 | FCI own h4 / h8 / h12 | ratio to 2-yr h4 / h8 / h12 |", "|---|---|---|---|---|---|---|"]
    base = A.loc[("gs2", order)]
    for name in monthly:
        r = A.loc[(name, order)]
        ratio = " / ".join(f"{r[f'gap_h{h}'] / base[f'gap_h{h}']:.1f}" for h in HZ) if name != "gs2" else "1"
        lines.append(f"| {name} | {r['start']}-{r['end']} | {fmt(r, 4)} | {fmt(r, 8)} | {fmt(r, 12)} | {r['fci_h4']:.2f} / {r['fci_h8']:.2f} / {r['fci_h12']:.2f} | {ratio} |")
(OUT / "summary.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))


# ------------------------------------------------------------------ FRB/US benchmark for each VAR path: treat the index's own VAR path as a funds-rate path
# implied(h) = sum_{s=0..h} (x_s - x_{s-1}) G[h - s + 1]: a sum of persistent steps, FRB/US quarter 1 = VAR quarter 0 (impact). Needs the full own path.
def path(name, order):
    df = build(gap, to_q(monthly[name], "avg")); pt, _ = run(df, order, boot=False); return pt
bm = []
for name in monthly:
    for order in ["gap", "fci"]:
        pt = path(name, order); x = pt[:, 1]; dx = np.diff(np.r_[0.0, x])
        imp = {h: sum(dx[s] * Gq[h - s + 1] for s in range(h + 1)) for h in HZ}
        bm.append(dict(fci=name, order=order + "_first", **{f"var_h{h}": pt[h, 0] for h in HZ}, **{f"frbus_h{h}": imp[h] for h in HZ},
                       **{f"ratio_h{h}": pt[h, 0] / imp[h] for h in HZ}))
BM = pd.DataFrame(bm); BM.to_csv(OUT / "frbus_implied.csv", index=False, float_format="%.4f")
print(BM.to_string(float_format=lambda v: f"{v:+.2f}"))
