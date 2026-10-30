"""
Detailed local-projection results (user, 30 Oct; follows lp_unemp.py, RSTAR_QA S8a). Same specification: u(t+h) on u(t..t-L+1) and x(t..t-L+1), L = 4, HAC (max(h,1)+1 lags),
months touching 2020-01..2021-03 dropped.
 1. Horizon profiles h = 0..24: c_0 (current reading) and sum of c_l (reading held 4 months), 90% bands, for FCI-G (all real, nominal, r* LW, 1974-2026; published and
    nominal replication, 1990-2026) and for the level indexes (real and r* LW EP_4, MKT, GS). FCI-G's claim at h = 12: +0.5.
 2. Coefficient detail at h = 12 for every index: c_0..c_3 (se), sum, Wald p, adjusted R2 gain.
 3. Out-of-sample by subperiod (origins 1995-2007, 2008-2019, 2021-2025): RMSE ratio to the u-only projection, plus the Diebold-Mariano statistic (HAC 12) on the full period.
Usage: python experimental/rstar_case/lp_detail.py      Outputs: lp_detail.log (via tee), lp_detail_fcig.png, lp_detail_levels.png, lp_detail_profiles.csv
"""
import os, sys, warnings
import numpy as np, pandas as pd
import statsmodels.api as sm
warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import var_fcig_horse as H
import lp_unemp as LP

L = 4


def design(u, x, h):
    cols = {"y": u.shift(-h)}
    for l in range(L):
        cols[f"u{l}"] = u.shift(l)
        if x is not None:
            cols[f"x{l}"] = x.shift(l)
    J = pd.DataFrame(cols)
    keep = [not (LP.BAD(t + h) or any(LP.BAD(t - l) for l in range(L))) for t in J.index]
    return J[keep]


def fit(u, x, h, start, end="2026-09"):
    J = design(u, x, h).loc[start:end].dropna()
    X = sm.add_constant(J.drop(columns="y"))
    r = sm.OLS(J.y, X).fit(cov_type="HAC", cov_kwds={"maxlags": max(h, 1) + 1})
    xs = [f"x{l}" for l in range(L)]
    s = np.array([1.0 if c in xs else 0.0 for c in X.columns])
    t = r.t_test(s)
    R = np.array([[1.0 if c == k else 0.0 for c in X.columns] for k in xs])
    r0 = sm.OLS(J.y, sm.add_constant(J[[f"u{l}" for l in range(L)]])).fit()
    return r, float(np.ravel(t.effect)[0]), float(np.ravel(t.sd)[0]), float(r.wald_test(R, scalar=True).pvalue), r.rsquared_adj - r0.rsquared_adj, len(J)


def oos_errors(u, x, start, first="1995-01", last="2025-09", h=12):
    J = design(u, x, h).loc[start:]
    uc = [f"u{l}" for l in range(L)]
    out = []
    for t in pd.period_range(first, last, freq="M"):
        if t not in J.index or J.loc[t].isna().any():
            continue
        tr = J.loc[:t - h].dropna()
        b1 = np.linalg.lstsq(np.c_[np.ones(len(tr)), tr.drop(columns="y").values], tr.y.values, rcond=None)[0]
        b0 = np.linalg.lstsq(np.c_[np.ones(len(tr)), tr[uc].values], tr.y.values, rcond=None)[0]
        row = J.loc[t]
        out.append((t, row.y - b1 @ np.r_[1, row.drop("y").values], row.y - b0 @ np.r_[1, row[uc].values]))
    return pd.DataFrame(out, columns=["t", "e1", "e0"]).set_index("t")


def dm(E):
    d = E.e1 ** 2 - E.e0 ** 2
    r = sm.OLS(d.values, np.ones(len(d))).fit(cov_type="HAC", cov_kwds={"maxlags": 12})
    return float(r.tvalues[0])


def main():
    u = H.MO.V.macro_data(False)["unemployment gap"]
    rd, RC = H.rd, H.RC
    fr, mr, mk, gs, nf, rs = (rd(os.path.join(RC, "fcig_real_monthly.csv")), rd(os.path.join(RC, "macro_real_monthly.csv")), rd(os.path.join(RC, "market_real_monthly.csv")),
                              rd(os.path.join(RC, "gs_real_monthly.csv")), rd(os.path.join(RC, "nfci_real_monthly.csv")), rd(os.path.join(HERE, "rstar_indexes_monthly.csv")))
    pub = pd.read_csv(os.path.join(H.ROOT, "raw", "fed_monthly_1yr.csv"), parse_dates=["date"]).set_index("date").iloc[:, 0]; pub.index = pub.index.to_period("M")
    F = H.MO.LL.financial()[H.MO.VARS]
    pd.set_option("display.width", 230)
    # 1. profiles
    PROF = {"FCI-G all real (1974-)": (fr["1yr all real"], "1974-03"), "FCI-G nominal repl. (1974-)": (fr["1yr nominal"], "1974-03"), "FCI-G r* LW (1974-)": (rs["FCI-G 1yr LW"], "1974-03"),
            "FCI-G published (1990-)": (pub, "1990-01"), "FCI-G nominal repl. (1990-)": (fr["1yr nominal"], "1990-01"),
            "real EP_4 (1974-)": (mr.EP_4, "1974-03"), "real MKT (1974-)": (mk.MKT_real, "1974-03"), "real GS (1974-)": (gs.GS_real, "1974-03"),
            "r* LW EP_4 (1974-)": (rs["EP_4 LW"], "1974-03"), "r* LW MKT (1974-)": (rs["MKT LW"], "1974-03"), "r* LW GS (1974-)": (rs["GS LW"], "1974-03")}
    hs = list(range(0, 25))
    P = {}
    print("1. HORIZON PROFILES (L = 4): c0 [current reading] and sum c [reading held 4 months], se in parentheses")
    for nm, (x, st) in PROF.items():
        rows = []
        for h in hs:
            r, sc, ssd, wp, dr2, n = fit(u, x, h, st)
            rows.append({"h": h, "c0": r.params["x0"], "se c0": r.bse["x0"], "sum": sc, "se sum": ssd, "Wald p": wp})
        T = pd.DataFrame(rows).set_index("h"); P[nm] = T
        print(f"\n   {nm}:  " + "  ".join(f"h{h}: c0 {T.c0[h]:+.2f} ({T['se c0'][h]:.2f}) sum {T['sum'][h]:+.2f} ({T['se sum'][h]:.2f})" for h in (3, 6, 12, 18, 24)))
    pd.concat(P, axis=1).to_csv(os.path.join(HERE, "lp_detail_profiles.csv"), float_format="%.4f")
    # 2. coefficient detail at h = 12
    IDX = {"real EP_4 (FRB/US)": mr.EP_4, "real MKT": mk.MKT_real, "real GS": gs.GS_real, "real FCI-G 1yr": fr["1yr all real"],
           "r* LW EP_4": rs["EP_4 LW"], "r* LW MKT": rs["MKT LW"], "r* LW GS": rs["GS LW"], "r* LW FCI-G 1yr": rs["FCI-G 1yr LW"],
           "r* Ki EP_4": rs["EP_4 Ki"], "r* Ki MKT": rs["MKT Ki"], "r* Ki GS": rs["GS Ki"], "r* Ki FCI-G 1yr": rs["FCI-G 1yr Ki"],
           "nominal MKT (long)": pd.Series((F - F.mean()).values @ H.MO.W, index=F.index)}
    for st, extra in (("1974-03", {}), ("1990-01", {"ANFCI": nf.ANFCI, "FCI-G published": pub})):
        ids = dict(IDX, **extra)
        rows = []
        for nm, x in ids.items():
            r, sc, ssd, wp, dr2, n = fit(u, x, 12, st)
            E = oos_errors(u, x, st)
            row = {"index": nm, **{f"c{l}": f"{r.params[f'x{l}']:+.3f} ({r.bse[f'x{l}']:.3f})" for l in range(L)}, "sum": f"{sc:+.3f} ({ssd:.3f})", "Wald p": round(wp, 4),
                   "dR2": round(dr2, 3), "sd x": round(float(x.loc[st:].std()), 2), "sum x sd": round(sc * float(x.loc[st:].std()), 3), "n": n}
            for lab, a, b in (("OOS 95-07", "1995-01", "2007-12"), ("OOS 08-19", "2008-01", "2019-12"), ("OOS 21-25", "2021-01", "2025-09"), ("OOS all", "1995-01", "2025-09")):
                e = E.loc[a:b]
                row[lab] = round(float(np.sqrt((e.e1 ** 2).mean() / (e.e0 ** 2).mean())), 3) if len(e) else np.nan
            row["DM t"] = round(dm(E), 2)
            rows.append(row)
        T = pd.DataFrame(rows).set_index("index")
        print(f"\n2-3. h = 12, sample {st}..2026-09 (targets to 2026-09). 'sum x sd': effect of a 1-sd reading held 4 months (u pp). DM t < 0: index forecasts better.")
        print(T.to_string())
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    for fn, names, title in (("lp_detail_fcig.png", ["FCI-G all real (1974-)", "FCI-G r* LW (1974-)", "FCI-G published (1990-)"], "FCI-G: unemployment-gap response to a reading of +1 held 4 months (sum of coefficients)"),
                             ("lp_detail_levels.png", ["real EP_4 (1974-)", "real MKT (1974-)", "real GS (1974-)", "r* LW EP_4 (1974-)", "r* LW MKT (1974-)", "r* LW GS (1974-)"],
                              "Level indexes: response to a 1-unit reading held 4 months (sum of coefficients)")):
        fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
        for nm, col in zip(names, ["black", "#d62728", "#1f5fa8", "#2ca02c", "#ff7f0e", "#9467bd"]):
            T = P[nm]
            for ax, c, sc in ((axes[0], "sum", "se sum"), (axes[1], "c0", "se c0")):
                ax.plot(hs, T[c], color=col, lw=1.4, label=nm)
                ax.fill_between(hs, T[c] - 1.645 * T[sc], T[c] + 1.645 * T[sc], color=col, alpha=0.10)
        if "FCI-G" in names[0]:
            axes[0].plot([0, 12], [0, 0.5], color="gray", ls="--", lw=1, label="FCI-G claim (0.5 by month 12)")
        axes[0].set_title("Reading held 4 months (sum of c)", fontsize=10); axes[1].set_title("New rise in the current reading (c0)", fontsize=10)
        for ax in axes:
            ax.axhline(0, color="gray", lw=0.8); ax.grid(alpha=0.25); ax.set_xlabel("months ahead"); ax.legend(fontsize=8, frameon=False)
        axes[0].set_ylabel("unemployment gap, pp")
        fig.suptitle(title, fontsize=11); fig.tight_layout(); fig.savefig(os.path.join(HERE, fn), dpi=130)


if __name__ == "__main__":
    main()
