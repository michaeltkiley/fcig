"""
Extract the NY Fed r* series used in the r* sets from the NY Fed's spreadsheets (https://www.newyorkfed.org/research/policy/rstar):
  LW current        Laubach_Williams_current_estimates.xlsx, sheet "data", "One-Sided Estimates" r* (current vintage; filtered with today's data and full-sample parameters)
  LW real-time      Laubach_Williams_real_time_estimates.xlsx: one sheet per vintage (2005q1 ... 2026q2, none for 2020q3-2022q3), each holding the whole history up to the vintage date.
                    Spliced series: 1961Q1-2004Q4 from the first vintage (2005q1) one-sided estimates (as known in 2005, backfill: not real time at each date);
                    2005Q1-2020Q2 and 2022Q4-2026Q2 the final one-sided observation of each vintage (the estimate published at the time: real time);
                    2020Q3-2022Q3 from the 2022q4 vintage one-sided estimates (backfill after the COVID suspension).
                    A flag column says which kind each value is.
  HLW current       Holston_Laubach_Williams_current_estimates.xlsx, sheet "HLW Estimates", US natural rate (r*), "All estimates are one-sided".
Usage: python -I experimental/fci_compare/rstar_ny_fed_extract.py LW_current.xlsx LW_real_time.xlsx HLW_current.xlsx     Output: rstar_series_ny_fed.csv
"""
import os, sys, warnings
import numpy as np, pandas as pd

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    cur_p, rt_p, hlw_p = sys.argv[1:4]
    cur = pd.read_excel(cur_p, sheet_name="data", header=None).iloc[6:, [0, 2]]
    cur = pd.Series(pd.to_numeric(cur[2]).values, index=pd.PeriodIndex(pd.to_datetime(cur[0]), freq="Q"), name="LW_current_onesided")
    h = pd.read_excel(hlw_p, sheet_name="HLW Estimates", header=None).iloc[6:, [0, 10]]
    hlw = pd.Series(pd.to_numeric(h[10]).values, index=pd.PeriodIndex(pd.to_datetime(h[0]), freq="Q"), name="HLW_current_onesided")
    x = pd.ExcelFile(rt_p)
    vint = {}
    for s in x.sheet_names:
        if s == "LW Estimates": continue
        d = x.parse(s, header=None)
        dates = pd.to_datetime(d[0], errors="coerce")
        col = 2 if d.shape[1] == 11 else 6                 # new layout (2022q4 on): r* one-sided in column 2; old layout: column 6
        ok = dates.notna()
        vint[s] = pd.Series(pd.to_numeric(d.loc[ok, col]).values, index=pd.PeriodIndex(dates[ok], freq="Q"))
    rt, flag = {}, {}
    first, resume = vint["2005q1"], vint["2022q4"]
    for q, v in first.items():
        if q < pd.Period("2005Q1", "Q"): rt[q] = v; flag[q] = "backfill: 2005q1 vintage"
    for q, v in resume.items():
        if pd.Period("2020Q3", "Q") <= q <= pd.Period("2022Q3", "Q"): rt[q] = v; flag[q] = "backfill: 2022q4 vintage"
    for s, v in vint.items():
        q = v.index[-1]; rt[q] = float(v.iloc[-1]); flag[q] = "real time"
    rts = pd.Series(rt).sort_index().rename("LW_realtime_spliced"); fl = pd.Series(flag).sort_index().rename("realtime_flag")
    D = pd.concat([cur, rts, fl, hlw], axis=1); D.index.name = "quarter"
    D.to_csv(os.path.join(HERE, "rstar_series_ny_fed.csv"), float_format="%.4f")
    print(D.loc["2004Q3":"2005Q2"].to_string()); print(D.loc["2020Q1":"2020Q4"].to_string()); print(D.loc["2022Q2":"2023Q1"].to_string())
    print(fl.value_counts().to_string())


if __name__ == "__main__":
    main()
