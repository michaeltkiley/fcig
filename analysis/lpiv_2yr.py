"""
Local-projection IV: response of the Goldman-style FCI and its five contributions to a monthly change in the 2-year
Treasury yield, instrumented by the FOMC target and path surprises (see lp_surprises.py for how those are built).

    y_{t+h} - y_{t-1} = a_h + b_h * d2y_t + controls + e_h,     d2y_t = 2y(t) - 2y(t-1), month-end values, h = 0..12
    d2y_t instrumented by target_t and path_t (the sums of event surprises in calendar month t).

Same controls as lp_surprises.py (3 lags of the monthly change in the FCI and of both surprises), the same controls for
every y, so the component responses sum to the FCI response. 2SLS with Newey-West (Bartlett, 13 lags) standard errors.
Coefficients are per +25 bp in the 2-year yield. Higher FCI = tighter. First-stage strength and the over-identification
test are reported; the ZLB eras pin the 2-year, so the ex-ZLB sample is the cleaner one.

Needs linearmodels (plus what lp_surprises.py needs).
Usage:  python analysis/lpiv_2yr.py [path/to/USMPD.xlsx]
Outputs: analysis/lpiv_results.csv, analysis/lpiv_irf.png
"""
import os, sys
import numpy as np, pandas as pd
from linearmodels.iv import IV2SLS

import lp_surprises as L
from fcig_replicate import fetch

HERE, ROOT = L.HERE, L.ROOT


def dgs2():
    p = os.path.join(ROOT, "raw", "DGS2.csv")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    body = fetch("https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS2")
    if body is not None:
        open(p, "wb").write(body)
    elif not os.path.exists(p):
        raise SystemExit("could not download FRED DGS2")
    else:
        print("  DGS2 download failed, using saved file")
    d = pd.read_csv(p, na_values=["."])
    s = pd.Series(d.iloc[:, 1].values, index=pd.to_datetime(d.iloc[:, 0]), dtype=float).dropna()
    return s.groupby(s.index.to_period("M")).last()


def lpiv(y, s, x, instruments, mask=None):
    rows, diag = [], []
    dy = y["fci"].diff()
    for h in range(L.H + 1):
        base = pd.DataFrame({"x": x})
        for k in range(1, L.LAGS + 1):
            base[f"dy{k}"] = dy.shift(k)
            base[f"t{k}"], base[f"p{k}"] = s["target"].shift(k), s["path"].shift(k)
        base[["target", "path"]] = s[["target", "path"]]
        lhs = pd.concat({v: y[v].shift(-h) - y[v].shift(1) for v in y.columns}, axis=1)
        df = pd.concat([lhs, base], axis=1).dropna()
        if mask is not None:
            df = df[mask.reindex(df.index).fillna(False)]
        exog = df[[c for c in df.columns if c not in list(y.columns) + ["x", "target", "path"]]].assign(const=1.0)
        for v in y.columns:
            r = IV2SLS(df[v], exog, df[["x"]], df[instruments]).fit(cov_type="kernel", kernel="bartlett", bandwidth=13)
            rows.append(dict(series=v, h=h, coef=r.params["x"], se=r.std_errors["x"], n=int(r.nobs)))
        fs = r.first_stage.diagnostics.loc["x"]
        diag.append(dict(h=h, first_stage_F=float(fs["f.stat"]), n=int(r.nobs),
                         J_p=float(r.wooldridge_overid.pval) if len(instruments) > 1 else np.nan))
    return pd.DataFrame(rows), pd.DataFrame(diag)


def main():
    d = L.usmpd(sys.argv[1] if len(sys.argv) > 1 else None)
    y = L.monthly_y()
    ev, *_ = L.factors(d, "orth")
    s = ev.assign(m=ev.Date.dt.to_period("M")).groupby("m")[["target", "path"]].sum().reindex(y.index).fillna(0.0)
    s = s[s.index >= "1994-01"]
    y = y.loc[s.index]
    last_full = y.index[-1] - 1 if pd.Timestamp.today().to_period("M") == y.index[-1] else y.index[-1]
    y, s = y.loc[:last_full], s.loc[:last_full]
    two = dgs2().reindex(y.index)
    x = two.diff()
    zlb = pd.Series(False, index=y.index)
    for a, b in L.ZLB:
        zlb |= (y.index >= pd.Period(a, "M")) & (y.index <= pd.Period(b, "M"))

    out, dg = [], []
    for smp, mask in (("full", None), ("ex-ZLB", ~zlb)):
        for name, inst in (("target+path", ["target", "path"]), ("target", ["target"]), ("path", ["path"])):
            r, g = lpiv(y, s, x, inst, mask)
            r["coef"] *= 0.25   # per +25 bp in the 2-year yield
            r["se"] *= 0.25
            out.append(r.assign(sample=smp, instruments=name))
            dg.append(g.assign(sample=smp, instruments=name))
    res, diag = pd.concat(out), pd.concat(dg)
    res.to_csv(os.path.join(HERE, "lpiv_results.csv"), index=False, float_format="%.5f")

    chk = res.pivot_table(index=["sample", "instruments", "h"], columns="series", values="coef")
    print("max |sum of components - FCI| =", float((chk[L.COMP].sum(axis=1) - chk["fci"]).abs().max()))
    print("\nFirst-stage F (robust) and over-identification p-value (Wooldridge) at h=0, 6, 12:")
    for (smp, inst), g in diag.groupby(["sample", "instruments"]):
        g = g.set_index("h")
        print(f"  {smp:7s} {inst:12s} F={g.loc[0, 'first_stage_F']:.1f} n={int(g.loc[0, 'n'])}"
              + (f"  overid p at h=0/6/12: {g.loc[0, 'J_p']:.2f}/{g.loc[6, 'J_p']:.2f}/{g.loc[12, 'J_p']:.2f}" if inst == "target+path" else ""))
    print("\nFCI response per +25 bp in the 2-year yield (index points; t-stat):")
    for smp in ("full", "ex-ZLB"):
        for inst in ("target+path", "target", "path"):
            r = res[(res["sample"] == smp) & (res.instruments == inst) & (res.series == "fci") & res.h.isin([0, 3, 6, 9, 12])]
            print(f"  {smp:7s} {inst:12s}", "  ".join(f"h={int(h)}: {c:+.2f} ({c / e:+.1f})" for h, c, e in zip(r.h, r.coef, r.se)))
    plot(res[res.instruments == "target+path"])


def plot(res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    pal = {"c_ffr": "#7f7f7f", "c_y10": "#1f77b4", "c_bbb": "#d62728", "c_cape": "#2ca02c", "c_usd": "#9467bd"}
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2), sharex=True)
    for a, smp in zip(ax, ("full", "ex-ZLB")):
        r = res[res["sample"] == smp]
        P = r.pivot_table(index="h", columns="series", values="coef")
        pos, neg = np.zeros(len(P)), np.zeros(len(P))
        for c in L.COMP:
            v = P[c].values
            a.bar(P.index, v, bottom=np.where(v >= 0, pos, neg), color=pal[c], width=0.8, label=L.LABEL[c])
            pos, neg = pos + np.clip(v, 0, None), neg + np.clip(v, None, 0)
        f = r[r.series == "fci"].set_index("h")
        a.plot(f.index, f.coef, "k-o", ms=3, lw=1.6, label="FCI")
        a.fill_between(f.index, f.coef - 1.645 * f.se, f.coef + 1.645 * f.se, color="k", alpha=0.12, lw=0)
        a.axhline(0, color="k", lw=0.6)
        a.set_title(f"{smp}: per +25 bp in the 2-yr yield (IV: target + path; 90% band)", fontsize=10)
        a.set_xlabel("months after the meeting month (h)")
    ax[0].set_ylabel("index points")
    ax[0].legend(fontsize=8, ncol=2, frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "lpiv_irf.png"), dpi=140)


if __name__ == "__main__":
    main()
