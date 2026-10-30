"""
r* question S1b: how the equity weight (per log point of CAPE) carries over to the earnings-yield gap E/P - r* (pp). Illustration, not a decision.
    real case        w * [100 ln CAPE - mean]
    option 1         w * (-100 / mean E/P) * [(E/P - r*) - mean]        fixed factor at the 1973-2026 mean E/P
    option 3         w * (-100 / E/P(t)) * [(E/P - r*) - mean]          factor varies with each month's E/P
    w: market -0.0512, GS -0.049 (x 0.945/0.98), FRB/US EP_4 equity weight. r*: Kiley or LW one-sided (full-sample), quarterly held within the quarter.
    Zero point: 1973-2026 mean (illustration only; agenda item 3 is open).
CAPE level: data_long 'equities' (100 ln CAPE, demeaned project series) with its constant restored from Shiller CAPE over 1990-92.
Usage: python experimental/rstar_case/equity_conversion.py      Outputs: equity_conversion_monthly.csv, equity_conversion.png
"""
import os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "experimental", "ms_fci"))
sys.path.insert(0, os.path.join(ROOT, "experimental", "real_case"))
import macro_model_dl as DL
import macro_real as MR


def rd(p):
    d = pd.read_csv(p, index_col=0); d.index = pd.PeriodIndex(d.index, freq="M"); return d


def main():
    D = rd(os.path.join(ROOT, "experimental", "real_case", "data_long_monthly.csv")).loc["1973-01":"2026-09"]
    sh = pd.read_csv(os.path.join(ROOT, "raw", "shiller_cape.csv")); sh = pd.Series(sh.cape.values, index=pd.PeriodIndex(sh.month, freq="M"))
    k = float((100 * np.log(sh.loc["1990-01":"1992-12"]) - D.equities.loc["1990-01":"1992-12"]).mean())
    cape = np.exp((D.equities + k) / 100)
    ep = 100 / cape
    rs = pd.read_csv(os.path.join(ROOT, "experimental", "fci_compare", "rstar_series.csv"), index_col=0); rs.index = pd.PeriodIndex(rs.index, freq="Q")
    P, G = DL.paths("base")
    w = {"MKT": -0.0512, "GS": -0.049 * 0.945 / 0.98, "EP_4": float((DL.phi_at(P[MR.COLS0], 4) / G[4])["equities"])}
    print("equity weights per log point of CAPE: " + ", ".join(f"{a} {b:+.4f}" for a, b in w.items()))
    print(f"E/P: mean {ep.mean():.2f}, min {ep.min():.2f} ({ep.idxmin()}), max {ep.max():.2f} ({ep.idxmax()}), latest {ep.iloc[-1]:.2f}; fixed factor 100/mean = {100 / ep.mean():.1f}")
    lc = 100 * np.log(cape); base = lc - lc.mean()
    out = {"CAPE": cape, "E/P": ep}
    mk = rd(os.path.join(ROOT, "experimental", "real_case", "market_real_monthly.csv"))
    gs = rd(os.path.join(ROOT, "experimental", "real_case", "gs_real_monthly.csv"))
    mr = rd(os.path.join(ROOT, "experimental", "real_case", "macro_real_monthly.csv"))
    tot = {"MKT": mk.MKT_real, "GS": gs.GS_real * 0.945 / 0.98, "EP_4": mr.EP_4}
    for rn in ("Kiley_onesided", "LW_onesided"):
        r = pd.Series(rs[rn].reindex(D.index.asfreq("Q")).values, index=D.index).ffill()   # after 2026Q2: last value held
        gap = ep - r; gd = gap - gap.mean()
        out[f"E/P - r* ({rn[:2]})"] = gap
        for a, wa in w.items():
            c0 = wa * base
            c1 = wa * (-100 / ep.mean()) * gd
            c3 = wa * (-100 / ep) * gd
            out[f"{a} equity real case"] = c0
            out[f"{a} equity opt1 {rn[:2]}"] = c1; out[f"{a} equity opt3 {rn[:2]}"] = c3
            out[f"{a} total opt1 {rn[:2]}"] = tot[a] - c0 + c1; out[f"{a} total opt3 {rn[:2]}"] = tot[a] - c0 + c3
            out[f"{a} total real case"] = tot[a]
    O = pd.DataFrame(out)
    O.to_csv(os.path.join(HERE, "equity_conversion_monthly.csv"), float_format="%.4f", index_label="month")
    pd.set_option("display.width", 250)
    sel = [pd.Period(m, "M") for m in ("1974-12", "1979-12", "1982-07", "1987-08", "1995-01", "2000-03", "2003-03", "2008-12", "2015-01", "2021-12", "2023-10", "2026-09")]
    print("\nmarket index: equity contribution and total (2-year units), Kiley r*:")
    cols = ["CAPE", "E/P", "E/P - r* (Ki)", "MKT equity real case", "MKT equity opt1 Ki", "MKT equity opt3 Ki", "MKT total real case", "MKT total opt1 Ki", "MKT total opt3 Ki"]
    print(O.loc[sel, cols].round(2).to_string())
    print("\nsame with LW r*:")
    print(O.loc[sel, ["E/P - r* (LW)", "MKT equity opt1 LW", "MKT equity opt3 LW", "MKT total opt1 LW", "MKT total opt3 LW"]].round(2).to_string())
    print("\nsd and correlation with the real-case total, 1974-2026:")
    for a in w:
        for rn in ("Ki", "LW"):
            print(f"   {a:5s} {rn}: sd equity term real {O[f'{a} equity real case'].std():.2f}, opt1 {O[f'{a} equity opt1 {rn}'].std():.2f}, opt3 {O[f'{a} equity opt3 {rn}'].std():.2f};"
                  f"  total corr with real case: opt1 {O[f'{a} total opt1 {rn}'].corr(O[f'{a} total real case']):.2f}, opt3 {O[f'{a} total opt3 {rn}'].corr(O[f'{a} total real case']):.2f};"
                  f"  latest total real {O[f'{a} total real case'].iloc[-1]:+.2f}, opt1 {O[f'{a} total opt1 {rn}'].iloc[-1]:+.2f}, opt3 {O[f'{a} total opt3 {rn}'].iloc[-1]:+.2f}")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 1, figsize=(13, 10), sharex=True)
    t = O.index.to_timestamp()
    axes[0].plot(t, O["MKT equity real case"], color="black", lw=1.3, label="Real case: weight x 100 ln CAPE")
    axes[0].plot(t, O["MKT equity opt1 Ki"], color="#1f5fa8", lw=1.3, label="Option 1: E/P - r* (Kiley), fixed factor")
    axes[0].plot(t, O["MKT equity opt3 Ki"], color="#d62728", lw=1.3, label="Option 3: E/P - r* (Kiley), factor 100 / E/P(t)")
    axes[0].set_title("Market index: equity contribution (2-year units; tighter above zero)", fontsize=11)
    axes[1].plot(t, O["MKT total real case"], color="black", lw=1.3, label="Real case")
    axes[1].plot(t, O["MKT total opt1 Ki"], color="#1f5fa8", lw=1.3, label="Option 1 (Kiley)")
    axes[1].plot(t, O["MKT total opt3 Ki"], color="#d62728", lw=1.3, label="Option 3 (Kiley)")
    axes[1].set_title("Market index total, with only the equity term changed (10-year still the real case)", fontsize=11)
    for ax in axes:
        ax.axhline(0, color="gray", lw=0.8); ax.grid(alpha=0.25); ax.legend(fontsize=9, frameon=False, loc="upper right")
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "equity_conversion.png"), dpi=130)


if __name__ == "__main__":
    main()
