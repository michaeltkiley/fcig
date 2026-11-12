"""Correlation between the funds-rate gap and each index, by period (levels and 12-month changes), every step. Descriptive."""
from common import *
P = {"full 1976-2026": ("1976-03", "2026-09"), "pre-2009 1976-2008": ("1976-03", "2008-12"), "2004-06": ("2004-06", "2006-06"), "zlb 2009-15": ("2009-01", "2015-12"), "post 2022-26": ("2022-04", "2026-09")}
rows = []
for s in STEPS:
    f = ffg(s)
    for k in INDEXES:
        x = index(s, k)
        for pn, (a, b) in P.items():
            r = {"step": s, "index": k, "period": pn}
            for form, (ff, xx) in {"level": (f, x), "flow": (f.diff(12), x.diff(12))}.items():
                z = pd.concat([ff, xx], axis=1).loc[a:b].dropna(); r[f"corr_{form}"] = z.corr().iloc[0, 1]; r["n"] = len(z)
            r["sd_ffg"] = f.loc[a:b].std(); rows.append(r)
pd.DataFrame(rows).to_csv(OUT / "corr.csv", index=False)
print(pd.DataFrame(rows).query("step=='rstar'").round(2).to_string())
