"""Step 2. Market-index weights from policy news and the market index in each step (nominal, real, r*-gap with Laubach-Williams r*, r*-gap with Kiley r*).
Output: output/market_weights.csv, output/indexes_{nominal,real,rstar,rstar_kiley}.csv (column `market`).
If the Note A replication package is present, checks the result against its published files."""
import numpy as np, pandas as pd
from lib import noteA
from lib.paths import OUT, ROOT

D = pd.read_csv(OUT / "data_monthly.csv", index_col=0); D.index = pd.PeriodIndex(D.index, freq="M")
ev = noteA.events()
w, psi, se = noteA.gls_weights(ev[["UST10Y", "SP500", "DXY"]].values, ev.ns.values)
pd.DataFrame({"weight": w, "response": psi, "se": se}, index=noteA.MARKET_VARS).to_csv(OUT / "market_weights.csv")
# Robustness (information effects): the same GLS weights estimated only on the announcements that pass the Jarocinski-Karadi (2020) sign restriction
# (2-year yield and S&P 500 move in opposite directions in the window); the policy-news factor keeps its full-sample scaling.
jk = (np.sign(ev.UST2Y) * np.sign(ev.SP500) < 0).values
wj, psij, sej = noteA.gls_weights(ev.loc[jk, ["UST10Y", "SP500", "DXY"]].values, ev.ns.values[jk])
pd.DataFrame({"weight": wj, "response": psij, "se": sej}, index=noteA.MARKET_VARS).assign(events=int(jk.sum())).to_csv(OUT / "market_weights_jk.csv")
print(f"  Jarocinski-Karadi subset: {jk.sum()} of {len(ev)} events; weights", dict(zip(noteA.MARKET_VARS, np.round(wj, 4))))
noteA.market_index(noteA.index_inputs(D, "rstar", "rstar LW"), wj).loc[noteA.START:noteA.END].rename("market").to_csv(OUT / "indexes_rstar_jkw.csv", float_format="%.4f")
print(f"{len(ev)} events {ev.Date.min():%Y-%m} to {ev.Date.max():%Y-%m}; weights", dict(zip(noteA.MARKET_VARS, np.round(w, 4))))
for name, case, r in (("nominal", "nominal", "rstar LW"), ("real", "real", "rstar LW"), ("rstar", "rstar", "rstar LW"), ("rstar_kiley", "rstar", "rstar Kiley")):
    m = noteA.market_index(noteA.index_inputs(D, case, r), w).loc[noteA.START:noteA.END]
    m.rename("market").to_csv(OUT / f"indexes_{name}.csv", float_format="%.4f")

A = ROOT.parents[2] / "fci_note" / "replication" / "output"
if A.exists():
    bad = 0
    for name in ("nominal", "real", "rstar", "rstar_kiley"):
        a = pd.read_csv(A / f"indexes_{name}.csv", index_col=0).market; b = pd.read_csv(OUT / f"indexes_{name}.csv", index_col=0).market
        d = (a - b).abs().max(); bad += d > 1e-3; print(f"  vs Note A indexes_{name}: max abs difference {d:.5f}")
    wa = pd.read_csv(A / "market_weights.csv", index_col=0).weight; print("  vs Note A weights: max abs difference", float((wa - pd.Series(w, index=wa.index)).abs().max()))
    assert not bad, "market index differs from Note A"
