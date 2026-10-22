"""
Changes in the GSS-path and Nakamura-Steinsson indexes (path_fci_rates_variants.py: nominal, real and r*-gap 10-year versions) between two dates and the latest day,
total and by component (10-year, equities, dollar). Weights as in path_fci_rates_variants.py (full covariance, estimated once from the event window).
Usage:  python experimental/path_fci/path_fci_changes.py [date ...]     (default 2026-02-27 2026-08-27)
"""
import os, sys
import numpy as np, pandas as pd
import path_fci as P
import path_fci_gss_ns as Q

HERE, ROOT = P.HERE, P.ROOT


def main():
    dates = sys.argv[1:] or ["2026-02-27", "2026-08-27"]
    ev = P.events(P.USMPD)
    d = ev.dropna(subset=Q.FUT + ["UST2Y"] + list(Q.ENDOG.values())).reset_index(drop=True)
    gss, ns, _, _ = Q.gss_ns(d)
    W = {f: pd.Series(Q.estimate(d, fac, True)[0], index=list(Q.ENDOG)) for f, fac in (("GSS path", gss), ("NS news", ns))}
    sens = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "frbus_sensitivities.csv"), index_col=0)
    req = float(sens.loc["req", "unit_size"])
    rows = []
    for vlab, (real, rstar) in {"nominal": (False, False), "real": (True, False), "r* gap": (False, True)}.items():
        P.L.REAL10, P.L.RSTAR = real, rstar
        X, G = P.L.build()
        last = X.index[-1]
        ms = P.L.level(X, sens["ffr_eq_q4"].to_dict(), req)
        for f, w in W.items():
            comp = pd.DataFrame({n: w[n] * P.VARS[n][1] * X[P.VARS[n][0]] for n in w.index})
            for dt in dates:
                i0 = X.index[X.index.get_indexer([pd.Timestamp(dt)], method="pad")[0]]
                dc = comp.loc[last] - comp.loc[i0]
                rows.append(dict(index=f, tenyr=vlab, start=i0.date(), total=dc.sum(), **{k.split(" (")[0]: v for k, v in dc.items()}))
        for dt in dates:
            i0 = X.index[X.index.get_indexer([pd.Timestamp(dt)], method="pad")[0]]
            dc = ms.loc[last] - ms.loc[i0]
            rows.append(dict(index="MS FRB/US", tenyr=vlab, start=i0.date(), total=dc.Total, **{"10-yr": dc["10-yr"], "Equities": dc.Equities, "Dollar": dc.Dollar, "BBB+oil": dc["BBB spread"] + dc.Oil}))
        if vlab == "nominal":
            for dt in dates:
                i0 = X.index[X.index.get_indexer([pd.Timestamp(dt)], method="pad")[0]]
                rows.append(dict(index="GS FCI (index pts)", tenyr="-", start=i0.date(), total=G.fci.loc[last] - G.fci.loc[i0]))
        raw = {n: P.VARS[n][1] * (X[P.VARS[n][0]].iloc[-1] - X[P.VARS[n][0]].loc[X.index[X.index.get_indexer([pd.Timestamp(dates[0])], method='pad')[0]])) for n in W['GSS path'].index}
        print(f"[{vlab}] change since {dates[0]} in the inputs (10-yr pp, 100 ln CAPE, 100 ln real dollar): " + ", ".join(f"{k.split(' (')[0]} {v:+.2f}" for k, v in raw.items()), f"(to {last.date()})")
    R = pd.DataFrame(rows)
    pd.set_option("display.width", 200)
    print(R.round(2).to_string(index=False))


if __name__ == "__main__":
    main()
