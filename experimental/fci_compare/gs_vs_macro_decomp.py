"""
Decompose the difference between the GS replication and the macro-model (FRB/US-weighted) levels index into weights, data and coverage, all in pp of funds rate.

Both indexes are linear: GS = kappa * (0.044 FFR + 0.451 Y10 + 0.396 BBB - 0.049 (100 ln CAPE) + 0.060 (100 ln USD)),  kappa = funds-rate pp per GS index point (0.95 from the NS conversion);
macro = sum_j m_j x_j  over the same five variables (policy rate 0.0085, 10-year 0.569, BBB 0.127, equities -0.0316 per %, real dollar 0.100 per %) plus variables GS does not have
(mortgage spread 0.416 and, in one version, house prices -0.029 per % as a price-to-rent ratio). Every term is demeaned over 1990-2026.
D = macro - GS splits exactly into
    weights effect_j  = (m_j - g_j) * xM_j      on the macro index's data xM_j, for the five shared variables  (g_j = kappa * GS weight)
    data effect_j     = g_j * (xM_j - xG_j)     at the GS weights, where xG_j is the series GS uses (nominal rates and nominal dollar) and xM_j the macro index's
    coverage effect   = sum over macro-only variables of m_k x_k
Three comparisons: (1) GS nominal vs macro nominal (data difference = GS's nominal dollar versus the real dollar in the macro-model index), (2) GS as published (nominal) vs macro in real terms (the data effect then includes
the real treatment of the policy rate, 10-year and dollar), (3) GS real vs macro real (no data effect). Macro versions without and with house prices.
Usage: python experimental/fci_compare/gs_vs_macro_decomp.py [kappa]     Outputs: gs_vs_macro_decomp.png, gs_vs_macro_decomp.csv
"""
import os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "experimental", "path_fci"))
import path_fci as P
import fcig_replicate as R

KAPPA = float(sys.argv[1]) if len(sys.argv) > 1 else 0.945
GSW = {"policy rate": 0.044, "10-year": 0.451, "BBB spread": 0.396, "equities": -0.049, "dollar": 0.060}
SHARED = list(GSW)


def data_sets():
    out = {}
    for real in (False, True):
        P.L.REAL10 = real; P.L.RSTAR = False
        X, G = P.L.build()
        idx = X.index
        einf = X.einf if real else 0.0
        d = pd.DataFrame({"policy rate": X.ffr - einf, "10-year": X.y10, "BBB spread": X.bbb, "equities": 100 * X.lncape,
                          "dollar": 100 * (X.lnrusd if real else np.log(G.x_usd.reindex(idx)))})
        out[real] = d                                                        # the series GS uses: nominal rates and nominal dollar unless real
        dm = d.copy(); dm["dollar"] = 100 * X.lnrusd                         # the macro-model index always uses the real dollar
        out[("macro", real)] = dm
        out["X"] = X; out["G"] = G
    mort = R.fred("MORTGAGE30US").reindex(idx, method="ffill")
    spread = mort - out["G"].x_y10.reindex(idx)
    hp = np.log(R.splice_level(R.zillow(), R.fred("CSUSHPISA")))
    oer = np.log(P.L.get("CUSR0000SEHC"))
    hp = hp - oer.reindex(hp.index.union(oer.index)).sort_index().ffill().reindex(hp.index)
    hp = hp.reindex(idx.union(hp.index)).sort_index().ffill().reindex(idx) * 100
    return out, spread, hp


def main():
    ds, spread, hp = data_sets()
    base = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "frbus_sensitivities.csv"), index_col=0)["ffr_eq_q4"]
    ext = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "frbus_sensitivities_ext.csv"), index_col=0)["ffr_eq_q4"]
    M = {"policy rate": ext["rshort_direct"], "10-year": base["rg10"], "BBB spread": base["rbbbp"], "equities": -base["req"], "dollar": base["fpxr"]}
    EXTRA = {"mortgage spread": (ext["rme"], spread), "house prices": (ext["phouse"], hp)}
    g = {k: KAPPA * v for k, v in GSW.items()}
    print(f"kappa {KAPPA}: GS weights in funds-rate pp per unit: " + ", ".join(f"{k} {v:+.3f}" for k, v in g.items()))
    print("macro weights:                          " + ", ".join(f"{k} {v:+.3f}" for k, v in M.items()) + f", mortgage spread {ext['rme']:+.3f}, house prices {ext['phouse']:+.3f}")
    xm0 = ds[("macro", False)]
    print("\nweight gap x variable variation (full-sample sd of the demeaned variable; macro nominal data):")
    for j in SHARED:
        sdj = float(xm0[j].std())
        print(f"   {j:12s} GS {g[j]:+.3f}  macro {M[j]:+.3f}  gap {M[j] - g[j]:+.3f}  sd of variable {sdj:6.2f}  gap x sd {abs(M[j] - g[j]) * sdj:.2f} pp")
    res = {}
    cases = (("GS nominal vs macro nominal", False, False), ("GS nominal vs macro real", False, True), ("GS real vs macro real", True, True))
    for cname, gs_real, m_real in cases:
        xg = ds[gs_real]; xm = ds[("macro", m_real)]
        for hp_on in (False, True):
            W = pd.DataFrame({j: (M[j] - g[j]) * (xm[j] - xm[j].mean()) for j in SHARED})
            Dd = pd.DataFrame({j: g[j] * ((xm[j] - xm[j].mean()) - (xg[j] - xg[j].mean())) for j in SHARED})
            cov = pd.DataFrame({k: w * (x - x.mean()) for k, (w, x) in EXTRA.items() if hp_on or k != "house prices"})
            comp = pd.concat({"weights": W, "data": Dd, "coverage": cov}, axis=1).dropna()
            D = comp.sum(axis=1)
            macro = sum(M[j] * (xm[j] - xm[j].mean()) for j in SHARED) + cov.sum(axis=1)
            gs = sum(g[j] * (xg[j] - xg[j].mean()) for j in SHARED)
            assert np.allclose((macro - gs).reindex(D.index).values, D.values, atol=1e-8)
            tot = {t: comp[t].sum(axis=1) for t in ("weights", "data", "coverage")}
            share = {t: float(np.cov(tot[t], D)[0, 1] / D.var()) for t in tot}
            res[(cname, hp_on)] = (comp, D, tot)
            lab = f"{cname}, macro {'with' if hp_on else 'without'} house prices"
            print(f"\n[{lab}] sd of D (macro - GS) {D.std():.2f} pp; mean abs {D.abs().mean():.2f}; share of variance: " + ", ".join(f"{t} {v:.0%}" for t, v in share.items())
                  + f"; mean of D {D.mean():+.2f}")
            print("   mean abs by part:", {t: round(float(tot[t].abs().mean()), 2) for t in tot})
            v = comp.groupby(level=0, axis=1).sum() if False else None
            var_by = {f"{a}:{b}": float(np.cov(comp[(a, b)], D)[0, 1] / D.var()) for a, b in comp.columns}
            print("   variance share by term:", {k: f"{x:.0%}" for k, x in sorted(var_by.items(), key=lambda kv: -abs(kv[1])) if abs(x) > 0.02})
            # windows
            rows = []
            for wlab, a, b in (("1990-92", "1990-01-01", "1992-12-31"), ("2008-10..2009-03", "2008-10-01", "2009-03-31"), ("2012-2015", "2012-01-01", "2015-12-31"), ("2020-07..2021-12", "2020-07-01", "2021-12-31")):
                rows.append((wlab, D.loc[a:b].mean(), *(tot[t].loc[a:b].mean() for t in tot)))
            last = D.index[-1]
            for wlab, d0 in (("latest", None), ("chg since 27 Feb 2026", "2026-02-27"), ("chg since 27 Aug 2026", "2026-08-27")):
                f = (lambda s: s.iloc[-1]) if d0 is None else (lambda s, d0=d0: s.iloc[-1] - s.loc[:d0].iloc[-1])
                rows.append((wlab, f(D), *(f(tot[t]) for t in tot)))
            print("   " + pd.DataFrame(rows, columns=["window", "D", "weights", "data", "coverage"]).round(2).to_string(index=False).replace("\n", "\n   "))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 1, figsize=(13, 9), sharex=True)
    for a, (cname, hp_on) in zip(ax, (("GS nominal vs macro real", False), ("GS nominal vs macro real", True))):
        comp, D, tot = res[(cname, hp_on)]
        m = lambda s: s.resample("ME").last()
        a.plot(m(D).index, m(D), color="black", lw=1.8, label="difference: macro-model index minus GS")
        a.plot(m(tot["weights"]).index, m(tot["weights"]), color="#1f5fa8", lw=1.3, label="weights on shared variables")
        a.plot(m(tot["data"]).index, m(tot["data"]), color="#2ca02c", lw=1.3, label="data (nominal GS versus real macro model)")
        a.plot(m(tot["coverage"]).index, m(tot["coverage"]), color="#d62728", lw=1.3, label=f"variables only in the macro model ({'mortgage spread and house prices' if hp_on else 'mortgage spread'})")
        a.axhline(0, color="gray", lw=0.8); a.grid(alpha=0.25)
        a.set_ylabel("pp of funds rate"); a.set_title(f"GS as published (nominal) vs macro-model real index, {'with' if hp_on else 'without'} house prices (kappa {KAPPA})", fontsize=11)
    h, l = ax[1].get_legend_handles_labels()
    fig.legend(h, [x.replace("(mortgage spread and house prices)", "(mortgage spread; house prices in the lower panel)") for x in l], loc="lower center", ncol=2, fontsize=9, frameon=False)
    fig.tight_layout(rect=(0, 0.06, 1, 1)); fig.savefig(os.path.join(HERE, "gs_vs_macro_decomp.png"), dpi=130)
    rows = []
    for (cname, hp_on), (comp, D, tot) in res.items():
        rows.append(dict(case=cname, house_prices=hp_on, sd_D=D.std(), **{f"sd_{t}": tot[t].std() for t in tot}))
    pd.DataFrame(rows).round(3).to_csv(os.path.join(HERE, "gs_vs_macro_decomp.csv"), index=False)


if __name__ == "__main__":
    main()
