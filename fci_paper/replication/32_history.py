"""Step 32. History of the policy-news index (market index, "MCFCI") against the macro-model and statistical indexes (new version, stage 2; FP-A66).

Level indexes at the r* step: market (policy-news weights), GS replication (published weights), FRB/US (headline, no house prices). Flow: FCI-G 1-year
(nominal step, closest to the published series; r* step as a check). Statistical: NFCI, ANFCI (monthly means, in two-year-yield units via their policy-news
response). Monthly, 1973-01 to END (NFCI from 1973, FCI-G from 1974).
 (1) Co-movement: correlations in levels and 12-month changes, 1973-2026, 1973-1995, 1996-2026; 90 percent intervals from a moving-block bootstrap
     of months (blocks of 24). FCI-G is itself built from past changes, so in the change12 rows it enters as published (not differenced again).
 (2) Variance by asset: share of each level index's variance carried by rates, equities and the dollar (cov(component, index) / var(index); shares sum to one).
 (3) Similarity of directions on the r* step assets (10-year, equities, dollar): cosine of the weights scaled by each asset's standard deviation, and the
     correlation of the readings (w_j' Omega w_k / sqrt(...)), levels and 12-month changes; the reduced-form bridge beta_k = g' Omega w_k / w_k' Omega w_k.
 (4) Tight or tightening: the market level (r* step; above zero = tighter than its 1973-2026 mean) against FCI-G 1-year (a flow; above zero = a drag on
     growth over the next year from the past year's changes), by episode and in all months: share of months in which the flow says tightening while the
     level says loose, and the reverse.
 (5) Shape: skewness, excess kurtosis and the tail ratio (q95 - q50) / (q50 - q05) of each index, 1990-2026 and 1973-2026.
Writes results/32_*.csv and scalars_32_history.csv."""
import numpy as np, pandas as pd
from scipy.stats import skew, kurtosis
from lib import data, cases, indexes as I
from lib.agree_core import MV, load_frbus, b_persist, mbb
from lib.config import RES, SEED, START, END
from lib.report import Scalars

S = Scalars("32_history")
IX = {st: pd.read_csv(RES / f"indexes_{st}.csv", index_col=0) for st in ("nominal", "rstar")}
for d in IX.values():
    d.index = pd.PeriodIndex(d.index, freq="M")
R, N = IX["rstar"], IX["nominal"]
SER = pd.DataFrame({"market": R.market, "gs": R.gs, "frbus": R.frbus, "fcig": N.fcig_1yr, "fcig_rstar": R.fcig_1yr, "nfci": R.nfci, "anfci": R.anfci})
SER.to_csv(RES / "32_series.csv", float_format="%.5f")
NAMES = ["market", "gs", "frbus", "fcig", "fcig_rstar", "nfci", "anfci"]

# (1) co-movement
PER = {"1973-2026": ("1973-01", END), "1973-1995": ("1973-01", "1995-12"), "1996-2026": ("1996-01", END)}
rng = np.random.default_rng(SEED); REPS = 1000; L = 24
rows = []
for basis in ("level", "change12"):
    Z = SER if basis == "level" else SER.diff(12).assign(fcig=SER.fcig, fcig_rstar=SER.fcig_rstar)   # FCI-G is already a flow (12-month changes): not differenced again
    for per, (a, b) in PER.items():
        Zp = Z.loc[a:b]
        for i, x in enumerate(NAMES):
            for y in NAMES[i + 1:]:
                P = Zp[[x, y]].dropna().values
                if len(P) < 60:
                    continue
                c0 = np.corrcoef(P.T)[0, 1]
                draws = [np.corrcoef(P[mbb(len(P), L, rng)].T)[0, 1] for _ in range(REPS)]
                lo, hi = np.percentile(draws, [5, 95])
                rows.append(dict(basis=basis, period=per, x=x, y=y, n=len(P), corr=c0, lo=lo, hi=hi))
                S.add(f"corr_{basis}_{per}_{x}_{y}", c0); S.add(f"corr_{basis}_{per}_{x}_{y}_lo", lo); S.add(f"corr_{basis}_{per}_{x}_{y}_hi", hi)
pd.DataFrame(rows).to_csv(RES / "32_comovement.csv", index=False, float_format="%.4f")

# (2) variance by asset (r* step)
D = data.load(); X = cases.inputs(D, "rstar")
w = pd.read_csv(RES / "market_weights.csv", index_col=0).weight.values
conv = pd.read_csv(RES / "conversions.csv", index_col=0).to_2y
_, Cm = I.market(X, w); _, Cg = I.gs(X, conv["GS"]); _, Cf, _ = I.frbus(X, house=False)
GROUP = {"policy": "rates", "y10": "rates", "mortgage_spread": "rates", "bbb_spread": "rates", "equities": "equities", "dollar": "dollar", "dollar_gs": "dollar"}
vrows = []
for lab, C in (("market", Cm), ("gs", Cg), ("frbus", Cf)):
    C = C.loc[START:END].dropna()
    G = C.T.groupby(lambda c: GROUP[c]).sum().T
    for basis in ("level", "change12"):
        Gb = G if basis == "level" else G.diff(12).dropna()
        tot = Gb.sum(axis=1)
        for grp in ("rates", "equities", "dollar"):
            sh = float(Gb[grp].cov(tot) / tot.var()) if grp in Gb else 0.0
            vrows.append(dict(index=lab, basis=basis, group=grp, share=sh)); S.add(f"var_{lab}_{basis}_{grp}", sh)
pd.DataFrame(vrows).to_csv(RES / "32_variance_by_asset.csv", index=False, float_format="%.4f")

# (3) similarity of directions on the three common assets (r* step; common scale as step 26)
raw = I.events_raw(); ev = I.events()
Yw = ev[["UST10Y", "SP500", "DXY"]].values; _, psiF, _ = I.gls_weights(Yw, ev.ns.values)
Rq, Gq = load_frbus(); b = b_persist(Rq, Gq, 4); g = np.array([I.GS_W["y10"], I.GS_W["equities"], I.GS_W["dollar_gs"]])
W = {"market": w, "frbus": b / (b @ psiF), "gs": g / (g @ psiF)}
Xm = X[MV].loc[START:END].dropna()
srows = []
for basis, Zb in (("level", Xm), ("change12", Xm.diff(12).dropna())):
    O = np.cov(Zb.values.T); sd = np.sqrt(np.diag(O))
    for x, y in (("market", "gs"), ("market", "frbus"), ("gs", "frbus")):
        wx, wy = W[x], W[y]
        cos_sd = float((wx * sd) @ (wy * sd) / np.linalg.norm(wx * sd) / np.linalg.norm(wy * sd))
        corr_o = float(wx @ O @ wy / np.sqrt((wx @ O @ wx) * (wy @ O @ wy)))
        beta_xy = float(wy @ O @ wx / (wx @ O @ wx))          # response of index x if the true direction were y (common scale)
        srows.append(dict(basis=basis, x=x, y=y, cos_sd=cos_sd, corr_omega=corr_o, beta_x_if_y=beta_xy, beta_y_if_x=float(wx @ O @ wy / (wy @ O @ wy))))
        S.add(f"sim_{basis}_{x}_{y}_cos", cos_sd); S.add(f"sim_{basis}_{x}_{y}_corr", corr_o)
pd.DataFrame(srows).to_csv(RES / "32_similarity.csv", index=False, float_format="%.4f")
pd.DataFrame(W, index=MV).to_csv(RES / "32_weights_common.csv", float_format="%.6g")

# (4) tight or tightening: market level (r*) against FCI-G 1-year (nominal)
EP = {"1980-82": ("1980-01", "1982-12"), "1990-91": ("1990-01", "1991-12"), "1994": ("1994-01", "1994-12"), "1998-2001": ("1998-01", "2001-12"),
      "2004-06": ("2004-06", "2006-06"), "2008-09": ("2008-01", "2009-12"), "2013": ("2013-05", "2013-12"), "2020": ("2020-02", "2020-12"),
      "2022-24": ("2022-03", "2024-12")}
TT = SER[["market", "fcig"]].dropna()
erows = []
for ep, (a, e) in {**EP, "all months": (str(TT.index[0]), END)}.items():
    s = TT.loc[a:e]
    r = dict(episode=ep, n=len(s), market_level=s.market.mean(), fcig=s.fcig.mean(),
             flow_tightening_level_loose=float(((s.fcig > 0) & (s.market < 0)).mean()), flow_easing_level_tight=float(((s.fcig < 0) & (s.market > 0)).mean()),
             same_sign=float((np.sign(s.fcig) == np.sign(s.market)).mean()))
    erows.append(r)
    for k, v in r.items():
        if k != "episode":
            S.add(f"tt_{ep}_{k}", v)
pd.DataFrame(erows).to_csv(RES / "32_tight_vs_tightening.csv", index=False, float_format="%.4f")
S.add("tt_corr_level_fcig", float(TT.market.corr(TT.fcig))); S.add("tt_corr_change12_fcig", float(TT.market.diff(12).corr(TT.fcig)))

# (5) shape
hrows = []
for per, a in (("1990-2026", "1990-01"), ("1973-2026", "1973-01")):
    for c in NAMES:
        s = SER[c].loc[a:END].dropna(); q = s.quantile([0.05, 0.5, 0.95])
        r = dict(period=per, index=c, n=len(s), skew=float(skew(s)), excess_kurtosis=float(kurtosis(s)), tail_ratio=float((q[0.95] - q[0.5]) / (q[0.5] - q[0.05])))
        hrows.append(r)
        for k in ("skew", "excess_kurtosis", "tail_ratio"):
            S.add(f"shape_{per}_{c}_{k}", r[k])
pd.DataFrame(hrows).to_csv(RES / "32_shape.csv", index=False, float_format="%.4f")
print(pd.DataFrame(rows).query("period == '1973-2026'").round(2).to_string(index=False))
print(pd.DataFrame(vrows).round(2).to_string(index=False)); print(pd.DataFrame(srows).round(3).to_string(index=False))
print(pd.DataFrame(erows).round(2).to_string(index=False)); print(pd.DataFrame(hrows).round(2).to_string(index=False))
S.save()
