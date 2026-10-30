"""
Macro-model levels index: financial variables weighted by FRB/US funds-rate equivalents (q4), levels relative to the 1990-2026 average, in pp of funds rate (tighter above zero).
Replaces the "MS-style" label (no direct source for that index; this is our own construction); oil is dropped.
Variables and weights (frbus_sensitivities.csv and frbus_sensitivities_ext.csv, q4):
    policy rate (DFF; short end)   0.009 per pp (direct effect, VAR expectations held fixed; --withexp uses 0.242, which includes the funds rate's role in the expectations VAR)          10-year Treasury (parallel curve)  0.570 per pp
    mortgage spread (PMMS 30-yr less 10-yr)  0.416 per pp   BBB spread (ICE BofA/Baa)  0.127 per pp
    equities (100 ln CAPE)  -0.032 per %           real dollar (100 ln)  0.100 per %
    house prices (100 ln of the house price to rent ratio: Zillow ZHVI, Case-Shiller before 2000, over CPI owners' equivalent rent CUSR0000SEHC; monthly, carried within the month)  -0.029 per %
        [version "with house prices" only; the ratio is the stationary analogue of CAPE and is the variable in the FRB/US house-price equation. In raw levels the house price index trends so strongly
         that it contributes about -2.2 pp today and swamps everything else; --rawhp uses it]
Two versions: without and with house prices. --real10: the policy rate and 10-year are real (each less Cleveland Fed 10-year expected inflation).
Usage: python experimental/ms_fci/macro_model_levels.py [--real10] [--rawhp] [--withexp]
Outputs: macro_model_levels_daily[_real10].csv, macro_model_levels[_real10].png
"""
import os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "experimental", "path_fci"))
import path_fci as P
import fcig_replicate as R

REAL = "--real10" in sys.argv


def components(real=False, withexp=False, rawhp=False, verbose=True):
    """Daily contributions by variable (pp of funds rate, demeaned over 1990-2026); also returns the build data (X, G)."""
    P.L.REAL10 = real; P.L.RSTAR = False
    X, G = P.L.build()
    base = pd.read_csv(os.path.join(HERE, "frbus_sensitivities.csv"), index_col=0)["ffr_eq_q4"]
    ext = pd.read_csv(os.path.join(HERE, "frbus_sensitivities_ext.csv"), index_col=0)["ffr_eq_q4"]
    W = {"policy rate": ext["rshort" if withexp else "rshort_direct"], "10-year": base["rg10"], "mortgage spread": ext["rme"], "BBB spread": base["rbbbp"], "equities": -base["req"], "dollar": base["fpxr"], "house prices": ext["phouse"]}
    if verbose: print("weights (pp of funds rate per unit, q4): " + ", ".join(f"{k} {v:+.3f}" for k, v in W.items()))
    idx = X.index
    mort = R.fred("MORTGAGE30US").reindex(idx, method="ffill")
    spread = mort - G.x_y10.reindex(idx)
    hp = np.log(R.splice_level(R.zillow(), R.fred("CSUSHPISA")))
    if not rawhp:
        oer = np.log(P.L.get("CUSR0000SEHC"))
        hp = hp - oer.reindex(hp.index.union(oer.index)).sort_index().ffill().reindex(hp.index)       # price-to-rent ratio
    hp = hp.reindex(idx.union(hp.index)).sort_index().ffill().reindex(idx) * 100          # stepped monthly, carried within the month
    einf = X.einf if real else 0.0
    comp = pd.DataFrame({
        "policy rate": W["policy rate"] * (X.ffr - einf), "10-year": W["10-year"] * X.y10, "mortgage spread": W["mortgage spread"] * spread,
        "BBB spread": W["BBB spread"] * X.bbb, "equities": W["equities"] * 100 * X.lncape, "dollar": W["dollar"] * 100 * X.lnrusd,
        "house prices": W["house prices"] * hp}).dropna()
    comp = comp - comp.mean()
    return comp, X, G


def main():
    comp, X, G = components(REAL, "--withexp" in sys.argv, "--rawhp" in sys.argv)
    A = comp.drop(columns="house prices").sum(axis=1)
    B = comp.sum(axis=1)
    out = pd.DataFrame({"without house prices": A, "with house prices": B})
    tag = ("_real10" if REAL else "") + ("_rawhp" if "--rawhp" in sys.argv else "") + ("_withexp" if "--withexp" in sys.argv else "")
    out.to_csv(os.path.join(HERE, f"macro_model_levels_daily{tag}.csv"), float_format="%.4f", index_label="date")
    print(f"\n{'real' if REAL else 'nominal'} versions. sd of level: {out.std().round(2).to_dict()}; daily-change sd {out.diff().std().round(3).to_dict()}; corr of the two (levels {out.corr().iloc[0, 1]:.3f}, daily changes {out.diff().corr().iloc[0, 1]:.3f})")
    print("latest:", out.iloc[-1].round(2).to_dict(), "on", out.index[-1].date())
    grp = {"rates": ["policy rate", "10-year", "mortgage spread", "BBB spread"], "equities": ["equities"], "dollar": ["dollar"], "other (house prices)": ["house prices"]}
    me = comp.resample("ME").last()
    rows = []
    for lab, d0 in (("latest", None), ("chg since 27 Feb 2026", "2026-02-27"), ("chg since 27 Aug 2026", "2026-08-27")):
        v = comp.iloc[-1] if d0 is None else comp.iloc[-1] - comp.loc[:d0].iloc[-1]
        rows.append(dict(window=lab, **{g: round(float(v[c].sum()), 2) for g, c in grp.items()}, total_without_hp=round(float(v.drop("house prices").sum()), 2), total_with_hp=round(float(v.sum()), 2)))
    print(pd.DataFrame(rows).to_string(index=False))
    print("\nbreakdown latest by variable:", comp.iloc[-1].round(2).to_dict())
    # comparison with the other indexes (monthly)
    f3 = pd.read_csv(os.path.join(ROOT, "raw", "fed_monthly_3yr.csv"), parse_dates=["date"]).set_index("date").iloc[:, 0]
    f3.index = f3.index.to_period("M")
    gs = (G.fci - G.fci.mean()).resample("ME").last(); gs.index = gs.index.to_period("M")
    mo = out.resample("ME").last(); mo.index = mo.index.to_period("M")
    cmp = pd.concat([mo, (f3 / 0.4525).rename("FCI-G (output yardstick)"), (gs * 0.95).rename("GS (NS conversion)")], axis=1).dropna()
    print("\nmonthly corr of levels:\n", cmp.corr().round(2).to_string())
    print("12-month changes:\n", cmp.diff(12).corr().round(2).to_string())
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(13, 6.5))
    ax.plot(out.index, out["without house prices"], color="#1f5fa8", lw=1.5, label="Macro-model levels index, without house prices")
    ax.plot(out.index, out["with house prices"], color="#d62728", lw=1.5, label="Macro-model levels index, with house prices")
    ax.axhline(0, color="gray", lw=0.8); ax.grid(alpha=0.25); ax.tick_params(labelsize=11)
    ax.set_ylabel("pp of funds rate, tighter above zero (vs 1990-2026 average)", fontsize=11)
    ax.set_title(f"Macro-model (FRB/US-weighted) levels index in funds-rate equivalents, {'real' if REAL else 'nominal'} policy rate and 10-year", fontsize=11)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=2, fontsize=10, frameon=False)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, f"macro_model_levels{tag}.png"), dpi=130)


if __name__ == "__main__":
    main()
