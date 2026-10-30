"""
SF Fed Proxy Funds Rate (Choi, Doh, Foerster, Martinez; weekly, raw/proxy-funds-rate-data.xlsx) against the indexes in funds-rate pp.
The proxy equals the effective funds rate until the week of 12 Dec 2008 by construction; afterwards it maps 12 rates and spreads (PCA) into funds-rate units using pre-2008 relationships.
So before 2009 the proxy just is the funds rate and carries no information on financial conditions beyond it; the comparison is from 2009 (changes are the natural object, as the proxy is a level of an
equivalent policy rate and ours are deviations from the 1990-2026 average).
Indexes: macro-model levels index (nominal, without and with house prices; real), market-based (NS weights, nominal), GS (NS conversion 0.945, nominal), FCI-G (official / yardstick 0.4525).
Usage: python experimental/fci_compare/proxy_compare.py
"""
import os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "experimental", "path_fci"))
import path_fci as P
import path_fci_gss_ns as Q


def main():
    w = pd.read_excel(os.path.join(ROOT, "raw", "proxy-funds-rate-data.xlsx"), sheet_name="Weekly", skiprows=1, names=["date", "ffr", "proxy"])
    w["date"] = pd.to_datetime(w.date); w = w.set_index("date")
    ev = P.events(P.USMPD)
    d = ev.dropna(subset=Q.FUT + ["UST2Y"] + list(Q.ENDOG.values())).reset_index(drop=True)
    gss, ns, _, _ = Q.gss_ns(d)
    wt = pd.Series(Q.estimate(d, ns, True)[0], index=list(Q.ENDOG))
    P.L.REAL10 = False; P.L.RSTAR = False
    X, G = P.L.build()
    mkt = sum(wt[n] * P.VARS[n][1] * (X[P.VARS[n][0]] - X[P.VARS[n][0]].mean()) for n in wt.index) * 0.983
    gs = (G.fci - G.fci.mean()) * 0.945
    mm = {t: pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", f"macro_model_levels_daily{t}.csv"), parse_dates=["date"]).set_index("date") for t in ("", "_real10")}
    S = {"macro nominal, no HP": mm[""]["without house prices"], "macro nominal, with HP": mm[""]["with house prices"], "macro real, no HP": mm["_real10"]["without house prices"],
         "market-based (NS)": mkt, "GS (NS conversion)": gs}
    f3 = pd.read_csv(os.path.join(ROOT, "raw", "fed_monthly_3yr.csv"), parse_dates=["date"]).set_index("date").iloc[:, 0]
    # weekly (Friday) alignment
    wk = {k: v.resample("W-FRI").last() for k, v in S.items()}
    P_ = w.proxy
    print("Proxy funds rate (weekly), last:", P_.index[-1].date(), round(float(P_.iloc[-1]), 2), "; EFFR", float(w.ffr.iloc[-1]))
    def at(s, d0):
        return float(s.loc[:d0].iloc[-1])
    last = P_.index[-1]
    print("\nChange to", last.date(), "in funds-rate pp:")
    rows = [("SF Fed proxy", at(P_, last) - at(P_, "2026-02-27"), at(P_, last) - at(P_, "2026-08-27"))]
    for k, s in wk.items():
        rows.append((k, at(s, last) - at(s, "2026-02-27"), at(s, last) - at(s, "2026-08-27")))
    print(pd.DataFrame(rows, columns=["index", "since 27 Feb", "since 27 Aug"]).round(2).to_string(index=False))
    print("\nFrom 2009: weekly proxy vs index, correlation of levels and of 13-week and 52-week changes; slope of the index on the proxy in 52-week changes")
    out = []
    for k, s in wk.items():
        j = pd.concat({"proxy": P_, "idx": s}, axis=1).dropna().loc["2009-01-01":]
        c52 = j.diff(52).dropna(); c13 = j.diff(13).dropna()
        out.append(dict(index=k, lev=j.corr().iloc[0, 1], chg13=c13.corr().iloc[0, 1], chg52=c52.corr().iloc[0, 1], slope52=np.polyfit(c52.proxy, c52.idx, 1)[0], sd_proxy52=c52.proxy.std(), sd_idx52=c52.idx.std()))
    print(pd.DataFrame(out).round(2).to_string(index=False))
    print("\nProxy minus effective funds rate (the post-2008 gap) latest and selected dates:", {str(d0): round(float((w.proxy - w.ffr).loc[:d0].iloc[-1]), 2) for d0 in ("2010-01-01", "2014-12-31", "2019-12-31", "2021-12-31", "2023-12-31", "2026-02-27", "2026-10-09")})


if __name__ == "__main__":
    main()
