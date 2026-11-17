"""Step 36. Levels and changes in the quarterly output-gap equation (new version, stage 5; FP-A69).

The author's point (FP-A63): a level index read in a VAR with lags carries the same dynamics as a change measure such as FCI-G, while the level also says
whether conditions are tight or loose. The output-gap equation of the step-33 VAR (gap on 4 own lags and 4 lags of an index) is estimated with:
  (a) 4 lags of the index level; (b) 4 lags of its 4-quarter change; (c) 4 lags of FCI-G 1-year (nominal; a published change measure).
Reported: R2 of the gap equation; for (a), the sum of the level coefficients (zero when only changes matter: the lags then form differences) with a HAC
Wald test; the 4-quarter-ahead local projection of the gap change on the same regressors (R2 and the long-run coefficient). 1973Q1 (FCI-G 1974Q1) to the
last GDP quarter, 2020Q1-2021Q1 dummies, quarterly averages, r* step for the level indexes.
Writes results/36_levelflow_q.csv and scalars_36_levelflow_q.csv."""
import numpy as np, pandas as pd
import statsmodels.api as sm
from lib.config import RES, DATA
from lib.report import Scalars

S = Scalars("36_levelflow_q")
def fred_q(name):
    s = pd.read_csv(DATA / f"{name}.csv"); s = pd.Series(pd.to_numeric(s.iloc[:, 1], errors="coerce").values, index=pd.PeriodIndex(pd.to_datetime(s.iloc[:, 0]), freq="Q"))
    return s.dropna()
gap = (100 * (fred_q("GDPC1") / fred_q("GDPPOT") - 1)).dropna()
def q(s):
    s = s.dropna(); return s.groupby(s.index.asfreq("Q")).mean()
R = pd.read_csv(RES / "indexes_rstar.csv", index_col=0); R.index = pd.PeriodIndex(R.index, freq="M")
N = pd.read_csv(RES / "indexes_nominal.csv", index_col=0); N.index = pd.PeriodIndex(N.index, freq="M")
FG = q(N.fcig_1yr)
DUM = pd.period_range("2020Q1", "2021Q1", freq="Q")
rows = []
for lab in ("market", "gs", "frbus"):
    L = q(R[lab]); D4 = L - L.shift(4)
    base = pd.DataFrame({"gap": gap})
    for k in range(1, 5):
        base[f"g{k}"] = gap.shift(k); base[f"L{k}"] = L.shift(k); base[f"D{k}"] = D4.shift(k); base[f"F{k}"] = FG.shift(k)
    base["y4"] = gap.shift(-4) - gap
    for d in DUM:
        base[f"d{d}"] = (base.index == d).astype(float)
    base = base.loc[pd.Period("1974Q2", "Q"):]
    dums = [c for c in base.columns if c.startswith("d")]
    own = [f"g{k}" for k in range(1, 5)]
    for spec, xs in (("level", [f"L{k}" for k in range(1, 5)]), ("change4", [f"D{k}" for k in range(1, 5)]), ("fcig", [f"F{k}" for k in range(1, 5)]),
                     ("level+fcig", [f"L{k}" for k in range(1, 5)] + [f"F{k}" for k in range(1, 5)])):
        for dep in ("gap", "y4"):
            dd = base[[dep] + own + xs + dums].dropna()
            m = sm.OLS(dd[dep], sm.add_constant(dd[own + xs + dums])).fit(cov_type="HAC", cov_kwds={"maxlags": 4})
            r = dict(index=lab, spec=spec, dep=dep, n=len(dd), r2=m.rsquared, r2_own_only=sm.OLS(dd[dep], sm.add_constant(dd[own + dums])).fit().rsquared)
            lv = [c for c in xs if c.startswith("L")]
            if lv:
                R_ = np.zeros((1, len(m.params))); R_[0, [list(m.params.index).index(c) for c in lv]] = 1
                w = m.wald_test(R_, scalar=True); r["sum_level"] = float(m.params[lv].sum()); r["p_sum_level_zero"] = float(w.pvalue)
            fx = [c for c in xs if c.startswith("F")]
            if fx:
                R_ = np.zeros((len(fx), len(m.params)))
                for i, c in enumerate(fx): R_[i, list(m.params.index).index(c)] = 1
                r["p_fcig_joint_zero"] = float(m.wald_test(R_, scalar=True).pvalue)
            rows.append(r)
            for k, v in r.items():
                if k not in ("index", "spec", "dep"):
                    S.add(f"{lab}_{spec}_{dep}_{k}", v)
T = pd.DataFrame(rows); T.to_csv(RES / "36_levelflow_q.csv", index=False, float_format="%.4f")
print(T.round(3).to_string(index=False))
S.save()
