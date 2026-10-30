"""Step 7. Appendix: current pressure (Figure A1) and the checks: Kiley r* and the 4-lag VAR (Table A1)."""
import pandas as pd
import matplotlib.pyplot as plt
from fci import data, compare as K, report

N = report.Numbers("appendix")
I = data.read("indexes_rstar.csv"); F = data.read("flow_rstar.csv")
t = I.index.to_timestamp()
fig, ax = plt.subplots(figsize=(10, 3.8))
ax.plot(t, I.market, color=report.COLORS["market"], lw=1.3, label="Market index (eventual pressure)")
ax.plot(t, F.current_pressure_p12, color=report.COLORS["frbus"], lw=1.1, label="Current pressure (part already passed through)")
ax.plot(t, F.forward_impetus_p12, color=report.COLORS["fcig"], lw=1.0, label="Forward impetus (still to come over the next year)")
report.axes(ax, "pp of the 2-year yield")
report.figure("figA1_current_pressure", fig)
lag = K.corr(I.market, F.current_pressure_p12)
N.add("CorrLevelCP", lag)

Ik = data.read("indexes_rstar_kiley.csv"); Fk = data.read("flow_rstar_kiley.csv")
rows = {}
for c, lab in (("market", "Market index"), ("gs", "GS"), ("frbus", "FRB/US index"), ("fcig_1yr", "FCI-G, 1-year")):
    rows[lab] = {"Kiley vs LW, levels": K.corr(I[c], Ik[c]), "Kiley vs LW, 12-month changes": K.corr(I[c], Ik[c], True)}
rows["Market forward impetus"] = {"Kiley vs LW, levels": K.corr(F.forward_impetus_p12, Fk.forward_impetus_p12), "Kiley vs LW, 12-month changes": float("nan")}
rows["Forward impetus, 4 vs 12 lags"] = {"Kiley vs LW, levels": K.corr(F.forward_impetus_p12, F.forward_impetus_p4), "Kiley vs LW, 12-month changes": float("nan")}
T = pd.DataFrame(rows).T
T.columns = ["Levels", "12-month changes"]
report.table("tabA1_checks", T, fmt="{:.2f}")
print(T.round(2))
N.add("KileyMarketCorr", rows["Market index"]["Kiley vs LW, levels"]); N.add("FourTwelveCorr", rows["Forward impetus, 4 vs 12 lags"]["Kiley vs LW, levels"])
N.write()
