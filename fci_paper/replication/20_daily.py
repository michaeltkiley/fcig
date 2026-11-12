"""Step 20. Announcement against non-announcement movements at the SAME horizon, on the same traded assets (daily data). Answers the reviewer's point that the earlier
comparison of D = (w_B,4 - w_M)'x (FRB/US reading minus market reading) mixes horizons: 0.19 of the market move in intraday announcement windows (step 18), 0.24 in monthly and
0.33 in overlapping 12-month changes.

DESIGN (pre-specified; descriptive, intervals are 5th-95th percentiles of bootstrap draws; no hypothesis tests)
 assets   : daily 10-year yield (FRED DGS10, pp), daily equity valuation (100 ln of the daily CAPE in data/gs_daily.csv), nominal broad dollar (100 ln; FRED DTWEXB changes before 2006, DTWEXBGS
            from 2006; data/daily/SOURCES.md). Dates: common dates 1996-01 to 2026-09 (dollar series start 1995). Intraday S&P is not available; FRED's daily SP500 starts in 2016, so CAPE is used.
            Simplification [inference]: the market index uses the REAL dollar and (in the r* case) r*-adjusted rates and equities; over days to weeks inflation expectations, CPI and r* move
            by far less than the assets, so the nominal daily changes stand in for the market variables. The nominal dollar is therefore used for the real dollar; this is the main limit.
 weights  : w_M (results/market_weights.csv) and FRB/US w_B,4 = b_4/(b_4'psi), b_4 persistent-shift GDP effect at 4 quarters over the funds-rate yardstick (b_4'psi = 0.975), fixed, as in step 18.
            D(x) = (w_B,4 - w_M)'x; market move m(x) = w_M'x. Both use 100 ln units for equities and dollar. Weights and psi redrawn (first REPS rows of results/weights_boot.csv), as in step 18.
 days     : announcement days = dates of the USMPD scheduled events kept by lib.indexes.events_raw; excluded from all samples: the dates of dropped USMPD events and March-April 2020.
 part A   : horizons k = 1, 5, 22 trading days. Announcement windows: the k days ending on an announcement date (k = 1 is the announcement day; k > 1 includes k - 1 earlier days).
            Non-announcement windows: non-overlapping consecutive k-day blocks tiled from the first day of the sample that contain no announcement day and no excluded day.
            Statistics: mean |D|, mean |m|, ratio of the two, sd ratio, shares of windows with |D| above 0.25, 0.5 and 1 times |m| (thresholds scaled to the window's own market move).
            Bootstrap: announcement windows iid; non-announcement windows moving-block with a block of max(1, round(40 / k)) windows (about eight weeks); weights drawn jointly.
            PRIMARY COMPARISONS (3): ratio_ann minus ratio_other at k = 1, 5, 22. Everything else is descriptive.
 part B   : horizon ladder, ends on common days j (all days from the 253rd), k = 1, 5, 22, 66, 252 (overlapping windows). Two series: 'total' (all daily changes) and 'exann' (daily changes on
            announcement and excluded days set to zero, so the window holds only non-announcement movements of the same assets, same dates). A 12-month window always contains announcements, so
            'exann' is the non-announcement part of it. Block bootstrap over end days with a common block of 252 days for all horizons, weights drawn jointly; contrasts of ratios in 'exann'
            (PRE-SPECIFIED, 3): ratio(22) - ratio(1), ratio(252) - ratio(1), ratio(252) - ratio(22).
 Total comparisons: 3 primary (part A) + 3 contrasts (part B); no multiplicity adjustment (descriptive intervals).
Writes results/20_announce_vs_other.csv, 20_ladder.csv, 20_contrasts.csv and scalars_20_daily.csv."""
import numpy as np, pandas as pd
from lib import indexes as I
from lib.agree_core import MV, load_frbus, b_persist
from lib.daily_core import load_daily, day_flags, stats, mbb, ci
from lib.config import RES, REPS, SEED
from lib.report import Scalars

S = Scalars("20_daily"); rng = np.random.default_rng(SEED + 20)
mw = pd.read_csv(RES / "market_weights.csv", index_col=0); wM, psi = mw.weight.values, mw.response.values
Bd = pd.read_csv(RES / "weights_boot.csv").iloc[:REPS]; WB, PB = Bd[["w_ten", "w_eq", "w_usd"]].values, Bd[["psi_ten", "psi_eq", "psi_usd"]].values; R = len(Bd)
R_, G = load_frbus(); b4 = b_persist(R_, G, 4); wB = b4 / (b4 @ psi)
S.add("bpsi_h4", b4 @ psi)
WBd = b4[None, :] / (PB @ b4)[:, None]                                            # R x 3 FRB/US weights per draw

df = load_daily(); L = df[MV].values; N = len(df); ann, excl = day_flags(df.index)
S.add("first_day", str(df.index[0].date())); S.add("last_day", str(df.index[-1].date())); S.add("n_days", N); S.add("n_ann_days", int(ann.sum())); S.add("n_excl_days", int(excl.sum()))
dX = np.diff(L, axis=0, prepend=np.nan)                                            # row j: change from day j-1 to j
# sanity: daily changes on announcement days should have the policy-news sign (a quick descriptive check, not used later)
ev = I.events(); e1 = ev.set_index("Date").ns.reindex(df.index[ann])
S.add("n_ann_days_in_events", int(e1.notna().sum()))
S.add("corr_ns_dy10_ann", float(np.corrcoef(e1.dropna(), dX[ann][:, 0][e1.notna().values])[0, 1]))

def wchg(k, ends): return L[ends] - L[ends - k]
def clean(k, ends):                                                                  # no excluded day inside the window
    cs = np.r_[0, np.cumsum(excl)]; return np.array([cs[j + 1] - cs[j - k + 1] == 0 for j in ends], bool)
def ann_in(k, ends):
    cs = np.r_[0, np.cumsum(ann)]; return np.array([cs[j + 1] - cs[j - k + 1] > 0 for j in ends], bool)

rows = []; TAB = {"ann": [], "lad": [], "con": []}
# ------------------------------------------------------------ part A
for k in (1, 5, 22):
    e_ann = np.where(ann)[0]; e_ann = e_ann[(e_ann >= k)]; e_ann = e_ann[clean(k, e_ann)]
    e_all = np.arange(k, N, k); e_all = e_all[clean(k, e_all) & ~ann_in(k, e_all)]
    Za, Zo = wchg(k, e_ann), wchg(k, e_all)
    # one cross-check: no NaN
    assert not (np.isnan(Za).any() or np.isnan(Zo).any())
    pt = {"ann": stats(Za @ (wB - wM), Za @ wM), "other": stats(Zo @ (wB - wM), Zo @ wM)}
    Lw = max(1, round(40 / k)); bs = {"ann": [], "other": []}
    for r in range(R):
        d = WBd[r] - WB[r]
        ia = rng.integers(0, len(Za), len(Za)); io = mbb(len(Zo), Lw, rng)
        bs["ann"].append(stats(Za[ia] @ d, Za[ia] @ WB[r])); bs["other"].append(stats(Zo[io] @ d, Zo[io] @ WB[r]))
    for g, n in (("ann", len(Za)), ("other", len(Zo))):
        for st, v in pt[g].items():
            l, u = ci([x[st] for x in bs[g]]); TAB["ann"].append(dict(k=k, group=g, stat=st, point=v, lo=l, hi=u, n=n))
            if st in ("ratio", "mean_abs_D", "mean_abs_market", "share_gt_half"): S.add(f"A_k{k}_{g}_{st}", v); S.add(f"A_k{k}_{g}_{st}_lo", l); S.add(f"A_k{k}_{g}_{st}_hi", u)
        S.add(f"A_k{k}_{g}_n", n)
    for st in ("ratio", "share_gt_half"):
        dif = [a[st] - o[st] for a, o in zip(bs["ann"], bs["other"])]; rr = [a[st] / o[st] if o[st] > 0 else np.nan for a, o in zip(bs["ann"], bs["other"])]
        l, u = ci(dif); TAB["ann"].append(dict(k=k, group="ann_minus_other", stat=st, point=pt["ann"][st] - pt["other"][st], lo=l, hi=u, n=len(Za)))
        S.add(f"A_k{k}_diff_{st}", pt["ann"][st] - pt["other"][st]); S.add(f"A_k{k}_diff_{st}_lo", l); S.add(f"A_k{k}_diff_{st}_hi", u)
        if st == "ratio":
            l2, u2 = ci(rr); TAB["ann"].append(dict(k=k, group="ann_over_other", stat=st, point=pt["ann"][st] / pt["other"][st], lo=l2, hi=u2, n=len(Za)))
            S.add(f"A_k{k}_ratio_of_ratios", pt["ann"][st] / pt["other"][st]); S.add(f"A_k{k}_ratio_of_ratios_lo", l2); S.add(f"A_k{k}_ratio_of_ratios_hi", u2)

# ------------------------------------------------------------ part B
KS = (1, 5, 22, 66, 252); J = np.arange(252, N)
dz = dX.copy(); dz[0] = 0; dz[excl] = 0
dx_ex = dz.copy(); dx_ex[ann] = 0
Z = {"total": {k: (np.cumsum(dz, 0)[J] - np.cumsum(dz, 0)[J - k]) for k in KS}, "exann": {k: (np.cumsum(dx_ex, 0)[J] - np.cumsum(dx_ex, 0)[J - k]) for k in KS}}
T = len(J); S.add("ladder_first_end_day", str(df.index[252].date())); S.add("ladder_n_windows", T)
bsl = {(s, k): [] for s in Z for k in KS}
for r in range(R):
    i = mbb(T, 252, rng); d = WBd[r] - WB[r]
    for s in Z:
        for k in KS: bsl[(s, k)].append(stats(Z[s][k][i] @ d, Z[s][k][i] @ WB[r]))
ptl = {(s, k): stats(Z[s][k] @ (wB - wM), Z[s][k] @ wM) for s in Z for k in KS}
for (s, k), p in ptl.items():
    for st, v in p.items():
        l, u = ci([x[st] for x in bsl[(s, k)]]); TAB["lad"].append(dict(series=s, k=k, stat=st, point=v, lo=l, hi=u, n=T))
        if st in ("ratio", "mean_abs_D", "mean_abs_market", "share_gt_half"): S.add(f"B_{s}_k{k}_{st}", v); S.add(f"B_{s}_k{k}_{st}_lo", l); S.add(f"B_{s}_k{k}_{st}_hi", u)
for a, b_ in ((22, 1), (252, 1), (252, 22)):
    for st in ("ratio", "share_gt_half"):
        dif = [x[st] - y[st] for x, y in zip(bsl[("exann", a)], bsl[("exann", b_)])]; pt = ptl[("exann", a)][st] - ptl[("exann", b_)][st]; l, u = ci(dif)
        TAB["con"].append(dict(series="exann", stat=st, k_hi=a, k_lo=b_, point=pt, lo=l, hi=u, share_draws_positive=float(np.mean(np.array(dif) > 0))))
        S.add(f"B_contrast_{st}_{a}_{b_}", pt); S.add(f"B_contrast_{st}_{a}_{b_}_lo", l); S.add(f"B_contrast_{st}_{a}_{b_}_hi", u)
for k, rows_ in TAB.items():
    pass
for key, name in (("ann", "announce_vs_other"), ("lad", "ladder"), ("con", "contrasts")):
    pd.DataFrame(TAB[key]).to_csv(RES / f"20_{name}.csv", index=False, float_format="%.6g")
S.save(); print({k: len(v) for k, v in TAB.items()})
