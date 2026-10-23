"""
r*-adjusted versions of the macro-model (with house prices), market-based (NS) and GS indexes using three one-sided r* estimates (rstar_series.csv, quarterly):
  Kiley (own Kalman-filter model, filtered/one-sided; experimental/ms_fci/kiley_rstar.csv),
  Laubach-Williams (NY Fed, "One-Sided Estimates" columns of Laubach_Williams_current_estimates.xlsx, estimates of 26 Aug 2026, through 2026Q2),
  Richmond Fed (Lubik-Matthes natural rate, median; model-based five-year-ahead real-rate forecast; the page does not say whether history is revised, so this is not verified as strictly one-sided).
Real-rate gap: the policy rate and the 10-year enter as (real rate - r*), real = nominal less Cleveland Fed 10-year expected inflation; spreads, equities, dollar and house prices unchanged; weights unchanged.
r* is stamped mid-quarter, interpolated daily and held at its last value after 2026Q2. Every index is demeaned over 1990-2026. GS: real GS less 0.495 r* (0.044 + 0.451 weights on the policy rate and 10-year),
converted at 0.945 pp per point; market-based x 0.983.
Usage: python experimental/fci_compare/rstar_sets.py     Outputs: rstar_sets_daily.csv, rstar_sets.png
"""
import os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "experimental", "path_fci"))
import path_fci as P
import path_fci_gss_ns as Q
import fcig_replicate as R

SRC = {"Kiley": "Kiley_onesided", "Laubach-Williams": "LW_onesided", "Richmond": "Richmond_median"}


def daily_rstar(q, idx):
    s = q.dropna().copy()
    s.index = pd.PeriodIndex(s.index, freq="Q").to_timestamp() + pd.Timedelta(days=45)
    return s.reindex(s.index.union(idx)).interpolate("time").ffill().bfill().reindex(idx)


def main():
    ev = P.events(P.USMPD)
    d = ev.dropna(subset=Q.FUT + ["UST2Y"] + list(Q.ENDOG.values())).reset_index(drop=True)
    gss, ns, _, _ = Q.gss_ns(d)
    wn = pd.Series(Q.estimate(d, ns, True)[0], index=list(Q.ENDOG))
    P.L.REAL10 = True; P.L.RSTAR = False
    X, G = P.L.build()
    idx = X.index
    Rq = pd.read_csv(os.path.join(HERE, "rstar_series.csv"), index_col=0); Rq.index = pd.PeriodIndex(Rq.index, freq="Q")
    rs = {k: daily_rstar(Rq[c], idx) for k, c in SRC.items()}
    rs["none (real rates)"] = pd.Series(0.0, index=idx)
    base = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "frbus_sensitivities.csv"), index_col=0)["ffr_eq_q4"]
    ext = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "frbus_sensitivities_ext.csv"), index_col=0)["ffr_eq_q4"]
    mort = R.fred("MORTGAGE30US").reindex(idx, method="ffill"); spread = mort - G.x_y10.reindex(idx)
    hp = np.log(R.splice_level(R.zillow(), R.fred("CSUSHPISA"))); oer = np.log(P.L.get("CUSR0000SEHC"))
    hp = hp - oer.reindex(hp.index.union(oer.index)).sort_index().ffill().reindex(hp.index)
    hp = hp.reindex(idx.union(hp.index)).sort_index().ffill().reindex(idx) * 100
    gs_real = G.fci.reindex(idx) - (0.044 + 0.451) * X.einf + 0.06 * (100 * X.lnrusd - 100 * np.log(G.x_usd.reindex(idx)))
    out = {}
    for name, r in rs.items():
        policy = X.ffr - X.einf - r
        tenyr = X.y10 - r                                   # X.y10 is already the real 10-year
        macro = (ext["rshort_direct"] * policy + base["rg10"] * tenyr + ext["rme"] * spread + base["rbbbp"] * X.bbb - base["req"] * 100 * X.lncape
                 + base["fpxr"] * 100 * X.lnrusd + ext["phouse"] * hp)
        mkt = (wn["10-yr"] * tenyr + wn["Equities (ln CAPE)"] * 100 * X.lncape + wn["Dollar (ln real)"] * 100 * X.lnrusd) * 0.983
        gs = (gs_real - (0.044 + 0.451) * r) * 0.945
        for fam, s in (("macro", macro), ("market", mkt), ("GS", gs)):
            out[(fam, name)] = s - s.mean()
    D = pd.concat(out, axis=1).dropna()
    D.columns = [f"{a} | {b}" for a, b in D.columns]
    D.to_csv(os.path.join(HERE, "rstar_sets_daily.csv"), float_format="%.4f", index_label="date")
    M = D.resample("ME").last()
    pd.set_option("display.width", 220)
    print("r* series (quarterly, 1990-2026): mean / sd / min / max / latest")
    for k, c in SRC.items():
        s = Rq[c].loc["1990Q1":]
        print(f"  {k:17s} {s.mean():5.2f} {s.std():5.2f} {s.min():6.2f} {s.max():5.2f}  latest {s.iloc[-1]:.2f}")
    print("  correlation of the three r* series:", Rq[list(SRC.values())].loc["1990Q1":].corr().round(2).values[np.triu_indices(3, 1)], "(K/LW, K/R, LW/R)")
    names = list(SRC) + ["none (real rates)"]
    for fam in ("macro", "market", "GS"):
        sub = M[[f"{fam} | {n}" for n in names]]; sub.columns = names
        print(f"\n=== {fam}: r*-gap versions ===")
        print("sd of level:", sub.std().round(2).to_dict(), "| latest:", sub.iloc[-1].round(2).to_dict())
        for lab, d0 in (("since 27 Feb 2026", "2026-02-27"), ("since 27 Aug 2026", "2026-08-27")):
            print(f"  change {lab}:", {n: round(float(D[f"{fam} | {n}"].iloc[-1] - D[f'{fam} | {n}'].loc[:d0].iloc[-1]), 2) for n in names})
        print("  monthly corr of levels:\n" + sub.corr().round(2).to_string().replace("\n", "\n  "))
        print("  corr of 12-month changes:\n" + sub.diff(12).corr().round(2).to_string().replace("\n", "\n  "))
        dd = sub.sub(sub["none (real rates)"], axis=0)
        print("  version minus no-r* (pp): mean abs", dd[list(SRC)].abs().mean().round(2).to_dict(), "| max abs", dd[list(SRC)].abs().max().round(2).to_dict())
        sp = sub[list(SRC)]; rng = sp.max(axis=1) - sp.min(axis=1)
        print(f"  range across the three r* versions: mean {rng.mean():.2f}, max {rng.max():.2f} ({rng.idxmax()}), latest {rng.iloc[-1]:.2f}")
    # FCI-G link: macro r*-gap 12-month change vs FCI-G (1-year lookback) level
    f1 = pd.read_csv(os.path.join(ROOT, "raw", "fed_monthly_1yr.csv"), parse_dates=["date"]).set_index("date").iloc[:, 0]; f1.index = f1.index.to_period("M")
    rep = pd.read_csv(os.path.join(ROOT, "fcig_replication_monthly.csv")); rep["month"] = pd.PeriodIndex(rep["month"], freq="M"); rep = rep.set_index("month")["1yr|FCI-G"]
    fcig = pd.concat([f1, rep.loc[f1.index[-1] + 1:]])
    Mm = M.copy(); Mm.index = Mm.index.to_period("M")
    print("\nCorrelation of the macro-model 12-month change with the 1-year FCI-G level:",
          {n: round(float(pd.concat({'m': Mm[f'macro | {n}'].diff(12), 'f': fcig}, axis=1).dropna().corr().iloc[0, 1]), 2) for n in names})
    print("Level correlation of each macro/market/GS r*-gap version with FCI-G (1yr):",
          {f"{fam}|{n}": round(float(pd.concat({'m': Mm[f'{fam} | {n}'], 'f': fcig}, axis=1).dropna().corr().iloc[0, 1]), 2) for fam in ("macro", "market", "GS") for n in ("Kiley", "Laubach-Williams", "Richmond")})
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 1, figsize=(13, 9))
    col = {"Kiley": "#1f5fa8", "Laubach-Williams": "#2ca02c", "Richmond": "#d62728"}
    for k, c in SRC.items():
        s = Rq[c].loc["1990Q1":]; ax[0].plot(s.index.to_timestamp(), s, color=col[k], lw=1.7, label=k)
    ax[0].set_title("One-sided r* estimates (%)", fontsize=12); ax[0].grid(alpha=0.25); ax[0].legend(fontsize=10); ax[0].axhline(0, color="gray", lw=0.8)
    for k in SRC:
        s = M[f"macro | {k}"]; ax[1].plot(s.index, s, color=col[k], lw=1.6, label=f"macro-model index (with house prices), real rates less {k} r*")
    s = M["macro | none (real rates)"]; ax[1].plot(s.index, s, color="black", lw=1.0, ls="--", label="macro-model index, real rates (no r* adjustment)")
    ax[1].axhline(0, color="gray", lw=0.8); ax[1].grid(alpha=0.25); ax[1].legend(fontsize=9, loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=1, frameon=False)
    ax[1].set_ylabel("pp of funds rate, tighter above zero (vs 1990-2026 average)"); ax[1].set_title("Macro-model levels index with r*-gap rates: three r* estimates", fontsize=12)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "rstar_sets.png"), dpi=130)


if __name__ == "__main__":
    main()
