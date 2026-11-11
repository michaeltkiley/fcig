"""Counts, aggregates and multiple-testing adjustments for the forecast contrasts. Reads results/oos_*.csv, oos_errors.npz, act_weights.csv.
Primary family (r*-gap step): four alternative weight sets (FRBUS3, PC1, EQ, ACT) against the market weights, 5 outcomes x 3 horizons x 2 forms = 120 two-sided paired DM tests
(Holm and Benjamini-Hochberg reported). Secondary: the full indexes as given against the market weights; each set against the no-index baseline (Clark-West, one-sided);
change form against level form within each set. The real step repeats everything and is not pooled with the primary family."""
import sys; sys.dont_write_bytecode = True
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np, pandas as pd
from scipy.stats import norm
import common as c

P = pd.read_csv(c.OUT / "oos_pairs.csv"); K = pd.read_csv(c.OUT / "oos_cells.csv"); E = np.load(c.OUT / "oos_errors.npz")
P["p"] = 2 * (1 - norm.cdf(P.dm_t.abs())); K["p_cw"] = 1 - norm.cdf(K.cw_t)


def holm(p):
    o = np.argsort(p); m = len(p); adj = np.empty(m); run = 0
    for r, i in enumerate(o): run = max(run, (m - r) * p[i]); adj[i] = min(run, 1)
    return adj


def bh(p):
    o = np.argsort(p)[::-1]; m = len(p); adj = np.empty(m); run = 1
    for r, i in enumerate(o): run = min(run, p[i] * m / (m - r)); adj[i] = run
    return adj


PRIM = ["FRBUS3", "PC1", "EQ", "ACT"]; GIVEN = ["GS", "FRBUS_full", "NFCI", "ANFCI", "FCIG", "FRBUS_gi"]
out = []
for step in ("rstar", "real"):
    q = P[(P.step == step) & P.set.isin(PRIM)].copy(); q["p_holm"] = holm(q.p.values); q["p_bh"] = bh(q.p.values)
    print(f"\n=== {step}: primary family, {len(q)} DM tests; expected false rejections at 10 percent: {0.1 * len(q):.0f}")
    print("raw |t|>1.645:", int((q.p < .10).sum()), " Holm<0.10:", int((q.p_holm < .10).sum()), " BH<0.10:", int((q.p_bh < .10).sum()))
    for form in ("level", "change"):
        print(f"-- form {form}: set, geo-mean MSE ratio to market (15 cells), cells alt better/worse at 10% (raw), cells below 1, | geo-mean MSE ratio to baseline, CW cells sig (5% one-sided)")
        for s in PRIM + GIVEN:
            r = P[(P.step == step) & (P.form == form) & (P.set == s)]
            if len(r) == 0: continue
            k = K[(K.step == step) & (K.form == form) & (K.set == s)]
            print(f"  {s:11s} {np.exp(np.log(r.mse_ratio_mkt).mean()):.3f}  better {int(((r.p < .1) & (r.dm_t < 0)).sum())} worse {int(((r.p < .1) & (r.dm_t > 0)).sum())}  <1: {int((r.mse_ratio_mkt < 1).sum())}/{len(r)}"
                  f" | {np.exp(np.log(k.mse_ratio_base).mean()):.3f}  CW {int((k.p_cw < .05).sum())}/{len(k)}  <1 {int((k.mse_ratio_base < 1).sum())}")
        m = K[(K.step == step) & (K.form == form) & (K.set == "MKT")]
        print(f"  MKT vs baseline: {np.exp(np.log(m.mse_ratio_base).mean()):.3f}  CW {int((m.p_cw < .05).sum())}/{len(m)}  <1 {int((m.mse_ratio_base < 1).sum())}")
    out.append(q.assign(adj="holm/bh"))
    # level versus change within each set (paired DM, same origins)
    rows = []
    for s in ["MKT", "FRBUS3", "PC1", "EQ", "ACT", "GS", "FRBUS_full", "NFCI", "ANFCI"]:
        for oc in c.OUTCOMES:
            for h in c.HORIZONS:
                a = E[f"{step}|level|{oc}|{h}|{s}"]; b = E[f"{step}|change|{oc}|{h}|{s}"]; ta = E[f"{step}|level|{oc}|{h}|t"]; tb = E[f"{step}|change|{oc}|{h}|t"]
                assert (ta == tb).all()
                rows.append(dict(step=step, set=s, outcome=oc, h=h, ratio_change_over_level=(b ** 2).mean() / (a ** 2).mean(), dm_t=c.dm(b ** 2 - a ** 2, c.HACLAG(h))))
    L = pd.DataFrame(rows); L["p"] = 2 * (1 - norm.cdf(L.dm_t.abs())); L.to_csv(c.OUT / f"level_vs_change_{step}.csv", index=False)
    print(f"-- change vs level, same set (negative t: change better): cells with t<-1.645 / t>1.645 out of 15")
    print(L.groupby("set").apply(lambda g: pd.Series({"change_better": int((g.dm_t < -1.645).sum()), "level_better": int((g.dm_t > 1.645).sum()),
                                                      "geo_ratio": np.exp(np.log(g.ratio_change_over_level).mean())})).round(2).to_string())
    print("-- by outcome (primary sets pooled, change form): geo-mean MSE ratio to baseline for MKT; to MKT for each alt")
    r = K[(K.step == step) & (K.form == "change")]
    print(r[r.set.isin(["MKT"] + PRIM)].groupby(["outcome", "set"]).mse_ratio_base.apply(lambda x: np.exp(np.log(x).mean())).unstack().round(2).to_string())
pd.concat(out).to_csv(c.OUT / "primary_family.csv", index=False)
# weights summary
A = pd.read_csv(c.OUT / "act_weights.csv")
print("\n=== activity-fitted weights, 12 months ahead (NNLS shares, 90 percent bootstrap)")
for step in ("rstar", "real"):
    a = A[A.step == step]
    ins = lambda r, pre: all((r[f"lo90_{v}"] <= r[f"{pre}_{v}"] <= r[f"hi90_{v}"]) for v in c.VARS)
    a = a.assign(mkt_in=a.apply(lambda r: ins(r, "mkt"), axis=1), frbus_in=a.apply(lambda r: ins(r, "frbus"), axis=1),
                 width_y10=a.hi90_y10 - a.lo90_y10, width_eq=a.hi90_equities - a.lo90_equities, width_usd=a.hi90_dollar - a.lo90_dollar)
    print(step, "cells:", len(a), " market shares inside all three intervals:", int(a.mkt_in.sum()), " FRB/US:", int(a.frbus_in.sum()),
          " mean interval width (y10, eq, usd):", a[["width_y10", "width_eq", "width_usd"]].mean().round(2).tolist(),
          " Wald proportional-to-market rejected at 10%:", int((a.wald_p_prop_MKT < .1).sum()), " to FRB/US:", int((a.wald_p_prop_FRBUS < .1).sum()),
          " point fit all-zero:", int(a.pt_all_zero.sum()))
    print(a[["form", "outcome", "wald_p_prop_MKT", "wald_p_prop_FRBUS"]].round(2).to_string())
Pth = pd.read_csv(c.OUT / "act_paths.csv")
print("\nrecursive path of the fitted y10 share (change form, r* step): min/max over origins 1995-2025 by outcome")
x = Pth[(Pth.step == "rstar") & (Pth.form == "change")].groupby("outcome").s_y10.agg(["min", "max"]).round(2); print(x.to_string())
x = Pth[(Pth.step == "rstar") & (Pth.form == "change")].groupby("outcome").s_equities.agg(["min", "max"]).round(2); print(x.to_string())
