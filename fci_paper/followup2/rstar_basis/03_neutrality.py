"""C: implied index level at an unemployment gap of zero. Level regression M_t = a + b u_t + e_t by subperiod; a = the index at u = 0.
Series: market (nominal, real, r* LW, r* Kiley), GS and FRB/US at three steps. Periods: P1 1973-89, P2 1990-2007, P3 2009-19 (headline); also Z 2009-15 (zero bound), L 2016-19, P5 2021-26 (u_gap fall; no Covid months, 2022-01..2026-09).
Comparisons (pre-specified): P2 vs P3 (headline); P1 vs P2; P2 vs Z; P2 vs L. Moving-block (24 months) pairs bootstrap within each period, 1000 draws; HAC(24) shown too.
Difference scaled by the full-sample sd of the index. A series passes if the 90% interval of a(P3) - a(P2) includes zero. Count: 11 series x 4 comparisons = 44 intervals."""
from common import *
rng = np.random.default_rng(20261111)
PER = {"P1_1973-89": ("1973-01", "1989-12"), "P2_1990-2007": ("1990-01", "2007-12"), "P3_2009-19": ("2009-01", "2019-12"), "Z_2009-15": ("2009-01", "2015-12"), "L_2016-19": ("2016-01", "2019-12"), "P5_2022-26": ("2022-01", "2026-09")}
SER = {f"{k[0]}|{k[1]}": v for k, v in all_series().items()}
SER["Market|rstar_kiley"] = index("rstar_kiley", "market")
def fit(m, a, z):
    d = pd.DataFrame({"M": m, "u": U}).loc[a:z].dropna(); X = np.c_[np.ones(len(d)), d.u]; b, e = ols(d.M.values, X); V = hac(X, e, 24)
    return d, b, np.sqrt(V[0, 0])
rows, draws = [], {}
for k, m in SER.items():
    sd = m.loc["1973-01":"2026-09"].std()
    for p, (a, z) in PER.items():
        d, b, se = fit(m, a, z); bs = []
        for _ in range(1000):
            dd = d.iloc[blocks(len(d), 24, rng)]; X = np.c_[np.ones(len(dd)), dd.u]; bs.append(ols(dd.M.values, X)[0])
        bs = np.array(bs); draws[(k, p)] = bs
        rows.append({"series": k, "period": p, "n": len(d), "a": b[0], "se_hac": se, "a_lo90": np.percentile(bs[:, 0], 5), "a_hi90": np.percentile(bs[:, 0], 95), "slope_u": b[1], "mean_u": d.u.mean(), "sd_index_full": sd})
A = pd.DataFrame(rows); A.to_csv(OUT / "neutrality_levels.csv", index=False)
comp = []
for k in SER:
    g = lambda p: A[(A.series == k) & (A.period == p)].iloc[0]
    for p1, p2 in (("P2_1990-2007", "P3_2009-19"), ("P1_1973-89", "P2_1990-2007"), ("P2_1990-2007", "Z_2009-15"), ("P2_1990-2007", "L_2016-19")):
        diff = g(p2).a - g(p1).a; dd = draws[(k, p2)][:, 0] - draws[(k, p1)][:, 0]; sd = g(p1).sd_index_full
        zh = diff / np.sqrt(g(p1).se_hac ** 2 + g(p2).se_hac ** 2)
        comp.append({"series": k, "from": p1, "to": p2, "diff": diff, "lo90": np.percentile(dd, 5), "hi90": np.percentile(dd, 95), "diff_in_sd": diff / sd, "z_hac": zh, "excludes0": bool(np.percentile(dd, 5) > 0 or np.percentile(dd, 95) < 0)})
C = pd.DataFrame(comp); C.to_csv(OUT / "neutrality_diffs.csv", index=False)
