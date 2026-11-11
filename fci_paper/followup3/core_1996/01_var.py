"""(i) VAR Phi(12), 90% block-bootstrap interval, Granger p, for rows a, b (12 and 4 lags), c, d. Row e reuses a's VAR (same 1973+ VAR sample). Writes out/var.csv"""
import warnings; warnings.filterwarnings("ignore")
from common import *
from lib import var
from statsmodels.tsa.api import VAR
from multiprocessing import Pool
REPS = 500

def frame(u, m, start, dum_ranges):
    D = pd.DataFrame({"u": u, "M": m}).loc[start:"2026-09"].dropna()
    dums = {}
    for k in range(1, 13): dums[f"d2020_{k:02d}"] = (D.index == pd.Period(f"2020-{k:02d}", "M")).astype(float)
    for a, b in dum_ranges:
        for p in pd.period_range(a, b, freq="M"): dums[f"d{p}"] = (D.index == p).astype(float)
    dum = pd.DataFrame(dums, index=D.index); dum = dum.loc[:, dum.any()]
    D.index = D.index.to_timestamp(); dum.index = D.index
    return D, dum

def job(a):
    row, step, key, p = a
    R = ROWS[row]
    m = index(step, key, R.get("w2019", False))
    D, dum = frame(M.u_gap, m, R["var_start"], R["var_dum"])
    r = VAR(D, exog=dum if dum.shape[1] else None).fit(p)
    Phi, own_ = var.response(r)
    gc = r.test_causality("u", ["M"], kind="f")
    ph, _ = var.bootstrap(D, dum, p, 36, REPS)
    lo, hi = var.bands(ph, 0.90)
    return dict(row=row, step=step, series=key, lags=p, n=len(D), start=str(D.index[0].to_period("M")), phi6=Phi[6], phi12=Phi[12], lo90=lo[12], hi90=hi[12], phi24=Phi[24],
                lo90_24=var.bands(ph, 0.90)[0][24], hi90_24=var.bands(ph, 0.90)[1][24], granger_F=gc.test_statistic, granger_p=gc.pvalue, boot_share_pos=float((ph[:, 12] > 0).mean()))

if __name__ == "__main__":
    jobs = []
    for row, R in ROWS.items():
        if row == "e": continue
        for p in R["lags"]:
            for step in STEPS:
                for key, _ in SERIES:
                    if R.get("w2019") and key != "market": continue
                    jobs.append((row, step, key, p))
    with Pool(4) as pl: res = pl.map(job, jobs)
    T = pd.DataFrame(res); T.to_csv(OUT / "var.csv", index=False)
    print(T[T.series == "market"][["row", "step", "lags", "n", "phi12", "lo90", "hi90", "granger_p"]].round(3).to_string())
