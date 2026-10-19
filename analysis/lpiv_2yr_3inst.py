"""
Local-projection IV on the 2-year yield (as lpiv_2yr.py) with a third instrument: the FOMC-window change in the 10-year
yield (USMPD UST10Y, summed within the month), alongside the target and path surprises.

Instrument sets: target+path+10y (baseline here), 10y alone, path+10y. Per +25 bp in the 2-year yield; same controls
(3 lags of the monthly FCI change and of all three instrument series) and HAC errors as lpiv_2yr.py.
Caveat: the 10-year event change is highly correlated with path (it is largely the same news), so the third instrument
adds relevance but also leans harder on the exclusion restriction (a 10-year surprise must affect the FCI only through the
2-year yield).

Usage:  python analysis/lpiv_2yr_3inst.py [path/to/USMPD.xlsx]
Outputs: analysis/lpiv3_results.csv, analysis/lpiv3_irf.png
"""
import os, sys
import numpy as np, pandas as pd

import lp_surprises as L
import lpiv_2yr as I


def main():
    d = L.usmpd(sys.argv[1] if len(sys.argv) > 1 else None)
    y = L.monthly_y()
    ev, *_ = L.factors(d, "orth")
    ev["ev10y"] = d["UST10Y"].values
    s = ev.assign(m=ev.Date.dt.to_period("M")).groupby("m")[["target", "path", "ev10y"]].sum().reindex(y.index).fillna(0.0)
    s = s[s.index >= "1994-01"]
    y = y.loc[s.index]
    last_full = y.index[-1] - 1 if pd.Timestamp.today().to_period("M") == y.index[-1] else y.index[-1]
    y, s = y.loc[:last_full], s.loc[:last_full]
    x = I.dgs2().reindex(y.index).diff()
    print("corr of monthly shocks:\n", s.corr().round(2).to_string())
    zlb = pd.Series(False, index=y.index)
    for a, b in L.ZLB:
        zlb |= (y.index >= pd.Period(a, "M")) & (y.index <= pd.Period(b, "M"))

    sets = (("target+path+10y", ["target", "path", "ev10y"]), ("path+10y", ["path", "ev10y"]), ("10y", ["ev10y"]))
    out, dg = [], []
    for smp, mask in (("full", None), ("ex-ZLB", ~zlb)):
        for name, inst in sets:
            r, g = I.lpiv(y, s, x, inst, mask)
            r["coef"] *= 0.25
            r["se"] *= 0.25
            out.append(r.assign(sample=smp, instruments=name))
            dg.append(g.assign(sample=smp, instruments=name))
    res, diag = pd.concat(out), pd.concat(dg)
    res.to_csv(os.path.join(L.HERE, "lpiv3_results.csv"), index=False, float_format="%.5f")

    chk = res.pivot_table(index=["sample", "instruments", "h"], columns="series", values="coef")
    print("max |sum of components - FCI| =", float((chk[L.COMP].sum(axis=1) - chk["fci"]).abs().max()))
    print("\nFirst-stage F (robust); over-identification p at h=0/6/12:")
    for (smp, inst), gg in diag.groupby(["sample", "instruments"], sort=False):
        gg = gg.set_index("h")
        print(f"  {smp:7s} {inst:16s} F={gg.loc[0, 'first_stage_F']:.1f} n={int(gg.loc[0, 'n'])}"
              + (f"  overid p: {gg.loc[0, 'J_p']:.2f}/{gg.loc[6, 'J_p']:.2f}/{gg.loc[12, 'J_p']:.2f}" if len(inst.split('+')) > 1 else ""))
    print("\nFCI response per +25 bp in the 2-year yield (index points; t-stat):")
    for smp in ("full", "ex-ZLB"):
        for name, _ in sets:
            r = res[(res["sample"] == smp) & (res.instruments == name) & (res.series == "fci") & res.h.isin([0, 3, 6, 9, 12])]
            print(f"  {smp:7s} {name:16s}", "  ".join(f"h={int(h)}: {c:+.2f} ({c / e:+.1f})" for h, c, e in zip(r.h, r.coef, r.se)))
    I.LABEL_X = "2-yr"
    I.plot(res[res.instruments == "target+path+10y"], name="lpiv3_irf.png")


if __name__ == "__main__":
    main()
