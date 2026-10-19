"""
Goldman-style FCI against the replicated Fed FCI-G (3-year and 1-year lookbacks) in standardized units.

Shocks (monthly sums of event surprises, as in lp_alt.py): baseline path (estimated with target), Swanson forward guidance
(estimated with the Swanson FFR and LSAP factors), Nakamura-Steinsson policy news, and the raw 2-year change in the FOMC
window.  Each coefficient is scaled to
    shock:   per 1 standard deviation of that monthly shock (sd over the 1994 to latest-month sample, zeros included)
    outcome: in standard deviations of the index LEVEL over the same sample (GS index: 1.02 points; FCI-G: 0.58 pp (3-year) and 0.55 pp (1-year)).
Contributions are divided by the same outcome sd as their total, so they still sum to it. The components are matched as
FFR, 10-year, BBB, equity (GS: CAPE contribution; Fed: stock market) and dollar. The mortgage rate and house prices exist only
in the Fed index and are shown separately.

Usage:  python analysis/lp_compare.py [path/to/USMPD.xlsx]
Outputs: analysis/lp_compare_results.csv, lp_compare_total_{full,exzlb}.png, lp_compare_contrib_{full,exzlb}.png
"""
import os, sys
import numpy as np, pandas as pd

import lp_surprises as L
import lp_alt as A
import lp_fed as F

HERE = L.HERE
SPECS = {"baseline": ["target", "path"], "swanson": ["swanson_ffr", "swanson_fg", "swanson_lsap"], "ns": ["ns"], "raw2y": ["raw2y"]}
SHOCKS = [("baseline", "path", "Baseline path"), ("swanson", "swanson_fg", "Swanson forward guidance"),
          ("ns", "ns", "Nakamura-Steinsson"), ("raw2y", "raw2y", "Raw 2-year change")]
# common component names -> column in each index
GSMAP = {"FFR": "c_ffr", "10-yr": "c_y10", "BBB": "c_bbb", "Equity": "c_cape", "Dollar": "c_usd"}
FEDMAP = {"FFR": "FFR", "10-yr": "10Yr Treasury", "BBB": "BBB", "Equity": "Stock Market", "Dollar": "Dollar"}
FEDONLY = {"Mortgage": "Mortgage Rate", "Houses": "House Prices"}
COMMON = list(GSMAP)
COLORS = {"FFR": "#7f7f7f", "10-yr": "#1f77b4", "Mortgage": "#9ecae1", "BBB": "#d62728", "Equity": "#2ca02c", "Dollar": "#9467bd", "Houses": "#8c564b"}
H = [0, 3, 6, 9, 12]


def main():
    d = L.usmpd(sys.argv[1] if len(sys.argv) > 1 else None)
    base, *_ = L.factors(d, "orth")
    sw, *_ = A.swanson(d)
    ev = base.merge(sw, on="Date")
    ev["ns"] = A.ns(d)
    ev["raw2y"] = d["UST2Y"].values
    allsh = ["target", "path", "swanson_ffr", "swanson_fg", "swanson_lsap", "ns", "raw2y"]

    indices = {"GS FCI": L.monthly_y().rename(columns={v: k for k, v in GSMAP.items()}).rename(columns={"fci": "fci"})}
    gs = L.monthly_y()
    indices = {"GS FCI": gs.rename(columns={v: k for k, v in GSMAP.items()}),
               "Fed FCI-G (3yr)": F.fed_monthly("3yr").rename(columns={v: k for k, v in {**FEDMAP, **FEDONLY}.items()}),
               "Fed FCI-G (1yr)": F.fed_monthly("1yr").rename(columns={v: k for k, v in {**FEDMAP, **FEDONLY}.items()})}

    parts, sds = [], []
    sd_shock = None
    for name, y in indices.items():
        s = ev.assign(m=ev.Date.dt.to_period("M")).groupby("m")[allsh].sum().reindex(y.index).fillna(0.0)
        s = s[s.index >= "1994-01"]
        y = y.loc[s.index]
        last_full = y.index[-1] - 1 if pd.Timestamp.today().to_period("M") == y.index[-1] else y.index[-1]
        y, s = y.loc[:last_full], s.loc[:last_full]
        if sd_shock is None:
            sd_shock = s.std()
        sd_y = float(y["fci"].std())
        sds.append((name, sd_y))
        zlb = pd.Series(False, index=y.index)
        for a, b in L.ZLB:
            zlb |= (y.index >= pd.Period(a, "M")) & (y.index <= pd.Period(b, "M"))
        z = s / sd_shock                                   # per 1 sd of the shock
        for smp, mask in (("full", None), ("ex-ZLB", ~zlb)):
            for spec, cols in SPECS.items():
                r = L.lp(y, z[cols], mask)
                r = r[r.shock.isin([sh for sp, sh, _ in SHOCKS if sp == spec])]
                r["coef"] /= sd_y                          # in sd of the index level
                r["se"] /= sd_y
                parts.append(r.assign(index=name, sample=smp, spec=spec))
    res = pd.concat(parts)
    res.to_csv(os.path.join(HERE, "lp_compare_results.csv"), index=False, float_format="%.5f")

    print("sd of the index level (units of the outcome):", {n: round(v, 3) for n, v in sds})
    print("sd of each monthly shock (pp):", {k: round(float(v), 3) for k, v in sd_shock.items() if k in ("path", "swanson_fg", "ns", "raw2y")})
    names = list(indices)
    for smp in ("full", "ex-ZLB"):
        print(f"\nResponse of the index in index-sd per 1-sd shock, {smp} (t-stat):")
        for spec, sh, lab in SHOCKS:
            for n in names:
                r = res[(res["sample"] == smp) & (res.spec == spec) & (res.shock == sh) & (res.series == "fci") & (res["index"] == n) & res.h.isin(H)]
                print(f"  {lab:26s} {n:16s}", "  ".join(f"h={int(h)}: {c:+.2f} ({c / e:+.1f})" for h, c, e in zip(r.h, r.coef, r.se)))
    print("\nContributions at h=12, full sample, index-sd per 1-sd shock (GS | Fed 3yr):")
    for spec, sh, lab in SHOCKS:
        row = []
        for comp in COMMON + list(FEDONLY):
            g = res[(res["sample"] == "full") & (res.spec == spec) & (res.shock == sh) & (res.h == 12) & (res.series == comp) & (res["index"] == "GS FCI")].coef
            f_ = res[(res["sample"] == "full") & (res.spec == spec) & (res.shock == sh) & (res.h == 12) & (res.series == comp) & (res["index"] == "Fed FCI-G (3yr)")].coef
            row.append(f"{comp} {g.iloc[0]:+.2f}|{f_.iloc[0]:+.2f}" if len(g) else f"{comp}  -  |{f_.iloc[0]:+.2f}")
        print(f"  {lab:26s}", "  ".join(row))
    tag = lambda smp: smp.replace("-", "").lower()
    for smp in ("full", "ex-ZLB"):
        plot_total(res, smp, f"lp_compare_total_{tag(smp)}.png")
        plot_contrib(res, smp, f"lp_compare_contrib_{tag(smp)}.png")


def plot_total(res, smp, name):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    col = {"GS FCI": "#1f77b4", "Fed FCI-G (3yr)": "#d62728", "Fed FCI-G (1yr)": "#ff7f0e"}
    fig, ax = plt.subplots(1, 4, figsize=(15, 3.8), sharex=True, sharey=True)
    for a, (spec, sh, lab) in zip(ax, SHOCKS):
        for n, c in col.items():
            r = res[(res["sample"] == smp) & (res.spec == spec) & (res.shock == sh) & (res.series == "fci") & (res["index"] == n)].set_index("h")
            if n != "Fed FCI-G (1yr)":
                a.fill_between(r.index, r.coef - 1.645 * r.se, r.coef + 1.645 * r.se, color=c, alpha=0.12, lw=0)
            a.plot(r.index, r.coef, marker="o", color=c, ms=3, lw=1.5 if n != "Fed FCI-G (1yr)" else 1.0,
                   ls="-" if n != "Fed FCI-G (1yr)" else "--", label=n)
        a.axhline(0, color="k", lw=0.6)
        a.set_title(lab, fontsize=10)
        a.set_xlabel("months after the meeting month (h)")
    ax[0].set_ylabel("index sd per 1-sd shock")
    ax[0].legend(fontsize=7, frameon=False)
    fig.suptitle(f"{smp}: standardized response of each index (90% HAC bands for GS and Fed 3yr)", fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(os.path.join(HERE, name), dpi=130)


def plot_contrib(res, smp, name):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rows = [("GS FCI", COMMON), ("Fed FCI-G (3yr)", COMMON + list(FEDONLY))]
    fig, ax = plt.subplots(2, 4, figsize=(15, 6.5), sharex=True)
    for j, (spec, sh, lab) in enumerate(SHOCKS):
        lo, hi = 0, 0
        for i, (n, comps) in enumerate(rows):
            a = ax[i, j]
            r = res[(res["sample"] == smp) & (res.spec == spec) & (res.shock == sh) & (res["index"] == n)]
            P = r.pivot_table(index="h", columns="series", values="coef")
            pos, neg = np.zeros(len(P)), np.zeros(len(P))
            for c in comps:
                v = P[c].values
                a.bar(P.index, v, bottom=np.where(v >= 0, pos, neg), color=COLORS[c], width=0.8, label=c)
                pos, neg = pos + np.clip(v, 0, None), neg + np.clip(v, None, 0)
            a.plot(P.index, P["fci"], "k-o", ms=3, lw=1.4, label="total")
            a.axhline(0, color="k", lw=0.6)
            lo, hi = min(lo, neg.min()), max(hi, pos.max())
            a.set_title(f"{lab} - {n}", fontsize=9, loc="left")
        for i in range(2):
            ax[i, j].set_ylim(lo * 1.1 - 0.01, hi * 1.1 + 0.01)
    ax[0, 0].set_ylabel("index sd per 1-sd shock")
    ax[1, 0].set_ylabel("index sd per 1-sd shock")
    ax[1, 0].legend(fontsize=7, ncol=2, frameon=False, loc="upper left")
    for a in ax[-1]:
        a.set_xlabel("months after the meeting month (h)")
    fig.suptitle(f"{smp}: contributions to the standardized response (same scale within each shock)", fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(os.path.join(HERE, name), dpi=130)


if __name__ == "__main__":
    main()
