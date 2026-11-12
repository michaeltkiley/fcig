from common import *
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
P = pd.read_csv(OUT / "weight_paths.csv", parse_dates=["date"]); BB = pd.read_csv(OUT / "weight_path_bands.csv", parse_dates=["date"])
B = pd.read_csv(RES / "weights_boot.csv"); base = pd.read_csv(RES / "market_weights.csv", index_col=0).weight.values
fig, ax = plt.subplots(2, 2, figsize=(11, 7.5), sharex=True)
for k, (nm, lab) in enumerate((("ten", "Weight on the 10-year yield"), ("eq", "Weight on equity valuation (CAPE)"), ("usd", "Weight on the real dollar"), ("load", "Scale of the policy-news factor (2-year pp per unit of raw factor)"))):
    a = ax.flat[k]
    if k < 3:
        lo, hi = np.percentile(B[f"w_{nm}"], [5, 95]); a.axhspan(lo, hi, color="0.88", label="baseline 90% bootstrap band"); a.axhline(base[k], color="0.4", lw=1, ls=":")
    for wt, col, off in (("expanding", "C0", -40), ("rolling20", "C3", 40)):
        q = P[(P.window == wt) & (P.n >= MIN_N)]; y = q[f"w_{nm}"] if k < 3 else q["load"]
        a.plot(q.date, y, color=col, lw=1.3, label={"expanding": "expanding window", "rolling20": "20-year rolling window"}[wt])
        b = BB[BB.window == wt]; a.errorbar(b.date + pd.Timedelta(days=off), b[f"{nm}_pt"], yerr=[b[f"{nm}_pt"] - b[f"{nm}_lo"], b[f"{nm}_hi"] - b[f"{nm}_pt"]], fmt="none", ecolor=col, alpha=.5, lw=1, capsize=1.5)
    a.set_title(lab, fontsize=10); a.axvline(pd.Timestamp("2010-12-31"), color="k", lw=.5, ls="--")
ax[0, 0].legend(fontsize=8, loc="upper right")
fig.text(.01, .005, "Bars: 90% announcement-bootstrap intervals (500 draws) of each window's estimate at year ends. Dashed line: 2010. Dotted: full-sample weight.", fontsize=8)
fig.tight_layout(rect=(0, .02, 1, 1)); fig.savefig(OUT / "weight_path.png", dpi=150)
