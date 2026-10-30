"""
EXPERIMENTAL add-on (path_fci_ipc_lean.py unchanged): the lean instrumental-PC weights (ED1 + UST2Y) without purging the path surprise of the target.

Same steps as path_fci_ipc_lean.py (set R: first PC of standardised ED1, UST2Y; instrumented path = fitted path on the PC; 2SLS purged responses b_j; weights
w = Psi^-1 b / (b' Psi^-1 b)), in three versions:
    A  orth path + MP1 control   (path_fci_ipc_lean.py: path = ED4 residual after MP1; MP1 a control in steps 2 and 3)
    B  orth path, no control     (path still the ED4 residual after MP1, MP1 dropped from steps 2 and 3)
    C  raw ED4, no MP1 anywhere  (path = the whole ED4 surprise, i.e. the change in the expected 3-month rate about a year ahead, target news included;
                                  MP1 in no step; the index is then in pp of that ED4 surprise)
Usage:  python experimental/path_fci/path_fci_ipc_nomp1.py [--sample full|nonzlb] [--real10]
Outputs: path_fci_ipc_nomp1_{ms,gs}_<sample>[_real10].png (version C)
"""
import os, argparse
import numpy as np, pandas as pd
import statsmodels.api as sm
import path_fci as P

HERE, ROOT = P.HERE, P.ROOT
ENDOG = {"10-yr": "UST10Y", "Equities (ln CAPE)": "SP500", "Dollar (ln real)": "DXY"}
Z = ["ED1", "UST2Y"]


def estimate(d, ctrl, raw):
    z = d[Z].values; z = (z - z.mean(0)) / z.std(0)
    U, S, Vt = np.linalg.svd(z, full_matrices=False)
    F = U[:, :1] * S[:1]
    path = d.ED4.values if raw else d.path.values
    cols = [np.ones(len(d))] + ([d.MP1.values] if ctrl else []) + [F[:, 0]]
    first = sm.OLS(path, np.column_stack(cols)).fit()
    f = F[:, 0] * first.params[-1]
    X2 = pd.DataFrame({"const": 1.0, "f": f})
    if ctrl: X2["MP1"] = d.MP1.values
    res = [sm.OLS(d[c].values, X2).fit(cov_type="HC1") for c in ENDOG.values()]
    b = np.array([r.params["f"] for r in res]); se = [r.bse["f"] for r in res]
    R = np.array([r.resid for r in res]).T
    Pi = np.linalg.inv(np.cov(R.T, ddof=X2.shape[1]))
    w = Pi @ b
    return w / (b @ w), b, se, first


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--sample", default="full", choices=["full", "nonzlb"]); ap.add_argument("--real10", action="store_true")
    ap.add_argument("usmpd", nargs="?", default=P.USMPD)
    a = ap.parse_args()
    ev = P.events(a.usmpd)
    P.L.REAL10 = a.real10
    X, G = P.L.build()
    tag = "_real10" if a.real10 else ""
    ten = "real 10-yr" if a.real10 else "10-yr"
    d = ev.dropna(subset=Z + list(ENDOG.values())).reset_index(drop=True)
    if a.sample == "nonzlb":
        d = d[~P.in_zlb(d.Date)].reset_index(drop=True)
    sens = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "frbus_sensitivities.csv"), index_col=0)
    ms_frbus = P.L.level(X, sens["ffr_eq_q4"].to_dict(), float(sens.loc["req", "unit_size"])).Total
    gs = G.fci.reindex(X.index)
    names = list(ENDOG)
    out = {}
    for lab, ctrl, raw in (("A: orth path + MP1 control", True, False), ("B: orth path, no control", False, False), ("C: raw ED4, no MP1 anywhere", False, True)):
        w, b, se, first = estimate(d, ctrl, raw)
        rng = np.random.default_rng(5)
        bs = np.array([estimate(d.iloc[rng.integers(0, len(d), len(d))].reset_index(drop=True), ctrl, raw)[0] for _ in range(300)])
        ww = pd.Series(w, index=names)
        idx = sum(ww[n] * P.VARS[n][1] * (X[P.VARS[n][0]] - X[P.VARS[n][0]].mean()) for n in names)
        out[lab] = idx
        print(f"\n[{lab}] {len(d)} events ({a.sample}); instruments explain {first.rsquared:.0%} of the path measure")
        print("  responses per +1 pp (se): " + ", ".join(f"{n} {b[i]:+.3f} ({se[i]:.3f})" for i, n in enumerate(names)))
        print("  weights [90% band]: " + ", ".join(f"{n} {w[i]:+.4f} [{np.percentile(bs[:, i], 5):+.3f}, {np.percentile(bs[:, i], 95):+.3f}]" for i, n in enumerate(names)) + f"; shares {', '.join(f'{x:.0%}' for x in w * b)}")
        print(f"  index: level sd {idx.std():.2f}, daily sd {idx.diff().std():.3f}; vs MS FRB/US: levels {np.corrcoef(idx, ms_frbus)[0, 1]:.2f}, daily {idx.diff().corr(ms_frbus.diff()):.2f}; "
              f"vs GS FCI: levels {np.corrcoef(idx, gs)[0, 1]:.2f}, daily {idx.diff().corr(gs.diff()):.2f}; latest {idx.iloc[-1]:+.2f}")
    idx = out["C: raw ED4, no MP1 anywhere"]
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    for key in ("ms", "gs"):
        fig, ax = plt.subplots(figsize=(13, 6.5))
        ax.plot(idx.index, idx, color="#1f5fa8", lw=1.8, label=f"Instrumental-PC weights (ED1 + 2-yr), raw ED4 surprise, no MP1 control; {ten}, CAPE, real dollar (left axis, pp of ED4 surprise)")
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
        ax.set_title(f"Instrumental-PC index without MP1 {title}", fontsize=12); ax.grid(alpha=0.25); ax.tick_params(labelsize=11)
        fig.tight_layout(); fig.savefig(os.path.join(HERE, f"path_fci_ipc_nomp1_{key}_{a.sample}{tag}.png"), dpi=130); plt.close(fig)


if __name__ == "__main__":
    main()
