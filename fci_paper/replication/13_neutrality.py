"""Step 13. Does the r* basis make the index mean the same thing across regimes? (a) The neutrality shift: the index level at a zero unemployment gap, 2009-19 minus 1990-2007,
by basis (nominal, real, r* Laubach-Williams) for the market, GS and FRB/US indexes, and the r* (Kiley) market index. (b) The unit restriction on r*: the coefficient on r* implied by the
construction and the test of freeing it.

PRE-SPECIFIED DESIGN (ported unchanged from followup2/rstar_basis/02_unit_restriction.py and 03_neutrality.py)
 (a) Level regression M_t = a + b u_t + e_t by period (a = the index at u = 0). Periods: P1 1973-89, P2 1990-2007, P3 2009-19 (headline), Z 2009-15 (zero bound), L 2016-19, P5 2022-26.
     Moving-block (24 months) pairs bootstrap within each period (REPS draws); HAC(24) shown too. Difference scaled by the full-sample sd of the index. Headline comparison P3 - P2;
     also P1 - P2 vs P2, P2 vs Z, P2 vs L. 10 series x 4 comparisons = 40 intervals; descriptive (shared data; no adjustment). A series is stable if the 90% interval of a(P3) - a(P2) includes zero.
 (b) With weights w10 (10y), wE (equities), wD (dollar): M_rstar = M_real-form + c r*, c = -w10 + wE (100/EPbar) (EPbar = mean earnings yield 1973-2026), checked numerically against lib/cases.py.
     Outcome u(t+12)-u(t), controls u and du12, HAC(18), Covid rule, origins 1976-03..2025-09. Regress on M_rstar and, freely, r* (R) or r* and 10-year expected inflation (N):
     rho = 1 + delta/(c b) = free coefficient on r* in units of the restriction (1 = restriction, 0 = no adjustment). Wald p for rho = 1 and rho = 0; moving-block (24-month) pairs bootstrap CI
     (REPS draws). 8 specifications: level or 12-month flow x r* (LW, Kiley) x extra (R, N). The test has little power because r* moves little over 12 months; the paper states it as untestable here.
Writes results/13_neutrality_levels.csv, 13_neutrality_diffs.csv, 13_unit_restriction.csv, scalars_13_neutrality.csv."""
import numpy as np, pandas as pd
from lib import cases, indexes as I
from lib.config import RES, REPS, SEED
from lib.report import Scalars
from lib.purge_util import read_res, ols, hac, wald, blocks, covid

from lib.purge_util import single_thread_blas
single_thread_blas()
S = Scalars("13_neutrality")
DM = read_res("data_monthly.csv"); U = DM.u_gap
W = pd.read_csv(RES / "market_weights.csv", index_col=0).weight
ix = lambda step, col: read_res(f"indexes_{step}.csv")[col]
PER = {"P1_1973-89": ("1973-01", "1989-12"), "P2_1990-2007": ("1990-01", "2007-12"), "P3_2009-19": ("2009-01", "2019-12"), "Z_2009-15": ("2009-01", "2015-12"),
       "L_2016-19": ("2016-01", "2019-12"), "P5_2022-26": ("2022-01", "2026-09")}
SER = {}
for fam, col in (("Market", "market"), ("GS", "gs"), ("FRBUS", "frbus")):
    for s in ("nominal", "real", "rstar"):
        SER[f"{fam}|{s}"] = ix(s, col)
SER["Market|rstar_kiley"] = ix("rstar_kiley", "market")

# ---------------- (a) neutrality
rng = np.random.default_rng(SEED)


def fit(m, a, z):
    d = pd.DataFrame({"M": m, "u": U}).loc[a:z].dropna(); X = np.c_[np.ones(len(d)), d.u]; b, e = ols(d.M.values, X)
    return d, b, np.sqrt(hac(X, e, 24)[0, 0])


rows, draws = [], {}
for k, m in SER.items():
    sd = m.loc["1973-01":"2026-09"].std()
    for p, (a, z) in PER.items():
        d, b, se = fit(m, a, z); bs = []
        for _ in range(REPS):
            dd = d.iloc[blocks(len(d), 24, rng)]; bs.append(ols(dd.M.values, np.c_[np.ones(len(dd)), dd.u])[0])
        bs = np.array(bs); draws[(k, p)] = bs
        rows.append({"series": k, "period": p, "n": len(d), "a": b[0], "se_hac": se, "a_lo90": np.percentile(bs[:, 0], 5), "a_hi90": np.percentile(bs[:, 0], 95),
                     "slope_u": b[1], "mean_u": d.u.mean(), "sd_index_full": sd})
A = pd.DataFrame(rows); A.to_csv(RES / "13_neutrality_levels.csv", index=False)
comp = []
for k in SER:
    g = lambda p: A[(A.series == k) & (A.period == p)].iloc[0]
    for p1, p2 in (("P2_1990-2007", "P3_2009-19"), ("P1_1973-89", "P2_1990-2007"), ("P2_1990-2007", "Z_2009-15"), ("P2_1990-2007", "L_2016-19")):
        diff = g(p2).a - g(p1).a; dd = draws[(k, p2)][:, 0] - draws[(k, p1)][:, 0]; sd = g(p1).sd_index_full
        zh = diff / np.sqrt(g(p1).se_hac ** 2 + g(p2).se_hac ** 2)
        comp.append({"series": k, "from": p1, "to": p2, "diff": diff, "lo90": np.percentile(dd, 5), "hi90": np.percentile(dd, 95), "diff_in_sd": diff / sd, "z_hac": zh,
                     "excludes0": bool(np.percentile(dd, 5) > 0 or np.percentile(dd, 95) < 0)})
C = pd.DataFrame(comp); C.to_csv(RES / "13_neutrality_diffs.csv", index=False)
for _, r in C.iterrows():
    f, t = r["from"][:2], r["to"][:2]
    tag = f"{r.series.replace('|', '_').lower()}_{f.lower()}_{t.lower()}"
    for q in ("diff", "lo90", "hi90", "diff_in_sd"):
        S.add(f"neut_{q}_{tag}", r[q])
h = C[(C["from"] == "P2_1990-2007") & (C["to"] == "P3_2009-19")]
S.add("neut_n_series", len(h)); S.add("neut_n_p3p2_excl_zero", int(h.excludes0.sum()))
S.add("neut_n_p3p2_positive_rstar_lw", int(((h["diff"] > 0) & h.series.str.endswith("|rstar")).sum()))
S.add("neut_n_p3p2_negative_nominal_real", int(((h["diff"] < 0) & h.series.str.endswith(("|nominal", "|real"))).sum()))
S.add("neut_n_obs_p2", int(A[(A.series == "Market|rstar") & (A.period == "P2_1990-2007")].n.iloc[0]))
S.add("neut_n_obs_p3", int(A[(A.series == "Market|rstar") & (A.period == "P3_2009-19")].n.iloc[0]))

# ---------------- (b) unit restriction
rng = np.random.default_rng(SEED)
EP = 100 / DM.cape; EPbar = EP.loc["1973-01":"2026-09"].mean()
c = -W["y10"] + W["equities"] * 100 / EPbar
for rs in ("rstar LW", "rstar Kiley"):                         # numerical check of c against lib/cases.py and lib/indexes.py
    base = DM.loc["1973-01":"2026-09"].copy(); dr = pd.Series(np.arange(len(base)) / 100.0, index=base.index)
    X2 = base.copy(); X2[rs] = X2[rs] + dr
    m1 = I.market(cases.inputs(base, "rstar", rs), W.values)[0]; m2 = I.market(cases.inputs(X2, "rstar", rs), W.values)[0]
    k = float(((m2 - m1) * (dr - dr.mean())).sum() / ((dr - dr.mean()) ** 2).sum()); assert abs(k - c) < 1e-6, (k, c)
S.add("unit_c", c); S.add("unit_w10", W["y10"]); S.add("unit_wE", W["equities"]); S.add("unit_EPbar", EPbar)
M, MK = ix("rstar", "market"), ix("rstar_kiley", "market")
rows = []
for rname, col, Mx in (("LW", "rstar LW", M), ("Kiley", "rstar Kiley", MK)):
    for kind in ("level", "flow"):
        for extra in ("R", "N"):
            f = (lambda s: s) if kind == "level" else (lambda s: s - s.shift(12))
            Dd = pd.DataFrame({"y": U.shift(-12) - U, "u": U, "du12": U - U.shift(12), "M": f(Mx), "r": f(DM[col]), "e": f(DM.einf_10y)}).loc["1976-03":"2025-09"]
            Dd = Dd[[not any(covid(t + k) for k in range(-12, 13)) for t in Dd.index]].dropna()
            cols = ["u", "du12", "M", "r"] + (["e"] if extra == "N" else [])
            est = lambda d: (ols(d.y.values, np.c_[np.ones(len(d)), d[cols].values]), np.c_[np.ones(len(d)), d[cols].values])
            (b, e_), X = est(Dd); V = hac(X, e_, 18)
            iM, ir = 1 + cols.index("M"), 1 + cols.index("r")
            Rr = np.zeros((1, len(b))); Rr[0, ir] = 1; _, p1 = wald(b, V, Rr)
            R0 = Rr.copy(); R0[0, iM] = c; _, p0 = wald(b, V, R0)
            row = {"rstar": rname, "kind": kind, "extra": extra, "n": len(Dd), "first": str(Dd.index[0]), "last": str(Dd.index[-1]), "b_M": b[iM], "se_M": np.sqrt(V[iM, iM]),
                   "delta_r": b[ir], "se_delta": np.sqrt(V[ir, ir]), "c_b": c * b[iM], "rho": 1 + b[ir] / (c * b[iM]), "p_rho1": p1, "p_rho0": p0, "sd_r": Dd.r.std()}
            if extra == "N":
                ie = 1 + cols.index("e"); row.update(delta_e=b[ie], se_e=np.sqrt(V[ie, ie]))
                Rj = np.zeros((2, len(b))); Rj[0, ir] = 1; Rj[1, ie] = 1; row["W_joint"], row["p_joint"] = wald(b, V, Rj)
            rh = []
            for _ in range(REPS):
                (bb, _e), _X = est(Dd.iloc[blocks(len(Dd), 24, rng)]); rh.append(1 + bb[ir] / (c * bb[iM]))
            rh = np.array(rh); row["rho_lo90"], row["rho_hi90"] = np.percentile(rh, [5, 95]); row["rho_boot_med"] = np.median(rh)
            rows.append(row)
            tag = f"{rname.lower()}_{kind}_{extra.lower()}"
            for q in ("rho", "rho_lo90", "rho_hi90", "p_rho1", "p_rho0", "sd_r"):
                S.add(f"unit_{q}_{tag}", row[q])
            if extra == "N":
                S.add(f"unit_p_joint_{tag}", row["p_joint"])
T = pd.DataFrame(rows); T.to_csv(RES / "13_unit_restriction.csv", index=False)
S.add("unit_n_specs", len(T)); S.add("unit_n_rho1_rejected_10pct", int((T.p_rho1 < 0.10).sum())); S.add("unit_n_rho0_rejected_10pct", int((T.p_rho0 < 0.10).sum()))
S.save()
