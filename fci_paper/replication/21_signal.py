"""Step 21. How much of the dollar-over-equity contrast between the FRB/US weights and the market weights depends on what is called policy news? (colleague report, p. 2.)

DESIGN (descriptive; no hypothesis tests; intervals are 5th-95th percentiles of announcement-bootstrap draws; contrasts across definitions use COMMON draws)
 definitions of the policy-news signal s in the announcement windows (the market portfolio recovers s from the three window moves by one-factor GLS, w'psi = 1; same code as 02_weights.py):
   baseline        Nakamura-Steinsson futures factor (first principal component of MP1, MP2, ED2, ED3, ED4), all announcements
   two_year        the window change of the two-year yield itself, the same announcements
   to_2019         futures factor, announcements before 2020
   no_lower_bound  futures factor, announcements outside 2008-12 .. 2015-11
 FRB/US weights b (GDP effect at four quarters of a persistent unit shift / that of a persistent 1 pp funds-rate rise) are fixed; w_B = b / (b'psi) is re-normalized for each definition and draw.
 Bootstrap: R draws of announcement indices (same generator and order as 02_weights.py, so the baseline reproduces results/weights_boot.csv); a definition on a subsample uses the announcements
 of the SAME draw that fall in its subsample, so the draws are paired across definitions [inference: the subsample size varies by draw].
 part A   weights, b'psi, dollar-over-equity ratios of effects, ratio of ratios, and the dollar-minus-equity contrast in points, per definition
 part B   paired differences, two_year minus baseline (and the other two), on common draws
 part C   counterfactual: weights built from (psi of one signal, Sigma of the other); both orders; single elements (psi_k; residual sd vs residual correlations)
 part D   what variation each signal captures (correlation of the signals, R2 and residual covariance of the regressions, regressions on both signals)
 part E   carried through: 12-month changes 1996-2026 (r* step): mean |D| (points, basis points) and its ratio to the mean |market move|; held-out announcement windows (leave-one-event-out
          within the definition); matched episode readings 1998-2001, 2004-06, 2022-24 (12-month changes, same construction as step 19: market, FRB/US, D, contributions of each asset), levels
 part F   FCI-G multipliers (data/multipliers.csv) as a second spending calibration: row 0 (effect on growth over the next four quarters of a shift now = four-quarter effect of a persistent shift)
 Writes results/21_*.csv and scalars_21_signal.csv."""
import time
import numpy as np, pandas as pd
from lib import data, cases, indexes as I
from lib.agree_core import MV, load_frbus, b_persist, ns_arr, mbb
from lib.config import RES, DATA, REPS_W as REPS, SEED, START, END
from lib.report import Scalars

T0 = time.time()
S = Scalars("21_signal")
TAB = {}
def add(tab, **kw): TAB.setdefault(tab, []).append(kw)
def ci(a, lo=5, hi=95):
    a = np.nan_to_num(np.asarray(a, float), nan=np.nan, posinf=1e9, neginf=-1e9)
    return float(np.nanpercentile(a, lo)), float(np.nanpercentile(a, hi))

EQ, USD = -5.0, 3.9                                  # the illustrative movements (equity valuation -5 log points, dollar +3.9)
raw = I.events_raw(); n = len(raw)
X5 = raw[["MP1", "MP2", "ED2", "ED3", "ED4"]].values; u2 = raw.UST2Y.values; Y3 = raw[["UST10Y", "SP500", "DXY"]].values
dates = raw.Date
MASK = {"baseline": np.ones(n, bool), "two_year": np.ones(n, bool), "to_2019": (dates < "2020-01-01").values,
        "no_lower_bound": ((dates < "2008-12-01") | (dates >= "2015-12-01")).values}
KIND = {"baseline": "ns", "two_year": "ust2y", "to_2019": "ns", "no_lower_bound": "ns"}
DEFS = list(MASK)


def signal(rows, kind):
    return ns_arr(X5[rows], u2[rows]) if kind == "ns" else u2[rows]


def fitg(f, Y):
    """One-factor GLS (same algebra as lib.indexes.gls_weights): responses psi, residual covariance Sigma (ddof 2), weights w with w'psi = 1."""
    fc = f - f.mean(); Yc = Y - Y.mean(0)
    psi = (fc @ Yc) / (fc @ fc)
    Rr = Yc - np.outer(fc, psi)
    Sg = Rr.T @ Rr / (len(f) - 2)
    w = np.linalg.solve(Sg, psi)
    return w / (psi @ w), psi, Sg


def est(rows, kind):
    return fitg(signal(rows, kind), Y3[rows])


# ---------------------------------------------------------------- FRB/US weights and checks against the stored results
R_, G = load_frbus()
b = b_persist(R_, G, 4)
mw = pd.read_csv(RES / "market_weights.csv", index_col=0)
wM0, psi0 = mw.weight.values, mw.response.values
P_, G_ = I.frbus_paths(); assert np.allclose(I.phi_at(P_, 4)[MV].values / G_[4], b)
POINT = {}
for d in DEFS:
    rows = np.where(MASK[d])[0]
    POINT[d] = est(rows, KIND[d])
w_, p_, _ = POINT["baseline"]
assert np.allclose(w_, wM0, atol=1e-8) and np.allclose(p_, psi0, atol=1e-8)
WV = pd.read_csv(RES / "weights_variants.csv").set_index("variant")
for d in DEFS:
    assert np.allclose(POINT[d][0], WV.loc[d, ["w_ten", "w_eq", "w_usd"]].values.astype(float), atol=1e-8), d
    assert np.allclose(POINT[d][1], WV.loc[d, ["psi_ten", "psi_eq", "psi_usd"]].values.astype(float), atol=1e-8), d
S.add("check_points_match_weights_variants", 1)

rng = np.random.default_rng(SEED)
IX = np.array([rng.integers(0, n, n) for _ in range(REPS)])
R = len(IX)
Bd = pd.read_csv(RES / "weights_boot.csv").iloc[:REPS]
BW = {d: np.empty((R, 3)) for d in DEFS}; BP = {d: np.empty((R, 3)) for d in DEFS}; BS = {d: np.empty((R, 3, 3)) for d in DEFS}
for r in range(R):
    ix = IX[r]
    for d in DEFS:
        rows = ix[MASK[d][ix]]
        BW[d][r], BP[d][r], BS[d][r] = est(rows, KIND[d])
mxd = float(np.abs(BW["baseline"] - Bd[["w_ten", "w_eq", "w_usd"]].values).max())
mxp = float(np.abs(BP["baseline"] - Bd[["psi_ten", "psi_eq", "psi_usd"]].values).max())
S.add("check_boot_maxdiff_w", mxd); S.add("check_boot_maxdiff_psi", mxp)
assert mxd < 1e-6 and mxp < 1e-6, (mxd, mxp)                       # the baseline draws are the stored draws

# ---------------------------------------------------------------- part A: per definition
NM = ("ten", "eq", "usd")
def stats(w, psi, bb=b):
    """Quantities for one (w_M, psi) pair; FRB/US weights bb fixed and re-normalized."""
    bp = bb @ psi; wB = bb / bp
    eq_m, us_m = w[1] * EQ, w[2] * USD; eq_f, us_f = wB[1] * EQ, wB[2] * USD
    rm = us_m / eq_m; rf = us_f / eq_f
    return dict(bpsi=bp, eq_mkt=eq_m, usd_mkt=us_m, eq_fr=eq_f, usd_fr=us_f, ratio_mkt=rm, ratio_fr=rf, ror=rf / rm,
                contrast_mkt=us_m - eq_m, contrast_fr=us_f - eq_f, contrast_diff=(us_f - eq_f) - (us_m - eq_m), wB_ten=wB[0], wB_eq=wB[1], wB_usd=wB[2])
ST = {d: stats(*POINT[d][:2]) for d in DEFS}
STB = {d: [stats(BW[d][r], BP[d][r]) for r in range(R)] for d in DEFS}
def col(d, k): return np.array([s[k] for s in STB[d]])
for d in DEFS:
    w, psi, Sg = POINT[d]
    add("defs", definition=d, quantity="n_announcements", point=int(MASK[d].sum()), lo=np.nan, hi=np.nan)
    for k, a in enumerate(NM):
        add("defs", definition=d, quantity=f"psi_{a}", point=psi[k], lo=ci(BP[d][:, k])[0], hi=ci(BP[d][:, k])[1])
        add("defs", definition=d, quantity=f"wM_{a}", point=w[k], lo=ci(BW[d][:, k])[0], hi=ci(BW[d][:, k])[1])
        S.add(f"{d}_psi_{a}", psi[k]); S.add(f"{d}_wM_{a}", w[k]); S.add(f"{d}_wM_{a}_lo", ci(BW[d][:, k])[0]); S.add(f"{d}_wM_{a}_hi", ci(BW[d][:, k])[1])
    for k, v in ST[d].items():
        l, u = ci(col(d, k)); add("defs", definition=d, quantity=k, point=v, lo=l, hi=u); S.add(f"{d}_{k}", v); S.add(f"{d}_{k}_lo", l); S.add(f"{d}_{k}_hi", u)
    for k in ("ratio_mkt", "ror"):
        c_ = col(d, k); add("defs", definition=d, quantity=f"{k}_share_draws_nonpositive", point=float((c_ <= 0).mean()), lo=np.nan, hi=np.nan)
        S.add(f"{d}_{k}_share_nonpositive", float((c_ <= 0).mean()))
    add("defs", definition=d, quantity="share_draws_weq_positive", point=float((BW[d][:, 1] > 0).mean()), lo=np.nan, hi=np.nan); S.add(f"{d}_share_weq_positive", float((BW[d][:, 1] > 0).mean()))
    for i_, a in enumerate(NM):
        for j_, c2 in enumerate(NM):
            add("sigma", definition=d, row=a, col=c2, point=Sg[i_, j_], sd_or_corr=np.sqrt(Sg[i_, i_]) if i_ == j_ else Sg[i_, j_] / np.sqrt(Sg[i_, i_] * Sg[j_, j_]))
# verification against the stored step-18 baseline
E18 = pd.read_csv(RES / "18_example.csv"); sel = lambda ix_, q: E18[(E18.h == 4) & (E18["index"] == ix_) & (E18.quantity == q)].iloc[0]
rr18 = sel("frbus_over_market", "ratio_of_ratios"); bp18 = sel("frbus_b", "joint_response")
S.add("check_ror_stored", rr18.point); S.add("check_ror_stored_lo", rr18.lo); S.add("check_ror_stored_hi", rr18.hi)
assert abs(ST["baseline"]["ror"] - rr18.point) < 1e-5 and abs(ST["baseline"]["bpsi"] - bp18.point) < 1e-5
rl, ru = ci(col("baseline", "ror")); assert abs(rl - rr18.lo) < 1e-4 and abs(ru - rr18.hi) < 1e-3, (rl, ru, rr18.lo, rr18.hi)
S.add("check_baseline_reproduces", 1)

# ---------------------------------------------------------------- part B: paired differences vs baseline
QS = ["bpsi", "ror", "ratio_mkt", "ratio_fr", "contrast_mkt", "contrast_fr", "contrast_diff", "eq_mkt", "usd_mkt", "wB_eq", "wB_usd"]
for d in DEFS[1:]:
    for q in QS + [f"wM_{a}" for a in NM]:
        if q.startswith("wM_"):
            k = NM.index(q[3:]); pt = POINT[d][0][k] - POINT["baseline"][0][k]; dr = BW[d][:, k] - BW["baseline"][:, k]
        else:
            pt = ST[d][q] - ST["baseline"][q]; dr = col(d, q) - col("baseline", q)
        l, u = ci(dr); add("paired", definition=d, versus="baseline", quantity=q, diff=pt, lo=l, hi=u, share_positive=float((dr > 0).mean()))
        if q in ("ror", "contrast_diff", "ratio_mkt", "wM_eq", "wM_usd"):
            S.add(f"pair_{d}_{q}", pt); S.add(f"pair_{d}_{q}_lo", l); S.add(f"pair_{d}_{q}_hi", u)

# ---------------------------------------------------------------- part C: counterfactuals (signals baseline = 1, two_year = 2)
def cfw(psi_a, Sig_b):
    w = np.linalg.solve(Sig_b, psi_a); return w / (psi_a @ w)
def cf_stats(psi_a, Sig_b, psi_norm=None):
    w = cfw(psi_a, Sig_b)
    st = stats(w, psi_a)
    return dict(w_ten=w[0], w_eq=w[1], w_usd=w[2], ratio_mkt=st["ratio_mkt"], ror=st["ror"], contrast_diff=st["contrast_diff"])
def sdcorr(Sg):
    s = np.sqrt(np.diag(Sg)); return s, Sg / np.outer(s, s)
def build(spec, which):
    """spec: dict of 'psi' and 'sig' choices; returns (psi, Sigma) from baseline (1) and two_year (2) components; which = 'pt' or draw index"""
    get = (lambda d: (POINT[d][1], POINT[d][2])) if which == "pt" else (lambda d: (BP[d][which], BS[d][which]))
    p1, s1 = get("baseline"); p2, s2 = get("two_year")
    psi = (p2 if spec["psi"] == 2 else p1).copy()
    if "psi_only" in spec:                                   # only one element of psi from signal 2
        psi = p1.copy(); psi[spec["psi_only"]] = p2[spec["psi_only"]]
    sd1, C1 = sdcorr(s1); sd2, C2 = sdcorr(s2)
    sg = spec.get("sig", 1)
    if sg == 1: Sg = s1
    elif sg == 2: Sg = s2
    elif sg == "sd2": Sg = np.outer(sd2, sd2) * C1
    elif sg == "corr2": Sg = np.outer(sd1, sd1) * C2
    elif isinstance(sg, tuple) and sg[0] == "sd_only":
        sd = sd1.copy(); sd[sg[1]] = sd2[sg[1]]; Sg = np.outer(sd, sd) * C1
    return psi, Sg
COMBOS = {"psi1_sig1 (baseline)": dict(psi=1, sig=1), "psi2_sig1": dict(psi=2, sig=1), "psi1_sig2": dict(psi=1, sig=2), "psi2_sig2 (two_year)": dict(psi=2, sig=2),
          "psi1_sdOf2_corrOf1": dict(psi=1, sig="sd2"), "psi1_sdOf1_corrOf2": dict(psi=1, sig="corr2"),
          "psi_ten_from2": dict(psi=1, psi_only=0, sig=1), "psi_eq_from2": dict(psi=1, psi_only=1, sig=1), "psi_usd_from2": dict(psi=1, psi_only=2, sig=1),
          "sd_ten_from2": dict(psi=1, sig=("sd_only", 0)), "sd_eq_from2": dict(psi=1, sig=("sd_only", 1)), "sd_usd_from2": dict(psi=1, sig=("sd_only", 2))}
CF = {}; CFB = {}
for k, sp in COMBOS.items():
    CF[k] = cf_stats(*build(sp, "pt")); CFB[k] = [cf_stats(*build(sp, r)) for r in range(R)]
    for q in ("w_ten", "w_eq", "w_usd", "ratio_mkt", "ror", "contrast_diff"):
        l, u = ci([x[q] for x in CFB[k]]); add("counterfactual", combination=k, quantity=q, point=CF[k][q], lo=l, hi=u)
        tag = k.split(" ")[0]; S.add(f"cf_{tag}_{q}", CF[k][q])
# step decomposition: change in each quantity from baseline (1,1) to two_year (2,2) by order
for q in ("w_eq", "w_usd", "w_ten", "ratio_mkt", "ror", "contrast_diff"):
    g = lambda k: CF[k][q]; gb = lambda k: np.array([x[q] for x in CFB[k]])
    A = ["psi1_sig1 (baseline)", "psi2_sig1", "psi2_sig2 (two_year)"]; B = ["psi1_sig1 (baseline)", "psi1_sig2", "psi2_sig2 (two_year)"]
    steps = {"psi_first__psi": (g(A[1]) - g(A[0]), gb(A[1]) - gb(A[0])), "psi_first__sigma": (g(A[2]) - g(A[1]), gb(A[2]) - gb(A[1])),
             "sigma_first__sigma": (g(B[1]) - g(B[0]), gb(B[1]) - gb(B[0])), "sigma_first__psi": (g(B[2]) - g(B[1]), gb(B[2]) - gb(B[1])),
             "total": (g(A[2]) - g(A[0]), gb(A[2]) - gb(A[0]))}
    steps["psi_shapley"] = ((steps["psi_first__psi"][0] + steps["sigma_first__psi"][0]) / 2, (steps["psi_first__psi"][1] + steps["sigma_first__psi"][1]) / 2)
    steps["sigma_shapley"] = ((steps["psi_first__sigma"][0] + steps["sigma_first__sigma"][0]) / 2, (steps["psi_first__sigma"][1] + steps["sigma_first__sigma"][1]) / 2)
    steps["order_gap_psi"] = (steps["psi_first__psi"][0] - steps["sigma_first__psi"][0], steps["psi_first__psi"][1] - steps["sigma_first__psi"][1])
    for k, (pt, dr) in steps.items():
        l, u = ci(dr); add("counterfactual_steps", quantity=q, step=k, point=pt, lo=l, hi=u)
        if q in ("w_eq", "w_usd", "ror"): S.add(f"cfstep_{q}_{k}", pt)

# ---------------------------------------------------------------- part D: what variation each signal captures
def r2(y, X):
    Xc = np.c_[np.ones(len(y)), X]; bb, *_ = np.linalg.lstsq(Xc, y, rcond=None); res = y - Xc @ bb
    return 1 - (res @ res) / (((y - y.mean()) ** 2).sum()), res, bb
import statsmodels.api as sm
f_ns = signal(np.arange(n), "ns"); f_2y = u2
S.add("sig_corr_ns_2y", float(np.corrcoef(f_ns, f_2y)[0, 1])); S.add("sig_sd_ns", float(f_ns.std(ddof=1))); S.add("sig_sd_2y", float(f_2y.std(ddof=1)))
S.add("sig_slope_2y_on_ns", float(np.polyfit(f_ns, f_2y, 1)[0])); S.add("sig_r2_2y_on_ns", float(np.corrcoef(f_ns, f_2y)[0, 1] ** 2))
res2 = f_2y - np.polyval(np.polyfit(f_ns, f_2y, 1), f_ns)
for k, a in enumerate(NM):
    y = Y3[:, k]
    for nm_, X_ in (("ns", f_ns), ("two_year", f_2y), ("both", np.c_[f_ns, f_2y])):
        r2v, res, bb = r2(y, X_)
        add("signal_content", asset=a, regressors=nm_, r2=r2v, resid_sd=res.std(ddof=X_.reshape(n, -1).shape[1] + 1), n=n)
        S.add(f"content_{a}_{nm_}_r2", r2v); S.add(f"content_{a}_{nm_}_resid_sd", res.std(ddof=X_.reshape(n, -1).shape[1] + 1))
    fit2 = sm.OLS(y, sm.add_constant(np.c_[f_ns, f_2y])).fit(cov_type="HC1")
    add("signal_content_both", asset=a, coef_ns=fit2.params[1], t_ns=fit2.tvalues[1], coef_2y=fit2.params[2], t_2y=fit2.tvalues[2])
    S.add(f"both_{a}_t_ns", fit2.tvalues[1]); S.add(f"both_{a}_t_2y", fit2.tvalues[2]); S.add(f"both_{a}_coef_ns", fit2.params[1]); S.add(f"both_{a}_coef_2y", fit2.params[2])
    S.add(f"corr_res2y_{a}_resid_ns", float(np.corrcoef(res2, y - np.polyval(np.polyfit(f_ns, y, 1), f_ns))[0, 1]))
S.add("sd_2y_residual_on_ns", float(res2.std(ddof=2))); S.add("sd_2y_residual_share", float(res2.std(ddof=2) / f_2y.std(ddof=1)))
# the same under the subsample definitions (signal vs two-year yield)
for d in ("to_2019", "no_lower_bound"):
    rows = np.where(MASK[d])[0]; f = signal(rows, "ns"); S.add(f"sig_corr_ns_2y_{d}", float(np.corrcoef(f, u2[rows])[0, 1]))

# ---------------------------------------------------------------- part E: carried through
Dm = data.load()
Xr = cases.inputs(Dm, "rstar")[MV]
Z12 = Xr.diff(12).loc["1996-01":END].dropna().values; TT = len(Z12)
bb_ = lambda psi: b / (b @ psi)
WBN = {d: bb_(POINT[d][1]) for d in DEFS}
rngm = np.random.default_rng(SEED + 21)
IM = np.array([mbb(TT, 24, rngm) for _ in range(R)])
def dsum(Z, wB, w):
    D = Z @ (wB - w); m = Z @ w; return dict(mean_abs_pts=np.abs(D).mean(), ratio=np.abs(D).mean() / np.abs(m).mean(), mean_abs_market=np.abs(m).mean(), share_gt_025=(np.abs(D) > 0.25).mean())
E12 = {d: dsum(Z12, WBN[d], POINT[d][0]) for d in DEFS}
E12B = {d: [dsum(Z12[IM[r]], bb_(BP[d][r]), BW[d][r]) for r in range(R)] for d in DEFS}
for d in DEFS:
    for k, v in E12[d].items():
        l, u = ci([x[k] for x in E12B[d]]); add("disagreement", definition=d, sample="12m_changes_1996_2026", stat=k, point=v, lo=l, hi=u, diff_vs_baseline=np.nan, diff_lo=np.nan, diff_hi=np.nan)
        S.add(f"d12_{d}_{k}", v)
        if d != "baseline":
            dr = np.array([x[k] for x in E12B[d]]) - np.array([x[k] for x in E12B["baseline"]]); dl, du = ci(dr)
            TAB["disagreement"][-1].update(diff_vs_baseline=v - E12["baseline"][k], diff_lo=dl, diff_hi=du)
            if k == "ratio": S.add(f"d12_{d}_ratio_diff", v - E12["baseline"][k]); S.add(f"d12_{d}_ratio_diff_lo", dl); S.add(f"d12_{d}_ratio_diff_hi", du)
    S.add(f"d12_{d}_mean_abs_bp", 100 * E12[d]["mean_abs_pts"])
# held-out announcement windows within each definition
def loo_point(d):
    rows = np.where(MASK[d])[0]; Dv, mv = [], []
    for i in rows:
        rr = rows[rows != i]; w_, p_, _ = est(rr, KIND[d]); Dv.append((b / (b @ p_) - w_) @ Y3[i]); mv.append(w_ @ Y3[i])
    return np.array(Dv), np.array(mv)
LOO = {}
for d in DEFS:
    Dv, mv = loo_point(d); LOO[d] = (Dv, mv)
def loo_boot(d):
    out = []
    for r in range(R):
        ix = IX[r]; cnt = np.bincount(ix, minlength=n); inm = MASK[d][ix]; Dd, md, wt = [], [], []
        for i in np.where((cnt > 0) & MASK[d])[0]:
            rows = ix[(ix != i) & inm]
            w_, p_, _ = est(rows, KIND[d]); Dd.append((b / (b @ p_) - w_) @ Y3[i]); md.append(w_ @ Y3[i]); wt.append(cnt[i])
        Dd, md, wt = np.array(Dd), np.array(md), np.array(wt, float)
        out.append(dict(mean_abs_pts=(wt * np.abs(Dd)).sum() / wt.sum(), ratio=(wt * np.abs(Dd)).sum() / (wt * np.abs(md)).sum(), mean_abs_market=(wt * np.abs(md)).sum() / wt.sum()))
    return out
LB = {d: loo_boot(d) for d in DEFS}
for d in DEFS:
    Dv, mv = LOO[d]; pt = dict(mean_abs_pts=np.abs(Dv).mean(), ratio=np.abs(Dv).mean() / np.abs(mv).mean(), mean_abs_market=np.abs(mv).mean())
    for k, v in pt.items():
        l, u = ci([x[k] for x in LB[d]]); add("disagreement", definition=d, sample="held_out_announcements", stat=k, point=v, lo=l, hi=u, diff_vs_baseline=np.nan, diff_lo=np.nan, diff_hi=np.nan)
        S.add(f"dev_{d}_{k}", v)
        if d != "baseline":
            dr = np.array([x[k] for x in LB[d]]) - np.array([x[k] for x in LB["baseline"]]); dl, du = ci(dr)
            b0_ = dict(mean_abs_pts=np.abs(LOO["baseline"][0]).mean(), ratio=np.abs(LOO["baseline"][0]).mean() / np.abs(LOO["baseline"][1]).mean(), mean_abs_market=np.abs(LOO["baseline"][1]).mean())[k]
            TAB["disagreement"][-1].update(diff_vs_baseline=v - b0_, diff_lo=dl, diff_hi=du)
            if k == "ratio": S.add(f"dev_{d}_ratio_diff_lo", dl); S.add(f"dev_{d}_ratio_diff_hi", du)
# the held-out ratio on the common set of announcements (the subsample definitions are evaluated on their own announcements; the baseline on the same subset for a like-for-like comparison)
for d in ("to_2019", "no_lower_bound"):
    rows = np.where(MASK[d])[0]; Dv, mv = LOO["baseline"]; sub = np.isin(np.arange(n), rows)
    S.add(f"dev_baseline_on_{d}_ratio", float(np.abs(Dv[sub]).mean() / np.abs(mv[sub]).mean()))

# matched episodes (12-month changes of the r* step inputs, months a..b; same construction as 19_composition.py and report block 'what the assets did')
XL = cases.demean(Xr).loc[START:END]
dX = XL.diff(12)
EPIS = {"1998-2001": ("1998-01", "2001-12"), "2004-06": ("2004-06", "2006-06"), "2022-24": ("2022-03", "2024-12")}
def epmean(A, a, e): return np.nanmean(A[(A.index >= pd.Period(a, "M")) & (A.index <= pd.Period(e, "M"))].values, axis=0)
def epr(wMv, wBv, ep):
    a, e = EPIS[ep]; mx = epmean(dX, a, e); lv = epmean(XL, a, e); dw = wBv - wMv
    out = dict(market=mx @ wMv, frbus=mx @ wBv, D=mx @ dw, level_market=lv @ wMv, level_D=lv @ dw)
    for k, a_ in enumerate(NM): out[f"contrib_{a_}"] = dw[k] * mx[k]
    return out
EPT = {(d, ep): epr(POINT[d][0], WBN[d], ep) for d in DEFS for ep in EPIS}
EPB = {(d, ep): [epr(BW[d][r], bb_(BP[d][r]), ep) for r in range(R)] for d in DEFS for ep in EPIS}
for ep, (a, e) in EPIS.items():
    mx = epmean(dX, a, e)
    for k, a_ in enumerate(NM): S.add(f"ep_{ep}_mean_change_{a_}", mx[k])
for (d, ep), pt in EPT.items():
    for k, v in pt.items():
        l, u = ci([x[k] for x in EPB[(d, ep)]]); row = dict(definition=d, episode=ep, quantity=k, point=v, lo=l, hi=u, diff_vs_baseline=np.nan, diff_lo=np.nan, diff_hi=np.nan)
        if d != "baseline":
            dr = np.array([x[k] for x in EPB[(d, ep)]]) - np.array([x[k] for x in EPB[("baseline", ep)]]); dl, du = ci(dr)
            row.update(diff_vs_baseline=v - EPT[("baseline", ep)][k], diff_lo=dl, diff_hi=du)
            if k in ("market", "frbus", "D"): S.add(f"epdiff_{d}_{ep}_{k}", v - EPT[("baseline", ep)][k]); S.add(f"epdiff_{d}_{ep}_{k}_lo", dl); S.add(f"epdiff_{d}_{ep}_{k}_hi", du)
        add("episodes", **row); S.add(f"ep_{d}_{ep}_{k}", v); S.add(f"ep_{d}_{ep}_{k}_lo", l); S.add(f"ep_{d}_{ep}_{k}_hi", u)
# does the historical conclusion survive each definition? (criteria fixed here, before reading the numbers)
for d in DEFS:
    e98, e22 = EPT[(d, "1998-2001")], EPT[(d, "2022-24")]
    crit = {"1998_opposite_signs": float(np.sign(e98["market"]) != np.sign(e98["frbus"])), "1998_both_small_lt_0p5": float(max(abs(e98["market"]), abs(e98["frbus"])) < 0.5),
            "1998_D_positive": float(e98["D"] > 0), "1998_dollar_contrib_gt_equity": float(abs(e98["contrib_usd"]) > abs(e98["contrib_eq"])),
            "2022_agree_within_0p05": float(abs(e22["D"]) < 0.05), "2022_both_tighten_gt_0p5": float(min(e22["market"], e22["frbus"]) > 0.5),
            "2022_equity_dollar_contribs_offset": float(np.sign(e22["contrib_eq"]) != np.sign(e22["contrib_usd"]))}
    for k, v in crit.items(): add("survival", definition=d, criterion=k, value=v); S.add(f"surv_{d}_{k}", v)
    S.add(f"surv_{d}_n_criteria_met", sum(crit.values()))

# ---------------------------------------------------------------- part F: FCI-G multipliers as a second spending calibration
M = pd.read_csv(DATA / "multipliers.csv").values
row0 = M[0]                                                      # effect on growth over the next four quarters of a unit shift now (the Board's published multipliers)
m10 = row0[1] + row0[2] + row0[3]                                # 10-year yield with the mortgage and BBB yields moving with it (spreads fixed): 10-year + mortgage + BBB multipliers
m_eq, m_usd = abs(row0[4]), abs(row0[6])                          # per 1 percent of stock prices (rise lowers the drag) and of the dollar (rise raises it); signs as in lib.indexes.fcig_weights
bF = np.array([abs(m10), -m_eq, m_usd])                           # signed like b: an equity fall tightens, so the equity weight is negative
G4 = abs(G[4])                                                    # FRB/US funds-rate yardstick (full transmission), percent of GDP
bF_f = bF / G4                                                    # FCI-G multipliers on the FRB/US funds-rate yardstick [inference: the FCI-G policy multiplier is a direct effect; its yardstick differs]
S.add("fcig_m10_spreads_fixed", m10); S.add("fcig_m_eq", m_eq); S.add("fcig_m_usd", m_usd); S.add("fcig_policy_direct", row0[0])
S.add("fcig_ratio_usd_eq", m_usd / m_eq); S.add("frbus_ratio_usd_eq", b[2] / abs(b[1]))
for d in DEFS:
    rm = POINT[d][0][2] * USD / (POINT[d][0][1] * EQ); rf = (m_usd * USD) / (m_eq * abs(EQ)); rr = rf / rm
    rrb = np.array([(m_usd * USD) / (m_eq * abs(EQ)) / ((BW[d][r][2] * USD) / (BW[d][r][1] * EQ)) for r in range(R)])
    rrb_frb = np.array([x for x in col(d, "ror")])
    l, u = ci(rrb)
    bpF = bF_f @ POINT[d][1]; bpFb = np.array([bF_f @ BP[d][r] for r in range(R)])
    add("fcig", definition=d, quantity="ror_fcig", point=rr, lo=l, hi=u); add("fcig", definition=d, quantity="ror_frbus", point=ST[d]["ror"], lo=ci(rrb_frb)[0], hi=ci(rrb_frb)[1])
    add("fcig", definition=d, quantity="bpsi_fcig_on_frbus_yardstick", point=bpF, lo=ci(bpFb)[0], hi=ci(bpFb)[1])
    S.add(f"fcig_{d}_ror", rr); S.add(f"fcig_{d}_ror_lo", l); S.add(f"fcig_{d}_ror_hi", u); S.add(f"fcig_{d}_bpsi", bpF)
add("fcig", definition="all", quantity="m_usd_over_m_eq_fcig", point=m_usd / m_eq, lo=np.nan, hi=np.nan); add("fcig", definition="all", quantity="m_usd_over_m_eq_frbus", point=b[2] / abs(b[1]), lo=np.nan, hi=np.nan)
for k, a_ in enumerate(NM):
    add("fcig_weights", asset=a_, fcig_gdp_pp=bF[k], frbus_gdp_pp=b[k] * G4, fcig_funds_equiv=bF_f[k], frbus_funds_equiv=b[k])

# ---------------------------------------------------------------- write
for k, rows in TAB.items():
    pd.DataFrame(rows).to_csv(RES / f"21_{k}.csv", index=False, float_format="%.6g")
S.save()
print({k: len(v) for k, v in TAB.items()}, f"runtime {time.time() - T0:.0f}s")
