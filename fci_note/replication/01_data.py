"""Step 1. Build the monthly data set (output/data_monthly.csv) and Figure 1 (expected inflation and r*)."""
import matplotlib.pyplot as plt
from fci import data, report

D = data.build()
D.to_csv(data.OUT / "data_monthly.csv", float_format="%.5f")
print(f"monthly data {D.index[0]}..{D.index[-1]}, {D.shape[1]} series")

N = report.Numbers("data")
N.add("EinfOneSeventyFour", D.einf_1y.loc["1974-01":"1974-12"].mean())
N.add("EinfOneEightyOne", D.einf_1y.loc["1981-01":"1981-12"].mean())
N.add("EinfOneLatest", D.einf_1y.iloc[-1])
N.add("RstarLWSeventies", D["rstar LW"].loc["1973-01":"1979-12"].mean())
N.add("RstarLWPreGFC", D["rstar LW"].loc["1990-01":"2007-12"].mean())
N.add("RstarLWPostGFC", D["rstar LW"].loc["2009-01":"2016-12"].mean())
N.add("RstarLWLatest", D["rstar LW"].iloc[-1])
N.add("RstarKiPostGFC", D["rstar Kiley"].loc["2009-01":"2016-12"].mean())
N.write()

fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
t = D.loc["1973-01":].index.to_timestamp()
X = D.loc["1973-01":]
ax[0].plot(t, X.einf_1y, color=report.COLORS["market"], lw=1.2, label="1-year expected inflation")
ax[0].plot(t, X.einf_10y, color=report.COLORS["frbus"], lw=1.2, label="10-year expected inflation")
ax[0].axvspan(t[(X.index >= "1982-01").argmax()], t[(X.index >= "1982-12").argmax()], color="#dddddd", lw=0)
ax[0].set_title("Expected inflation (Livingston before 1982, Cleveland Fed after)", fontsize=9)
ax[1].plot(t, X["rstar LW"], color="black", lw=1.2, label="Laubach-Williams (baseline)")
ax[1].plot(t, X["rstar Kiley"], color=report.COLORS["grey"], lw=1.2, label="Kiley (check)")
ax[1].set_title("r* (one-sided estimates)", fontsize=9)
for a in ax:
    report.axes(a, "percent")
report.figure("fig1_inflation_rstar", fig)
