"""
Smoothed (impulse-response-weighted) indexes in the unemployment local projection (user, 30 Oct; RSTAR_QA S8c).
FCI-G smooths financial changes over time with impulse-response weights; so do the dynamic indexes built in the project:
    FRB/US: current pressure CP_4 (distributed lag on levels), growth impetus GI_1yr+HP (FCI-G form), realized impetus (12-month change of CP_4)
    market VAR (4 and 12 lags): current pressure CP, forward impetus, realized impetus
    FCI-G: 1-year and 3-year lookback
  each in the real case and the r*-gap case (LW); the level indexes (EP_4, market index) as reference.
Regression (as lp_unemp / lp_detail): u(t+12) on u(t..t-L+1) and x(t..t-L+1), L = 4 (main) and L = 1 (current reading only); HAC; months touching 2020-01..2021-03 dropped.
In sample: Wald p of the index terms, adjusted R2 gain over u lags only, residual sd. Out of sample: recursive, origins 1995-01..2025-09, RMSE ratio to the u-only projection,
by subperiod, and Diebold-Mariano t (HAC 12; negative = index better).
Caveat: the market-VAR indexes use lag weights estimated on the full sample (look-ahead in the out-of-sample exercise); FRB/US and FCI-G weights are model-based (no look-ahead).
Usage: python experimental/rstar_case/lp_smoothed.py      Output: lp_smoothed.log (via tee)
"""
import os, sys, warnings
import numpy as np, pandas as pd
import statsmodels.api as sm
warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import var_fcig_horse as H
import lp_detail as D


def run(u, x, st, L):
    D.L = L
    r, sc, ssd, wp, dr2, n = D.fit(u, x, 12, st)
    E = D.oos_errors(u, x, st)
    row = {"sum c": round(sc, 3), "t sum": round(sc / ssd, 1), "Wald p": round(wp, 4), "dR2": round(dr2, 3), "resid sd": round(float(r.resid.std()), 4)}
    for lab, a, b in (("OOS 95-07", "1995-01", "2007-12"), ("OOS 08-19", "2008-01", "2019-12"), ("OOS 21-25", "2021-01", "2025-09"), ("OOS all", "1995-01", "2025-09")):
        e = E.loc[a:b]
        row[lab] = round(float(np.sqrt((e.e1 ** 2).mean() / (e.e0 ** 2).mean())), 3)
    row["DM t"] = round(D.dm(E), 2)
    return row


def main():
    u = H.MO.V.macro_data(False)["unemployment gap"]
    rd, RC = H.rd, H.RC
    mr, fr, vr = rd(os.path.join(RC, "macro_real_monthly.csv")), rd(os.path.join(RC, "fcig_real_monthly.csv")), rd(os.path.join(RC, "var_real_monthly.csv"))
    rs, vs = rd(os.path.join(HERE, "rstar_indexes_monthly.csv")), rd(os.path.join(HERE, "var_rstar_monthly.csv"))
    IDX = {
        "real | FCI-G 1yr": fr["1yr all real"], "real | FCI-G 3yr": fr["3yr all real"],
        "real | FRB/US GI_1yr+HP": mr["GI_1yr+HP"], "real | FRB/US CP_4": mr.CP_4, "real | FRB/US CP_4 12m chg": mr.CP_4.diff(12), "real | FRB/US EP_4 (level)": mr.EP_4,
        "real | VAR4 CP": vr["CP p4"], "real | VAR4 fwd impetus": vr["forward impetus p4"], "real | VAR4 realized": vr["realized impetus p4"],
        "real | VAR12 CP": vr["CP p12"], "real | VAR12 fwd impetus": vr["forward impetus p12"], "real | VAR12 realized": vr["realized impetus p12"],
        "real | MKT (level)": vr["EP (real market index)"],
        "r* LW | FCI-G 1yr": rs["FCI-G 1yr LW"], "r* LW | FCI-G 3yr": rs["FCI-G 3yr LW"],
        "r* LW | FRB/US GI_1yr+HP": rs["GI_1yr+HP LW"], "r* LW | FRB/US CP_4": rs["CP_4 LW"], "r* LW | FRB/US CP_4 12m chg": rs["CP_4 LW"].diff(12), "r* LW | FRB/US EP_4 (level)": rs["EP_4 LW"],
        "r* LW | VAR4 CP": vs["CP p4 LW"], "r* LW | VAR4 fwd impetus": vs["forward impetus p4 LW"], "r* LW | VAR4 realized": vs["realized impetus p4 LW"],
        "r* LW | VAR12 CP": vs["CP p12 LW"], "r* LW | VAR12 fwd impetus": vs["forward impetus p12 LW"], "r* LW | VAR12 realized": vs["realized impetus p12 LW"],
        "r* LW | MKT (level)": vs["EP LW"]}
    st = "1976-03"   # common start: FCI-G 3yr and 12-month changes of CP are available
    pd.set_option("display.width", 230)
    print(f"common sample {st}..2026-09 (targets); u-only residual sd at L=4 and L=1 printed with each table\n")
    print("correlation of the smoothed indexes with FCI-G 1yr (same case), 1976-2026:")
    for case, f in (("real", fr["1yr all real"]), ("r* LW", rs["FCI-G 1yr LW"])):
        print("   " + case + ": " + ", ".join(f"{k.split('| ')[1]} {pd.concat([x, f], axis=1).loc[st:].corr().iloc[0, 1]:+.2f}" for k, x in IDX.items() if k.startswith(case + " |") and "FCI-G 1yr" not in k))
    for L in (4, 1):
        rows = [dict(index=k, **run(u, x, st, L)) for k, x in IDX.items()]
        T = pd.DataFrame(rows).set_index("index")
        J = D.design(u, None, 12).loc[st:"2026-09"].dropna() if L == 4 else None
        print(f"\n===== L = {L} ({'current and 3 lags' if L == 4 else 'current reading only'}); sorted by out-of-sample RMSE ratio =====")
        print(T.sort_values("OOS all").to_string())


if __name__ == "__main__":
    main()
