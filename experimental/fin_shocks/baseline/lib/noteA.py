"""Note A's construction of the market index (the FCI), vendored from fci_note/replication/fci/{data,cases,indexes}.py so that this package rebuilds
every input of Note B from raw data (data/). Trimmed to what Note B uses: the monthly inputs of the market index (10-year yield, CAPE, real broad dollar,
expected inflation, r*), the unemployment gap, the policy-news events and factor, the one-factor GLS weights, and the index in three steps
(nominal -> real -> r*-gap, with Laubach-Williams or Kiley r*). 02_indexes.py checks the result against Note A's published files."""
import numpy as np, pandas as pd
import statsmodels.api as sm
from .paths import DATA

START, END = "1973-01", "2026-09"          # sample and zero-point window (each variable demeaned over it)
MARKET_VARS = ["y10", "equities", "dollar"]          # USMPD: UST10Y (pp), SP500 (%), DXY (%)

# ---------------------------------------------------------------- monthly data
def fred(name, how="mean"):
    """FRED csv -> monthly series (mean or last observation in the month), PeriodIndex."""
    d = pd.read_csv(DATA / f"{name}.csv")
    s = pd.Series(pd.to_numeric(d.iloc[:, 1], errors="coerce").values, index=pd.to_datetime(d.iloc[:, 0])).dropna()
    g = s.groupby(s.index.to_period("M"))
    return g.mean() if how == "mean" else g.last()

def monthly_csv(name, col):
    d = pd.read_csv(DATA / name)
    return pd.Series(d[col].values, index=pd.PeriodIndex(d.iloc[:, 0], freq="M"))

def splice_log(new, old, overlap):
    """Extend `new` back with `old`, shifted in logs by their mean log gap over `overlap`."""
    k = float(np.log(new.loc[overlap]).mean() - np.log(old.loc[overlap]).mean())
    return pd.concat([old.loc[:new.index[0] - 1] * np.exp(k), new])

def mid_quarter(q):
    """Quarterly values placed in the middle month of each quarter, linearly interpolated, last value held."""
    m = pd.Series(q.values, index=[p.asfreq("M", "s") + 1 for p in q.index])
    full = pd.period_range(m.index[0], END, freq="M")
    return m.reindex(full).interpolate(limit_area="inside").ffill()

def unemployment_gap():
    u = fred("UNRATE")
    n = pd.read_csv(DATA / "NROU.csv"); n = pd.Series(n.iloc[:, 1].values, index=pd.PeriodIndex(pd.to_datetime(n.iloc[:, 0]), freq="Q"))
    return u - mid_quarter(n).reindex(u.index)

def expected_inflation():
    """Cleveland Fed 1- and 10-year expectations from 1982; before, the Livingston 12-month CPI expectation (semiannual, interpolated),
    shifted to each Cleveland series by the mean gap over 1982-84 and blended over 1982 (Cleveland weight 1/12 in January to 1 in December)."""
    lv = pd.read_excel(DATA / "livingston_median_growth.xlsx", "CPI").set_index("Date")["G_BP_To_12M"].dropna()
    lv.index = pd.to_datetime(lv.index).to_period("M")
    lv = lv.reindex(pd.period_range(lv.index[0], END, freq="M")).interpolate(limit_area="inside")
    out = {}
    for lab, name in (("einf_1y", "EXPINF1YR"), ("einf_10y", "EXPINF10YR")):
        c = fred(name)
        k = float((c.loc["1982-01":"1984-12"] - lv.loc["1982-01":"1984-12"]).mean())
        s = pd.concat([lv.loc[:c.index[0] - 1] + k, c])
        for i, m in enumerate(pd.period_range("1982-01", "1982-12", freq="M")):
            s.loc[m] = (1 - (i + 1) / 12) * (lv.loc[m] + k) + (i + 1) / 12 * c.loc[m]
        out[lab] = s
    return pd.DataFrame(out)

def rstar():
    """One-sided r* (full-sample estimation): Laubach-Williams (main) and Kiley (check), quarterly -> monthly."""
    r = pd.read_csv(DATA / "rstar_onesided.csv", index_col=0); r.index = pd.PeriodIndex(r.index, freq="Q")
    return pd.DataFrame({"rstar LW": mid_quarter(r.LW_onesided.dropna()), "rstar Kiley": mid_quarter(r.Kiley_onesided.dropna())})

def cape():
    """Shiller CAPE, spliced in logs (1990-92) to the monthly average of the daily CAPE behind the repository's GS replication (Shiller E10, multpl.com)."""
    g = pd.read_csv(DATA / "gs_daily.csv", parse_dates=["date"]).set_index("date").cape
    new = g.groupby(g.index.to_period("M")).mean()
    return splice_log(new, monthly_csv("shiller_cape.csv", "cape"), slice("1990-01", "1992-12"))

def dollar_real():
    return splice_log(fred("RTWEXBGS"), fred("TWEXBPA"), slice("2006-01", "2006-12"))

def build():
    """Monthly inputs, 1958 onward: 10-year yield, CAPE, real broad dollar, unemployment gap, expected inflation (1- and 10-year), r* (LW, Kiley)."""
    D = pd.DataFrame({"y10": fred("GS10"), "cape": cape(), "usd_real": dollar_real(), "u_gap": unemployment_gap()})
    D = D.join(expected_inflation()).join(rstar())
    D["u_gap"] = D["u_gap"].interpolate(limit_area="inside")           # October 2025: no unemployment release (government shutdown); interpolated
    return D.loc["1958-01":END]

# ---------------------------------------------------------------- events and weights
def ns_factor(ev):
    """Nakamura-Steinsson policy news: first principal component of MP1, MP2, ED2, ED3, ED4, scaled so that 1 unit moves the 2-year yield by 1 pp."""
    X = ev[["MP1", "MP2", "ED2", "ED3", "ED4"]].values
    U, S, Vt = np.linalg.svd(X, full_matrices=False)
    f = U[:, 0] * S[0]
    if f @ ev.ED4.values < 0:
        f = -f
    return f * (f @ ev.UST2Y.values) / (f @ f)

def events():
    """USMPD 'Monetary Events' (statement + press conference window): drop unscheduled no-move events and March-April 2020."""
    d = pd.read_csv(DATA / "usmpd_monetary_events.csv", parse_dates=["Date"])
    d = d[~((d.Unscheduled == 1) & (d.MP1 == 0))]
    d = d[~((d.Date >= "2020-03-01") & (d.Date <= "2020-04-30"))]
    d = d.dropna(subset=["MP1", "MP2", "ED2", "ED3", "ED4", "UST2Y", "UST10Y", "SP500", "DXY"]).reset_index(drop=True)
    d["ns"] = ns_factor(d)
    return d

def gls_weights(Y, f):
    """One-factor GLS: responses psi (OLS of each window move on f), residual covariance S, weights w = S^-1 psi / (psi' S^-1 psi), so w' psi = 1."""
    Z = sm.add_constant(f)
    fits = [sm.OLS(Y[:, j], Z).fit(cov_type="HC1") for j in range(Y.shape[1])]
    psi = np.array([r.params[1] for r in fits]); se = np.array([r.bse[1] for r in fits])
    S = np.cov(np.array([r.resid for r in fits]), ddof=2)
    w = np.linalg.solve(S, psi)
    return w / (psi @ w), psi, se

# ---------------------------------------------------------------- the index
def index_inputs(D, case, rstar="rstar LW"):
    """Monthly inputs of the market index for one step. nominal: rates as published, equities 100 ln CAPE; real: 10-year yield less 10-year expected inflation;
    rstar: also less r*, equities as the earnings-yield gap E/P - r* converted to CAPE log points at the average E/P (so the index keeps its CAPE weight).
    The dollar is the real broad dollar (100 ln) in every step."""
    e10 = D.einf_10y if case != "nominal" else 0.0
    r = D[rstar] if case == "rstar" else 0.0
    X = pd.DataFrame(index=D.index)
    X["y10"] = D.y10 - e10 - r
    if case == "rstar":
        ep = 100 / D.cape
        X["equities"] = -(100 / ep.loc[START:END].mean()) * (ep - r)
    else:
        X["equities"] = 100 * np.log(D.cape)
    X["dollar"] = 100 * np.log(D.usd_real)
    return X

def market_index(X, w):
    """Weighted sum of the demeaned inputs (demeaned over START..END): the market index in 2-year-yield equivalents."""
    C = (X[MARKET_VARS] - X[MARKET_VARS].loc[START:END].mean()) * pd.Series(w, index=MARKET_VARS)
    return C.sum(axis=1)
