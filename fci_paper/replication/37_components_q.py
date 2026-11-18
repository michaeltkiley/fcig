"""Step 37. Which financial variables carry the activity response: the quarterly VAR of step 33 with the MCFCI replaced by its components
(FP-A75; the analysis Note B left to Note A, FS-A85 D10).

Components are the MCFCI's contributions (weight times demeaned variable, in index points; results/groups_<step>.csv): the 10-year yield ("rates"),
equities and the dollar, quarterly averages. Three models, same sample, lags, constant, 2020Q1-2021Q1 dummies and block bootstrap as step 33:
  R  gap + MCFCI                      (step 33's model; the shock raises the index 1 point, gap first)
  E  gap + (rates + dollar) + equities (equities free)
  F  gap + rates + equities + dollar   (all three free)
The shock in E and F is a policy-direction impulse: the components move on impact by their shares of a policy move in the windows (w_i psi_i, summing to
1; results/market_weights.csv), the gap does not move on impact (gap first). In R this is the Cholesky shock of step 33, so R reproduces it exactly.
Weights test: in the gap equation of F (E), the restriction of the index is that the three (two) components carry equal coefficients at every lag;
F test of 2P (P) restrictions. The F response is also split by component (each component moved alone by its share). Writes results/37_components.csv, 37_tests.csv, 37_by_component.csv, scalars_37_components.csv."""
import numpy as np, pandas as pd
from scipy import stats
from lib.config import RES, DATA, SEED
from lib.report import Scalars

S = Scalars("37_components")
P, H, BL, Q_REPS = 4, 12, 4, 1000
HZ = [4, 8, 12]
DUM = list(pd.period_range("2020Q1", "2021Q1", freq="Q"))

def fred_q(name):
    s = pd.read_csv(DATA / f"{name}.csv"); s = pd.Series(pd.to_numeric(s.iloc[:, 1], errors="coerce").values, index=pd.PeriodIndex(pd.to_datetime(s.iloc[:, 0]), freq="Q"))
    return s.dropna()
gap = (100 * (fred_q("GDPC1") / fred_q("GDPPOT") - 1)).dropna()
START_Q, END_Q = pd.Period("1973Q1", "Q"), gap.index.max()

wm = pd.read_csv(RES / "market_weights.csv", index_col=0)
SH = (wm.weight * wm.response).rename({"y10": "rates"})                      # shares of a policy move in the windows; sum to 1
assert abs(SH.sum() - 1) < 1e-6

def regressors(Z, dums):
    T = len(Z)
    return np.column_stack([np.ones(T - P)] + [Z[P - l:T - l] for l in range(1, P + 1)] + ([dums[P:]] if dums is not None else []))

def ols(Z, dums):
    X = regressors(Z, dums); B = np.linalg.lstsq(X, Z[P:], rcond=None)[0]; U = Z[P:] - X @ B
    return B, U

def irf(B, b, k):
    A = [B[1 + k * (l - 1):1 + k * l].T for l in range(1, P + 1)]
    Y = np.zeros((H + 1, k)); Y[0] = b
    for t in range(1, H + 1):
        Y[t] = sum(A[l - 1] @ Y[t - l] for l in range(1, P + 1) if t - l >= 0)
    return Y

def run(Z, b, dums):
    T, k = Z.shape; B, U = ols(Z, dums); pt = irf(B, b, k)
    rng = np.random.default_rng(SEED); n = len(U); Uc = U - U.mean(0); dr = []
    for _ in range(Q_REPS):
        st = rng.integers(0, n - BL + 1, int(np.ceil(n / BL))); Ub = np.concatenate([Uc[s:s + BL] for s in st])[:n]; Zb = Z.copy()
        for t in range(P, T):
            x = np.r_[1.0, np.concatenate([Zb[t - l] for l in range(1, P + 1)]), (dums[t] if dums is not None else [])]
            Zb[t] = x @ B + Ub[t - P]
        Bb, _ = ols(Zb, dums); dr.append(irf(Bb, b, k))
    return pt, np.array(dr)

def ftest(Z, dums, groups):
    """Gap equation: equal coefficients on the components in `groups` (column indexes into Z) at every lag."""
    X = regressors(Z, dums); y = Z[P:, 0]; k = Z.shape[1]
    beta = np.linalg.lstsq(X, y, rcond=None)[0]; e = y - X @ beta; df = len(y) - X.shape[1]; s2 = e @ e / df
    R = []
    for l in range(1, P + 1):
        for g in groups[1:]:
            r = np.zeros(X.shape[1]); r[1 + k * (l - 1) + groups[0]] = 1; r[1 + k * (l - 1) + g] = -1; R.append(r)
    R = np.array(R); Rb = R @ beta; V = s2 * np.linalg.inv(X.T @ X)
    F = Rb @ np.linalg.solve(R @ V @ R.T, Rb) / len(R)
    return F, len(R), df, 1 - stats.f.cdf(F, len(R), df)

def q(s):
    s = s.dropna(); return s.groupby(s.index.asfreq("Q")).mean()

rows, trows, crows = [], [], []
for step in ("rstar", "real", "nominal"):
    ix = pd.read_csv(RES / f"indexes_{step}.csv", index_col=0); ix.index = pd.PeriodIndex(ix.index, freq="M")
    g = pd.read_csv(RES / f"groups_{step}.csv", index_col=0); g.index = pd.PeriodIndex(g.index, freq="M")
    c = pd.DataFrame({k: q(g[f"market|{k}"]) for k in ("rates", "equities", "dollar")})
    assert (q(ix.market) - c.sum(axis=1)).abs().max() < 1e-3, "components do not add to the MCFCI"
    base = pd.concat([gap.rename("gap"), q(ix.market).rename("fci"), c], axis=1).loc[START_Q:END_Q].dropna()
    MODELS = {"R": (base[["gap", "fci"]], [0, 1.0], None),
              "E": (pd.DataFrame({"gap": base.gap, "rd": base.rates + base.dollar, "eq": base.equities}), [0, SH.rates + SH.dollar, SH.equities], [1, 2]),
              "F": (base[["gap", "rates", "equities", "dollar"]], [0, SH.rates, SH.equities, SH.dollar], [1, 2, 3])}
    for dummies in (True, False):
        for m, (df, b, grp) in MODELS.items():
            Z = df.values; dums = np.column_stack([(df.index == d).astype(float) for d in DUM]) if dummies else None
            pt, dr = run(Z, np.array(b, float), dums)
            tag = f"{step}_{m}_{'d' if dummies else 'nd'}"
            r = dict(step=step, model=m, dummies=dummies, start=str(df.index[0]), end=str(df.index[-1]))
            for h in HZ:
                lo, hi = np.percentile(dr[:, h, 0], [5, 95])
                r[f"gap_h{h}"], r[f"lo_h{h}"], r[f"hi_h{h}"] = pt[h, 0], lo, hi
                r[f"fci_h{h}"] = pt[h, 1:].sum()                              # the MCFCI's own path (sum of the components)
                S.add(f"{tag}_h{h}", pt[h, 0]); S.add(f"{tag}_h{h}_lo", lo); S.add(f"{tag}_h{h}_hi", hi); S.add(f"{tag}_fci_h{h}", r[f"fci_h{h}"])
            rows.append(r)
            if grp:
                F, nr, dfd, p = ftest(Z, dums, grp)
                trows.append(dict(step=step, model=m, dummies=dummies, F=F, restrictions=nr, df=dfd, p=p))
                S.add(f"{tag}_F", F); S.add(f"{tag}_p", p)
            print(f"{tag:14s} gap " + " ".join(f"{r[f'gap_h{h}']:+.2f} [{r[f'lo_h{h}']:+.2f},{r[f'hi_h{h}']:+.2f}]" for h in HZ)
                  + (f"   F={F:.2f} p={p:.3f}" if grp else ""), flush=True)
            if m == "F":                                                      # the F response split by component (each component's share alone)
                B, _ = ols(Z, dums)
                for j, kk in enumerate(("rates", "equities", "dollar")):
                    bj = np.zeros(4); bj[1 + j] = b[1 + j]; y = irf(B, bj, 4)
                    crows.append(dict(step=step, dummies=dummies, component=kk, share=b[1 + j], **{f"gap_h{h}": y[h, 0] for h in HZ}))
                    for h in HZ:
                        S.add(f"{tag}_{kk}_h{h}", y[h, 0])
for k, v in SH.items():
    S.add(f"share_{k}", v)
R = pd.DataFrame(rows); R.to_csv(RES / "37_components.csv", index=False, float_format="%.4f")
pd.DataFrame(trows).to_csv(RES / "37_tests.csv", index=False, float_format="%.4f")
pd.DataFrame(crows).to_csv(RES / "37_by_component.csv", index=False, float_format="%.4f")
s33 = pd.read_csv(RES / "scalars_33_qvar.csv", index_col=0).iloc[:, 0]
assert abs(R.query("step == 'rstar' and model == 'R' and dummies").gap_h4.iloc[0] - s33["rstar_market_d_gap_h4"]) < 1e-8, "R does not reproduce step 33"
S.save()
