"""Small simulation for Section 2 of Note B (FS-A34): what happens in a sample of our length when a VAR omits financial conditions?
True model: monthly VAR in [u gap, core PCE inflation, 2-year yield, FCI] with a quadratic trend, estimated on the note's sample
(1994-02..2026-09, 2020-03..12 dropped), for the nominal and r*-gap steps. Simulated with jointly resampled residuals.
Estimated models, on each simulated sample: (a) all four variables; (b) the same VAR without the FCI.
The experiment is the note's: +1 pp on the 2-year in the announcement month, FCI +window ratio (full model only), u and inflation zero on impact.
Monthly only (no daily block). Usage: python3 omit_fci_sim.py [draws=2000] [--force]. Output: omit_fci_sim.csv, omit_fci_sim.log"""
import os, sys, numpy as np, pandas as pd
OUT, LOG = "omit_fci_sim.csv", "omit_fci_sim.log"
FORCE = "--force" in sys.argv
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
DRAWS = int(ARGS[0]) if ARGS else 2000
DGP_LAGS, EST_LAGS, HS = (6, 12), (3, 6, 12), (12, 24, 36)
LONG_MULT, LONG_DRAWS = 10, 300     # a much longer sample separates small-sample effects from the omission itself


# Numbers quoted in Section 2 of the note: (step, var, h) -> (true, mean with FCI, mean without FCI, wrong-sign share without FCI). True model and estimates 6 lags, actual sample length.
PAPER_SIM = {("nom", "u", 12): (0.36, 0.32, -0.08, 0.66), ("nom", "P", 24): (-0.32, -0.34, -0.21, 0.18),
             ("rstar", "u", 12): (0.51, 0.43, 0.11, 0.26), ("rstar", "P", 24): (-0.84, -0.75, -0.57, 0.01)}
PAPER_LONG_NOM_U_WITHOUT = -0.08       # nominal, u 12 m, without the FCI, 10 times as many months
TABLE = "paper/tables/tab0_sim.tex"


def report():
    """Compare the numbers quoted in the note with the output, and write the table."""
    d = pd.read_csv(OUT); d = d[(d.dgp_lags == 6) & (d.lags == 6)]
    q = lambda st, v, h, m, sm="actual": d[(d.step == st) & (d["var"] == v) & (d.h == h) & (d.model == m) & (d["sample"] == sm)].iloc[0]
    L = [r"\begin{tabular}{llcccccc}\toprule", r"& & True & \multicolumn{2}{c}{With the FCI} & & \multicolumn{2}{c}{Without the FCI} \\", r"\cmidrule{4-5}\cmidrule{7-8}", r"& & response & Mean (s.d.) & Wrong sign & & Mean (s.d.) & Wrong sign \\\midrule"]
    lab = {"nom": "Nominal", "rstar": r"$r^*$-gap"}; name = {"u": "Unemployment, 12 months", "P": "Price level, 24 months"}
    for (st, v, h), claim in PAPER_SIM.items():
        a, b = q(st, v, h, "with FCI"), q(st, v, h, "without FCI")
        L.append(f"{lab[st] if v == 'u' else ''} & {name[v]} & {a.true:+.2f} & {a['mean']:+.2f} ({a.sd:.2f}) & {a.wrong_sign:.0%} & & {b['mean']:+.2f} ({b.sd:.2f}) & {b.wrong_sign:.0%} \\\\".replace("%", r"\%"))
        for nm, c, val in zip(("true", "with", "without", "wrong"), claim, (a.true, a["mean"], b["mean"], b.wrong_sign)):
            print(f"{'OK' if abs(c - val) < 0.0051 else 'MISMATCH'} {st} {v} {h} {nm}: paper {c:+.2f}, computed {val:+.3f}")
    val = q("nom", "u", 12, "without FCI", "long")["mean"]; print(f"{'OK' if abs(PAPER_LONG_NOM_U_WITHOUT - val) < 0.0051 else 'MISMATCH'} long sample nom u: paper {PAPER_LONG_NOM_U_WITHOUT:+.2f}, computed {val:+.3f}")
    L.append(r"\bottomrule\end{tabular}"); open(TABLE, "w").write("\n".join(L) + "\n")


def fit(Z, L, tt):
    """OLS on contiguous data; returns coefficients on [1, lags, t, t^2]."""
    X = np.column_stack([np.ones(len(Z) - L)] + [Z[L - l:-l] for l in range(1, L + 1)] + [tt[L:], tt[L:] ** 2])
    return np.linalg.lstsq(X, Z[L:], rcond=None)[0]


def irf(C, K, L, b, H=36):
    """Response to impact vector b; column 1 (inflation) cumulated to the price level, as in midas_core."""
    A = [C[1 + K * l:1 + K * (l + 1)].T for l in range(L)]; out = [np.array(b, float)]
    for h in range(1, H + 1):
        out.append(sum(A[l] @ out[h - 1 - l] for l in range(min(L, h))))
    m = np.array(out); m[:, 1] = np.cumsum(m[:, 1]) / 12
    return m


def simulate(C, K, L, res, init, tt, rng):
    n = len(tt); Y = np.zeros((n, K)); Y[:L] = init; e = res[rng.integers(0, len(res), n)]
    for t in range(L, n):
        Y[t] = np.r_[1.0, Y[t - L:t][::-1].ravel(), tt[t], tt[t] ** 2] @ C + e[t]
    return Y


def main():
    import midas_core as MC
    idx0 = MC.event_index("NS"); _, _, idx0 = MC.slopes(idx0, "NS")
    ratio = MC.impact(1, idx0); ratio = ratio[1] / ratio[0]
    rows, log = [], [f"Omitted-FCI simulation. Window ratio FCI/2-year {ratio:.3f}. {DRAWS} draws at the actual sample length; {LONG_DRAWS} at {LONG_MULT} times it.\n"]
    for step in ("nom", "rstar"):
        D = MC.MAC[["u", "pi"]].join(MC.fin_monthly(step, 1), how="inner").dropna()
        for Lt in DGP_LAGS:
            rng = np.random.default_rng(341)
            X, Y, tt0 = [], [], []
            for p in D.index:
                if p < pd.Period("1994-02", "M") or p > pd.Period("2026-09", "M") or (p.year == 2020 and p.month >= 3): continue
                t_ = (p.year + (p.month - 1) / 12 - 2010) / 10
                X.append(np.r_[1.0, np.concatenate([D.loc[p - l].values for l in range(1, Lt + 1)]), t_, t_ * t_]); Y.append(D.loc[p].values); tt0.append(t_)
            X, Y = np.array(X), np.array(Y); C = np.linalg.lstsq(X, Y, rcond=None)[0]; res = Y - X @ C; T = len(Y)
            Comp = np.zeros((4 * Lt, 4 * Lt)); Comp[:4] = C[1:1 + 4 * Lt].T; Comp[4:, :-4] = np.eye(4 * (Lt - 1))
            eig = np.abs(np.linalg.eigvals(Comp)).max()
            b = [0, 0, 1, ratio]; true = irf(C, 4, Lt, b)
            init = D.loc[pd.Period("1994-02", "M") - Lt:pd.Period("1994-02", "M") - 1].values
            log.append(f"\n{step}: FCI residual per unit of 2-year residual in ordinary months {np.cov(res[:, 3], res[:, 2])[0, 1] / res[:, 2].var(ddof=1):.2f} (window ratio {ratio:.2f})")
            log.append(f"{step}, true model {Lt} lags, T={T}, largest root {eig:.3f}; true u " + " ".join(f"{h}m {true[h, 0]:+.2f}" for h in HS) + "; true P " + " ".join(f"{h}m {true[h, 1]:+.2f}" for h in HS))
            for sample, n, draws in (("actual", T, DRAWS), ("long", T * LONG_MULT, LONG_DRAWS)):
                tt = np.linspace(tt0[0], tt0[-1], n + Lt)     # same trend shape over the span, however many months
                E = {}
                for d in range(draws):
                    Z = simulate(C, 4, Lt, res, init, tt, rng)
                    for L in EST_LAGS:
                        E.setdefault(("with FCI", L), []).append(irf(fit(Z, L, tt), 4, L, b)[[*HS]][:, :2])
                        s = irf(fit(Z[:, :3], L, tt), 3, L, b[:3])[[*HS]][:, :2]; E.setdefault(("without FCI", L), []).append(s)
                for (model, L), v in E.items():
                    v = np.array(v)
                    for j, var in enumerate(("u", "P")):
                        for i, h in enumerate(HS):
                            x = v[:, i, j]; tv = true[h, j]; right = np.sign(tv)
                            rows.append(dict(step=step, dgp_lags=Lt, sample=sample, T=n, model=model, lags=L, var=var, h=h, true=tv, mean=x.mean(), median=np.median(x), sd=x.std(), rmse=np.sqrt(((x - tv) ** 2).mean()), wrong_sign=(np.sign(x) != right).mean()))
                dd = pd.DataFrame(rows); dd = dd[(dd.step == step) & (dd.dgp_lags == Lt) & (dd["sample"] == sample) & (dd.h.isin([12, 24])) & (((dd["var"] == "u") & (dd.h == 12)) | ((dd["var"] == "P") & (dd.h == 24)))]
                log.append(f"  {sample} sample: estimate mean (sd) [share wrong sign]")
                for (model, L), g in dd.groupby(["model", "lags"], sort=False):
                    u, p = g[g["var"] == "u"].iloc[0], g[g["var"] == "P"].iloc[0]
                    log.append(f"    {model:12s} {L:2d} lags: u 12m {u['mean']:+.2f} ({u.sd:.2f}) [{u.wrong_sign:.0%}]   P 24m {p['mean']:+.2f} ({p.sd:.2f}) [{p.wrong_sign:.0%}]")
    pd.DataFrame(rows).to_csv(OUT, index=False, float_format="%.4f")
    open(LOG, "w").write("\n".join(log) + "\n"); print("\n".join(log))


if __name__ == "__main__":
    if os.path.exists(OUT) and not FORCE: print(f"{OUT} exists; use --force to rerun")
    else: main()
    report()
