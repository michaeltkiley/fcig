"""
Variance decomposition of each index by the project's four groups: rates (policy rate, 10-year, mortgage and BBB rates/spreads), equities, dollar, other (house prices).
share_g = cov(contribution of group g, index) / var(index); the four shares sum to 100% (a negative share means the group works against the rest of the index's variation).
Monthly (end of month), 1990-2026 and from 1998; levels (base) and 12-month changes. Macro model with house prices (nominal and real), market-based (NS), GS (replication; nominal and real), FCI-G
(official components, 3-year and 1-year lookback, to 2026-08).
Usage: python experimental/fci_compare/variance_by_group.py        Output: variance_by_group.csv
"""
import os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "experimental", "path_fci"))
import path_fci as P
import path_fci_gss_ns as Q
import fcig_replicate as R

GROUPS = ["rates", "equities", "dollar", "other"]


def me(df):
    d = df.resample("ME").last(); d.index = d.index.to_period("M"); return d


def build(real, wn):
    P.L.REAL10 = real; P.L.RSTAR = False
    X, G = P.L.build()
    idx = X.index
    einf = X.einf if real else 0.0
    base = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "frbus_sensitivities.csv"), index_col=0)["ffr_eq_q4"]
    ext = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "frbus_sensitivities_ext.csv"), index_col=0)["ffr_eq_q4"]
    mort = R.fred("MORTGAGE30US").reindex(idx, method="ffill"); spread = mort - G.x_y10.reindex(idx)
    hp = np.log(R.splice_level(R.zillow(), R.fred("CSUSHPISA"))); oer = np.log(P.L.get("CUSR0000SEHC"))
    hp = hp - oer.reindex(hp.index.union(oer.index)).sort_index().ffill().reindex(hp.index)
    hp = hp.reindex(idx.union(hp.index)).sort_index().ffill().reindex(idx) * 100
    dm = lambda s: s - s.mean()
    macro = pd.DataFrame({"rates": ext["rshort_direct"] * dm(X.ffr - einf) + base["rg10"] * dm(X.y10) + ext["rme"] * dm(spread) + base["rbbbp"] * dm(X.bbb),
                          "equities": -base["req"] * dm(100 * X.lncape), "dollar": base["fpxr"] * dm(100 * X.lnrusd), "other": ext["phouse"] * dm(hp)}).dropna()
    mkt = pd.DataFrame({"rates": wn["10-yr"] * 0.983 * dm(X.y10), "equities": wn["Equities (ln CAPE)"] * 0.983 * dm(100 * X.lncape),
                        "dollar": wn["Dollar (ln real)"] * 0.983 * dm(100 * X.lnrusd), "other": 0.0})
    usd = 100 * X.lnrusd if real else 100 * np.log(G.x_usd.reindex(idx))
    gs = pd.DataFrame({"rates": 0.945 * (0.044 * dm(X.ffr - einf) + 0.451 * dm(X.y10) + 0.396 * dm(X.bbb)), "equities": -0.049 * 0.945 * dm(100 * X.lncape),
                       "dollar": 0.060 * 0.945 * dm(usd), "other": 0.0})
    return macro, mkt, gs


def shares(C):
    T = C.sum(axis=1)
    return {g: float(np.cov(C[g], T)[0, 1] / T.var()) for g in GROUPS}, float(T.std())


def main():
    ev = P.events(P.USMPD)
    d = ev.dropna(subset=Q.FUT + ["UST2Y"] + list(Q.ENDOG.values())).reset_index(drop=True)
    gss, ns, _, _ = Q.gss_ns(d)
    wn = pd.Series(Q.estimate(d, ns, True)[0], index=list(Q.ENDOG))
    comps = {}
    for real in (False, True):
        tag = "real" if real else "nominal"
        macro, mkt, gs = build(real, wn)
        comps[f"Macro model with house prices, {tag}"] = me(macro); comps[f"Market-based (NS), {tag}"] = me(mkt); comps[f"GS, {tag}"] = me(gs)
    for lb in ("3yr", "1yr"):
        f = pd.read_csv(os.path.join(ROOT, "raw", f"fed_monthly_{lb}.csv"), parse_dates=["date"]).set_index("date"); f.index = f.index.to_period("M")
        comps[f"FCI-G, {lb} lookback"] = pd.DataFrame({"rates": f["FFR"] + f["10Yr Treasury"] + f["Mortgage Rate"] + f["BBB"], "equities": f["Stock Market"], "dollar": f["Dollar"], "other": f["House Prices"]})
    rows = []
    for name, C in comps.items():
        for samp, a in (("1990-", "1990-01"), ("1998-", "1998-01")):
            Cs = C.loc[a:].dropna()
            for kind, X_ in (("level", Cs), ("12m change", Cs.diff(12).dropna())):
                sh, sdv = shares(X_)
                rows.append(dict(index=name, sample=samp, basis=kind, **{g: round(100 * v) for g, v in sh.items()}, sd=round(sdv, 2)))
    R_ = pd.DataFrame(rows)
    R_.to_csv(os.path.join(HERE, "variance_by_group.csv"), index=False)
    pd.set_option("display.width", 200)
    for samp in ("1990-", "1998-"):
        for kind in ("level", "12m change"):
            t = R_[(R_["sample"] == samp) & (R_.basis == kind)].drop(columns=["sample", "basis"])
            print(f"\n=== Share of variance (%), {kind}, monthly, from {samp[:-1]} ===")
            print(t.to_string(index=False))


if __name__ == "__main__":
    main()
