"""Chudik-Georgiadis (2019 Dallas Fed GWP 356; JBES 2022) mixed-frequency distributed-lag (MFDL) check: the monthly outcome regressed DIRECTLY on the
daily (event-day) shocks, without any financial-conditions channel. This is the comparison for the window-identified MIDAS-VAR (midas_step.py),
which assumes the shock reaches macro only through the policy rate and the market index.

Set-up. Daily response b_l (l = weekdays after the event day) of an outcome observed as a monthly average:
   x_s = (1/n_s) sum_{tau in month s} sum_i b_{tau - p_i} e_i + error,       e_i = shock on event day p_i.
Unrestricted MFDL (one coefficient per day position and monthly lag) is far too large for ~260 sparse events, so the RESTRICTED MFDL (their section
2.3.2) is used: b_l is piecewise linear in l with knots at 0, 1, 2, 3, 6, 9, 12, 18, 24, 30, 36 months (21.7 weekdays a month) and b_l = 0 after 36
months (truncation lag p). Then x_s is linear in the knot values theta, with regressors built exactly from each event's day in the month; OLS.
Outcomes: unemployment gap in levels (pure DL, as in CG; Newey-West, 36 lags) and in first differences (same theta, differenced regressors; Newey-West
12 lags), and the core PCE price level in first differences (dependent variable = monthly core PCE rate / 12, so theta = price-level response in %).
Shock units: per +1 pp window move in the 2-year yield (NS, NS-GB: shock times the window slope of UST2Y on the shock) or in the funds rate (MP1).
Sample: 1994-02..2026-09 (dependent months), 2020-03..12 dropped, events with a valid shock from 1994-02. Inference: HAC, and a permutation test (shock values reshuffled across the same event dates, 500 times) for the 12-month response. Output: direct_mfdl.log, direct_mfdl.csv"""
import numpy as np, pandas as pd, statsmodels.api as sm
from mf_common import EV, SHOCKS, CAL, MONTH, NB, M

KNOTS_M = np.array([0, 1, 2, 3, 6, 9, 12, 18, 24, 30, 36]); DPM = 21.7
KN = np.round(KNOTS_M * DPM).astype(int); LMAX = KN[-1]
REPORT = (6, 12, 24, 36)

def hats(l, flat=False):
    """Hat-function basis at day l (piecewise-linear interpolation between knots). After the last knot: zero (levels; CG truncation) or held at the
    last knot value (differences: the change in the response is truncated, so the level response stays at its 36-month value)."""
    out = np.zeros(len(KN))
    if l > LMAX:
        if flat: out[-1] = 1.0
        return out
    j = np.searchsorted(KN, l, side="right") - 1
    if j == len(KN) - 1: out[j] = 1.0; return out
    w = (l - KN[j]) / (KN[j + 1] - KN[j]); out[j] = 1 - w; out[j + 1] = w; return out

LFLAT = 2 * LMAX
BASIS = {False: np.array([hats(l) for l in range(LMAX + 1)]), True: np.array([hats(l, True) for l in range(LFLAT + 1)])}
MI = MONTH.values; NBV = NB.values

def scaled_shock(sk, drop=None):
    s = SHOCKS[sk]
    ok = s.notna().values & EV.p.notna().values & (EV.d >= "1994-02-01").values
    if drop: ok &= ~((EV.d >= drop[0]) & (EV.d <= drop[1])).values
    if sk == "MP1": scale = 1.0                                   # MP1 is the funds-rate window move
    else:
        x = s[ok].values; y = EV.UST2Y[ok].values; g = ~np.isnan(y)
        xc = x[g] - x[g].mean(); scale = np.sum(xc * (y[g] - y[g].mean())) / np.sum(xc * xc)
    return np.where(ok)[0], s.values * scale

def unit_contrib(idx, months, flat):
    """C[i, s, j] = (1/n_s) sum_{tau in month s} basis_j(tau - p_i): monthly-average regressor of a unit shock on event i's day."""
    C = np.zeros((len(idx), len(months), len(KN))); Bs = BASIS[flat]; pos = {m: k for k, m in enumerate(months)}
    for a, i in enumerate(idx):
        p = int(EV.p[i]); last = min(p + len(Bs) - 1, len(CAL) - 1); taus = np.arange(p, last + 1)
        g = pd.DataFrame(Bs[taus - p] / NBV[taus][:, None]).groupby(MI[taus]).sum()
        for m, row in zip(g.index, g.values):
            if m in pos: C[a, pos[m]] = row
    return C

def regressors(e, C, months):
    """Monthly-average regressors for each knot value: R[s, j] = sum_i e_i C[i, s, j]."""
    return pd.DataFrame(np.tensordot(e, C, axes=1), index=months, columns=range(len(KN)))

def fit(y, R, diff, nw):
    D = pd.concat([y.rename("y"), R], axis=1)
    if diff: D = D.diff()
    D = D[(D.index >= pd.Period("1994-02", "M")) & (D.index <= pd.Period("2026-09", "M"))]
    D = D[~((D.index.year == 2020) & (D.index.month >= 3))].dropna()
    # with differences, also drop 2021-01 (its difference spans the dropped months)
    if diff: D = D[D.index != pd.Period("2021-01", "M")]
    X = sm.add_constant(D.drop(columns="y").values)
    r = sm.OLS(D.y.values, X).fit(cov_type="HAC", cov_kwds={"maxlags": nw})
    th, V = r.params[1:], r.cov_params()[1:, 1:]
    F = float(th @ np.linalg.solve(V, th) / len(th))
    return th, np.sqrt(np.diag(V)), len(D), F

if __name__ == "__main__":
    months = pd.period_range("1990-01", "2026-10", freq="M")
    U = M.u_gap.reindex(months); PL = (M.pi_core / 12).reindex(months)
    out = []
    print("Chudik-Georgiadis restricted MFDL: direct regression of the monthly outcome on event-day shocks (no financial channel imposed)")
    print("Response at a horizon of h months = knot value theta_h (daily response h*21.7 weekdays after the event; comparable to month t+h in the VAR)")
    print("Units: pp of the unemployment gap, or % of the core PCE price level, per +1 pp window move in the 2-year (NS, NS-GB) or funds rate (MP1); 90% = 1.645 HAC se\n")
    CRISIS = ("2007-08-01", "2009-06-30")
    rng = np.random.default_rng(7); NPERM = 500; j12 = list(KNOTS_M).index(12)
    for sk, drop in (("NS", None), ("NS-GB", None), ("MP1", None), ("NS", CRISIS), ("MP1", CRISIS)):
        idx, e = scaled_shock(sk, drop); e = e[idx]; nev = len(idx)
        Cl, Cd = unit_contrib(idx, months, False), unit_contrib(idx, months, True)
        Rl, Rd = regressors(e, Cl, months), regressors(e, Cd, months)
        if drop: print(f"--- events {drop[0]}..{drop[1]} dropped")
        for lab, y, diff, nw in (("u gap, levels (pure DL)", U, False, 36), ("u gap, differences", U, True, 12), ("core PCE price level, differences", None, True, 12)):
            th, se, n, F = fit(PL.cumsum() if y is None else y, Rd if diff else Rl, diff, nw)   # price level = cumulated monthly core PCE rate / 12
            perm = np.array([fit(PL.cumsum() if y is None else y, regressors(rng.permutation(e), Cd if diff else Cl, months), diff, nw)[0][j12] for _ in range(NPERM)])
            pp = float(np.mean(np.abs(perm) >= abs(th[j12])))
            line = "  ".join(f"h{h} {th[list(KNOTS_M).index(h)]:+.2f} [{th[list(KNOTS_M).index(h)] - 1.645 * se[list(KNOTS_M).index(h)]:+.2f},{th[list(KNOTS_M).index(h)] + 1.645 * se[list(KNOTS_M).index(h)]:+.2f}]" for h in REPORT)
            print(f"{sk:6s} {lab:34s} ({nev} events, {n} months): {line}   joint F {F:.2f}   permutation: h12 null 90% [{np.percentile(perm, 5):+.2f},{np.percentile(perm, 95):+.2f}], p {pp:.2f}", flush=True)
            out.append(dict(shock=sk, drop="crisis" if drop else "", outcome=lab, events=nev, months=n, F=F, perm_p12=pp, perm_lo12=np.percentile(perm, 5), perm_hi12=np.percentile(perm, 95), **{f"th{h}": th[j] for j, h in enumerate(KNOTS_M)}, **{f"se{h}": se[j] for j, h in enumerate(KNOTS_M)}))
        print()
    pd.DataFrame(out).to_csv("direct_mfdl.csv", index=False, float_format="%.4f")


# ---------------------------------------------------------------- Chudik-Kilian (2026, Dallas Fed WP 2603) pooled ARDL estimator
def monthly_sum(e, idx, months):
    """Pooled regressor for a shock on a uniformly random day of the month: omega_i = 1/m, so omega-tilde_i = 1 and e~_s = sum of shocks in month s."""
    s = pd.Series(e, index=[EV.d[i].to_period("M") for i in idx]).groupby(level=0).sum()
    return s.reindex(months).fillna(0.0)

def ardl(y, es, p, h, months):
    """x_s = c + sum_{r=1}^p phi_r x_{s-r} + sum_{r=0}^h delta_r e~_{s-r} + v; IRF d_0 = delta_0, d_l = delta_l + sum_r phi_r d_{l-r} (their eqs 61-65)."""
    D = pd.DataFrame({"y": y}, index=months)
    for r in range(1, p + 1): D[f"y{r}"] = y.shift(r)
    for r in range(h + 1): D[f"e{r}"] = es.shift(r)
    D = D[(D.index >= pd.Period("1994-02", "M")) & (D.index <= pd.Period("2026-09", "M"))]
    bad = (D.index.year == 2020) & (D.index.month >= 3) | ((D.index >= pd.Period("2021-01", "M")) & (D.index <= pd.Period(f"2021-{p:02d}", "M")) if p <= 12 else False)
    D = D[~bad].dropna()
    r = sm.OLS(D.y.values, sm.add_constant(D.drop(columns="y").values)).fit()
    phi, dl = r.params[1:1 + p], r.params[1 + p:]
    d = np.zeros(h + 1)
    for l in range(h + 1): d[l] = dl[l] + sum(phi[k - 1] * d[l - k] for k in range(1, min(p, l) + 1))
    return d, len(D)

def ardl_main():
    months = pd.period_range("1990-01", "2026-10", freq="M")
    U = M.u_gap.reindex(months); PI = (M.pi_core / 12).reindex(months)
    rng = np.random.default_rng(11); NPERM = 500; out = []
    print("\nChudik-Kilian pooled ARDL (12 own lags, shock lags 0..36; pooled regressor = monthly sum of shocks, i.e. a shock on a uniformly random day)")
    print("u gap: d_h in pp; core PCE: monthly rate/12 as dependent, cumulated to the price level (%). Same units as above. Null 90% = permutation of shock values across event dates\n")
    CRISIS = ("2007-08-01", "2009-06-30")
    for sk, drop in (("NS", None), ("NS-GB", None), ("MP1", None), ("NS", CRISIS), ("MP1", CRISIS)):
        idx, e = scaled_shock(sk, drop); e = e[idx]; es = monthly_sum(e, idx, months)
        for lab, y, cum in (("u gap", U, False), ("core PCE price level", PI, True)):
            d, n = ardl(y, es, 12, 36, months); d = np.cumsum(d) if cum else d
            perm = []
            for _ in range(NPERM):
                dp, _ = ardl(y, monthly_sum(rng.permutation(e), idx, months), 12, 36, months); perm.append(np.cumsum(dp) if cum else dp)
            perm = np.array(perm); lo, hi = np.percentile(perm, [5, 95], axis=0)
            pv = {h: float(np.mean(np.abs(perm[:, h]) >= abs(d[h]))) for h in REPORT}
            tag = f"{sk}{' (crisis events dropped)' if drop else ''}"
            print(f"{tag:32s} {lab:22s} ({len(idx)} events, {n} months): " + "  ".join(f"h{h} {d[h]:+.2f} (null [{lo[h]:+.2f},{hi[h]:+.2f}], p {pv[h]:.2f})" for h in REPORT), flush=True)
            out.append(dict(shock=sk, drop="crisis" if drop else "", outcome=lab, **{f"d{h}": d[h] for h in REPORT}, **{f"nlo{h}": lo[h] for h in REPORT}, **{f"nhi{h}": hi[h] for h in REPORT}, **{f"p{h}": pv[h] for h in REPORT}))
    pd.DataFrame(out).to_csv("direct_ardl.csv", index=False, float_format="%.4f")

if __name__ == "__main__":
    ardl_main()
