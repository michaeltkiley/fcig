"""B: free the unit coefficient on r*. 
DERIVATION (lib/cases.py + lib/indexes.py market()): with weights w10 (10y yield), wE (equities, CAPE log points), wD (dollar) and, in the r* case,
   M_rstar = w10 (y10 - e10 - r) + wE * [-(100/EPbar)(EP - r)] + wD d,   EP = 100/CAPE, EPbar = its 1973-2026 mean, all demeaned.
 so  M_rstar = M_real-form + c r,   c = dM/dr = -w10 + wE (100/EPbar)   (both terms negative: wE < 0 multiplies a positive coefficient 100/EPbar),
 and the nominal -> real step contributes -w10 e10.  [The r* step also swaps 100 ln CAPE for the linear earnings-yield gap; that is part of the construct.]
TEST: regress outcome on M_rstar and, freely, r* (and e10): the unit restriction says the coefficient on r* (and on e10) is zero given M_rstar. 
 rho = (c b + delta)/(c b) = 1 + delta/(c b)  is the free coefficient on r* in units of the restriction (1 = restriction, 0 = no adjustment for r*).
 Also Wald p for rho=0.
SPECS (pre-specified, 8): kind {level, flow(12m changes)} x r* {LW, Kiley} x extra {r* only (R); e10 and r* (N)}. Outcome: u(t+12)-u(t), controls u, du12, HAC(18).
 Bootstrap CI for rho: moving blocks of 24 months of rows (pairs), 999 draws.
"""
from common import *
from scipy import stats
rng = np.random.default_rng(20261111)
W = read(RES / "market_weights.csv") if False else pd.read_csv(RES / "market_weights.csv", index_col=0).weight
EP = 100 / DM.cape; EPbar = EP.loc["1973-01":"2026-09"].mean()
c = -W["y10"] + W["equities"] * 100 / EPbar
print("w10", W["y10"], "wE", W["equities"], "EPbar", EPbar, "c", c)
# numerical check of c against lib/cases.py
from lib import cases, indexes
for rs in ("rstar LW", "rstar Kiley"):
    X1 = cases.inputs(DM.loc["1973-01":"2026-09"], "rstar", rs); X2 = DM.loc["1973-01":"2026-09"].copy(); dr = pd.Series(np.arange(len(X2)) / 100.0, index=X2.index); X2[rs] = X2[rs] + dr
    X2 = cases.inputs(X2, "rstar", rs)
    m1 = indexes.market(X1, W.values)[0]; m2 = indexes.market(X2, W.values)[0]
    k = float(((m2 - m1) * (dr - dr.mean())).sum() / ((dr - dr.mean()) ** 2).sum()); print(rs, "numerical dM/dr", k, "vs c", c)
    assert abs(k - c) < 1e-6
M = index("rstar", "market"); MK = index("rstar_kiley", "market")
rows = []
for rname, col, Mx in (("LW", "rstar LW", M), ("Kiley", "rstar Kiley", MK)):
    for kind in ("level", "flow"):
        for extra in ("R", "N"):
            r = DM[col]; e = DM.einf_10y
            f = (lambda s: s) if kind == "level" else (lambda s: s - s.shift(12))
            D = pd.DataFrame({"y": U.shift(-H) - U, "u": U, "du12": U - U.shift(12), "M": f(Mx), "r": f(r), "e": f(e)}).loc[START:LAST]
            D = D[keep(D.index)].dropna()
            cols = ["u", "du12", "M", "r"] + (["e"] if extra == "N" else [])
            def est(d):
                X = np.c_[np.ones(len(d)), d[cols].values]; return ols(d.y.values, X), X
            (b, e_), X = est(D); V = hac(X, e_, 18)
            iM, ir = 1 + cols.index("M"), 1 + cols.index("r")
            Rr = np.zeros((1, len(b))); Rr[0, ir] = 1
            Wd, pd_ = wald(b, V, Rr)                                  # rho = 1  (delta = 0)
            R0 = Rr.copy(); R0[0, iM] = c; W0, p0 = wald(b, V, R0)    # rho = 0  (delta + c b = 0)
            row = {"rstar": rname, "kind": kind, "extra": extra, "n": len(D), "first": str(D.index[0]), "last": str(D.index[-1]), "b_M": b[iM], "se_M": np.sqrt(V[iM, iM]),
                   "delta_r": b[ir], "se_delta": np.sqrt(V[ir, ir]), "c_b": c * b[iM], "rho": 1 + b[ir] / (c * b[iM]), "p_rho1": pd_, "p_rho0": p0, "sd_r": D.r.std()}
            if extra == "N":
                ie = 1 + cols.index("e"); row.update(delta_e=b[ie], se_e=np.sqrt(V[ie, ie]), expect_e0=0.0)
                Rj = np.zeros((2, len(b))); Rj[0, ir] = 1; Rj[1, ie] = 1; row["W_joint"], row["p_joint"] = wald(b, V, Rj)
                Rj0 = np.zeros((2, len(b))); Rj0[0, ir] = 1; Rj0[0, iM] = c; Rj0[1, ie] = 1; Rj0[1, iM] = -W["y10"]; row["p_joint_noadj"] = wald(b, V, Rj0)[1]  # no adjustment: r coef=-c b? see note
            rh = []
            for _ in range(999):
                d = D.iloc[blocks(len(D), 24, rng)]; (bb, _e), _X = est(d); rh.append(1 + bb[ir] / (c * bb[iM]))
            rh = np.array(rh); row["rho_lo90"], row["rho_hi90"] = np.percentile(rh, [5, 95]); row["rho_boot_med"] = np.median(rh)
            rows.append(row); print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in row.items()}, flush=True)
pd.DataFrame(rows).to_csv(OUT / "unit_restriction.csv", index=False)
