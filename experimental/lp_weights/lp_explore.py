"""
Exploration (29 Oct 2026, user away): local-projection ways to get macro-relevant weights for financial variables, using NS policy surprises.
Monthly data: financial variables = demeaned levels of the macro-model index variables (policy rate, 10-year, mortgage spread, BBB spread, equities 100 ln CAPE,
real dollar 100 ln); activity = unemployment gap (UNRATE - CBO NROU); inflation = core PCE 12-month less 2. Surprises: monthly sums of raw NS policy news
(2-year-yield units); split into "pure policy" (stocks move opposite to the surprise) and "information" (same direction) events, Jarocinski-Karadi poor man's
sign rule; MP1 sums (target) and GSS path factor sums. Months in 2020 are excluded from every regression. HAC (Newey-West) standard errors.

E1  one variable at a time, LP-IV of u(t+h) on the change in x_j instrumented by NS: shows what this identifies (algebra: beta_j = g_h / psi_j,h).
E2  responses of unemployment and inflation to NS surprises (do tightenings raise unemployment in our data?), all events and pure-policy events.
E3  multi-horizon minimum distance (the tutorial's g_h = theta' psi_h): theta from stacking responses at h = 0..24.
E4  "LP macro-model" weights: theta from a multivariate predictive LP of u(t+12) - u(t-1) on all financial levels (with macro controls); normalized by the
    complete-transmission sum theta' psi (psi = response of each variable to a 1-unit NS surprise), the weighting note's normalization.
E5  LP-IV with several instruments (pure, information, MP1, GSS path) for several financial variables at once.
Usage: python experimental/lp_weights/lp_explore.py
"""
import os, sys
import numpy as np, pandas as pd
import statsmodels.api as sm

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for sub in ("fci_compare", "ms_fci", "path_fci"):
    sys.path.insert(0, os.path.join(ROOT, "experimental", sub))
import mf_var_us as V
import macro_model_dl as DL
import path_fci as P
import path_fci_gss_ns as Q

FIN = ["policy rate", "10-year", "mortgage spread", "BBB spread", "equities", "dollar"]
EW = ["10-year", "equities", "dollar"]                       # variables with intraday event-window responses
RNG = pd.period_range("1994-02", "2025-12", freq="M")


def surprises():
    ev = P.events(P.USMPD)
    d = ev.dropna(subset=Q.FUT + ["UST2Y"] + list(Q.ENDOG.values())).reset_index(drop=True)
    gss, ns, _, _ = Q.gss_ns(d)
    d = d.assign(ns=ns, gss=gss, m=pd.PeriodIndex(d.Date, freq="M"))
    d["pure"] = np.where(np.sign(d.ns) != np.sign(d.SP500), d.ns, 0.0)
    d["info"] = d.ns - d.pure
    S = pd.DataFrame({c: d.groupby("m")[c].sum() for c in ("ns", "pure", "info", "MP1", "gss")}).reindex(RNG).fillna(0.0)
    # event-window responses per NS unit (intraday): 10-year, S&P 500, DXY
    psi_ew = {n: float(np.polyfit(d.ns, d[c], 1)[0]) for n, c in Q.ENDOG.items()}
    return S, dict(zip(EW, psi_ew.values())), d


def keep(idx):
    return np.array([t.year != 2020 for t in idx])


def ols_hac(y, X, lags):
    ok = np.isfinite(y) & np.isfinite(X).all(axis=1)
    r = sm.OLS(y[ok], X[ok]).fit(cov_type="HAC", cov_kwds={"maxlags": lags})
    return r


def lp(y, s, h, ctrl=None, nlag=3):
    """y(t+h) - y(t-1) = a + b s_t + lags of dy and s (+ ctrl) ; returns b, se."""
    dy = y.diff()
    cols = {"y": y.shift(-h) - y.shift(1), "s": s, **{f"dy{l}": dy.shift(l) for l in range(1, nlag + 1)}, **{f"s{l}": s.shift(l) for l in range(1, nlag + 1)}}
    if ctrl is not None:
        for k, c in ctrl.items():
            cols[k] = c
    Z = pd.concat(cols, axis=1).reindex(RNG)
    Z = Z[keep(Z.index)].dropna()
    X = sm.add_constant(Z.drop(columns="y"))
    r = sm.OLS(Z.y, X).fit(cov_type="HAC", cov_kwds={"maxlags": max(h, 1)})
    return r.params["s"], r.bse["s"]


def main():
    x, _ = DL.levels_data()
    M = V.macro_data(False)
    u, pi = M["unemployment gap"], M["inflation gap"]
    S, psi_ew, d = surprises()
    pd.set_option("display.width", 220)
    print(f"months {len(RNG)} (2020 excluded in regressions); event-window psi per NS unit: " + ", ".join(f"{k} {v:+.3f}" for k, v in psi_ew.items()))

    # ---------------- E2: activity and inflation responses to NS ----------------
    print("\n=== E2. Responses of the unemployment gap and inflation gap to a 1-unit NS surprise (pp), monthly LP ===")
    for lab, s in (("all events", S["ns"]), ("pure-policy events", S["pure"]), ("information events", S["info"])):
        for nm_, y in (("unemployment gap", u), ("core inflation gap", pi)):
            out = [lp(y, s, h) for h in (0, 3, 6, 12, 18, 24)]
            print(f"  {lab:20s} {nm_:18s} " + "  ".join(f"h={h}: {b:+.2f} ({se:.2f})" for h, (b, se) in zip((0, 3, 6, 12, 18, 24), out)))

    # ---------------- financial responses psi_h (monthly LP) ----------------
    H = 24
    psi = {v: np.array([lp(x[v], S.ns, h)[0] for h in range(H + 1)]) for v in FIN}
    g = np.array([lp(u, S.ns, h)[0] for h in range(H + 1)])
    print("\nmonthly LP responses to NS, h = 0 / 12 / 24: " + "; ".join(f"{v} {psi[v][0]:+.2f} / {psi[v][12]:+.2f} / {psi[v][24]:+.2f}" for v in FIN)
          + f"; unemployment {g[0]:+.2f} / {g[12]:+.2f} / {g[24]:+.2f}")

    # ---------------- E1: one at a time LP-IV ----------------
    print("\n=== E1. One variable at a time: LP-IV of u(t+12) - u(t-1) on the month-t change in x_j, instrument NS ===")
    print("    beta_j = (response of u at 12) / (response of x_j in month t); every beta_j * psi_j equals the same number (the shock's total effect),")
    print("    so these 'effects' are inverse responses, i.e. market-type weights, not separate causal effects.")
    for v in FIN:
        b = g[12] / psi[v][0]
        print(f"    {v:16s} psi_j(0) {psi[v][0]:+7.3f}   beta_j {b:+9.3f}   beta_j*psi_j {b * psi[v][0]:+.3f}")

    # ---------------- E3: multi-horizon minimum distance ----------------
    print("\n=== E3. theta from g_h = theta' psi_h stacked over h = 0..24 (unemployment; event-window variables and all six) ===")
    for vars_ in (EW, FIN):
        Ps = np.column_stack([psi[v] for v in vars_])
        th = np.linalg.lstsq(Ps, g, rcond=None)[0]
        fit = 1 - np.sum((g - Ps @ th) ** 2) / np.sum((g - g.mean()) ** 2)
        print(f"  {len(vars_)} variables: cond(Psi) {np.linalg.cond(Ps):.0f}, R2 of g on Psi {fit:.2f}; theta (u pp per unit): " + ", ".join(f"{v} {t:+.4f}" for v, t in zip(vars_, th)))
    # block bootstrap of E3 (3 variables)
    rs = np.random.default_rng(11); T = len(RNG); bl = 24; th_b = []
    Xd = pd.concat([x[EW], u.rename("u"), S.ns.rename("s")], axis=1).reindex(RNG)
    for r in range(80):
        st = rs.integers(0, T - bl, size=T // bl + 1)
        pick = np.concatenate([np.arange(a, a + bl) for a in st])[:T]
        Xb = Xd.iloc[pick].copy(); Xb.index = RNG
        try:
            Pb = np.column_stack([[lp(Xb[v], Xb.s, h)[0] for h in range(0, H + 1, 2)] for v in EW])
            gb = np.array([lp(Xb.u, Xb.s, h)[0] for h in range(0, H + 1, 2)])
            th_b.append(np.linalg.lstsq(Pb, gb, rcond=None)[0])
        except Exception:
            pass
    th_b = np.array(th_b)
    print("  bootstrap (80 block resamples, even horizons) 90% bands, 3 variables: " + ", ".join(f"{v} [{np.percentile(th_b[:, i], 5):+.3f}, {np.percentile(th_b[:, i], 95):+.3f}]" for i, v in enumerate(EW))
          + "   (resampled months break the time order of the surprises; indicative only)")

    # ---------------- E4: predictive multivariate LP, normalized by theta' psi ----------------
    print("\n=== E4. 'LP macro-model' weights: u(t+h) - u(t-1) on financial levels x_t (all six), controls: u_t-1, inflation_t-1, 3 lags of du ===")
    psi0 = {v: (psi_ew[v] if v in psi_ew else psi[v][0]) for v in FIN}
    print("    psi used for normalization (per NS unit): " + ", ".join(f"{v} {psi0[v]:+.3f}" for v in FIN) + "  (event window for 10-year, equities, dollar; monthly LP h=0 for the others)")
    frb = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "frbus_sensitivities.csv"), index_col=0)["ffr_eq_q4"]
    ext = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "frbus_sensitivities_ext.csv"), index_col=0)["ffr_eq_q4"]
    sF = pd.Series({"policy rate": ext["rshort_direct"], "10-year": frb["rg10"], "mortgage spread": ext["rme"], "BBB spread": frb["rbbbp"], "equities": -frb["req"], "dollar": frb["fpxr"]})
    res = {}
    for h in (6, 12, 24):
        du = u.diff()
        Z = pd.concat({"y": u.shift(-h) - u.shift(1), **{v: x[v] for v in FIN}, "u1": u.shift(1), "pi1": pi.shift(1), **{f"du{l}": du.shift(l) for l in (1, 2, 3)}}, axis=1)
        Z = Z.loc["1990-07":"2025-12"]; Z = Z[keep(Z.index)].dropna()
        r = sm.OLS(Z.y, sm.add_constant(Z.drop(columns="y"))).fit(cov_type="HAC", cov_kwds={"maxlags": h})
        th = r.params[FIN]
        G = float(sum(th[v] * psi0[v] for v in FIN))
        w = th / G
        res[h] = (th, r.bse[FIN], w, G)
        print(f"  h={h:2d}: theta (u pp per unit; se) " + ", ".join(f"{v} {th[v]:+.4f} ({r.bse[v]:.4f})" for v in FIN))
        print(f"         complete-transmission sum theta'psi = {G:+.4f} u pp per NS unit;  weights theta_j / theta'psi (2-year pp per unit): " + ", ".join(f"{v} {w[v]:+.3f}" for v in FIN))
    w12 = res[12][2]
    print("  compare relative weights (10-year = 1): LP h=12 " + ", ".join(f"{v} {w12[v] / w12['10-year']:+.3f}" for v in FIN)
          + "\n                                          FRB/US q4 " + ", ".join(f"{v} {sF[v] / sF['10-year']:+.3f}" for v in FIN))
    idx = (x[FIN] * w12).sum(axis=1)
    mm = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "macro_model_v3_monthly.csv"), index_col=0); mm.index = pd.PeriodIndex(mm.index, freq="M")
    tr = pd.read_csv(os.path.join(ROOT, "experimental", "fci_compare", "transmission_v3_monthly.csv"), index_col=0); tr.index = pd.PeriodIndex(tr.index, freq="M")
    J = pd.concat({"LP-macro (h=12)": idx, "EP_4": mm["EP_4"], "MKT": tr["MKT"], "GS": tr["GS"]}, axis=1).loc["1990-01":].dropna()
    print(f"  LP-macro index (h=12 weights, 2-year pp): sd {J.iloc[:, 0].std():.2f}, latest {J.iloc[-1, 0]:+.2f}; corr levels / 12m changes: "
          + ", ".join(f"{c} {J.iloc[:, 0].corr(J[c]):.2f} / {J.iloc[:, 0].diff(12).corr(J[c].diff(12)):.2f}" for c in ("EP_4", "MKT", "GS")))
    pd.DataFrame({"theta_h12": res[12][0], "se_h12": res[12][1], "weight_h12": w12, "frbus_q4": sF}).to_csv(os.path.join(HERE, "lp_macro_weights.csv"), float_format="%.5f")
    J.to_csv(os.path.join(HERE, "lp_macro_index_monthly.csv"), float_format="%.4f", index_label="month")

    # ---------------- E5: multi-instrument LP-IV ----------------
    print("\n=== E5. LP-IV: u(t+12) - u(t-1) on the month-t changes in the 10-year, equities and dollar, instruments: pure, information, MP1, GSS path ===")
    dx = x[EW].diff()
    du = u.diff()
    Z = pd.concat({"y": u.shift(-12) - u.shift(1), **{f"d_{v}": dx[v] for v in EW}, **{k: S[k] for k in ("pure", "info", "MP1", "gss")},
                   **{f"du{l}": du.shift(l) for l in (1, 2, 3)}, **{f"l_{v}": dx[v].shift(1) for v in EW}}, axis=1).reindex(RNG)
    Z = Z[keep(Z.index)].dropna()
    W = sm.add_constant(Z[[c for c in Z if c.startswith("du") or c.startswith("l_")]])
    Zi = Z[["pure", "info", "MP1", "gss"]]
    fs_F = {}
    Xhat = {}
    for v in EW:
        full = sm.OLS(Z[f"d_{v}"], pd.concat([W, Zi], axis=1)).fit()
        rest = sm.OLS(Z[f"d_{v}"], W).fit()
        q = Zi.shape[1]
        F = ((rest.ssr - full.ssr) / q) / (full.ssr / (len(Z) - full.df_model - 1))
        fs_F[v] = F; Xhat[v] = full.fittedvalues
    X2 = pd.concat([W, pd.DataFrame({f"d_{v}": Xhat[v] for v in EW})], axis=1)
    r2 = sm.OLS(Z.y, X2).fit()
    # 2SLS coefficients with HAC on the second stage (standard errors approximate: generated regressors not corrected)
    r2h = sm.OLS(Z.y, X2).fit(cov_type="HAC", cov_kwds={"maxlags": 12})
    th5 = pd.Series({v: r2.params[f"d_{v}"] for v in EW})
    G5 = float(sum(th5[v] * psi_ew[v] for v in EW))
    print("  first-stage F (4 instruments): " + ", ".join(f"{v} {fs_F[v]:.1f}" for v in EW) + f";  months {len(Z)}")
    print("  theta (u pp at 12 months per unit change; approx se): " + ", ".join(f"{v} {th5[v]:+.4f} ({r2h.bse[f'd_{v}']:.4f})" for v in EW))
    print(f"  theta'psi = {G5:+.4f}; weights theta_j / theta'psi: " + ", ".join(f"{v} {th5[v] / G5:+.3f}" for v in EW))


if __name__ == "__main__":
    main()
