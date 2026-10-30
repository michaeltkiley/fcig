"""
EXPERIMENTAL second pass of the comparison in funds-rate equivalents (metric in METRIC.md; changes from the first pass are logged there).
Changes from common_unit.py: the macro-model levels index (experimental/ms_fci/macro_model_levels.py; FRB/US q4 weights, no oil; adds the policy rate, mortgage spread
and, in one version, house prices) replaces the MS-style FRB/US index (which had oil); the market-based index uses the preferred NS policy-news weights; GS uses the NS
conversion (0.945 pp per point); ANFCI, NFCI, OFR FSI and the SF Fed proxy funds rate are added; FCI-G is compared with level indexes through matched-horizon changes.

Indexes (monthly, end of month; pp of funds rate; higher = tighter; each demeaned over its own 1990-2026 sample):
  MACRO      macro-model levels index without house prices (nominal);  MACRO+HP  with house prices
  MKT        market-based index, NS weights, x 0.983 (funds-rate content of an NS unit)
  GS         GS replication x 0.945 (NS conversion)
  FCI-G      official 3-year (and 1-year) lookback / 0.4525 (FRB/US yardstick), replication after 2026-08
  ANFCI, NFCI, OFR FSI   divided by their same-month response to a parallel surprise (MP1 + ED4, monthly LP, h = 0; METRIC.md set B conversion)
  PROXY      SF Fed proxy funds rate (level of an equivalent policy rate; informative only from 2009; compared in changes)
  MS-FRB     the old MS-style index (with oil), only to show what dropping oil (and adding the other variables) changes
Inputs not in git (raw/ is ignored): raw/ANFCI.csv, raw/NFCI.csv (FRED), raw/ofr_fsi.csv (financialresearch.gov/financial-stress-index/data/fsi.csv).
Usage: python experimental/fci_compare/common_unit_v2.py
Outputs: common_unit_v2_monthly.csv, common_unit_v2_groups.csv, common_unit_v2_levels.png
"""
import os, sys
import numpy as np, pandas as pd
import statsmodels.api as sm

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for sub in ("path_fci", "ms_fci"):
    sys.path.insert(0, os.path.join(ROOT, "experimental", sub))
import path_fci as P
import path_fci_gss_ns as Q
import macro_model_levels as M

START, END = "1990-01", "2026-10"
NS_FFR, GS_NS, YARD = 0.983, 0.945, 0.4525
LEVEL_SET = ["MACRO", "MACRO+HP", "MKT", "GS", "ANFCI"]


def me(s):
    s = s.resample("ME").last(); s.index = s.index.to_period("M"); return s


def raw_series(name, col=1):
    d = pd.read_csv(os.path.join(ROOT, "raw", name))
    return pd.Series(pd.to_numeric(d.iloc[:, col], errors="coerce").values, index=pd.to_datetime(d.iloc[:, 0])).dropna()


def ns_weights():
    ev = P.events(P.USMPD)
    d = ev.dropna(subset=Q.FUT + ["UST2Y"] + list(Q.ENDOG.values())).reset_index(drop=True)
    _, ns, _, _ = Q.gss_ns(d)
    return pd.Series(Q.estimate(d, ns, True)[0], index=list(Q.ENDOG)), ev


def build():
    """Monthly indexes (pp of funds rate) plus daily components of MACRO and MKT."""
    comp, X, G = M.components(False, verbose=False)
    w, ev = ns_weights()
    mk = pd.DataFrame({n: NS_FFR * w[n] * P.VARS[n][1] * (X[P.VARS[n][0]] - X[P.VARS[n][0]].mean()) for n in w.index})
    mk.columns = ["10-year", "equities", "dollar"]
    f3 = pd.read_csv(os.path.join(ROOT, "raw", "fed_monthly_3yr.csv"), parse_dates=["date"]).set_index("date").iloc[:, 0]; f3.index = f3.index.to_period("M")
    f1 = pd.read_csv(os.path.join(ROOT, "raw", "fed_monthly_1yr.csv"), parse_dates=["date"]).set_index("date").iloc[:, 0]; f1.index = f1.index.to_period("M")
    rep = pd.read_csv(os.path.join(ROOT, "fcig_replication_monthly.csv")); rep["month"] = pd.PeriodIndex(rep["month"], freq="M"); rep = rep.set_index("month")
    f3 = pd.concat([f3, rep["3yr|FCI-G"].loc[f3.index[-1] + 1:]]); f1 = pd.concat([f1, rep["1yr|FCI-G"].loc[f1.index[-1] + 1:]])
    msold = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "ms5_level_daily.csv"), parse_dates=["date"]).set_index("date")
    prox = pd.read_excel(os.path.join(ROOT, "raw", "proxy-funds-rate-data.xlsx"), sheet_name="Weekly", skiprows=1, names=["date", "ffr", "proxy"])
    prox["date"] = pd.to_datetime(prox.date); prox = prox.set_index("date")
    S = pd.DataFrame({
        "MACRO": me(comp.drop(columns="house prices").sum(axis=1)), "MACRO+HP": me(comp.sum(axis=1)), "MKT": me(mk.sum(axis=1)),
        "GS": me((G.fci - G.fci.mean()) * GS_NS), "FCI-G (3yr)": f3 / YARD, "FCI-G (1yr)": f1 / YARD,
        "ANFCI": me(raw_series("ANFCI.csv")), "NFCI": me(raw_series("NFCI.csv")), "OFR FSI": me(raw_series("ofr_fsi.csv")),
        "PROXY": me(prox.proxy), "MS-FRB (old, oil)": me(msold.Total)}).loc[START:END]
    # conversion of ANFCI, NFCI, OFR FSI by the same-month response to a parallel surprise
    e2 = ev.copy(); e2["m"] = pd.PeriodIndex(e2.Date, freq="M")
    sur = e2.groupby("m")[["MP1", "ED4"]].sum().reindex(S.index).fillna(0.0)
    conv = {}
    for n in ("ANFCI", "NFCI", "OFR FSI", "MACRO", "MKT", "GS"):
        dy = (S[n] - S[n].shift(1)); ok = dy.notna()
        r = sm.OLS(dy[ok], sm.add_constant(sur[ok])).fit(cov_type="HAC", cov_kwds={"maxlags": 6})
        v = r.cov_params().loc[["MP1", "ED4"], ["MP1", "ED4"]].values
        conv[n] = (r.params["MP1"] + r.params["ED4"], float(np.sqrt(v.sum())))
    for n in ("ANFCI", "NFCI", "OFR FSI"):
        S[n] = S[n] / conv[n][0]
    for n in S:
        if n != "PROXY": S[n] = S[n] - S[n].mean()
    return S, conv, comp, mk, X, ev


def pair_table(D, names, start=None):
    rows = []
    for i, a in enumerate(names):
        for c in names[i + 1:]:
            j = D[[a, c]].loc[start:].dropna(); ch = j.diff(12).dropna()
            rows.append(dict(pair=f"{a} / {c}", start=str(j.index[0]), corr_lev=j[a].corr(j[c]), corr_12m=ch[a].corr(ch[c]),
                             sign_12m=float((np.sign(ch[a]) == np.sign(ch[c])).mean()), slope_12m=np.polyfit(ch[a], ch[c], 1)[0]))
    return pd.DataFrame(rows)


def main():
    S, conv, comp, mk, X, ev = build()
    S.to_csv(os.path.join(HERE, "common_unit_v2_monthly.csv"), float_format="%.4f", index_label="month")
    print("Same-month response to a parallel 1 pp surprise (index units before conversion; MACRO/MKT/GS already in pp): "
          + "; ".join(f"{n} {b:+.2f} ({s:.2f})" for n, (b, s) in conv.items()))
    print("\nsd of level (pp):", S.std().round(2).to_dict())
    print("latest", S.index[-1], ":", S.iloc[-1].round(2).to_dict())
    # what replacing MS-FRB by MACRO changes
    j = S[["MACRO", "MS-FRB (old, oil)"]].dropna()
    print(f"\nMACRO vs old MS-FRB: corr levels {j.corr().iloc[0, 1]:.2f}, 12m changes {j.diff(12).corr().iloc[0, 1]:.2f}; latest {j.iloc[-1].round(2).to_dict()}")
    ms = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "ms5_level_daily.csv"), parse_dates=["date"]).set_index("date")
    oil = me(ms.Oil).loc[START:END]
    print(f"   old index oil contribution: sd {oil.std():.2f} pp, range {oil.min():+.2f}..{oil.max():+.2f}, latest {oil.iloc[-1]:+.2f}; corr of oil contribution with (MS-FRB - MACRO): {oil.corr(j.iloc[:, 1] - j.iloc[:, 0]):.2f}")
    mc = me(comp).loc[START:END]
    print("   MACRO-only additions, sd (pp):", mc[["policy rate", "mortgage spread", "house prices"]].std().round(2).to_dict())
    # comparison among level indexes
    names = ["MACRO", "MACRO+HP", "MKT", "GS", "ANFCI", "NFCI", "OFR FSI"]
    print("\n===== Level indexes: pairwise (monthly; levels and 12-month changes) =====")
    print(pair_table(S, names).round(2).to_string(index=False))
    # FCI-G matched horizon: FCI-G (1yr) level vs 12-month change, FCI-G (3yr) level vs 24-month change
    print("\n===== FCI-G (a flow measure) against matched-horizon changes of level indexes =====")
    rows = []
    for n in names:
        for lab, f, h in (("FCI-G 1yr vs 12m chg", "FCI-G (1yr)", 12), ("FCI-G 3yr vs 24m chg", "FCI-G (3yr)", 24), ("FCI-G 3yr vs level", "FCI-G (3yr)", 0)):
            x = S[n] if h == 0 else S[n].diff(h)
            jj = pd.concat([S[f], x], axis=1).dropna()
            rows.append(dict(index=n, compare=lab, corr=jj.corr().iloc[0, 1], slope=np.polyfit(jj.iloc[:, 1], jj.iloc[:, 0], 1)[0]))
    print(pd.DataFrame(rows).pivot(index="index", columns="compare", values="corr").round(2).to_string())
    # proxy funds rate in changes from 2009
    print("\n===== SF Fed proxy funds rate (from 2009): correlation of 12-month changes; slope of index on proxy =====")
    rows = []
    for n in names + ["FCI-G (1yr)"]:
        jj = S[["PROXY", n]].loc["2009-01":].diff(12).dropna()
        rows.append(dict(index=n, corr_12m=jj.corr().iloc[0, 1], slope=np.polyfit(jj.PROXY, jj[n], 1)[0], sd_idx=jj[n].std(), sd_proxy=jj.PROXY.std()))
    print(pd.DataFrame(rows).round(2).to_string(index=False))
    # pre-specified range metric on the level set (FCI-G excluded from levels: deviation logged)
    D = S[LEVEL_SET]
    rng = D.max(axis=1) - D.min(axis=1)
    print(f"\n===== Cross-index range, level set {LEVEL_SET}: mean {rng.mean():.2f}, max {rng.max():.2f} ({rng.idxmax()}), latest {rng.iloc[-1]:.2f}")
    print("mean abs gap to cross-index median:", D.sub(D.median(axis=1), axis=0).abs().mean().round(2).to_dict())
    roll = rng.rolling(6).mean().dropna()
    for lab, asc in (("closest alignment", True), ("biggest differences", False)):
        chosen = []
        for e, v in roll.sort_values(ascending=asc).items():
            if all(abs((e - c0).n) >= 6 for c0, _ in chosen): chosen.append((e, v))
            if len(chosen) == 4: break
        print(f"  {lab}:")
        for e, v in sorted(chosen):
            m = D.loc[e - 5:e].mean()
            print(f"    {e - 5}..{e} (range {v:.2f}): " + ", ".join(f"{n} {m[n]:+.2f}" for n in LEVEL_SET))
    # groups
    rows = []
    groups_macro = {"rates": ["policy rate", "10-year", "mortgage spread", "BBB spread"], "equities": ["equities"], "dollar": ["dollar"], "other": ["house prices"]}
    rows.append(("MACRO+HP", {g: mc[c].sum(axis=1) for g, c in groups_macro.items()}))
    mm = me(mk).loc[START:END]
    rows.append(("MKT", {"rates": mm["10-year"], "equities": mm.equities, "dollar": mm.dollar}))
    out = []
    for n, g in rows:
        g = pd.DataFrame(g).reindex(columns=["rates", "equities", "dollar", "other"]).fillna(0.0)
        for lab, d0 in (("latest", None), ("chg since 2026-02", "2026-02"), ("chg since 2026-08", "2026-08")):
            v = g.iloc[-1] if d0 is None else g.iloc[-1] - g.loc[d0]
            out.append(dict(index=n, window=lab, total=v.sum(), **v.to_dict()))
    G2 = pd.DataFrame(out); G2.to_csv(os.path.join(HERE, "common_unit_v2_groups.csv"), float_format="%.3f", index=False)
    print("\n===== By group (pp of funds rate) =====\n" + G2.round(2).to_string(index=False))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 1, figsize=(13, 10), sharex=True)
    col = {"MACRO": "#d62728", "MKT": "#ff7f0e", "GS": "#2ca02c", "ANFCI": "#7f3fbf", "OFR FSI": "#8c564b"}
    for n, c in col.items():
        axes[0].plot(S.index.to_timestamp(), S[n], color=c, lw=1.4, label=n)
    axes[0].set_title("Level indexes in funds-rate equivalents (vs own 1990-2026 average)", fontsize=11)
    for n, c in (("FCI-G (1yr)", "#1f5fa8"), ("MACRO", "#d62728"), ("MKT", "#ff7f0e")):
        y = S[n] if n.startswith("FCI-G") else S[n].diff(12)
        axes[1].plot(S.index.to_timestamp(), y, color=c, lw=1.4, label=n + ("" if n.startswith("FCI-G") else ", 12-month change"))
    axes[1].set_title("FCI-G (1-year lookback, level) and 12-month changes of level indexes", fontsize=11)
    for ax in axes:
        ax.axhline(0, color="gray", lw=0.8); ax.grid(alpha=0.25); ax.set_ylabel("pp of funds rate, tighter above zero")
        ax.legend(loc="upper right", ncol=3, fontsize=9, frameon=False)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "common_unit_v2_levels.png"), dpi=130)


if __name__ == "__main__":
    main()
