"""Step 26. Four calibrations on common assets, dates, transformations and units (FP-A44; Path B, step 1).

PORTFOLIOS on the three common assets at the r* step (10-year yield less expected inflation less r*, pp; equity valuation as the earnings-yield gap converted to CAPE log points; real broad dollar, 100 ln):
  F   market weights, policy news = futures factor (baseline; 02_weights.py)
  Y   market weights, policy news = two-year yield change, same 253 announcements (21_signal.py)
  B   FRB/US weights b at four quarters, persistent shifts (funds-rate equivalents; 18/21)
  G   published Goldman Sachs U.S. FCI weights on the same three variables (lib/indexes.GS_W: 10-year 0.451 per pp, equities -0.049 per percent, dollar 0.060 per percent; GS points;
      Hatzius et al. 2017 as reported in Caballero-Simsek 2026, Table 1; calibrated to one-year-ahead GDP growth effects). The GS policy rate and BBB spread are held fixed, as the
      FRB/US index's other variables are held fixed in B. G is a PUBLISHED BENCHMARK applied to this package's series: GS defines its equity variable as prices over a 10-year average of
      earnings and uses a nominal trade-weighted dollar; here the r*-step equity and real dollar series are used for all four portfolios.
QUESTIONS (fixed before any number was read)
 (1) Figure 1 valuation: each portfolio's reading of the dollar appreciation (3.9 log points) relative to the equity decline (5 log points); unit-free.
 (2) Historical distances: every portfolio normalized to ONE common reference direction, the futures-factor response psi_F (w'psi_F = 1), so that differences reflect relative weights and not
     the yardstick. Pairwise mean absolute difference of the 12-month-change readings, 1996-01..data end (points and basis points of the two-year yield), and its ratio to the mean absolute
     F reading. Secondary: each market portfolio on its own signal (w_Y'psi_Y = 1), as in the paper.
 (3) Judgments: in each month, do all four agree on the sign? do at least two give materially opposing readings (opposite signs, each at least t from zero), t = 0.10 and 0.25? Share of months,
     and the years with the largest cross-portfolio range.
 Uncertainty: announcement bootstrap (REPS_W draws, same generator as steps 02/21/25): F, Y and psi_F re-estimated on each draw; B and G fixed. 5th-95th percentiles; paired across portfolios.
Writes results/26_*.csv and scalars_26_four_way.csv."""
import numpy as np, pandas as pd
from lib import data, cases, indexes as I
from lib.agree_core import MV, load_frbus, b_persist, ns_arr
from lib.config import RES, SEED, END, REPS_W
from lib.report import Scalars

S = Scalars("26_four_way")
EQ, USD = -5.0, 3.9
raw = I.events_raw(); n = len(raw)
X5 = raw[["MP1", "MP2", "ED2", "ED3", "ED4"]].values; u2 = raw.UST2Y.values; Y3 = raw[["UST10Y", "SP500", "DXY"]].values

def fitg(f, Yv):
    fc = f - f.mean(); Yc = Yv - Yv.mean(0); psi = (fc @ Yc) / (fc @ fc); Rr = Yc - np.outer(fc, psi)
    Sg = Rr.T @ Rr / (len(f) - 2); w = np.linalg.solve(Sg, psi); return w / (psi @ w), psi
def est(rows):
    wF, pF = fitg(ns_arr(X5[rows], u2[rows]), Y3[rows]); wY, pY = fitg(u2[rows], Y3[rows]); return wF, pF, wY, pY

R_, Gq = load_frbus(); b = b_persist(R_, Gq, 4)
g = np.array([I.GS_W["y10"], I.GS_W["equities"], I.GS_W["dollar_gs"]])
allr = np.arange(n); wF0, pF0, wY0, pY0 = est(allr)
assert np.allclose(wF0, pd.read_csv(RES / "market_weights.csv", index_col=0).weight.values, atol=1e-8)
rng = np.random.default_rng(SEED); IX = np.array([rng.integers(0, n, n) for _ in range(REPS_W)])
DR = [est(ix) for ix in IX]
Bd = pd.read_csv(RES / "weights_boot.csv"); k0 = min(len(Bd), len(DR))
assert np.abs(np.array([d[0] for d in DR[:k0]]) - Bd[["w_ten", "w_eq", "w_usd"]].values[:k0]).max() < 1e-6
ci = lambda a: (float(np.nanpercentile(a, 5)), float(np.nanpercentile(a, 95)))
NAMES = ["F", "Y", "B", "G"]

def portfolios(wF, pF, wY, pY, own=False):
    """Weights of the four portfolios; common normalization w'psi_F = 1 (own=True: Y on its own signal)."""
    P = {"F": wF, "Y": wY if own else wY / (wY @ pF), "B": b / (b @ pF), "G": g / (g @ pF)}
    return P

# (1) Figure 1 valuation (unit-free)
def fig1(w): return (w[2] * USD) / (w[1] * EQ)
P0 = portfolios(wF0, pF0, wY0, pY0)
rows = []
for k in NAMES:
    v0 = fig1(P0[k]); dr = [fig1(portfolios(*d)[k]) for d in DR]; l, u = ci(dr) if k in ("F", "Y") else (np.nan, np.nan)
    rows.append(dict(portfolio=k, dollar_over_equity=v0, lo=l, hi=u, eq_reading=P0[k][1] * EQ, usd_reading=P0[k][2] * USD, w_ten=P0[k][0], w_eq=P0[k][1], w_usd=P0[k][2]))
    S.add(f"fig1_{k}", v0); S.add(f"fig1_{k}_lo", l); S.add(f"fig1_{k}_hi", u)
    S.add(f"eqread_{k}", P0[k][1] * EQ); S.add(f"usdread_{k}", P0[k][2] * USD)
pd.DataFrame(rows).to_csv(RES / "26_fig1.csv", index=False, float_format="%.6g")
S.add("wY_on_psiF", float(wY0 @ pF0)); S.add("gs_ratio_raw", (g[2] * USD) / (abs(g[1]) * abs(EQ)))      # the published-weight arithmetic (0.06 x 3.9)/(0.049 x 5)

# (2) historical distances, (3) judgments
Xr = cases.inputs(data.load(), "rstar")[MV]
Z = Xr.diff(12).loc["1996-01":END].dropna(); idx = Z.index; Zv = Z.values; T = len(Zv)
PAIRS = [(a, c) for i, a in enumerate(NAMES) for c in NAMES[i + 1:]]
def summary(P):
    Rd = {k: Zv @ P[k] for k in NAMES}; mF = np.abs(Rd["F"]).mean(); out = {}
    for a, c in PAIRS:
        d = np.abs(Rd[a] - Rd[c]).mean(); out[f"mad_{a}{c}"] = d; out[f"ratio_{a}{c}"] = d / mF
    M = np.column_stack([Rd[k] for k in NAMES]); sg = np.sign(M)
    out["all_same_sign"] = float((np.abs(sg.sum(1)) == 4).mean())
    for t in (0.10, 0.25):
        pos = (M >= t).any(1); neg = (M <= -t).any(1); out[f"any_opposing_t{int(t*100)}"] = float((pos & neg).mean())
        out[f"range_ge_t{int(t*100)}"] = float((M.max(1) - M.min(1) >= t).mean())
        for a, c in PAIRS:
            out[f"opp_{a}{c}_t{int(t*100)}"] = float(((np.sign(Rd[a]) != np.sign(Rd[c])) & (np.minimum(np.abs(Rd[a]), np.abs(Rd[c])) >= t)).mean())
    out["mean_range"] = float((M.max(1) - M.min(1)).mean())
    return out, M
O0, M0 = summary(P0); OD = [summary(portfolios(*d))[0] for d in DR]
O0own, _ = summary(portfolios(wF0, pF0, wY0, pY0, own=True))
rows = []
for k, v in O0.items():
    dr = np.array([o[k] for o in OD]); l, u = ci(dr)
    rows.append(dict(stat=k, point=v, lo=l, hi=u, own_normalization=O0own[k])); S.add(f"h_{k}", v); S.add(f"h_{k}_lo", l); S.add(f"h_{k}_hi", u); S.add(f"own_{k}", O0own[k])
# paired comparison of the two discrepancies the paper ranks: |B - F| against |Y - F| (common normalization)
dd = np.array([o["mad_FB"] - o["mad_FY"] for o in OD]); l, u = ci(dd); S.add("pair_madFB_minus_madFY", O0["mad_FB"] - O0["mad_FY"]); S.add("pair_madFB_minus_madFY_lo", l); S.add("pair_madFB_minus_madFY_hi", u)
rows.append(dict(stat="madFB_minus_madFY", point=O0["mad_FB"] - O0["mad_FY"], lo=l, hi=u, own_normalization=np.nan))
dd = np.array([o["mad_BG"] - o["mad_FB"] for o in OD]); l, u = ci(dd); rows.append(dict(stat="madBG_minus_madFB", point=O0["mad_BG"] - O0["mad_FB"], lo=l, hi=u, own_normalization=np.nan))
pd.DataFrame(rows).to_csv(RES / "26_history.csv", index=False, float_format="%.6g")
mon = pd.DataFrame(M0, columns=NAMES); mon.insert(0, "month", idx.astype(str)); mon["range"] = M0.max(1) - M0.min(1)
mon.to_csv(RES / "26_monthly.csv", index=False, float_format="%.6g")
yr = mon.assign(year=mon.month.str[:4]).groupby("year")["range"].mean().sort_values(ascending=False)
yr.rename("mean_range").to_csv(RES / "26_years.csv", float_format="%.6g")
for i, (y, v) in enumerate(yr.head(5).items()): S.add(f"top_year_{i+1}", int(y)); S.add(f"top_year_{i+1}_range", v)
# (4) the months of material opposition (any pair, t = 0.25 and 0.10), which portfolios oppose, and episode averages of the four readings
opp_rows = []
for t in (0.25, 0.10):
    for i in range(T):
        r = M0[i]
        if (r >= t).any() and (r <= -t).any():
            opp_rows.append(dict(threshold=t, month=str(idx[i]), **{k: r[j] for j, k in enumerate(NAMES)}, d_y10=Zv[i, 0], d_eq=Zv[i, 1], d_usd=Zv[i, 2],
                                 tight=",".join(k for j, k in enumerate(NAMES) if r[j] >= t), easy=",".join(k for j, k in enumerate(NAMES) if r[j] <= -t)))
OPP = pd.DataFrame(opp_rows); OPP.to_csv(RES / "26_opposing_months.csv", index=False, float_format="%.6g")
o25 = OPP[OPP.threshold == 0.25]
S.add("opp25_n", len(o25)); S.add("opp10_n", int((OPP.threshold == 0.10).sum()))
S.add("opp25_first", o25.month.min() if len(o25) else ""); S.add("opp25_last", o25.month.max() if len(o25) else "")
EP = {"1998-2001": ("1998-01", "2001-12"), "2022-24": ("2022-03", "2024-12"), "2004-06": ("2004-06", "2006-06"), "2008-09": ("2008-01", "2009-12")}
erow = []
for ep, (a, e) in EP.items():
    msk = np.array([(p_ >= pd.Period(a, "M")) and (p_ <= pd.Period(e, "M")) for p_ in idx])
    for j, k in enumerate(NAMES):
        v = float(M0[msk, j].mean()); erow.append(dict(episode=ep, portfolio=k, mean=v)); S.add(f"ep_{ep}_{k}", v)
    S.add(f"ep_{ep}_n", int(msk.sum())); S.add(f"ep_{ep}_range_mean", float((M0[msk].max(1) - M0[msk].min(1)).mean()))
    S.add(f"ep_{ep}_opp25", int((((M0[msk] >= 0.25).any(1)) & ((M0[msk] <= -0.25).any(1))).sum()))
pd.DataFrame(erow).to_csv(RES / "26_episodes.csv", index=False, float_format="%.6g")
# (5) accounting for a month and for the episodes: asset changes and each portfolio's contributions (weight x change), so that I_j - I_k = sum_a (w_ja - w_ka) x_a can be read off
AN = ["y10", "eq", "usd"]; wrow = []
def account(label, xv):
    for j, a in enumerate(AN): S.add(f"acc_{label}_x_{a}", float(xv[j]))
    for k in NAMES:
        for j, a in enumerate(AN):
            S.add(f"acc_{label}_{k}_{a}", float(P0[k][j] * xv[j])); wrow.append(dict(case=label, portfolio=k, asset=a, change=float(xv[j]), weight=float(P0[k][j]), contribution=float(P0[k][j] * xv[j])))
        S.add(f"acc_{label}_{k}_total", float(P0[k] @ xv))
i98 = list(idx.astype(str)).index("1998-01"); account("jan1998", Zv[i98])
for ep, (a, e) in EP.items():
    msk = np.array([(p_ >= pd.Period(a, "M")) and (p_ <= pd.Period(e, "M")) for p_ in idx]); account("ep" + ep.replace("-", ""), Zv[msk].mean(0))
pd.DataFrame(wrow).to_csv(RES / "26_accounting.csv", index=False, float_format="%.6g")
# (6) co-movement and peaks: correlations of the four readings; the peak reading and the range of B - F within each episode
Cm = np.corrcoef(M0.T); off = Cm[np.triu_indices(4, 1)]
S.add("corr_min", float(off.min())); S.add("corr_max", float(off.max())); S.add("corr_FB", float(Cm[0, 2])); S.add("corr_FG", float(Cm[0, 3]))
for j, k in enumerate(NAMES): S.add(f"sd_{k}", float(M0[:, j].std(ddof=1)))
for ep, (a, e) in EP.items():
    msk = np.array([(p_ >= pd.Period(a, "M")) and (p_ <= pd.Period(e, "M")) for p_ in idx]); sub = M0[msk]; mi = idx[msk]
    tag = "ep" + ep.replace("-", "")
    for j, k in enumerate(NAMES): S.add(f"peak_{tag}_{k}", float(sub[:, j].max()))
    S.add(f"peak_{tag}_month", mi[int(sub[:, 0].argmax())].strftime("%B %Y"))
    dBF = sub[:, 2] - sub[:, 0]; S.add(f"dBF_{tag}_min", float(dBF.min())); S.add(f"dBF_{tag}_max", float(dBF.max())); S.add(f"dFB_{tag}_n25", int((np.abs(dBF) >= 0.25).sum()))
    S.add(f"range_{tag}_max", float((sub.max(1) - sub.min(1)).max()))
S.add("n_months", T); S.save()
print(pd.DataFrame(rows).round(3).to_string()); print(yr.head(8).round(3))
