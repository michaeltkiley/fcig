"""
Check 1 of NOTE_PLAN.md: does the event-window index map into policy-path units outside FOMC event windows?

The index (GSS or NS weights, path_fci_rates_variants.py) is in pp of a year-ahead rate path. If its variation is policy-like it should co-move one-for-one with a market measure of the
expected policy path. Proxy: the 1-year Treasury yield (FRED DGS1; the 2-year DGS2 also shown), which averages expected short rates over the next year (ED4 refers to about 9-12 months ahead).
For horizons h = 1, 5, 21, 63, 126, 252 trading days, on non-overlapping windows, regress the change in the index on the change in the 1-year yield:
    d index_h = a + beta d y1_h + e;   report beta and R2. 'Event' = windows that contain an FOMC event, 'non-event' = windows that do not (h = 1 only).
beta near 1 means the index moves like the expected policy path; R2 says how much of the index variation is policy-path-like. For comparison the same regressions with the
index replaced by its three components are not run; only the total.
Usage: python experimental/path_fci/path_fci_levelmap.py
"""
import os
import numpy as np, pandas as pd
import statsmodels.api as sm
import path_fci as P
import path_fci_gss_ns as Q

HERE, ROOT = P.HERE, P.ROOT


def main():
    ev = P.events(P.USMPD)
    d = ev.dropna(subset=Q.FUT + ["UST2Y"] + list(Q.ENDOG.values())).reset_index(drop=True)
    gss, ns, _, _ = Q.gss_ns(d)
    W = {f: pd.Series(Q.estimate(d, fac, True)[0], index=list(Q.ENDOG)) for f, fac in (("GSS", gss), ("NS", ns))}
    y = {}
    for s in ("DGS1", "DGS2"):
        try:
            y[s] = P.L.get(s)
        except Exception as e:
            print("could not get", s, e)
    evdates = set(ev.Date)
    idxs = {}
    for vlab, (real, rstar) in {"nominal": (False, False), "real": (True, False)}.items():
        P.L.REAL10, P.L.RSTAR = real, rstar
        X, G = P.L.build()
        for f in W:
            idxs[(f, vlab)] = sum(W[f][n] * P.VARS[n][1] * (X[P.VARS[n][0]] - X[P.VARS[n][0]].mean()) for n in W[f].index)
    idx0 = X.index
    rows = []
    for yname, ys in y.items():
        ys = ys.reindex(idx0).ffill()
        for (f, vlab), s in idxs.items():
            for h in (1, 5, 21, 63, 126, 252):
                pos = np.arange(0, len(idx0) - h, h)          # non-overlapping windows
                a, b = idx0[pos], idx0[pos + h]
                dy = ys.values[pos + h] - ys.values[pos]
                di = s.values[pos + h] - s.values[pos]
                has = np.array([any((e > x0) and (e <= x1) for e in evdates) for x0, x1 in zip(a, b)]) if h <= 5 else np.zeros(len(pos), bool)
                groups = [("all", np.ones(len(pos), bool))] + ([("event", has), ("non-event", ~has)] if h <= 5 else [])
                for g, m in groups:
                    ok = m & ~np.isnan(dy) & ~np.isnan(di)
                    if ok.sum() < 20: continue
                    r = sm.OLS(di[ok], sm.add_constant(dy[ok])).fit(cov_type="HC1")
                    rows.append(dict(yield_=yname, index=f"{f} {vlab}", h=h, windows=g, n=int(ok.sum()), beta=r.params[1], se=r.bse[1], R2=r.rsquared))
    R = pd.DataFrame(rows)
    R.round(3).to_csv(os.path.join(HERE, "path_fci_levelmap.csv"), index=False)
    pd.set_option("display.width", 200)
    for yname in y:
        for idxn in ("GSS nominal", "GSS real", "NS nominal", "NS real"):
            t = R[(R.yield_ == yname) & (R["index"] == idxn)]
            print(f"\n{idxn} index vs change in the {yname} yield:")
            print(t[["h", "windows", "n", "beta", "se", "R2"]].round(2).to_string(index=False))
    # levels
    print("\nLevels (daily, 1990-2026): correlation of the index with the 1-year / 2-year yield level, and slope")
    for (f, vlab), s in idxs.items():
        out = []
        for yname, ys in y.items():
            ys = ys.reindex(idx0).ffill(); ok = ys.notna()
            r = sm.OLS(s[ok], sm.add_constant(ys[ok])).fit()
            out.append(f"{yname}: corr {np.corrcoef(s[ok], ys[ok])[0, 1]:.2f}, slope {r.params.iloc[1]:.2f}")
        print(f"  {f} {vlab}: " + "; ".join(out))


if __name__ == "__main__":
    main()
