"""
Correlations of the macro-model levels index (nominal and real; without and with house prices) with the market-based index (MKT, NS-shock weights), the GS replication and FCI-G,
monthly (end-of-month), levels and 12-month changes, for samples starting 1990 (full), 1992 and 1998. Nominal macro versions are matched with the nominal MKT and GS; real with real.
FCI-G (official through 2026-08, replication after) has only a nominal version and is shown against all.
Scaling does not matter for correlations, so no funds-rate conversion is applied here.
Usage: python experimental/fci_compare/corr_table.py
"""
import os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "experimental", "path_fci"))
import path_fci as P
import path_fci_gss_ns as Q


def me(s):
    s = s.resample("ME").last(); s.index = s.index.to_period("M"); return s


def main():
    ev = P.events(P.USMPD)
    d = ev.dropna(subset=Q.FUT + ["UST2Y"] + list(Q.ENDOG.values())).reset_index(drop=True)
    gss, ns, _, _ = Q.gss_ns(d)
    w = pd.Series(Q.estimate(d, ns, True)[0], index=list(Q.ENDOG))
    series = {}
    for tag, real in (("nominal", False), ("real", True)):
        P.L.REAL10 = real; P.L.RSTAR = False
        X, G = P.L.build()
        mkt = sum(w[n] * P.VARS[n][1] * (X[P.VARS[n][0]] - X[P.VARS[n][0]].mean()) for n in w.index)
        gs = G.fci.reindex(X.index)
        if real:
            gs = gs - (0.044 + 0.451) * X.einf + 0.06 * (100 * X.lnrusd - 100 * np.log(G.x_usd.reindex(X.index)))
        mm = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", f"macro_model_levels_daily{'_real10' if real else ''}.csv"), parse_dates=["date"]).set_index("date")
        series[tag] = dict(MKT=me(mkt), GS=me(gs), MACRO_noHP=me(mm["without house prices"]), MACRO_HP=me(mm["with house prices"]))
    f3 = pd.read_csv(os.path.join(ROOT, "raw", "fed_monthly_3yr.csv"), parse_dates=["date"]).set_index("date").iloc[:, 0]; f3.index = f3.index.to_period("M")
    rep = pd.read_csv(os.path.join(ROOT, "fcig_replication_monthly.csv")); rep["month"] = pd.PeriodIndex(rep["month"], freq="M"); rep = rep.set_index("month")["3yr|FCI-G"]
    fcig = pd.concat([f3, rep.loc[f3.index[-1] + 1:]])
    rows = []
    for samp, a in (("1990-", "1990-01"), ("1992-", "1992-01"), ("1998-", "1998-01")):
        for tag in ("nominal", "real"):
            S = series[tag]
            for mname in ("MACRO_noHP", "MACRO_HP"):
                for oth in ("MKT", "GS", "FCI-G"):
                    x = S[mname]
                    y = fcig if oth == "FCI-G" else S[oth]
                    j = pd.concat([x, y], axis=1).dropna().loc[a:]
                    rows.append(dict(sample=samp, version=tag, macro=mname.replace("MACRO_", ""), vs=oth, levels=j.corr().iloc[0, 1], chg12=j.diff(12).corr().iloc[0, 1], n=len(j)))
    R = pd.DataFrame(rows)
    pd.set_option("display.width", 200)
    for samp in R["sample"].unique():
        t = R[R["sample"] == samp]
        print(f"\n=== Monthly, from {samp[:-1]}: macro-model index versus ... (levels / 12-month changes) ===")
        pv = t.pivot_table(index=["version", "macro"], columns="vs", values=["levels", "chg12"])
        out = pd.DataFrame({o: pv["levels"][o].round(2).astype(str) + " / " + pv["chg12"][o].round(2).astype(str) for o in ("MKT", "GS", "FCI-G")})
        print(out.to_string())
    # the other pairs for context
    print("\n=== Context: MKT vs GS vs FCI-G (levels / 12-month changes) ===")
    for samp, a in (("1990-", "1990-01"), ("1992-", "1992-01"), ("1998-", "1998-01")):
        for tag in ("nominal", "real"):
            S = series[tag]
            j = pd.concat({"MKT": S["MKT"], "GS": S["GS"], "FCI-G": fcig}, axis=1).dropna().loc[a:]
            c, c12 = j.corr(), j.diff(12).corr()
            print(f"  {samp} {tag}: MKT/GS {c.loc['MKT', 'GS']:.2f}/{c12.loc['MKT', 'GS']:.2f}; MKT/FCI-G {c.loc['MKT', 'FCI-G']:.2f}/{c12.loc['MKT', 'FCI-G']:.2f}; GS/FCI-G {c.loc['GS', 'FCI-G']:.2f}/{c12.loc['GS', 'FCI-G']:.2f}")
    R.round(3).to_csv(os.path.join(HERE, "corr_table.csv"), index=False)


if __name__ == "__main__":
    main()
