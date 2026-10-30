"""
Local-projection version of the FCI-G scale check and the horse race (user, 30 Oct; replaces the direct regressions in var_fcig_horse.py, RSTAR_QA S8a):
    u(t+12) = a + sum_{l=0}^{L-1} b_l u(t-l) + sum_{l=0}^{L-1} c_l x(t-l) + e,     L = 4 (main) or 12 lags, x = an index;  HAC (Newey-West, 12 lags)
    Dropped: origins t whose target (t+12) or any regressor month falls in 2020-01..2021-03.
    Reported: c_0 (effect of the current reading, holding past readings and u), sum of c_l (effect of a reading held over the lag window), Wald test of all c_l = 0,
    gain in adjusted R^2 over u lags only, and the out-of-sample RMSE ratio to the u-only projection (recursive, origins 1995-01..2025-09).
    FCI-G scale: FCI-G says a reading of +1 lowers growth over the next year by 1 pp, i.e. about +0.5 pp on the unemployment gap (Okun 2): compare with c_0.
Usage: python experimental/rstar_case/lp_unemp.py      Output: lp_unemp.log (via tee)
"""
import os, sys, warnings
import numpy as np, pandas as pd
import statsmodels.api as sm
warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import var_fcig_horse as H

BAD = lambda p: (p.year == 2020) or (p.year == 2021 and p.month <= 3)


def design(u, x, L, h=12):
    cols = {"y": u.shift(-h)}
    for l in range(L):
        cols[f"u{l}"] = u.shift(l)
    if x is not None:
        for l in range(L):
            cols[f"x{l}"] = x.shift(l)
    J = pd.DataFrame(cols)
    keep = [not (BAD(t + h) or any(BAD(t - l) for l in range(L))) for t in J.index]
    return J[keep]


def lp(u, x, L, start, end="2026-09"):
    J = design(u, x, L).loc[start:end].dropna()
    X = sm.add_constant(J.drop(columns="y"))
    r = sm.OLS(J.y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 12})
    r0 = sm.OLS(J.y, sm.add_constant(J[[f"u{l}" for l in range(L)]])).fit()
    xs = [f"x{l}" for l in range(L)]
    R = np.zeros((L, X.shape[1])); R[np.arange(L), [list(X.columns).index(c) for c in xs]] = 1
    w = r.wald_test(R, scalar=True)
    s = np.zeros(X.shape[1]); s[[list(X.columns).index(c) for c in xs]] = 1
    tsum = r.t_test(s)
    return {"c0": r.params["x0"], "se c0": r.bse["x0"], "sum c": float(np.ravel(tsum.effect)[0]), "se sum": float(np.ravel(tsum.sd)[0]), "Wald p": float(w.pvalue),
            "dR2 adj": r.rsquared_adj - r0.rsquared_adj, "n": len(J)}


def oos(u, x, L, start, first="1995-01", last="2025-09", h=12):
    J1 = design(u, x, L).loc[start:].dropna(subset=[c for c in design(u, x, L).columns if c != "y"])
    e1, e0 = [], []
    uc = [f"u{l}" for l in range(L)]
    for t in pd.period_range(first, last, freq="M"):
        if t not in J1.index or pd.isna(J1.y.get(t)):
            continue
        tr = J1.loc[:t - h].dropna()
        if len(tr) < 120:
            continue
        Xa = np.c_[np.ones(len(tr)), tr.drop(columns="y").values]; Xb = np.c_[np.ones(len(tr)), tr[uc].values]
        b1 = np.linalg.lstsq(Xa, tr.y.values, rcond=None)[0]; b0 = np.linalg.lstsq(Xb, tr.y.values, rcond=None)[0]
        row = J1.loc[t]
        e1.append(row.y - b1 @ np.r_[1, row.drop("y").values]); e0.append(row.y - b0 @ np.r_[1, row[uc].values])
    e1, e0 = np.array(e1), np.array(e0)
    return np.sqrt((e1 ** 2).mean() / (e0 ** 2).mean()), len(e1)


def main():
    u = H.MO.V.macro_data(False)["unemployment gap"]
    rd, RC = H.rd, H.RC
    fr, mr, mk, gs, nf, rs = (rd(os.path.join(RC, "fcig_real_monthly.csv")), rd(os.path.join(RC, "macro_real_monthly.csv")), rd(os.path.join(RC, "market_real_monthly.csv")),
                              rd(os.path.join(RC, "gs_real_monthly.csv")), rd(os.path.join(RC, "nfci_real_monthly.csv")), rd(os.path.join(HERE, "rstar_indexes_monthly.csv")))
    pub = pd.read_csv(os.path.join(H.ROOT, "raw", "fed_monthly_1yr.csv"), parse_dates=["date"]).set_index("date").iloc[:, 0]; pub.index = pub.index.to_period("M")
    pd.set_option("display.width", 220)
    print("A. FCI-G SCALE (c_0 should be about +0.5)")
    V = {"all real 1yr": (fr["1yr all real"], "1974-03"), "nominal 1yr (replication)": (fr["1yr nominal"], "1974-03"), "r* LW 1yr": (rs["FCI-G 1yr LW"], "1974-03"),
         "published 1yr, 1990-": (pub, "1990-01"), "nominal replication, 1990-": (fr["1yr nominal"], "1990-01"), "all real 3yr": (fr["3yr all real"], "1976-03")}
    for nm, (x, st) in V.items():
        for L in (4, 12):
            o = lp(u, x, L, st)
            print(f"   {nm:28s} L={L:2d}: c0 {o['c0']:+.3f} (se {o['se c0']:.3f}), sum c {o['sum c']:+.3f} (se {o['se sum']:.3f}), Wald p {o['Wald p']:.4f}, n {o['n']}")
    print("\nB. HORSE RACE: u(t+12) on current and lagged u and current and lagged index")
    IDX = {"real EP_4 (FRB/US)": mr.EP_4, "real MKT": mk.MKT_real, "real GS": gs.GS_real, "real FCI-G 1yr": fr["1yr all real"],
           "r* LW EP_4": rs["EP_4 LW"], "r* LW MKT": rs["MKT LW"], "r* LW GS": rs["GS LW"], "r* LW FCI-G 1yr": rs["FCI-G 1yr LW"],
           "r* Ki EP_4": rs["EP_4 Ki"], "r* Ki MKT": rs["MKT Ki"], "r* Ki GS": rs["GS Ki"], "r* Ki FCI-G 1yr": rs["FCI-G 1yr Ki"]}
    F = H.MO.LL.financial()[H.MO.VARS]
    IDX["nominal MKT (long)"] = pd.Series((F - F.mean()).values @ H.MO.W, index=F.index)
    for st, extra in (("1974-03", {}), ("1990-01", {"ANFCI": nf.ANFCI})):
        ids = dict(IDX, **extra)
        rows = []
        for nm, x in ids.items():
            row = {"index": nm}
            for L in (4, 12):
                o = lp(u, x, L, st)
                row[f"Wald p L{L}"] = o["Wald p"]; row[f"dR2 L{L}"] = o["dR2 adj"]; row[f"sum c L{L}"] = o["sum c"]
                row[f"OOS ratio L{L}"], _ = oos(u, x, L, st)
            rows.append(row)
        T = pd.DataFrame(rows).set_index("index").sort_values("OOS ratio L4")
        print(f"\n   sample {st}..2026-09 (targets to 2026-09; OOS origins 1995-01..2025-09):")
        print(T.round(3).to_string())


if __name__ == "__main__":
    main()
