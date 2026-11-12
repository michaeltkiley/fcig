"""Pseudo-real-time versions of the stance / level-flow inputs. Reuses followup2/stance/common.py (monkey-patching its Y and CTL) and the replication package.
Writes only into this folder."""
import sys, numpy as np, pandas as pd, statsmodels.api as sm
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "followup2" / "stance")); sys.path.insert(0, str(HERE.parent.parent / "replication"))
import common as C
from lib.config import RES
from lib import data as RD, cases as RC, indexes as RI
OUT = HERE / "out"; OUT.mkdir(exist_ok=True)
H = 12
P = pd.read_csv(OUT / "rt_panel.csv", index_col=0); P.index = pd.PeriodIndex(P.index, freq="M")

def nrou_expost():
    n = pd.read_csv(RD.DATA / "NROU.csv"); n = pd.Series(n.iloc[:, 1].values, index=pd.PeriodIndex(pd.to_datetime(n.iloc[:, 0]), freq="Q"))
    return RD.mid_quarter(n)
NEX = nrou_expost()
def ex(t):  # ex-post NROU at months t (PeriodIndex)
    return pd.Series(NEX.reindex(t).values, index=t)

def versions():
    """name -> (Y, CTL) for outcomes du, pay, pi. 'rev' = revised data as in the stance package."""
    t = P.index; out = {"rev": (C.Y, C.CTL)}
    def build(gap_k, gap12_k, gap_t_f, gap_h_f):
        Y = pd.DataFrame({"du": gap_h_f - gap_t_f, "pay": P.p_h_f - P.p_t_f, "pi": P.c_h_f - P.c_t_f}, index=t)
        ctl = {"du": pd.DataFrame({"u": gap_k, "du12": gap_k - gap12_k}),
               "pay": pd.DataFrame({"g12": P.p_k - P.p12_k, "g3": 4 * (P.p_k - P.p3_k)}),
               "pi": pd.DataFrame({"p12": P.c_k - P.c12_k, "p3": 4 * (P.c_k - P.c3_k)})}
        return Y, ctl
    nt, nt12, nh = ex(t), ex(t - 12), ex(t + 12)
    out["rt1"] = build(P.u_k - nt.values, P.u12_k - nt12.values, P.u_t_f - nt.values, P.u_h_f - nh.values)      # real-time u, payrolls, core PCE; ex-post NROU
    out["rt2"] = build(P.u_k - P.n_k, P.u12_k - P.n12_k, P.u_t_f - P.n_t_f, P.u_h_f - P.n_h_f)                  # + real-time CBO NROU (origins from 2011)
    return out

def rstar_rt():
    """Monthly real-time Laubach-Williams r*: the final-point estimate of the latest vintage released by the end of the month (step function)."""
    R = pd.read_csv(OUT / "lw_realtime.csv", parse_dates=["release"])
    fix = {"2010q4": "2011-01-26", "2016q4": "2017-04-21", "2019q2": "2019-08-29"}     # release dates mistyped / duplicated in the NY Fed file (the last is an inference)
    for k, v in fix.items(): R.loc[R.vintage == k, "release"] = pd.Timestamp(v)
    R = R.sort_values("release"); s = pd.Series(np.nan, index=pd.period_range("2005-01", "2026-09", freq="M"))
    for m in s.index:
        a = R[R.release <= m.to_timestamp(how="end")]
        if len(a): s[m] = a.rstar_rt.iloc[-1]
    s.loc["2020-09":"2023-04"] = np.nan          # no vintage published between Aug 2020 and May 2023
    return s

def rt_index_rstar():
    """Market index at the r* step with real-time r* (weights unchanged); also returns the check that the package series is reproduced."""
    D = RD.load(); w = pd.read_csv(RES / "market_weights.csv", index_col=0).weight.values
    X = RC.inputs(D, "rstar", rstar="rstar LW"); chk = RI.market(X, w)[0].loc["1973-01":"2026-09"]
    ref = C.index("rstar", "market")
    D = D.copy(); D["rstar RT"] = rstar_rt()
    X2 = RC.inputs(D, "rstar", rstar="rstar RT"); m2 = RI.market(X2, w)[0].where(D["rstar RT"].notna()); return m2, float((chk - ref).abs().max())

def hacstats(D, ow, lags, oos=True):
    r0 = C.hac_ols(D, ow, lags); r1 = C.hac_ols(D, ow + ["ff"], lags); r2 = C.hac_ols(D, ow + ["idx"], lags); r3 = C.hac_ols(D, ow + ["ff", "idx"], lags)
    s = dict(n=len(D), first=str(D.index[0]), last=str(D.index[-1]), gain_idx_alone=r2.rsquared_adj - r0.rsquared_adj, gain_ff_alone=r1.rsquared_adj - r0.rsquared_adj,
             gain_idx_given_ff=r3.rsquared_adj - r1.rsquared_adj, t_idx_alone=r2.tvalues["idx"], t_idx_both=r3.tvalues["idx"], b_idx_both=r3.params["idx"],
             t_ff_both=r3.tvalues["ff"], b_ff_both=r3.params["ff"])
    if oos:
        F = C.oos(D, ow)
        if len(F) >= 60:
            e = {m: F.y - F[m] for m in ("M0", "M1", "M3")}
            d = e["M1"] ** 2 - e["M3"] ** 2; cw = d + (F["M1"] - F["M3"]) ** 2
            s.update(n_oos=len(F), rmse_idx_given_ff=float(np.sqrt((e["M3"] ** 2).mean() / (e["M1"] ** 2).mean())), cw_idx_given_ff=C.mean_t(cw.values), dm_idx_given_ff=C.mean_t(d.values))
    return s

def design_v(Y, CTL, yname, f, x, form, start=None, stop=None):
    """as C.design but with explicit Y, CTL; standardisation on the final common sample is done by the caller via align()."""
    C.Y, C.CTL = Y, CTL
    D = C.design(yname, f, x, form)
    C.Y, C.CTL = ORIG
    return D
ORIG = (C.Y, C.CTL)
