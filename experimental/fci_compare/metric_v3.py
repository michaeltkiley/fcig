"""
Pre-specified comparison metric (METRIC.md) re-run on the v3 indexes (INDEX_QA.md specification), monthly 1990-01..2026-10. Units as agreed (answer 35):
output lens = pp of funds rate (EP_4, EP_4+HP, CP_4, FCI-G / 0.4525); transmission lens = pp of the 2-year yield per NS unit (MKT, MKT+Baa, MKT+Baa diag, GS,
NFCI, ANFCI). Every index demeaned over 1990-2026.
Metrics:
  1. levels: pairwise correlation and slope (level indexes)
  2. 12-month changes: correlation, slope, sign agreement
  3. gap to the cross-index median and cross-index range, over the level set used since the second pass (METRIC.md deviation log):
     EP_4, EP_4+HP, MKT, GS, ANFCI; plus a sensitivity without ANFCI (its conversion is imprecise)
  4. episodes: non-overlapping 6-month windows ranked by the mean range (4 closest, 4 widest), every index's mean in each
  5. groups (rates incl. policy rate and spreads; equities; dollar; other; ANFCI macro adjustment): latest, change since end-Feb 2026 and end-Aug 2026,
     and each index's group means in the episode windows
  FCI-G: compared with levels and with 12-month changes of the level indexes (answer 15).
Inputs: ms_fci/macro_model_v3_monthly.csv, transmission_v3_monthly.csv, nfci_groups_monthly.csv, fcig_replication_monthly.csv, raw official FCI-G;
        group components rebuilt here for EP_4+HP (macro_model_dl.levels_data and FRB/US q4 weights), MKT (NS weights), GS (replication components x 0.945/0.98).
Usage: python experimental/fci_compare/metric_v3.py
Outputs: metric_v3.log (via tee), metric_v3_groups.csv, metric_v3_levels.png, metric_v3_groups.png
"""
import os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for sub in ("ms_fci", "path_fci"):
    sys.path.insert(0, os.path.join(ROOT, "experimental", sub))
import macro_model_levels as MLV
import path_fci as P
import path_fci_gss_ns as Q

LEVEL_SET = ["EP_4", "EP_4+HP", "MKT", "GS", "ANFCI"]
GROUPS = ["rates", "equities", "dollar", "other"]


def rd(path):
    d = pd.read_csv(path, index_col=0); d.index = pd.PeriodIndex(d.index, freq="M"); return d


def me(s):
    s = s.resample("ME").last(); s.index = s.index.to_period("M"); return s


def group_components():
    """Monthly group contributions (demeaned 1990-2026) for EP_4+HP, MKT, GS, FCI-G (1yr, 3yr), NFCI, ANFCI."""
    comp, X, G = MLV.components(False, verbose=False)
    gm = {"rates": ["policy rate", "10-year", "mortgage spread", "BBB spread"], "equities": ["equities"], "dollar": ["dollar"], "other": ["house prices"]}
    out = {"EP_4+HP": pd.DataFrame({g: me(comp[c].sum(axis=1)) for g, c in gm.items()})}
    ev = P.events(P.USMPD)
    d = ev.dropna(subset=Q.FUT + ["UST2Y"] + list(Q.ENDOG.values())).reset_index(drop=True)
    _, ns, _, _ = Q.gss_ns(d)
    w = pd.Series(Q.estimate(d, ns, True)[0], index=list(Q.ENDOG))
    mk = {n: w[n] * P.VARS[n][1] * (X[P.VARS[n][0]] - X[P.VARS[n][0]].mean()) for n in w.index}
    out["MKT"] = pd.DataFrame({"rates": me(mk["10-yr"]), "equities": me(mk["Equities (ln CAPE)"]), "dollar": me(mk["Dollar (ln real)"])})
    k = 0.945 / 0.98
    out["GS"] = pd.DataFrame({"rates": me((G.c_ffr + G.c_y10 + G.c_bbb) * k), "equities": me(G.c_cape * k), "dollar": me(G.c_usd * k)})
    rep = pd.read_csv(os.path.join(ROOT, "fcig_replication_monthly.csv")); rep.index = pd.PeriodIndex(rep["month"], freq="M")
    for lb in ("1yr", "3yr"):
        out[f"FCI-G {lb}"] = pd.DataFrame({"rates": rep[[f"{lb}|FFR", f"{lb}|10Yr Treasury", f"{lb}|Mortgage Rate", f"{lb}|BBB"]].sum(axis=1) / 0.4525,
                                           "equities": rep[f"{lb}|Stock Market"] / 0.4525, "dollar": rep[f"{lb}|Dollar"] / 0.4525, "other": rep[f"{lb}|House Prices"] / 0.4525})
    ng = rd(os.path.join(HERE, "nfci_groups_monthly.csv"))
    for nm in ("NFCI", "ANFCI"):
        c = {k_.split("|")[1]: v for k_, v in ng.items() if k_.startswith(nm + "|")}
        df = pd.DataFrame({"rates": c["rates: policy and Treasury"] + c["rates: spreads"], "equities": c["equities"], "dollar": c["dollar"], "other": c["other"]})
        if "macro adjustment" in c: df["macro adjustment"] = c["macro adjustment"]
        out[nm] = df
    res = {}
    for k_, df in out.items():
        df = df.loc["1990-01":"2026-10"].reindex(columns=GROUPS + (["macro adjustment"] if "macro adjustment" in df else [])).fillna(0.0)
        res[k_] = df - df.mean()
    return res


def main():
    mm = rd(os.path.join(ROOT, "experimental", "ms_fci", "macro_model_v3_monthly.csv"))
    tr = rd(os.path.join(HERE, "transmission_v3_monthly.csv"))
    f1 = pd.read_csv(os.path.join(ROOT, "raw", "fed_monthly_1yr.csv"), parse_dates=["date"]).set_index("date").iloc[:, 0]; f1.index = f1.index.to_period("M")
    f3 = pd.read_csv(os.path.join(ROOT, "raw", "fed_monthly_3yr.csv"), parse_dates=["date"]).set_index("date").iloc[:, 0]; f3.index = f3.index.to_period("M")
    rep = pd.read_csv(os.path.join(ROOT, "fcig_replication_monthly.csv")); rep.index = pd.PeriodIndex(rep["month"], freq="M")
    f1 = pd.concat([f1, rep["1yr|FCI-G"].loc[f1.index[-1] + 1:]]); f3 = pd.concat([f3, rep["3yr|FCI-G"].loc[f3.index[-1] + 1:]])
    S = pd.DataFrame({"EP_4": mm["EP_4"], "EP_4+HP": mm["EP_4+HP"], "CP_4": mm["CP_4"], "MKT": tr["MKT"], "MKT+Baa": tr["MKT+Baa"], "MKT+Baa diag": tr["MKT+Baa diag"],
                      "GS": tr["GS"], "NFCI": tr["NFCI"], "ANFCI": tr["ANFCI"], "FCI-G 1yr": f1 / 0.4525, "FCI-G 3yr": f3 / 0.4525}).loc["1990-01":"2026-10"]
    S = S - S.mean()
    pd.set_option("display.width", 230)
    lev = ["EP_4", "EP_4+HP", "CP_4", "MKT", "MKT+Baa", "MKT+Baa diag", "GS", "NFCI", "ANFCI"]
    print("Units: EP_4, EP_4+HP, CP_4, FCI-G in pp of funds rate; MKT, MKT+Baa, GS, NFCI, ANFCI in pp of the 2-year yield per NS unit. Demeaned 1990-2026.")
    print("\nsd / latest:\n" + pd.DataFrame({"sd": S.std(), "latest": S.ffill().iloc[-1]}).round(2).T.to_string())
    # 1-2
    rows = []
    for i, a in enumerate(lev):
        for c in lev[i + 1:]:
            j = S[[a, c]].dropna(); ch = j.diff(12).dropna()
            rows.append(dict(pair=f"{a} / {c}", corr_lev=j[a].corr(j[c]), slope_lev=np.polyfit(j[a], j[c], 1)[0], corr_12m=ch[a].corr(ch[c]),
                             slope_12m=np.polyfit(ch[a], ch[c], 1)[0], sign_12m=float((np.sign(ch[a]) == np.sign(ch[c])).mean())))
    print("\n(1-2) pairwise, levels and 12-month changes:\n" + pd.DataFrame(rows).round(2).to_string(index=False))
    rows = []
    for f in ("FCI-G 1yr", "FCI-G 3yr"):
        for n in lev:
            a = S[[f, n]].dropna(); b = pd.concat([S[f], S[n].diff(12)], axis=1).dropna()
            rows.append(dict(fcig=f, index=n, corr_level=a.corr().iloc[0, 1], corr_with_12m_change=b.corr().iloc[0, 1], slope_on_12m_change=np.polyfit(b.iloc[:, 1], b.iloc[:, 0], 1)[0]))
    print("\nFCI-G against levels and 12-month changes:\n" + pd.DataFrame(rows).pivot(index="index", columns="fcig").round(2).to_string())
    # 3-4
    groups = group_components()
    gtab = []
    for setname, cols in (("main", LEVEL_SET), ("without ANFCI", [c for c in LEVEL_SET if c != "ANFCI"])):
        D = S[cols].dropna()
        rng = D.max(axis=1) - D.min(axis=1)
        print(f"\n(3) cross-index range, set {setname} {cols}: mean {rng.mean():.2f}, max {rng.max():.2f} ({rng.idxmax()}), latest {rng.iloc[-1]:.2f}")
        print("    mean abs gap to cross-index median: " + str(D.sub(D.median(axis=1), axis=0).abs().mean().round(2).to_dict()))
        roll = rng.rolling(6).mean().dropna()
        for lab, asc in (("closest alignment", True), ("widest differences", False)):
            chosen = []
            for e, v in roll.sort_values(ascending=asc).items():
                if all(abs((e - c0).n) >= 6 for c0, _ in chosen): chosen.append((e, v))
                if len(chosen) == 4: break
            print(f"  (4) {lab}:")
            for e, v in sorted(chosen):
                m = D.loc[e - 5:e].mean()
                print(f"      {e - 5}..{e} (mean range {v:.2f}): " + ", ".join(f"{n} {m[n]:+.2f}" for n in cols))
                if setname == "main":
                    for n in ("EP_4+HP", "MKT", "GS", "ANFCI"):
                        g = groups[n].loc[e - 5:e].mean()
                        gtab.append(dict(window=f"{e - 5}..{e}", kind=lab, index=n, **g.round(3).to_dict()))
    # 5
    print("\n(5) groups: latest, change since end-Feb 2026 and end-Aug 2026 (index units as above)")
    rows = []
    for n, df in groups.items():
        for lab, d0 in (("latest", None), ("chg since 2026-02", "2026-02"), ("chg since 2026-08", "2026-08")):
            v = df.iloc[-1] if d0 is None else df.iloc[-1] - df.loc[d0]
            rows.append(dict(index=n, window=lab, total=float(v.sum()), **v.round(2).to_dict()))
    G5 = pd.DataFrame(rows)
    print(G5.round(2).to_string(index=False))
    print("\n    group sd since 1990: " + "; ".join(f"{n}: " + ", ".join(f"{g} {df[g].std():.2f}" for g in df.columns) for n, df in groups.items()))
    print("\n(4b) group means in the episode windows (main set):")
    E = pd.DataFrame(gtab); print(E.to_string(index=False))
    pd.concat([G5.assign(table="latest/changes"), E.assign(table="episodes")]).to_csv(os.path.join(HERE, "metric_v3_groups.csv"), float_format="%.3f", index=False)
    # figures
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(3, 1, figsize=(13, 14), sharex=True)
    t = S.index.to_timestamp()
    D = S[LEVEL_SET]; rng = D.max(axis=1) - D.min(axis=1); roll = rng.rolling(6).mean()
    for n, c, lab in (("EP_4", "black", "Macro model, eventual pressure (4 qtr)"), ("EP_4+HP", "#7f7f7f", "Macro model with house prices"), ("CP_4", "#1f5fa8", "Macro model, current pressure (4 qtr)")):
        axes[0].plot(t, S[n], color=c, lw=1.3, label=lab)
    axes[0].set_title("Output lens, pp of funds rate", fontsize=11)
    for n, c, lab in (("MKT", "#ff7f0e", "Market-based (NS weights)"), ("GS", "#2ca02c", "GS replication"), ("ANFCI", "#8c564b", "ANFCI"), ("NFCI", "#d62728", "NFCI")):
        axes[1].plot(t, S[n], color=c, lw=1.2, label=lab)
    axes[1].set_title("Transmission lens, pp of 2-year yield per NS unit", fontsize=11)
    axes[2].plot(t, rng, color="black", lw=1.2, label="Cross-index range (EP_4, EP_4+HP, MKT, GS, ANFCI)")
    axes[2].plot(t, (S[["EP_4", "EP_4+HP", "MKT", "GS"]].max(axis=1) - S[["EP_4", "EP_4+HP", "MKT", "GS"]].min(axis=1)), color="#1f5fa8", lw=1.0, label="Range without ANFCI")
    axes[2].set_title("Cross-index range (mixed units, as agreed)", fontsize=11)
    for ax in axes:
        ax.axhline(0, color="gray", lw=0.8); ax.grid(alpha=0.25); ax.legend(loc="upper right", fontsize=9, frameon=False)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "metric_v3_levels.png"), dpi=130)
    fig, axes = plt.subplots(2, 3, figsize=(15, 8), sharex=True)
    for ax, n in zip(axes.flat, ["EP_4+HP", "MKT", "GS", "FCI-G 1yr", "NFCI", "ANFCI"]):
        df = groups[n].loc["1990-01":]
        for g, c in zip(df.columns, ("#1f5fa8", "#2ca02c", "#9467bd", "#8c564b", "#7f7f7f")):
            ax.plot(df.index.to_timestamp(), df[g], color=c, lw=1.0, label=g)
        ax.axhline(0, color="gray", lw=0.8); ax.grid(alpha=0.25); ax.set_title(n, fontsize=10); ax.legend(fontsize=7, frameon=False, loc="upper left")
    fig.suptitle("Contributions by group (output lens: funds-rate pp; transmission lens: 2-year pp per NS unit)", fontsize=11)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "metric_v3_groups.png"), dpi=130)


if __name__ == "__main__":
    main()
