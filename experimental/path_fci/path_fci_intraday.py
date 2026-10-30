"""
EXPERIMENTAL add-on (path_fci.py unchanged): weights from the INTRADAY (USMPD event-window) surprises in the 10-year yield, the S&P 500 and the dollar index,
each regressed individually on the path surprise (controlling for the target surprise), then applied to the daily index data.

    surprise_j,e = a_j + b_j path_e + c_j target_e + u_j,e       j = UST10Y (pp), SP500 (%), DXY (%)
    w_j = (b_j / s_j^2) / sum_k (b_k^2 / s_k^2)                  one-factor GLS weights, so sum_j w_j b_j = 1 (as in path_fci.py)
The weights are estimated once, from the event-window data; they are NOT re-estimated for the real 10-year. The index data are the real series:
    index = sum_j w_j (x_j - mean_j),   x = 10-year yield (nominal or real, DGS10 less Cleveland Fed expected inflation), 100 ln CAPE, 100 ln real dollar
USMPD has no BBB, oil or funds-rate-path series in its window, so the index has these three variables (MS and GS charts therefore show the same index,
each against its own comparator: the MS-style FRB/US-weighted index, and the GS FCI). A 1% S&P move and a 1% DXY move are taken as 1 unit of 100 ln CAPE / 100 ln dollar.

Usage:  python experimental/path_fci/path_fci_intraday.py [--sample full|nonzlb] [--real10]
Outputs: path_fci_intraday_ms_<sample>[_real10].png, path_fci_intraday_gs_<sample>[_real10].png
"""
import os, argparse
import numpy as np, pandas as pd
import statsmodels.api as sm
import path_fci as P

HERE, ROOT = P.HERE, P.ROOT
COLS = {"10-yr": "UST10Y", "Equities (ln CAPE)": "SP500", "Dollar (ln real)": "DXY"}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--sample", default="full", choices=["full", "nonzlb"]); ap.add_argument("--real10", action="store_true")
    ap.add_argument("usmpd", nargs="?", default=P.USMPD)
    a = ap.parse_args()
    ev = P.events(a.usmpd)
    P.L.REAL10 = a.real10
    X, G = P.L.build()
    ev = ev.dropna(subset=list(COLS.values())).reset_index(drop=True)
    if a.sample == "nonzlb":
        ev = ev[~P.in_zlb(ev.Date)].reset_index(drop=True)
    Z = sm.add_constant(ev[["path", "target"]])
    rows = {}
    for n, c in COLS.items():
        r = sm.OLS(ev[c], Z).fit(cov_type="HC1")
        rows[n] = dict(b=r.params["path"], se=r.bse["path"], s2=r.resid.var(ddof=3))
    B = pd.DataFrame(rows).T
    names = list(COLS)
    w = P.weights(B, names)
    print(f"{len(ev)} events ({a.sample}). Intraday responses to a +1 pp path surprise: " + ", ".join(f"{n} {B.b[n]:+.3f} (se {B.se[n]:.3f})" for n in names))
    print("weights (pp of path-rate per unit): " + ", ".join(f"{n} {w[n]:+.3f}" for n in names), "| sum w*b =", round(float((w * B.b).sum()), 3))
    tag = "_real10" if a.real10 else ""
    ten = "real 10-yr" if a.real10 else "10-yr"
    lev = lambda ww, nn: sum(ww[n] * P.VARS[n][1] * (X[P.VARS[n][0]] - X[P.VARS[n][0]].mean()) for n in nn)
    idx = lev(w, names)
    sens = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "frbus_sensitivities.csv"), index_col=0)
    ms_frbus = P.L.level(X, sens["ffr_eq_q4"].to_dict(), float(sens.loc["req", "unit_size"])).Total
    gs = G.fci.reindex(X.index)
    print(f"index vs MS FRB/US index: corr levels {np.corrcoef(idx, ms_frbus)[0, 1]:.2f}, daily changes {idx.diff().corr(ms_frbus.diff()):.2f}; latest {idx.iloc[-1]:+.2f} vs {ms_frbus.iloc[-1]:+.2f}")
    print(f"index vs GS FCI: corr levels {np.corrcoef(idx, gs)[0, 1]:.2f}, daily changes {idx.diff().corr(gs.diff()):.2f}")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    for key in ("ms", "gs"):
        fig, ax = plt.subplots(figsize=(13, 6.5))
        ax.plot(idx.index, idx, color="#1f5fa8", lw=1.8, label=f"Path-surprise weights (intraday event-window), {ten}, CAPE, real dollar (left axis, pp of funds rate)")
        ax.axhline(0, color="gray", lw=0.8)
        ax.set_ylabel("pp of funds rate, tighter above zero (vs 1990-2026 average)", fontsize=11)
        if key == "ms":
            ax.plot(ms_frbus.index, ms_frbus, color="#d62728", lw=1.8, label=f"MS-style index, FRB/US weights, all five variables, {ten} (left axis)")
            ax.set_ylim(min(idx.min(), ms_frbus.min()) - 0.3, max(idx.max(), ms_frbus.max()) + 0.3)
            ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=1, fontsize=10, frameon=False)
            title = f"vs MS-style index ({ten}): corr {np.corrcoef(idx, ms_frbus)[0, 1]:.2f} levels, {idx.diff().corr(ms_frbus.diff()):.2f} daily changes"
        else:
            k = gs.std() / idx.std()
            gl = (gs - gs.mean()) / k
            allv = pd.concat([idx, gl]); pad = 0.04 * (allv.max() - allv.min())
            lo, hi = allv.min() - pad, allv.max() + pad
            ax.set_ylim(lo, hi)
            b = ax.twinx(); b.plot(gs.index, gs, color="#d62728", lw=1.8, label="GS FCI, Goldman-style weights (right axis, scaled to the same spread)")
            b.set_ylim(gs.mean() + k * lo, gs.mean() + k * hi); b.set_ylabel("GS FCI", fontsize=11); b.tick_params(labelsize=11)
            h1, l1 = ax.get_legend_handles_labels(); h2, l2 = b.get_legend_handles_labels()
            ax.legend(h1 + h2, l1 + l2, loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=1, fontsize=10, frameon=False)
            title = f"vs GS FCI: corr {np.corrcoef(idx, gs)[0, 1]:.2f} levels, {idx.diff().corr(gs.diff()):.2f} daily changes"
        ax.set_title(f"Index with intraday path-surprise weights {title}", fontsize=12); ax.grid(alpha=0.25); ax.tick_params(labelsize=11)
        fig.tight_layout(); fig.savefig(os.path.join(HERE, f"path_fci_intraday_{key}_{a.sample}{tag}.png"), dpi=130)


if __name__ == "__main__":
    main()
