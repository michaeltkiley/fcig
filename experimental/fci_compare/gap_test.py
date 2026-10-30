"""
EXPERIMENTAL test of the weighting note's equivalence result (experimental/weighting_note): with both indexes normalized to the funds-rate unit, the gap between an
impulse-response (macro-model) index and a market-weighted index is a weighted sum of NON-POLICY movements, (s - w)'u, plus the macro-only variables.
So the gap should (i) barely respond to monetary policy surprises, (ii) move with non-policy financial news (risk appetite, credit, oil, the dollar), and
(iii) change most in non-policy episodes and least in policy-driven ones.

gap = MACRO (macro-model levels index, no house prices; FRB/US q4 weights) - MKT (NS weights x 0.983), daily, pp of funds rate.
Decomposition: common variables (s_j - w_j) x_j for the 10-year, equities (100 ln CAPE), real dollar (100 ln); macro-only variables s_j x_j (policy rate, mortgage spread, BBB spread).
Tests:
  1. response to NS policy surprises (funds-rate pp = NS x 0.983): event window for the common part (identity check: s'psi - 1), monthly local projections h = 0..12 for the full gap and each index
  2. 12-month changes of the gap and its parts on 12-month changes in the excess bond premium (Gilchrist-Zakrajsek, Fed), VIX, ln WTI oil, and cumulated NS surprises
  3. episodes chosen before looking (dates from the policy/market record, listed below): change in MACRO, MKT and the gap and the gap by variable
Inputs not in git (raw/ is ignored): raw/ebp.csv (federalreserve.gov/econres/notes/feds-notes/ebp_csv.csv), raw/VIXCLS.csv, raw/DCOILWTICO.csv (FRED).
Usage: python experimental/fci_compare/gap_test.py
Outputs: gap_test_episodes.csv, gap_test.png
"""
import os, sys
import numpy as np, pandas as pd
import statsmodels.api as sm

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common_unit_v2 as C
P, Q, M, me = C.P, C.Q, C.M, C.me
ROOT = C.ROOT

EPISODES = [  # (label, start month-end, end month-end, type)
    ("1994 tightening", "1993-12", "1995-02", "policy"),
    ("1998 LTCM / Russia", "1998-06", "1998-10", "non-policy"),
    ("2000-02 equity bust", "2000-03", "2002-09", "non-policy"),
    ("2004-06 tightening", "2004-05", "2006-06", "policy"),
    ("2007-09 financial crisis", "2007-06", "2009-03", "non-policy"),
    ("2013 taper tantrum", "2013-04", "2013-09", "policy"),
    ("2014-16 dollar and oil", "2014-06", "2016-01", "non-policy"),
    ("2019 cuts", "2019-04", "2019-10", "policy"),
    ("2020 COVID shock", "2020-01", "2020-03", "non-policy"),
    ("2022 tightening", "2021-12", "2022-10", "policy"),
    ("2024 cuts", "2024-06", "2024-12", "policy"),
    ("2025 tariff shock", "2025-02", "2025-04", "non-policy"),
]


def main():
    comp, X, G = M.components(False, verbose=False)
    w, ev = C.ns_weights()
    wf = C.NS_FFR * w                                        # pp of funds rate per unit
    base = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "frbus_sensitivities.csv"), index_col=0)["ffr_eq_q4"]
    s = pd.Series({"10-yr": base["rg10"], "Equities (ln CAPE)": -base["req"], "Dollar (ln real)": base["fpxr"]})
    names = {"10-yr": "10-year", "Equities (ln CAPE)": "equities", "Dollar (ln real)": "dollar"}
    print("weights per unit (pp of funds rate): s (FRB/US) " + ", ".join(f"{names[k]} {s[k]:+.4f}" for k in s.index) + " | w (market, NS) " + ", ".join(f"{names[k]} {wf[k]:+.4f}" for k in s.index))
    # ---- event-window identity check
    d = ev.dropna(subset=Q.FUT + ["UST2Y"] + list(Q.ENDOG.values())).reset_index(drop=True)
    _, ns, _, _ = Q.gss_ns(d)
    nsf = ns * 0.98                                          # NS units -> funds-rate pp (average of the MP1 and ED4 loadings)
    dx = pd.DataFrame({k: d[c] for k, c in Q.ENDOG.items()})
    psi = np.array([np.polyfit(nsf, dx[k], 1)[0] for k in s.index])
    print(f"event window (n={len(d)}): psi per funds-rate pp " + ", ".join(f"{names[k]} {psi[i]:+.3f}" for i, k in enumerate(s.index))
          + f";  s'psi = {s.values @ psi:.3f}, w'psi = {wf.values @ psi * 0.98 / C.NS_FFR:.3f}")
    gwin = dx.values @ (s.values - (wf.values / C.NS_FFR * 0.98))
    r = sm.OLS(gwin, sm.add_constant(nsf)).fit(cov_type="HC1")
    print(f"   event-window common-variable gap on the surprise: slope {r.params[1]:+.3f} (se {r.bse[1]:.3f}), R2 {r.rsquared:.3f}; "
          f"MACRO-common slope {sm.OLS(dx.values @ s.values, sm.add_constant(nsf)).fit().params[1]:+.3f}")
    # ---- daily gap and its parts
    mk = pd.DataFrame({names[n]: wf[n] * P.VARS[n][1] * (X[P.VARS[n][0]] - X[P.VARS[n][0]].mean()) for n in wf.index}).reindex(comp.index)
    parts = pd.DataFrame({"10-year": comp["10-year"] - mk["10-year"], "equities": comp["equities"] - mk["equities"], "dollar": comp["dollar"] - mk["dollar"],
                          "policy rate": comp["policy rate"], "mortgage spread": comp["mortgage spread"], "BBB spread": comp["BBB spread"]})
    gap = parts.sum(axis=1)
    macro = comp.drop(columns="house prices").sum(axis=1); mkt = mk.sum(axis=1)
    Mo = pd.DataFrame({"MACRO": me(macro), "MKT": me(mkt), "gap": me(gap)}).join(me(parts)).loc[C.START:C.END]
    print(f"\nmonthly: sd of level MACRO {Mo.MACRO.std():.2f}, MKT {Mo.MKT.std():.2f}, gap {Mo.gap.std():.2f}; sd of 12m change {Mo.MACRO.diff(12).std():.2f}, {Mo.MKT.diff(12).std():.2f}, {Mo.gap.diff(12).std():.2f}")
    vs = Mo[list(parts)].diff(12).dropna()
    print("share of gap 12m-change variance by part (own variance / gap variance; covariances excluded):", (vs.var() / Mo.gap.diff(12).var()).round(2).to_dict())
    print("share of gap level variance by part:", (Mo[list(parts)].var() / Mo.gap.var()).round(2).to_dict())
    # ---- monthly LP on NS surprises
    e2 = d.assign(m=pd.PeriodIndex(d.Date, freq="M"), f=nsf)
    sur = e2.groupby("m").f.sum().reindex(Mo.index).fillna(0.0)
    print("\nMonthly local projections: y(t+h) - y(t-1) on the month-t NS surprise (funds-rate pp), HAC se")
    rows = []
    for h in (0, 3, 6, 12):
        row = {"h": h}
        for n in ("MACRO", "MKT", "gap", "10-year", "equities", "dollar", "mortgage spread", "BBB spread"):
            y = (Mo[n].shift(-h) - Mo[n].shift(1)); ok = y.notna()
            r = sm.OLS(y[ok], sm.add_constant(sur[ok])).fit(cov_type="HAC", cov_kwds={"maxlags": max(h, 1)})
            row[n] = f"{r.params.iloc[1]:+.2f} ({r.bse.iloc[1]:.2f})"
        rows.append(row)
    print(pd.DataFrame(rows).to_string(index=False))
    # ---- non-policy correlates
    ebp = C.raw_series(os.path.join("ebp.csv"), 2); ebp.index = ebp.index.to_period("M")
    vix = me(C.raw_series("VIXCLS.csv")); oil = me(np.log(C.raw_series("DCOILWTICO.csv")) * 100)
    Z = pd.DataFrame({"EBP": ebp, "VIX": vix, "oil (100 ln)": oil, "NS surprises (12m sum)": sur.rolling(12).sum()}).reindex(Mo.index)
    dZ = pd.concat([Z[["EBP", "VIX", "oil (100 ln)"]].diff(12), Z[["NS surprises (12m sum)"]]], axis=1)
    print("\n12-month changes, 1991-2026 (overlapping; HAC 12): correlations")
    Y = Mo[["MACRO", "MKT", "gap", "10-year", "equities", "dollar", "mortgage spread", "BBB spread"]].diff(12)
    J = pd.concat([Y, dZ], axis=1).dropna()
    print(J.corr().loc[list(Y), list(dZ)].round(2).to_string())
    print("\nJoint regressions of 12-month changes (coef, HAC t), and R2 from policy surprises alone vs non-policy variables alone:")
    rows = []
    for n in ("MACRO", "MKT", "gap"):
        r = sm.OLS(J[n], sm.add_constant(J[list(dZ)])).fit(cov_type="HAC", cov_kwds={"maxlags": 12})
        r_pol = sm.OLS(J[n], sm.add_constant(J[["NS surprises (12m sum)"]])).fit()
        r_np = sm.OLS(J[n], sm.add_constant(J[["EBP", "VIX", "oil (100 ln)"]])).fit()
        rows.append(dict(y=n, **{k: f"{r.params[k]:+.3f} ({r.tvalues[k]:.1f})" for k in dZ}, R2=round(r.rsquared, 2), R2_policy=round(r_pol.rsquared, 2), R2_nonpolicy=round(r_np.rsquared, 2)))
    print(pd.DataFrame(rows).to_string(index=False))
    # ---- episodes
    rows = []
    for lab, a, b, typ in EPISODES:
        a0 = pd.Period(a, "M"); b0 = pd.Period(b, "M")
        ch = Mo.loc[b0] - Mo.loc[a0]
        rows.append(dict(episode=lab, type=typ, months=f"{a}..{b}", NS_surprises=sur.loc[a0 + 1:b0].sum(), MACRO=ch.MACRO, MKT=ch.MKT, gap=ch.gap,
                         gap_ratio=abs(ch.gap) / max((abs(ch.MACRO) + abs(ch.MKT)) / 2, 1e-9), **{f"gap:{k}": ch[k] for k in parts}))
    E = pd.DataFrame(rows); E.to_csv(os.path.join(HERE, "gap_test_episodes.csv"), float_format="%.3f", index=False)
    print("\nEpisodes (changes over the window, pp of funds rate; gap_ratio = |gap change| / mean |index change|):")
    print(E.round(2).to_string(index=False))
    print("\nmean gap_ratio by type:", E.groupby("type").gap_ratio.mean().round(2).to_dict(), "| mean |gap change|:", E.assign(a=E.gap.abs()).groupby("type").a.mean().round(2).to_dict())
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 1, figsize=(13, 10), sharex=True)
    t = Mo.index.to_timestamp()
    axes[0].plot(t, Mo.MACRO, color="#d62728", lw=1.4, label="Macro-model levels index (FRB/US weights, no house prices)")
    axes[0].plot(t, Mo.MKT, color="#ff7f0e", lw=1.4, label="Market-based index (NS weights)")
    axes[0].plot(t, Mo.gap, color="black", lw=1.2, label="Gap (macro minus market)")
    axes[0].set_title("Macro-model and market-based indexes and their gap, pp of funds rate", fontsize=11)
    cols = {"10-year": "#1f5fa8", "equities": "#2ca02c", "dollar": "#9467bd", "policy rate": "#7f7f7f", "mortgage spread": "#8c564b", "BBB spread": "#e377c2"}
    for k, c in cols.items():
        axes[1].plot(t, Mo[k], color=c, lw=1.2, label=k)
    axes[1].set_title("Gap by variable: weight differences (10-year, equities, dollar) and macro-only variables", fontsize=11)
    for lab, a, b, typ in EPISODES:
        for ax in axes:
            ax.axvspan(pd.Period(a, "M").to_timestamp(), pd.Period(b, "M").to_timestamp(), color="#1f5fa8" if typ == "policy" else "#d62728", alpha=0.07, lw=0)
    for ax in axes:
        ax.axhline(0, color="gray", lw=0.8); ax.grid(alpha=0.25); ax.legend(loc="upper right", fontsize=9, ncol=2, frameon=False)
    axes[1].set_xlabel("shaded: blue = policy episodes, red = non-policy episodes (chosen before computing)")
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "gap_test.png"), dpi=130)


if __name__ == "__main__":
    main()
