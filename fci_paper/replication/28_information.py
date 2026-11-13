"""Step 28. Market weights with policy news cleaned of information effects (FP-A54, item 6; FP-A55: Bauer-Swanson only).

Questions (fixed before any number was read):
 (1) Re-estimate the futures-based market weights F with three published measures of policy news that remove information effects, each matched to this package's announcements and
     scaled so that one unit raises the two-year yield by one percentage point (same scaling as lib.indexes.ns_factor):
       BS_orth Bauer-Swanson (2023) surprise orthogonalized to public news before the announcement (MPS_ORTH; data/bauer_swanson_surprises.csv; announcements to 2019)
     To separate the measure from the sample, the baseline futures factor is re-estimated on each matched sample (F_same) and BS's raw surprise MPS is run on the BS sample.
 (2) For each set: weights on the common scale (w'psi_F = 1, psi_F = full-sample baseline response), the Figure 1 ratio (dollar reading over equity reading),
     the mean absolute distance of 12-month-change readings (1996 to sample end) from F, B (FRB/US) and G (published GS weights), as in step 26.
 (3) Announcement bootstrap (REPS_W draws, resampling the matched announcements) for the Figure 1 ratio and the distance to F.
Writes results/28_information.csv and scalars_28_information.csv."""
import numpy as np, pandas as pd
from lib import data, cases, indexes as I
from lib.agree_core import MV, load_frbus, b_persist, ns_arr
from lib.config import RES, SEED, END, REPS_W, DATA
from lib.report import Scalars

S = Scalars("28_information")
EQ, USD = -5.0, 3.9
raw = I.events_raw().copy(); raw["d"] = raw.Date.dt.strftime("%Y-%m-%d")
bs = pd.read_csv(DATA / "bauer_swanson_surprises.csv").groupby("Date", as_index=False).first()


def fitg(f, Yv):
    fc = f - f.mean(); Yc = Yv - Yv.mean(0); psi = (fc @ Yc) / (fc @ fc); Rr = Yc - np.outer(fc, psi)
    Sg = Rr.T @ Rr / (len(f) - 2); w = np.linalg.solve(Sg, psi); return w / (psi @ w), psi


def to2y(f, u2):
    return f * (f @ u2) / (f @ f)


X5a = raw[["MP1", "MP2", "ED2", "ED3", "ED4"]].values; u2a = raw.UST2Y.values; Y3a = raw[["UST10Y", "SP500", "DXY"]].values
wF0, pF0 = fitg(ns_arr(X5a, u2a), Y3a)
assert np.allclose(wF0, pd.read_csv(RES / "market_weights.csv", index_col=0).weight.values, atol=1e-8)
R_, Gq = load_frbus(); b = b_persist(R_, Gq, 4); b = b / (b @ pF0)
g = np.array([I.GS_W["y10"], I.GS_W["equities"], I.GS_W["dollar_gs"]]); g = g / (g @ pF0)
Xr = cases.inputs(data.load(), "rstar")[MV]
Zv = Xr.diff(12).loc["1996-01":END].dropna().values
RF0 = Zv @ wF0; mF = np.abs(RF0).mean()

mb = raw.merge(bs, left_on="d", right_on="Date", suffixes=("", "_bs")).dropna(subset=["MPS", "MPS_ORTH"])
CASES = {"F_full": (raw, None), "F_sameBS": (mb, None), "BS_raw": (mb, "MPS"), "BS_orth": (mb, "MPS_ORTH")}


def weights(df, col):
    X5 = df[["MP1", "MP2", "ED2", "ED3", "ED4"]].values; u2 = df.UST2Y.values; Y3 = df[["UST10Y", "SP500", "DXY"]].values
    f = ns_arr(X5, u2) if col is None else to2y(df[col].values.astype(float), u2)
    w, p = fitg(f, Y3)
    return w / (w @ pF0), p, float(np.corrcoef(f, ns_arr(X5, u2))[0, 1])


def stats(w):
    R = Zv @ w
    return dict(fig1=(w[2] * USD) / (w[1] * EQ), dF=np.abs(R - RF0).mean() / mF, dB=np.abs(R - Zv @ b).mean() / mF, dG=np.abs(R - Zv @ g).mean() / mF,
                dF_bp=100 * np.abs(R - RF0).mean())


rng = np.random.default_rng(SEED); rows = []
ci = lambda a: (float(np.nanpercentile(a, 5)), float(np.nanpercentile(a, 95)))
for k, (df, col) in CASES.items():
    w, p, rho = weights(df, col); st = stats(w); n = len(df)
    boot = [stats(weights(df.iloc[rng.integers(0, n, n)], col)[0]) for _ in range(REPS_W)]
    row = dict(case=k, n=n, first=df.d.min(), last=df.d.max(), corr_with_ns=rho, w_ten=w[0], w_eq=w[1], w_usd=w[2], psi_ten=p[0], psi_eq=p[1], psi_usd=p[2], **st)
    for s in ("fig1", "dF"):
        l, u = ci([x[s] for x in boot]); row[f"{s}_lo"], row[f"{s}_hi"] = l, u
    rows.append(row)
    for kk, v in row.items():
        if kk not in ("case", "first", "last"):
            S.add(f"{k}_{kk}", v)
    S.add(f"{k}_first", pd.Timestamp(row['first']).strftime("%B %Y")); S.add(f"{k}_last", pd.Timestamp(row['last']).strftime("%B %Y"))
S.add("fig1_B", stats(b)["fig1"]); S.add("fig1_G", stats(g)["fig1"]); S.add("dB_F", stats(b)["dF"]); S.add("dG_F", stats(g)["dF"])
T = pd.DataFrame(rows); T.to_csv(RES / "28_information.csv", index=False, float_format="%.6g")
S.save()
print(T[["case", "n", "corr_with_ns", "w_ten", "w_eq", "w_usd", "fig1", "fig1_lo", "fig1_hi", "dF", "dF_lo", "dF_hi", "dB", "dG"]].round(3).to_string())
print("B fig1", round(stats(b)["fig1"], 3), "G fig1", round(stats(g)["fig1"], 3), "dB_F", round(stats(b)["dF"], 3), "dG_F", round(stats(g)["dF"], 3))
