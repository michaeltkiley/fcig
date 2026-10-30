"""
Long monthly data for the real case (REAL_QA.md R5-R6), 1973-01..latest.
Project series (end-of-month, from 1990; macro_model_dl.levels_data, demeaned levels) are extended back to 1973 with long monthly-average series, each
level-matched to the project series by the mean difference over 1990-01..1992-12:
    policy rate      FEDFUNDS                       10-year         GS10
    mortgage spread  MORTGAGE30US (monthly mean) - GS10              BBB spread      BAA - GS10 (Moody's)
    equities         100 ln Shiller CAPE (raw/shiller_cape.csv)      dollar          100 ln real broad dollar (TWEXBPA, spliced to RTWEXBGS)
    house prices     100 ln [Shiller real home price x CPI / CPI rent of primary residence (CUUR0000SEHA)]  (raw/shiller_home_price.csv, CPIAUCSL)
Real rates (R3): real policy rate = policy rate - einf_1y; real 10-year = 10-year - einf_10y (expinf.py). Spreads are not deflated.
Output columns: nominal and real versions of the two rates, the other variables, the expected-inflation series, and a flag for the long-series months.
Usage: python experimental/real_case/data_long.py
Output: data_long_monthly.csv
"""
import os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "experimental", "ms_fci"))
sys.path.insert(0, os.path.join(ROOT, "experimental", "fci_compare"))
sys.path.insert(0, HERE)
import macro_model_dl as DL
import mf_var_us_long as LL
import expinf as EI

OVERLAP = slice("1990-01", "1992-12")


def fm(name):
    s = LL.V.fred_m(name).resample("MS").mean(); s.index = s.index.to_period("M"); return s


def long_series():
    F = LL.financial()                         # policy rate, 10-year, mortgage spread, Baa spread, equities (100 ln CAPE), dollar (100 ln real broad)
    hp = pd.read_csv(os.path.join(ROOT, "raw", "shiller_home_price.csv")); hp.index = pd.PeriodIndex(hp.month, freq="M"); hp = hp.real_home_price
    cpi = fm("CPIAUCSL"); rent = fm("CUUR0000SEHA")
    hpr = 100 * np.log(hp * cpi.reindex(hp.index) / rent.reindex(hp.index))
    return pd.DataFrame({"policy rate": F["policy rate"], "10-year": F["10-year"], "mortgage spread": F["mortgage spread"], "BBB spread": F["Baa spread"],
                         "equities": F["equities"], "dollar": F["dollar"], "house prices": hpr})


def build():
    x, _ = DL.levels_data()                    # project series, demeaned, from 1990
    L = long_series()
    out, info = {}, {}
    for c in x.columns:
        p = x[c].dropna(); l = L[c].dropna()
        k = float((p.loc[OVERLAP] - l.loc[OVERLAP]).mean())
        s = pd.concat([l.loc[:p.index[0] - 1] + k, p])
        out[c] = s; info[c] = (k, float((p.loc[OVERLAP] - l.loc[OVERLAP] - k).std()))
    D = pd.DataFrame(out).loc["1973-01":]
    E = pd.read_csv(os.path.join(HERE, "expinf_monthly.csv"), index_col=0); E.index = pd.PeriodIndex(E.index, freq="M")
    D["einf_1y"] = E.einf_1y.reindex(D.index); D["einf_10y"] = E.einf_10y.reindex(D.index)
    # the project series are demeaned, so the nominal levels carry an unknown constant; restore it from the long series (mean over the overlap)
    for c, raw in (("policy rate", L["policy rate"]), ("10-year", L["10-year"])):
        D[c] = D[c] + float((raw.loc[OVERLAP] - x[c].loc[OVERLAP]).mean())
    D["real policy rate"] = D["policy rate"] - D.einf_1y
    D["real 10-year"] = D["10-year"] - D.einf_10y
    D["long_series"] = (D.index < x.index[0]).astype(int)
    return D, info


def main():
    D, info = build()
    for c, (k, sd) in info.items():
        print(f"{c:16s} level shift {k:+8.3f}; residual sd of the difference over 1990-92 {sd:.3f}")
    D.to_csv(os.path.join(HERE, "data_long_monthly.csv"), float_format="%.4f", index_label="month")
    print(D.loc[["1973-01", "1980-01", "1989-12", "1990-01", "2000-01", "2026-09"], ["policy rate", "real policy rate", "10-year", "real 10-year", "BBB spread", "house prices"]].round(2).to_string())


if __name__ == "__main__":
    main()
