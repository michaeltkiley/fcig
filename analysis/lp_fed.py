"""
The lp_alt.py cases (baseline target/path, Swanson three factors, Nakamura-Steinsson, raw 2-year surprise) with the
replicated Fed FCI-G as the outcome, for the 3-year and 1-year lookbacks, and each of its seven contributions.

Outcome: the month-end FCI-G from fcig_replication_monthly.csv (percentage points of real GDP growth over the next year;
positive = headwind, as for the GS index). The 3-year version weights 12 quarters of past 3-month changes and the 1-year
version only 4, so a one-time level shift in a variable stops entering the 1-year index after about four quarters (a bit
longer for the averaged rates). Responses beyond that horizon therefore reflect later movements in the variables
themselves, not the weights. Same monthly LP as lp_surprises.py (h = 0..12, 3 lags of the monthly FCI-G change and of the shocks, HAC errors),
per +25 bp. The components sum to the FCI-G response.

Usage:  python analysis/lp_fed.py [path/to/USMPD.xlsx]
Outputs: analysis/lp_fed_results.csv and analysis/lp_fed_*.png
"""
import os, sys
import numpy as np, pandas as pd

import lp_surprises as L
import lp_alt as A

HERE = L.HERE
FED = ["FFR", "10Yr Treasury", "Mortgage Rate", "BBB", "Stock Market", "House Prices", "Dollar"]
FLABEL = {"fci": "Fed FCI-G", "FFR": "Fed funds", "10Yr Treasury": "10-yr", "Mortgage Rate": "Mortgage rate", "BBB": "BBB yield",
          "Stock Market": "Stocks", "House Prices": "House prices", "Dollar": "Dollar"}
LOOK = ("3yr", "1yr")


def fed_monthly(k):
    m = pd.read_csv(os.path.join(L.ROOT, "fcig_replication_monthly.csv"), index_col=0)
    y = m[[f"{k}|FCI-G"] + [f"{k}|{c}" for c in FED]]
    y.columns = ["fci"] + FED
    y.index = pd.PeriodIndex(y.index, freq="M")
    return y


def main():
    d = L.usmpd(sys.argv[1] if len(sys.argv) > 1 else None)
    base, *_ = L.factors(d, "orth")
    sw, load, fit = A.swanson(d)
    ev = base.merge(sw, on="Date")
    ev["ns"] = A.ns(d)
    ev["raw2y"] = d["UST2Y"].values
    shocks = ["target", "path", "swanson_ffr", "swanson_fg", "swanson_lsap", "ns", "raw2y"]
    specs = {"baseline": ["target", "path"], "swanson": ["swanson_ffr", "swanson_fg", "swanson_lsap"], "ns": ["ns"], "raw2y": ["raw2y"]}

    parts = []
    for k in LOOK:
        y = fed_monthly(k)
        s = ev.assign(m=ev.Date.dt.to_period("M")).groupby("m")[shocks].sum().reindex(y.index).fillna(0.0)
        s = s[s.index >= "1994-01"]
        y = y.loc[s.index]
        last_full = y.index[-1] - 1 if pd.Timestamp.today().to_period("M") == y.index[-1] else y.index[-1]
        y, s = y.loc[:last_full], s.loc[:last_full]
        zlb = pd.Series(False, index=y.index)
        for a, b in L.ZLB:
            zlb |= (y.index >= pd.Period(a, "M")) & (y.index <= pd.Period(b, "M"))
        for smp, mask in (("full", None), ("ex-ZLB", ~zlb)):
            for spec, cols in specs.items():
                r = L.lp(y, s[cols], mask).assign(sample=smp, spec=spec, lookback=k)
                r["coef"] *= 0.25
                r["se"] *= 0.25
                parts.append(r)
    res = pd.concat(parts)
    res.to_csv(os.path.join(HERE, "lp_fed_results.csv"), index=False, float_format="%.5f")

    chk = res[res["sample"] == "full"].pivot_table(index=["lookback", "spec", "shock", "h"], columns="series", values="coef")
    print("max |sum of components - FCI-G|, full sample =", float((chk[FED].sum(axis=1) - chk["fci"]).abs().max()))
    for k in LOOK:
        for smp in ("full", "ex-ZLB"):
            print(f"\nFed FCI-G ({k}) response per +25 bp, {smp} (pp of GDP growth; t-stat):")
            for spec, cols in specs.items():
                for sh in cols:
                    r = res[(res.lookback == k) & (res["sample"] == smp) & (res.spec == spec) & (res.series == "fci") & (res.shock == sh) & res.h.isin([0, 3, 6, 9, 12])]
                    print(f"  {sh:13s}", "  ".join(f"h={int(h)}: {c:+.2f} ({c / e:+.1f})" for h, c, e in zip(r.h, r.coef, r.se)))
    tag = lambda smp: smp.replace("-", "").lower()
    series = ["fci"] + FED
    for k in LOOK:
        R = res[res.lookback == k]
        A.plot_fci(R, name=f"lp_fed_{k}_overview.png", main_title=f"Fed FCI-G ({k} lookback) response per +25 bp (90% HAC bands)", unit="pp of GDP growth")
        for smp in ("full", "ex-ZLB"):
            A.plot_grid(R[R.spec == "baseline"], ["target", "path"], smp, f"lp_fed_{k}_baseline_{tag(smp)}.png",
                        {"target": "target", "path": "path"}, series=series, series_label=FLABEL, unit="pp of GDP growth")


if __name__ == "__main__":
    main()
