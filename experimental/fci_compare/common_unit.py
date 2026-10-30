"""
EXPERIMENTAL first-pass comparison of financial conditions indexes in funds-rate equivalents (metric fixed in METRIC.md before computing).

Indexes (monthly, end-of-month values; each demeaned over the common window, higher = tighter):
  FCI-G   the Fed's official FCI-G, 3-year-lookback baseline (raw/fed_monthly_3yr.csv; pp of next-year GDP growth, positive = headwind); 1-year lookback as a check
  GS      the GS-style replication (fcig_gs_daily.csv, index points)
  MKT     market-based index: intraday event-window responses of the 10-year, S&P 500 and dollar index to a PARALLEL policy surprise (MP1 and ED4 both up 1 pp),
          one-factor weights with the full error covariance, applied to daily levels (nominal 10-year, 100 ln CAPE, 100 ln real dollar)
  MS-FRB  MS-style index with FRB/US q4 weights (experimental/ms_fci; native funds-rate equivalents, includes BBB and oil)
Conversions to funds-rate units:
  output       FCI-G divided by the FRB/US GDP effect of a 1 pp full-transmission hike at 4 quarters (-0.4525%); MS-FRB native; 8 and 12 quarters printed as sensitivity
  transmission every index divided by its response (h = 0, the same month; h = 3 printed as a sensitivity, see the deviation log in METRIC.md) to a parallel surprise, by monthly local
               projection on USMPD surprises summed by month: y(t+h) - y(t-1) = a + b1 MP1_t + b4 ED4_t + e, parallel response = b1 + b4 (HAC errors)
Set A (mixed): FCI-G by output, MS-FRB native, GS by transmission (h = 0), MKT native.  Set B: every index by the h = 0 transmission response.
Usage: python experimental/fci_compare/common_unit.py   (needs the Python/USMPD set-up of experimental/path_fci)
Outputs: common_unit_monthly.csv, common_unit_groups.csv, common_unit_levels.png
"""
import os, sys
import numpy as np, pandas as pd
import statsmodels.api as sm

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "experimental", "path_fci"))
import path_fci as P

END = "2026-10"         # official FCI-G ends 2026-08; the replication fills the later months
START = "1990-01"
GROUP = {"FFR": "rates", "10Yr Treasury": "rates", "Mortgage Rate": "rates", "BBB": "rates", "Stock Market": "equities", "House Prices": "other", "Dollar": "dollar"}


def monthly_end(s):
    s = s.copy(); s.index = pd.PeriodIndex(s.index, freq="M")
    return s[~s.index.duplicated(keep="last")]


def official(path):
    d = pd.read_csv(os.path.join(ROOT, "raw", path), parse_dates=["date"]).set_index("date")
    d.index = d.index.to_period("M")
    return d


def main():
    ev = P.events(P.USMPD)
    P.L.REAL10 = False; P.L.RSTAR = False
    X, G = P.L.build()
    # ---- market index with parallel weights
    d = ev.dropna(subset=["UST10Y", "SP500", "DXY", "MP1", "ED4"]).reset_index(drop=True)
    cols = {"10-yr": "UST10Y", "Equities (ln CAPE)": "SP500", "Dollar (ln real)": "DXY"}
    Z = sm.add_constant(d[["MP1", "ED4"]])
    res = [sm.OLS(d[c], Z).fit() for c in cols.values()]
    b = np.array([r.params["MP1"] + r.params["ED4"] for r in res])
    Psi = np.cov(np.array([r.resid for r in res]).T if False else np.array([r.resid.values for r in res]), ddof=3)
    w = np.linalg.solve(Psi, b); w = w / (b @ w)
    wser = pd.Series(w, index=list(cols))
    print(f"{len(d)} events. Intraday responses to a parallel 1 pp surprise: " + ", ".join(f"{n} {b[i]:+.3f}" for i, n in enumerate(cols)))
    print("market-index weights (pp of parallel unit per unit): " + ", ".join(f"{n} {w[i]:+.4f}" for i, n in enumerate(cols)))
    comp_mkt = pd.DataFrame({n: wser[n] * P.VARS[n][1] * (X[P.VARS[n][0]] - X[P.VARS[n][0]].mean()) for n in cols})
    mkt = comp_mkt.sum(axis=1)
    # ---- MS-style FRB/US index
    sens = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "frbus_sensitivities.csv"), index_col=0)
    ms = P.L.level(X, sens["ffr_eq_q4"].to_dict(), float(sens.loc["req", "unit_size"]))
    # ---- monthly series and components
    f3, f1 = official("fed_monthly_3yr.csv"), official("fed_monthly_1yr.csv")
    rep = pd.read_csv(os.path.join(ROOT, "fcig_replication_monthly.csv")); rep["month"] = pd.PeriodIndex(rep["month"], freq="M"); rep = rep.set_index("month")
    ov = f3.iloc[:, 0].index.intersection(rep.index)
    print(f"official vs replication FCI-G (3yr), {ov[0]}..{ov[-1]}: corr {np.corrcoef(f3.iloc[:, 0].loc[ov], rep['3yr|FCI-G'].loc[ov])[0, 1]:.3f}, mean abs diff {float((f3.iloc[:, 0].loc[ov] - rep['3yr|FCI-G'].loc[ov]).abs().mean()):.3f} pp")
    ext = lambda off, col: pd.concat([off, rep[col].loc[off.index[-1] + 1:]])
    S = {"FCI-G (3yr)": ext(f3.iloc[:, 0], "3yr|FCI-G"), "FCI-G (1yr)": ext(f1.iloc[:, 0], "1yr|FCI-G"), "GS": monthly_end(G.fci), "MKT": monthly_end(mkt), "MS-FRB": monthly_end(ms.Total)}
    S = pd.DataFrame(S).loc[START:END]
    comps = {}
    rc = rep[[c for c in rep.columns if c.startswith("3yr|") and not c.endswith("FCI-G") and "next year" not in c and "|fed" not in c]]
    rc.columns = [GROUP[c.split("|")[1]] for c in rc.columns]
    comps["FCI-G (3yr)"] = rc.T.groupby(level=0).sum().T
    gsc = G[["c_ffr", "c_y10", "c_bbb", "c_cape", "c_usd"]].rename(columns={"c_ffr": "rates", "c_y10": "rates", "c_bbb": "rates", "c_cape": "equities", "c_usd": "dollar"})
    comps["GS"] = monthly_end(gsc.T.groupby(level=0).sum().T)
    comps["MKT"] = monthly_end(pd.DataFrame({"rates": comp_mkt["10-yr"], "equities": comp_mkt["Equities (ln CAPE)"], "dollar": comp_mkt["Dollar (ln real)"]}))
    mc = pd.DataFrame({"rates": ms["10-yr"] + ms["BBB spread"], "equities": ms["Equities"], "dollar": ms["Dollar"], "other": ms["Oil"]})
    comps["MS-FRB"] = monthly_end(mc)
    # ---- monthly parallel surprises and LP conversion
    e2 = ev.copy(); e2["m"] = pd.PeriodIndex(e2.Date, freq="M")
    sm_ = e2.groupby("m")[["MP1", "ED4"]].sum().reindex(S.index).fillna(0.0)

    def lp(y, h):
        dy = (y.shift(-h) - y.shift(1)).reindex(S.index)
        ok = dy.notna()
        r = sm.OLS(dy[ok], sm.add_constant(sm_[ok])).fit(cov_type="HAC", cov_kwds={"maxlags": 6})
        v = r.cov_params().loc[["MP1", "ED4"], ["MP1", "ED4"]].values
        return r.params["MP1"] + r.params["ED4"], float(np.sqrt(v.sum()))
    k = {}
    print("\nResponse (index units) to a parallel +1 pp surprise, monthly LP (se):")
    for h in (0, 3):
        for n in S:
            k[(n, h)] = lp(S[n], h)
        print(f"  h={h}: " + "; ".join(f"{n} {k[(n, h)][0]:+.2f} ({k[(n, h)][1]:.2f})" for n in S))
    gdp = {q: abs(float(sens.loc["rff", f"gdp_{q}"])) for q in ("q4", "q8", "q12")}
    print(f"FRB/US GDP effect of a 1 pp full-transmission hike: q4 {gdp['q4']:.3f}, q8 {gdp['q8']:.3f}, q12 {gdp['q12']:.3f}")
    # ---- conversions
    mean = S.mean()
    dm = S - mean
    A = pd.DataFrame({"FCI-G": dm["FCI-G (3yr)"] / gdp["q4"], "GS": dm["GS"] / k[("GS", 0)][0], "MKT": dm["MKT"], "MS-FRB": dm["MS-FRB"]})
    B = pd.DataFrame({n: dm[n] / k[(n, 0)][0] for n in ("FCI-G (3yr)", "GS", "MKT", "MS-FRB")}).rename(columns={"FCI-G (3yr)": "FCI-G"})
    out = {"A": A, "B": B}
    allm = pd.concat({f"{s}|{c}": v[c] for s, v in out.items() for c in v}, axis=1)
    allm.to_csv(os.path.join(HERE, "common_unit_monthly.csv"), float_format="%.4f", index_label="month")
    for sname, Dd in out.items():
        print(f"\n===== Set {sname} ({'FCI-G by output yardstick, MS-FRB native, GS and MKT by transmission' if sname == 'A' else 'every index by the h=0 transmission response'}) =====")
        print("sd of level (pp):", Dd.std().round(2).to_dict(), "| latest:", Dd.iloc[-1].round(2).to_dict())
        names = list(Dd)
        rows = []
        for a in names:
            for c in names:
                if a >= c: continue
                ch = Dd[[a, c]].diff(12).dropna()
                sl = np.polyfit(Dd[a], Dd[c], 1)[0]; slc = np.polyfit(ch[a], ch[c], 1)[0]
                rows.append(dict(pair=f"{a} / {c}", corr_lev=Dd[a].corr(Dd[c]), slope_lev=sl, corr_12m=ch[a].corr(ch[c]), slope_12m=slc,
                                 sign_agree=float((np.sign(ch[a]) == np.sign(ch[c])).mean())))
        print(pd.DataFrame(rows).round(2).to_string(index=False))
        med = Dd.median(axis=1)
        print("mean abs gap to the cross-index median (pp):", (Dd.sub(med, axis=0)).abs().mean().round(2).to_dict())
        rng = Dd.max(axis=1) - Dd.min(axis=1)
        print(f"cross-index range: mean {rng.mean():.2f}, max {rng.max():.2f} ({rng.idxmax()}), latest {rng.iloc[-1]:.2f}")
        # episodes: non-overlapping 6-month windows
        roll = rng.rolling(6).mean().dropna()
        for lab, asc in (("closest alignment", True), ("biggest differences", False)):
            order = roll.sort_values(ascending=asc)
            chosen = []
            for end, val in order.items():
                if all(abs((end - c0).n) >= 6 for c0, _ in chosen):
                    chosen.append((end, val))
                if len(chosen) == 4: break
            print(f"  {lab}: " + "; ".join(f"{(e - 5)}..{e} (mean range {v:.2f})" for e, v in sorted(chosen)))
            for e, v in sorted(chosen):
                m = Dd.loc[e - 5:e].mean()
                print(f"      {(e - 5)}..{e}: " + ", ".join(f"{n} {m[n]:+.2f}" for n in names))
    # ---- groups
    print("\n===== By group, Set A conversion (pp of funds rate; demeaned over the common window) =====")
    scale = {"FCI-G": 1 / gdp["q4"], "GS": 1 / k[("GS", 0)][0], "MKT": 1.0, "MS-FRB": 1.0}
    key = {"FCI-G": "FCI-G (3yr)", "GS": "GS", "MKT": "MKT", "MS-FRB": "MS-FRB"}
    rows = []
    for n in ("FCI-G", "GS", "MKT", "MS-FRB"):
        c = comps[key[n]].reindex(S.index)
        if n == "MKT" or n == "MS-FRB": pass
        c = (c - c.mean()) * scale[n]
        c = c.reindex(columns=["rates", "equities", "dollar", "other"]).fillna(0.0)
        for lab, d0 in (("latest", None), ("chg since 2026-02", "2026-02"), ("chg since 2026-08", "2026-08")):
            v = c.iloc[-1] if d0 is None else c.iloc[-1] - c.loc[d0]
            rows.append(dict(index=n, window=lab, total=v.sum(), **v.round(2).to_dict()))
    G2 = pd.DataFrame(rows)
    G2.to_csv(os.path.join(HERE, "common_unit_groups.csv"), float_format="%.3f", index=False)
    print(G2.round(2).to_string(index=False))
    print("(months: latest =", S.index[-1], "; FCI-G groups use the repository replication)")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(13, 6.5))
    colr = {"FCI-G": "#1f5fa8", "GS": "#2ca02c", "MKT": "#ff7f0e", "MS-FRB": "#d62728"}
    for n in A:
        ax.plot(A.index.to_timestamp(), A[n], color=colr[n], lw=1.6, label=f"{n}")
    ax.axhline(0, color="gray", lw=0.8); ax.grid(alpha=0.25)
    ax.set_ylabel("pp of funds rate, tighter above zero (vs 1990-2026 average)", fontsize=11)
    ax.set_title("Indexes in funds-rate equivalents (set A: FCI-G by the FRB/US yardstick; GS and market-based by response to a parallel surprise)", fontsize=11)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=4, fontsize=10, frameon=False)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "common_unit_levels.png"), dpi=130)


if __name__ == "__main__":
    main()
