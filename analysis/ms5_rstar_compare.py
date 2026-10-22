"""
Chart: the MS-style level index with the nominal 10-year (default), the real 10-year, and the real 10-year gap to r* (Kiley), plus the underlying rates.

Panels: (1) the three versions of the total; (2) the 10-year term in each version (funds-rate pp); (3) nominal 10-year, expected inflation (Cleveland Fed),
real 10-year and Kiley's r* (one-sided, as used, and two-sided for reference). Output: analysis/ms5_rstar_compare.png
"""
import os, sys
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ms5_level as L

SENS = pd.read_csv(os.path.join(HERE, "frbus_sensitivities.csv"), index_col=0)
S = SENS["ffr_eq_q4"].to_dict()
KREQ = float(SENS.loc["req", "unit_size"])

out = {}
for name, real10, rstar in (("nominal 10-year (default)", False, False), ("real 10-year", True, False), ("real 10-year gap to r*", False, True)):
    L.REAL10, L.RSTAR = real10, rstar
    X, G = L.build()
    out[name] = L.level(X, S, KREQ)
L.REAL10, L.RSTAR = False, False
X, G = L.build()
r2 = pd.read_csv(os.path.join(L.ROOT, "history", "kiley_rstar.csv"), index_col=0)["rstar_2side"]
r2.index = pd.PeriodIndex(r2.index, freq="Q").to_timestamp() + pd.Timedelta(days=45)
r2d = r2.reindex(r2.index.union(X.index)).interpolate("time").reindex(X.index).ffill().bfill()

n, rl, rs = out["nominal 10-year (default)"], out["real 10-year"], out["real 10-year gap to r*"]
c = {"nominal": "#1f77b4", "real": "#2ca02c", "rstar": "#d62728"}
fig, ax = plt.subplots(3, 1, figsize=(12, 11.5), sharex=True, gridspec_kw={"height_ratios": [1.2, 1, 1.2]})
a = ax[0]
a.plot(n.index, n.Total, color=c["nominal"], lw=0.9, label="nominal 10-year (default)")
a.plot(rl.index, rl.Total, color=c["real"], lw=0.9, ls="--", label="real 10-year (less Cleveland Fed expected inflation)")
a.plot(rs.index, rs.Total, color=c["rstar"], lw=0.9, label="real 10-year gap to r* (Kiley)")
a.axhline(0, color="k", lw=0.5)
dn, dr = n.Total.diff().dropna(), rs.Total.diff().dropna()
a.set_ylabel("pp of funds rate vs 1990-2026 average"); a.legend(fontsize=8, frameon=False, loc="upper right")
a.set_title("Total index: with and without the real-rate / r* adjustment of the 10-year (other four components identical)", fontsize=10, loc="left")
a.text(0.01, 0.04, "correlation nominal vs r*-gap: levels %+.2f, daily changes %+.3f; latest (20 Oct): nominal %+.2f, real %+.2f, r*-gap %+.2f"
       % (np.corrcoef(n.Total, rs.Total)[0, 1], np.corrcoef(dn.align(dr, join="inner")[0], dn.align(dr, join="inner")[1])[0, 1], n.Total.iloc[-1], rl.Total.iloc[-1], rs.Total.iloc[-1]), transform=a.transAxes, fontsize=9)
b = ax[1]
b.plot(n.index, n["10-yr"], color=c["nominal"], lw=0.9, label="10-year term, nominal")
b.plot(rl.index, rl["10-yr"], color=c["real"], lw=0.9, ls="--", label="10-year term, real")
b.plot(rs.index, rs["10-yr"], color=c["rstar"], lw=0.9, label="10-year term, real gap to r*")
b.axhline(0, color="k", lw=0.5); b.set_ylabel("pp of funds rate"); b.legend(fontsize=8, frameon=False, loc="upper right")
b.set_title("The 10-year component (sensitivity 0.57 pp of funds rate per pp, deviation from each version's own 1990-2026 mean)", fontsize=10, loc="left")
d = ax[2]
d.plot(X.index, X.y10, color=c["nominal"], lw=0.9, label="nominal 10-year yield (FRED DGS10)")
d.plot(X.index, X.einf, color="#7f7f7f", lw=0.9, label="10-year expected inflation (Cleveland Fed)")
d.plot(X.index, X.real10, color=c["real"], lw=0.9, ls="--", label="real 10-year yield")
d.plot(X.index, X.rstar, color=c["rstar"], lw=1.6, label="r*, Kiley one-sided (used)")
d.plot(X.index, r2d, color=c["rstar"], lw=1.0, ls=":", label="r*, Kiley two-sided (reference)")
d.plot(X.index, X.real10 - X.rstar, color="k", lw=0.8, label="real 10-year minus r*")
d.axhline(0, color="k", lw=0.5); d.set_ylabel("percent"); d.legend(fontsize=7.5, frameon=False, ncol=2, loc="upper right")
d.set_title("Underlying rates", fontsize=10, loc="left")
fig.tight_layout(); fig.savefig(os.path.join(HERE, "ms5_rstar_compare.png"), dpi=140)
print("saved; corr nominal vs r*-gap levels %.3f ; daily changes %.4f" % (np.corrcoef(n.Total, rs.Total)[0, 1], np.corrcoef(*dn.align(dr, join="inner"))[0, 1]))
print("latest: nominal %.2f real %.2f r*-gap %.2f" % (n.Total.iloc[-1], rl.Total.iloc[-1], rs.Total.iloc[-1]))
print("10-yr term latest: nominal %.2f real %.2f r*-gap %.2f" % (n['10-yr'].iloc[-1], rl['10-yr'].iloc[-1], rs['10-yr'].iloc[-1]))
print("level correlation with GS FCI: nominal %.3f real %.3f r*-gap %.3f" % tuple(np.corrcoef(x.Total.reindex(G.index), G.fci)[0, 1] for x in (n, rl, rs)))
