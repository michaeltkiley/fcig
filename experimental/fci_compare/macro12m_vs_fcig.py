"""
Twelve-month change in the macro-model levels index against the level of FCI-G (monthly; FCI-G is a contribution built from past changes, so its level is naturally related to recent changes of a levels index).
FCI-G: official 3-year-lookback baseline (raw/fed_monthly_3yr.csv, to 2026-08) with the repository replication for later months; shown in funds-rate pp by the FRB/US yardstick (divide by 0.4525).
Macro-model index: nominal, without house prices (also printed: with house prices, real versions, other change horizons).
Usage: python experimental/fci_compare/macro12m_vs_fcig.py [--1yr] [--hp]        Output: macro12m_vs_fcig.png (macro12m_vs_fcig_1yr.png with --1yr, the 1-year-lookback FCI-G)
"""
import os, sys
import numpy as np, pandas as pd

HP = "--hp" in sys.argv                          # main macro-model version: with house prices
LB = "1yr" if "--1yr" in sys.argv else "3yr"      # FCI-G lookback: 3-year baseline (default) or 1-year

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def main():
    f3 = pd.read_csv(os.path.join(ROOT, "raw", f"fed_monthly_{LB}.csv"), parse_dates=["date"]).set_index("date").iloc[:, 0]; f3.index = f3.index.to_period("M")
    rep = pd.read_csv(os.path.join(ROOT, "fcig_replication_monthly.csv")); rep["month"] = pd.PeriodIndex(rep["month"], freq="M"); rep = rep.set_index("month")[f"{LB}|FCI-G"]
    fcig = pd.concat([f3, rep.loc[f3.index[-1] + 1:]])
    mm = {}
    for t in ("", "_real10"):
        d = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", f"macro_model_levels_daily{t}.csv"), parse_dates=["date"]).set_index("date")
        for c in d.columns:
            s = d[c].resample("ME").last(); s.index = s.index.to_period("M")
            mm[f"{'real' if t else 'nominal'}, {c}"] = s
    M = pd.DataFrame(mm)
    main_col = "nominal, with house prices" if HP else "nominal, without house prices"
    j = pd.concat({"macro12": M[main_col].diff(12), "fcig": fcig}, axis=1).dropna()
    print(f"main: 12-month change of the macro-model index ({main_col}) vs the level of FCI-G, {j.index[0]}..{j.index[-1]}: correlation {j.corr().iloc[0, 1]:.2f}")
    print("\nCorrelation of the level of FCI-G with the change of the macro-model index over h months:")
    rows = []
    for col in M:
        r = {"macro version": col}
        for samp, a in (("1990-", "1990-01"), ("1992-", "1992-01"), ("1998-", "1998-01")):
            for h in (6, 12, 22, 24):
                jj = pd.concat({"m": M[col].diff(h), "f": fcig}, axis=1).dropna().loc[a:]
                r[f"{samp} {h}m"] = round(jj.corr().iloc[0, 1], 2)
        rows.append(r)
    pd.set_option("display.width", 220)
    print(pd.DataFrame(rows).to_string(index=False))
    print("\nLead/lag check for the 12-month change (1990-): corr of FCI-G(t) with the 12m change at t+k months:",
          {k: round(float(pd.concat({'m': M[main_col].diff(12).shift(-k), 'f': fcig}, axis=1).dropna().corr().iloc[0, 1]), 2) for k in (-6, -3, 0, 3, 6)})
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(13, 6.5))
    x = j.index.to_timestamp()
    ax.plot(x, j.macro12, color="#d62728", lw=1.8, label=f"Macro-model levels index, 12-month change (nominal, {'with' if HP else 'without'} house prices)")
    ax.plot(x, j.fcig / 0.4525, color="#1f5fa8", lw=1.8, label=f"FCI-G level (official, {LB} lookback), in funds-rate pp (divided by 0.4525)")
    ax.axhline(0, color="gray", lw=0.8); ax.grid(alpha=0.25); ax.tick_params(labelsize=11)
    ax.set_ylabel("pp of funds rate (tighter above zero)", fontsize=11)
    ax.set_title(f"Macro-model index, 12-month change, and the FCI-G level: correlation {j.corr().iloc[0, 1]:.2f} (monthly, {j.index[0]} to {j.index[-1]})", fontsize=12)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=1, fontsize=10, frameon=False)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "macro12m_vs_fcig" + ("_1yr" if LB == "1yr" else "") + ("_hp" if HP else "") + ".png"), dpi=130)


if __name__ == "__main__":
    main()
