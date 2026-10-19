"""
Local projections of the Goldman-style FCI (and its five contributions) on FOMC target and path surprises.

Surprises: SF Fed US Monetary Policy Event-Study Database (USMPD, "Monetary Events" sheet, 1994 on; Acosta, Ajello,
Bauer, Loria and Miranda-Agrippino 2025). The database holds raw market surprises, so the two shocks are built here.
Unscheduled events with MP1 == 0 are dropped, as in michaeltkiley/monetary_policy_surprises.
  orth (baseline): target = MP1, the current-meeting fed funds surprise; path = the part of the ED4 surprise (the rate
      about a year ahead) not explained by MP1. Uncorrelated with the target by construction. Units: percentage points.
  gss (robustness): Gurkaynak, Sack and Swanson (2005): first two principal components of (MP1, MP2, ED2, ED3, ED4),
      rotated so the second does not move MP1. Target = 1 pp on MP1, path = 1 pp on ED4. In this sample the rotated
      target also lowers ED4 (loading -0.2) and the two factors are correlated (0.5), so its target coefficient is
      conditional on a path that moves in the opposite direction from the usual co-movement.

Regression (monthly, month-end values):
    y_{t+h} - y_{t-1} = a_h + b_h^target * target_t + b_h^path * path_t
                        + controls (3 lags of the monthly change in the FCI and of both surprises) + e,   h = 0..12
where target_t and path_t are the sums of event surprises in calendar month t (zero in months without a meeting) and y is
the last trading day's value of the FCI or of one component's contribution. Contributions sum to the index, so the
component responses sum to the FCI response exactly. Newey-West (HAC) standard errors, 12 lags. Higher FCI = tighter.

Needs statsmodels, matplotlib and openpyxl (not in requirements.txt: the daily workflow does not run this).
Usage:  python analysis/lp_surprises.py [path/to/USMPD.xlsx]    (downloads it to raw/ if no path is given)
Outputs: analysis/lp_results.csv, analysis/lp_irf.png (orth), analysis/lp_irf_gss.png
"""
import os, sys, urllib.request
import numpy as np, pandas as pd
import statsmodels.api as sm

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
URL = "https://www.frbsf.org/wp-content/uploads/USMPD.xlsx"
H = 12
LAGS = 3
COMP = ["c_ffr", "c_y10", "c_bbb", "c_cape", "c_usd"]
LABEL = {"fci": "GS FCI", "c_ffr": "Fed funds", "c_y10": "10-yr", "c_bbb": "BBB spread", "c_cape": "Equity (CAPE)", "c_usd": "Dollar"}
ZLB = [("2008-12-16", "2015-12-16"), ("2020-03-15", "2022-03-16")]  # same eras as the surprise repo


def usmpd(path=None):
    if path is None:
        path = os.path.join(ROOT, "raw", "USMPD.xlsx")
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
            open(path, "wb").write(urllib.request.urlopen(req, timeout=60).read())
    d = pd.read_excel(path, sheet_name="Monetary Events")
    d = d[~((d["Unscheduled"] == 1) & (d["MP1"] == 0))]
    return d.dropna(subset=["MP1", "MP2", "ED2", "ED3", "ED4"]).reset_index(drop=True)


def factors(d, method="orth"):
    """Target and path, in percentage points: the events with two columns (and, for gss, loadings and fit)."""
    if method == "orth":
        slope, icpt = np.polyfit(d["MP1"], d["ED4"], 1)
        out = d[["Date"]].copy()
        out["target"], out["path"] = d["MP1"].values, (d["ED4"] - icpt - slope * d["MP1"]).values
        return out, {"ED4 on MP1 slope": slope}, None, None
    cols = ["MP1", "MP2", "ED2", "ED3", "ED4"]
    X = d[cols].values
    U, S, Vt = np.linalg.svd(X, full_matrices=False)
    F, L = U[:, :2] * S[:2], Vt[:2].T  # X ~ F @ L.T
    # rotate so factor 2 has zero loading on MP1: Q maps (L row of MP1) to (a, 0)
    a, b = L[0]
    Q = np.array([[a, -b], [b, a]]) / np.hypot(a, b)
    F, L = F @ Q, L @ Q
    if L[0, 0] < 0:
        F[:, 0], L[:, 0] = -F[:, 0], -L[:, 0]
    if L[4, 1] < 0:
        F[:, 1], L[:, 1] = -F[:, 1], -L[:, 1]
    tgt = F[:, 0] * L[0, 0]           # unit = 1 pp on MP1
    pth = F[:, 1] * L[4, 1]           # unit = 1 pp on ED4
    out = d[["Date"]].copy()
    out["target"], out["path"] = tgt, pth
    fit = 1 - ((X - F @ L.T) ** 2).sum() / (X ** 2).sum()
    return out, dict(zip(cols, L[:, 0] / L[0, 0])), dict(zip(cols, L[:, 1] / L[4, 1])), fit


def monthly_y():
    g = pd.read_csv(os.path.join(ROOT, "fcig_gs_daily.csv"), parse_dates=["date"]).set_index("date")
    y = g[["fci"] + COMP]
    return y.groupby(y.index.to_period("M")).last()   # month-end values


def lp(y, s, mask=None, future=False):
    """Returns tidy rows for every series in y and every shock (column of s). With future=True, the sums of the target and path
    surprises over months t+1..t+h are added as controls, so the response holds later surprises at zero."""
    rows = []
    X0 = s.copy()
    dy = y["fci"].diff()
    for v in y.columns:
        for h in range(H + 1):
            lhs = y[v].shift(-h) - y[v].shift(1)
            X = X0.copy()
            for k in range(1, LAGS + 1):
                X[f"dy{k}"] = dy.shift(k)
                for c in s.columns:
                    X[f"{c}_l{k}"] = s[c].shift(k)
            if future and h > 0:
                X["fut_target"] = sum(s["target"].shift(-k) for k in range(1, h + 1))
                X["fut_path"] = sum(s["path"].shift(-k) for k in range(1, h + 1))
            df = pd.concat([lhs.rename("lhs"), X], axis=1).dropna()
            if mask is not None:
                df = df[mask.reindex(df.index).fillna(False)]
            m = sm.OLS(df["lhs"], sm.add_constant(df.drop(columns="lhs"))).fit(cov_type="HAC", cov_kwds={"maxlags": 12})
            for sh in s.columns:
                rows.append(dict(series=v, shock=sh, h=h, coef=m.params[sh], se=m.bse[sh], n=int(m.nobs)))
    return pd.DataFrame(rows)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else None
    d = usmpd(path)
    y = monthly_y()
    parts = []
    for method in ("orth", "gss"):
        ev, a, b, fit = factors(d, method)
        print(f"\n[{method}] {len(ev)} events {ev.Date.min().date()} to {ev.Date.max().date()}", a if b is None else
              f"| two factors explain {fit:.1%}; target loadings { {k: round(v, 2) for k, v in a.items()} }; path loadings { {k: round(v, 2) for k, v in b.items()} }")
        s = ev.assign(m=ev.Date.dt.to_period("M")).groupby("m")[["target", "path"]].sum().reindex(y.index).fillna(0.0)
        s = s[s.index >= "1994-01"]
        yy = y.loc[s.index]
        # drop the current, incomplete month so every y is a month-end value
        last_full = yy.index[-1] - 1 if pd.Timestamp.today().to_period("M") == yy.index[-1] else yy.index[-1]
        yy, s = yy.loc[:last_full], s.loc[:last_full]
        zlb = pd.Series(False, index=yy.index)
        for a_, b_ in ZLB:
            zlb |= (yy.index >= pd.Period(a_, "M")) & (yy.index <= pd.Period(b_, "M"))
        for smp, mask in (("full", None), ("ex-ZLB", ~zlb)):
            for spec in (("base", "future") if method == "orth" else ("base",)):
                r = lp(yy, s, mask, future=(spec == "future")).assign(sample=smp, factors=method, spec=spec)
                r["coef"] *= 0.25   # per +25 bp
                r["se"] *= 0.25
                parts.append(r)
    res = pd.concat(parts)
    res.to_csv(os.path.join(HERE, "lp_results.csv"), index=False, float_format="%.5f")
    chk = res.pivot_table(index=["factors", "spec", "sample", "shock", "h"], columns="series", values="coef")
    print("\nmax |sum of components - FCI| =", float((chk[COMP].sum(axis=1) - chk["fci"]).abs().max()))
    for method in ("orth", "gss"):
        for smp in ("full", "ex-ZLB"):
            print(f"\nFCI response per +25 bp, {method}, {smp} (index points; t-stat):")
            for sh in ("target", "path"):
                r = res[(res.factors == method) & (res.spec == "base") & (res["sample"] == smp) & (res.series == "fci") & (res.shock == sh) & res.h.isin([0, 3, 6, 9, 12])]
                print(f"  {sh:6s}", "  ".join(f"h={int(h)}: {c:+.2f} ({c / e:+.1f})" for h, c, e in zip(r.h, r.coef, r.se)))
    for smp in ("full", "ex-ZLB"):
        print(f"\nFCI response per +25 bp, orth, {smp}, controlling for later surprises (index points; t-stat):")
        for sh in ("target", "path"):
            r = res[(res.factors == "orth") & (res.spec == "future") & (res["sample"] == smp) & (res.series == "fci") & (res.shock == sh) & res.h.isin([0, 3, 6, 9, 12])]
            print(f"  {sh:6s}", "  ".join(f"h={int(h)}: {c:+.2f} ({c / e:+.1f})" for h, c, e in zip(r.h, r.coef, r.se)))
    plot(res[(res.factors == "orth") & (res.spec == "base")], "lp_irf.png")
    plot(res[(res.factors == "gss") & (res.spec == "base")], "lp_irf_gss.png")
    for smp in ("full", "ex-ZLB"):
        plot_ci(res[res.factors == "orth"], smp, f"lp_ci_{smp.replace('-', '').lower()}.png")


def plot(res, name):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    pal = {"c_ffr": "#7f7f7f", "c_y10": "#1f77b4", "c_bbb": "#d62728", "c_cape": "#2ca02c", "c_usd": "#9467bd"}
    fig, ax = plt.subplots(2, 2, figsize=(11, 7), sharex=True)
    for j, sh in enumerate(("target", "path")):
        for i, smp in enumerate(("full", "ex-ZLB")):
            a = ax[i, j]
            r = res[(res["sample"] == smp) & (res.shock == sh)]
            P = r.pivot_table(index="h", columns="series", values="coef")
            pos, neg = np.zeros(len(P)), np.zeros(len(P))
            for c in COMP:
                v = P[c].values
                lo = np.where(v >= 0, pos, neg)
                a.bar(P.index, v, bottom=lo, color=pal[c], width=0.8, label=LABEL[c])
                pos, neg = pos + np.clip(v, 0, None), neg + np.clip(v, None, 0)
            f = r[r.series == "fci"].set_index("h")
            a.plot(f.index, f.coef, "k-o", ms=3, lw=1.6, label="FCI")
            a.fill_between(f.index, f.coef - 1.645 * f.se, f.coef + 1.645 * f.se, color="k", alpha=0.12, lw=0)
            a.axhline(0, color="k", lw=0.6)
            a.set_title(f"{sh.capitalize()} surprise, {smp} (per +25 bp; 90% band)", fontsize=10)
            a.set_ylabel("index points")
    for a in ax[1]:
        a.set_xlabel("months after the meeting month (h)")
    ax[0, 0].legend(fontsize=8, ncol=2, frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, name), dpi=140)




def plot_ci(res, smp, name):
    """FCI and each contribution, one panel each, target (left) and path (right): the baseline response with 68% and 90%
    bands, and the response controlling for later surprises (dashed, no band)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    series = ["fci"] + COMP
    fig, ax = plt.subplots(len(series), 2, figsize=(10, 12), sharex=True)
    for j, sh in enumerate(("target", "path")):
        for i, v in enumerate(series):
            a = ax[i, j]
            b = res[(res["sample"] == smp) & (res.shock == sh) & (res.series == v) & (res.spec == "base")].set_index("h")
            f = res[(res["sample"] == smp) & (res.shock == sh) & (res.series == v) & (res.spec == "future")].set_index("h")
            a.fill_between(b.index, b.coef - 1.645 * b.se, b.coef + 1.645 * b.se, color="#1f77b4", alpha=0.15, lw=0)
            a.fill_between(b.index, b.coef - b.se, b.coef + b.se, color="#1f77b4", alpha=0.30, lw=0)
            a.plot(b.index, b.coef, "-o", color="#1f77b4", ms=3, lw=1.6, label="baseline")
            a.plot(f.index, f.coef, "--", color="#d62728", lw=1.3, label="controlling for later surprises")
            a.axhline(0, color="k", lw=0.6)
            a.set_title(f"{LABEL[v]} - {sh}", fontsize=9, loc="left")
            if j == 0:
                a.set_ylabel("index points")
    for a in ax[-1]:
        a.set_xlabel("months after the meeting month (h)")
    ax[0, 0].legend(fontsize=7, frameon=False, loc="lower left")
    fig.suptitle(f"{smp}: response per +25 bp surprise; bands are 68% (dark) and 90% (light), HAC", fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.985))
    fig.savefig(os.path.join(HERE, name), dpi=130)


if __name__ == "__main__":
    main()
