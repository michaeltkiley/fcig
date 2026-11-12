"""Reads out/*.csv; writes out/summary.txt (counts, multiple-testing, tables used in RESULT.md)."""
import numpy as np, pandas as pd
from scipy import stats
from common import OUT
P = pd.read_csv(OUT / "paired.csv"); V = pd.read_csv(OUT / "vs_baseline.csv"); S = pd.read_csv(OUT / "subperiods.csv")
P["is_sig"] = (P.is_lo90 > 0) | (P.is_hi90 < 0); P["dm_p"] = 2 * (1 - stats.norm.cdf(abs(P.dm_t)))
L = []
def holm(p):
    p = np.sort(np.asarray(p)); ok = p <= 0.05 / (len(p) - np.arange(len(p))); return int(np.cumprod(ok).sum())
def w(*a): L.append(" ".join(str(x) for x in a))
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
for A, B in (("rstar", "nominal"), ("rstar", "real"), ("real", "nominal")):
    Q = P[(P.A == A) & (P.B == B)]
    w(f"\n=== {A} vs {B}: {len(Q)} tests (positive = {A} better)")
    w(f"OOS DM: |t|>1.645 in {int((Q.dm_t.abs()>1.645).sum())} (r* better {int((Q.dm_t>1.645).sum())}, worse {int((Q.dm_t<-1.645).sum())}); expected by chance at 10%: {0.1*len(Q):.1f}; "
      f"Holm-5% survivors: {holm(Q.dm_p)}; min p {Q.dm_p.min():.3f}")
    w(f"OOS ratio A/B (RMSE; Brier for recession) <1 in {int((Q.oos_ratio_AoverB<1).sum())} of {len(Q)}; mean DM t {Q.dm_t.mean():.2f}")
    w(f"IS diff: interval excludes 0 in {int(Q.is_sig.sum())} (positive {int((Q.is_lo90>0).sum())}, negative {int((Q.is_hi90<0).sum())}); point diff >0 in {int((Q.is_diff>0).sum())}; expected by chance {0.1*len(Q):.1f}")
    for o, g in Q.groupby("outcome"):
        w(f"  {o}: n={len(g)}  DM t mean {g.dm_t.mean():.2f}  share t>0 {(g.dm_t>0).mean():.2f}  IS diff mean {g.is_diff.mean():.4f} share>0 {(g.is_diff>0).mean():.2f}  ratio mean {g.oos_ratio_AoverB.mean():.3f}")
for A, B in (("rstar", "nominal"), ("rstar", "real")):
    Q = P[(P.A == A) & (P.B == B)]
    w(f"\n--- by family, {A} vs {B}: mean DM t over 13 combos; share of combos with r* better (OOS, IS)")
    w(Q.groupby("family").agg(dm_t=("dm_t", "mean"), oos_better=("dm_t", lambda s: (s > 0).mean()), is_better=("is_diff", lambda s: (s > 0).mean()), nsig_is=("is_sig", "sum")).round(2).to_string())
w("\n--- full table, rstar vs nominal and rstar vs real, one row per test")
cols = ["outcome", "h", "family", "A", "B", "n_is", "n_oos", "is_diff", "is_lo90", "is_hi90", "oos_ratio_AoverB", "dm_t"]
w(P[P.primary == 1][cols].round(3).to_string(index=False))
w("\n--- vs baseline (own lags only): Clark-West t (one-sided 1.28 at 10%), count significant by step")
V["cw_sig"] = V.cw_t > 1.282
w(V.groupby(["outcome", "step"]).agg(cw_sig=("cw_sig", "sum"), n=("cw_sig", "size"), is_gain=("is_gain", "mean"), oos_ratio=("oos_ratio", "mean")).round(3).to_string())
w("\n--- subperiods: mean over families and horizons of RMSE ratio r*/nominal and r*/real, by outcome")
w(S[S.A == "rstar"].groupby(["B", "outcome", "sub"]).ratio_AoverB.agg(["mean", "count"]).round(3).unstack("sub").to_string())
w("\n--- subperiods, share of the loss differential (sum of d in subperiod / total MSE_B), mean over families/h")
w(S[S.A == "rstar"].groupby(["B", "outcome", "sub"]).diff_share_of_mseB.mean().round(3).unstack("sub").to_string())
(OUT / "summary.txt").write_text("\n".join(L)); print("\n".join(L[:60]))
