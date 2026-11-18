"""Note B's model, real case, 12 lags, from 1996 and from 1973, with the Chicago Fed NFCI added as a third monthly variable (author, 18 Nov 2026).
NFCI: weekly (Friday) index from January 1971 (FRED, copied from fci_note/replication/data/NFCI.csv), averaged by month. It enters as the excess bond premium does in the package's
robustness case R3a: its own monthly equation, lags in every monthly equation, this and last month's value in the daily block's regressors; zero response on impact.
Cases: real 2-year with the real FCI (the real baseline) and without the FCI, each without and with the NFCI. March-December 2020 dropped, no trend. Point estimates (no bootstrap).
Writes nfci_var.md, nfci_var.csv."""
import os, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; BASE = HERE.parent / "baseline"; sys.path.insert(0, str(BASE)); os.chdir(BASE)
import numpy as np, pandas as pd
from lib import model as M
n = pd.read_csv(HERE / "data_extra" / "NFCI.csv", parse_dates=["observation_date"]).set_index("observation_date").NFCI
M.MAC["nfci"] = n.groupby(n.index.to_period("M")).mean().reindex(M.MAC.index)
HS = (6, 12, 18, 24, 36); rows = []
for start in ("1996-01", "1973-01"):
    for fci in ("real", 0):
        for macro in ("u,pi", "u,pi,nfci"):
            est = next(M.estimate("real", fci, macro, start, None, "out", "none", 2, lags=(12,)))
            for j, v in enumerate(est["names"]):
                rows.append(dict(start=start[:4], fci="with FCI" if fci else "no FCI", macro=macro, nobs=est["nobs"], var=v, **{f"r{h}": est["s0"][h, j] for h in HS}))
R = pd.DataFrame(rows); R.to_csv(HERE / "nfci_var.csv", index=False, float_format="%.4f")
chk = pd.read_csv(BASE / "results" / "real_real_upi_1996-01_all_out.csv"); chk = chk[(chk.lags == 12) & (chk["var"] == "u")].r12.iloc[0]
md = ["# Real case with the NFCI added (Note B's model, 12 lags, point estimates)", "",
      f"Per +1 pp on the 2-year in the window: u = unemployment gap (pp), P = price level (percent), NFCI (index units). Check: real case with the FCI from 1996 without the NFCI, u at 12 months = "
      f"{R[(R.start == '1996') & (R.fci == 'with FCI') & (R.macro == 'u,pi') & (R['var'] == 'u')].r12.iloc[0]:+.3f} (package: {chk:+.3f}).", ""]
for fc in ("with FCI", "no FCI"):
    md += [f"## {fc}", "", "| start | monthly variables | nobs | " + " | ".join(f"u {h}m" for h in HS) + " | " + " | ".join(f"P {h}m" for h in HS) + " | NFCI 6m | NFCI 12m | NFCI 24m |", "|---|---|---|" + "---|" * 13]
    for (s, mc), g in R[R.fci == fc].groupby(["start", "macro"], sort=False):
        q = g.set_index("var"); u, p = q.loc["u"], q.loc["P"]; nf = q.loc["nfci"] if "nfci" in q.index else None
        md.append(f"| {s} | {mc} | {u.nobs} | " + " | ".join(f"{u[f'r{h}']:+.2f}" for h in HS) + " | " + " | ".join(f"{p[f'r{h}']:+.2f}" for h in HS) + " | " +
                  (" | ".join(f"{nf[f'r{h}']:+.2f}" for h in (6, 12, 24)) if nf is not None else "- | - | -") + " |")
    md.append("")
(HERE / "nfci_var.md").write_text("\n".join(md)); print("\n".join(md))
