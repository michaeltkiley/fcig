"""Experiment (16 Nov 2026, second request): the same two-variable quarterly VAR on Note A's four full indexes, as published by the paper's package
(fci_paper/replication/results/indexes_<step>.csv): market index, GS replication, FRB/US (headline, no house prices; FP-A9), FCI-G 1-year.
Output gap (CBO) and one FCI; quarterly average; 4 lags; constant; 1973Q1 (FCI-G: 1974Q1, first available) to 2026Q3; Cholesky both orderings;
FCI shock scaled to raise the FCI 1 point on impact; with and without dummies 2020Q1..2021Q1. Bands: moving-block bootstrap of residual pairs (4-quarter
blocks), recursive, dummies fixed, 1,000 draws, 90 percent. Steps nominal, real, rstar (baseline)."""
from pathlib import Path
import numpy as np, pandas as pd

HERE = Path(__file__).resolve().parent; PKG = HERE.parents[1] / "fci_paper" / "replication"
OUT = HERE / "results"; OUT.mkdir(exist_ok=True)
P, H, REPS, BL, SEED = 4, 12, 1000, 4, 20261116
HZ = [4, 8, 12]; START, END_Q = pd.Period("1973Q1", "Q"), pd.Period("2026Q3", "Q")
DUM = list(pd.period_range("2020Q1", "2021Q1", freq="Q"))
IDX = {"market": "Market", "gs": "GS", "frbus": "FRB/US", "fcig_1yr": "FCI-G"}

def fred_q(name):
    s = pd.read_csv(HERE / "data" / f"{name}.csv", parse_dates=["observation_date"]).set_index("observation_date").iloc[:, 0]
    s = pd.to_numeric(s, errors="coerce"); s.index = s.index.to_period("Q"); return s
gap = (100 * (fred_q("GDPC1") / fred_q("GDPPOT") - 1)).dropna()

def ols(Z, dums):
    T = len(Z); Xl = np.column_stack([np.ones(T - P)] + [Z[P - l:T - l] for l in range(1, P + 1)] + ([dums[P:]] if dums is not None else []))
    B = np.linalg.lstsq(Xl, Z[P:], rcond=None)[0]; U = Z[P:] - Xl @ B; return B, U, U.T @ U / (len(U) - Xl.shape[1])

def irf(B, Sig, order):
    A = [B[1 + 2 * (l - 1):1 + 2 * l].T for l in range(1, P + 1)]
    perm = [0, 1] if order == "gap" else [1, 0]; L = np.zeros((2, 2)); L[np.ix_(perm, perm)] = np.linalg.cholesky(Sig[np.ix_(perm, perm)])
    Y = np.zeros((H + 1, 2)); Y[0] = L[:, 1] / L[1, 1]
    for t in range(1, H + 1): Y[t] = sum(A[l - 1] @ Y[t - l] for l in range(1, P + 1) if t - l >= 0)
    return Y

def run(df, order, dummies):
    Z = df.values; T = len(Z)
    dums = np.column_stack([(df.index == q).astype(float) for q in DUM]) if dummies else None
    B, U, S = ols(Z, dums); pt = irf(B, S, order)
    rng = np.random.default_rng(SEED); n = len(U); Uc = U - U.mean(0); dr = []
    for _ in range(REPS):
        st = rng.integers(0, n - BL + 1, int(np.ceil(n / BL))); Ub = np.concatenate([Uc[s:s + BL] for s in st])[:n]; Zb = Z.copy()
        for t in range(P, T):
            x = np.r_[1.0, np.concatenate([Zb[t - l] for l in range(1, P + 1)]), (dums[t] if dums is not None else [])]; Zb[t] = x @ B + Ub[t - P]
        Bb, _, Sb = ols(Zb, dums); dr.append(irf(Bb, Sb, order))
    return pt, np.array(dr)

rows = []
for step in ["rstar", "real", "nominal"]:
    ix = pd.read_csv(PKG / "results" / f"indexes_{step}.csv", index_col=0); ix.index = pd.PeriodIndex(ix.index, freq="M")
    for col, lab in IDX.items():
        q = ix[col].dropna(); q = q.groupby(q.index.asfreq("Q")).mean()
        df = pd.concat([gap.rename("gap"), q.rename("fci")], axis=1).loc[START:END_Q].dropna()
        for dummies in [True, False]:
            for order in ["gap", "fci"]:
                pt, dr = run(df, order, dummies)
                r = dict(step=step, fci=lab, dummies_2020=dummies, order=order + "_first", start=str(df.index[0]), end=str(df.index[-1]))
                for h in HZ:
                    r[f"gap_h{h}"] = pt[h, 0]; r[f"lo90_h{h}"], r[f"hi90_h{h}"] = np.percentile(dr[:, h, 0], [5, 95]); r[f"fci_own_h{h}"] = pt[h, 1]
                rows.append(r); print(step, lab, dummies, order, " ".join(f"{pt[h,0]:+.2f}" for h in HZ), flush=True)
R = pd.DataFrame(rows); R.to_csv(OUT / "irf_full_indexes.csv", index=False, float_format="%.4f")

md = []
for step in ["rstar", "real", "nominal"]:
    md += [f"\n### Step: {step}\n", "| FCI | 2020 dummies | ordering | h4 | h8 | h12 | FCI own h4 / h8 / h12 |", "|---|---|---|---|---|---|---|"]
    for _, r in R[R.step == step].iterrows():
        md.append(f"| {r.fci} | {'yes' if r.dummies_2020 else 'no'} | {r.order.replace('_', ' ')} | " + " | ".join(f"{r[f'gap_h{h}']:+.2f} [{r[f'lo90_h{h}']:+.2f}, {r[f'hi90_h{h}']:+.2f}]" for h in HZ)
                  + f" | {r.fci_own_h4:.2f} / {r.fci_own_h8:.2f} / {r.fci_own_h12:.2f} |")
(OUT / "summary_full_indexes.md").write_text("\n".join(md) + "\n")
