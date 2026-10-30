"""
Comparison and episodes on the real set (REAL_QA R17): the nominal-case metric (fci_compare/metric_v3.py, episodes_v3.py) on the real indexes.
Units as in the nominal case: output lens pp of funds rate (EP_4, EP_4+HP, FCI-G all real / 0.4525); transmission lens pp of the 2-year yield per NS unit
(MKT real, GS real x 0.945/0.98, ANFCI / 0.185).
Samples: main 1974-01..2026-09, each index demeaned 1973-2026 (ANFCI from 1990 only, R15); check 1990-01..2026-09, demeaned 1990-2026 (the "_z90" versions),
    set against the nominal results over the same window.
Metrics: 1. level correlations; 2. 12-month changes (corr, sign agreement) and the FCI-G (1-year, all real) against 12-month changes of the level indexes;
    3. cross-index range and gap to the median (level set EP_4, EP_4+HP, MKT, GS; with ANFCI from 1990); 4. 10 closest / 10 widest non-overlapping 6-month windows,
    with each index's mean and, for the widest, the group split (rates incl. spreads; equities; dollar; other = house prices) of the gap between the extreme indexes.
Usage: python experimental/real_case/compare_real.py
Outputs: compare_real.log (via tee), compare_real_levels.png
"""
import os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "experimental", "ms_fci"))
import macro_model_dl as DL
import macro_real as MR

K = 0.945 / 0.98
SET = ["EP_4", "EP_4+HP", "MKT", "GS"]
GROUPS = ["rates", "equities", "dollar", "other"]


def rd(name):
    d = pd.read_csv(os.path.join(HERE, name), index_col=0); d.index = pd.PeriodIndex(d.index, freq="M"); return d


def indexes(z90):
    s = "_z90" if z90 else ""
    mr, mk, gs, nf, fg = rd("macro_real_monthly.csv"), rd("market_real_monthly.csv"), rd("gs_real_monthly.csv"), rd("nfci_real_monthly.csv"), rd("fcig_real_monthly.csv")
    S = pd.DataFrame({"EP_4": mr["EP_4" + s], "EP_4+HP": mr["EP_4+HP" + s], "MKT": mk["MKT_real" + s], "GS": gs["GS_real" + s] * K,
                      "ANFCI": nf["ANFCI_2y" + s], "FCI-G 1yr": fg["1yr all real"] / 0.4525})
    S.loc[:"1989-12", "ANFCI"] = np.nan
    return S.loc[("1990-01" if z90 else "1974-01"):"2026-09"]


def groups(z90):
    """Group contributions, same zero as the indexes."""
    win = slice("1990-01", "2026-10") if z90 else slice("1973-01", "2026-10")
    X = MR.data(); Xd = X - X.loc[win].mean()
    P, G = DL.paths("base")
    cols = MR.COLS0 + ["house prices"]
    phi = DL.phi_at(P[cols], 4) / G[4]
    c = Xd[cols] * phi
    gm = {"rates": ["policy rate", "10-year", "mortgage spread", "BBB spread"], "equities": ["equities"], "dollar": ["dollar"], "other": ["house prices"]}
    out = {"EP_4+HP": pd.DataFrame({g: c[v].sum(axis=1) for g, v in gm.items()})}
    out["EP_4"] = out["EP_4+HP"].assign(other=0.0)
    D = rd("data_long_monthly.csv")
    w = {"real 10-year": 0.6089, "equities": -0.0512, "dollar": 0.0654}
    m = {k: w[k] * (D[k] - D[k].loc[win].mean()) for k in w}
    out["MKT"] = pd.DataFrame({"rates": m["real 10-year"], "equities": m["equities"], "dollar": m["dollar"], "other": 0.0})
    gw = {"real policy rate": 0.044, "real 10-year": 0.451, "BBB spread": 0.396, "equities": -0.049, "dollar": 0.060}
    g = {k: gw[k] * (D[k] - D[k].loc[win].mean()) * K for k in gw}
    out["GS"] = pd.DataFrame({"rates": g["real policy rate"] + g["real 10-year"] + g["BBB spread"], "equities": g["equities"], "dollar": g["dollar"], "other": 0.0})
    return out


def windows(D, n=10, asc=True):
    rng = (D.max(axis=1) - D.min(axis=1)).rolling(6).mean().dropna()
    chosen = []
    for e, v in rng.sort_values(ascending=asc).items():
        if all(abs((e - c0).n) >= 6 for c0, _ in chosen): chosen.append((e, v))
        if len(chosen) == n: break
    return sorted(chosen)


def report(lab, S, Gc):
    print(f"\n################ {lab}: {S.index[0]}..{S.index[-1]} ################")
    L = S[SET + ["ANFCI"]]
    print("1. level correlations:\n" + L.corr().round(2).to_string())
    C = L.diff(12)
    print("\n2. 12-month changes, correlations:\n" + C.corr().round(2).to_string())
    sa = pd.DataFrame({a: {b: float((np.sign(C[a]) == np.sign(C[b]))[C[[a, b]].notna().all(axis=1)].mean()) for b in C} for a in C})
    print("   sign agreement:\n" + sa.round(2).to_string())
    f = S["FCI-G 1yr"]
    print("   FCI-G 1yr (all real, /0.4525) vs: " + ", ".join(f"{c} level {S[c].corr(f):+.2f} / 12m chg {C[c].corr(f):+.2f}" for c in SET + ["ANFCI"]))
    for nm, cols in (("level set without ANFCI", SET), ("level set with ANFCI (from 1990)", SET + ["ANFCI"])):
        D = S[cols].dropna()
        rng = D.max(axis=1) - D.min(axis=1)
        gap = D.sub(D.median(axis=1), axis=0).abs().mean()
        print(f"\n3. {nm}, {D.index[0]}..: range mean {rng.mean():.2f}, median {rng.median():.2f}, 90th pct {rng.quantile(0.9):.2f}, latest {rng.iloc[-1]:.2f}; "
              f"mean |gap to median|: " + ", ".join(f"{c} {v:.2f}" for c, v in gap.items()))
        print(f"   latest ({D.index[-1]}): " + ", ".join(f"{c} {v:+.2f}" for c, v in D.iloc[-1].items()))
        for kind, asc in (("closest", True), ("widest", False)):
            print(f"4. {kind} 6-month windows:")
            for e, v in windows(D, 10, asc):
                m = D.loc[e - 5:e].mean()
                line = f"   {e - 5}..{e} range {v:.2f}: " + ", ".join(f"{c} {m[c]:+.2f}" for c in D.columns)
                if not asc:
                    hi, lo = m.idxmax(), m.idxmin()
                    if hi in Gc and lo in Gc:
                        dg = (Gc[hi].loc[e - 5:e].mean() - Gc[lo].loc[e - 5:e].mean()).reindex(GROUPS)
                        line += f"  | {hi} - {lo}: " + ", ".join(f"{g} {dg[g]:+.2f}" for g in GROUPS)
                    else:
                        line += f"  | {hi} - {lo}"
                print(line)


def main():
    pd.set_option("display.width", 220)
    S = indexes(False); report("MAIN, real, 1974-2026 (zero 1973-2026)", S, groups(False))
    S9 = indexes(True); report("CHECK, real, 1990-2026 (zero 1990-2026)", S9, groups(True))
    mm = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "macro_model_v3_monthly.csv"), index_col=0); mm.index = pd.PeriodIndex(mm.index, freq="M")
    tr = pd.read_csv(os.path.join(ROOT, "experimental", "fci_compare", "transmission_v3_monthly.csv"), index_col=0); tr.index = pd.PeriodIndex(tr.index, freq="M")
    N = pd.DataFrame({"EP_4": mm["EP_4"], "EP_4+HP": mm["EP_4+HP"], "MKT": tr["MKT"], "GS": tr["GS"], "ANFCI": tr["ANFCI"]}).loc["1990-01":"2026-09"]
    N = N - N.mean()
    print("\n################ real vs nominal, 1990-2026 (both zero 1990-2026) ################")
    for c in N:
        j = pd.concat([S9[c], N[c]], axis=1).dropna()
        print(f"   {c:8s} corr levels {j.corr().iloc[0, 1]:.2f}, 12m {j.diff(12).corr().iloc[0, 1]:.2f}; sd real {j.iloc[:, 0].std():.2f}, nominal {j.iloc[:, 1].std():.2f}; latest real {j.iloc[-1, 0]:+.2f}, nominal {j.iloc[-1, 1]:+.2f}")
    for nm, D in (("real", S9[SET].dropna()), ("nominal", N[SET].dropna())):
        r = D.max(axis=1) - D.min(axis=1)
        print(f"   cross-index range (EP_4, EP_4+HP, MKT, GS), {nm}: mean {r.mean():.2f}, 90th pct {r.quantile(0.9):.2f}, latest {r.iloc[-1]:.2f}")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(13, 6.5))
    t = S.index.to_timestamp()
    for c, col in (("EP_4", "black"), ("EP_4+HP", "#7f7f7f"), ("MKT", "#ff7f0e"), ("GS", "#2ca02c"), ("ANFCI", "#9467bd")):
        ax.plot(t, S[c], color=col, lw=1.2, label={"EP_4": "FRB/US eventual pressure (funds-rate pp)", "EP_4+HP": "FRB/US with house prices",
                                                   "MKT": "Market index (2-year units)", "GS": "GS replication (2-year units)", "ANFCI": "ANFCI (2-year units, from 1990)"}[c])
    ax.axhline(0, color="gray", lw=0.8); ax.grid(alpha=0.25); ax.legend(fontsize=9, frameon=False, loc="upper right")
    ax.set_ylabel("tighter above zero (vs 1973-2026 average)"); ax.set_title("Real-rate financial conditions indexes, 1974-2026", fontsize=11)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "compare_real_levels.png"), dpi=130)


if __name__ == "__main__":
    main()
