"""Step 18. Do the market weights and the FRB/US weights agree, and does the disagreement survive a fair comparison? (follow-up 4, items 1 and 2.)

DESIGN (pre-specified; descriptive, no hypothesis tests, so no multiple-testing adjustment; intervals are 5th-95th percentiles of bootstrap draws)
 inputs   : psi (responses of 10-year yield pp, 100 ln CAPE, real dollar 100 ln to one unit of NS policy news = 1 pp on the 2-year yield), market GLS weights w_M (w_M'psi = 1),
            and 500 announcement-bootstrap draws of both (results/weights_boot.csv, first REPS draws). FRB/US weights b_h = Phi(h)/G(h): GDP response at quarter h to a persistent
            unit shift in each variable (data/frbus_paths.csv, design zfree, experiment rg10, req, fpxr) over the GDP response to a persistent 1 pp funds-rate hike, h = 2, 4 (main), 8.
            b_h is treated as fixed. w_B,h = b_h / (b_h'psi), so w_B,h'psi = 1 and D_h(x) = (w_B,h - w_M)'x vanishes for any conventional surprise.
 linearity: any asset path x_s (s = 1..h) is priced from the TEMPORARY-shock responses: GDP(h) = sum_s x_s Tmp(h-s+1). Persistent (x_s = 1) must equal the cumulated temporary
            responses; results/18_persist_check.csv gives the difference (<= 0.0004 at h <= 8 quarters; it grows to 0.02 by quarter 32).
 item 1   : b_h'psi (with interval), w_B,h; item 2 (worked example): equity valuation -5 log points, dollar +3.9 log points, typical joint response to a one-unit surprise.
 item 3   : matched persistence. Paths: persistent (now used), common half-lives 8, 4, 2 quarters (pre-specified grid), the post-1996 AR(1) half-lives of the levels of each variable
            ('est_ar1'), and the daily-equity post-announcement half-life ('est_daily_eq'). Persistence estimates in results/18_persistence_*.csv (see CHECK note for what they identify).
 item 4   : D_h on (i) announcement windows, held out (leave-one-event-out: NS factor, psi and w_M re-estimated without the event; in bootstrap draws without all copies of it),
            and (ii) monthly and 12-month changes of the three variables (nominal and r* steps; 1996-2026 and 1973-2026): size, size relative to the market-index movement,
            frequency above 0.25 and 0.5 policy-rate points, run lengths. Joint bootstrap: draws of (w_M, psi) paired with a moving-block resample of the months (blocks 12 / 24).
 item 5   : bridge F - M (FRB/US index with house prices minus market index, levels and 12-month changes, nominal / real / r* steps) in stages: weights on the three common assets,
            normalisation (b vs w_B), policy rate, spreads, housing, then the real and r* transformations; variance shares Cov(stage, F - M)/Var(F - M) with the joint bootstrap
            (block 24 months), episode contributions with intervals over the weight draws.
Writes results/18_<table>.csv and scalars_18_agreement.csv."""
import numpy as np, pandas as pd
import statsmodels.api as sm
from lib import data, cases, indexes as I
from lib.agree_core import *
from lib.agree_bridge import *
from lib.config import RES, REPS, SEED, START, END, BLOCK
from lib.report import Scalars

S = Scalars("18_agreement")
TAB = {}
def add(tab, **kw): TAB.setdefault(tab, []).append(kw)
def ci3(d, a=5, b=95):
    d = np.nan_to_num(np.asarray(d, float), posinf=1e9)          # infinite half-lives sort last
    f = lambda q: (lambda v: np.inf if v >= 1e8 else float(v))(np.nanpercentile(d, q))
    return (f(a), f(b))
HS = (2, 4, 8)

mw = pd.read_csv(RES / "market_weights.csv", index_col=0)
wM, psi = mw.weight.values, mw.response.values
Bd = pd.read_csv(RES / "weights_boot.csv").iloc[:REPS]
WB, PB = Bd[["w_ten", "w_eq", "w_usd"]].values, Bd[["psi_ten", "psi_eq", "psi_usd"]].values
R = len(Bd)
R_, G = load_frbus()
b = {h: b_persist(R_, G, h) for h in HS}
wBh = {h: b[h] / (b[h] @ psi) for h in HS}
# the package's own weights (lib.indexes) must agree
P_, G_ = I.frbus_paths()
assert np.allclose(I.phi_at(P_, 4)[MV].values / G_[4], b[4])

# ---------------------------------------------------------------- linearity check: persistent = cumulated temporary
for h in HS + (16, 32):
    for v in MV:
        pp = R_[(v, "persistent")][h]; ct = R_[(v, "temporary")][1:h + 1].sum()
        add("persist_check", h=h, variable=v, persistent=pp, cumulated_temporary=ct, difference=pp - ct, relative=(pp - ct) / abs(pp) if pp else np.nan)
    if h in HS:
        S.add(f"linearity_maxabs_h{h}", max(abs(R_[(v, 'persistent')][h] - R_[(v, 'temporary')][1:h + 1].sum()) for v in MV))
        S.add(f"linearity_b_maxabs_h{h}", float(np.abs(b_path(R_, G, h, (np.inf,) * 3) - b[h]).max()))

# ---------------------------------------------------------------- item 1: b_h'psi and w_B,h
names = {"y10": "ten", "equities": "eq", "dollar": "usd"}
for h in HS:
    bp = PB @ b[h]
    add("weights", h=h, quantity="bpsi", point=b[h] @ psi, lo=ci3(bp)[0], hi=ci3(bp)[1])
    S.add(f"bpsi_h{h}", b[h] @ psi); S.add(f"bpsi_h{h}_lo", ci3(bp)[0]); S.add(f"bpsi_h{h}_hi", ci3(bp)[1]); S.add(f"bpsi_h{h}_se", bp.std(ddof=1))
    S.add(f"bpsi_h{h}_share_neg1", float((bp < 1).mean()))                       # draws with b'psi below 1 (FRB/US typical response smaller than market's)
    for k, v in enumerate(MV):
        n = names[v]
        add("weights", h=h, quantity=f"b_{n}", point=b[h][k], lo=np.nan, hi=np.nan)
        wbk = b[h][k] / bp; l, u = ci3(wbk)
        add("weights", h=h, quantity=f"wB_{n}", point=wBh[h][k], lo=l, hi=u)
        add("weights", h=h, quantity=f"wM_{n}", point=wM[k], lo=ci3(WB[:, k])[0], hi=ci3(WB[:, k])[1])
        add("weights", h=h, quantity=f"contrib_b_psi_{n}", point=b[h][k] * psi[k], lo=ci3(b[h][k] * PB[:, k])[0], hi=ci3(b[h][k] * PB[:, k])[1])
        add("weights", h=h, quantity=f"contrib_wM_psi_{n}", point=wM[k] * psi[k], lo=ci3(WB[:, k] * PB[:, k])[0], hi=ci3(WB[:, k] * PB[:, k])[1])
        S.add(f"wB_{n}_h{h}", wBh[h][k]); S.add(f"wB_{n}_h{h}_lo", l); S.add(f"wB_{n}_h{h}_hi", u); S.add(f"b_{n}_h{h}", b[h][k])
for k, v in enumerate(MV):
    S.add(f"wM_{names[v]}", wM[k]); S.add(f"wM_{names[v]}_lo", ci3(WB[:, k])[0]); S.add(f"wM_{names[v]}_hi", ci3(WB[:, k])[1]); S.add(f"psi_{names[v]}_boot_lo", ci3(PB[:, k])[0]); S.add(f"psi_{names[v]}_boot_hi", ci3(PB[:, k])[1])
S.add("max_abs_D_psi", max(abs((wBh[h] - wM) @ psi) for h in HS))                 # D_h(psi s) = 0 by construction

# ---------------------------------------------------------------- item 2: worked example
EQ, USD = -5.0, 3.9
for h in HS:
    bp = PB @ b[h]
    rows = {"market": (wM, WB), "frbus_b": (b[h], None), "frbus_wB": (wBh[h], b[h][None, :] / bp[:, None])}
    for tag, (wv, draws) in rows.items():
        eq, us = wv[1] * EQ, wv[2] * USD
        jt = {"market": wM @ psi, "frbus_b": b[h] @ psi, "frbus_wB": 1.0}[tag]
        jt_d = {"market": (WB * PB).sum(1), "frbus_b": bp, "frbus_wB": np.ones(R)}[tag]
        if draws is None:
            eq_d = np.full(R, eq); us_d = np.full(R, us)
        else:
            eq_d, us_d = draws[:, 1] * EQ, draws[:, 2] * USD
        for q, pt, d in (("eq_effect", eq, eq_d), ("usd_effect", us, us_d), ("ratio_usd_eq", us / eq, us_d / eq_d), ("joint_response", jt, jt_d)):
            l, u = ci3(d) if not np.allclose(d, d[0]) else (np.nan, np.nan)
            add("example", h=h, index=tag, quantity=q, point=pt, lo=l, hi=u)
            S.add(f"ex_{tag}_{q}_h{h}", pt)
        if tag == "market":
            mk_ratio_d = us_d / eq_d
    fr = b[h][2] * USD / (b[h][1] * EQ)
    rr = fr / (wM[2] * USD / (wM[1] * EQ)); rr_d = fr / mk_ratio_d
    l, u = ci3(rr_d)
    add("example", h=h, index="frbus_over_market", quantity="ratio_of_ratios", point=rr, lo=l, hi=u)
    S.add(f"ex_ratio_of_ratios_h{h}", rr); S.add(f"ex_ratio_of_ratios_h{h}_lo", l); S.add(f"ex_ratio_of_ratios_h{h}_hi", u)
    S.add(f"ex_market_ratio_h{h}_lo", ci3(WB[:, 2] * USD / (WB[:, 1] * EQ))[0]); S.add(f"ex_market_ratio_h{h}_hi", ci3(WB[:, 2] * USD / (WB[:, 1] * EQ))[1])

# ---------------------------------------------------------------- persistence estimates (inputs of item 3)
Dm = data.load()
Xn = cases.inputs(Dm, "nominal")[MV]
rng = np.random.default_rng(SEED + 18)
hl_q = lambda r: np.log(0.5) / np.log(r) / 3 if 0 < r < 1 else np.inf
HL_AR = {}
for per, a in (("1996-2026", "1996-01"), ("1973-2026", "1973-01")):
    for v in MV:
        s = Xn[v].loc[a:END].dropna().values; y, yl = s[1:], s[:-1]
        slope = lambda yy, ll: np.cov(yy, ll)[0, 1] / np.var(ll, ddof=1)
        rho = slope(y, yl); T = len(y); hs = []
        for _ in range(R):
            i = mbb(T, BLOCK, rng); hs.append(hl_q(slope(y[i], yl[i])))
        l, u = ci3(hs); HL_AR[(per, v)] = hl_q(rho)
        add("persistence_ar1", period=per, variable=v, rho_monthly=rho, halflife_quarters=hl_q(rho), lo=l, hi=u, n=T)
        S.add(f"hl_ar1_{names[v]}_{per[:4]}", hl_q(rho))
# daily equity: response of 100 ln CAPE (previous close to k trading days after the announcement day) to NS news; one quarter = 63 trading days
ev = I.events(); dd = pd.read_csv(data.DATA / "gs_daily.csv", parse_dates=["date"]).set_index("date")
c = 100 * np.log(dd.cape); KS = [0, 1, 2, 5, 10, 20, 40, 60, 120]
Yk = np.full((len(ev), len(KS)), np.nan)
for r_, dt in enumerate(ev.Date):
    i = c.index.searchsorted(dt)
    if 0 < i < len(c) and c.index[i] == dt:
        for j, k in enumerate(KS):
            if i + k < len(c): Yk[r_, j] = c.iloc[i + k] - c.iloc[i - 1]
nsv = ev.ns.values
def slopes(ix):
    f, Y = nsv[ix], Yk[ix]; ok = ~np.isnan(Y); out = np.empty(len(KS))
    for j in range(len(KS)):
        m = ok[:, j]; ff = f[m] - f[m].mean(); out[j] = ff @ (Y[m, j] - Y[m, j].mean()) / (ff @ ff)
    return out
b0 = slopes(np.arange(len(ev)))
# HC1 standard errors from statsmodels for the table
se0 = []
for j in range(len(KS)):
    m = ~np.isnan(Yk[:, j]); se0.append(sm.OLS(Yk[m, j], sm.add_constant(nsv[m])).fit(cov_type="HC1").bse[1])
se0 = np.array(se0)
HLGRID = np.r_[np.geomspace(0.25, 64, 45), np.inf]
def fit_hl(beta, se):
    w = 1 / se ** 2; best = (np.inf, None)
    for hl in HLGRID:
        g = np.ones(len(KS)) if np.isinf(hl) else 0.5 ** (np.array(KS) / (63 * hl)); A = (w * beta * g).sum() / (w * g * g).sum()
        sse = (w * (beta - A * g) ** 2).sum()
        if sse < best[0]: best = (sse, hl)
    return np.inf if best[1] >= 64 else best[1]
hl_eq_daily = fit_hl(b0, se0)
bb = np.array([slopes(rng.integers(0, len(ev), len(ev))) for _ in range(R)])
hl_b = [fit_hl(x, se0) for x in bb]
for j, k in enumerate(KS):
    add("persistence_daily_equity", trading_days=k, response=b0[j], se=se0[j], ratio_to_day0=b0[j] / b0[0], lo_ratio=ci3(bb[:, j] / bb[:, 0])[0], hi_ratio=ci3(bb[:, j] / bb[:, 0])[1])
add("persistence_daily_equity", trading_days=-1, response=np.nan, se=np.nan, ratio_to_day0=hl_eq_daily, lo_ratio=ci3(hl_b)[0], hi_ratio=ci3(hl_b)[1])     # row -1: fitted half-life in quarters
S.add("hl_daily_eq", hl_eq_daily); S.add("hl_daily_eq_lo", ci3(hl_b)[0]); S.add("hl_daily_eq_hi", ci3(hl_b)[1])
S.add("daily_eq_ratio_60d", b0[KS.index(60)] / b0[0]); S.add("daily_eq_ratio_120d", b0[KS.index(120)] / b0[0]); S.add("daily_eq_resp_day0", b0[0]); S.add("daily_eq_resp_20d", b0[KS.index(20)])
# monthly local projections on the month's NS news (all three variables; noisy because other news moves the month)
evm = ev.assign(m=ev.Date.dt.to_period("M")).groupby("m").ns.sum().reindex(Xn.index).fillna(0.0)
for v in MV:
    for k in (0, 3, 6, 12, 24):
        y = (Xn[v].shift(-k) - Xn[v].shift(1)).loc["1996-01":"2026-01"]
        j_ = pd.concat([y, evm], axis=1).dropna(); j_.columns = ["y", "n"]
        r = sm.OLS(j_.y, sm.add_constant(j_.n)).fit(cov_type="HAC", cov_kwds={"maxlags": k + 3})
        add("persistence_monthly_lp", variable=v, months=k, response=r.params["n"], se=r.bse["n"], n=len(j_))

# ---------------------------------------------------------------- item 3: matched paths
HLP = {"persistent": (np.inf,) * 3, "hl8": (8.0,) * 3, "hl4": (4.0,) * 3, "hl2": (2.0,) * 3,
       "est_ar1": tuple(HL_AR[("1996-2026", v)] for v in MV)}
if np.isfinite(hl_eq_daily):
    HLP["est_daily_eq"] = (HL_AR[("1996-2026", "y10")], hl_eq_daily, HL_AR[("1996-2026", "dollar")])
for h in HS:
    mk_ratio_pt = wM[2] * USD / (wM[1] * EQ); mk_ratio_d = WB[:, 2] * USD / (WB[:, 1] * EQ)
    for lab, hl in HLP.items():
        bv = b_path(R_, G, h, hl); bp = PB @ bv; wb = bv / (bv @ psi)
        for k, v in enumerate(MV):
            add("matched_paths", h=h, path=lab, hl_y10=hl[0], hl_eq=hl[1], hl_usd=hl[2], quantity=f"b_{names[v]}", point=bv[k], lo=np.nan, hi=np.nan)
        l, u = ci3(bp); add("matched_paths", h=h, path=lab, hl_y10=hl[0], hl_eq=hl[1], hl_usd=hl[2], quantity="bpsi", point=bv @ psi, lo=l, hi=u)
        for k, v in enumerate(MV):
            l, u = ci3(bv[k] / bp); add("matched_paths", h=h, path=lab, hl_y10=hl[0], hl_eq=hl[1], hl_usd=hl[2], quantity=f"wB_{names[v]}", point=wb[k], lo=l, hi=u)
        fr = bv[2] * USD / (bv[1] * EQ); rr = fr / mk_ratio_pt; l, u = ci3(fr / mk_ratio_d)
        add("matched_paths", h=h, path=lab, hl_y10=hl[0], hl_eq=hl[1], hl_usd=hl[2], quantity="eq_effect_wB", point=wb[1] * EQ, lo=ci3(bv[1] * EQ / bp)[0], hi=ci3(bv[1] * EQ / bp)[1])
        add("matched_paths", h=h, path=lab, hl_y10=hl[0], hl_eq=hl[1], hl_usd=hl[2], quantity="usd_effect_wB", point=wb[2] * USD, lo=ci3(bv[2] * USD / bp)[0], hi=ci3(bv[2] * USD / bp)[1])
        add("matched_paths", h=h, path=lab, hl_y10=hl[0], hl_eq=hl[1], hl_usd=hl[2], quantity="ratio_usd_eq", point=fr, lo=np.nan, hi=np.nan)
        add("matched_paths", h=h, path=lab, hl_y10=hl[0], hl_eq=hl[1], hl_usd=hl[2], quantity="ratio_of_ratios", point=rr, lo=l, hi=u)
        S.add(f"mp_ratio_{lab}_h{h}", fr); S.add(f"mp_ror_{lab}_h{h}", rr); S.add(f"mp_ror_{lab}_h{h}_lo", l); S.add(f"mp_ror_{lab}_h{h}_hi", u); S.add(f"mp_bpsi_{lab}_h{h}", bv @ psi)
    for he in (np.inf, 8.0, 4.0, 2.0):                      # equity and dollar with different persistence
        for hu in (np.inf, 8.0, 4.0, 2.0):
            bv = b_path(R_, G, h, (np.inf, he, hu)); fr = bv[2] * USD / (bv[1] * EQ)
            add("matched_grid", h=h, hl_eq=he, hl_usd=hu, ratio_usd_eq=fr, ratio_of_ratios=fr / mk_ratio_pt, lo=ci3(fr / mk_ratio_d)[0], hi=ci3(fr / mk_ratio_d)[1])

# ---------------------------------------------------------------- item 4(i): D_h on announcement windows, held out
raw = I.events_raw(); n = len(raw)
X5 = raw[["MP1", "MP2", "ED2", "ED3", "ED4"]].values; u2 = raw.UST2Y.values; Y3 = raw[["UST10Y", "SP500", "DXY"]].values
w_chk, psi_chk = fit(X5, u2, Y3)
S.add("fastfit_maxdiff_w", float(np.abs(w_chk - wM).max())); S.add("fastfit_maxdiff_psi", float(np.abs(psi_chk - psi).max()))
assert np.allclose(w_chk, wM, atol=1e-8) and np.allclose(psi_chk, psi, atol=1e-8)
def evstats(D, m):
    o = dstats(D, m); return {k: v for k, v in o.items() if not k.startswith(("mean_run", "max_run", "n_runs"))}
def loo_all():
    Dh = {h: np.empty(n) for h in HS}; mm = np.empty(n)
    for i in range(n):
        k = np.arange(n) != i; w_, p_ = fit(X5[k], u2[k], Y3[k]); mm[i] = w_ @ Y3[i]
        for h in HS: Dh[h][i] = (b[h] / (b[h] @ p_) - w_) @ Y3[i]
    return Dh, mm
Dl, ml = loo_all()
Dins = {h: Y3 @ (wBh[h] - wM) for h in HS}; mins = Y3 @ wM
bs = {h: [] for h in HS}
for _ in range(R):
    ix = rng.integers(0, n, n); cnt = np.bincount(ix, minlength=n); Dd = {h: np.zeros(n) for h in HS}; md = np.zeros(n)
    for i in np.where(cnt > 0)[0]:
        rows = ix[ix != i]; w_, p_ = fit(X5[rows], u2[rows], Y3[rows]); md[i] = w_ @ Y3[i]
        for h in HS: Dd[h][i] = (b[h] / (b[h] @ p_) - w_) @ Y3[i]
    for h in HS: bs[h].append(evstats(Dd[h][ix], md[ix]))
for h in HS:
    for spec, Dv, mv in (("loo", Dl[h], ml), ("insample", Dins[h], mins)):
        pt = evstats(Dv, mv)
        for k, v in pt.items():
            if spec == "loo":
                l, u = ci3([d[k] for d in bs[h]])
            else:
                l = u = np.nan
            add("D_events", h=h, spec=spec, stat=k, point=v, lo=l, hi=u, n=n)
            if spec == "loo" and h == 4: S.add(f"Devent_{k}_h4", v); S.add(f"Devent_{k}_h4_lo", l); S.add(f"Devent_{k}_h4_hi", u)
    S.add(f"Devent_sd_market_move", float(ml.std())); S.add("Devent_ns_sd", float(ev.ns.std()))
S.add("n_events_D", n)

# ---------------------------------------------------------------- item 4(ii): D_h on monthly and 12-month changes
for case in ("nominal", "rstar"):
    Xc = cases.inputs(Dm, case)[MV]
    for chg, L in (("1m", BLOCK), ("12m", 2 * BLOCK)):
        Z = Xc.diff(1 if chg == "1m" else 12)
        for per, a in (("1996-2026", "1996-01"), ("1973-2026", "1973-01")):
            Zp = Z.loc[a:END].dropna().values; T = len(Zp)
            if T < 100: continue
            for h in HS:
                pt = dstats(Zp @ (wBh[h] - wM), Zp @ wM)
                bsd = []
                for r_ in range(R):
                    i = mbb(T, L, rng); wb_ = b[h] / (b[h] @ PB[r_]); bsd.append(dstats(Zp[i] @ (wb_ - WB[r_]), Zp[i] @ WB[r_]))
                for k, v in pt.items():
                    l, u = ci3([d[k] for d in bsd]); add("D_monthly", h=h, case=case, change=chg, period=per, stat=k, point=v, lo=l, hi=u, n=T)
                    if case == "rstar" and per == "1996-2026" and h == 4 or (case == "nominal" and h == 4):
                        S.add(f"Dm_{case}_{chg}_{per[:4]}_{k}_h4", v); S.add(f"Dm_{case}_{chg}_{per[:4]}_{k}_h4_lo", l); S.add(f"Dm_{case}_{chg}_{per[:4]}_{k}_h4_hi", u)

# ---------------------------------------------------------------- item 5: bridge from the market index to the FRB/US index
bF = frbus_b(4); CASES = ["nominal", "real", "rstar"]
XD = {c_: cases.demean(cases.inputs(Dm, "rstar" if c_ == "rstar" else c_))[COLS].loc[START:END] for c_ in CASES}
idx = XD["nominal"].dropna().index
for c_ in CASES: idx = idx.intersection(XD[c_].dropna().index)
XV = {c_: XD[c_].loc[idx].values for c_ in CASES}; T = len(idx)
S.add("bridge_first_month", str(idx[0])); S.add("bridge_n_months", T)
S0 = {c_: stage_terms(XV[c_], bF, wM, psi) for c_ in CASES}
SD = {c_: np.array([stage_terms(XV[c_], bF, WB[r_], PB[r_]) for r_ in range(R)]) for c_ in CASES}        # R x T x 8
# identity check against the package indexes (rounded to 5 decimals there)
mx = 0.0
for c_ in CASES:
    ix = pd.read_csv(RES / f"indexes_{c_}.csv", index_col=0); ix.index = pd.PeriodIndex(ix.index, freq="M"); ix = ix.loc[idx]
    mx = max(mx, np.abs(S0[c_].sum(1) - (ix.frbus_hp - ix.market).values).max())
S.add("bridge_identity_maxdiff", mx); assert mx < 2e-4
G0 = {c_: S0[c_].sum(1) for c_ in CASES}
LAB = STAGES
def chg12(a): return a[12:] - a[:-12]
# episodes
EPIS = {"1998-2001": ("1998-01", "2001-12"), "2004-06": ("2004-06", "2006-06"), "2022-24": ("2022-03", "2024-12")}
sel = lambda a, b_: (idx >= pd.Period(a, "M")) & (idx <= pd.Period(b_, "M"))
grp = {c_: pd.read_csv(RES / f"groups_{c_}.csv", index_col=0) for c_ in CASES}
for c_ in CASES: grp[c_].index = pd.PeriodIndex(grp[c_].index, freq="M")
for c_ in CASES:
    for form in ("level", "chg12"):
        for en, (a, e) in EPIS.items():
            sl = sel(a, e); sl12 = sl[12:]
            mean = (lambda A: A[sl].mean(0)) if form == "level" else (lambda A: chg12(A)[sl12].mean(0))
            pt = mean(S0[c_]); dr = np.array([mean(SD[c_][r_]) for r_ in range(R)])
            for k, st in enumerate(LAB):
                l, u = ci3(dr[:, k]); add("bridge_episodes", case=c_, form=form, episode=en, stage=st, point=pt[k], lo=l, hi=u)
            tot = dr.sum(1); l, u = ci3(tot)
            add("bridge_episodes", case=c_, form=form, episode=en, stage="total_F_minus_M", point=pt.sum(), lo=l, hi=u)
            S.add(f"ep_{en}_{c_}_{form}_gap", pt.sum()); S.add(f"ep_{en}_{c_}_{form}_gap_lo", l); S.add(f"ep_{en}_{c_}_{form}_gap_hi", u)
            for k, st in enumerate(LAB):
                S.add(f"ep_{en}_{c_}_{form}_{st}", pt[k])
            # equity attribution: group-style (equities group of F minus of M) against the like-for-like weight term
            if form == "level":
                gq = (grp[c_]["frbus_hp|equities"] - grp[c_]["market|equities"]).loc[idx][sl].mean()
                eqterm = pt[1] + (bF["equities"] - wBh[4][1]) * XV[c_][sl, 1].mean()
                other = pt.sum() - eqterm
                b3 = np.array([bF["y10"], bF["equities"], bF["dollar"]])
                eqb = dr[:, 1] + (b3[1] - b3[1] / (PB @ b3)) * XV[c_][sl, 1].mean(); eq_lo, eq_hi = ci3(eqb / dr.sum(1))
                add("equity_attribution", case=c_, episode=en, gap=pt.sum(), group_equity_gap=gq, weights_eq_term=pt[1], scale_eq_term=eqterm - pt[1], equity_total=eqterm,
                    all_other=other, equity_share=eqterm / pt.sum() if abs(pt.sum()) > 1e-9 else np.nan,
                    equity_share_lo=eq_lo, equity_share_hi=eq_hi,
                    dollar_term=pt[2], rates_term=pt[0] + pt[4] + pt[5] + pt[6], house_term=pt[7], scale_term=pt[3])
# variance shares, joint bootstrap
rngb = np.random.default_rng(SEED + 181)
for form in ("level", "chg12"):
    Tf = T if form == "level" else T - 12; L = 2 * BLOCK
    P0 = {c_: (S0[c_] if form == "level" else chg12(S0[c_])) for c_ in CASES}
    Mfix = {c_: (XV[c_][:, :3] @ wM) for c_ in CASES}
    pt = {c_: cov_shares(P0[c_], P0[c_].sum(1)) for c_ in CASES}
    bsr = {c_: [] for c_ in CASES}; bst = {c_: [] for c_ in CASES}
    # chain target: r* step; terms: weights+scale (nominal), policy, spreads, house (nominal), real transformation, r* equity transformation, r* other transformation
    def chain(Sn, Sr, Ss, form_):
        f = (lambda a: a) if form_ == "level" else chg12
        Sn, Sr, Ss = f(Sn), f(Sr), f(Ss)
        eq_tr = Ss[:, 1] - Sr[:, 1]
        t = np.c_[Sn[:, :4].sum(1), Sn[:, 4], Sn[:, 5] + Sn[:, 6], Sn[:, 7], Sr.sum(1) - Sn.sum(1), eq_tr, (Ss.sum(1) - Sr.sum(1)) - eq_tr]
        return t, Ss.sum(1)
    CH = ["weights_3assets_nominal", "policy_nominal", "spreads_nominal", "housing_nominal", "real_transformation", "rstar_equity_transformation", "rstar_other_transformation"]
    t0, g0 = chain(S0["nominal"], S0["real"], S0["rstar"], form); chpt = cov_shares(t0, g0)
    chb = []; sdr = {c_: [] for c_ in CASES}; corr = {c_: [] for c_ in CASES}
    for r_ in range(R):
        i = mbb(Tf, L, rngb)
        for c_ in CASES:
            A = SD[c_][r_]; A = A if form == "level" else chg12(A)
            bsr[c_].append(cov_shares(A[i], A[i].sum(1)))
            Mb = XV[c_][:, :3] @ WB[r_]; Fb = Mb + SD[c_][r_].sum(1)
            if form != "level": Mb, Fb = chg12(Mb), chg12(Fb)
            corr[c_].append(np.corrcoef(Mb[i], Fb[i])[0, 1]); sdr[c_].append(Mb[i].std() / Fb[i].std())
        tt, gg = chain(SD["nominal"][r_], SD["real"][r_], SD["rstar"][r_], form); chb.append(cov_shares(tt[i], gg[i]))
    for c_ in CASES:
        bsa = np.array(bsr[c_]); G_pt = P0[c_].sum(1)
        for k, st in enumerate(LAB):
            l, u = ci3(bsa[:, k]); add("bridge_variance", case=c_, form=form, stage=st, share=pt[c_][k], lo=l, hi=u)
            if c_ == "rstar": S.add(f"var_{form}_{st}", pt[c_][k]); S.add(f"var_{form}_{st}_lo", l); S.add(f"var_{form}_{st}_hi", u)
        Fp = Mfix[c_] + G_pt if form == "level" else None
        Mp = Mfix[c_] if form == "level" else chg12(Mfix[c_]); Fp = Mp + G_pt
        l, u = ci3(corr[c_]); add("bridge_summary", case=c_, form=form, stat="corr_F_M", point=np.corrcoef(Mp, Fp)[0, 1], lo=l, hi=u)
        l2, u2 = ci3(sdr[c_]); add("bridge_summary", case=c_, form=form, stat="sd_M_over_sd_F", point=Mp.std() / Fp.std(), lo=l2, hi=u2)
        add("bridge_summary", case=c_, form=form, stat="sd_F_minus_M", point=G_pt.std(), lo=np.nan, hi=np.nan)
        add("bridge_summary", case=c_, form=form, stat="sd_F", point=Fp.std(), lo=np.nan, hi=np.nan)
        S.add(f"corr_FM_{c_}_{form}", np.corrcoef(Mp, Fp)[0, 1]); S.add(f"corr_FM_{c_}_{form}_lo", l); S.add(f"corr_FM_{c_}_{form}_hi", u)
        S.add(f"sd_gap_{c_}_{form}", G_pt.std()); S.add(f"sd_F_{c_}_{form}", Fp.std())
    cha = np.array(chb)
    for k, st in enumerate(CH):
        l, u = ci3(cha[:, k]); add("bridge_chain", form=form, stage=st, share=chpt[k], lo=l, hi=u)
        S.add(f"chain_{form}_{st}", chpt[k]); S.add(f"chain_{form}_{st}_lo", l); S.add(f"chain_{form}_{st}_hi", u)
    # chain episode contributions (point and weight-draw interval)
    if form == "level":
        for en, (a, e) in EPIS.items():
            sl = sel(a, e)
            tdraw = np.array([chain(SD["nominal"][r_], SD["real"][r_], SD["rstar"][r_], "level")[0][sl].mean(0) for r_ in range(R)])
            for k, st in enumerate(CH):
                l, u = ci3(tdraw[:, k]); add("bridge_chain_episodes", episode=en, stage=st, point=t0[sl].mean(0)[k], lo=l, hi=u)
                S.add(f"chainep_{en}_{st}", t0[sl].mean(0)[k])

# ---------------------------------------------------------------- write
for k, rows in TAB.items():
    pd.DataFrame(rows).to_csv(RES / f"18_{k}.csv", index=False, float_format="%.6g")
S.save()
print({k: len(v) for k, v in TAB.items()})
