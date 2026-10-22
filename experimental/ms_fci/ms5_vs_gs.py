"""
Correlation of the five-variable (MS-style) index with the GS FCI, in daily changes (and weekly and monthly), and with the Fed FCI-G since 2020.

The MS-style index is the level index of ms5_level.py (FRED inputs by default), so its daily change is sum_j s_j * d x_j with the FRB/US funds-rate
equivalents s_j. Variants: nominal 10-year, real 10-year, real gap to r*, each at the q4 sensitivities, and the q8 / q12 sensitivities, plus the
index without oil. Both indices are on the same trading-day calendar (the GS file's).

Usage:  python experimental/ms_fci/ms5_vs_gs.py [--source fred|frbus]
Output: experimental/ms_fci/ms5_vs_gs.csv
"""
import os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ms5_level as L

SENS = pd.read_csv(os.path.join(HERE, "frbus_sensitivities.csv"), index_col=0)


def index_variants():
    """Returns ({name: DataFrame of contributions + Total}, GS daily file) for the variants, all on the GS file's trading days."""
    out = {}
    for tag, real10, rstar in (("nominal 10y", False, False), ("real 10y", True, False), ("real gap to r*", False, True)):
        L.REAL10, L.RSTAR = real10, rstar
        X, G = L.build()
        for h in ("q4", "q8", "q12"):
            C = L.level(X, SENS[f"ffr_eq_{h}"].to_dict(), float(SENS.loc["req", "unit_size"]))
            out[f"{tag}, {h}"] = C
        C4 = out[f"{tag}, q4"]
        out[f"{tag}, q4, no oil"] = C4.assign(Total=C4.Total - C4.Oil)
    return out, G


def corr(a, b):
    d = pd.concat([a, b], axis=1).dropna()
    return float(np.corrcoef(d.iloc[:, 0], d.iloc[:, 1])[0, 1]), len(d)


def main():
    variants, G = index_variants()
    gs = G.fci
    rows = []
    periods = (("1990-2026", "1990", "2026"), ("1990-1999", "1990", "1999"), ("2000-2008", "2000", "2008"), ("2009-2019", "2009", "2019"),
               ("2020-2026", "2020", "2026"), ("last 12 months", str((gs.index[-1] - pd.DateOffset(years=1)).date()), "2026"))
    for name, C in variants.items():
        T = C.Total.reindex(gs.index)
        d_ms, d_gs = T.diff(), gs.diff()
        wk = pd.concat([T, gs], axis=1).resample("W-FRI").last().diff()
        mo = pd.concat([T, gs], axis=1).resample("ME").last().diff()
        for pname, a, b in periods:
            r, n = corr(d_ms[a:b], d_gs[a:b])
            rw, _ = corr(wk.iloc[:, 0][a:b], wk.iloc[:, 1][a:b])
            rm, _ = corr(mo.iloc[:, 0][a:b], mo.iloc[:, 1][a:b])
            rows.append(dict(variant=name, period=pname, daily=r, weekly=rw, monthly=rm, n_daily=n))
    R = pd.DataFrame(rows)
    R.to_csv(os.path.join(HERE, "ms5_vs_gs.csv"), index=False, float_format="%.3f")
    show = R[R.variant.isin(["nominal 10y, q4", "real 10y, q4", "real gap to r*, q4", "real gap to r*, q8", "real gap to r*, q12", "real gap to r*, q4, no oil"])]
    print(f"source: {L.SOURCE}; sample through {gs.index[-1].date()}")
    print("\nCorrelation of DAILY changes with the GS FCI:")
    print(show.pivot(index="variant", columns="period", values="daily")[[p[0] for p in periods]].round(2).to_string())
    print("\nWeekly changes:"); print(show.pivot(index="variant", columns="period", values="weekly")[[p[0] for p in periods]].round(2).to_string())
    print("\nMonthly changes:"); print(show.pivot(index="variant", columns="period", values="monthly")[[p[0] for p in periods]].round(2).to_string())

    # components: daily-change correlation of each MS-based term with the matching GS contribution, and share of GS daily variance explained
    C = variants["real gap to r*, q4"]
    comp = {"10-yr": "c_y10", "BBB spread": "c_bbb", "Equities": "c_cape", "Dollar": "c_usd"}
    print("\nMatching components, daily-change correlation (GS contribution vs MS-based term):")
    print({k: round(corr(C[k].diff(), G[v].diff())[0], 3) for k, v in comp.items()})
    # regression of GS daily change on MS daily change
    d = pd.concat([C.Total.diff(), gs.diff()], axis=1).dropna(); d.columns = ["ms", "gs"]
    b = np.polyfit(d.ms, d.gs, 1)[0]
    print(f"slope: GS daily change = {b:.2f} index points per pp of MS-style funds-rate equivalent; R2 {np.corrcoef(d.ms, d.gs)[0, 1] ** 2:.2f}")
    # versus Fed FCI-G daily changes since 2020
    dd = pd.read_csv(os.path.join(ROOT, "fcig_replication_daily.csv"), parse_dates=["date"]).set_index("date")
    print("\nDaily changes since 2020 versus the Fed FCI-G (replication): real gap to r*, q4")
    for k in ("3yr|FCI-G", "1yr|FCI-G"):
        print(f"  {k}: MS-style {corr(C.Total.diff(), dd[k].diff())[0]:+.2f}   GS FCI {corr(gs.diff(), dd[k].diff())[0]:+.2f}")


if __name__ == "__main__":
    main()
