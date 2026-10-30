"""Step 4. The market index's flow: VAR of the unemployment gap and the market index (12 lags main, 4 lags check), yardstick Phi(12), forward impetus.
Output: output/var_phi.csv, output/flow_<case>.csv, Table 2, Figures 2-3."""
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from fci import data, var, report

D = data.load()
u = D.u_gap
N = report.Numbers("var")
rows, phis, bands = [], {}, {}
for case in ("nominal", "real", "rstar", "rstar_kiley"):
    m = data.read(f"indexes_{case}.csv").market
    flow = {}
    for p in (12, 4):
        r, Y, dum = var.fit(u, m, p)
        Phi, se, own = var.response(r)
        gc = r.test_causality("u", ["M"], kind="f")
        if case == "rstar":
            lo, hi = var.bootstrap(r, Y, dum)
            bands[p] = (lo, hi)
            sig = [h for h in range(1, 37) if lo[h] > 0]
            N.add(f"SigFrom{['Twelve','Four'][p == 4]}", sig[0], "{:d}"); N.add(f"SigTo{['Twelve','Four'][p == 4]}", sig[-1], "{:d}")
        phis[f"{case} p{p}"] = Phi
        flow[f"forward_impetus_p{p}"] = var.forward_impetus(m, Phi)
        flow[f"current_pressure_p{p}"] = var.current_pressure(m, Phi)
        rows.append({"case": case, "lags": p, "Granger F": gc.test_statistic, "p-value": gc.pvalue, "Phi(6)": Phi[6], "Phi(12)": Phi[12], "Phi(24)": Phi[24],
                     "t Phi(12)": Phi[12] / se[12]})
    pd.DataFrame(flow).to_csv(data.OUT / f"flow_{case}.csv", float_format="%.4f")
T = pd.DataFrame(rows)
pd.DataFrame(phis).to_csv(data.OUT / "var_phi.csv", float_format="%.5f", index_label="month")
print(T.round(4).to_string())
lab = {"nominal": "Nominal", "real": "Real", "rstar": "r* (baseline)", "rstar_kiley": "r* (Kiley)"}
T2 = T.assign(Step=T.case.map(lab), Lags=T.lags.astype(str)).set_index("Step")[["Lags", "Granger F", "p-value", "Phi(6)", "Phi(12)", "Phi(24)"]]
T2["p-value"] = T2["p-value"].map(lambda x: "<0.0001" if x < 1e-4 else f"{x:.4f}")
report.table("tab2_var", T2, fmt="{:.2f}")
for _, rw in T.iterrows():
    k = {"nominal": "Nom", "real": "Real", "rstar": "Rstar", "rstar_kiley": "RstarKi"}[rw.case] + ("Twelve" if rw.lags == 12 else "Four")
    N.add(f"Phi{k}", rw["Phi(12)"]); N.add(f"GrangerF{k}", rw["Granger F"]); N.add(f"GrangerP{k}", rw["p-value"], "{:.4f}")

# Figure 2: unemployment response, r* baseline
fig, ax = plt.subplots(figsize=(7, 3.8))
h = np.arange(37)
ax.fill_between(h, *bands[12], color=report.COLORS["market"], alpha=0.18, lw=0)
ax.plot(h, phis["rstar p12"], color=report.COLORS["market"], lw=1.8, label="12 lags (baseline), 95% bootstrap band")
ax.plot(h, phis["rstar p4"], color=report.COLORS["market"], lw=1.2, ls="--", label="4 lags")
ax.plot(h, phis["nominal p12"], color=report.COLORS["grey"], lw=1.0, label="nominal market index, 12 lags")
ax.set_xlabel("months after a one-unit tightening of the market index")
report.axes(ax, "unemployment gap, pp")
report.figure("fig2_var_response", fig)

# Figure 3: market index level and flow, r* baseline, with the r* FCI-G
I = data.read("indexes_rstar.csv"); F = data.read("flow_rstar.csv")
t = I.index.to_timestamp()
fig, ax = plt.subplots(2, 1, figsize=(10, 6.5), sharex=True)
ax[0].plot(t, I.market, color=report.COLORS["market"], lw=1.3, label="Market index (level), pp of the 2-year yield")
ax[0].set_title("Level: where financial conditions stand (relative to r*)", fontsize=9)
ax[1].plot(t, F.forward_impetus_p12, color=report.COLORS["market"], lw=1.3, label="Market index forward impetus (12-lag VAR), index units")
a2 = ax[1].twinx()
a2.plot(t, I.fcig_1yr, color=report.COLORS["fcig"], lw=1.0, alpha=0.8, label="FCI-G, 1-year lookback, r* version (right, pp of GDP growth)")
a2.set_ylim(np.array(ax[1].get_ylim()) * 1.0)
ax[1].set_title("Flow: what conditions imply for growth over the next year", fontsize=9)
for a in ax:
    report.axes(a)
a2.legend(frameon=False, fontsize=8, loc="lower left"); a2.spines["top"].set_visible(False)
report.figure("fig3_market_level_flow", fig)
j = pd.concat([F.forward_impetus_p12, I.fcig_1yr], axis=1).loc["1975-01":].dropna()
N.add("CorrFIFcigRstar", j.corr().iloc[0, 1])
N.add("MarketLatestRstar", I.market.iloc[-1]); N.add("FILatestRstar", F.forward_impetus_p12.iloc[-1])
N.write()
