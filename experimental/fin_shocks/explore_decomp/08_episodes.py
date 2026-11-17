"""Historical decomposition at selected months, r*-gap with FCI: Route 2 (VAR in monthly averages from 1973, window column, 90% band) and Route 1 (Note B's model from 1996
and the measured surprises, 90% band), with the all-shocks component.   python3 08_episodes.py -> results/hd_episodes_rstar_avg1973.csv"""
import numpy as np, pandas as pd
from pathlib import Path
RES = Path(__file__).resolve().parent / "results"
MONTHS = ["1975-05", "1980-12", "1982-12", "1987-12", "1992-06", "2001-12", "2003-06", "2009-10", "2014-12", "2019-12", "2022-12", "2023-12", "2024-12", "2026-09"]
ma = lambda x: pd.Series(x).rolling(12).mean().values

def table(case="rstar_rstar_avg1973_L12_WE_in", boot="boot_hd_rstar_rstar_avg_WE.npz", r1="route1_rstar_rstar_1996.npz"):
    h = pd.read_csv(RES / f"hd_{case}.csv"); B = np.load(RES / boot, allow_pickle=True); R1 = np.load(RES / r1, allow_pickle=True)
    mon = list(B["months"]); m1 = list(R1["months"]); rows = []
    for month in MONTHS:
        out = {"month": month}
        for v, j in (("u", 0), ("pi", 1), ("pol", 2), ("idx", 3)):
            g = h[h["var"] == v].reset_index(drop=True); i = mon.index(month)
            x, xs, d = g.route2.values, g.stochastic.values, B["hd"][:, :, j].astype(float)
            if v == "pi": x, xs, d = ma(x), ma(xs), np.array([ma(r) for r in d])
            out.update({f"{v}_all": xs[i], f"{v}_r2": x[i], f"{v}_r2lo": np.nanpercentile(d[:, i], 5), f"{v}_r2hi": np.nanpercentile(d[:, i], 95)})
            if month in m1:
                k = m1.index(month); p, dd = R1["point"][:, j], R1["draws"][:, :, j].astype(float)
                if v == "pi": p, dd = ma(p), np.array([ma(r) for r in dd])
                out.update({f"{v}_r1": p[k], f"{v}_r1lo": np.nanpercentile(dd[:, k], 5), f"{v}_r1hi": np.nanpercentile(dd[:, k], 95)})
        rows.append(out)
    return pd.DataFrame(rows)

if __name__ == "__main__":
    T = table(); T.to_csv(RES / "hd_episodes_rstar_avg1973.csv", index=False, float_format="%.3f"); print(T.round(2).T.to_string())
