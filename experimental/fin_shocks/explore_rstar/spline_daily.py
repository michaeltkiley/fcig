"""Real version with the FCI, cubic spline trend, from 1996 and from 1973 (author, 18 Nov 2026): the spline in the monthly equations only, or in the monthly and the daily equations.
Monthly equations (u, pi): the package's natural cubic spline with its first knot at the first estimation month (from 1996: 1996-01, 2001-03, 2007-12, 2020-02, 2026-09;
from 1973: 1974-01, 1980-01, 1981-07, 1990-07, 2001-03, 2007-12, 2020-02, 2026-09; the corrected knots of real_trends.py, 'spl74').
Daily equations (2-year, FCI): the daily block is estimated on 1996-2026 in both baselines, so its spline uses the knots of that sample (1996-01, 2001-03, 2007-12, 2020-02, 2026-09),
evaluated at each day. It enters by Frisch-Waugh: the regressors (except the constant) and the outcomes of the daily block are residualized on [1, spline] before estimation, which gives
exactly the slope coefficients of the regression with the spline; the responses depend only on the slopes. The residualization is done once on the full daily sample (the bootstrap redraws
the residualized rows). 12 lags, March-December 2020 dropped, 500 draws. Writes results/real_<case>.csv and spline_daily.md."""
import os, sys, time
os.environ.setdefault("OMP_NUM_THREADS", "1"); os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
from pathlib import Path
HERE = Path(__file__).resolve().parent; BASE = HERE.parent / "baseline"
exec(open(HERE / "real_trends.py").read().split("HS = (6, 12")[0])            # the model with trend option spl74 (corrected first knot)
RES = HERE / "results"; RES.mkdir(exist_ok=True)
DKN = [M._dec(pd.Period(k, "M")) for k in ("1996-01", "2001-03", "2007-12", "2020-02", "2026-09")]
def daily_spline(dates):
    t = np.array([(d.year + (d.dayofyear - 0.5) / 365.25 - 2010) / 10 for d in pd.DatetimeIndex(dates)]); kn = DKN; K = len(kn)
    dd = lambda k: (np.maximum(t - kn[k], 0) ** 3 - np.maximum(t - kn[-1], 0) ** 3) / (kn[-1] - kn[k])
    return np.c_[t, *[dd(k) - dd(K - 2) for k in range(K - 2)]]
_har = M.har_rows; DAILY_TREND = {"on": False}
def har_rows(form, fci, mvars, end, t2020, months=False, dates=False):
    X, Y, mo, dt = _har(form, fci, mvars, end, t2020, months=True, dates=True)
    if DAILY_TREND["on"]:
        Z = np.c_[np.ones(len(dt)), daily_spline(dt)]; Pz = lambda A: A - Z @ np.linalg.lstsq(Z, A, rcond=None)[0]
        X = np.c_[X[:, :1], Pz(X[:, 1:])]; Y = Pz(Y)
    out = (X, Y, mo) if months else (X, Y)
    return out + (dt,) if dates else out
M.har_rows = har_rows
CASES = [("1996-01", "monthly"), ("1996-01", "monthly+daily"), ("1973-01", "monthly"), ("1973-01", "monthly+daily")]
def fname(c): return RES / f"real_splineD_{c[0]}_{'md' if c[1] == 'monthly+daily' else 'm'}.csv"
def work(c):
    start, where = c; t0 = time.time(); DAILY_TREND["on"] = where == "monthly+daily"; tr = "spl74" if where == "monthly" else "spl74d"
    if tr == "spl74d": M.macro_data.__globals__  # same monthly spline; the distinct name only changes the bootstrap seed tag
    sp = dict(form="real", fci="real", macro="u,pi", start=start, end="", t2020="out", trend=where, shock="ns")
    est = next(M.estimate("real", "real", "u,pi", start, None, "out", "spl74", 500, lags=(12,)))
    pd.DataFrame(M.summary_rows(sp, est)).to_csv(fname(c), index=False, float_format="%.4f"); return f"{c} {time.time() - t0:.0f}s"
if __name__ == "__main__":
    jobs = [c for c in CASES if not fname(c).exists()]
    from multiprocessing import Pool
    if jobs:
        with Pool(4) as p:
            for m in p.imap_unordered(work, jobs): print(m, flush=True)
    def star(r, h): return "**" if r[f"lo95_{h}"] > 0 or r[f"hi95_{h}"] < 0 else "*" if r[f"lo{h}"] > 0 or r[f"hi{h}"] < 0 else ""
    md = ["# Real version with the FCI, cubic spline in the monthly equations only or in the monthly and daily equations (12 lags, 500 draws)", "",
          "Per +1 pp on the 2-year in the window: u = unemployment gap (pp), P = price level (percent). `**` / `*`: 95 / 90 percent interval excludes zero; 90 percent intervals in brackets. "
          "Monthly spline knots: from 1996 1996-01, 2001-03, 2007-12, 2020-02, 2026-09; from 1973 1974-01, 1980-01, 1981-07, 1990-07, 2001-03, 2007-12, 2020-02, 2026-09. "
          "Daily spline (daily block, 1996-2026 in both): 1996-01, 2001-03, 2007-12, 2020-02, 2026-09. No-trend rows: the package's real baseline.", ""]
    for s in ("1996-01", "1973-01"):
        md += [f"## From {s[:4]}", "", "| trend | u 12m | u 24m | u 36m | P 12m | P 24m | P 36m |", "|---|---|---|---|---|---|---|"]
        for lab, f in (("no trend", BASE / "results" / f"real_real_upi_{s}_all_out.csv"), ("spline, monthly equations only", fname((s, "monthly"))), ("spline, monthly and daily equations", fname((s, "monthly+daily")))):
            R = pd.read_csv(f); R = R[R.lags == 12].set_index("var")
            md.append(f"| {lab} | " + " | ".join(f"{R.loc[v, f'r{h}']:+.2f}{star(R.loc[v], h)} [{R.loc[v, f'lo{h}']:+.2f}, {R.loc[v, f'hi{h}']:+.2f}]" for v in ("u", "P") for h in (12, 24, 36)) + " |")
        md.append("")
    (HERE / "spline_daily.md").write_text("\n".join(md)); print("\n".join(md))
