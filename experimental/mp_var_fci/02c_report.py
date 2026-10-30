"""Step 2c. Summaries and figures from irf_cholesky.csv: bands at key horizons, cross-sample distance (long vs matched) with and without the index, figures.
Output: 02c_report.log, cholesky_u.png, cholesky_price.png, cholesky_funds_index.png, cholesky_cases.png"""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = pd.read_csv("irf_cholesky.csv")
main = R[(R.lags == 12) & (R.order == "ffr_then_index")]


def get(case, window, system, var, order="ffr_then_index", lags=12):
    d = R[(R.case == case) & (R.window == window) & (R.system == system) & (R.variable == var) & (R.order == order) & (R.lags == lags)].sort_values("h")
    return d


print("Unemployment-gap response to +1 pp funds-rate innovation, 95% bootstrap band (lo, hi), r*-gap case, 12 lags")
for window in ("long", "matched"):
    for system in ("without index", "with index"):
        d = get("rstar", window, system, "u_gap")
        print(f"  {window:8s} {system:14s} " + "  ".join(f"h{h}: {d.irf.iloc[h]:+.2f} ({d.lo95.iloc[h]:+.2f},{d.hi95.iloc[h]:+.2f})" for h in (6, 12, 24, 36)))
print("\nFunds-rate and index responses (same shock), with-index system, 95% band")
for case in ("nominal", "real", "rstar"):
    for window in ("long", "matched"):
        v = f"market_{case}"
        d = get(case, window, "with index", v); f = get(case, window, "with index", "ffr")
        print(f"  {case:8s} {window:8s} index h0 {d.irf.iloc[0]:+.2f} ({d.lo95.iloc[0]:+.2f},{d.hi95.iloc[0]:+.2f})  h12 {d.irf.iloc[12]:+.2f} ({d.lo95.iloc[12]:+.2f},{d.hi95.iloc[12]:+.2f}) | funds rate h12 {f.irf.iloc[12]:+.2f} ({f.lo95.iloc[12]:+.2f},{f.hi95.iloc[12]:+.2f}) h36 {f.irf.iloc[36]:+.2f}")

print("\nCross-sample distance of the unemployment response: mean |long - matched| over h = 0..36 (pp of unemployment gap per 1 pp funds rate)")
for case in ("nominal", "real", "rstar"):
    a = get(case, "long", "with index", "u_gap").irf.values[:37]; b = get(case, "matched", "with index", "u_gap").irf.values[:37]
    print(f"  {case:8s} with index   : {np.abs(a - b).mean():.2f}   (long mean |irf| {np.abs(a).mean():.2f}, matched {np.abs(b).mean():.2f})")
a = get("rstar", "long", "without index", "u_gap").irf.values[:37]; b = get("rstar", "matched", "without index", "u_gap").irf.values[:37]
print(f"  without index (system does not depend on the case): {np.abs(a - b).mean():.2f}   (long {np.abs(a).mean():.2f}, matched {np.abs(b).mean():.2f})")
print("Within-sample distance: mean |with index - without index|, r*-gap, h = 0..36")
for window in ("long", "matched"):
    a = get("rstar", window, "with index", "u_gap").irf.values[:37]; b = get("rstar", window, "without index", "u_gap").irf.values[:37]
    print(f"  {window:8s}: {np.abs(a - b).mean():.2f}")
print("Price puzzle check: cumulative core PCE price level response at 24 and 48 months (%, per 1 pp funds rate), r*-gap, with index")
for window in ("long", "matched"):
    d = get("rstar", window, "with index", "pi_core")
    c = np.cumsum(d.irf.values) / 12; lo = np.cumsum(d.lo95.values) / 12; hi = np.cumsum(d.hi95.values) / 12
    print(f"  {window:8s} h24 {c[24]:+.2f} (band of the sum not computed; bound by summed band edges {lo[24]:+.2f},{hi[24]:+.2f})  h48 {c[48]:+.2f}")

C = {"without index": "#8a8a8a", "with index": "#c4501f"}
fig, ax = plt.subplots(1, 2, figsize=(11, 3.8), sharey=False)
for a_, window in zip(ax, ("long", "matched")):
    for system in ("without index", "with index"):
        d = get("rstar", window, system, "u_gap")
        a_.fill_between(d.h, d.lo95, d.hi95, color=C[system], alpha=0.15, lw=0); a_.plot(d.h, d.irf, color=C[system], label=system, lw=1.6)
    a_.axhline(0, color="k", lw=0.6); a_.set_title(f"{window} window ({'1973' if window == 'long' else '1994'}-2026)", fontsize=10); a_.set_xlabel("months after a +1 pp funds-rate innovation")
ax[0].set_ylabel("unemployment gap, pp"); ax[0].legend(frameon=False, fontsize=8)
fig.suptitle("Cholesky: unemployment response (r*-gap index, 12 lags, 95% bootstrap bands)", fontsize=10); fig.tight_layout(); fig.savefig("cholesky_u.png", dpi=140); plt.close(fig)

fig, ax = plt.subplots(2, 2, figsize=(11, 6.2))
for j, window in enumerate(("long", "matched")):
    for case, col in (("nominal", "#4c78a8"), ("real", "#54a24b"), ("rstar", "#c4501f")):
        d = get(case, window, "with index", f"market_{case}"); ax[0, j].plot(d.h, d.irf, color=col, label=case, lw=1.4)
        f = get(case, window, "with index", "ffr"); ax[1, j].plot(f.h, f.irf, color=col, lw=1.4)
    for i in (0, 1):
        ax[i, j].axhline(0, color="k", lw=0.6)
    ax[0, j].set_title(f"{window} window", fontsize=10)
ax[0, 0].set_ylabel("market index (units)"); ax[1, 0].set_ylabel("funds rate, pp"); ax[1, 0].set_xlabel("months"); ax[1, 1].set_xlabel("months"); ax[0, 0].legend(frameon=False, fontsize=8)
fig.suptitle("Cholesky: response of the index and the funds rate to a +1 pp funds-rate innovation", fontsize=10); fig.tight_layout(); fig.savefig("cholesky_funds_index.png", dpi=140); plt.close(fig)

fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
for a_, window in zip(ax, ("long", "matched")):
    for system in ("without index", "with index"):
        d = get("rstar", window, system, "pi_core"); a_.plot(d.h, np.cumsum(d.irf.values) / 12, color=C[system], label=system, lw=1.6)
    a_.axhline(0, color="k", lw=0.6); a_.set_title(f"{window} window", fontsize=10); a_.set_xlabel("months")
ax[0].set_ylabel("core PCE price level, %"); ax[0].legend(frameon=False, fontsize=8)
fig.suptitle("Cholesky: cumulative core PCE price-level response (r*-gap, 12 lags)", fontsize=10); fig.tight_layout(); fig.savefig("cholesky_price.png", dpi=140); plt.close(fig)

# Size of the funds-rate innovation (sd of the orthogonalized shock = impact of a one-sd shock on the funds rate), r*-gap with-index system, 12 lags
import warnings
from statsmodels.tsa.api import VAR
warnings.filterwarnings("ignore")
D = pd.read_csv("data/mp_monthly.csv", index_col=0); D.index = pd.PeriodIndex(D.index, freq="M")
print("\nSize of the funds-rate innovation (one-sd orthogonalized shock, pp) and the unemployment response per one-sd shock at 12 and 24 months")
for window, start in (("long", "1973-01"), ("matched", "1994-01")):
    X = D.loc[start:"2026-09", ["u_gap", "pi_core", "ffr", "market_rstar"]].dropna()
    dum = pd.DataFrame({f"d{k:02d}": (X.index == pd.Period(f"2020-{k:02d}", "M")).astype(float) for k in range(1, 13)}, index=X.index)
    X = X.copy(); X.index = X.index.to_timestamp(); dum.index = X.index
    r = VAR(X, exog=dum).fit(12); sd = r.irf(48).orth_irfs[0, 2, 2]
    u = get("rstar", window, "with index", "u_gap").irf.values
    print(f"  {window:8s} one-sd funds-rate innovation = {sd:.2f} pp;  unemployment gap per one-sd shock: h12 {u[12] * sd:+.2f}, h24 {u[24] * sd:+.2f} pp")
