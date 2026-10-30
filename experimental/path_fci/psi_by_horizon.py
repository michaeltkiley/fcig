"""
Financial-side response profiles to monetary policy (DYNAMICS_PLAN.md, step 2), and the gap test with the distributed-lag macro index (step 1c).

Monthly local projections, 1994-02..2026-09 (months without an FOMC event have a zero surprise):
    y(t+h) - y(t-1) = a + b_h s_t + sum_{l=1..3} [c_l dy(t-l) + d_l s(t-l)] + e,   h = 0..24
y: monthly (end of month) demeaned levels of the macro-model variables (10-year, equities = 100 ln CAPE, real dollar = 100 ln, mortgage spread, BBB spread, policy rate, house prices),
plus industrial production (100 ln INDPRO) for the GDP-side ratio, and the indexes (macro static, macro distributed-lag, market).
s: monthly sum of the NS policy-news factor in funds-rate pp (NS x 0.98). Variants: GSS path factor (pp on ED4); NS "pure policy" events only (equities move opposite to the surprise,
Jarocinski-Karadi poor man's sign split); NS excluding 2008-09 and 2020.
Inference: influence-function (FWL) scores, Newey-West long-run covariance across all (variable, horizon) pairs jointly (bandwidth 24), so linear combinations and ratios across
variables and horizons get correct standard errors.
Tests (common variables 10-year, equities, dollar):
    proportionality  H0: psi_h proportional to psi_0 (2 restrictions per h, delta method, Wald chi2(2))
    weight gap       (s - w)'psi_h for the common variables, plus s'psi_h for macro-only variables = the response of the macro-minus-market gap (accounting link to gap_test.py)
    theta            exploratory: GDP weights from stacking g_h = theta'psi_h over h = 0..24 (tutorial section 6.2), IP as monthly output, OLS on the point estimates, block-bootstrap bands
Daily event-day projections (n = event days): y(e+h) - y(e-1) on the surprise, h = 0..60 trading days (10-year, equities, dollar).
Distributed-lag readings (step 1c): the responses implied by the estimated profiles for the macro distributed-lag index (FRB/US lags applied to each variable) and for the
market index transmitted with the funds-rate hike's own lags; the direct LP of the very smooth DL index is also printed but is dominated by pre-trends.
Usage: python experimental/path_fci/psi_by_horizon.py
Outputs: psi_by_horizon.csv, psi_dl_implied.csv, psi_by_horizon.png, psi_daily.png
"""
import os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for sub in ("path_fci", "ms_fci", "fci_compare"):
    sys.path.insert(0, os.path.join(ROOT, "experimental", sub))
import path_fci as P
import path_fci_gss_ns as Q
import macro_model_dl as DL
import common_unit_v2 as C

H = 24
COMMON = ["10-year", "equities", "dollar"]
NLAG = 3


def lp_scores(y, s, h):
    """FWL local projection; returns b, influence series (indexed by t) and n."""
    dy = y.diff()
    Z = pd.concat({"y": y.shift(-h) - y.shift(1), "s": s, **{f"dy{l}": dy.shift(l) for l in range(1, NLAG + 1)}, **{f"s{l}": s.shift(l) for l in range(1, NLAG + 1)}}, axis=1).dropna()
    X = np.column_stack([np.ones(len(Z))] + [Z[c].values for c in Z if c not in ("y", "s")])
    proj = lambda v: v - X @ np.linalg.lstsq(X, v, rcond=None)[0]
    st, yt = proj(Z.s.values), proj(Z.y.values)
    b = st @ yt / (st @ st)
    e = yt - b * st
    infl = pd.Series(st * e / np.mean(st * st), index=Z.index)
    return b, infl, len(Z)


def joint_cov(infls, ns, L=24):
    idx = sorted(set().union(*[i.index for i in infls]))
    A = np.column_stack([i.reindex(idx).fillna(0.0).values for i in infls])
    n = np.array(ns, float)
    S = A.T @ A
    for l in range(1, L + 1):
        G = A[l:].T @ A[:-l]
        S += (1 - l / (L + 1)) * (G + G.T)
    return S / np.outer(n, n)


def run(Y, s, names, H=H):
    b, infl, ns, keys = [], [], [], []
    for v in names:
        for h in range(H + 1):
            bb, ii, nn = lp_scores(Y[v], s, h)
            b.append(bb); infl.append(ii); ns.append(nn); keys.append((v, h))
    V = joint_cov(infl, ns)
    return pd.Series(b, index=pd.MultiIndex.from_tuples(keys)), pd.DataFrame(V, index=pd.MultiIndex.from_tuples(keys), columns=pd.MultiIndex.from_tuples(keys))


def lin(b, V, coefs):
    """Linear combination sum coef * b[key]; returns value and se."""
    k = list(coefs); a = np.array([coefs[x] for x in k])
    return float(a @ b[k].values), float(np.sqrt(a @ V.loc[k, k].values @ a))


def prop_wald(b, V, h):
    """H0: psi_h proportional to psi_0 for the common variables (ratios to the 10-year)."""
    k = [(v, hh) for hh in (0, h) for v in COMMON]
    p0 = b[[(v, 0) for v in COMMON]].values; ph = b[[(v, h) for v in COMMON]].values
    g = np.array([ph[j] * p0[0] - p0[j] * ph[0] for j in (1, 2)])
    J = np.zeros((2, 6))
    for r, j in enumerate((1, 2)):
        J[r, j] = -ph[0]; J[r, 0] = ph[j]               # d/d p0_j, d/d p0_0
        J[r, 3 + j] = p0[0]; J[r, 3] = -p0[j]           # d/d ph_j, d/d ph_0
    Vg = J @ V.loc[k, k].values @ J.T
    return float(g @ np.linalg.solve(Vg, g))


def main():
    x, comp = DL.levels_data()
    ip = C.me(C.raw_series("INDPRO.csv")) if False else None
    ipr = C.raw_series("INDPRO.csv"); ipr.index = ipr.index.to_period("M")
    x["IP"] = 100 * np.log(ipr)
    # indexes
    w, ev = C.ns_weights(); wf = (C.NS_FFR * w).values
    s4 = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "frbus_sensitivities.csv"), index_col=0)["ffr_eq_q4"]
    sv = np.array([s4["rg10"], -s4["req"], s4["fpxr"]])
    dlm = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "macro_model_dl_monthly.csv")); dlm.index = pd.PeriodIndex(dlm.month, freq="M")
    x["MKT"] = x[COMMON].values @ wf
    x["MACRO static"] = dlm["base|STATIC_4"]; x["MACRO DL_12"] = dlm["base|DL_12"]
    x["gap static"] = x["MACRO static"] - x.MKT; x["gap DL_12"] = x["MACRO DL_12"] - x.MKT
    # surprises
    d = ev.dropna(subset=Q.FUT + ["UST2Y"] + list(Q.ENDOG.values())).reset_index(drop=True)
    gss, ns, _, _ = Q.gss_ns(d)
    d = d.assign(ns=ns * 0.98, gss=gss, m=pd.PeriodIndex(d.Date, freq="M"))
    d["pure"] = np.where(np.sign(d.ns) != np.sign(d.SP500), d.ns, 0.0)
    rng = pd.period_range("1994-02", "2026-09", freq="M")
    sur = {k: d.groupby("m")[c].sum().reindex(rng).fillna(0.0) for k, c in (("NS", "ns"), ("GSS", "gss"), ("NS pure policy", "pure"))}
    ex = sur["NS"].copy(); ex[(ex.index >= pd.Period("2008-07", "M")) & (ex.index <= pd.Period("2009-12", "M"))] = np.nan; ex[(ex.index >= pd.Period("2020-01", "M")) & (ex.index <= pd.Period("2020-12", "M"))] = np.nan
    sur["NS ex 2008-09, 2020"] = ex
    print("events:", len(d), "| pure-policy share of NS events:", round(float((d.pure != 0).mean()), 2))
    Y = x.loc[rng[0] - 6:rng[-1] + H]
    names = COMMON + ["mortgage spread", "BBB spread", "policy rate", "house prices", "IP", "MKT", "MACRO static", "MACRO DL_12", "gap static", "gap DL_12"]
    smac = {"mortgage spread": float(pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "frbus_sensitivities_ext.csv"), index_col=0).loc["rme", "ffr_eq_q4"]),
            "BBB spread": float(s4["rbbbp"]), "policy rate": float(pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "frbus_sensitivities_ext.csv"), index_col=0).loc["rshort_direct", "ffr_eq_q4"])}
    allrows = []
    for lab, s in sur.items():
        Ys = Y.copy()
        if lab.startswith("NS ex"):
            Ys = Ys.copy()
        b, V = run(Ys, s.reindex(Ys.index), names if lab == "NS" else COMMON + ["mortgage spread", "BBB spread", "policy rate", "IP", "gap static"])
        print(f"\n===== {lab} (responses per unit of surprise; HAC se) =====")
        hs = [0, 1, 3, 6, 9, 12, 18, 24]
        tab = {}
        for v in [n for n in names if (n, 0) in b.index]:
            tab[v] = [f"{b[(v, h)]:+.2f} ({np.sqrt(V.loc[(v, h), (v, h)]):.2f})" for h in hs]
        print(pd.DataFrame(tab, index=[f"h={h}" for h in hs]).T.to_string())
        rows = []
        for h in hs:
            gcoef = {(v, h): float(sv[i] - wf[i]) for i, v in enumerate(COMMON)}
            gcoef.update({(v, h): smac[v] for v in smac})
            gv, gse = lin(b, V, gcoef)
            ccoef = {(v, h): float(sv[i] - wf[i]) for i, v in enumerate(COMMON)}
            cv, cse = lin(b, V, ccoef)
            wv, wse = lin(b, V, {(v, h): float(wf[i]) for i, v in enumerate(COMMON)})
            sv_, sse = lin(b, V, {(v, h): float(sv[i]) for i, v in enumerate(COMMON)})
            wald = prop_wald(b, V, h) if h > 0 else np.nan
            ratio = {v: b[(v, h)] / b[(v, 0)] for v in COMMON}
            rows.append(dict(surprise=lab, h=h, market_reading=wv, market_se=wse, macro_reading_common=sv_, macro_se=sse, gap_common=cv, gap_common_se=cse, gap_with_macro_only=gv, gap_se=gse,
                             wald_prop=wald, p_prop=float(np.exp(-wald / 2)) if h > 0 else np.nan, **{f"ratio_{v}": ratio[v] for v in COMMON}))
        R = pd.DataFrame(rows); allrows.append(R)
        print("\nreadings of psi_h by static weights (w = market, s = FRB/US q4), gap = (s - w)'psi_h (+ macro-only variables), proportionality test (chi2(2), p):")
        print(R.drop(columns=["surprise"]).round(3).to_string(index=False))
        if lab == "NS":
            bN, VN = b, V
    out = pd.concat(allrows)
    out.to_csv(os.path.join(HERE, "psi_by_horizon.csv"), float_format="%.4f", index=False)
    # accounting link: the gap LP equals the linear combination of variable LPs only up to sample/controls differences
    b, V = bN, VN
    print("\nGap index LP vs implied linear combination (NS):")
    for h in (0, 6, 12, 24):
        gcoef = {(v, h): float(sv[i] - wf[i]) for i, v in enumerate(COMMON)}; gcoef.update({(v, h): smac[v] for v in smac})
        print(f"  h={h:2d}: gap static LP {b[('gap static', h)]:+.2f} ({np.sqrt(VN.loc[('gap static', h), ('gap static', h)]):.2f}); implied {lin(b, V, gcoef)[0]:+.2f};  gap DL_12 LP {b[('gap DL_12', h)]:+.2f} ({np.sqrt(VN.loc[('gap DL_12', h), ('gap DL_12', h)]):.2f}); MACRO DL_12 {b[('MACRO DL_12', h)]:+.2f}, MKT {b[('MKT', h)]:+.2f}")
    # distributed-lag readings implied by the estimated profiles (linear in the LP coefficients, so exact standard errors):
    #   macro DL_K response at h = sum_m Phi((m+1)/3 capped at K)' dpsi_{h-m} / G(K)        (FRB/US output lags applied to the financial responses)
    #   market DL_K response at h = sum_m [G((m+1)/3 capped)/G(K)] d(w'psi)_{h-m}          (the market index treated as a policy state, transmitted with the hike's own lags)
    Pp, Gp = DL.paths("base")
    vars6 = ["policy rate", "10-year", "mortgage spread", "BBB spread", "equities", "dollar"]
    wfull = dict(zip(COMMON, wf))
    print("\nImplied distributed-lag readings of the response to a 1 pp NS surprise (K = 12 quarters), pp of funds rate:")
    rows = []
    for K in (4, 12):
        for h in (0, 3, 6, 9, 12, 18, 24):
            cm, ck = {}, {}
            for m in range(h + 1):
                q = min((m + 1) / 3, K)
                ph = DL.phi_at(Pp[vars6], q) / Gp[K]
                gr = np.interp(q, np.arange(len(Gp)), Gp) / Gp[K]
                for k, sgn in ((h - m, 1.0), (h - m - 1, -1.0)):
                    if k < 0: continue
                    for v in vars6:
                        cm[(v, k)] = cm.get((v, k), 0.0) + sgn * ph[v]
                    for v in COMMON:
                        ck[(v, k)] = ck.get((v, k), 0.0) + sgn * gr * wfull[v]
            mv, mse = lin(b, V, cm); kv, kse = lin(b, V, ck)
            gc = {k_: cm.get(k_, 0.0) - ck.get(k_, 0.0) for k_ in set(cm) | set(ck)}
            gv, gse = lin(b, V, gc)
            rows.append(dict(K=K, h=h, macro_DL=mv, macro_DL_se=mse, market_DL=kv, market_DL_se=kse, gap_DL=gv, gap_DL_se=gse, hike_DL=float(np.interp(min((h + 1) / 3, K), np.arange(len(Gp)), Gp) / Gp[K])))
    print(pd.DataFrame(rows).round(3).to_string(index=False))
    pd.DataFrame(rows).to_csv(os.path.join(HERE, "psi_dl_implied.csv"), float_format="%.4f", index=False)
    # theta from g_h = theta' psi_h (IP), h = 0..24
    Psi = np.array([[b[(v, h)] for v in COMMON] for h in range(H + 1)]); g = np.array([b[("IP", h)] for h in range(H + 1)])
    th = np.linalg.lstsq(Psi, g, rcond=None)[0]
    D = th @ np.array([b[(v, 0)] for v in COMMON])
    print(f"\ntheta (IP per unit, h=0..24 stacked): " + ", ".join(f"{v} {th[i]:+.3f}" for i, v in enumerate(COMMON)) + f"; condition number of Psi {np.linalg.cond(Psi):.0f}")
    print("   relative weights theta/theta_10y: " + ", ".join(f"{v} {th[i] / th[0]:+.3f}" for i, v in enumerate(COMMON)) + "  | FRB/US s/s_10y: " + ", ".join(f"{v} {sv[i] / sv[0]:+.3f}" for i, v in enumerate(COMMON)) + "  | market w/w_10y: " + ", ".join(f"{v} {wf[i] / wf[0]:+.3f}" for i, v in enumerate(COMMON)))
    # block bootstrap for theta ratios (months, block 24)
    rs = np.random.default_rng(7); boots = []
    s = sur["NS"]; Yb0 = Y[COMMON + ["IP"]]
    T = len(rng); blocks = 24
    for r in range(150):
        starts = rs.integers(0, T - blocks, size=T // blocks + 1)
        pick = np.concatenate([np.arange(a, a + blocks) for a in starts])[:T]
        # resample (surprise, future-path) pairs by month index: rebuild LPs on resampled months using precomputed regressors
        bb = []
        for v in COMMON + ["IP"]:
            row = []
            for h in range(H + 1):
                dy = Yb0[v].diff()
                Z = pd.concat({"y": Yb0[v].shift(-h) - Yb0[v].shift(1), "s": s.reindex(Yb0.index), **{f"dy{l}": dy.shift(l) for l in range(1, NLAG + 1)}, **{f"s{l}": s.reindex(Yb0.index).shift(l) for l in range(1, NLAG + 1)}}, axis=1).reindex(rng).iloc[pick].dropna()
                X = np.column_stack([np.ones(len(Z))] + [Z[c].values for c in Z if c not in ("y", "s")])
                pr = lambda u: u - X @ np.linalg.lstsq(X, u, rcond=None)[0]
                st, yt = pr(Z.s.values), pr(Z.y.values)
                row.append(st @ yt / (st @ st))
            bb.append(row)
        bb = np.array(bb)
        t_ = np.linalg.lstsq(bb[:3].T, bb[3], rcond=None)[0]
        boots.append(t_ / t_[0])
    boots = np.array(boots)
    print("   bootstrap 90% band for theta/theta_10y: " + ", ".join(f"{v} [{np.percentile(boots[:, i], 5):+.3f}, {np.percentile(boots[:, i], 95):+.3f}]" for i, v in enumerate(COMMON)))
    # daily event-day projections
    P.L.REAL10 = False; P.L.RSTAR = False
    X, G = P.L.build()
    dd = {"10-year": X.y10, "equities": 100 * X.lncape, "dollar": 100 * X.lnrusd}
    dates = X.index
    pos = dates.get_indexer(pd.to_datetime(d.Date))
    ok = pos > 0
    dres = {}
    for v, ser in dd.items():
        vals = ser.values; row = []
        for h in range(61):
            yv = np.array([vals[p + h] - vals[p - 1] if (p > 0 and p + h < len(vals)) else np.nan for p in pos])
            m = ~np.isnan(yv) & ok
            sx = d.ns.values[m]; yy = yv[m]
            sx_c = sx - sx.mean(); bb_ = sx_c @ (yy - yy.mean()) / (sx_c @ sx_c)
            e = yy - yy.mean() - bb_ * sx_c
            se = np.sqrt(np.sum(sx_c ** 2 * e ** 2)) / (sx_c @ sx_c)
            row.append((bb_, se))
        dres[v] = row
    print("\nDaily event-day responses to a 1 pp NS surprise (funds-rate pp), selected trading days:")
    for v in dd:
        print(f"  {v:9s} " + "  ".join(f"h={h}: {dres[v][h][0]:+.2f} ({dres[v][h][1]:.2f})" for h in (0, 1, 5, 10, 20, 40, 60)))
    gd = [sum((sv[i] - wf[i]) * dres[v][h][0] for i, v in enumerate(COMMON)) for h in range(61)]
    print("  gap (s - w)'psi_h, common variables: " + "  ".join(f"h={h}: {gd[h]:+.2f}" for h in (0, 1, 5, 10, 20, 40, 60)))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    hh = np.arange(H + 1)
    for ax, v in zip(axes.flat[:3], COMMON):
        m = np.array([b[(v, h)] for h in hh]); se = np.array([np.sqrt(V.loc[(v, h), (v, h)]) for h in hh])
        ax.plot(hh, m, color="#1f5fa8", lw=1.6); ax.fill_between(hh, m - 1.645 * se, m + 1.645 * se, color="#1f5fa8", alpha=0.15)
        ax.axhline(0, color="gray", lw=0.8); ax.set_title(f"{v}: response to a 1 pp NS surprise (90% band)", fontsize=10); ax.set_xlabel("months"); ax.grid(alpha=0.25)
    ax = axes.flat[3]
    R = out[out.surprise == "NS"]
    for col, c, lab in (("market_reading", "#ff7f0e", "market weights w'psi_h"), ("macro_reading_common", "#d62728", "FRB/US weights s'psi_h (common variables)"), ("gap_with_macro_only", "black", "gap (macro minus market)")):
        ax.plot(R.h, R[col], color=c, lw=1.6, marker="o", ms=3, label=lab)
    ax.fill_between(R.h, R.gap_with_macro_only - 1.645 * R.gap_se, R.gap_with_macro_only + 1.645 * R.gap_se, color="black", alpha=0.1)
    ax.axhline(0, color="gray", lw=0.8); ax.grid(alpha=0.25); ax.legend(fontsize=8, frameon=False); ax.set_xlabel("months")
    ax.set_title("Readings of the response by static weights (pp of funds rate)", fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "psi_by_horizon.png"), dpi=130)
    fig, ax = plt.subplots(figsize=(11, 5))
    for v, c in zip(COMMON, ("#1f5fa8", "#2ca02c", "#9467bd")):
        r0 = dres[v][0][0]
        ax.plot(range(61), [dres[v][h][0] / r0 for h in range(61)], color=c, lw=1.5, label=f"{v} (impact {r0:+.2f})")
    ax.axhline(1, color="gray", lw=0.8, ls="--"); ax.axhline(0, color="gray", lw=0.8); ax.grid(alpha=0.25); ax.legend(frameon=False)
    ax.set_title("Event-day responses relative to impact, trading days after the FOMC announcement (NS surprise)", fontsize=10); ax.set_xlabel("trading days")
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "psi_daily.png"), dpi=130)


if __name__ == "__main__":
    main()
