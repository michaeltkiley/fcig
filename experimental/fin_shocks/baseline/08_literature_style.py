"""Literature-style estimators on the package's own data (Section 3.3 comparison): recursive Cholesky VARs (2-year yield and funds rate, several samples),
and the monthly proxy VAR; all per +1 pp on the policy variable, 12 lags (specification in lib/litstyle.py).
   python3 08_literature_style.py [--draws 200]
Output: results/lit_style.csv (case, var, h, point, lo, hi) and results/lit_style_info.csv (sample, observations, first-stage F)."""
import os, argparse
os.environ.setdefault("OMP_NUM_THREADS", "1")
import pandas as pd
from lib import litstyle as LS
from lib.paths import RESULTS

ap = argparse.ArgumentParser(); ap.add_argument("--draws", type=int, default=200); a = ap.parse_args()
CHOL = [("chol_2y_1996", "2y", "1996-01", "2026-09", False, "Cholesky, 2-year yield, 1996-2026"),
        ("chol_2y_1984", "2y", "1984-01", "2026-09", False, "Cholesky, 2-year yield, 1984-2026"),
        ("chol_ffr_1984_2007", "ffr", "1984-01", "2007-12", False, "Cholesky, funds rate, 1984-2007"),
        ("chol_2y_1996_com", "2y", "1996-01", "2026-09", True, "Cholesky with commodity prices, 2-year yield, 1996-2026"),
        ("chol_ffr_1984_2007_com", "ffr", "1984-01", "2007-12", True, "Cholesky with commodity prices, funds rate, 1984-2007")]
rows, info = [], []
def add(case, out, label, **kw):
    for v, (pt, lo, hi) in out.items():
        for h in range(len(pt)): rows.append(dict(case=case, var=v, h=h, point=pt[h], lo=lo[h], hi=hi[h]))
    info.append(dict(case=case, label=label, **kw))
for case, kind, s, e, com, label in CHOL:
    out, n = LS.paths_chol(LS.frame(kind, s, e, com), s, a.draws, case); add(case, out, label, nobs=n, F=float("nan")); print(case, n, flush=True)
out, F, n = LS.paths_p1(); add("proxy_2y_1996", out, "Monthly proxy VAR (NS instrument), 2-year yield, no FCI, 1996-2026", nobs=n, F=F); print("proxy", F, n)
pd.DataFrame(rows).to_csv(RESULTS / "lit_style.csv", index=False, float_format="%.4f"); pd.DataFrame(info).to_csv(RESULTS / "lit_style_info.csv", index=False, float_format="%.3f")
