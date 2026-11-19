"""FS-A108: list what changes when the plain percentile intervals are replaced by bias-corrected ones.
   python3 compare_intervals.py OLD_RESULTS_DIR      (writes report/INTERVALS_CHANGE.md)
Compares every case file results/<id>.csv (12-lag rows; u and P at 12, 24, 36 months) with the same file in OLD_RESULTS_DIR: the 90% and 95% significance verdicts
and the size of the shift of the interval."""
import sys
import numpy as np, pandas as pd
import cases as CS
from lib.paths import RESULTS, REPORT
OLD = sys.argv[1]
rows = []
for c in CS.unique_cases():
    i = CS.case_id(c)
    try: a = pd.read_csv(f"{OLD}/{i}.csv"); b = pd.read_csv(RESULTS / f"{i}.csv")
    except FileNotFoundError: continue
    for L in (12, 6):
        for v in ("u", "P"):
            ra = a[(a.lags == L) & (a["var"] == v)].iloc[0]; rb = b[(b.lags == L) & (b["var"] == v)].iloc[0]
            for h in (12, 24, 36):
                s = lambda r, lo, hi: bool(r[lo] * r[hi] > 0)
                rows.append(dict(case=i, lags=L, var=v, h=h, r=rb[f"r{h}"], old_lo=ra[f"lo{h}"], old_hi=ra[f"hi{h}"], new_lo=rb[f"lo{h}"], new_hi=rb[f"hi{h}"],
                                 old10=s(ra, f"lo{h}", f"hi{h}"), new10=s(rb, f"lo{h}", f"hi{h}"), old5=s(ra, f"lo95_{h}", f"hi95_{h}"), new5=s(rb, f"lo95_{h}", f"hi95_{h}"),
                                 shift=(rb[f"lo{h}"] + rb[f"hi{h}"] - ra[f"lo{h}"] - ra[f"hi{h}"]) / 2))
D = pd.DataFrame(rows); ch = D[(D.old10 != D.new10) | (D.old5 != D.new5)]
fmt = lambda x: f"{x:+.2f}"
L = ["# Bias-corrected against plain percentile intervals (FS-A108)", "", f"{len(D)} responses compared (12 and 6 lags; u and P at 12, 24, 36 months; every case). "
     f"Verdict changes at 10 percent: {int((D.old10 != D.new10).sum())} (gained {int((~D.old10 & D.new10).sum())}, lost {int((D.old10 & ~D.new10).sum())}); "
     f"at 5 percent: {int((D.old5 != D.new5).sum())} (gained {int((~D.old5 & D.new5).sum())}, lost {int((D.old5 & ~D.new5).sum())}). "
     f"Median absolute shift of the interval midpoint: {D['shift'].abs().median():.3f}; 90th percentile {D['shift'].abs().quantile(0.9):.3f}.", "",
     "| case | lags | var | h | point | old 90% | new 90% | 10% old→new | 5% old→new |", "|---|---|---|---|---|---|---|---|---|"]
for _, r in ch.sort_values(["lags", "case", "var", "h"], ascending=[False, True, True, True]).iterrows():
    L.append(f"| {r.case} | {r.lags} | {r['var']} | {r.h} | {fmt(r.r)} | [{fmt(r.old_lo)}, {fmt(r.old_hi)}] | [{fmt(r.new_lo)}, {fmt(r.new_hi)}] | {'sig' if r.old10 else 'ns'}→{'sig' if r.new10 else 'ns'} | {'sig' if r.old5 else 'ns'}→{'sig' if r.new5 else 'ns'} |")
(REPORT / "INTERVALS_CHANGE.md").write_text("\n".join(L) + "\n"); D.to_csv(REPORT.parent / "results" / "intervals_compare.csv", index=False, float_format="%.4f"); print("\n".join(L[:3]))
