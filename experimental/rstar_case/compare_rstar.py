"""
Comparison and episodes on the r*-gap set (RSTAR_QA S6, option 2): the real-case metric (real_case/compare_real.py) on the r*-gap indexes (LW main).
    Main: 1974-2026, zero 1973-2026, against the real case. Check: 1990-2026, every index re-demeaned over 1990-2026 (indexes are linear in demeaned variables, so this equals
    demeaning the variables over 1990-2026), against the real and nominal cases (nominal -> real -> r*). Kiley in summary lines.
Usage: python experimental/rstar_case/compare_rstar.py      Outputs: compare_rstar.log (via tee), compare_rstar_levels.png
"""
import os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
RC = os.path.join(ROOT, "experimental", "real_case")
for p in (RC, os.path.join(ROOT, "experimental", "ms_fci"), HERE):
    sys.path.insert(0, p)
import macro_model_dl as DL
import macro_real as MR
import compare_real as CR
import rstar_indexes as RI

K = CR.K
SET = CR.SET


def rd(p):
    d = pd.read_csv(p, index_col=0); d.index = pd.PeriodIndex(d.index, freq="M"); return d


def indexes(lab="LW"):
    R = rd(os.path.join(HERE, "rstar_indexes_monthly.csv"))
    nf = rd(os.path.join(RC, "nfci_real_monthly.csv"))
    S = pd.DataFrame({"EP_4": R[f"EP_4 {lab}"], "EP_4+HP": R[f"EP_4+HP {lab}"], "MKT": R[f"MKT {lab}"], "GS": R[f"GS {lab}"], "ANFCI": nf["ANFCI_2y"],
                      "FCI-G 1yr": R[f"FCI-G 1yr {lab}"] / 0.4525})
    S.loc[:"1989-12", "ANFCI"] = np.nan
    return S.loc["1974-01":"2026-09"]


def groups(lab="LW"):
    D = rd(os.path.join(RC, "data_long_monthly.csv")).loc["1972-01":"2026-10"]
    EP = RI.ep_level(D); fac = 100 / EP.loc[RI.WIN].mean()
    r = RI.rstar(D.index)[lab]
    xeq = -fac * (EP - r)
    X = MR.data()
    X["policy rate"] = (D["real policy rate"] - r).reindex(X.index); X["10-year"] = (D["real 10-year"] - r).reindex(X.index); X["equities"] = xeq.reindex(X.index)
    Xd = X - X.loc[RI.WIN].mean()
    P, G = DL.paths("base")
    cols = MR.COLS0 + ["house prices"]
    c = Xd[cols] * (DL.phi_at(P[cols], 4) / G[4])
    gm = {"rates": ["policy rate", "10-year", "mortgage spread", "BBB spread"], "equities": ["equities"], "dollar": ["dollar"], "other": ["house prices"]}
    out = {"EP_4+HP": pd.DataFrame({g: c[v].sum(axis=1) for g, v in gm.items()})}
    out["EP_4"] = out["EP_4+HP"].assign(other=0.0)
    V = pd.DataFrame({"real policy rate": D["real policy rate"] - r, "real 10-year": D["real 10-year"] - r, "BBB spread": D["BBB spread"], "equities": xeq, "dollar": D["dollar"]}).loc[RI.WIN]
    Vd = V - V.mean()
    out["MKT"] = pd.DataFrame({"rates": RI.WM["real 10-year"] * Vd["real 10-year"], "equities": RI.WM["equities"] * Vd.equities, "dollar": RI.WM["dollar"] * Vd.dollar, "other": 0.0})
    out["GS"] = pd.DataFrame({"rates": K * (RI.WG["real policy rate"] * Vd["real policy rate"] + RI.WG["real 10-year"] * Vd["real 10-year"] + RI.WG["BBB spread"] * Vd["BBB spread"]),
                              "equities": K * RI.WG["equities"] * Vd.equities, "dollar": K * RI.WG["dollar"] * Vd.dollar, "other": 0.0})
    return out


def z90(S):
    return S.loc["1990-01":] - S.loc["1990-01":].mean()


def main():
    pd.set_option("display.width", 220)
    S = indexes("LW"); Gc = groups("LW")
    CR.report("MAIN, r* gaps (LW), 1974-2026 (zero 1973-2026)", S, Gc)
    S9 = z90(S); G9 = {k: z90(v) for k, v in Gc.items()}
    CR.report("CHECK, r* gaps (LW), 1990-2026 (zero 1990-2026)", S9, G9)
    Ski = indexes("Ki")
    real = CR.indexes(False); real9 = CR.indexes(True)
    mm = rd(os.path.join(ROOT, "experimental", "ms_fci", "macro_model_v3_monthly.csv"))
    tr = rd(os.path.join(ROOT, "experimental", "fci_compare", "transmission_v3_monthly.csv"))
    N = pd.DataFrame({"EP_4": mm["EP_4"], "EP_4+HP": mm["EP_4+HP"], "MKT": tr["MKT"], "GS": tr["GS"]}).loc["1990-01":"2026-09"]; N = N - N.mean()
    print("\n################ r* (LW) vs real case, 1974-2026 (Kiley in brackets) ################")
    for c in SET + ["FCI-G 1yr"]:
        j = pd.concat([S[c], real[c]], axis=1).dropna(); jk = pd.concat([Ski[c], real[c]], axis=1).dropna()
        print(f"   {c:9s} corr levels {j.corr().iloc[0, 1]:.2f} [{jk.corr().iloc[0, 1]:.2f}], 12m {j.diff(12).corr().iloc[0, 1]:.2f} [{jk.diff(12).corr().iloc[0, 1]:.2f}]; "
              f"latest r* {j.iloc[-1, 0]:+.2f} [{jk.iloc[-1, 0]:+.2f}], real {j.iloc[-1, 1]:+.2f}")
    print("\n################ nominal -> real -> r* (LW), 1990-2026, zero 1990-2026 ################")
    for c in SET:
        a = pd.concat([N[c], real9[c], S9[c]], axis=1, keys=["nom", "real", "r*"]).dropna()
        cc = a.corr()
        print(f"   {c:8s} corr nominal-real {cc.loc['nom', 'real']:.2f}, real-r* {cc.loc['real', 'r*']:.2f}, nominal-r* {cc.loc['nom', 'r*']:.2f}; sd {a.std().round(2).tolist()}; latest {a.iloc[-1].round(2).tolist()}")
    S9k = z90(Ski)
    for nm, D in (("nominal", N[SET]), ("real", real9[SET]), ("r* LW", S9[SET]), ("r* Kiley", S9k[SET])):
        D = D.dropna(); r = D.max(axis=1) - D.min(axis=1)
        print(f"   cross-index range (EP_4, EP_4+HP, MKT, GS), {nm:8s}: mean {r.mean():.2f}, 90th pct {r.quantile(0.9):.2f}, latest {r.iloc[-1]:.2f}")
    for nm, D in (("real", real[SET]), ("r* LW", S[SET]), ("r* Kiley", Ski[SET])):
        D = D.dropna(); r = D.max(axis=1) - D.min(axis=1)
        print(f"   cross-index range 1974-2026, {nm:8s}: mean {r.mean():.2f}, 90th pct {r.quantile(0.9):.2f}")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(13, 6.5))
    t = S.index.to_timestamp()
    for c, col, lb in (("EP_4", "black", "FRB/US eventual pressure (funds-rate pp)"), ("EP_4+HP", "#7f7f7f", "FRB/US with house prices"), ("MKT", "#ff7f0e", "Market index (2-year units)"),
                       ("GS", "#2ca02c", "GS replication (2-year units)"), ("ANFCI", "#9467bd", "ANFCI (2-year units, from 1990)")):
        ax.plot(t, S[c], color=col, lw=1.2, label=lb)
    ax.axhline(0, color="gray", lw=0.8); ax.grid(alpha=0.25); ax.legend(fontsize=9, frameon=False, loc="upper right")
    ax.set_ylabel("tighter above zero (vs 1973-2026 average)"); ax.set_title("Financial conditions indexes with rates as gaps to r* (Laubach-Williams), 1974-2026", fontsize=11)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "compare_rstar_levels.png"), dpi=130)


if __name__ == "__main__":
    main()
