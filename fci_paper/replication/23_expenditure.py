"""Step 23. Do the two readings predict different expenditure components? (colleague report p.5, a ReStat-style implication; FRB/US channels from step 22.)

PRE-SPECIFIED (written before any estimate was looked at)
 y_net = mean over the next four quarters (t+1..t+4) of the contribution of net exports to real GDP growth (percentage points, annualised; FRED A019RY2Q224SBEA).
 y_dom = same for private domestic demand: contributions of consumption and gross private domestic investment (DPCERY2Q224SBEA + A006RY2Q224SBEA).
 Regressors as in step 19's quarterly GDP check: own lags (previous four-quarter mean and previous quarter of the same contribution), dM and D (12-month changes at the quarter's last month, the same series as step 19),
 HAC with 6 quarterly lags, 8-quarter block bootstrap (REPS draws; common draws for both outcomes so that differences are paired). Samples: main (origins from 1976-03) and 1996+.
 Prediction P1 (channel logic of step 22: the dollar reaches GDP through net exports): the coefficient on D is negative for net exports (a reading in which the dollar weighs more predicts a weaker net-export contribution beyond the market-implied index change).
 Prediction P2: composition shifts net exports more than domestic demand, gamma_dom - gamma_net > 0.
 Everything else is descriptive. Two outcomes x two samples, no adjustment for the number of tests.
Writes results/23_expenditure.csv and scalars_23_expenditure.csv."""
import numpy as np, pandas as pd, statsmodels.api as sm
from lib import comp_core as C
from lib.config import RES, DATA, REPS
from lib.report import Scalars
from lib.stance_core import ffg

S = Scalars("23_expenditure")
X, X12, dM, D, dB, chk, W = C.changes()
FF = ffg("rstar").diff(12)
def q(name):
    d = pd.read_csv(DATA / f"{name}.csv"); return pd.Series(d.iloc[:, 1].values, index=pd.PeriodIndex(pd.to_datetime(d.observation_date), freq="Q"))
NET = q("A019RY2Q224SBEA"); DOM = q("DPCERY2Q224SBEA") + q("A006RY2Q224SBEA")
def frame(c, start):
    f4 = c.rolling(4).mean()                                  # mean of the last four quarters (quarters t-3..t)
    y = f4.shift(-4)                                          # mean of quarters t+1..t+4
    ix = pd.PeriodIndex([k.asfreq("M", "e") for k in c.index], freq="M")
    cols = {"y": pd.Series(y.values, ix), "g4": pd.Series(f4.values, ix), "g1": pd.Series(c.values, ix), "dM": dM.reindex(ix), "D": D.reindex(ix)}
    return pd.DataFrame(cols).loc[start:"2026-09"].dropna()
rows = []
for sname, start in (("main", "1976-03"), ("1996+", "1996-01")):
    Fn, Fd = frame(NET, start), frame(DOM, start); ix_ = Fn.index.intersection(Fd.index); Fn, Fd = Fn.loc[ix_], Fd.loc[ix_]
    idx = C.block_idx(len(Fn), REPS, 300 + (sname == "1996+"), 8); cols = ["g4", "g1", "dM", "D"]
    Bn, Bd = C.boot_coefs(Fn, cols, idx), C.boot_coefs(Fd, cols, idx)
    rg = float(np.percentile(sm.OLS(Fn.D, sm.add_constant(Fn.dM)).fit().resid, 95) - np.percentile(sm.OLS(Fn.D, sm.add_constant(Fn.dM)).fit().resid, 5))
    for nm, Fx, Bx in (("net_exports", Fn, Bn), ("private_domestic", Fd, Bd)):
        r = C.hac(Fx, cols, 6); ci = r.conf_int(alpha=0.10)
        for term in ("dM", "D"):
            j = cols.index(term) + 1
            rows.append(dict(sample=sname, outcome=nm, term=term, n=len(Fx), coef=r.params[term], se=r.bse[term], t=r.tvalues[term], lo90=ci.loc[term, 0], hi90=ci.loc[term, 1],
                             boot_lo90=C.pct(Bx[:, j], 5), boot_hi90=C.pct(Bx[:, j], 95), range_p5_p95=rg, effect=r.params[term] * rg, mean_y=float(Fx.y.mean()), sd_y=float(Fx.y.std())))
    jd = cols.index("D") + 1; diff = Bd[:, jd] - Bn[:, jd]
    rd = C.hac(Fd, cols, 6).params["D"] - C.hac(Fn, cols, 6).params["D"]
    rows.append(dict(sample=sname, outcome="dom_minus_net", term="D", n=len(Fn), coef=rd, se=np.nan, t=np.nan, lo90=np.nan, hi90=np.nan, boot_lo90=C.pct(diff, 5), boot_hi90=C.pct(diff, 95),
                     range_p5_p95=rg, effect=rd * rg, mean_y=np.nan, sd_y=np.nan))
R = pd.DataFrame(rows); R.to_csv(RES / "23_expenditure.csv", index=False)
for _, r in R.iterrows():
    for k in ("coef", "se", "t", "lo90", "hi90", "boot_lo90", "boot_hi90", "effect", "n"):
        if pd.notna(r[k]): S.add(f"exp_{r['sample'].replace('+','p')}_{r.outcome}_{r.term}_{k}", r[k])
S.add("exp_check_dM_vs_step03", chk); S.save()
print(R.round(3).to_string())
