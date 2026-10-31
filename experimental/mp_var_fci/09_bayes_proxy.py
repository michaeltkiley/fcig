"""Step 9 (user's choice after the summary). Bayesian proxy-SVAR in the spirit of Caldara-Herbst (2019), with the policy REACTION FUNCTION from the same draws.
Model. VAR y_t = X_t Phi + u_t, u_t ~ N(0, Sigma) with a flat (Jeffreys) prior, so (Phi, Sigma) | data is normal-inverse-Wishart; explosive draws are discarded. Structural: u_t = B eps_t, B = L Q (L = chol Sigma, Q orthogonal);
the monetary shock is eps_1,t = q' L^-1 u_t with q a unit vector (uniform prior on the sphere). Proxy: m_t = beta eps_1,t + sigma_nu nu_t, parametrised by the reliability rho = beta^2/(beta^2 + sigma_nu^2):
beta = sqrt(rho) s, sigma_nu = sqrt(1 - rho) s with s the sample sd of m. PRIOR on rho: uniform on [rho_lo, 1): 'loose' rho_lo = 0, 'mid' 0.2, 'tight' 0.33 (CH report reliability 0.11 and 0.33 for their funds-rate proxy; 0.01 and 0.18 for 2-year).
Sampling: for each (Phi, Sigma) draw, 5 steps of Gibbs on (rho | q) by grid and (q | rho) by Metropolis-Hastings with a von Mises-Fisher proposal centred on the instrumental-variable direction. The proxy does not feed back into (Phi, Sigma) (CH's joint posterior
does): an approximation, stated here.
Outputs per draw: reliability rho; impact vector b = L q (sign fixed so the policy variable rises); IRFs Theta_h b; and the policy REACTION coefficients: eps_1 = w'u with w = L^-T q, so the policy equation is
u_policy = -sum_{i != policy} (w_i / w_policy) u_i + eps_1 / w_policy; a_i = -w_i / w_policy is the within-month reaction of the policy variable to the residual of variable i (unit: policy variable per unit of variable i).
Output: 09_bayes_proxy.log, bayes_proxy.csv"""
import numpy as np, pandas as pd, warnings, time
from scipy.stats import invwishart
from mpcommon import *
warnings.filterwarnings("ignore")
rng = np.random.default_rng(2026)
eb = pd.read_csv(HERE / "data/ebp.csv"); eb.index = pd.PeriodIndex(pd.to_datetime(eb.date), freq="M"); M["ebp"] = eb.ebp.reindex(M.index)
ip = fred("INDPRO"); ip = ip.groupby(ip.index.to_period("M")).mean(); M["dIP"] = 100 * np.log(ip).diff().reindex(M.index)
ev = events(); sch = ev[ev.Unscheduled == 0]
mon = lambda d, k: d.groupby("m")[k].sum().reindex(M.index).fillna(0.0)
Zall = monthly_instruments(ev); Zsch = {"MP1": mon(sch, "MP1")}
H = 24

def design(cols, vstart, vend, p):
    X0 = M.loc[vstart:vend, cols].dropna(); idx = X0.index
    ms = [m for m in pd.period_range("2020-01", "2020-12", freq="M") if m in idx]
    dum = np.column_stack([(idx == m).astype(float) for m in ms]) if ms else np.zeros((len(idx), 0))
    Y = X0.values; T = len(Y)
    lag = np.column_stack([Y[p - j - 1:T - j - 1] for j in range(p)])
    Xr = np.column_stack([np.ones(T - p), dum[p:], lag])
    return Y[p:], Xr, idx[p:], dum.shape[1]

def vmf(mu, kappa):
    k = len(mu)
    if kappa < 1e-8:
        x = rng.normal(size=k); return x / np.linalg.norm(x)
    b = (-2 * kappa + np.sqrt(4 * kappa ** 2 + (k - 1) ** 2)) / (k - 1); x0 = (1 - b) / (1 + b); c = kappa * x0 + (k - 1) * np.log(1 - x0 ** 2)
    while True:
        z = rng.beta((k - 1) / 2, (k - 1) / 2); w = (1 - (1 + b) * z) / (1 - (1 - b) * z)
        if kappa * w + (k - 1) * np.log(1 - x0 * w) - c >= np.log(rng.uniform()): break
    v = rng.normal(size=k); v -= (v @ mu) * mu; v /= np.linalg.norm(v)
    return w * mu + np.sqrt(max(1 - w * w, 0)) * v

def ma(Aj, H):
    p, k, _ = Aj.shape; Th = np.zeros((H + 1, k, k)); Th[0] = np.eye(k)
    for h in range(1, H + 1):
        for j in range(1, min(h, p) + 1): Th[h] += Aj[j - 1] @ Th[h - j]
    return Th

def run(cols, policy, z, vstart, vend, p, rstart, rho_lo, draws=700, burn=150, label=""):
    Y, Xr, idx, nd = design(cols, vstart, vend, p); T, K = Xr.shape; k = len(cols); pi_ = cols.index(policy)
    XtXi = np.linalg.inv(Xr.T @ Xr); Phi_hat = XtXi @ Xr.T @ Y; E = Y - Xr @ Phi_hat; S = E.T @ E; chX = np.linalg.cholesky(XtXi)
    win = np.array([pp >= pd.Period(rstart, "M") for pp in idx]); m = z.reindex(idx).values[win]; s = m.std(); n = win.sum()
    grid = np.linspace(max(rho_lo, 1e-4), 0.999, 300)
    q = None; out = []; rej = 0
    for it in range(draws + burn):
        Sig = invwishart.rvs(df=T - K, scale=S, random_state=rng); L = np.linalg.cholesky(Sig)
        Phi = Phi_hat + chX @ rng.normal(size=(K, k)) @ L.T
        Aj = Phi[1 + nd:].reshape(p, k, k).transpose(0, 2, 1)       # Phi rows are lag blocks (k x k each): A_j = block_j'
        comp = np.zeros((k * p, k * p)); comp[:k, :] = np.concatenate(list(Aj), axis=1); comp[k:, :-k] = np.eye(k * (p - 1))
        if np.max(np.abs(np.linalg.eigvals(comp))) > 1.0005: rej += 1; continue
        U = (Y - Xr @ Phi)[win]; Z = U @ np.linalg.inv(L).T; Zm = Z.T @ m; ZZ = Z.T @ Z; nZm = np.linalg.norm(Zm)
        if q is None: q = Zm / nZm
        for _ in range(5):
            Bq = q @ Zm; Cq = q @ ZZ @ q; Am = m @ m
            ll = -n / 2 * np.log((1 - grid) * s * s) - (Am - 2 * np.sqrt(grid) * s * Bq + grid * s * s * Cq) / (2 * (1 - grid) * s * s)
            pr = np.exp(ll - ll.max()); rho = rng.choice(grid, p=pr / pr.sum())
            kap = np.sqrt(rho) * nZm / ((1 - rho) * s); qn = vmf(Zm / nZm, kap); a = rho / (1 - rho)
            if np.log(rng.uniform()) < -a / 2 * (qn @ ZZ @ qn - q @ ZZ @ q): q = qn
        if it < burn: continue
        b = L @ q; sg = 1.0 if b[pi_] > 0 else -1.0; qs = sg * q; b = sg * b
        w = np.linalg.solve(L.T, qs); react = -w / w[pi_]
        Th = ma(Aj, H); irf = np.einsum("hij,j->hi", Th, b)
        cum = np.cumsum(irf, axis=0)                                  # cumulated responses (used for the industrial production growth rate dIP)
        sdU = U.std(axis=0)
        out.append(dict(rho=rho, bp=b[pi_], **{f"irf12_{c}": (cum[12, i] if c == "dIP" else irf[12, i]) for i, c in enumerate(cols)}, **{f"irf24_{c}": (cum[24, i] if c == "dIP" else irf[24, i]) for i, c in enumerate(cols)},
                        **{f"react_{c}": react[i] for i, c in enumerate(cols) if c != policy}, **{f"reactsd_{c}": react[i] * sdU[i] for i, c in enumerate(cols) if c != policy}, scale25=0.25 / b[pi_]))
    return pd.DataFrame(out), rej

def q_(x, lo, hi): return np.percentile(x, [lo, hi])
def summarize(df, cols, act, label, priorlab):
    a12, a24 = df[f"irf12_{act}"].values, df[f"irf24_{act}"].values; sc = df.scale25.values
    lo, hi = q_(a12, 5, 95); r = df.rho.values
    s25 = a12 * sc; l25, h25 = q_(s25, 5, 95)
    parts = [f"{label:42s} {priorlab:5s} rho {np.median(r):.2f} [{q_(r, 5, 95)[0]:.2f},{q_(r, 5, 95)[1]:.2f}]  b_pol(1sd) {np.median(df.bp):.2f}",
             f"{act} 12m: 1-sd {np.median(a12):+.2f} [{lo:+.2f},{hi:+.2f}] P>0 {np.mean(a12 > 0):.2f}; per 25bp {np.median(s25):+.2f} [{l25:+.2f},{h25:+.2f}]", f"24m 1-sd {np.median(a24):+.2f} [{q_(a24, 5, 95)[0]:+.2f},{q_(a24, 5, 95)[1]:+.2f}]"]
    rc = [c for c in df.columns if c.startswith("react_") and c != f"react_{act}"]
    keep = lambda c: c.split('_', 1)[1] not in ("u_gap", "pi_core", "dIP")
    parts.append(" | reaction (pp per 1 unit; per 1 sd of the residual): " + "  ".join(f"{c[6:]} {np.median(df[c]):+.2f} [{q_(df[c], 5, 95)[0]:+.2f},{q_(df[c], 5, 95)[1]:+.2f}] / {np.median(df['reactsd_' + c[6:]]):+.3f} [{q_(df['reactsd_' + c[6:]], 5, 95)[0]:+.3f},{q_(df['reactsd_' + c[6:]], 5, 95)[1]:+.3f}]" for c in rc if keep(c)))
    return " | ".join(parts[:3]) + parts[3]

CONFIGS = [
    # (label, cols, policy, instrument, vstart, vend, lags, rstart, activity)
    ("CH trivariate dIP,EBP,ffr (CH window)", ["dIP", "ebp", "ffr"], "ffr", Zsch["MP1"], "1993-07", "2007-06", 6, "1994-01", "dIP"),
    ("CH window: u,pi,ffr,EBP", ["u_gap", "pi_core", "ffr", "ebp"], "ffr", Zsch["MP1"], "1993-07", "2007-06", 6, "1994-01", "u_gap"),
    ("CH window: u,pi,ffr,index", ["u_gap", "pi_core", "ffr", "market_rstar"], "ffr", Zsch["MP1"], "1993-07", "2007-06", 6, "1994-01", "u_gap"),
    ("CH window: u,pi,ffr,index,EBP", ["u_gap", "pi_core", "ffr", "market_rstar", "ebp"], "ffr", Zsch["MP1"], "1993-07", "2007-06", 6, "1994-01", "u_gap"),
    ("FULL-S1: u,pi,ffr", ["u_gap", "pi_core", "ffr"], "ffr", Zall["MP1"], "1994-01", "2026-09", 12, "1994-01", "u_gap"),
    ("FULL-S1: u,pi,ffr,EBP", ["u_gap", "pi_core", "ffr", "ebp"], "ffr", Zall["MP1"], "1994-01", "2026-09", 12, "1994-01", "u_gap"),
    ("FULL-S1: u,pi,ffr,index", ["u_gap", "pi_core", "ffr", "market_rstar"], "ffr", Zall["MP1"], "1994-01", "2026-09", 12, "1994-01", "u_gap"),
    ("FULL-S1: u,pi,ffr,index,EBP", ["u_gap", "pi_core", "ffr", "market_rstar", "ebp"], "ffr", Zall["MP1"], "1994-01", "2026-09", 12, "1994-01", "u_gap"),
    ("FULL-S1 2-year/ED4: u,pi,gs2,index,EBP", ["u_gap", "pi_core", "gs2", "market_rstar", "ebp"], "gs2", Zall["ED4"], "1994-01", "2026-09", 12, "1994-01", "u_gap"),
]
PRIORS = {"loose": 0.0, "mid": 0.2, "tight": 0.33}
res = []
print("Bayesian proxy-SVAR (flat-prior VAR; proxy reliability prior U[rho_lo,1)); response of the activity variable to a ONE-SD monetary shock (policy variable units: pp), 5-95% credible interval; reaction = within-month response of the policy variable to the residual of the named variable")
t0 = time.time()
for label, cols, pol, z, vs, ve, p, rs, act in CONFIGS:
    for pl, lo in PRIORS.items():
        if pol == "gs2" and pl == "mid": continue
        df, rej = run(cols, pol, z, vs, ve, p, rs, lo)
        df["label"] = label; df["prior"] = pl; res.append(df)
        print(summarize(df, cols, act, label, pl), flush=True)
    print()
pd.concat(res).to_csv("bayes_proxy.csv", index=False, float_format="%.4f")
print(f"done in {time.time() - t0:.0f}s")
