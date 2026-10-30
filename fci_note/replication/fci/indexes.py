"""The indexes: market index, GS replication, FRB/US (macro-model) index, FCI-G replication. Each returns the index and its contributions."""
import numpy as np, pandas as pd
import statsmodels.api as sm
from .data import DATA
from .cases import demean

# ---------------------------------------------------------------- market index (weights from policy news)

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


MARKET_VARS = ["y10", "equities", "dollar"]          # USMPD: UST10Y (pp), SP500 (%), DXY (%)


def market(X, w):
    C = demean(X[MARKET_VARS]) * pd.Series(w, index=MARKET_VARS)
    return C.sum(axis=1), C


# ---------------------------------------------------------------- GS replication (published weights)

GS_W = {"policy": 0.044, "y10": 0.451, "bbb_spread": 0.396, "equities": -0.049, "dollar_gs": 0.060}


def gs(X, to_2y):
    """GS FCI replication (Hatzius et al. weights), in GS points times `to_2y` (2-year-yield units per GS point, from its response to policy news)."""
    C = demean(X[list(GS_W)]) * pd.Series(GS_W) * to_2y
    return C.sum(axis=1), C


# ---------------------------------------------------------------- FRB/US macro-model index

FRBUS_VARS = {"policy": "rshort", "y10": "rg10", "mortgage_spread": "rme", "bbb_spread": "rbbbp", "equities": "req", "dollar": "fpxr", "house": "phouse"}


def frbus_paths():
    """Cumulative GDP responses Phi_j(q) to a persistent unit shift in each variable (quarters 0..32), and the yardstick G(q): GDP response to a persistent
    1 pp funds-rate hike (FRB/US, VAR expectations; the short rate with z-expectations fixed)."""
    p = pd.read_csv(DATA / "frbus_paths.csv"); p = p[p["shape"] == "persistent"]
    P = {}
    for v, e in FRBUS_VARS.items():
        g = p[(p.design == ("zfixed" if e == "rshort" else "zfree")) & (p.experiment == e)].sort_values("quarter").gdp_per_unit.values
        P[v] = np.r_[0.0, g]
    G = np.r_[0.0, pd.read_csv(DATA / "frbus_hike_paths.csv").sort_values("quarter").gdp.values]
    return pd.DataFrame(P), G


def phi_at(P, q):
    qs = np.arange(len(P))
    return pd.Series({v: np.interp(q, qs, P[v].values) for v in P.columns})


def frbus(X, house=False, K=4):
    """Eventual pressure (level): Phi(K)' x / G(K), funds-rate pp. Growth impetus (FCI-G form, 1-year lookback): effect over the next 4 quarters
    of the last 12 months of changes, sum_m [Phi((m+1)/3 + 4) - Phi((m+1)/3)]' dx(t-m) / G(4)."""
    P, G = frbus_paths()
    cols = [c for c in FRBUS_VARS if house or c != "house"]
    Xd = demean(X[cols])
    w = phi_at(P[cols], K) / G[K]
    C = Xd * w
    dX = Xd.diff()
    Wg = [(phi_at(P[cols], (m + 1) / 3 + 4) - phi_at(P[cols], (m + 1) / 3)) / G[4] for m in range(12)]
    gi = sum((dX.shift(m) * Wg[m]).sum(axis=1, min_count=len(cols)) for m in range(12))
    return C.sum(axis=1, min_count=len(cols)), C, gi


# ---------------------------------------------------------------- FCI-G replication (Fed multipliers, monthly)

FCIG_VARS = ["policy", "y10", "mortgage_yield", "baa_yield", "stocks_level", "house_level", "dollar_gs"]


def fcig_weights():
    W = -pd.read_csv(DATA / "multipliers.csv").values          # rows: quarter lags (beta_{i+4} - beta_i); the Fed's code enters stocks and houses with the opposite sign
    W[:, 4:6] *= -1
    return W[:12]


def fcig(X, lookback=4):
    """FCI-G (Ajello et al. 2023) on monthly data: sum over quarter lags i < lookback of w_i' dX(t - 3i), where dX is the 3-month change of the 3-month average
    (rates, pp), 100 x the 3-month log change (stock and house prices), 100 x the log change of the 3-month average (dollar). Units: pp of GDP growth."""
    W = fcig_weights()
    D = pd.DataFrame(index=X.index)
    for c in FCIG_VARS:
        if c in ("stocks_level", "house_level"):
            D[c] = 100 * np.log(X[c]).diff(3)
        elif c == "dollar_gs":
            D[c] = 100 * np.log(np.exp(X[c] / 100).rolling(3).mean()).diff(3)
        else:
            D[c] = X[c].rolling(3).mean().diff(3)
    C = sum(D.shift(3 * i) * W[i] for i in range(lookback))
    return C.sum(axis=1, min_count=len(FCIG_VARS)), C
