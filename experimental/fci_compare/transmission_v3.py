"""
Transmission-lens indexes as specified in experimental/INDEX_QA.md (approved 29 Oct 2026). Unit: pp of the 2-year yield per Nakamura-Steinsson (NS) policy-news unit (answer 11).
    MKT       NS one-factor GLS weights (full residual covariance) from intraday window moves of the 10-year, S&P 500 and DXY (USMPD), applied to daily levels of the
              nominal 10-year, 100 ln CAPE and 100 ln real broad dollar, demeaned over the daily sample (answer 10); static (answer 31)
    MKT+Baa   robustness (answers 12-13): adds the Moody's Baa yield (DBAA); its response and residual use the event-day change (previous business day to the event day),
              the other three keep their intraday windows; index adds the demeaned Baa yield level
    GS        GS replication x 0.945 / 0.98 (= its NS response in 2-year units, answer 14)
    NFCI, ANFCI  divided by their weekly response to NS surprises (weekly change on the sum of NS surprises in the week, Friday-dated weeks, HAC 4) (answer 16)
    OFR FSI   divided by its event-day response to NS surprises (daily, from 2000) (answer 34)
Usage: python experimental/fci_compare/transmission_v3.py
Outputs: transmission_v3_monthly.csv, transmission_v3_daily.csv (MKT, MKT+Baa, GS)
"""
import os, sys
import numpy as np, pandas as pd
import statsmodels.api as sm

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "experimental", "path_fci"))
import path_fci as P
import path_fci_gss_ns as Q


def raw(name, col=1):
    d = pd.read_csv(os.path.join(ROOT, "raw", name))
    return pd.Series(pd.to_numeric(d.iloc[:, col], errors="coerce").values, index=pd.to_datetime(d.iloc[:, 0])).dropna()


def me(s):
    s = s.resample("ME").last(); s.index = s.index.to_period("M"); return s


def gls(Y, f):
    """Y: n x k window changes; f: factor. Returns weights (w'b = 1), b, se(b), residual covariance."""
    Z = sm.add_constant(f)
    res = [sm.OLS(Y[:, j], Z).fit(cov_type="HC1") for j in range(Y.shape[1])]
    b = np.array([r.params[1] for r in res]); se = np.array([r.bse[1] for r in res])
    S = np.cov(np.array([r.resid for r in res]), ddof=2)
    w = np.linalg.solve(S, b)
    return w / (b @ w), b, se, S


def event_day_change(series, dates):
    s = series.sort_index()
    out = []
    for dt in dates:
        dt = pd.Timestamp(dt)
        if dt not in s.index:
            out.append(np.nan); continue
        i = s.index.get_loc(dt)
        out.append(s.iloc[i] - s.iloc[i - 1] if i > 0 else np.nan)
    return np.array(out)


def main():
    ev = P.events(P.USMPD)
    d = ev.dropna(subset=Q.FUT + ["UST2Y"] + list(Q.ENDOG.values())).reset_index(drop=True)
    _, ns, _, _ = Q.gss_ns(d)
    d = d.assign(ns=ns)
    names = list(Q.ENDOG)
    Y = d[list(Q.ENDOG.values())].values
    w, b, se, S = gls(Y, d.ns.values)
    print(f"{len(d)} events. MKT: responses per NS unit " + ", ".join(f"{n} {b[i]:+.3f} ({se[i]:.3f})" for i, n in enumerate(names)))
    print("     weights (2-year-yield pp per unit): " + ", ".join(f"{n} {w[i]:+.4f}" for i, n in enumerate(names)))
    P.L.REAL10 = False; P.L.RSTAR = False
    X, G = P.L.build()
    lev = {n: P.VARS[n][1] * X[P.VARS[n][0]] for n in names}
    mkt = sum(w[i] * (lev[n] - lev[n].mean()) for i, n in enumerate(names))
    # robustness: + Baa yield (event-day change)
    baa = raw("DBAA.csv")
    db = event_day_change(baa, d.Date)
    ok = ~np.isnan(db)
    Y4 = np.column_stack([Y[ok], db[ok]])
    w4, b4, se4, S4 = gls(Y4, d.ns.values[ok])
    names4 = names + ["Baa yield"]
    print(f"MKT+Baa ({ok.sum()} events): responses " + ", ".join(f"{n} {b4[i]:+.3f} ({se4[i]:.3f})" for i, n in enumerate(names4)))
    print("     weights: " + ", ".join(f"{n} {w4[i]:+.4f}" for i, n in enumerate(names4)))
    baal = baa.reindex(X.index).ffill()
    mkt4 = sum(w4[i] * (lev[n] - lev[n].mean()) for i, n in enumerate(names)) + w4[3] * (baal - baal.mean())
    gs = (G.fci - G.fci.mean()) * 0.945 / 0.98
    daily = pd.DataFrame({"MKT": mkt, "MKT+Baa": mkt4, "GS": gs.reindex(X.index)})
    daily.to_csv(os.path.join(HERE, "transmission_v3_daily.csv"), float_format="%.4f", index_label="date")
    # NFCI / ANFCI weekly
    conv = {}
    for nm in ("NFCI", "ANFCI"):
        s = raw(f"{nm}.csv")
        wk = pd.Series(0.0, index=s.index)
        fri = pd.to_datetime(d.Date) + pd.to_timedelta((4 - pd.to_datetime(d.Date).dt.weekday) % 7, unit="D")
        for f_, v in zip(fri, d.ns):
            if f_ in wk.index: wk[f_] += v
        j = pd.DataFrame({"dy": s.diff(), "s": wk}).loc["1994-01-01":"2026-12-31"].dropna()
        r = sm.OLS(j.dy, sm.add_constant(j.s)).fit(cov_type="HAC", cov_kwds={"maxlags": 4})
        conv[nm] = (r.params["s"], r.bse["s"], int((j.s != 0).sum()))
    ofr = raw("ofr_fsi.csv")
    dd = event_day_change(ofr, d.Date)
    okk = ~np.isnan(dd)
    r = sm.OLS(dd[okk], sm.add_constant(d.ns.values[okk])).fit(cov_type="HC1")
    conv["OFR FSI"] = (r.params[1], r.bse[1], int(okk.sum()))
    print("\nResponse to a 1-unit NS surprise (index units; se; events): " + "; ".join(f"{k} {v[0]:+.3f} ({v[1]:.3f}; n={v[2]})" for k, v in conv.items()))
    M = pd.DataFrame({"MKT": me(mkt), "MKT+Baa": me(mkt4), "GS": me(gs),
                      "NFCI": me(raw("NFCI.csv")) / conv["NFCI"][0], "ANFCI": me(raw("ANFCI.csv")) / conv["ANFCI"][0], "OFR FSI": me(ofr) / conv["OFR FSI"][0]}).loc["1990-01":"2026-10"]
    for c in ("NFCI", "ANFCI", "OFR FSI"):
        M[c] = M[c] - M[c].mean()
    M.to_csv(os.path.join(HERE, "transmission_v3_monthly.csv"), float_format="%.4f", index_label="month")
    print("\nmonthly, pp of 2-year yield: sd", M.std().round(2).to_dict())
    print("latest", M.index[-1], M.iloc[-1].round(2).to_dict())


if __name__ == "__main__":
    main()
