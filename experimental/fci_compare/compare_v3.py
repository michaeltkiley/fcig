"""
Comparison of the indexes specified in experimental/INDEX_QA.md (approved 29 Oct 2026). Monthly, 1990-2026 (each series on its own available sample).
Units stated, not converted across lenses (answer 35): output lens in pp of funds rate; transmission lens in pp of the 2-year yield per NS unit.
    output lens:        EP_4 (main), EP_4+HP, CP_4, CP_4+HP (macro_model_v3), GI_1yr+HP, GI_3yr+HP, FCI-G 1yr and 3yr (official / 0.4525, replication after 2026-08);
                        the ECB-method index is discussed in the text only (answer 45), not compared here
    transmission lens:  MKT, MKT+Baa (full and diagonal covariance), GS, NFCI, ANFCI (transmission_v3); OFR FSI reported but its conversion failed (event-day response not different from zero)
    other:              SF Fed proxy funds rate, 12-month changes from 2009
Tables: (1) level and 12-month-change correlations among level indexes; (2) FCI-G (both lookbacks) against levels and 12-month changes (answer 15);
(3) proxy funds rate; (4) gap test: static macro EP_4 minus static market MKT, monthly local projections on NS surprises (answer 32; units mixed, stated).
Usage: python experimental/fci_compare/compare_v3.py
Outputs: compare_v3.png
"""
import os, sys
import numpy as np, pandas as pd
import statsmodels.api as sm

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "experimental", "path_fci"))
import path_fci as P
import path_fci_gss_ns as Q


def rd(path):
    d = pd.read_csv(path); d.index = pd.PeriodIndex(d.iloc[:, 0], freq="M"); return d.iloc[:, 1:]


def main():
    mm = rd(os.path.join(ROOT, "experimental", "ms_fci", "macro_model_v3_monthly.csv"))
    tr = rd(os.path.join(HERE, "transmission_v3_monthly.csv"))
    f3 = pd.read_csv(os.path.join(ROOT, "raw", "fed_monthly_3yr.csv"), parse_dates=["date"]).set_index("date").iloc[:, 0]; f3.index = f3.index.to_period("M")
    f1 = pd.read_csv(os.path.join(ROOT, "raw", "fed_monthly_1yr.csv"), parse_dates=["date"]).set_index("date").iloc[:, 0]; f1.index = f1.index.to_period("M")
    rep = pd.read_csv(os.path.join(ROOT, "fcig_replication_monthly.csv")); rep.index = pd.PeriodIndex(rep["month"], freq="M")
    f3 = pd.concat([f3, rep["3yr|FCI-G"].loc[f3.index[-1] + 1:]]); f1 = pd.concat([f1, rep["1yr|FCI-G"].loc[f1.index[-1] + 1:]])
    prox = pd.read_excel(os.path.join(ROOT, "raw", "proxy-funds-rate-data.xlsx"), sheet_name="Weekly", skiprows=1, names=["date", "ffr", "proxy"])
    prox["date"] = pd.to_datetime(prox.date); prox = prox.set_index("date").proxy.resample("ME").last(); prox.index = prox.index.to_period("M")
    S = pd.DataFrame({"EP_4": mm["EP_4"], "EP_4+HP": mm["EP_4+HP"], "CP_4": mm["CP_4"], "CP_4+HP": mm["CP_4+HP"], "GI_1yr+HP": mm["GI_1yr+HP"], "GI_3yr+HP": mm["GI_3yr+HP"],
                      "FCI-G 1yr": f1 / 0.4525, "FCI-G 3yr": f3 / 0.4525,                       "MKT": tr["MKT"], "MKT+Baa": tr["MKT+Baa"], "MKT+Baa diag": tr["MKT+Baa diag"], "GS": tr["GS"], "NFCI": tr["NFCI"], "ANFCI": tr["ANFCI"], "PROXY": prox}).loc["1990-01":"2026-10"]
    lev = ["EP_4", "EP_4+HP", "CP_4", "MKT", "MKT+Baa", "MKT+Baa diag", "GS", "ANFCI", "NFCI"]   # ECB-method index: text only (answer 45)
    pd.set_option("display.width", 220)
    print("sd and latest (output lens: pp funds rate; transmission lens: pp 2-year yield):")
    print(pd.DataFrame({"sd": S.std(), "latest": S.ffill().iloc[-1]}).round(2).T.to_string())
    print("\n(1) correlations, levels (upper) and 12-month changes (lower):")
    C = S[lev].corr(); C2 = S[lev].diff(12).corr()
    T = C.copy()
    for i in range(len(lev)):
        for j in range(len(lev)):
            if i > j: T.iloc[i, j] = C2.iloc[i, j]
    print(T.round(2).to_string())
    print("\n(2) FCI-G against level indexes: corr with level | corr with 12-month change")
    rows = []
    for f in ("FCI-G 1yr", "FCI-G 3yr"):
        for n in lev + ["GI_1yr+HP", "GI_3yr+HP"]:
            a = S[[f, n]].dropna(); b = pd.concat([S[f], S[n].diff(12)], axis=1).dropna()
            rows.append(dict(fcig=f, index=n, level=a.corr().iloc[0, 1], chg12=b.corr().iloc[0, 1] if not n.startswith("GI") else np.nan))
    print(pd.DataFrame(rows).pivot(index="index", columns="fcig", values=["level", "chg12"]).round(2).to_string())
    print("\n(3) SF Fed proxy funds rate, 12-month changes from 2009: correlation")
    print({n: round(float(S[["PROXY", n]].loc["2009-01":].diff(12).corr().iloc[0, 1]), 2) for n in lev + ["FCI-G 1yr"]})
    # (4) gap test
    ev = P.events(P.USMPD)
    d = ev.dropna(subset=Q.FUT + ["UST2Y"] + list(Q.ENDOG.values())).reset_index(drop=True)
    _, ns, _, _ = Q.gss_ns(d)
    s = pd.Series(ns).groupby(pd.PeriodIndex(d.Date, freq="M")).sum().reindex(pd.period_range("1994-02", "2026-09", freq="M")).fillna(0.0)
    gap = S["EP_4"] - S["MKT"]
    print("\n(4) gap test (EP_4 minus MKT; mixed units): y(t+h) - y(t-1) on the month's NS surprise (NS units), HAC")
    for nme, y in (("EP_4", S["EP_4"]), ("MKT", S["MKT"]), ("gap", gap)):
        out = []
        for h in (0, 3, 6, 12, 24):
            dy = (y.shift(-h) - y.shift(1)).reindex(s.index); ok = dy.notna()
            r = sm.OLS(dy[ok], sm.add_constant(s[ok])).fit(cov_type="HAC", cov_kwds={"maxlags": max(h, 1)})
            out.append(f"h={h}: {r.params.iloc[1]:+.2f} ({r.bse.iloc[1]:.2f})")
        print(f"   {nme:5s} " + "  ".join(out))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(3, 1, figsize=(13, 14), sharex=True)
    t = S.index.to_timestamp()
    for n, c in (("EP_4", "black"), ("CP_4", "#1f5fa8")):
        axes[0].plot(t, S[n], color=c, lw=1.4, label={"EP_4": "Macro model, eventual pressure (4 qtr)", "CP_4": "Macro model, current pressure (4 qtr)"}[n])
    axes[0].set_title("Output lens, pp of funds rate", fontsize=11)
    for n, c in (("MKT", "#ff7f0e"), ("GS", "#2ca02c"), ("ANFCI", "#8c564b")):
        axes[1].plot(t, S[n], color=c, lw=1.4, label={"MKT": "Market-based (NS weights)", "GS": "GS replication", "ANFCI": "ANFCI (weekly NS conversion)"}[n])
    axes[1].set_title("Transmission lens, pp of 2-year yield per NS unit", fontsize=11)
    for n, c, lab in (("FCI-G 1yr", "#1f5fa8", "FCI-G 1-year lookback / 0.4525"), ("GI_1yr+HP", "#d62728", "Growth over next year from FRB/US paths (1-year lookback, with house prices)")):
        axes[2].plot(t, S[n], color=c, lw=1.4, label=lab)
    axes[2].plot(t, S["EP_4"].diff(12), color="gray", lw=1.0, ls="--", label="Eventual pressure, 12-month change")
    axes[2].set_title("FCI-G and the growth-over-next-year form, pp of funds rate", fontsize=11)
    for ax in axes:
        ax.axhline(0, color="gray", lw=0.8); ax.grid(alpha=0.25); ax.legend(loc="upper right", fontsize=9, frameon=False)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "compare_v3.png"), dpi=130)


if __name__ == "__main__":
    main()
