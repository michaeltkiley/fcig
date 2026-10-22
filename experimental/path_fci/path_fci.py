"""
EXPERIMENTAL. Funds-rate-equivalent weights for the GS and MS-style index variables from their response to FOMC path surprises.

Path surprise (orth, as in the earlier local-projection work): the part of the ED4 surprise not explained by the current-meeting
fed funds surprise MP1. ED4 is the fourth quarterly Eurodollar future (SOFR future from 2022), i.e. the expected 3-month rate for the quarter that
starts about 9 months ahead (an average over roughly 9-12 months ahead). A path surprise of 1.00 = a 100 bp (1 pp) rise in that expected
rate with the current funds rate surprise (MP1) unchanged: the policy rate about a year ahead, not the rate today. Events: USMPD
"Monetary Events" sheet (SF Fed); unscheduled events with MP1 == 0 dropped, Mar-Apr 2020 dropped (as in michaeltkiley/monetary_policy_surprises).

Step 1. For each variable x_j (daily levels, same as the GS / MS-style indexes), regress its close-to-close change on each event date on the path
    surprise, controlling for the target surprise (MP1):
        dx_j,e = a_j + b_j path_e + c_j target_e + u_j,e              b_j = response to a 1 pp path surprise (HC1 errors)
    The event-day change includes other news that day (BBB spreads and oil have no intraday series); for 10-year, S&P 500 and dollar an intraday
    (USMPD window) version is shown as a check.
Step 2. Funds-rate-equivalent weights. A single variable gives its own estimate, 1 / b_j (pp of path-rate move per unit of x_j), but summing those
    would count the same surprise several times. The weights used are the one-factor (GLS, Bartlett) weights
        w_j = (b_j / s_j^2) / sum_k (b_k^2 / s_k^2),      s_j^2 = residual variance of regression j,
    so that sum_j w_j b_j = 1: an index sum_j w_j (x_j - mean_j) moves exactly 1 pp when a 1 pp path surprise moves every variable by b_j, and
    noisy variables (small b_j / s_j^2) get little weight. Units of w_j: pp of path-rate per unit of x_j. Compare weights with the FRB/US ones
    (experimental/ms_fci). Level index = sum_j w_j (x_j - mean_j over the daily sample), higher = tighter.

Usage:  python experimental/path_fci/path_fci.py [--sample full|nonzlb] [path/to/USMPD.xlsx]
Outputs: path_fci_betas.csv, path_fci_daily_<sample>.csv, path_fci_<sample>.png
Needs statsmodels, matplotlib, openpyxl.
"""
import os, sys, argparse
import numpy as np, pandas as pd
import statsmodels.api as sm

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "experimental", "ms_fci"))
sys.path.insert(0, ROOT)
import ms5_level as L

USMPD = "/tmp/claude-0/-home-user-fcig/d46513a9-f2f3-5da4-b70e-4c3b1670484e/scratchpad/usmpd/USMPD.xlsx"
ZLB = [("2008-12-16", "2015-12-16"), ("2020-03-15", "2022-03-16")]
# variable -> (column in X, scale to index units: pp for rates, 100*ln otherwise, sign of the index term)
VARS = {"10-yr": ("y10", 1.0), "BBB spread": ("bbb", 1.0), "Equities (ln CAPE)": ("lncape", 100.0), "Dollar (ln real)": ("lnrusd", 100.0),
        "Oil (ln real)": ("lnroil", 100.0), "Fed funds": ("ffr", 1.0)}
SETS = {"GS": ["Fed funds", "10-yr", "BBB spread", "Equities (ln CAPE)", "Dollar (ln real)"],
        "MS": ["10-yr", "BBB spread", "Equities (ln CAPE)", "Dollar (ln real)", "Oil (ln real)"],
        "Core": ["10-yr", "Equities (ln CAPE)", "Dollar (ln real)"]}   # drops the two variables whose path response has the "wrong" sign for a tightening (BBB spread, oil)
INTRADAY = {"10-yr": ("UST10Y", 1.0), "Equities (ln CAPE)": ("SP500", 1.0), "Dollar (ln real)": ("DXY", 1.0)}   # USMPD columns: pp, percent, percent


def events(path):
    d = pd.read_excel(path, sheet_name="Monetary Events")
    d = d[~((d["Unscheduled"] == 1) & (d["MP1"] == 0))]
    d = d.dropna(subset=["MP1", "ED4"]).reset_index(drop=True)
    d = d[~((d.Date >= "2020-03-01") & (d.Date <= "2020-04-30"))].reset_index(drop=True)
    slope, icpt = np.polyfit(d.MP1, d.ED4, 1)
    d["target"], d["path"] = d.MP1, d.ED4 - icpt - slope * d.MP1
    d.attrs["ED4_on_MP1"] = slope
    return d


def in_zlb(dates):
    m = np.zeros(len(dates), bool)
    for a, b in ZLB:
        m |= ((dates > a) & (dates < b)).values if hasattr(dates, "values") else ((dates > a) & (dates < b))
    return m


LEAD = {"Dollar (ln real)"}   # FRED's broad dollar index uses noon rates, so a 2 pm FOMC move shows up the next day: use t-1 to t+1


def event_changes(X, ev):
    """Change in each variable (index units) from the trading day before the event to the event day (dollar: to the day after)."""
    out = pd.DataFrame(index=ev.index)
    for name, (col, sc) in VARS.items():
        s = sc * X[col]
        pos = s.index.get_indexer(ev.Date)
        k = 1 if name in LEAD else 0
        hi = np.minimum(pos + k, len(s) - 1)
        out[name] = s.values[hi] - s.values[pos - 1]
    return out


def fit(dx, ev):
    """b_j (path), c_j (target), residual variance, HC1 s.e. for each variable."""
    rows = {}
    Z = sm.add_constant(ev[["path", "target"]])
    for name in dx:
        y = dx[name]
        ok = y.notna()
        r = sm.OLS(y[ok], Z[ok]).fit(cov_type="HC1")
        rows[name] = dict(b=r.params["path"], se=r.bse["path"], c=r.params["target"], se_c=r.bse["target"], s2=r.resid.var(ddof=3), n=int(ok.sum()),
                          r2=r.rsquared)
    return pd.DataFrame(rows).T


def weights(B, names):
    b, s2 = B.loc[names, "b"].astype(float), B.loc[names, "s2"].astype(float)
    g = b / s2
    return g / (b * g).sum()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", default="full", choices=["full", "nonzlb"])
    ap.add_argument("usmpd", nargs="?", default=USMPD)
    a = ap.parse_args()
    ev = events(a.usmpd)
    X, G = L.build()
    ev = ev[ev.Date.isin(X.index)].reset_index(drop=True)
    if a.sample == "nonzlb":
        ev = ev[~in_zlb(ev.Date)].reset_index(drop=True)
    dx = event_changes(X, ev)
    print(f"{len(ev)} events {ev.Date.min().date()} to {ev.Date.max().date()}  (sample: {a.sample}); ED4 on MP1 slope {ev.attrs['ED4_on_MP1']:.2f}; "
          f"sd path {ev.path.std():.3f} pp, sd target {ev.target.std():.3f} pp")
    B = fit(dx, ev)
    # intraday check
    chk = {}
    for name, (col, _) in INTRADAY.items():
        scale = 1.0 if name == "10-yr" else 1.0
        ok = ev[col].notna()
        r = sm.OLS(ev.loc[ok, col], sm.add_constant(ev.loc[ok, ["path", "target"]])).fit(cov_type="HC1")
        chk[name] = (r.params["path"], r.bse["path"])
    print("\nResponse to a +1 pp path surprise, event-day close-to-close change (index units: pp; 100 ln for CAPE, dollar, oil):")
    pr = B[["b", "se", "c", "se_c", "r2", "n"]].astype(float).round(3)
    pr["t"] = (B.b / B.se).astype(float).round(1)
    pr["1/b (pp path per unit)"] = (1 / B.b.astype(float)).round(2)
    print(pr.to_string())
    print("\nIntraday (USMPD window) response to a +1 pp path surprise: 10-yr in pp; S&P 500 and dollar in percent:")
    for k, (b, se) in chk.items():
        print(f"  {k}: {b:+.3f} (se {se:.3f})")
    pre = ev.Date < "1997-01-01"
    for lab, m in (("BBB spread, events before 1997 (Moody's Baa less 10-yr)", pre), ("BBB spread, events from 1997 (ICE BofA OAS)", ~pre)):
        r = sm.OLS(dx["BBB spread"][m], sm.add_constant(ev.loc[m, ["path", "target"]])).fit(cov_type="HC1")
        print(f"  {lab}: b {r.params['path']:+.3f} (se {r.bse['path']:.3f}), n {int(m.sum())}")
    # weights
    out = {}
    for sname, names in SETS.items():
        w = weights(B, names)
        out[sname] = w
    W = pd.DataFrame(out)
    print("\nFunds-rate-equivalent weights (pp of path-rate per unit of x), one-factor GLS:")
    print(W.round(3).to_string())
    # bootstrap over events: weights and the standalone 1/b
    rng = np.random.default_rng(0)
    boots = {s: [] for s in SETS}; inv = []
    for _ in range(1000):
        i = rng.integers(0, len(ev), len(ev))
        e2, d2 = ev.iloc[i].reset_index(drop=True), dx.iloc[i].reset_index(drop=True)
        Bb = fit(d2, e2)
        for sname, names in SETS.items():
            boots[sname].append(weights(Bb, names))
        inv.append(1 / Bb.b.astype(float))
    print("\n90% bootstrap bands for the weights and standalone 1/b:")
    for sname in SETS:
        bb = pd.DataFrame(boots[sname])
        print(sname, {k: (round(bb[k].quantile(.05), 3), round(bb[k].quantile(.95), 3)) for k in bb})
    inv = pd.DataFrame(inv)
    print("1/b", {k: (round(inv[k].quantile(.05), 2), round(inv[k].quantile(.95), 2)) for k in inv})
    # index levels
    S = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "frbus_sensitivities.csv"), index_col=0)["ffr_eq_q4"]
    C = {}
    for sname, names in SETS.items():
        idx = sum(W.loc[n, sname] * VARS[n][1] * (X[VARS[n][0]] - X[VARS[n][0]].mean()) for n in names)
        C[f"{sname} set, path weights"] = idx
    frbus = L.level(X, S.to_dict(), float(pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "frbus_sensitivities.csv"), index_col=0).loc["req", "unit_size"])).Total
    C["MS FRB/US weights"] = frbus
    C["GS FCI"] = G.fci.reindex(X.index)
    D = pd.DataFrame(C)
    D.to_csv(os.path.join(HERE, f"path_fci_daily_{a.sample}.csv"), float_format="%.4f", index_label="date")
    B.astype(float).round(5).to_csv(os.path.join(HERE, f"path_fci_betas_{a.sample}.csv"), index_label="variable")
    W.to_csv(os.path.join(HERE, f"path_fci_weights_{a.sample}.csv"), float_format="%.5f", index_label="variable")
    print("\nCorrelation of levels / daily changes (1990-2026 / 2009-2026):")
    for per, (p0, p1) in {"1990-2026": ("1990", "2026"), "2009-2026": ("2009", "2026")}.items():
        print(per, "levels\n", D[p0:p1].corr().round(2).to_string(), "\n", per, "daily changes\n", D[p0:p1].diff().corr().round(2).to_string())
    print("\nlatest (20 Oct) values, pp:", D.iloc[-1].round(2).to_dict())
    print("sd of daily change:", D.diff().std().round(3).to_dict())
    plot(D, W, B, a.sample)


def plot(D, W, B, sample):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 1, figsize=(11, 9))
    a = ax[0]
    a.plot(D.index, D["MS set, path weights"], color="#1f77b4", lw=1.2, label="MS variables, path-surprise weights (left, pp)")
    a.plot(D.index, D["MS FRB/US weights"], color="#d62728", lw=1.0, label="MS variables, FRB/US weights (left, pp)")
    a.plot(D.index, D["GS set, path weights"], color="#2ca02c", lw=1.0, alpha=0.8, label="GS variables, path-surprise weights (left, pp)")
    a.axhline(0, color="gray", lw=0.6)
    a.set_ylabel("pp of funds-rate equivalent vs 1990-2026 mean")
    b = a.twinx(); b.plot(D.index, D["GS FCI"], color="k", lw=0.8, alpha=0.6, label="GS FCI (right)")
    h1, l1 = a.get_legend_handles_labels(); h2, l2 = b.get_legend_handles_labels()
    a.legend(h1 + h2, l1 + l2, loc="upper right", fontsize=8)
    a.set_title(f"Indexes with path-surprise weights (sample for betas: {sample})")
    names = list(W.index)
    x = np.arange(len(names)); a2 = ax[1]
    a2.bar(x - 0.2, W["MS"], 0.4, label="path-surprise weights (MS set)", color="#1f77b4")
    S = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "frbus_sensitivities.csv"), index_col=0)["ffr_eq_q4"]
    fr = {"10-yr": S.rg10, "BBB spread": S.rbbbp, "Equities (ln CAPE)": -S.req, "Dollar (ln real)": S.fpxr, "Oil (ln real)": S.poil, "Fed funds": 0.0}
    a2.bar(x + 0.2, [fr[n] for n in names], 0.4, label="FRB/US weights (q4)", color="#d62728")
    a2.set_xticks(x); a2.set_xticklabels(names, rotation=15, fontsize=8); a2.axhline(0, color="gray", lw=0.6)
    a2.set_ylabel("pp per unit (pp, or per 1% for CAPE, dollar, oil)"); a2.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, f"path_fci_{sample}.png"), dpi=130)


if __name__ == "__main__":
    main()
