"""Step 2. Market-index weights from policy news and the market index in each step (nominal, real, r*-gap with Laubach-Williams r*, r*-gap with Kiley r*).
Output: output/market_weights.csv, output/indexes_{nominal,real,rstar,rstar_kiley}.csv (column `market`).
Method of Note A on Note B's announcement sample, with an intercept in the factor scaling and the weight regressions (lib/events.py, FS_QA FS-A75):
the factor and the index each move 1 unit per 1 pp on the 2-year yield in the windows. If the Note A package is present, reports the differences from its files."""
import numpy as np, pandas as pd
from lib import noteA, events
from lib.paths import OUT, ROOT

D = pd.read_csv(OUT / "data_monthly.csv", index_col=0); D.index = pd.PeriodIndex(D.index, freq="M")
ev = events.events()
w, psi, se = events.weights(ev)
I = ev[["UST10Y", "SP500", "DXY"]].values @ w
assert abs(events.slope(ev.UST2Y, ev.ns) - 1) < 1e-10 and abs(events.slope(I, ev.ns) - 1) < 1e-10, "factor or index not in 2-year units"
pd.DataFrame({"weight": w, "response": psi, "se": se}, index=noteA.MARKET_VARS).to_csv(OUT / "market_weights.csv")
# Robustness (information effects): the same GLS weights estimated only on the announcements that pass the Jarocinski-Karadi (2020) sign restriction
# (2-year yield and S&P 500 move in opposite directions in the window); the policy-news factor keeps its full-sample scaling.
jk = (np.sign(ev.UST2Y) * np.sign(ev.SP500) < 0).values
wj, psij, sej = events.weights(ev, jk)
pd.DataFrame({"weight": wj, "response": psij, "se": sej}, index=noteA.MARKET_VARS).assign(events=int(jk.sum())).to_csv(OUT / "market_weights_jk.csv")
print(f"  Jarocinski-Karadi subset: {jk.sum()} of {len(ev)} events; weights", dict(zip(noteA.MARKET_VARS, np.round(wj, 4))))
noteA.market_index(noteA.index_inputs(D, "rstar", "rstar LW"), wj).loc[noteA.START:noteA.END].rename("market").to_csv(OUT / "indexes_rstar_jkw.csv", float_format="%.4f")
print(f"{len(ev)} events {ev.Date.min():%Y-%m-%d} to {ev.Date.max():%Y-%m-%d}; weights", dict(zip(noteA.MARKET_VARS, np.round(w, 4))), "; window slopes on the factor: 2-year 1, index 1")
for name, case, r in (("nominal", "nominal", "rstar LW"), ("real", "real", "rstar LW"), ("rstar", "rstar", "rstar LW"), ("rstar_kiley", "rstar", "rstar Kiley")):
    m = noteA.market_index(noteA.index_inputs(D, case, r), w).loc[noteA.START:noteA.END]
    m.rename("market").to_csv(OUT / f"indexes_{name}.csv", float_format="%.4f")

A = ROOT.parents[2] / "fci_note" / "replication" / "output"
if A.exists():                                       # Note B's weights differ from Note A's by design (sample and intercept; FS-A75): report, do not require equality
    wa = pd.read_csv(A / "market_weights.csv", index_col=0).weight; print("  Note A weights:", dict(zip(wa.index, np.round(wa.values, 4))), "; ratio Note B / Note A:", dict(zip(wa.index, np.round(w / wa.values, 4))))
    for name in ("nominal", "real", "rstar", "rstar_kiley"):
        a = pd.read_csv(A / f"indexes_{name}.csv", index_col=0).market; b = pd.read_csv(OUT / f"indexes_{name}.csv", index_col=0).market
        print(f"  vs Note A indexes_{name}: max abs difference {(a - b).abs().max():.4f}, correlation {a.corr(b):.5f}")

# Four calibrations of the same three assets (companion paper, step 26; data/four_weights.csv): F = market weights from the futures factor (there Note A's
# weights; Note B uses its own, `w`, for F), Y = market weights with the two-year yield as the policy signal, B = FRB/US weights, G = published Goldman Sachs weights.
FW = pd.read_csv(ROOT / "data" / "four_weights.csv", index_col=0)
print("  companion paper's F (Note A) weights vs Note B's: max abs difference", round(float(np.abs(FW.loc["F"].values - w).max()), 4))
# Note B's versions (FS-A75): F = w; Y, B, G each rescaled so that its window loading on the factor is 1 on Note B's sample (2-year units; ratios unchanged).
FW.loc["F"] = w
for k in ("Y", "B", "G"):
    c = events.slope(ev[["UST10Y", "SP500", "DXY"]].values @ FW.loc[k].values, ev.ns); FW.loc[k] = FW.loc[k] / c; print(f"  calibration {k}: window loading {c:.4f} in the companion paper's scale; rescaled to 1")
FW.to_csv(OUT / "four_weights_nb.csv", float_format="%.7f")
for k in ("Y", "B", "G"):
    noteA.market_index(noteA.index_inputs(D, "rstar", "rstar LW"), FW.loc[k].values).loc[noteA.START:noteA.END].rename("market").to_csv(OUT / f"indexes_rstar_cal{k}.csv", float_format="%.4f")
print("  four calibrations: r*-gap indexes written for Y, B, G (F = the baseline index)")
