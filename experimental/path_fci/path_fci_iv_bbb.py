"""
EXPERIMENTAL add-on to path_fci.py (unchanged). Spread response to the 10-year yield, instrumented by the path surprise.

    first stage   d y10_e  = a + p * path_e + g * target_e + v_e          (event-day change in the 10-year, same window as the spread)
    second stage  d spread_e = c + beta * d y10_e + h * target_e + u_e   (beta = spread change per 1 pp of path-driven 10-year change)
Spread = Moody's Baa yield less the 10-year Treasury (FRED DBAA - DGS10): one continuous daily series for the whole sample (the ICE BofA BBB OAS
starts in 1997, shown as a check from 1997, taken from the GS file). Window: close of t-1 to close of t (--window 2 uses t-1 to t+1). Just identified (instrument = path); HC1 errors.
Because the spread is Baa less the same 10-year, beta - 1 is the response of the Baa yield to a path-driven 1 pp in the 10-year, minus 1 -- i.e. the
Baa yield passes through (1 + beta) per pp of 10-year.

Usage:  python experimental/path_fci/path_fci_iv_bbb.py
"""
import os, sys
import numpy as np, pandas as pd
import statsmodels.api as sm
import path_fci as P

HERE, ROOT = P.HERE, P.ROOT


def ld(name):
    d = pd.read_csv(os.path.join(ROOT, "raw", f"{name}.csv")); d.columns = ["date", "v"]
    d["date"] = pd.to_datetime(d.date); d["v"] = pd.to_numeric(d.v, errors="coerce")
    return d.set_index("date").v.dropna()


def window_change(s, dates, k):
    pos = s.index.get_indexer(dates, method="bfill")
    return pd.Series(s.values[np.minimum(pos + k, len(s) - 1)] - s.values[pos - 1], index=dates.index)


def tsls(y, x, Z, ex):
    """y on endogenous x, instruments Z (list of cols), exogenous ex (with const). Returns beta, se (HC1), first-stage F for the instruments."""
    ok = y.notna() & x.notna()
    y, x, Z, ex = y[ok], x[ok], Z[ok], ex[ok]
    fs = sm.OLS(x, pd.concat([ex, Z], axis=1)).fit(cov_type="HC1")
    f = float(fs.wald_test(" , ".join(f"{c} = 0" for c in Z.columns), use_f=True, scalar=True).statistic)
    xh = fs.fittedvalues.rename("xh")
    ss = sm.OLS(y, pd.concat([ex, xh], axis=1)).fit()
    # 2SLS residuals use the actual x
    b = ss.params
    res = y - ex.values @ b[ex.columns].values - x.values * b["xh"]
    W = pd.concat([ex, xh], axis=1).values
    A = np.linalg.inv(W.T @ W); meat = (W * res.values[:, None]).T @ (W * res.values[:, None]) * len(y) / (len(y) - W.shape[1])
    se = np.sqrt(np.diag(A @ meat @ A))
    k = list(pd.concat([ex, xh], axis=1).columns).index("xh")
    return float(b["xh"]), float(se[k]), f, int(ok.sum()), fs.params[Z.columns[0]], fs.rsquared


def main():
    ev = P.events(P.USMPD)
    baa, t10 = ld("DBAA"), ld("DGS10")
    spread = (baa - t10).dropna()
    # ICE BofA BBB OAS from 1997 (x_bbb in the GS file: ICE OAS from 1997, Baa less 10-year before); only used for events from 1997
    oas = pd.read_csv(os.path.join(ROOT, "fcig_gs_daily.csv"), parse_dates=["date"]).set_index("date").x_bbb.dropna()
    ev = ev[ev.Date.isin(spread.index)].reset_index(drop=True)
    print(f"Baa - 10-year spread, {spread.index[0].date()} to {spread.index[-1].date()}, mean {spread.mean():.2f}, sd of daily change {spread.diff().std():.3f}\n")
    rows = []
    for samp in ("full", "nonzlb", "1997+ (ICE OAS)"):
        e = ev.copy()
        if samp == "nonzlb":
            e = e[~P.in_zlb(e.Date)].reset_index(drop=True)
        if samp.startswith("1997"):
            e = e[e.Date >= "1997-01-01"].reset_index(drop=True)
        for k in (0, 1):
            dy = window_change(t10, e.Date, k)
            ds = window_change(oas if samp.startswith("1997") else spread, e.Date, k)
            dbaa = window_change(baa, e.Date, k)
            ex = sm.add_constant(e[["target"]])
            Zp = e[["path"]]
            ols = sm.OLS(ds, pd.concat([ex, dy.rename("dy")], axis=1), missing="drop").fit(cov_type="HC1")
            b, se, F, n, p, r2 = tsls(ds, dy, Zp, ex)
            red = sm.OLS(ds, pd.concat([ex, e[["path"]]], axis=1), missing="drop").fit(cov_type="HC1")
            rows.append(dict(sample=samp, window="t-1..t" if k == 0 else "t-1..t+1", n=n, first_stage_path=p, F=F, iv_beta=b, iv_se=se, ols_beta=ols.params["dy"],
                             reduced_form_path=red.params["path"]))
    R = pd.DataFrame(rows)
    pd.set_option("display.width", 200)
    print(R.round(3).to_string(index=False))
    R.round(5).to_csv(os.path.join(HERE, "path_fci_iv_bbb.csv"), index=False)
    # implied weights: replace BBB response to path by iv_beta * (10-year response), keep the rest of the MS set; shown for the full / t-1..t case
    r = R[(R["sample"] == "full") & (R.window == "t-1..t")].iloc[0]
    print(f"\nFull sample: IV beta {r.iv_beta:+.3f} (se {r.iv_se:.3f}); first-stage F {r.F:.0f}. Spread falls {-r.iv_beta:.2f} pp for each 1 pp of path-driven 10-year rise, so a Baa yield "
          f"rises {1 + r.iv_beta:.2f} per 1 pp 10-year.")


if __name__ == "__main__":
    main()
