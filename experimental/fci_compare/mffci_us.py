"""
APPROXIMATE US version of the ECB Macro-Finance FCI (Bletzinger, Martorana and Mistak; ECB WP 3193 and Economic Bulletin 6/2026 box), put in funds-rate units (DYNAMICS_PLAN.md, C2).
NOT the ECB series: weights are read from the box text (normalized so their squares sum to 1); CAPE and dollar weights are not reported, so two variants bracket them:
    reported: funds rate 0.63; real 2-year forward 1 year ahead 0.45; real 5-year 0.45; 10-year 0.40; mortgage spread (30-year mortgage less 30-year Treasury) 0.11; corporate spread 0.11
    variant A  CAPE -0.053, dollar 0.105   (euro-area CAPE/NEER weights -0.038/0.075 scaled up to fill the remaining sum of squares, 0.014)
    variant B  CAPE -0.100, dollar 0.060   (dollar smaller, as the box says the dollar has the smallest positive weight)
Data (monthly, end of month, our sources): EFFR (DFF); 10-year (DGS10); real 1y1y = (2 DGS2 - DGS1) - (2 EXPINF2YR - EXPINF1YR); real 5-year = DGS5 - EXPINF5YR (Cleveland Fed expected inflation);
mortgage spread = MORTGAGE30US - DGS30 (DGS20 where DGS30 is missing, 2002-06); corporate spread: the project's BBB spread as a proxy for the A-rated spread (FRED carries ICE A OAS only from 2023);
CAPE and the broad nominal dollar (DTWEXB spliced to DTWEXBGS) as % deviations from their 1999-2025 means (the ECB transformation for the euro area); rates and spreads in percent.
Funds-rate units, two conversions:
    parallel   divide by the index response to a parallel 1 pp move in all nominal and real rates (sum of the rate weights) - the "policy-rate scale" read literally
    transmission  divide by the same-month response to a parallel surprise (MP1 + ED4), as for ANFCI/NFCI (METRIC.md set B)
Inputs not in git (raw/ is ignored): DGS1, DGS2, DGS5, DGS10, DGS20, DGS30, EXPINF1YR, EXPINF2YR, EXPINF5YR, MORTGAGE30US, DTWEXB, DTWEXBGS, DFF (FRED).
Usage: python experimental/fci_compare/mffci_us.py
Outputs: mffci_us_monthly.csv, mffci_us.png
"""
import os, sys
import numpy as np, pandas as pd
import statsmodels.api as sm

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common_unit_v2 as C

RATES = {"funds rate": 0.63, "real 1y1y": 0.45, "real 5y": 0.45, "10-year": 0.40, "mortgage spread": 0.11, "corporate spread": 0.11}
VAR = {"A": {"CAPE": -0.053, "dollar": 0.105}, "B": {"CAPE": -0.100, "dollar": 0.060}}


def m(name):
    s = C.raw_series(f"{name}.csv"); s = s.resample("ME").last(); s.index = s.index.to_period("M"); return s


def main():
    S, conv, comp, mk, X, ev = C.build()
    e1, e2, e5 = m("EXPINF1YR"), m("EXPINF2YR"), m("EXPINF5YR")
    d30 = m("DGS30").combine_first(m("DGS20"))
    usd_old, usd_new = m("DTWEXB"), m("DTWEXBGS")
    k = (usd_new.loc["2006-01":"2006-12"] / usd_old.loc["2006-01":"2006-12"]).mean()
    usd = pd.concat([usd_old.loc[:"2005-12"] * k, usd_new.loc["2006-01":]])
    lncape = C.me(X.lncape)
    bbb = C.me(X.bbb)
    Z = pd.DataFrame({"funds rate": m("DFF"), "real 1y1y": (2 * m("DGS2") - m("DGS1")) - (2 * e2 - e1), "real 5y": m("DGS5") - e5, "10-year": m("DGS10"),
                      "mortgage spread": m("MORTGAGE30US") - d30, "corporate spread": bbb, "CAPE": 100 * lncape, "dollar": 100 * np.log(usd)}).loc["1999-01":"2026-10"].dropna()
    mean = Z.loc[:"2025-12"].mean()
    Zc = Z.copy()
    for c in ("CAPE", "dollar"):
        Zc[c] = Z[c] - mean[c]                               # % deviation from the 1999-2025 mean
    out = {}
    e2_ = ev.copy(); e2_["m"] = pd.PeriodIndex(e2_.Date, freq="M")
    sur = e2_.groupby("m")[["MP1", "ED4"]].sum().reindex(Zc.index).fillna(0.0)
    for v, extra in VAR.items():
        a = pd.Series({**RATES, **extra})
        print(f"variant {v}: sum of squared weights {float((a ** 2).sum()):.3f}")
        F = Zc[a.index] @ a
        par = sum(RATES[c] for c in ("funds rate", "real 1y1y", "real 5y", "10-year"))
        dy = F.diff(); ok = dy.notna()
        r = sm.OLS(dy[ok], sm.add_constant(sur[ok])).fit(cov_type="HAC", cov_kwds={"maxlags": 6})
        tr = r.params["MP1"] + r.params["ED4"]; trse = float(np.sqrt(r.cov_params().loc[["MP1", "ED4"], ["MP1", "ED4"]].values.sum()))
        print(f"   index units per 1 pp: parallel move in all rates {par:.2f}; same-month response to a parallel surprise {tr:+.2f} ({trse:.2f})")
        out[f"MF-FCI {v} (level, percent)"] = F
        out[f"MF-FCI {v} parallel"] = (F - F.mean()) / par
        out[f"MF-FCI {v} transmission"] = (F - F.mean()) / tr
        contrib = (Zc[a.index] * a)
        print("   latest contributions:", contrib.iloc[-1].round(2).to_dict(), "total", round(float(F.iloc[-1]), 2))
    O = pd.DataFrame(out)
    O.to_csv(os.path.join(HERE, "mffci_us_monthly.csv"), float_format="%.4f", index_label="month")
    J = pd.concat([O[["MF-FCI A parallel", "MF-FCI B parallel"]], S[["MACRO", "MACRO+HP", "MKT", "GS", "ANFCI", "FCI-G (1yr)", "FCI-G (3yr)"]]], axis=1).loc["1999-01":].dropna()
    for c in J:
        J[c] = J[c] - J[c].mean()
    print(f"\nsample {J.index[0]}..{J.index[-1]}; sd (pp):", J.std().round(2).to_dict())
    print("latest (pp of funds rate, demeaned over the common sample):", J.iloc[-1].round(2).to_dict())
    rows = []
    for a_ in ("MF-FCI A parallel", "MF-FCI B parallel"):
        for c in ("MACRO", "MACRO+HP", "MKT", "GS", "ANFCI"):
            ch = J[[a_, c]].diff(12).dropna()
            rows.append(dict(pair=f"{a_} / {c}", corr_lev=J[a_].corr(J[c]), corr_12m=ch.corr().iloc[0, 1], slope_lev=np.polyfit(J[a_], J[c], 1)[0]))
        for f, h in (("FCI-G (1yr)", 12), ("FCI-G (3yr)", 24)):
            jj = pd.concat([J[f], J[a_].diff(h)], axis=1).dropna()
            rows.append(dict(pair=f"{f} / {a_} {h}m change", corr_lev=jj.corr().iloc[0, 1], corr_12m=np.nan, slope_lev=np.nan))
    print(pd.DataFrame(rows).round(2).to_string(index=False))
    # policy surprise check: same-month response of the parallel-unit index and of its gap to MKT, NS surprises
    w, _ = C.ns_weights()
    import path_fci_gss_ns as Q
    d = ev.dropna(subset=Q.FUT + ["UST2Y"] + list(Q.ENDOG.values())).reset_index(drop=True)
    _, ns, _, _ = Q.gss_ns(d)
    s = pd.Series(ns * 0.98).groupby(pd.PeriodIndex(d.Date, freq="M")).sum().reindex(J.index).fillna(0.0)
    for c in ("MF-FCI A parallel", "MKT", "MACRO"):
        for lab, y in ((c, J[c]), (f"{c} - MKT", J[c] - J["MKT"])):
            if lab == "MKT - MKT": continue
            dy = y.diff(); ok = dy.notna()
            r = sm.OLS(dy[ok], sm.add_constant(s[ok])).fit(cov_type="HAC", cov_kwds={"maxlags": 6})
            print(f"   same-month response to a 1 pp NS surprise, {lab}: {r.params.iloc[1]:+.2f} ({r.bse.iloc[1]:.2f})")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(13, 6.5))
    t = J.index.to_timestamp()
    for c, col, lab in (("MF-FCI A parallel", "#7f3fbf", "ECB Macro-Finance FCI, approximate US weights (variant A), parallel-move units"),
                        ("MACRO", "#d62728", "Macro-model levels index (FRB/US weights)"), ("MKT", "#ff7f0e", "Market-based index (NS weights)"), ("GS", "#2ca02c", "GS (NS conversion)")):
        ax.plot(t, J[c], color=col, lw=1.4, label=lab)
    ax.axhline(0, color="gray", lw=0.8); ax.grid(alpha=0.25); ax.set_ylabel("pp of funds rate, tighter above zero (vs 1999-2026 average)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=2, fontsize=9, frameon=False)
    ax.set_title("Approximate US Macro-Finance FCI against the project's indexes, funds-rate units", fontsize=11)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "mffci_us.png"), dpi=130)


if __name__ == "__main__":
    main()
