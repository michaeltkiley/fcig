"""MIDAS-VAR (route A extended). Observation-driven, estimated equation by equation; no latent states.
DAILY financial block f = [policy (2-year or funds rate), market index (r*-gap)]: HAR-VAR in levels (1-, 5-, 22-, 66-day averages) + lagged monthly macro, OLS, 1990-.
MONTHLY macro equations (unemployment gap, core PCE):  m_t = c + sum_{l=1}^{6} A_l m_{t-l} + sum_k beta_k sum_{j=0}^{251} w_j(theta_k) f_k[tau_{t-1} - j] + e_t
   with f_k the DAILY level of financial variable k on the j-th weekday before the start of month t (last 252 weekdays = 12 months) and ONE-parameter exponential MIDAS weights w_j(theta) proportional to exp(-theta j/252), normalised to sum to one, theta in [-8, 8]
   (estimated by nonlinear least squares; theta = 0 gives equal weights, i.e. the monthly-average structure of route A). A two-parameter Almon polynomial ran to its bounds (the financial weights are not identified because the equation is almost entirely autoregressive), hence the restriction. Months 2020-03 to 2020-12 are dropped from the macro equations. No contemporaneous financial regressor in the macro equations (macro does not respond in the event month).
Daily index = nominal daily index (from the note's weights, 1990-) plus a smooth (mid-month interpolated) offset so that its monthly average equals the monthly r*-gap index; before 1990 the monthly r*-gap index interpolated between mid-months. Daily policy: DGS2 (from 1976-06) or DFF (from 1954).
IRF: window impact vector b (30-minute windows; credit spread excluded; macro zero) applied on the event day, then simulated forward. Two variants of the post-window financial path:
   MODEL: the daily block's own dynamics throughout;
   PATH : the directly estimated cumulative daily response (window local projection) through the END OF MONTH t+1, then the daily block takes over (the user's proposal, 31 Oct).
Event day drawn from six empirical position bins. Uncertainty: 50 draws over events (shock responses, positions) and a residual bootstrap of the macro equations (regressors held fixed).
Output: midas_var.log, midas_var.csv"""
import sys, time, numpy as np, pandas as pd
from scipy.optimize import least_squares
import mf_common as F
from mf_common import *
from route_a_pos import positions
rng = np.random.default_rng(11)
J, LM, HAR, H = 252, 6, (1, 5, 22, 66), 36

# ---------------------------------------------------------------- daily series on a weekday calendar
CALW = pd.bdate_range("1972-01-03", "2026-10-30")
def interp_monthly(s):
    """Monthly (PeriodIndex) series -> smooth daily series on CALW by linear interpolation between mid-month dates."""
    s = s.dropna(); mid = pd.to_datetime([p.to_timestamp() + pd.Timedelta(days=14) for p in s.index])
    return pd.Series(np.interp(CALW.asi8, mid.asi8, s.values, left=np.nan, right=s.values[-1]), index=CALW)
def daily_idx():
    nom = DAILY["idx"].reindex(CALW).ffill(limit=3)
    mnom = nom.groupby(nom.index.to_period("M")).mean(); off = (M.market_rstar - mnom).dropna()
    offd = interp_monthly(off)
    out = nom + offd                                                    # 1990-: nominal daily + smooth offset
    pre = interp_monthly(M.market_rstar)
    return out.where(nom.notna(), pre)
IDX = daily_idx()
POL = {"y2": fred("DGS2").reindex(CALW).ffill(limit=3), "ff": fred("DFF").reindex(CALW).ffill(limit=3)}
MON = CALW.to_period("M"); LASTDAY = pd.Series(np.arange(len(CALW)), index=CALW).groupby(MON).max()    # position of the last weekday of each month

def har_block(pol):
    D = pd.DataFrame({"pol": POL[pol], "idx": IDX}).loc["1990-01-02":].dropna(); mo = D.index.to_period("M")
    mac = pd.DataFrame({"u": M.u_gap, "p": M.pi_core}).reindex(mo - 1).values
    X = np.column_stack([np.ones(len(D))] + [D.rolling(h).mean().shift(1).values for h in HAR] + [mac]); Y = D.values
    ok = ~np.isnan(X).any(axis=1) & ~np.isnan(Y).any(axis=1)
    return np.linalg.lstsq(X[ok], Y[ok], rcond=None)[0]

def macro_data(pol, first_month):
    """Regressors for months t >= first_month: macro lags, and the (T x 2 x J) matrix of daily financial levels before the start of month t."""
    ms = [p for p in M.index if p >= pd.Period(first_month, "M") and p <= pd.Period("2026-09", "M") and not (p.year == 2020 and p.month >= 3)]
    fin = np.stack([POL[pol].values, IDX.values], axis=1); rows, Xf, Y, Xm = [], [], [], []
    for p in ms:
        tau0 = LASTDAY[p - 1]; w = fin[tau0 - J + 1:tau0 + 1][::-1]            # j = 0 is the last day of month t-1
        lags = [M[["u_gap", "pi_core"]].loc[p - l].values for l in range(1, LM + 1)]
        if w.shape[0] < J or np.isnan(w).any() or np.isnan(np.concatenate(lags)).any() or np.isnan(M[["u_gap", "pi_core"]].loc[p].values).any(): continue
        rows.append(p); Xf.append(w.T); Y.append(M[["u_gap", "pi_core"]].loc[p].values); Xm.append(np.concatenate(lags))
    return rows, np.array(Xf), np.array(Y), np.array(Xm)

def weights(theta):
    """One-parameter exponential MIDAS weights: w_j proportional to exp(-theta * j/J); theta > 0 puts more weight on recent days, theta = 0 is equal weights."""
    x = np.arange(J) / J; z = -theta * x; z -= z.max(); w = np.exp(z); return w / w.sum()

def fit_eq(y, Xm, Xf, init=None):
    """NLS for one equation: params [c, a (2*LM), beta (2), theta (2 x 2)]."""
    T = len(y)
    def pred(p):
        c, a, beta, th = p[0], p[1:1 + 2 * LM], p[1 + 2 * LM:3 + 2 * LM], p[3 + 2 * LM:]
        z = np.column_stack([Xf[:, k, :] @ weights(th[k]) for k in range(2)])
        return c + Xm @ a + z @ beta
    if init is None:
        Z = np.column_stack([np.ones(T), Xm, Xf.mean(axis=2)]); b0 = np.linalg.lstsq(Z, y, rcond=None)[0]; init = np.r_[b0, np.zeros(2)]
    lb = np.r_[np.full(3 + 2 * LM, -np.inf), np.full(2, -8.0)]; ub = np.r_[np.full(3 + 2 * LM, np.inf), np.full(2, 8.0)]
    r = least_squares(lambda p: y - pred(p), init, bounds=(lb, ub), method="trf", x_scale="jac", max_nfev=200)
    return r.x, y - pred(r.x), pred(r.x)

def parts(p):
    return p[1:1 + 2 * LM].reshape(LM, 2), p[1 + 2 * LM:3 + 2 * LM], p[3 + 2 * LM:]

def simulate(Bd, mp, b_day, k0, n0, path=None, months=H + 1, nother=21):
    """mp: list of two parameter vectors (u, pi equations)."""
    off = J; nd = n0 + nother * (months - 1); f = np.zeros((nd + off, 2)); macro = np.zeros((months, 2))
    lens = [n0] + [nother] * (months - 1); start = np.concatenate([[0], np.cumsum(lens)])
    W = [[weights(parts(mp[i])[2][k]) for k in range(2)] for i in range(2)]
    He = (n0 - 1 - k0) + nother                                           # last horizon (days after the event day) inside month t+1
    for t in range(months):
        if t >= 1:
            for i in range(2):
                a, beta, th = parts(mp[i]); m = 0.0
                for l in range(1, LM + 1):
                    if t - l >= 0: m += a[l - 1] @ macro[t - l]
                for k in range(2):
                    seg = f[off + start[t] - J:off + start[t]][::-1, k]; m += beta[k] * (W[i][k] @ seg)
                macro[t, i] = m
        for tau in range(start[t], start[t + 1]):
            if tau < k0: continue
            if tau == k0: f[off + tau] = b_day; continue
            if path is not None and tau - k0 <= min(He, HZ): f[off + tau] = path[tau - k0]; continue
            x = np.concatenate([[0.0]] + [f[off + tau - h:off + tau].mean(axis=0) for h in HAR] + [macro[t - 1] if t >= 1 else np.zeros(2)])
            f[off + tau] = x @ Bd
    return macro

def irf(Bd, mp, P, fin_d, idx, pos, sk, use_path):
    wr = win_response(sk, idx); b_day = np.array([wr["ff" if v == "ff" else "y2" if v == "y2" else "idx"] for v in fin_d])
    path = np.column_stack([np.concatenate([[b_day[j]], P[v][1:HZ + 1]]) for j, v in enumerate(fin_d)]) if use_path else None
    tot = np.zeros((H + 1, 2))
    for k0, n0, w in pos: tot += w * simulate(Bd, mp, b_day, k0, n0, path)
    return tot

SPECS = [("long 1977- (2-year)", "y2", "1977-06"), ("short 1994- (2-year)", "y2", "1994-02"), ("long 1974- (funds rate)", "ff", "1974-01")]
if __name__ == "__main__":
    B = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    rows = []; t0 = time.time()
    print("MIDAS-VAR: unemployment-gap response (pp) per +1 pp event-day rise in the scaling variable; median [90% interval]; MODEL = daily block dynamics; PATH = direct daily response through the end of month t+1, then the model\n")
    for lab, pol, fm in SPECS:
        Bd = har_block(pol); mon, Xf, Y, Xm = macro_data(pol, fm)
        fits = [fit_eq(Y[:, i], Xm, Xf) for i in range(2)]; mp0 = [f[0] for f in fits]; res = np.column_stack([f[1] for f in fits]); fitted = np.column_stack([f[2] for f in fits])
        wu = [weights(parts(mp0[0])[2][k]) for k in range(2)]
        print(f"=== {lab}: macro-equation sample {mon[0]}..{mon[-1]} ({len(mon)} months); u-equation: beta policy {parts(mp0[0])[1][0]:+.3f}, beta index {parts(mp0[0])[1][1]:+.3f}; MIDAS theta policy {parts(mp0[0])[2][0]:+.1f}, index {parts(mp0[0])[2][1]:+.1f}; "
              f"share of weight on the most recent 63 days: policy {wu[0][:63].sum():.2f}, index {wu[1][:63].sum():.2f} (equal weights = 0.25); R2 u {1 - res[:, 0].var() / Y[:, 0].var():.3f}", flush=True)
        for sk in ("NS", "NS-GB") + (("MP1",) if pol == "ff" else ()):
            fin_d = ["ff" if pol == "ff" else "y2", "idx"]; idx0 = event_index(sk); P0, _, idx0 = slopes(idx0, sk); pos0 = positions(idx0)
            out = {}
            for var, use_path in (("MODEL", False), ("PATH", True)):
                base = irf(Bd, mp0, P0, fin_d, idx0, pos0, sk, use_path); dr = []
                for _ in range(B):
                    ib = rng.choice(idx0, size=len(idx0), replace=True); Pb, _, ib = slopes(ib, sk); posb = positions(ib)
                    ystar = fitted + res[rng.integers(0, len(res), size=len(res))]
                    mpb = [fit_eq(ystar[:, i], Xm, Xf, init=mp0[i])[0] for i in range(2)]
                    dr.append(irf(Bd, mpb, Pb, fin_d, ib, posb, sk, use_path)[:, 0])
                dr = np.array(dr); lo, hi = np.percentile(dr, [5, 95], axis=0); out[var] = (base, lo, hi, dr)
                rows.append(dict(shock=sk, spec=lab, variant=var, u12=base[12, 0], lo12=lo[12], hi12=hi[12], u24=base[24, 0], lo24=lo[24], hi24=hi[24], u36=base[36, 0], pi12=base[12, 1], P12=float(np.mean(dr[:, 12] > 0))))
            for var in ("MODEL", "PATH"):
                b_, lo, hi, dr = out[var]
                print(f"   {sk:6s} {var:5s}: u12 {b_[12, 0]:+.3f} [{lo[12]:+.3f},{hi[12]:+.3f}]  u24 {b_[24, 0]:+.3f} [{lo[24]:+.3f},{hi[24]:+.3f}]  u36 {b_[36, 0]:+.3f}  P(u12>0) {np.mean(dr[:, 12] > 0):.2f}  | core PCE 12m {b_[12, 1]:+.2f}   ({time.time() - t0:.0f}s)", flush=True)
        print()
    pd.DataFrame(rows).to_csv("midas_var.csv", index=False, float_format="%.4f")
