"""
Local-projection IV: response of the Goldman-style FCI and its five contributions to a monthly change in the 10-year
Treasury yield, instrumented by the FOMC-window changes in the 2-year and 5-year yields (USMPD UST2Y and UST5Y,
summed within the calendar month).

    y_{t+h} - y_{t-1} = a_h + b_h * d10y_t + controls + e_h,     d10y_t = 10y(t) - 10y(t-1), month-end, h = 0..12
    d10y_t instrumented by (d2y_event_t, d5y_event_t)

Controls as in lp_surprises.py but with the 2y/5y event surprises (3 lags of the monthly FCI change and of both).
Per +25 bp in the 10-year yield. Higher FCI = tighter.

Reading it: the 10-year yield is itself 45% of the FCI, so the 10-yr contribution responds mechanically
(0.451 x 0.25 = 0.113 at h = 0); that row is a check on the code, not a finding. The exclusion restriction is also
demanding: a 2y or 5y surprise has to move the other FCI components only through the 10-year yield, which is a strong
assumption for equities and the dollar. The results are the response to a 10-year move that comes with FOMC-window
news at the 2- and 5-year horizons, not to an isolated term-premium shock. Single-instrument versions are reported too.

Usage:  python analysis/lpiv_10yr.py [path/to/USMPD.xlsx]
Outputs: analysis/lpiv10_results.csv, analysis/lpiv10_irf.png
"""
import os, sys
import numpy as np, pandas as pd

import lp_surprises as L
import lpiv_2yr as I

HERE = L.HERE


def main():
    d = L.usmpd(sys.argv[1] if len(sys.argv) > 1 else None)
    y = L.monthly_y()
    g = pd.read_csv(os.path.join(L.ROOT, "fcig_gs_daily.csv"), parse_dates=["date"]).set_index("date")["x_y10"]
    ten = g.groupby(g.index.to_period("M")).last()
    s = d.assign(m=d.Date.dt.to_period("M")).groupby("m")[["UST2Y", "UST5Y"]].sum().reindex(y.index).fillna(0.0)
    s.columns = ["ev2y", "ev5y"]
    s = s[s.index >= "1994-01"]
    y = y.loc[s.index]
    last_full = y.index[-1] - 1 if pd.Timestamp.today().to_period("M") == y.index[-1] else y.index[-1]
    y, s = y.loc[:last_full], s.loc[:last_full]
    x = ten.reindex(y.index).diff()
    zlb = pd.Series(False, index=y.index)
    for a, b in L.ZLB:
        zlb |= (y.index >= pd.Period(a, "M")) & (y.index <= pd.Period(b, "M"))

    out, dg = [], []
    for smp, mask in (("full", None), ("ex-ZLB", ~zlb)):
        for name, inst in (("2y+5y", ["ev2y", "ev5y"]), ("2y", ["ev2y"]), ("5y", ["ev5y"])):
            r, gdiag = I.lpiv(y, s, x, inst, mask)
            r["coef"] *= 0.25   # per +25 bp in the 10-year yield
            r["se"] *= 0.25
            out.append(r.assign(sample=smp, instruments=name))
            dg.append(gdiag.assign(sample=smp, instruments=name))
    res, diag = pd.concat(out), pd.concat(dg)
    res.to_csv(os.path.join(HERE, "lpiv10_results.csv"), index=False, float_format="%.5f")

    chk = res[res["sample"] == "full"].pivot_table(index=["sample", "instruments", "h"], columns="series", values="coef")
    print("max |sum of components - FCI|, full sample =", float((chk[L.COMP].sum(axis=1) - chk["fci"]).abs().max()))
    print("10-yr contribution at h=0 (mechanical, expect 0.113):", chk.xs((("full", "2y+5y", 0)))["c_y10"].round(3))
    print("\nFirst-stage F (robust); over-identification p at h=0/6/12:")
    for (smp, inst), gg in diag.groupby(["sample", "instruments"]):
        gg = gg.set_index("h")
        print(f"  {smp:7s} {inst:6s} F={gg.loc[0, 'first_stage_F']:.1f} n={int(gg.loc[0, 'n'])}"
              + (f"  overid p: {gg.loc[0, 'J_p']:.2f}/{gg.loc[6, 'J_p']:.2f}/{gg.loc[12, 'J_p']:.2f}" if inst == "2y+5y" else ""))
    print("\nFCI response per +25 bp in the 10-year yield (index points; t-stat):")
    for smp in ("full", "ex-ZLB"):
        for inst in ("2y+5y", "2y", "5y"):
            r = res[(res["sample"] == smp) & (res.instruments == inst) & (res.series == "fci") & res.h.isin([0, 3, 6, 9, 12])]
            print(f"  {smp:7s} {inst:6s}", "  ".join(f"h={int(h)}: {c:+.2f} ({c / e:+.1f})" for h, c, e in zip(r.h, r.coef, r.se)))
    P = res[res.instruments == "2y+5y"]
    I.LABEL_X = "10-yr"
    I.plot(P, samples=("full",), name="lpiv10_irf.png")   # ex-ZLB first stage is too weak to plot


if __name__ == "__main__":
    main()
