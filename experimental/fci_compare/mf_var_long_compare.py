"""
Option 3 (answer 44): the ECB-method index from the 1973 recursive VAR (mf_var_us_long.py; 6 variables, BIC 2 lags; 6 lags as a check), in funds-rate pp,
compared with the project's indexes. Each index demeaned over 1990-2026 for the comparison (the VAR index was demeaned over 1973-2025 for estimation).
Reports: weights; contributions by variable (sd and latest); correlations (levels, 12-month changes) with the macro-model eventual-pressure index (EP_4, EP_4+HP),
current pressure (CP_4), market index (MKT), GS, ANFCI; FCI-G against levels and 12-month changes; proxy funds rate (12-month changes from 2009);
same-month and later responses to NS surprises (monthly LP) of the index and of its gap to EP_4; the yardstick against the long-sample LP (lp_weights/E7).
Usage: python experimental/fci_compare/mf_var_long_compare.py
Outputs: mf_var_long_compare.png
"""
import os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "experimental", "lp_weights"))
import mf_var_us_long as LL
import lp_explore as L


def rd(path):
    d = pd.read_csv(path, index_col=0); d.index = pd.PeriodIndex(d.index, freq="M"); return d


def main():
    W = pd.read_csv(os.path.join(HERE, "mf_var_us_long.csv"))
    W = W[W["sample"] == "1973, 6 variables"]
    pd.set_option("display.width", 220)
    print("weights (pp of funds rate per unit):")
    print(W.pivot(index="variable", columns="lags", values="weight").round(4).to_string())
    print("yardstick: unemployment gap at month 12:", W.groupby("lags").yardstick_u_m12.first().round(3).to_dict(), "(output = -2 x)")
    F = LL.financial()
    cols = ["policy rate", "10-year", "mortgage spread", "Baa spread", "equities", "dollar"]
    Z = F[cols].loc["1973-01":"2025-12"]
    Z = Z - Z.drop(index=[t for t in Z.index if t.year == 2020]).mean()
    Zx = F[cols].loc["1973-01":] - (F[cols].loc["1973-01":"2025-12"].drop(index=[t for t in Z.index if t.year == 2020]).mean())
    out = {}
    for p in (2, 6):
        w = W[W.lags == p].set_index("variable").weight
        C = Zx[cols] * w
        out[p] = C
        print(f"\np={p}: contributions, sd since 1990 / latest (pp): " + ", ".join(f"{c} {C[c].loc['1990-01':].std():.2f} / {C[c].dropna().iloc[-1]:+.2f}" for c in cols)
              + f";  total sd {C.sum(axis=1).loc['1990-01':].std():.2f}, latest {C.sum(axis=1).dropna().iloc[-1]:+.2f} ({C.dropna().index[-1]})")
    mm = rd(os.path.join(ROOT, "experimental", "ms_fci", "macro_model_v3_monthly.csv"))
    tr = rd(os.path.join(HERE, "transmission_v3_monthly.csv"))
    f1 = pd.read_csv(os.path.join(ROOT, "raw", "fed_monthly_1yr.csv"), parse_dates=["date"]).set_index("date").iloc[:, 0]; f1.index = f1.index.to_period("M")
    f3 = pd.read_csv(os.path.join(ROOT, "raw", "fed_monthly_3yr.csv"), parse_dates=["date"]).set_index("date").iloc[:, 0]; f3.index = f3.index.to_period("M")
    prox = pd.read_excel(os.path.join(ROOT, "raw", "proxy-funds-rate-data.xlsx"), sheet_name="Weekly", skiprows=1, names=["date", "ffr", "proxy"])
    prox["date"] = pd.to_datetime(prox.date); prox = prox.set_index("date").proxy.resample("ME").last(); prox.index = prox.index.to_period("M")
    S = pd.DataFrame({"MF-VAR (p=2)": out[2].sum(axis=1, min_count=6), "MF-VAR (p=6)": out[6].sum(axis=1, min_count=6), "EP_4": mm["EP_4"], "EP_4+HP": mm["EP_4+HP"], "CP_4": mm["CP_4"],
                      "MKT": tr["MKT"], "GS": tr["GS"], "ANFCI": tr["ANFCI"], "FCI-G 1yr": f1 / 0.4525, "FCI-G 3yr": f3 / 0.4525, "PROXY": prox}).loc["1990-01":"2026-10"]
    for c in ("MF-VAR (p=2)", "MF-VAR (p=6)"):
        S[c] = S[c] - S[c].mean()
    m = "MF-VAR (p=2)"
    print("\ncorrelations of the MF-VAR index (p=2) [p=6 in brackets]: levels | 12-month changes")
    for c in ("EP_4", "EP_4+HP", "CP_4", "MKT", "GS", "ANFCI"):
        a = S[[m, c]].dropna(); b = S[["MF-VAR (p=6)", c]].dropna()
        print(f"  {c:8s} {a.corr().iloc[0, 1]:+.2f} [{b.corr().iloc[0, 1]:+.2f}] | {a.diff(12).corr().iloc[0, 1]:+.2f} [{b.diff(12).corr().iloc[0, 1]:+.2f}]")
    for f in ("FCI-G 1yr", "FCI-G 3yr"):
        a = S[[f, m]].dropna(); b = pd.concat([S[f], S[m].diff(12)], axis=1).dropna()
        print(f"  {f}: with MF-VAR level {a.corr().iloc[0, 1]:+.2f}, with its 12-month change {b.corr().iloc[0, 1]:+.2f}")
    print(f"  proxy funds rate, 12-month changes from 2009: {S[['PROXY', m]].loc['2009-01':].diff(12).corr().iloc[0, 1]:+.2f}")
    print(f"  sd since 1990: MF-VAR {S[m].std():.2f}, EP_4 {S['EP_4'].std():.2f}; latest MF-VAR {S[m].dropna().iloc[-1]:+.2f}, EP_4 {S['EP_4'].dropna().iloc[-1]:+.2f}")
    # policy surprises
    Ssur, _, _ = L.surprises()
    print("\nresponses to a 1-unit NS surprise (monthly LP; MF-VAR and EP_4 in funds-rate pp):")
    for nm_, y in (("MF-VAR (p=2)", S[m]), ("EP_4", S["EP_4"]), ("MF-VAR minus EP_4", S[m] - S["EP_4"])):
        o = [L.lp(y, Ssur["ns"], h) for h in (0, 3, 6, 12, 24)]
        print(f"  {nm_:18s} " + "  ".join(f"h={h}: {b:+.2f} ({se:.2f})" for h, (b, se) in zip((0, 3, 6, 12, 24), o)))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 1, figsize=(13, 10), sharex=True)
    t = S.index.to_timestamp()
    axes[0].plot(t, S[m], color="#7f3fbf", lw=1.4, label="ECB-method VAR index (1973 sample, recursive yardstick, 2 lags)")
    axes[0].plot(t, S["EP_4"], color="black", lw=1.4, label="Macro-model eventual pressure (FRB/US, 4 quarters)")
    axes[0].set_title("ECB-method VAR index vs macro-model index, pp of funds rate (demeaned 1990-2026)", fontsize=11)
    C = out[2].loc["1990-01":]
    for c, col in zip(cols, ("#7f7f7f", "#1f5fa8", "#8c564b", "#e377c2", "#2ca02c", "#9467bd")):
        axes[1].plot(C.index.to_timestamp(), C[c] - C[c].mean(), color=col, lw=1.2, label=c)
    axes[1].set_title("ECB-method VAR index by variable (contributions, demeaned 1990-2026)", fontsize=11)
    for ax in axes:
        ax.axhline(0, color="gray", lw=0.8); ax.grid(alpha=0.25); ax.legend(loc="upper right", fontsize=9, frameon=False); ax.set_ylabel("pp of funds rate")
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "mf_var_long_compare.png"), dpi=130)


if __name__ == "__main__":
    main()
