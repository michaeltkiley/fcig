"""
EXPERIMENTAL add-on (path_fci.py unchanged): weights that purge measurement error, by an instrumental principal component.

Hypothesis: the event-window surprises in the 10-year (UST10Y), S&P 500 (SP500) and dollar (DXY) are a true response to the FOMC news plus measurement error / other news.
Step 1 (instrumental principal components): extract the policy-news factors from indicators that do NOT contain those three variables, MP1, MP2, ED1-ED4 and UST2Y (event window),
    two principal components rotated so that the second has no loading on MP1 (Gurkaynak-Sack-Swanson): target = 1 pp on MP1, path = 1 pp on ED4.
    Averaging seven indicators averages out the measurement error in any single one (the raw path surprise in path_fci.py is one noisy ED4 residual).
Step 2 (purge): regress each x_j on the two factors:  x_j = a_j + b_j path + c_j target + e_j.  B = [b c] (3 x 2) is the true response; e (full 3 x 3 covariance Psi) is the error.
Step 3 (scale to the path surprise): weights w minimise the error variance w' Psi w subject to w'b = 1 (unit response to a 1 pp path surprise): w = Psi^-1 b / (b' Psi^-1 b).
    --neutral also imposes w'c = 0 (no response to the target): W = Psi^-1 B (B' Psi^-1 B)^-1, column "path". That constraint is estimated from poorly determined target loadings c and moves
    most of the weight to equities with a very wide band on the 10-year, so the default is path only (the target is still a control in step 2). index = sum_j w_j (x_j - mean_j), in pp of path surprise (a funds-rate-path equivalent), with a full error covariance (no double counting).
x_j are the real 10-year (--real10), 100 ln CAPE and 100 ln real dollar at index time; weights are estimated once from the event window.

Usage:  python experimental/path_fci/path_fci_ipc.py [--sample full|nonzlb] [--real10] [--neutral]
Outputs: path_fci_ipc_{ms,gs}_<sample>[_real10].png
"""
import os, argparse
import numpy as np, pandas as pd
import statsmodels.api as sm
import path_fci as P

HERE, ROOT = P.HERE, P.ROOT
IND = ["MP1", "MP2", "ED1", "ED2", "ED3", "ED4", "UST2Y"]
ENDOG = {"10-yr": "UST10Y", "Equities (ln CAPE)": "SP500", "Dollar (ln real)": "DXY"}


def factors(d):
    X = d[IND].values
    U, S, Vt = np.linalg.svd(X, full_matrices=False)
    F, L = U[:, :2] * S[:2], Vt[:2].T
    a, b = L[0]
    Q = np.array([[a, -b], [b, a]]) / np.hypot(a, b)       # second factor gets zero MP1 loading
    F, L = F @ Q, L @ Q
    if L[0, 0] < 0: F[:, 0], L[:, 0] = -F[:, 0], -L[:, 0]
    if L[IND.index("ED4"), 1] < 0: F[:, 1], L[:, 1] = -F[:, 1], -L[:, 1]
    tgt, pth = F[:, 0] * L[0, 0], F[:, 1] * L[IND.index("ED4"), 1]    # units: pp on MP1, pp on ED4
    fit = 1 - ((X - F @ L.T) ** 2).sum() / (X ** 2).sum()
    return tgt, pth, dict(zip(IND, L[:, 1] / L[IND.index("ED4"), 1])), fit


NEUTRAL = False


def estimate(d):
    tgt, pth, load, fit = factors(d)
    Z = sm.add_constant(pd.DataFrame({"path": pth, "target": tgt}))
    cols = list(ENDOG.values())
    res = {c: sm.OLS(d[c].values, Z).fit(cov_type="HC1") for c in cols}
    B = np.array([[res[c].params["path"], res[c].params["target"]] for c in cols])
    R = np.array([res[c].resid for c in cols]).T
    Psi = np.cov(R.T, ddof=3)
    Pi = np.linalg.inv(Psi)
    if NEUTRAL:
        W = Pi @ B @ np.linalg.inv(B.T @ Pi @ B)
        return W[:, 0], B, Psi, res, (tgt, pth, load, fit)
    b = B[:, 0]
    w = Pi @ b
    return w / (b @ w), B, Psi, res, (tgt, pth, load, fit)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--sample", default="full", choices=["full", "nonzlb"]); ap.add_argument("--real10", action="store_true"); ap.add_argument("--neutral", action="store_true")
    ap.add_argument("usmpd", nargs="?", default=P.USMPD)
    a = ap.parse_args()
    global NEUTRAL
    NEUTRAL = a.neutral
    ev = P.events(a.usmpd)
    P.L.REAL10 = a.real10
    X, G = P.L.build()
    d = ev.dropna(subset=IND + list(ENDOG.values())).reset_index(drop=True)
    if a.sample == "nonzlb":
        d = d[~P.in_zlb(d.Date)].reset_index(drop=True)
    w, B, Psi, res, (tgt, pth, load, fit) = estimate(d)
    names = list(ENDOG)
    print(f"{len(d)} events ({a.sample}). Two factors explain {fit:.0%} of the variance of {IND}. Path-factor loadings (per 1 pp on ED4): " + ", ".join(f"{k} {v:+.2f}" for k, v in load.items()))
    print(f"corr of path factor with the raw path surprise (ED4 residual): {np.corrcoef(pth, d.path)[0, 1]:.2f}")
    print("\nTrue response to a +1 pp path factor (se), and to the target factor:")
    for n, c in ENDOG.items():
        print(f"  {n}: path {res[c].params['path']:+.3f} ({res[c].bse['path']:.3f}), target {res[c].params['target']:+.3f}; R2 {res[c].rsquared:.2f}")
    print("error correlations:\n", pd.DataFrame(np.corrcoef(np.array([res[c].resid for c in ENDOG.values()])), index=names, columns=names).round(2).to_string())
    sh = w * B[:, 0]
    print("\nweights (pp of path surprise per unit of x): " + ", ".join(f"{n} {w[i]:+.4f}" for i, n in enumerate(names)) + f"   check w'b = {w @ B[:, 0]:.2f}, w'c = {w @ B[:, 1]:.2f}" + (" (target-neutral)" if NEUTRAL else ""))
    print("share of the unit response: " + ", ".join(f"{n} {sh[i]:.0%}" for i, n in enumerate(names)))
    # bootstrap
    rng = np.random.default_rng(1); bs = []
    for _ in range(500):
        i = rng.integers(0, len(d), len(d))
        try:
            bs.append(estimate(d.iloc[i].reset_index(drop=True))[0])
        except Exception:
            pass
    bs = np.array(bs)
    print("90% bootstrap bands: " + ", ".join(f"{n} [{np.percentile(bs[:, i], 5):+.3f}, {np.percentile(bs[:, i], 95):+.3f}]" for i, n in enumerate(names)))
    ww = pd.Series(w, index=names)
    tag = ("_real10" if a.real10 else "") + ("_neutral" if a.neutral else "")
    ten = "real 10-yr" if a.real10 else "10-yr"
    idx = sum(ww[n] * P.VARS[n][1] * (X[P.VARS[n][0]] - X[P.VARS[n][0]].mean()) for n in names)
    sens = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "frbus_sensitivities.csv"), index_col=0)
    ms_frbus = P.L.level(X, sens["ffr_eq_q4"].to_dict(), float(sens.loc["req", "unit_size"])).Total
    gs = G.fci.reindex(X.index)
    print(f"\nindex: level sd {idx.std():.2f}, daily sd {idx.diff().std():.3f}; vs MS FRB/US index: corr levels {np.corrcoef(idx, ms_frbus)[0, 1]:.2f}, daily {idx.diff().corr(ms_frbus.diff()):.2f}; "
          f"vs GS FCI: levels {np.corrcoef(idx, gs)[0, 1]:.2f}, daily {idx.diff().corr(gs.diff()):.2f}; latest {idx.iloc[-1]:+.2f}")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    for key in ("ms", "gs"):
        fig, ax = plt.subplots(figsize=(13, 6.5))
        ax.plot(idx.index, idx, color="#1f5fa8", lw=1.8, label=f"Instrumental-PC weights (event window), {ten}, CAPE, real dollar (left axis, pp of path surprise)")
        ax.axhline(0, color="gray", lw=0.8); ax.set_ylabel("tighter above zero (vs 1990-2026 average)", fontsize=11)
        if key == "ms":
            ax.plot(ms_frbus.index, ms_frbus, color="#d62728", lw=1.8, label=f"MS-style index, FRB/US weights, all five variables, {ten} (left axis, pp of funds rate)")
            ax.set_ylim(min(idx.min(), ms_frbus.min()) - 0.3, max(idx.max(), ms_frbus.max()) + 0.3)
            ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=1, fontsize=10, frameon=False)
            title = f"vs MS-style index: corr {np.corrcoef(idx, ms_frbus)[0, 1]:.2f} levels, {idx.diff().corr(ms_frbus.diff()):.2f} daily changes"
        else:
            k = gs.std() / idx.std(); gl = (gs - gs.mean()) / k
            allv = pd.concat([idx, gl]); pad = 0.04 * (allv.max() - allv.min()); lo, hi = allv.min() - pad, allv.max() + pad
            ax.set_ylim(lo, hi)
            b = ax.twinx(); b.plot(gs.index, gs, color="#d62728", lw=1.8, label="GS FCI, Goldman-style weights (right axis, scaled to the same spread)")
            b.set_ylim(gs.mean() + k * lo, gs.mean() + k * hi); b.set_ylabel("GS FCI", fontsize=11); b.tick_params(labelsize=11)
            h1, l1 = ax.get_legend_handles_labels(); h2, l2 = b.get_legend_handles_labels()
            ax.legend(h1 + h2, l1 + l2, loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=1, fontsize=10, frameon=False)
            title = f"vs GS FCI: corr {np.corrcoef(idx, gs)[0, 1]:.2f} levels, {idx.diff().corr(gs.diff()):.2f} daily changes"
        ax.set_title(f"Index with instrumental-PC weights {title}", fontsize=12); ax.grid(alpha=0.25); ax.tick_params(labelsize=11)
        fig.tight_layout(); fig.savefig(os.path.join(HERE, f"path_fci_ipc_{key}_{a.sample}{tag}.png"), dpi=130); plt.close(fig)


if __name__ == "__main__":
    main()
