"""
EXPERIMENTAL add-on (path_fci.py unchanged): reverse regression by IV on the intraday (USMPD event-window) surprises.

    path_e = a + w_10y UST10Y_e + w_eq SP500_e + w_usd DXY_e + g target_e + u_e
with UST10Y, SP500 and DXY treated as endogenous (they carry non-path news and measurement error) and instrumented by
    ED1, ED2, ED3, ED4 (rates futures surprises), UST2Y, UST30Y, SPFUT (S&P E-mini futures return)
The requested 20-year yield and Wilshire 5000 are not in USMPD: the 30-year yield and the S&P futures return (a second measure of the same equity move)
are used instead. Variant B adds EURUSD and USDJPY (more dollar measures). 2SLS, heteroskedasticity-robust errors (linearmodels).

WARNING (exclusion restriction): the path surprise is built as ED4 less its projection on MP1, so ED1-ED4 are mechanically correlated with the dependent
variable. They cannot be excluded instruments for it; with ED4 alone the IV coefficient is just the inverse of the forward response (1/b) per variable. The overidentification
(Sargan/Wooldridge robust overid) test is printed. Treat the IV estimates as a diagnostic, not as weights.

Usage:  python experimental/path_fci/path_fci_intraday_iv.py [--sample full|nonzlb] [--real10]
Outputs: path_fci_intraday_iv_{ms,gs}_<sample>[_real10].png
"""
import os, argparse
import numpy as np, pandas as pd
import statsmodels.api as sm
from linearmodels.iv import IV2SLS
import path_fci as P

HERE, ROOT = P.HERE, P.ROOT
ENDOG = {"10-yr": "UST10Y", "Equities (ln CAPE)": "SP500", "Dollar (ln real)": "DXY"}
INST_A = ["ED1", "ED2", "ED3", "ED4", "UST2Y", "UST30Y", "SPFUT"]
INST_B = INST_A + ["EURUSD", "USDJPY"]


def fit(ev, inst):
    d = ev.dropna(subset=list(ENDOG.values()) + inst).reset_index(drop=True)
    d = d.assign(const=1.0)
    m = IV2SLS(d.path, d[["const", "target"]], d[list(ENDOG.values())], d[inst]).fit(cov_type="robust")
    fs = {c: float(m.first_stage.diagnostics.loc[c, "f.stat"]) for c in ENDOG.values()}
    j = m.wooldridge_overid
    return d, m, fs, j


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--sample", default="full", choices=["full", "nonzlb"]); ap.add_argument("--real10", action="store_true")
    ap.add_argument("usmpd", nargs="?", default=P.USMPD)
    a = ap.parse_args()
    ev = P.events(a.usmpd)
    P.L.REAL10 = a.real10
    X, G = P.L.build()
    if a.sample == "nonzlb":
        ev = ev[~P.in_zlb(ev.Date)].reset_index(drop=True)
    res = {}
    for lab, inst in (("A: " + ", ".join(INST_A), INST_A), ("B: A + EURUSD, USDJPY", INST_B)):
        d, m, fs, j = fit(ev, inst)
        w = pd.Series({n: m.params[c] for n, c in ENDOG.items()})
        res[lab] = w
        print(f"\n[{lab}] {len(d)} events, {a.sample}")
        print(pd.DataFrame({"w": [m.params[c] for c in ENDOG.values()], "se": [m.std_errors[c] for c in ENDOG.values()],
                            "first-stage partial F": [fs[c] for c in ENDOG.values()]}, index=list(ENDOG)).round(4).to_string())
        print(f"  Wooldridge robust overid {j.stat:.1f}, df {j.df}, p = {j.pval:.3f}  (overid test: rejection = instruments not valid)")
    # diagnostic: ED4 alone as instrument (each variable: ratio cov(ED4,path)/cov(ED4,x)), to show the mechanical link
    d = ev.dropna(subset=list(ENDOG.values())).reset_index(drop=True)
    fb = {n: sm.OLS(d[c], sm.add_constant(d[["path", "target"]])).fit().params["path"] for n, c in ENDOG.items()}
    print("\nforward responses b (x on path, intraday) and their inverses 1/b: " + ", ".join(f"{n}: {fb[n]:+.3f}, {1 / fb[n]:+.3f}" for n in ENDOG))
    print("corr of path with ED4 in this sample: %.2f (path = ED4 - %.2f*MP1)" % (d.path.corr(d.ED4), d.ED4.sub(d.path).div(d.MP1.replace(0, np.nan)).median()))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sens = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "frbus_sensitivities.csv"), index_col=0)
    ms_frbus = P.L.level(X, sens["ffr_eq_q4"].to_dict(), float(sens.loc["req", "unit_size"])).Total
    gs = G.fci.reindex(X.index)
    for vtag, w in zip("ab", res.values()):
        draw(vtag, w, X, ms_frbus, gs, a, plt)


def draw(vtag, w, X, ms_frbus, gs, a, plt):
    tag = ("_real10" if a.real10 else "") + "_" + vtag
    ten = "real 10-yr" if a.real10 else "10-yr"
    idx = sum(w[n] * P.VARS[n][1] * (X[P.VARS[n][0]] - X[P.VARS[n][0]].mean()) for n in ENDOG)
    print(f"\nindex (variant {vtag.upper()} weights): level sd {idx.std():.2f}, daily sd {idx.diff().std():.3f}; vs MS FRB/US: corr levels {np.corrcoef(idx, ms_frbus)[0, 1]:.2f}, "
          f"daily {idx.diff().corr(ms_frbus.diff()):.2f}; vs GS FCI: levels {np.corrcoef(idx, gs)[0, 1]:.2f}, daily {idx.diff().corr(gs.diff()):.2f}; latest {idx.iloc[-1]:+.2f}")
    for key in ("ms", "gs"):
        fig, ax = plt.subplots(figsize=(13, 6.5))
        ax.plot(idx.index, idx, color="#1f5fa8", lw=1.8, label=f"IV reverse-regression weights (intraday event-window), {ten}, CAPE, real dollar (left axis, pp of path surprise)")
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
        ax.set_title(f"Index with intraday IV reverse-regression weights {title}", fontsize=12); ax.grid(alpha=0.25); ax.tick_params(labelsize=11)
        fig.tight_layout(); fig.savefig(os.path.join(HERE, f"path_fci_intraday_iv_{key}_{a.sample}{tag}.png"), dpi=130); plt.close(fig)


if __name__ == "__main__":
    main()
