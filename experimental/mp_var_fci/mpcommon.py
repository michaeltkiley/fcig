"""Shared helpers for steps 3-4: monthly data, event-level surprises (the note's 253 events, merged with FF4 from the USMPD workbook), monthly instruments
(simple sum, and timing-adjusted for monthly averages), VAR residuals, first-stage F, proxy-SVAR IRFs and conditional Anderson-Rubin sets."""
import sys, warnings, calendar
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.api import VAR
warnings.filterwarnings("ignore")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "fci_note" / "replication"))
from fci import indexes as I          # noqa: E402

M = pd.read_csv(HERE / "data/mp_monthly.csv", index_col=0); M.index = pd.PeriodIndex(M.index, freq="M")


def fred(n):
    f = HERE / f"data/{n}.csv"
    if not f.exists():                                               # download from FRED's CSV endpoint (no key needed)
        import subprocess, re
        txt = subprocess.run(["curl", "-sS", "-L", "--http1.1", "-m", "120", "-A", "fcig-replication/1.0 (+https://michaeltkiley.github.io/fcig/)",
                              f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={n}&cosd=1950-01-01"], capture_output=True, text=True).stdout.strip().splitlines()
        rows = [(a, b) for a, _, b in (l.partition(",") for l in txt[1:]) if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", a) and re.fullmatch(r"-?[0-9.]+", b) and b != "."]
        assert len(rows) > 100, f"download of {n} failed"
        pd.DataFrame(rows, columns=["observation_date", n]).to_csv(f, index=False)
    d = pd.read_csv(f); return pd.Series(d[n].values.astype(float), index=pd.to_datetime(d["observation_date"]))


def events():
    ev = I.events().copy()
    u = pd.read_excel(HERE / "data/USMPD.xlsx", "Monetary Events")[["Date", "FF4"]]
    ev = ev.merge(u, on="Date", how="left")
    b = sm.OLS(ev.ED4.values, sm.add_constant(ev.MP1.values)).fit(); ev["path"] = b.resid
    ev["m"] = ev.Date.dt.to_period("M")
    ev["w"] = [(calendar.monthrange(d.year, d.month)[1] - d.day) / calendar.monthrange(d.year, d.month)[1] for d in ev.Date]    # share of the month after the event
    return ev


def monthly_instruments(ev, cols=("ns", "MP1", "MP2", "ED4", "FF4", "path", "UST2Y")):
    out = {}
    for k in cols:
        s = ev[k].fillna(0.0)
        out[k] = (s.groupby(ev.m).sum()).reindex(M.index).fillna(0.0)
        # timing-adjusted for a monthly-average dependent variable: share w in the event month, share 1-w in the next month
        cur = (s * ev.w).groupby(ev.m).sum().reindex(M.index).fillna(0.0)
        nxt = (s * (1 - ev.w)).groupby(ev.m + 1).sum().reindex(M.index).fillna(0.0)
        out[k + "_adj"] = cur + nxt
    return pd.DataFrame(out)


def var_resid(cols, vstart, vend="2026-09", lags=12, zlb=False, rstart="1994-01"):
    X = M.loc[vstart:vend, cols].dropna()
    ms = set(pd.period_range("2020-01", "2020-12", freq="M"))
    if zlb:
        for s, e in (("2008-12", "2015-12"), ("2020-03", "2022-03")):
            ms |= set(pd.period_range(s, e, freq="M"))
    ms = [m for m in sorted(ms) if m in X.index]
    dum = pd.DataFrame({f"d{m}": (X.index == m).astype(float) for m in ms}, index=X.index)
    X = X.copy(); X.index = X.index.to_timestamp(); dum.index = X.index
    r = VAR(X, exog=dum if dum.shape[1] else None).fit(lags)
    e = r.resid.copy(); e.index = e.index.to_period("M")
    return r, e.loc[rstart:vend]


def first_stage(e, z):
    z = z.reindex(e.index)
    X = sm.add_constant(z.values)
    ro = sm.OLS(e.values, X).fit(cov_type="HC1"); rh = sm.OLS(e.values, X).fit()
    return ro.tvalues[1] ** 2, rh.tvalues[1] ** 2, ro.params[1]      # robust F, homoskedastic F, coefficient


def ar_set(Phi_rows, e, p, z, level=3.841):
    """Anderson-Rubin set (conditional on the VAR coefficients) for the response of one variable at each horizon.
    Phi_rows: (H+1, k) rows a_h of the MA matrices for that variable; e: residuals (T x k); p: scaling column; z: instrument (Series aligned with e).
    Returns list of (lo, hi): bounded interval, (-inf, inf) if unbounded, (nan, nan) if empty."""
    zc = (z - z.mean()).values; ep = e[:, p]; T = len(zc); out = []
    for a in Phi_rows:
        c = e @ a
        A, B = np.mean(zc * c), np.mean(zc * ep)
        Scc, Scp, Spp = np.mean(zc ** 2 * c * c), np.mean(zc ** 2 * c * ep), np.mean(zc ** 2 * ep * ep)
        qa, qb, qc = T * B * B - level * Spp, -2 * T * A * B + 2 * level * Scp, T * A * A - level * Scc
        if qa > 0:
            d = qb * qb - 4 * qa * qc
            out.append((np.nan, np.nan) if d < 0 else ((-qb - np.sqrt(d)) / (2 * qa), (-qb + np.sqrt(d)) / (2 * qa)))
        else:
            out.append((-np.inf, np.inf))
    return out


def lunsford_colombo(e, z, anchor):
    """Lunsford F (instrument projected on all VAR errors) and Colombo shock-based F; also the impact vector b (anchor normalized to 1)."""
    X1 = sm.add_constant(z.values)
    gam = np.array([sm.OLS(e[c].values, X1).fit().params[1] for c in e.columns]); b = gam / gam[list(e.columns).index(anchor)]
    FL = sm.OLS(z.values, sm.add_constant(e.values)).fit().fvalue
    w = e.values @ np.linalg.solve(np.cov(e.values.T), b); FC = sm.OLS(w, X1).fit().tvalues[1] ** 2
    return FL, FC, b
