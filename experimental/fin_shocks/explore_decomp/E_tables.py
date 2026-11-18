"""Route 2 tables (markdown) from results_route2/.   python3 E_tables.py -> results_route2/tables_route2.md"""
import numpy as np, pandas as pd
from pathlib import Path
R2 = Path(__file__).resolve().parent / "results_route2"
STEP = {"nom": "nominal", "real": "real", "rstar": "r*-gap"}
def lab(s, f): return f"{STEP[s]}{' + FCI' if str(f) != '0' else ''}"
out = []

D = pd.read_csv(R2 / "daily_summary.csv"); D = D[D.est == 1996]
out.append("### B1. Policy shocks recovered from daily innovations, 1990-2026 (Note B's daily block; s_d = b'Omega^-1 eps_d / b'Omega^-1 b)\n\n" + pd.DataFrame([{
    "case": lab(r.form, r.fci), "first day": r.first, "days": r.n_days, "window loading b_F": "" if pd.isna(r.b_F) else f"{r.b_F:.2f}",
    "ordinary-day FCI loading": "" if pd.isna(r.ordinary_loading) else f"{r.ordinary_loading:.2f}", "corr of innovations": "" if pd.isna(r.corr_eps) else f"{r.corr_eps:.2f}",
    "sd shock, all days": f"{r.sd_s_all:.3f}", "sd, announcement days": f"{r.sd_s_ann:.3f}", "sd, other days": f"{r.sd_s_other:.3f}", "sd measured surprise": f"{r.sd_ns:.3f}",
    "corr with measured, announcement days": f"{r.corr_s_ns_ann:.2f}", "slope on measured": f"{r.slope_s_on_ns_ann:.2f}"} for _, r in D.iterrows()]).to_markdown(index=False))

O = pd.read_csv(R2 / "overlap.csv")
out.append("### B2. Monthly-VAR shocks against the month's sum of daily shocks, May 1990 - September 2026 (the splice)\n\n" + pd.DataFrame([{
    "case": lab(r.step, r.fci), "corr, same month": f"{r.corr_same_month:.2f}", "R2 on same and next month": f"{r.r2_same_and_next:.2f}", "sd monthly-VAR shock": f"{r.sd_monthly_var_shock:.2f}",
    "sd daily sum": f"{r.sd_daily_sum:.2f}", "scale used before 1990 (sd ratio)": f"{r.scale:.2f}", "sd monthly-VAR shock 1974-89 (unscaled)": f"{r.sd_monthly_var_shock_pre1990:.2f}"} for _, r in O.iterrows()]).to_markdown(index=False))

S = pd.read_csv(R2 / "shares.csv"); B = pd.read_csv(R2 / "bands_shares.csv") if (R2 / "bands_shares.csv").exists() else None
SRC = [("1974-1989", "spliced", "monthly-recovered (scaled)"), ("1974-1989", "spliced_raw", "monthly-recovered (unscaled)"), ("1990-2026", "daily_all", "daily-recovered, all days"),
       ("1990-2026", "daily_other", "  non-announcement days"), ("1990-2026", "daily_ann", "  announcement days"), ("1990-2026", "measured", "measured surprises (Route 1)"),
       ("1996-2026", "daily_all", "daily-recovered, all days"), ("1996-2026", "measured", "measured surprises (Route 1)")]
for step, fci in (("rstar", "rstar"), ("nom", "nom"), ("real", "real"), ("rstar", "0"), ("nom", "0"), ("real", "0")):
    rows = []
    for era, src, name in SRC:
        g = S[(S.step == step) & (S.fci.astype(str) == fci) & (S.era == era) & (S.source == src) & (S.h == 24)]
        if g.empty: continue
        r = {"period": era, "shocks": name}
        for v in ("u", "pi", "pol", "idx"):
            if v not in g or pd.isna(g[v].iloc[0]): continue
            cellv = f"{100 * g[v].iloc[0]:.1f}"
            if B is not None:
                b = B[(B.step == step) & (B.fci.astype(str) == fci) & (B.era == era) & (B.source == src) & (B.h == 24) & (B["var"] == v)]
                if len(b): cellv += f" [{100 * b.p5.iloc[0]:.1f}, {100 * b.p95.iloc[0]:.1f}]"
            r[{"u": "unemployment gap", "pi": "core inflation", "pol": "2-year yield", "idx": "FCI"}[v]] = cellv
        rows.append(r)
    out.append(f"### B3 ({lab(step, fci)}). Share of the 24-month forecast-error variance, percent (Note B's model from 1973; exact day-of-month responses, 120 months; "
               "90% band from Note B's bootstrap with month-aggregated shocks and 36-month responses)\n\n" + pd.DataFrame(rows).to_markdown(index=False))

rows = []
for h in (12, 24, 36):
    for era, src, name in SRC:
        g = S[(S.step == "rstar") & (S.fci == "rstar") & (S.era == era) & (S.source == src) & (S.h == h)]
        if g.empty: continue
        rows.append({"h": h, "period": era, "shocks": name, **{k: f"{100 * g[v].iloc[0]:.1f}" for v, k in (("u", "unemployment gap"), ("pi", "core inflation"), ("pol", "2-year yield"), ("idx", "FCI"))}})
out.append("### B3b. r*-gap with FCI: shares at 12, 24 and 36 months, percent\n\n" + pd.DataFrame(rows).to_markdown(index=False))

if (R2 / "shares_model1996.csv").exists():
    S6 = pd.read_csv(R2 / "shares_model1996.csv"); rows = []
    for era, src, name in SRC:
        g = S6[(S6.step == "rstar") & (S6.fci == "rstar") & (S6.era == era) & (S6.source == src) & (S6.h == 24)]
        if g.empty: continue
        rows.append({"period": era, "shocks": name, **{k: f"{100 * g[v].iloc[0]:.1f}" for v, k in (("u", "unemployment gap"), ("pi", "core inflation"), ("pol", "2-year yield"), ("idx", "FCI"))}})
    out.append("### B3c. r*-gap with FCI, responses from Note B's baseline model (monthly equations from 1996): shares at 24 months, percent\n\n" + pd.DataFrame(rows).to_markdown(index=False))

E = pd.read_csv(R2 / "episodes.csv"); e = E[(E.step == "rstar") & (E.fci == "rstar")]
rows = []
for m, g in e.groupby("month", sort=False):
    r = {"month": m}
    for v, k in (("u", "u"), ("pi12", "core infl. 12m"), ("pol", "2-yr yield"), ("idx", "FCI")):
        x = g[g["var"] == v].iloc[0]; r[f"{k}: all shocks"] = f"{x.all_shocks:.2f}"; r[f"{k}: Route 2"] = f"{x.route2:.2f}"; r[f"{k}: measured"] = f"{x.measured:.2f}"
    rows.append(r)
out.append("### B4. Historical decomposition at selected months, r*-gap with FCI (Note B's model from 1973; Route 2 = policy-direction shocks, daily from May 1990, monthly scaled before; "
           "measured = window surprises; all shocks = the data's deviation from the monthly VAR's deterministic path)\n\n" + pd.DataFrame(rows).to_markdown(index=False))
(R2 / "tables_route2.md").write_text("\n\n".join(out) + "\n"); print("\n\n".join(out)[:3000])
