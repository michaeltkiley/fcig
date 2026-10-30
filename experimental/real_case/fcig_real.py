"""
FCI-G replication on monthly data from 1973, nominal and real (REAL_QA R11).
Same weights and lag structure as fcig_replicate.py (Fed multipliers; 3-month changes over 4 or 12 quarters ending at each month), computed on monthly data:
    rates and yields : 3-month average of monthly means minus the previous 3-month average (pp)
    stocks, houses   : 100 * 3-month log change of the month-end level (before 1986, Shiller's monthly-average S&P 500)
    dollar           : 100 * log change of the 3-month average of monthly means
Data: the daily series of fcig_replicate.series() (FFR DFF, 10-year DGS10, mortgage PMMS, BBB ICE yield spliced to DBAA, Dow Jones total market /
    S&P 500, Zillow / Case-Shiller, nominal broad dollar back to TWEXBMTH 1973), extended before their starts with: BBB <- Moody's BAA (monthly, difference
    splice), stocks <- Shiller S&P 500 (raw/shiller_sp500.csv, level splice), houses <- Shiller real home price x CPIAUCSL (level splice).
Real version (R11, option 3): each rate minus matched expected inflation (expinf_monthly.csv): funds rate - einf_1y; 10-year, mortgage, BBB - einf_10y.
    Stocks, house prices and dollar unchanged (as published: nominal).
Check: nominal monthly version vs the published FCI-G (raw/fed_monthly_1yr.csv, 3yr) and the daily replication.
Usage: python experimental/real_case/fcig_real.py
Output: fcig_real_monthly.csv
"""
import os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
import fcig_replicate as FR


def mp(s, how="mean"):
    g = s.groupby(s.index.to_period("M"))
    return g.mean() if how == "mean" else g.last()


def monthly():
    S, _ = FR.series()
    M = {}
    for c, (kind, s) in S.items():
        M[c] = mp(s, "last" if kind == "loglevel" else "mean")
    baa = mp(FR.fred("BAA"))
    b = M["BBB"]; M["BBB"] = pd.concat([baa.loc[:b.index[0] - 1] + float(b.iloc[0] - baa.loc[b.index[0]]), b])
    sp = pd.read_csv(os.path.join(ROOT, "raw", "shiller_sp500.csv")); sp = pd.Series(sp.sp500.values, index=pd.PeriodIndex(sp.month, freq="M"))
    s = M["Stock Market"]; M["Stock Market"] = pd.concat([sp.loc[:s.index[0] - 1] * float(s.iloc[0] / sp.loc[s.index[0]]), s])
    hp = pd.read_csv(os.path.join(ROOT, "raw", "shiller_home_price.csv")); hp = pd.Series(hp.real_home_price.values, index=pd.PeriodIndex(hp.month, freq="M"))
    hp = hp * mp(FR.fred("CPIAUCSL")).reindex(hp.index)
    h = M["House Prices"]; M["House Prices"] = pd.concat([hp.loc[:h.index[0] - 1] * float(h.iloc[0] / hp.loc[h.index[0]]), h])
    return pd.DataFrame(M).loc["1972-01":]


def changes(M):
    """dX[j] at month t for quarter lag 0 (3-month change ending at t); lags are shifts by 3i months."""
    D = pd.DataFrame(index=M.index)
    for c in FR.COLS:
        if c in ("Stock Market", "House Prices"):
            D[c] = 100 * np.log(M[c]).diff(3)
        else:
            A = M[c].rolling(3).mean()
            D[c] = A.diff(3) if c != "Dollar" else 100 * np.log(A).diff(3)
    return D


def fcig(D, T):
    comp = sum(D.shift(3 * i) * FR.W[i] for i in range(T))
    return comp.sum(axis=1, min_count=len(FR.COLS)), comp


def main():
    M = monthly()
    E = pd.read_csv(os.path.join(HERE, "expinf_monthly.csv"), index_col=0); E.index = pd.PeriodIndex(E.index, freq="M")
    R = M.copy()
    R["FFR"] = M["FFR"] - E.einf_1y.reindex(M.index)
    for c in ("10Yr Treasury", "Mortgage Rate", "BBB"):
        R[c] = M[c] - E.einf_10y.reindex(M.index)
    Dn, Dr = changes(M), changes(R)
    out = {}
    for T, k in ((4, "1yr"), (12, "3yr")):
        out[f"{k} nominal"], _ = fcig(Dn, T)
        out[f"{k} real"], comp = fcig(Dr, T)
        if k == "1yr":
            for c in FR.COLS:
                out[f"1yr real | {c}"] = comp[c]
    O = pd.DataFrame(out).loc["1973-01":"2026-10"]
    O.to_csv(os.path.join(HERE, "fcig_real_monthly.csv"), float_format="%.4f", index_label="month")
    pd.set_option("display.width", 230)
    print("first full months:", {c: str(O[c].first_valid_index()) for c in ("1yr nominal", "3yr nominal")})
    for k in ("1yr", "3yr"):
        f = FR.fed(k).iloc[:, 0]; f.index = pd.PeriodIndex(f.index, freq="M")
        j = pd.concat([O[f"{k} nominal"], f], axis=1).dropna()
        print(f"{k}: monthly nominal version vs published FCI-G {j.index[0]}..{j.index[-1]}: corr {j.corr().iloc[0, 1]:.3f}, sd {j.iloc[:, 0].std():.3f} vs {j.iloc[:, 1].std():.3f}, mean gap {(j.iloc[:, 0] - j.iloc[:, 1]).mean():+.3f}")
        k2 = pd.concat([O[f"{k} real"], O[f"{k} nominal"]], axis=1).dropna()
        print(f"     real vs nominal {k2.index[0]}..: corr {k2.corr().iloc[0, 1]:.3f}; since 1990 {k2.loc['1990-01':].corr().iloc[0, 1]:.3f}; sd real {k2.iloc[:, 0].std():.3f}, nominal {k2.iloc[:, 1].std():.3f}")
    sel = [pd.Period(m, "M") for m in ("1974-06", "1979-12", "1981-06", "1985-01", "1990-01", "2000-01", "2008-12", "2013-01", "2021-06", "2023-10", "2026-09")]
    print(O.loc[sel, ["1yr nominal", "1yr real", "3yr nominal", "3yr real", "1yr real | FFR", "1yr real | 10Yr Treasury", "1yr real | Mortgage Rate", "1yr real | BBB"]].round(2).to_string())
    print("latest:", O.dropna(subset=["1yr real"]).index[-1], O.dropna(subset=["1yr real"]).iloc[-1][["1yr nominal", "1yr real", "3yr real"]].round(2).to_dict())


if __name__ == "__main__":
    main()
