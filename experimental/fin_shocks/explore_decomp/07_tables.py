"""Markdown tables for REPORT.md, written from results/ (no typed numbers).   python3 07_tables.py  -> results/tables.md"""
import numpy as np, pandas as pd
from pathlib import Path
RES = Path(__file__).resolve().parent / "results"
S = pd.read_csv(RES / "summary.csv"); F = pd.read_csv(RES / "fevd.csv"); B = pd.read_csv(RES / "boot_summary.csv")
SIM = pd.read_csv(RES / "sim_invertibility.csv"); NB = pd.read_csv(RES / "noteb_shares.csv")
STEP = {"nom": "nominal", "real": "real", "rstar": "r*-gap"}
def lab(step, fci): return f"{STEP[step]}{' + FCI' if str(fci) != '0' else ''}"
def md(df): return df.to_markdown(index=False) if hasattr(df, "to_markdown") else df.to_string(index=False)
def f3(x): return f"{x:.3f}"
def pct(x): return f"{100 * x:.1f}"
out = []

# T1 diagnostics
m = S[(S.L == 12) & (S.t2020 == "in") & (S.ident == "WE")]
rows = []
for _, r in m.iterrows():
    rows.append({"case": lab(r.step, r.fci), "data": f"{r.kind} {r.start[:4]}", "first-stage F": f"{r.F:.1f}", "R2 of z on u_t (%)": pct(r.r2_z_u),
                 "corr(recovered, z)": f"{r.corr_e_z:.2f}", "sd recovered (inv.)": f3(r.sd_e_post_inv), "sd z": f3(r.sd_z), "variance ratio": f"{r.var_ratio:.0f}",
                 "leads p": f"{r.p_leads:.2f}", "lags p": f"{r.p_lags:.2f}"})
out.append("### T1. Invertibility diagnostics (12 lags, 2020 in, window column)\n\n" + md(pd.DataFrame(rows)))

# T1b bootstrap of the diagnostics for the main data versions
bb = B[B.stat.isin(["r2", "corr"]) & (B.ident == "WE")]
rows = []
for (step, fci, kind), g in bb.groupby(["step", "fci", "kind"], sort=False):
    r2 = g[g.stat == "r2"].iloc[0]; c = g[g.stat == "corr"].iloc[0]
    rows.append({"case": lab(step, fci), "data": "avg 1973" if kind == "avg" else "eom 1990", "R2 (%), median [5, 95]": f"{pct(r2.p50)} [{pct(r2.p5)}, {pct(r2.p95)}]",
                 "corr, median [5, 95]": f"{c.p50:.2f} [{c.p5:.2f}, {c.p95:.2f}]"})
out.append("### T1b. Bootstrap distribution of the diagnostics (500 draws)\n\n" + md(pd.DataFrame(rows)))

# T2 simulation
q = SIM.groupby("kind")[["r2_z_u", "corr_e_z", "var_ratio", "fevd_u24_upper", "fevd_u24_lower"]].quantile([0.05, 0.5, 0.95]).unstack()
rows = []
for kind in ("avg", "eom"):
    d = S[(S.step == "rstar") & (S.fci == "rstar") & (S.kind == kind) & (S.start == "1996-01") & (S.L == 12) & (S.t2020 == "in") & (S.ident == "WE")].iloc[0]
    fu = F[(F.case == d.case) & (F.h == 24)]
    g = lambda s: f"{q.loc[kind, (s, 0.5)]:.3f} [{q.loc[kind, (s, 0.05)]:.3f}, {q.loc[kind, (s, 0.95)]:.3f}]"
    rows.append({"data": kind, "statistic": "R2 of z on u_t", "Note B as truth: median [5, 95]": g("r2_z_u"), "data 1996-2026": f3(d.r2_z_u)})
    rows.append({"data": kind, "statistic": "corr(recovered, z)", "Note B as truth: median [5, 95]": g("corr_e_z"), "data 1996-2026": f3(d.corr_e_z)})
    rows.append({"data": kind, "statistic": "variance ratio", "Note B as truth: median [5, 95]": g("var_ratio").replace(".000", ""), "data 1996-2026": f"{d.var_ratio:.1f}"})
    rows.append({"data": kind, "statistic": "u share at 24 m, upper", "Note B as truth: median [5, 95]": g("fevd_u24_upper"), "data 1996-2026": f3(float(fu[fu.bound == "post_upper"].u.iloc[0]))})
    rows.append({"data": kind, "statistic": "u share at 24 m, lower", "Note B as truth: median [5, 95]": g("fevd_u24_lower"), "data 1996-2026": f3(float(fu[fu.bound == "post_lower"].u.iloc[0]))})
out.append(f"### T2. Note B's model as the true process ({SIM.sim.nunique()} simulated samples, 1996-2026) against the data\n\n" + md(pd.DataFrame(rows)))

# T3 variance shares at 24 months
rows = []
for (kind, start) in (("avg", "1973-01"), ("eom", "1990-01")):
    for step in ("nom", "real", "rstar"):
        for fci in ("0", step):
            g = F[(F.L == 12) & (F.t2020 == "in") & (F.ident == "WE") & (F.h == 24) & (F.kind == kind) & (F.start == start) & (F.step == step) & (F.fci.astype(str) == fci)]
            p1 = F[(F.L == 12) & (F.t2020 == "in") & (F.ident == "P1") & (F.h == 24) & (F.kind == kind) & (F.start == start) & (F.step == step) & (F.fci.astype(str) == fci)]
            bs = B[(B.ident == "WE") & (B.kind == kind) & (B.step == step) & (B.fci.astype(str) == fci) & (B.stat == "fevd_u24")]
            nb = NB[(NB.step == step) & (NB.fci.astype(str) == fci) & (NB.start == "1996-01") & (NB.h == 24)]
            v = lambda b, c, G=g: pct(float(G[G.bound == b][c].iloc[0]))
            rows.append({"data": f"{kind} {start[:4]}", "case": lab(step, fci),
                         "u: lower (VAR)": v("post_lower", "u"), "u: lower (Note B model)": pct(float(nb.u.iloc[0])) if len(nb) and kind == "avg" else "",
                         "u: upper 1996-": v("post_upper", "u"), "u: upper full": v("full_upper", "u"),
                         "u: upper full, 90% band": f"[{pct(bs.p5.iloc[0])}, {pct(bs.p95.iloc[0])}]" if len(bs) else "", "u: upper full, P1": v("full_upper", "u", p1),
                         "pi: lower": v("post_lower", "pi"), "pi: upper full": v("full_upper", "pi"), "yield: lower": v("post_lower", "pol"), "yield: upper full": v("full_upper", "pol")})
out.append("### T3. Share of the 24-month forecast-error variance due to policy shocks, percent (12 lags, 2020 in)\n\n" + md(pd.DataFrame(rows)))

# T4 responses: the VAR with the window column against Note B
rows = []
for _, r in m.iterrows():
    rows.append({"case": lab(r.step, r.fci), "data": f"{r.kind} {r.start[:4]}", "u12 VAR": f"{r.var_u12:.2f}", "u12 Note B": f"{r.nb_u12:.2f}", "u24 VAR": f"{r.var_u24:.2f}",
                 "u24 Note B": f"{r.nb_u24:.2f}", "P24 VAR": f"{r.var_P24:.2f}", "P24 Note B": f"{r.nb_P24:.2f}", "yield h=1 VAR": f"{r.var_pol1:.2f}"})
out.append("### T4. Responses per +1 pp window surprise: the monthly VAR with the window column against Note B's model (same step; Note B from 1973 for avg 1973, else from 1996)\n\n" + md(pd.DataFrame(rows)))

# T5 sensitivity of the main case
mm = S[(S.step == "rstar") & (S.fci == "rstar") & (S.ident.isin(["WE", "P1", "WE2"]))]
rows = []
for _, r in mm.iterrows():
    fu = F[(F.case == r.case) & (F.h == 24) & (F.bound == "full_upper")]
    rows.append({"data": f"{r.kind} {r.start[:4]}", "lags": r.L, "2020": r.t2020, "column": r.ident, "R2 (%)": pct(r.r2_z_u), "corr": f"{r.corr_e_z:.2f}",
                 "variance ratio": f"{r.var_ratio:.0f}", "u share 24 m, upper (%)": pct(float(fu.u.iloc[0])) if r.ident != "WE2" else "n.a."})
out.append("### T5. r*-gap with FCI: all versions\n\n" + md(pd.DataFrame(rows)))

# T6 episodes
if (RES / "hd_episodes_rstar_avg1973.csv").exists():
    E = pd.read_csv(RES / "hd_episodes_rstar_avg1973.csv")
    rows = []
    for _, r in E.iterrows():
        def c(v, k):
            x = r.get(f"{v}_{k}")
            return "" if pd.isna(x) else f"{x:.2f} [{r[f'{v}_{k}lo']:.2f}, {r[f'{v}_{k}hi']:.2f}]"
        rows.append({"month": r.month, "u: all shocks": f"{r.u_all:.2f}", "u: Route 2": c("u", "r2"), "u: Route 1": c("u", "r1"),
                     "infl. 12m: all": f"{r.pi_all:.2f}", "infl.: Route 2": c("pi", "r2"), "infl.: Route 1": c("pi", "r1")})
    out.append("### T6. Historical decomposition at selected months, r*-gap with FCI (Route 2: VAR in monthly averages from 1973; Route 1: Note B's model from 1996 and the measured surprises; 90% bands)\n\n" + md(pd.DataFrame(rows)))
(RES / "tables.md").write_text("\n\n".join(out) + "\n"); print("\n\n".join(out))
