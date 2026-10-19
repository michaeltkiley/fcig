"""
Alternatives to the baseline target/path surprises, run through the same monthly local projection as lp_surprises.py
(month-end values, h = 0..12, 3 lags of the monthly FCI change and of the shocks as controls, HAC errors, per +25 bp).

  swanson   Three factors in the spirit of Swanson (2021): federal funds rate (FFR), forward guidance (FG) and large-scale
            asset purchases (LSAP). Principal components of the event-window changes in MP1, MP2, ED2, ED3, ED4 and the
            2-, 5- and 10-year Treasury yields, rotated so that (i) FG and LSAP have no loading on MP1, and (ii) LSAP is the
            direction with the smallest variance before the zero lower bound (no asset purchases then). Scaling: FFR = 1 pp
            on MP1, FG = 1 pp on ED4, LSAP = 1 pp on the 10-year yield. This is a reconstruction from the paper's
            description, not his code; the loadings are printed so the factors can be checked.
  ns        Nakamura and Steinsson (2018) "policy news": the first principal component of MP1, MP2, ED2, ED3 and ED4,
            scaled so that a unit is a 1 pp move in the 2-year yield (USMPD has no 1-year Treasury series, which they use).
  raw2y     The raw 2-year Treasury yield change in the FOMC window (USMPD UST2Y).
Each is a single regressor except swanson (three regressors together). Baseline target and path are included for comparison.

Usage:  python analysis/lp_alt.py [path/to/USMPD.xlsx]
Outputs: analysis/lp_alt_results.csv and analysis/lp_alt_*.png
"""
import os, sys
import numpy as np, pandas as pd

import lp_surprises as L

HERE = L.HERE
FUT = ["MP1", "MP2", "ED2", "ED3", "ED4"]
YLD = ["UST2Y", "UST5Y", "UST10Y"]
PRE_ZLB_END = pd.Timestamp("2008-12-16")


def swanson(d):
    cols = FUT + YLD
    X = d[cols].values
    U, S, Vt = np.linalg.svd(X, full_matrices=False)
    F, Lm = U[:, :3] * S[:3], Vt[:3].T
    # (i) Householder rotation so the MP1 row of the loadings is (r, 0, 0): factors 2 and 3 do not move MP1
    l = Lm[0]
    v = l / np.linalg.norm(l) - np.array([1.0, 0, 0])
    Q = np.eye(3) if np.allclose(v, 0) else np.eye(3) - 2 * np.outer(v, v) / (v @ v)
    F, Lm = F @ Q, Lm @ Q
    # (ii) within factors 2 and 3, LSAP is the smallest-variance direction before the ZLB
    pre = (d["Date"] < PRE_ZLB_END).values
    w, E = np.linalg.eigh(np.cov(F[pre, 1:].T))     # ascending: column 0 = smallest variance
    R = E[:, ::-1]                                   # column 0 = FG (largest), column 1 = LSAP (smallest)
    F[:, 1:], Lm[:, 1:] = F[:, 1:] @ R, Lm[:, 1:] @ R
    out = d[["Date"]].copy()
    out["swanson_ffr"] = F[:, 0] * Lm[cols.index("MP1"), 0]
    out["swanson_fg"] = F[:, 1] * Lm[cols.index("ED4"), 1]
    out["swanson_lsap"] = F[:, 2] * Lm[cols.index("UST10Y"), 2]
    scaled = pd.DataFrame({"FFR": Lm[:, 0] / Lm[cols.index("MP1"), 0], "FG": Lm[:, 1] / Lm[cols.index("ED4"), 1],
                           "LSAP": Lm[:, 2] / Lm[cols.index("UST10Y"), 2]}, index=cols)
    return out, scaled, 1 - ((X - F @ Lm.T) ** 2).sum() / (X ** 2).sum()


def ns(d):
    X = d[FUT].values
    U, S, Vt = np.linalg.svd(X, full_matrices=False)
    f = U[:, 0] * S[0]
    slope = (f @ d["UST2Y"].values) / (f @ f)        # unit = 1 pp on the 2-year yield
    return f * slope


def main():
    d = L.usmpd(sys.argv[1] if len(sys.argv) > 1 else None)
    base, *_ = L.factors(d, "orth")
    sw, load, fit = swanson(d)
    ev = base.merge(sw, on="Date")
    ev["ns"] = ns(d)
    ev["raw2y"] = d["UST2Y"].values
    print(f"{len(ev)} events; Swanson three factors explain {fit:.1%} of the variance. Loadings (per unit of own scaling):")
    print(load.round(2).to_string())
    print("\ncorrelation across events:\n", ev.drop(columns="Date").corr().round(2).to_string())

    y = L.monthly_y()
    shocks = ["target", "path", "swanson_ffr", "swanson_fg", "swanson_lsap", "ns", "raw2y"]
    s = ev.assign(m=ev.Date.dt.to_period("M")).groupby("m")[shocks].sum().reindex(y.index).fillna(0.0)
    s = s[s.index >= "1994-01"]
    y = y.loc[s.index]
    last_full = y.index[-1] - 1 if pd.Timestamp.today().to_period("M") == y.index[-1] else y.index[-1]
    y, s = y.loc[:last_full], s.loc[:last_full]
    zlb = pd.Series(False, index=y.index)
    for a, b in L.ZLB:
        zlb |= (y.index >= pd.Period(a, "M")) & (y.index <= pd.Period(b, "M"))

    specs = {"baseline": ["target", "path"], "swanson": ["swanson_ffr", "swanson_fg", "swanson_lsap"], "ns": ["ns"], "raw2y": ["raw2y"]}
    parts = []
    for smp, mask in (("full", None), ("ex-ZLB", ~zlb)):
        for spec, cols in specs.items():
            r = L.lp(y, s[cols], mask).assign(sample=smp, spec=spec)
            r["coef"] *= 0.25
            r["se"] *= 0.25
            parts.append(r)
    res = pd.concat(parts)
    res.to_csv(os.path.join(HERE, "lp_alt_results.csv"), index=False, float_format="%.5f")

    for smp in ("full", "ex-ZLB"):
        print(f"\nFCI response per +25 bp, {smp} (index points; t-stat):")
        for spec, cols in specs.items():
            for sh in cols:
                r = res[(res["sample"] == smp) & (res.spec == spec) & (res.series == "fci") & (res.shock == sh) & res.h.isin([0, 3, 6, 9, 12])]
                print(f"  {sh:13s}", "  ".join(f"h={int(h)}: {c:+.2f} ({c / e:+.1f})" for h, c, e in zip(r.h, r.coef, r.se)))
    tag = lambda smp: smp.replace("-", "").lower()
    plot_fci(res)
    for smp in ("full", "ex-ZLB"):
        plot_grid(res[res.spec == "swanson"], ["swanson_ffr", "swanson_fg", "swanson_lsap"], smp, f"lp_alt_swanson_{tag(smp)}.png",
                  {"swanson_ffr": "Swanson FFR", "swanson_fg": "Swanson FG", "swanson_lsap": "Swanson LSAP"})
        plot_grid(res[res.spec.isin(["ns", "raw2y"])], ["ns", "raw2y"], smp, f"lp_alt_single_{tag(smp)}.png",
                  {"ns": "Nakamura-Steinsson", "raw2y": "Raw 2-yr change"})


def plot_fci(res, name="lp_alt_fci.png", main_title="GS FCI response per +25 bp (90% HAC bands)", unit="index points"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    panels = [("FFR / target", ["target", "swanson_ffr"]), ("Path / forward guidance", ["path", "swanson_fg"]),
              ("Asset purchases", ["swanson_lsap"]), ("Single shock", ["ns", "raw2y"])]
    names = {"target": "baseline target", "path": "baseline path", "swanson_ffr": "Swanson FFR", "swanson_fg": "Swanson FG",
             "swanson_lsap": "Swanson LSAP", "ns": "Nakamura-Steinsson", "raw2y": "raw 2-yr change"}
    col = ["#1f77b4", "#d62728"]
    fig, ax = plt.subplots(2, 4, figsize=(15, 6.5), sharex=True)
    for i, smp in enumerate(("full", "ex-ZLB")):
        for j, (title, shs) in enumerate(panels):
            a = ax[i, j]
            for k, sh in enumerate(shs):
                r = res[(res["sample"] == smp) & (res.series == "fci") & (res.shock == sh)].set_index("h")
                c = col[k]
                a.fill_between(r.index, r.coef - 1.645 * r.se, r.coef + 1.645 * r.se, color=c, alpha=0.13, lw=0)
                a.plot(r.index, r.coef, "-o", color=c, ms=3, lw=1.5, label=names[sh])
            a.axhline(0, color="k", lw=0.6)
            a.set_title(f"{title} - {smp}", fontsize=9, loc="left")
            a.legend(fontsize=7, frameon=False)
            if j == 0:
                a.set_ylabel(unit)
    for a in ax[-1]:
        a.set_xlabel("months after the meeting month (h)")
    fig.suptitle(main_title, fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(os.path.join(HERE, name), dpi=130)


def plot_grid(res, shocks, smp, name, label, series=None, series_label=None, unit="index points"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    series = series or ["fci"] + L.COMP
    series_label = series_label or L.LABEL
    fig, ax = plt.subplots(len(series), len(shocks), figsize=(3.9 * len(shocks) + 1, 2 * len(series)), sharex=True, squeeze=False)
    for j, sh in enumerate(shocks):
        for i, v in enumerate(series):
            a = ax[i, j]
            b = res[(res["sample"] == smp) & (res.shock == sh) & (res.series == v)].set_index("h")
            a.fill_between(b.index, b.coef - 1.645 * b.se, b.coef + 1.645 * b.se, color="#1f77b4", alpha=0.15, lw=0)
            a.fill_between(b.index, b.coef - b.se, b.coef + b.se, color="#1f77b4", alpha=0.30, lw=0)
            a.plot(b.index, b.coef, "-o", color="#1f77b4", ms=3, lw=1.5)
            a.axhline(0, color="k", lw=0.6)
            a.set_title(f"{series_label[v]} - {label[sh]}", fontsize=9, loc="left")
            if j == 0:
                a.set_ylabel(unit)
    for a in ax[-1]:
        a.set_xlabel("months after the meeting month (h)")
    fig.suptitle(f"{smp}: response per +25 bp; bands are 68% (dark) and 90% (light), HAC", fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.985))
    fig.savefig(os.path.join(HERE, name), dpi=125)


if __name__ == "__main__":
    main()
