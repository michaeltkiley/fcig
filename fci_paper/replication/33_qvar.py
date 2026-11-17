"""Step 33. Reduced-form effects on activity: two-variable quarterly VAR of the CBO output gap and one index, and an FRB/US benchmark (new version,
stage 4; FP-A67; moved into the package from experimental/note_a_qvar/qvar_full.py and frbus_match.py).

VAR: output gap 100 (GDPC1 / GDPPOT - 1) and one index (quarterly average of the monthly series), 4 lags, constant, 1973Q1 (FCI-G from 1974Q1) to the
last quarter with GDP; with and without dummies for 2020Q1-2021Q1. Shock scaled to raise the index 1 point on impact; two Cholesky orderings:
"gap first" (no same-quarter effect on the gap: GDP responds with a lag) and "index first" (= the generalized impulse response of Pesaran and Shin).
Indexes: market (MCFCI), GS, FRB/US (headline), FCI-G 1-year at the nominal, real and r* steps; NFCI and ANFCI (two-year-yield units). 90 percent
intervals: moving-block bootstrap of residual pairs (blocks of 4 quarters), recursive, dummies fixed, Q_REPS draws.
FRB/US benchmark: for each policy-unit index (market, GS, FRB/US) at the r* step, the funds-rate path that makes the index's FRB/US reading follow its own
VAR path, built from the persistent 1 pp hike (VAR expectations, full transmission; data/frbus_hike_paths.csv) by superposition; GDP read off FRB/US.
An index's reading of the hike uses the model's changes in the index's variables (r* step read off nominal model changes; stock-wealth change for CAPE).
Writes results/33_irf.csv, 33_frbus_match.csv, 33_hike_readings.csv, scalars_33_qvar.csv."""
import numpy as np, pandas as pd
from lib import indexes as I
from lib.config import RES, DATA, SEED
from lib.report import Scalars

S = Scalars("33_qvar")
P, H, BL, Q_REPS = 4, 12, 4, 1000
HZ = [4, 8, 12]
DUM = list(pd.period_range("2020Q1", "2021Q1", freq="Q"))

def fred_q(name):
    s = pd.read_csv(DATA / f"{name}.csv"); s = pd.Series(pd.to_numeric(s.iloc[:, 1], errors="coerce").values, index=pd.PeriodIndex(pd.to_datetime(s.iloc[:, 0]), freq="Q"))
    return s.dropna()
gap = (100 * (fred_q("GDPC1") / fred_q("GDPPOT") - 1)).dropna()
START_Q, END_Q = pd.Period("1973Q1", "Q"), gap.index.max()

def ols(Z, dums):
    T = len(Z); Xl = np.column_stack([np.ones(T - P)] + [Z[P - l:T - l] for l in range(1, P + 1)] + ([dums[P:]] if dums is not None else []))
    B = np.linalg.lstsq(Xl, Z[P:], rcond=None)[0]; U = Z[P:] - Xl @ B
    return B, U, U.T @ U / (len(U) - Xl.shape[1])

def irf(B, Sig, order):
    A = [B[1 + 2 * (l - 1):1 + 2 * l].T for l in range(1, P + 1)]
    perm = [0, 1] if order == "gap" else [1, 0]
    L = np.zeros((2, 2)); L[np.ix_(perm, perm)] = np.linalg.cholesky(Sig[np.ix_(perm, perm)])
    Y = np.zeros((H + 1, 2)); Y[0] = L[:, 1] / L[1, 1]
    for t in range(1, H + 1):
        Y[t] = sum(A[l - 1] @ Y[t - l] for l in range(1, P + 1) if t - l >= 0)
    return Y

def run(df, order, dummies, boot=True):
    Z = df.values; T = len(Z)
    dums = np.column_stack([(df.index == q).astype(float) for q in DUM]) if dummies else None
    B, U, Sg = ols(Z, dums); pt = irf(B, Sg, order)
    if not boot:
        return pt, None
    rng = np.random.default_rng(SEED); n = len(U); Uc = U - U.mean(0); dr = []
    for _ in range(Q_REPS):
        st = rng.integers(0, n - BL + 1, int(np.ceil(n / BL))); Ub = np.concatenate([Uc[s:s + BL] for s in st])[:n]; Zb = Z.copy()
        for t in range(P, T):
            x = np.r_[1.0, np.concatenate([Zb[t - l] for l in range(1, P + 1)]), (dums[t] if dums is not None else [])]
            Zb[t] = x @ B + Ub[t - P]
        Bb, _, Sb = ols(Zb, dums); dr.append(irf(Bb, Sb, order))
    return pt, np.array(dr)

def frame(m):
    q = m.dropna(); q = q.groupby(q.index.asfreq("Q")).mean()
    return pd.concat([gap.rename("gap"), q.rename("fci")], axis=1).loc[START_Q:END_Q].dropna()

IDX = {"market": "market", "gs": "gs", "frbus": "frbus", "fcig": "fcig_1yr", "nfci": "nfci", "anfci": "anfci"}
rows, paths = [], {}
for step in ("rstar", "real", "nominal"):
    ix = pd.read_csv(RES / f"indexes_{step}.csv", index_col=0); ix.index = pd.PeriodIndex(ix.index, freq="M")
    for lab, col in IDX.items():
        if lab in ("nfci", "anfci") and step != "rstar":
            continue                                          # NFCI/ANFCI do not depend on the step
        df = frame(ix[col])
        for dummies in (True, False):
            for order in ("gap", "fci"):
                pt, dr = run(df, order, dummies)
                paths[(step, lab, dummies, order)] = pt
                r = dict(step=step, index=lab, dummies=dummies, order=order + "_first", start=str(df.index[0]), end=str(df.index[-1]))
                for h in HZ:
                    r[f"gap_h{h}"] = pt[h, 0]; r[f"lo_h{h}"], r[f"hi_h{h}"] = np.percentile(dr[:, h, 0], [5, 95]); r[f"own_h{h}"] = pt[h, 1]
                    S.add(f"{step}_{lab}_{'d' if dummies else 'nd'}_{order}_h{h}", pt[h, 0])
                    S.add(f"{step}_{lab}_{'d' if dummies else 'nd'}_{order}_h{h}_lo", r[f"lo_h{h}"]); S.add(f"{step}_{lab}_{'d' if dummies else 'nd'}_{order}_h{h}_hi", r[f"hi_h{h}"])
                rows.append(r)
                print(step, lab, dummies, order, " ".join(f"{pt[h, 0]:+.2f}" for h in HZ), flush=True)
pd.DataFrame(rows).to_csv(RES / "33_irf.csv", index=False, float_format="%.4f")

# ------------------------------------------------------------------ FRB/US benchmark
Pf, Gf = I.frbus_paths(); cols = [c for c in I.FRBUS_VARS if c != "house"]
wf = I.phi_at(Pf[cols], 4) / Gf[4]
hk = pd.read_csv(DATA / "frbus_hike_paths.csv").sort_values("quarter")
dX = pd.DataFrame({"policy": hk.rff, "y10": hk.rg10, "mortgage_spread": hk["mortgage spread"], "bbb_spread": hk.rbbbp, "equities": hk["stocks %"],
                   "dollar": hk["dollar %"], "dollar_gs": hk["dollar %"]})
wm = pd.read_csv(RES / "market_weights.csv", index_col=0).weight
to2y = pd.read_csv(RES / "conversions.csv", index_col=0).to_2y["GS"]
WREAD = {"frbus": pd.Series(wf[cols].values, index=cols), "market": pd.Series(wm.values, index=I.MARKET_VARS),
         "gs": pd.Series(I.GS_W) * to2y}
READ = {k: dX[list(w.index)].values @ w.values for k, w in WREAD.items()}      # READ[k][q] = index k's reading q quarters after the hike starts
hr = pd.DataFrame({"quarter": hk.quarter.values, **{f"{k}_reading": v for k, v in READ.items()}, "gdp_persistent_hike": hk.gdp.values})
for k, w in WREAD.items():
    for v in w.index:
        hr[f"{k}_{v}"] = dX[v].values * w[v]
hr.to_csv(RES / "33_hike_readings.csv", index=False, float_format="%.5f")
Gk = hk.gdp.values
mrows = []
for lab in ("market", "gs", "frbus"):
    F = READ[lab]
    for dummies in (True, False):
        for order in ("gap", "fci"):
            pt = paths[("rstar", lab, dummies, order)]; x = pt[:, 1]; n = len(x); a = np.zeros(n)
            for t in range(n):
                a[t] = (x[t] - sum(a[s] * F[t - s] for s in range(t))) / F[0]
            gdp = np.array([sum(a[s] * Gk[h - s] for s in range(h + 1)) for h in range(n)])
            ffr = np.cumsum(a)
            for h in range(n):
                mrows.append(dict(index=lab, dummies=dummies, order=order + "_first", quarter=h, index_path=x[h], ffr_path=ffr[h], frbus_gdp=gdp[h], var_gap=pt[h, 0]))
            for h in HZ:
                tag = f"m_{lab}_{'d' if dummies else 'nd'}_{order}_h{h}"
                S.add(tag + "_frbus", gdp[h]); S.add(tag + "_ffr", ffr[h]); S.add(tag + "_ratio", pt[h, 0] / gdp[h])
pd.DataFrame(mrows).to_csv(RES / "33_frbus_match.csv", index=False, float_format="%.4f")
for k in READ:
    S.add(f"hike_reading_{k}_q1", READ[k][0]); S.add(f"hike_reading_{k}_q4", READ[k][3])
for h in HZ:
    S.add(f"frbus_hike_gdp_h{h}", Gk[h - 1])
assert abs(pd.DataFrame(rows).query("step == 'rstar' and index == 'market' and dummies and order == 'gap_first'").gap_h4.iloc[0] + 0.75) < 0.05, "VAR does not reproduce the exploration (about -0.75)"
S.save()
print(hr.head(8).round(3).to_string(index=False))
