"""Route 2 historical decomposition at selected months (r*-gap with FCI and the other cases): exact-position point estimates (B2) for the spliced shocks, of which
announcement days, and the measured surprises; 12-month core inflation from the monthly contributions.   python3 B4_episodes.py -> results_route2/episodes.csv"""
import pandas as pd
from pathlib import Path
R2 = Path(__file__).resolve().parent / "results_route2"
MONTHS = ["1975-06", "1979-12", "1980-12", "1982-06", "1982-12", "1984-06", "1986-12", "1989-06", "1992-06", "1995-06", "1998-12", "2001-12", "2003-06",
          "2008-12", "2009-10", "2013-12", "2016-12", "2019-12", "2021-06", "2022-12", "2023-12", "2024-12", "2026-09"]
rows = []
for step, fci in (("rstar", "rstar"), ("nom", "nom"), ("real", "real"), ("rstar", "0"), ("nom", "0")):
    h = pd.read_csv(R2 / f"hd_{step}_{fci}.csv")
    for v in ("u", "pi", "pol", "idx"):
        g = h[h["var"] == v].set_index("month")
        if g.empty: continue
        if v == "pi": g = g.drop(columns="var").rolling(12).mean()
        for m in MONTHS:
            rows.append(dict(step=step, fci=fci, var="pi12" if v == "pi" else v, month=m, all_shocks=g.loc[m, "all_shocks_var"], route2=g.loc[m, "spliced"],
                             route2_unscaled=g.loc[m, "spliced_raw"], announcement_days=g.loc[m, "daily_ann"], measured=g.loc[m, "measured"]))
E = pd.DataFrame(rows); E.to_csv(R2 / "episodes.csv", index=False, float_format="%.3f")
print(E[(E.step == "rstar") & (E.fci == "rstar")].pivot_table(index="month", columns="var", values=["all_shocks", "route2", "measured"]).round(2).to_string())
