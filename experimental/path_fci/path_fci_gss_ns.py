"""
EXPERIMENTAL add-on: regressions on the Gurkaynak-Sack-Swanson path factor and on the Nakamura-Steinsson policy news factor (no instruments, no controls).

Factors, from the event-window surprises in MP1, MP2, ED2, ED3, ED4 (USMPD "Monetary Events"; unscheduled MP1 == 0 events and Mar-Apr 2020 dropped):
  GSS path   first two principal components, rotated so the second has zero loading on MP1 (the first is then the target factor); path = the second, scaled so that
             1 unit = a 1 pp move in ED4. By construction it does not move the current-meeting rate.
  NS news    the first principal component, scaled so that 1 unit = a 1 pp move in the 2-year Treasury yield (USMPD UST2Y; Nakamura and Steinsson use the 1-year).
             It mixes target and path news (MP1 is one of the five inputs).
Then, as in path_fci_raw_ed4.py:  x_j = a_j + b_j factor + e_j  (UST10Y pp, SP500 %, DXY %);  w = Psi^-1 b / (b' Psi^-1 b), full error covariance (diagonal variant also printed);
index = sum_j w_j (x_j - mean_j) with the real 10-year (--real10), 100 ln CAPE and 100 ln real dollar.

Usage:  python experimental/path_fci/path_fci_gss_ns.py [--sample full|nonzlb] [--real10] [--diag]
Outputs: path_fci_{gss,ns}_{ms,gs}_<sample>[_real10].png
"""
import os, argparse
import numpy as np, pandas as pd
import statsmodels.api as sm
import path_fci as P

HERE, ROOT = P.HERE, P.ROOT
ENDOG = {"10-yr": "UST10Y", "Equities (ln CAPE)": "SP500", "Dollar (ln real)": "DXY"}
FUT = ["MP1", "MP2", "ED2", "ED3", "ED4"]


def gss_ns(d):
    Xm = d[FUT].values
    U, S, Vt = np.linalg.svd(Xm, full_matrices=False)
    F, L = U[:, :2] * S[:2], Vt[:2].T
    a, b = L[0]
    Q = np.array([[a, -b], [b, a]]) / np.hypot(a, b)
    F2, L2 = F @ Q, L @ Q
    if L2[0, 0] < 0: F2[:, 0], L2[:, 0] = -F2[:, 0], -L2[:, 0]
    if L2[4, 1] < 0: F2[:, 1], L2[:, 1] = -F2[:, 1], -L2[:, 1]
    gss = F2[:, 1] * L2[4, 1]                               # unit = 1 pp on ED4
    f = U[:, 0] * S[0]
    if (f @ d.ED4.values) < 0: f = -f
    ns = f * ((f @ d.UST2Y.values) / (f @ f))               # unit = 1 pp on the 2-year yield
    return gss, ns, dict(zip(FUT, L2[:, 1] / L2[4, 1])), dict(zip(FUT, Vt[0] / np.abs(Vt[0]).max()))


def estimate(d, fac, full=True):
    Z = sm.add_constant(pd.DataFrame({"f": fac}))
    res = [sm.OLS(d[c].values, Z).fit(cov_type="HC1") for c in ENDOG.values()]
    b = np.array([r.params["f"] for r in res]); se = [r.bse["f"] for r in res]
    R = np.array([r.resid for r in res]).T
    S = np.cov(R.T, ddof=2)
    if not full: S = np.diag(np.diag(S))
    w = np.linalg.solve(S, b)
    return w / (b @ w), b, se, [r.rsquared for r in res]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--sample", default="full", choices=["full", "nonzlb"]); ap.add_argument("--real10", action="store_true"); ap.add_argument("--diag", action="store_true", help="plot the diagonal-covariance weights (errors treated as independent)")
    ap.add_argument("usmpd", nargs="?", default=P.USMPD)
    a = ap.parse_args()
    ev = P.events(a.usmpd)
    P.L.REAL10 = a.real10
    X, G = P.L.build()
    tag = ("_real10" if a.real10 else "") + ("_diag" if a.diag else "")
    ten = "real 10-yr" if a.real10 else "10-yr"
    d = ev.dropna(subset=FUT + ["UST2Y"] + list(ENDOG.values())).reset_index(drop=True)
    if a.sample == "nonzlb":
        d = d[~P.in_zlb(d.Date)].reset_index(drop=True)
    gss, ns, lg, ln_ = gss_ns(d)
    d = d.assign(gss=gss, ns=ns)
    print(f"{len(d)} events ({a.sample}).  corr(GSS path, ED4 residual path) {np.corrcoef(gss, d.path)[0, 1]:.2f}; corr(NS, GSS path) {np.corrcoef(ns, gss)[0, 1]:.2f}; corr(NS, MP1) {np.corrcoef(ns, d.MP1)[0, 1]:.2f}; sd GSS {gss.std():.3f}, sd NS {ns.std():.3f}")
    print("GSS path loadings (per 1 pp ED4): " + ", ".join(f"{k} {v:+.2f}" for k, v in lg.items()))
    print("NS first-PC loadings (relative to the largest): " + ", ".join(f"{k} {v:+.2f}" for k, v in ln_.items()))
    sens = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "frbus_sensitivities.csv"), index_col=0)
    ms_frbus = P.L.level(X, sens["ffr_eq_q4"].to_dict(), float(sens.loc["req", "unit_size"])).Total
    gs = G.fci.reindex(X.index)
    names = list(ENDOG)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    unit = {"gss": "pp of GSS path (1 pp on ED4)", "ns": "pp of NS policy news (1 pp on the 2-year)"}
    for fname, lab in (("gss", "GSS path factor"), ("ns", "Nakamura-Steinsson policy news")):
        fac = d[fname].values
        idxs = {}
        for vlab, full in (("full cov", True), ("diag", False)):
            w, b, se, r2 = estimate(d, fac, full)
            rng = np.random.default_rng(11)
            bs = np.array([estimate(d.iloc[(i := rng.integers(0, len(d), len(d)))].reset_index(drop=True), fac[i], full)[0] for _ in range(300)])
            idx = sum(w[i] * P.VARS[n][1] * (X[P.VARS[n][0]] - X[P.VARS[n][0]].mean()) for i, n in enumerate(names))
            idxs[vlab] = idx
            print(f"\n[{lab}; {vlab}]")
            if full:
                print("  response per +1 unit (se; R2): " + ", ".join(f"{n} {b[i]:+.3f} ({se[i]:.3f}; {r2[i]:.2f})" for i, n in enumerate(names)))
            print("  weights [90% band]: " + ", ".join(f"{n} {w[i]:+.4f} [{np.percentile(bs[:, i], 5):+.3f}, {np.percentile(bs[:, i], 95):+.3f}]" for i, n in enumerate(names)) + f"; shares {', '.join(f'{x:.0%}' for x in w * b)}")
            print(f"  index: level sd {idx.std():.2f}, daily sd {idx.diff().std():.3f}; vs MS FRB/US: levels {np.corrcoef(idx, ms_frbus)[0, 1]:.2f}, daily {idx.diff().corr(ms_frbus.diff()):.2f}; "
                  f"vs GS FCI: levels {np.corrcoef(idx, gs)[0, 1]:.2f}, daily {idx.diff().corr(gs.diff()):.2f}; latest {idx.iloc[-1]:+.2f}")
        idx = idxs["diag" if a.diag else "full cov"]
        for key in ("ms", "gs"):
            fig, ax = plt.subplots(figsize=(13, 6.5))
            ax.plot(idx.index, idx, color="#1f5fa8", lw=1.8, label=f"{lab} regressions, no instruments, {'independent-error (diagonal)' if a.diag else 'full-covariance'} weights; {ten}, CAPE, real dollar (left axis, {unit[fname]})")
            ax.axhline(0, color="gray", lw=0.8); ax.set_ylabel("tighter above zero (vs 1990-2026 average)", fontsize=11)
            if key == "ms":
                ax.plot(ms_frbus.index, ms_frbus, color="#d62728", lw=1.8, label=f"MS-style index, FRB/US weights, all five variables, {ten} (left axis, pp of funds rate)")
                ax.set_ylim(min(idx.min(), ms_frbus.min()) - 0.3, max(idx.max(), ms_frbus.max()) + 0.3)
                ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=1, fontsize=9, frameon=False)
                title = f"vs MS-style index: corr {np.corrcoef(idx, ms_frbus)[0, 1]:.2f} levels, {idx.diff().corr(ms_frbus.diff()):.2f} daily changes"
            else:
                kk = gs.std() / idx.std(); gl = (gs - gs.mean()) / kk
                allv = pd.concat([idx, gl]); pad = 0.04 * (allv.max() - allv.min()); lo, hi = allv.min() - pad, allv.max() + pad
                ax.set_ylim(lo, hi)
                bb = ax.twinx(); bb.plot(gs.index, gs, color="#d62728", lw=1.8, label="GS FCI, Goldman-style weights (right axis, scaled to the same spread)")
                bb.set_ylim(gs.mean() + kk * lo, gs.mean() + kk * hi); bb.set_ylabel("GS FCI", fontsize=11); bb.tick_params(labelsize=11)
                h1, l1 = ax.get_legend_handles_labels(); h2, l2 = bb.get_legend_handles_labels()
                ax.legend(h1 + h2, l1 + l2, loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=1, fontsize=9, frameon=False)
                title = f"vs GS FCI: corr {np.corrcoef(idx, gs)[0, 1]:.2f} levels, {idx.diff().corr(gs.diff()):.2f} daily changes"
            ax.set_title(f"{lab} index {title}", fontsize=12); ax.grid(alpha=0.25); ax.tick_params(labelsize=11)
            fig.tight_layout(); fig.savefig(os.path.join(HERE, f"path_fci_{fname}_{key}_{a.sample}{tag}.png"), dpi=130); plt.close(fig)


if __name__ == "__main__":
    main()
