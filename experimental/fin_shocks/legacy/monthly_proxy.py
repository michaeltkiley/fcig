"""Purely monthly VAR comparison for Note B (FS-A38): the monthly VAR with and without the FCI under monthly identification, next to the note's model.
System: [u gap, core PCE inflation, policy rate, FCI (optional)], monthly averages of the note's daily series, 1994-02..2026-09 without 2020-03..12, quadratic trend, 3/6/12 lags, nominal/real/r*-gap.
Cases (per +1 pp, see UNIT):
  P1  standard proxy VAR: NS surprise summed over the month; every impact entry estimated.  Unit: +1 pp on the monthly-average 2-year.
  P0  proxy with macro entries zero on impact.                                               Same unit.
  WE  window impact, event timing: impact = phi * (1, b_F), macro zero, phi = average share of the month after the announcement. Unit: +1 pp 2-year in the window (as the note).
  WS  window impact, as if on the first day of the month: phi = 1 (upper bracket).           Unit: +1 pp on the monthly-average 2-year.
  MP1 as P1 and P0 with the funds rate (adjusted in each step by the 2-year's adjustment) and the MP1 surprise summed over the month. Unit: +1 pp funds rate.
Inference: P1/P0/MP1: Anderson-Rubin sets (90%, HC1, conditional on VAR coefficients) on a grid; WE/WS: 200 draws resampling events and monthly residuals, regressors fixed.
Instrument sample: months 1996-01..2026-07 (first and last announcement used by the note), zero in months without an announcement.
Usage: python3 monthly_proxy.py [draws=200] [--force]. Output: monthly_proxy.csv, monthly_proxy.log"""
import os, sys, numpy as np, pandas as pd
OUT, LOG = "monthly_proxy.csv", "monthly_proxy.log"
FORCE = "--force" in sys.argv
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
DRAWS = int(ARGS[0]) if ARGS else 200
LAGS, TARGETS = (3, 6, 12), (("u", 12), ("P", 24))
GRID = np.arange(-15, 15.0001, 0.01)
CRIT = 2.7055


def design(D, L):
    idx, X, Y = [], [], []
    for p in D.index:
        if p < pd.Period("1994-02", "M") or p > pd.Period("2026-09", "M") or (p.year == 2020 and p.month >= 3): continue
        try: lags = np.concatenate([D.loc[p - l].values for l in range(1, L + 1)])
        except KeyError: continue
        t = (p.year + (p.month - 1) / 12 - 2010) / 10
        X.append(np.r_[1.0, lags, t, t * t]); Y.append(D.loc[p].values); idx.append(p)
    return np.array(X), np.array(Y), pd.PeriodIndex(idx, freq="M")


def ma(C, K, L, H=36):
    """MA matrices Theta_0..Theta_H."""
    A = [C[1 + K * l:1 + K * (l + 1)].T for l in range(L)]; T = [np.eye(K)]
    for h in range(1, H + 1): T.append(sum(A[l] @ T[h - 1 - l] for l in range(min(L, h))))
    return np.array(T)


def row_of(T, var, h):
    """Row vector mapping an impact vector into the target (u at h, or the price level at h)."""
    return T[h, 0] if var == "u" else T[:h + 1, 1].sum(axis=0) / 12


def first_stage(e, z):
    x = np.column_stack([np.ones(len(z)), z]); xx = np.linalg.inv(x.T @ x); b = xx @ x.T @ e; r = e - x @ b; n, k = x.shape
    V = xx @ (x.T * (r ** 2)) @ x @ xx * n / (n - k)
    return b[1], b[1] ** 2 / V[1, 1]


def ar_set(c0, c1, res, z):
    """90% AR set for theta in H0: Cov(z, (c0 - theta c1)' res) = 0, c0 and c1 fixed. Returns (low, high, unbounded)."""
    x = np.column_stack([np.ones(len(z)), z]); xx = np.linalg.inv(x.T @ x); n, k = x.shape
    a = res @ c0; d = res @ c1
    def stat(th):
        e = a - th * d; b = xx @ x.T @ e; r = e - x @ b; V = xx @ (x.T * (r ** 2)) @ x @ xx * n / (n - k)
        return b[1] ** 2 / V[1, 1]
    acc = np.array([stat(g) <= CRIT for g in GRID])
    if not acc.any(): return np.nan, np.nan, False
    return GRID[acc].min(), GRID[acc].max(), bool(acc[0] or acc[-1])


def main():
    import midas_core as MC
    from mf_common import EV
    rng = np.random.default_rng(38)
    idx0 = MC.event_index("NS"); _, _, idx0 = MC.slopes(idx0, "NS"); ev = EV.iloc[idx0]
    mon = ev.Date.dt.to_period("M"); first, last = mon.min(), mon.max()
    zs = {"NS": ev.ns.groupby(mon).sum(), "MP1": ev.MP1.groupby(mon).sum()}
    share = lambda ii: float(np.mean([(EV.n[i] - EV.k[i]) / EV.n[i] for i in ii]))
    phi0 = share(idx0); rows, F = [], []
    log = [f"Monthly VAR comparison. {len(idx0)} announcements, instrument months {first}..{last}. Average share of the month after the announcement phi = {phi0:.3f}.\n"]
    y2m = MC.fin_monthly("nom", 0).pol
    ffm = MC.POL["ff"].groupby(MC.MON).mean()
    for step in ("nom", "real", "rstar"):
        adj = MC.fin_monthly(step, 0).pol - y2m
        for fci in (0, 1):
            K = 3 + fci; M_ = MC.MAC[["u", "pi"]]
            D0 = M_.join(MC.fin_monthly(step, fci), how="inner").dropna()
            Dff = D0.copy(); Dff["pol"] = (ffm + adj).reindex(D0.index)
            for L in LAGS:
                for pol, D, zn, cases in (("y2", D0, "NS", ("P1", "P0", "WE", "WS")), ("ff", Dff, "MP1", ("P1", "P0"))):
                    X, Y, per = design(D.dropna(), L); C = np.linalg.lstsq(X, Y, rcond=None)[0]; fit = X @ C; res = Y - fit; T = ma(C, K, L)
                    ok = (per >= first) & (per <= last); z = zs[zn].reindex(per[ok]).fillna(0.0).values; r = res[ok]
                    g = np.array([first_stage(r[:, j], z)[0] for j in range(K)]); fs = first_stage(r[:, 2], z)[1]
                    F.append(dict(step=step, fci=fci, lags=L, policy=pol, F=fs, n=len(z), impact_fci=(g[3] / g[2] if fci else np.nan), impact_u=g[0] / g[2], impact_pi=g[1] / g[2]))
                    if "WE" in cases:
                        b = MC.impact(1 if fci else 0, idx0); b = np.r_[0, 0, b / b[0]]
                    for case in cases:
                        for var, h in TARGETS:
                            c = row_of(T, var, h); e2 = np.eye(K)[2]
                            if case == "P1":
                                S = g / g[2]; c0 = c; lo, hi, unb = ar_set(c0, e2, r, z)
                            elif case == "P0":
                                w = np.zeros(K); w[2] = 1
                                if fci: w[3] = g[3] / g[2]
                                S = w; c2 = np.zeros(K); c2[2] = c[2]
                                if fci: c2[3] = c[3]
                                lo, hi, unb = ar_set(c2, e2, r, z)
                            else:
                                phi = phi0 if case == "WE" else 1.0; S = phi * b
                                dr = []
                                for _ in range(DRAWS):
                                    Cb = np.linalg.lstsq(X, fit + res[rng.integers(0, len(res), len(res))], rcond=None)[0]
                                    ib = rng.choice(idx0, size=len(idx0), replace=True); bb = MC.impact(1 if fci else 0, ib); bb = np.r_[0, 0, bb / bb[0]]
                                    dr.append(row_of(ma(Cb, K, L), var, h) @ ((share(ib) if case == "WE" else 1.0) * bb))
                                lo, hi = np.percentile(dr, [5, 95]); unb = False
                            rows.append(dict(step=step, fci=fci, lags=L, policy=pol, case=case, var=var, h=h, r=float(c @ S), lo=lo, hi=hi, unbounded=int(unb)))
    d = pd.DataFrame(rows); d.to_csv(OUT, index=False, float_format="%.4f"); f = pd.DataFrame(F); f.to_csv("monthly_proxy_F.csv", index=False, float_format="%.4f")
    log.append(f.round(2).to_string(index=False)); log.append("\n" + d.round(2).to_string(index=False))
    open(LOG, "w").write("\n".join(log) + "\n")


# Claims in the note: (description, computed, paper value)
PAPER = {"F_y2_with_min": 1.7, "F_y2_with_max": 6.4, "F_y2_without_min": 4.9, "F_y2_without_max": 6.3, "F_ff_min": 5.3, "F_ff_max": 8.3, "imp_min": 0.13, "imp_max": 0.62,
         "WE_u_min": 0.21, "WE_u_max": 0.23, "WS_u_min": 0.47, "WS_u_max": 0.51, "WE_P_min": -0.39, "WE_P_max": -0.29, "WS_P_min": -0.84, "WS_P_max": -0.62}
TABLE = "paper/tables/tabA_monthly.tex"


def report():
    d, f = pd.read_csv(OUT), pd.read_csv("monthly_proxy_F.csv")
    a = pd.read_csv("paper/tables/all_results.csv", dtype={"fci": str})
    a = a[(a.macro == "u,pi") & (a.trend == 1) & (a.shock == "NS") & (a.bootd == 0) & (a.mstart == "1994-02") & (a["sample"].isna()) & (a.rate.isin(["nom", "real", "rstar"])) & (a.fci.astype(str).isin(["0", "1"]))]
    a = a.drop_duplicates(["rate", "fci", "lags", "var"])
    g = f[f.policy == "y2"]; c = lambda cs, v, st="rstar": d[(d.policy == "y2") & (d.case == cs) & (d.fci == 1) & (d.step == st) & (d["var"] == v)].r
    comp = {"F_y2_with_min": g[g.fci == 1].F.min(), "F_y2_with_max": g[g.fci == 1].F.max(), "F_y2_without_min": g[g.fci == 0].F.min(), "F_y2_without_max": g[g.fci == 0].F.max(),
            "F_ff_min": f[f.policy == "ff"].F.min(), "F_ff_max": f[f.policy == "ff"].F.max(), "imp_min": g[g.fci == 1].impact_fci.min(), "imp_max": g[g.fci == 1].impact_fci.max(),
            "WE_u_min": c("WE", "u").min(), "WE_u_max": c("WE", "u").max(), "WS_u_min": c("WS", "u").min(), "WS_u_max": c("WS", "u").max(),
            "WE_P_min": c("WE", "P").min(), "WE_P_max": c("WE", "P").max(), "WS_P_min": c("WS", "P").min(), "WS_P_max": c("WS", "P").max()}
    for k, v in PAPER.items(): print(f"{'OK' if abs(v - comp[k]) < 0.0501 * (k[0] == 'F') + 0.0051 else 'MISMATCH'} {k}: paper {v:+.2f}, computed {comp[k]:+.3f}")
    fm = lambda r, lo, hi, u: f"${r:+.2f}" + ("^{\\circ}$" if u else ("^{**}$" if lo > 0 or hi < 0 else "$"))
    def cell(pol, cs, v, fci, st, L):
        x = d[(d.policy == pol) & (d.case == cs) & (d["var"] == v) & (d.fci == fci) & (d.step == st) & (d.lags == L)].iloc[0]
        return fm(x.r, x.lo, x.hi, x.unbounded) if not np.isnan(x.lo) else f"${x.r:+.2f}$"
    def base(v, h, fci, st, L):
        x = a[(a["var"] == v) & (a.fci == str(fci)) & (a.rate == st) & (a.lags == L)].iloc[0]; return fm(x[f"r{h}"], x[f"lo{h}"], x[f"hi{h}"], 0)
    ST = ("nom", "real", "rstar"); LG = (3, 6, 12)
    L = [r"\begin{tabular}{ll" + "c" * 9 + "}\\toprule", r" & & \multicolumn{3}{c}{Nominal} & \multicolumn{3}{c}{Real} & \multicolumn{3}{c}{$r^*$-gap}\\", r"\cmidrule(lr){3-5}\cmidrule(lr){6-8}\cmidrule(lr){9-11}", r"Model & FCI & " + " & ".join(str(x) for _ in ST for x in LG) + r"\\"]
    NAME = (("base", "Baseline mixed-frequency model"), ("WE", "Monthly, window impact, announcement timing"), ("WS", "Monthly, window impact, first day of month"), ("P0", "Monthly proxy, macro zero on impact"), ("P1", "Monthly proxy, standard"), ("MP1", "Monthly proxy, standard, funds rate and MP1"))
    for v, h, title in (("u", 12, "A. Unemployment gap after 12 months (percentage points)"), ("P", 24, "B. Core PCE price level after 24 months (percent)")):
        L += ["\\midrule", f"\\multicolumn{{11}}{{l}}{{\\textit{{{title}}}}}\\\\"]
        for k, nm in NAME:
            for fci in (0, 1):
                L.append((nm if fci == 0 else "") + f" & {'included' if fci else 'none'} & " + " & ".join((base(v, h, fci, s, l) if k == "base" else cell("ff", "P1", v, fci, s, l) if k == "MP1" else cell("y2", k, v, fci, s, l)) for s in ST for l in LG) + r"\\")
    L += ["\\midrule", r"\multicolumn{11}{l}{\textit{C. First-stage $F$ statistic of the monthly proxy}}\\"]
    for pol, fci, nm in (("y2", 0, "Two-year yield, NS surprise"), ("y2", 1, ""), ("ff", 0, "Funds rate, MP1 surprise"), ("ff", 1, "")):
        L.append(nm + f" & {'included' if fci else 'none'} & " + " & ".join(f"{f[(f.policy == pol) & (f.fci == fci) & (f.step == s) & (f.lags == l)].F.iloc[0]:.1f}" for s in ST for l in LG) + r"\\")
    L.append(r"\bottomrule\end{tabular}"); open(TABLE, "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    if os.path.exists(OUT) and not FORCE: print(f"{OUT} exists; use --force to rerun")
    else: main()
    report()
