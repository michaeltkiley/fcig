"""
Two follow-ups on the output lens (user, 30 Oct; RSTAR_QA S8):
 A. FCI-G scale check. FCI-G (1-year lookback) claims a reading of +1 means GDP growth over the next four quarters 1 pp lower; with Okun's law (coefficient 2, as in the project)
    the unemployment gap should be about 0.5 pp higher 12 months later. Tested two ways, 1974-2026 (2020 excluded / dummied):
      (i)  direct regression: u(t+12) - u(t) = a + b FCI-G(t) + c1 u(t) + c2 [u(t) - u(t-3)] + e (HAC, 12 lags; targets in 2020-2021-03 and origins in 2020 dropped); b should be about 0.5
      (ii) two-variable VAR (u, FCI-G; Cholesky with u first; 4 and 12 lags; 2020 dummies): unemployment response 12 months after a 1-unit FCI-G shock (with FCI-G's own path)
    Versions: all-real (main real case), r*-gap LW and Kiley, nominal monthly replication from 1974, published FCI-G (1990-2026); 3-year lookback as well.
 B. Horse race: which index best predicts unemployment? Same design for every index: 4 and 12 lags, Granger F, unemployment-equation residual sd; plus pseudo out-of-sample
    12-month-ahead forecasts (direct regression as in A(i), recursive, origins 1995-01..2025-09, 2020 targets excluded) as the ratio of RMSE to the no-index benchmark.
    Indexes: real and r*-gap (LW, Kiley) FRB/US EP_4, market index, GS, FCI-G 1-year; nominal market index (long); ANFCI (1990 on, second sample only).
    Samples: 1974-03..2026-09 (all but ANFCI) and 1990-01..2026-09 (all).
 C. Fairness check for B: level indexes as 12-month changes (the flow counterpart of FCI-G) in the direct regression and the out-of-sample forecasts.
Usage: python experimental/rstar_case/var_fcig_horse.py      Output: var_fcig_horse.log (via tee)
"""
import os, sys, warnings
import numpy as np, pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.api import VAR
warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
RC = os.path.join(ROOT, "experimental", "real_case")
sys.path.insert(0, os.path.join(ROOT, "experimental", "market_macro"))
import mkt_output as MO


def rd(p):
    d = pd.read_csv(p, index_col=0); d.index = pd.PeriodIndex(d.index, freq="M"); return d


def is2020(idx):
    return np.array([(p.year == 2020) or (p.year == 2021 and p.month <= 3) for p in idx])


def direct(u, x, start, end, h=12):
    J = pd.DataFrame({"dy": u.shift(-h) - u, "x": x, "u": u, "du3": u - u.shift(3)}).loc[start:end]
    tgt = pd.PeriodIndex([p + h for p in J.index])
    J = J[~is2020(tgt) & ~is2020(J.index)].dropna()
    r = sm.OLS(J.dy, sm.add_constant(J[["x", "u", "du3"]])).fit(cov_type="HAC", cov_kwds={"maxlags": 12})
    return r, J


def var_resp(u, x, start, end, p):
    D = pd.DataFrame({"u": u, "M": x}).loc[start:end].dropna()
    dum = pd.DataFrame({f"d{m}": (D.index == pd.Period(f"2020-{m:02d}", "M")).astype(float) for m in range(1, 13)}, index=D.index)
    D.index = D.index.to_timestamp(); dum.index = D.index
    r = VAR(D, exog=dum).fit(p)
    oi = r.irf(24).orth_irfs; sc = oi[0, 1, 1]
    se = r.irf(24).stderr(orth=True)[:, 0, 1] / sc
    return r, oi[:, 0, 1] / sc, se, oi[:, 1, 1] / sc


def u_only(u, start, end, p):
    D = pd.DataFrame({"u": u}).loc[start:end].dropna()
    X = pd.concat([D.u.shift(l) for l in range(1, p + 1)], axis=1)
    dum = pd.DataFrame({f"d{m}": (D.index == pd.Period(f"2020-{m:02d}", "M")).astype(float) for m in range(1, 13)}, index=D.index)
    J = pd.concat([D.u, X, dum], axis=1).dropna()
    return sm.OLS(J.iloc[:, 0], sm.add_constant(J.iloc[:, 1:])).fit().resid.std()


def oos(u, x, first="1995-01", last="2025-09", h=12):
    J = pd.DataFrame({"dy": u.shift(-h) - u, "x": x, "u": u, "du3": u - u.shift(3)}).dropna(subset=["x", "u", "du3"])
    e1, e0 = [], []
    for t in pd.period_range(first, last, freq="M"):
        if t not in J.index or pd.isna(J.dy.get(t)) or is2020(pd.PeriodIndex([t + h]))[0]:
            continue
        tr = J.loc[:t - h]
        tr = tr[~is2020(pd.PeriodIndex([p + h for p in tr.index])) & ~is2020(tr.index)].dropna()
        if len(tr) < 120:
            continue
        b1 = np.linalg.lstsq(np.c_[np.ones(len(tr)), tr[["x", "u", "du3"]].values], tr.dy.values, rcond=None)[0]
        b0 = np.linalg.lstsq(np.c_[np.ones(len(tr)), tr[["u", "du3"]].values], tr.dy.values, rcond=None)[0]
        row = J.loc[t]
        e1.append(row.dy - b1 @ np.r_[1, row.x, row.u, row.du3]); e0.append(row.dy - b0 @ np.r_[1, row.u, row.du3])
    e1, e0 = np.array(e1), np.array(e0)
    return np.sqrt((e1 ** 2).mean()) / np.sqrt((e0 ** 2).mean()), len(e1)


def main():
    u = MO.V.macro_data(False)["unemployment gap"]
    fr, mr, mk, gs, nf, rs = (rd(os.path.join(RC, "fcig_real_monthly.csv")), rd(os.path.join(RC, "macro_real_monthly.csv")), rd(os.path.join(RC, "market_real_monthly.csv")),
                              rd(os.path.join(RC, "gs_real_monthly.csv")), rd(os.path.join(RC, "nfci_real_monthly.csv")), rd(os.path.join(HERE, "rstar_indexes_monthly.csv")))
    pub = pd.read_csv(os.path.join(ROOT, "raw", "fed_monthly_1yr.csv"), parse_dates=["date"]).set_index("date").iloc[:, 0]; pub.index = pub.index.to_period("M")
    pub3 = pd.read_csv(os.path.join(ROOT, "raw", "fed_monthly_3yr.csv"), parse_dates=["date"]).set_index("date").iloc[:, 0]; pub3.index = pub3.index.to_period("M")
    print("A. FCI-G SCALE CHECK: a reading of +1 should be followed by unemployment about +0.5 pp higher after 12 months (Okun 2)")
    versions = {"all real 1yr": (fr["1yr all real"], "1974-03"), "rates-only real 1yr": (fr["1yr real"], "1974-03"), "nominal 1yr (replication)": (fr["1yr nominal"], "1974-03"),
                "r* LW 1yr": (rs["FCI-G 1yr LW"], "1974-03"), "r* Kiley 1yr": (rs["FCI-G 1yr Ki"], "1974-03"), "published 1yr": (pub, "1990-01"),
                "nominal 1yr (replication), 1990-": (fr["1yr nominal"], "1990-01"),
                "all real 3yr": (fr["3yr all real"], "1976-03"), "r* LW 3yr": (rs["FCI-G 3yr LW"], "1976-03"), "published 3yr": (pub3, "1990-01")}
    for nm, (x, st) in versions.items():
        r, J = direct(u, x, st, "2026-09")
        line = f"   {nm:34s} direct b {r.params['x']:+.3f} (se {r.bse['x']:.3f}; n {len(J)}; sd of index {x.loc[st:].std():.2f})"
        for p in (4, 12):
            _, Phi, se, own = var_resp(u, x, st, "2026-09", p)
            line += f" | VAR p{p}: Phi(12) {Phi[12]:+.3f} (t {Phi[12] / se[12]:.1f}), own m12 {own[12]:+.2f}"
        print(line)
    print("   (VAR Phi(12) is the response to a shock whose own path is shown as 'own m12'; the direct b holds the index reading at t and lets later readings follow their usual path)")

    print("\nB. HORSE RACE: predicting the unemployment gap")
    IDX = {"real EP_4 (FRB/US)": mr.EP_4, "real MKT": mk.MKT_real, "real GS": gs.GS_real, "real FCI-G 1yr": fr["1yr all real"],
           "r* LW EP_4": rs["EP_4 LW"], "r* LW MKT": rs["MKT LW"], "r* LW GS": rs["GS LW"], "r* LW FCI-G 1yr": rs["FCI-G 1yr LW"],
           "r* Ki EP_4": rs["EP_4 Ki"], "r* Ki MKT": rs["MKT Ki"], "r* Ki GS": rs["GS Ki"], "r* Ki FCI-G 1yr": rs["FCI-G 1yr Ki"]}
    F = MO.LL.financial()[MO.VARS]
    IDX["nominal MKT (long)"] = pd.Series((F - F.mean()).values @ MO.W, index=F.index)
    for st, extra in (("1974-03", {}), ("1990-01", {"ANFCI": nf.ANFCI})):
        ids = dict(IDX, **extra)
        print(f"\n   sample {st}..2026-09; u-equation residual sd without any index: p4 {u_only(u, st, '2026-09', 4):.4f}, p12 {u_only(u, st, '2026-09', 12):.4f}")
        rows = []
        for nm, x in ids.items():
            row = {"index": nm}
            for p in (4, 12):
                r, Phi, se, _ = var_resp(u, x, st, "2026-09", p)
                gc = r.test_causality("u", ["M"], kind="f")
                row[f"F p{p}"] = gc.test_statistic; row[f"pval p{p}"] = gc.pvalue; row[f"resid sd p{p}"] = r.resid["u"].std()
            row["OOS RMSE ratio"], row["n OOS"] = oos(u, x.loc[st:])
            rd_, _ = direct(u, x, st, "2026-09"); row["direct t"] = rd_.tvalues["x"]
            rows.append(row)
        T = pd.DataFrame(rows).set_index("index").sort_values("F p4", ascending=False)
        print(T.round({"F p4": 2, "F p12": 2, "pval p4": 4, "pval p12": 4, "resid sd p4": 4, "resid sd p12": 4, "OOS RMSE ratio": 3, "direct t": 2}).to_string())
        print(f"\n   C. level indexes as 12-month changes, sample {st}..2026-09:")
        for nm, x in ids.items():
            if "FCI-G" in nm:
                continue
            a = oos(u, x.diff(12).loc[st:]); r, _ = direct(u, x.diff(12), st, "2026-09")
            print(f"      {nm:20s} OOS RMSE ratio {a[0]:.3f}; direct b {r.params['x']:+.3f} (t {r.tvalues['x']:.2f})")


if __name__ == "__main__":
    main()
