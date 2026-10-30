"""
Real macro-model (FRB/US) indexes, 1973-2026 (REAL_QA.md R1-R8). Same construction as ms_fci/macro_model_v3.py; only the data change:
    real policy rate (funds rate - 1-year expected inflation), real 10-year (10-year - 10-year expected inflation), mortgage spread, BBB spread,
    equities (100 ln CAPE), real dollar (100 ln), house prices (deviation of the price-to-rent ratio from its trailing 15-year average; "+HP" version)
    FRB/US weights and yardstick unchanged (old design: VAR expectations, persistent shifts; policy rate direct effect).
    Zero: each variable demeaned over 1973-2026 (main) or 1990-2026 (check, suffix "_z90").
Indexes (funds-rate pp): EP_K = Phi(K)' x~ / G(K) (K = 4 main; 8, 12); CP_K = distributed lag on demeaned levels (lags up to K quarters) / G(K);
    GI_1yr, GI_3yr = growth over the next year (FCI-G form) / G(4).
Usage: python experimental/real_case/macro_real.py
Outputs: macro_real_monthly.csv, macro_real.png
"""
import os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "experimental", "ms_fci"))
import macro_model_dl as DL
import macro_model_v3 as MV3

COLS0 = ["policy rate", "10-year", "mortgage spread", "BBB spread", "equities", "dollar"]


def data():
    D = pd.read_csv(os.path.join(HERE, "data_long_monthly.csv"), index_col=0); D.index = pd.PeriodIndex(D.index, freq="M")
    H = pd.read_csv(os.path.join(HERE, "hp_trend_monthly.csv"), index_col=0); H.index = pd.PeriodIndex(H.index, freq="M")
    X = pd.DataFrame({"policy rate": D["real policy rate"], "10-year": D["real 10-year"], "mortgage spread": D["mortgage spread"], "BBB spread": D["BBB spread"],
                      "equities": D["equities"], "dollar": D["dollar"], "house prices": H["deviation from trailing 15-yr average"]}).loc["1973-01":"2026-10"]
    return X


def build(X, window):
    Xd = X - X.loc[window].mean()
    P, G = DL.paths("base")
    out = {}
    for hp, cols in (("", COLS0), ("+HP", COLS0 + ["house prices"])):
        V = Xd[cols].values
        for K in (4, 8, 12):
            out[f"EP_{K}{hp}"] = V @ DL.phi_at(P[cols], K).values / G[K]
            W = np.array([(DL.phi_at(P[cols], (m + 1) / 3) - DL.phi_at(P[cols], m / 3)).values for m in range(3 * K)]) / G[K]
            out[f"CP_{K}{hp}"] = MV3.lagsum(V, W)
        dV = np.nan_to_num(Xd[cols].diff().values)
        for lab, L in (("GI_1yr", 12), ("GI_3yr", 36)):
            Wg = np.array([(DL.phi_at(P[cols], (m + 1) / 3 + 4) - DL.phi_at(P[cols], (m + 1) / 3)).values for m in range(L)]) / G[4]
            s = MV3.lagsum(dV, Wg); s[:L] = np.nan
            out[f"{lab}{hp}"] = s
    return pd.DataFrame(out, index=Xd.index)


def main():
    X = data()
    print("data coverage:", {c: str(X[c].first_valid_index()) for c in X})
    A = build(X, slice("1973-01", "2026-10"))
    B = build(X, slice("1990-01", "2026-10")).add_suffix("_z90")
    R = pd.concat([A, B], axis=1)
    R.to_csv(os.path.join(HERE, "macro_real_monthly.csv"), float_format="%.4f", index_label="month")
    pd.set_option("display.width", 230)
    main_cols = ["EP_4", "EP_4+HP", "CP_4", "GI_1yr+HP", "EP_4_z90"]
    print("\nsd since 1974 / latest:\n" + pd.DataFrame({"sd": R[main_cols].loc["1974-01":].std(), "latest": R[main_cols].ffill().iloc[-1]}).round(2).T.to_string())
    nom = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "macro_model_v3_monthly.csv"), index_col=0); nom.index = pd.PeriodIndex(nom.index, freq="M")
    j = pd.concat([R["EP_4_z90"], nom["EP_4"]], axis=1).loc["1990-01":].dropna()
    print(f"\nreal EP_4 (1990-2026 zero) vs nominal EP_4, 1990-2026: corr levels {j.corr().iloc[0, 1]:.2f}, 12m changes {j.diff(12).corr().iloc[0, 1]:.2f}")
    sel = [pd.Period(m, "M") for m in ("1974-06", "1979-12", "1981-06", "1985-01", "1990-01", "2000-01", "2008-12", "2013-01", "2021-06", "2023-10", "2026-09")]
    print(R.loc[sel, ["EP_4", "EP_4+HP", "CP_4", "GI_1yr+HP", "EP_4_z90"]].round(2).to_string())
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(13, 6.5))
    t = R.index.to_timestamp()
    for c, col, lab in (("EP_4", "black", "Eventual pressure (4 qtr), real rates"), ("EP_4+HP", "#7f7f7f", "with detrended house prices"),
                        ("CP_4", "#1f5fa8", "Current pressure (4 qtr)")):
        ax.plot(t, R[c], color=col, lw=1.3, label=lab)
    ax.axhline(0, color="gray", lw=0.8); ax.grid(alpha=0.25); ax.set_ylabel("pp of funds rate, tighter above zero (vs 1973-2026 average)")
    ax.set_title("Real macro-model (FRB/US) indexes, 1973-2026", fontsize=11); ax.legend(fontsize=9, frameon=False, loc="upper right")
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "macro_real.png"), dpi=130)


if __name__ == "__main__":
    main()
