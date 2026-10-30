"""
r* cases (RSTAR_QA S1-S4): all indexes rebuilt with rates as gaps to r*.
    r*: Laubach-Williams one-sided, full-sample (main, "LW") and Kiley one-sided (check, "Ki"); quarterly, linear between mid-quarter months, last value held after 2026Q2.
    Gaps: real policy rate - r*, real 10-year - r*, real BBB yield - r* (FCI-G), real mortgage rate - r* (FCI-G); spreads over the 10-year unchanged (r* cancels).
    Equities: earnings-yield gap E/P - r* (E/P = 100 / CAPE), entered in CAPE log-point units with the fixed factor (S1b): x_eq = -(100 / mean E/P) (E/P - r*), so every
        index keeps its CAPE weight.
    Indexes: FRB/US EP/CP/GI (macro_real.build), market index, GS (2-year units), FCI-G all-real form with the gaps above (stocks: change of x_eq), NFCI/ANFCI unchanged.
    Zero: 1973-2026 mean of every variable (S3).
Usage: python experimental/rstar_case/rstar_indexes.py      Output: rstar_indexes_monthly.csv
"""
import os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
RC = os.path.join(ROOT, "experimental", "real_case")
for p in (RC, os.path.join(ROOT, "experimental", "ms_fci"), ROOT):
    sys.path.insert(0, p)
import macro_real as MR
import fcig_real as FG
import fcig_replicate as FR

WIN = slice("1973-01", "2026-10")
K = 0.945 / 0.98
WM = {"real 10-year": 0.6089, "equities": -0.0512, "dollar": 0.0654}
WG = {"real policy rate": 0.044, "real 10-year": 0.451, "BBB spread": 0.396, "equities": -0.049, "dollar": 0.060}


def rd(p):
    d = pd.read_csv(p, index_col=0); d.index = pd.PeriodIndex(d.index, freq="M"); return d


def rstar(idx):
    rs = pd.read_csv(os.path.join(ROOT, "experimental", "fci_compare", "rstar_series.csv"), index_col=0); rs.index = pd.PeriodIndex(rs.index, freq="Q")
    out = {}
    for lab, col in (("LW", "LW_onesided"), ("Ki", "Kiley_onesided")):
        q = rs[col].dropna()
        m = pd.Series(q.values, index=[p.asfreq("M", "s") + 1 for p in q.index])     # mid-quarter month
        full = pd.period_range(min(m.index[0], idx[0]), max(m.index[-1], idx[-1]), freq="M")
        out[lab] = m.reindex(full).interpolate(limit_area="inside").ffill().bfill().reindex(idx)
    return out


def ep_level(D):
    sh = pd.read_csv(os.path.join(ROOT, "raw", "shiller_cape.csv")); sh = pd.Series(sh.cape.values, index=pd.PeriodIndex(sh.month, freq="M"))
    k = float((100 * np.log(sh.loc["1990-01":"1992-12"]) - D.equities.loc["1990-01":"1992-12"]).mean())
    return 100 / np.exp((D.equities + k) / 100)


def main():
    D = rd(os.path.join(RC, "data_long_monthly.csv")).loc["1972-01":"2026-10"]
    EP = ep_level(D)
    fac = 100 / EP.loc[WIN].mean()
    print(f"mean E/P 1973-2026 {EP.loc[WIN].mean():.2f}; factor {fac:.2f}")
    RS = rstar(D.index)
    X0 = MR.data()
    M = FG.monthly()
    E = rd(os.path.join(RC, "expinf_monthly.csv"))
    cpi = FG.mp(FR.fred("CPIAUCSL")).reindex(M.index)
    old, new = FG.mp(FR.fred("TWEXBPA")), FG.mp(FR.fred("RTWEXBGS"))
    rdol = pd.concat([old.loc[:new.index[0] - 1] * float(new.iloc[0] / old.loc[new.index[0]]), new]).reindex(M.index)
    out = {}
    for lab, r in RS.items():
        xeq = -fac * (EP - r)
        # FRB/US
        X = X0.copy()
        X["policy rate"] = (D["real policy rate"] - r).reindex(X.index)
        X["10-year"] = (D["real 10-year"] - r).reindex(X.index)
        X["equities"] = xeq.reindex(X.index)
        B = MR.build(X, WIN)
        for c in ("EP_4", "EP_4+HP", "CP_4", "GI_1yr+HP"):
            out[f"{c} {lab}"] = B[c]
        # market and GS
        V = pd.DataFrame({"real policy rate": D["real policy rate"] - r, "real 10-year": D["real 10-year"] - r, "BBB spread": D["BBB spread"], "equities": xeq, "dollar": D["dollar"]}).loc[WIN]
        Vd = V - V.mean()
        out[f"MKT {lab}"] = sum(WM[k_] * Vd[k_] for k_ in WM)
        out[f"GS {lab}"] = sum(WG[k_] * Vd[k_] for k_ in WG) * K
        # FCI-G (all-real form, gaps to r*)
        rm = r.reindex(M.index).ffill().bfill()
        A = M.copy()
        A["FFR"] = M["FFR"] - E.einf_1y.reindex(M.index) - rm
        for c in ("10Yr Treasury", "Mortgage Rate", "BBB"):
            A[c] = M[c] - E.einf_10y.reindex(M.index) - rm
        A["Stock Market"] = np.exp(xeq.reindex(M.index) / 100)
        A["House Prices"] = M["House Prices"] / cpi
        A["Dollar"] = rdol
        Dc = FG.changes(A)
        out[f"FCI-G 1yr {lab}"], _ = FG.fcig(Dc, 4)
        out[f"FCI-G 3yr {lab}"], _ = FG.fcig(Dc, 12)
        out[f"rstar {lab}"] = r
    O = pd.DataFrame(out).loc["1973-01":"2026-09"]
    O.to_csv(os.path.join(HERE, "rstar_indexes_monthly.csv"), float_format="%.4f", index_label="month")
    # against the real case
    mr, mk, gs, fg = rd(os.path.join(RC, "macro_real_monthly.csv")), rd(os.path.join(RC, "market_real_monthly.csv")), rd(os.path.join(RC, "gs_real_monthly.csv")), rd(os.path.join(RC, "fcig_real_monthly.csv"))
    real = {"EP_4": mr.EP_4, "EP_4+HP": mr["EP_4+HP"], "CP_4": mr.CP_4, "MKT": mk.MKT_real, "GS": gs.GS_real * K, "FCI-G 1yr": fg["1yr all real"], "FCI-G 3yr": fg["3yr all real"]}
    pd.set_option("display.width", 250)
    print("\nagainst the real case, 1974-2026 (corr levels / 12m changes; sd r*-case vs real; latest r*-case vs real):")
    for c, s in real.items():
        for lab in ("LW", "Ki"):
            j = pd.concat([O[f"{c} {lab}"], s], axis=1).loc["1974-01":"2026-09"].dropna()
            print(f"   {c:9s} {lab}: {j.corr().iloc[0, 1]:.2f} / {j.diff(12).corr().iloc[0, 1]:.2f}; sd {j.iloc[:, 0].std():.2f} vs {j.iloc[:, 1].std():.2f}; latest {j.iloc[-1, 0]:+.2f} vs {j.iloc[-1, 1]:+.2f}")
    sel = [pd.Period(m, "M") for m in ("1974-12", "1979-12", "1981-06", "1985-01", "1990-01", "2000-03", "2008-12", "2013-01", "2015-01", "2021-12", "2023-10", "2026-09")]
    print("\nLW (main):")
    print(O.loc[sel, ["rstar LW", "EP_4 LW", "EP_4+HP LW", "MKT LW", "GS LW", "FCI-G 1yr LW", "FCI-G 3yr LW"]].round(2).to_string())
    R = pd.DataFrame({k_: v for k_, v in real.items()}).loc[sel]
    print("\nreal case, same months:\n" + R.round(2).to_string())


if __name__ == "__main__":
    main()
