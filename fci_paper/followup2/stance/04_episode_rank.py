"""How unusual are the episode differences? Rolling means of (index - FFG), Market, r* LW, 1976-2026 (months of the same length), rank of the episodes. Descriptive."""
from common import *
x = index("rstar", "market"); f = ffg("rstar"); x = x.loc["1976-01":"2026-09"]; f = f.loc[x.index]
d = (x - x.mean()) - (f - f.mean()); sd_all = d.std(); rows = []
for en, (a, b) in {"conundrum": ("2004-06", "2006-06"), "tightening": ("2022-03", "2024-12")}.items():
    n = len(d.loc[a:b]); rm = d.rolling(n).mean().dropna(); v = d.loc[a:b].mean()
    rows.append(dict(episode=en, n=n, mean_diff=v, sd_monthly_diff=sd_all, pct_rank=float((rm < v).mean()), min_rolling=rm.min(), median_rolling=rm.median(), p05=rm.quantile(.05), p95=rm.quantile(.95)))
R = pd.DataFrame(rows); R.to_csv(OUT / "episode_rank.csv", index=False); print(R.round(2).to_string())
