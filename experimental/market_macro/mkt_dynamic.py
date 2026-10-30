"""
Market-index output lens from the two-variable VAR (user's design, 29 Oct 2026), in market-index (interest-rate) units: pp of the 2-year yield per NS unit.
    VAR: unemployment gap and the market index M, 1973-2019 (2020 excluded), 4 lags (BIC), Cholesky with unemployment first (var2_mkt_u.py).
    Phi(m) = unemployment response m months after a 1-unit shock to M (Phi(0) = 0: unemployment reacts with a lag). M's own response stays close to 1
             (1.00, 1.09, 1.05, 0.98 at 0, 6, 12, 24 months), so Phi is close to the response to a sustained 1-unit shift; the response to a shift held
             at exactly 1 (sequence of M shocks) is printed as a check.
    Indexes (monthly, project market index MKT from transmission_v3, 1990-2026, demeaned):
      eventual pressure  EP_mkt(t) = M(t)                                    (by analogy: the market index itself)
      current pressure   CP_mkt(t) = sum_{m=0}^{12} [Phi(m) - Phi(m-1)] / Phi(12) * M(t-m)       (1-year lookback; weights sum to 1; Phi(-1) = 0)
                         = each past change counted with the share of its 12-month effect already realized
      growth impetus     GI_mkt(t) = sum_{m=0}^{11} [Phi(m+12) - Phi(m)] / Phi(12) * dM(t-m)      (FCI-G form, 1-year lookback: unemployment change over the
                         next 12 months implied by the last 12 months of changes, in units of the 12-month effect of a 1-unit shift; positive = tighter)
      realized impetus   CP_mkt(t) - CP_mkt(t-12): the growth effect realized over the past year (contemporaneous impetus)
      identity: because Phi is essentially flat after 12 months, GI_mkt(t) = EP_mkt(t) - CP_mkt(t) (forward impetus = eventual minus current pressure)
    Comparison: FCI-G 1-year lookback / 0.4525 (funds-rate pp), 12-month change of M, macro-model EP_4 and CP_4 (FRB/US).
Usage: python experimental/market_macro/mkt_dynamic.py
Outputs: mkt_dynamic_monthly.csv, mkt_dynamic.png
"""
import os, sys
import numpy as np, pandas as pd
from statsmodels.tsa.api import VAR

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import mkt_output as MO
LL, V = MO.LL, MO.V


def main():
    F = LL.financial()[MO.VARS]
    base = F.loc["1973-01":"2019-12"]
    Ml = pd.Series((F.loc["1973-01":] - base.mean()).values @ MO.W, index=F.loc["1973-01":].index)
    u = V.macro_data(False)["unemployment gap"]
    D = pd.DataFrame({"u": u, "M": Ml}).loc["1973-01":"2019-12"].dropna(); D.index = D.index.to_timestamp()
    r = VAR(D).fit(4)
    oi = r.irf(36).orth_irfs
    sc = oi[0, 1, 1]
    Phi = oi[:, 0, 1] / sc                                  # u response to a 1-unit M shock, months 0..36
    # check: response to M held at exactly 1 (sequence of M shocks, Cholesky impact vector)
    A = r.coefs; p = r.k_ar; L = np.linalg.cholesky(r.sigma_u); imp = L[:, 1] / L[1, 1]
    y = np.zeros((40 + p, 2))
    for t in range(40):
        pred = sum(A[l] @ y[p + t - 1 - l] for l in range(p))
        y[p + t] = pred + imp * (1.0 - pred[1])
    Phi_held = y[p:, 0]
    print("unemployment response to a 1-unit market-index shock (impulse) vs held shift, months 0,3,6,12,18,24:")
    print("   impulse " + "  ".join(f"{Phi[h]:+.3f}" for h in (0, 3, 6, 12, 18, 24)) + "\n   held    " + "  ".join(f"{Phi_held[h]:+.3f}" for h in (0, 3, 6, 12, 18, 24)))
    print(f"yardstick Phi(12) = {Phi[12]:+.3f} pp unemployment per unit (output equivalent {-2 * Phi[12]:+.3f}%)")
    wcp = np.array([Phi[m] - (Phi[m - 1] if m > 0 else 0.0) for m in range(13)]) / Phi[12]
    wgi = np.array([Phi[m + 12] - Phi[m] for m in range(12)]) / Phi[12]
    print("current-pressure lag weights (months 0..12, sum 1): " + " ".join(f"{x:.3f}" for x in wcp))
    print("growth-impetus weights on dM (months 0..11): " + " ".join(f"{x:.3f}" for x in wgi))
    tr = pd.read_csv(os.path.join(ROOT, "experimental", "fci_compare", "transmission_v3_monthly.csv"), index_col=0); tr.index = pd.PeriodIndex(tr.index, freq="M")
    M = tr["MKT"]
    CP = sum(wcp[m] * M.shift(m) for m in range(13))
    dM = M.diff()
    GI = sum(wgi[m] * dM.shift(m) for m in range(12))
    mm = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "macro_model_v3_monthly.csv"), index_col=0); mm.index = pd.PeriodIndex(mm.index, freq="M")
    f1 = pd.read_csv(os.path.join(ROOT, "raw", "fed_monthly_1yr.csv"), parse_dates=["date"]).set_index("date").iloc[:, 0]; f1.index = f1.index.to_period("M")
    rep = pd.read_csv(os.path.join(ROOT, "fcig_replication_monthly.csv")); rep.index = pd.PeriodIndex(rep["month"], freq="M")
    f1 = pd.concat([f1, rep["1yr|FCI-G"].loc[f1.index[-1] + 1:]])
    J = pd.DataFrame({"EP_mkt (market index)": M, "CP_mkt (current pressure, 1yr)": CP, "GI_mkt (growth impetus, 1yr)": GI, "CP_mkt 12m change (realized impetus)": CP.diff(12), "M 12m change": M.diff(12),
                      "FCI-G 1yr / 0.4525": f1 / 0.4525, "EP_4 (FRB/US)": mm["EP_4"], "CP_4 (FRB/US)": mm["CP_4"], "GI_1yr+HP (FRB/US)": mm["GI_1yr+HP"]}).loc["1991-01":"2026-10"]
    J.to_csv(os.path.join(HERE, "mkt_dynamic_monthly.csv"), float_format="%.4f", index_label="month")
    pd.set_option("display.width", 230)
    print("\nsd / latest (market units for *_mkt and M; funds-rate pp for FCI-G and FRB/US indexes):")
    print(pd.DataFrame({"sd": J.std(), "latest": J.ffill().iloc[-1]}).round(2).T.to_string())
    print("\ncorrelations, 1991-2026:\n" + J.corr().round(2).to_string())
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 1, figsize=(13, 10), sharex=True)
    t = J.index.to_timestamp()
    axes[0].plot(t, J.iloc[:, 0], color="#ff7f0e", lw=1.3, label="Eventual pressure: market index")
    axes[0].plot(t, J.iloc[:, 1], color="#1f5fa8", lw=1.3, label="Current pressure (1-year lookback, VAR lags)")
    axes[0].set_title("Market-index output lens: eventual and current pressure (pp of 2-year yield per NS unit)", fontsize=11)
    axes[1].plot(t, J.iloc[:, 2], color="#d62728", lw=1.3, label="Growth impetus from the market index (VAR lags, 1-year lookback)")
    axes[1].plot(t, J.iloc[:, 4], color="black", lw=1.2, label="FCI-G 1-year lookback / 0.4525 (funds-rate pp)")
    axes[1].set_title(f"Growth impetus vs FCI-G (corr {J.iloc[:, 2].corr(J.iloc[:, 4]):.2f})", fontsize=11)
    for ax in axes:
        ax.axhline(0, color="gray", lw=0.8); ax.grid(alpha=0.25); ax.legend(loc="upper right", fontsize=9, frameon=False)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "mkt_dynamic.png"), dpi=130)


if __name__ == "__main__":
    main()
