"""
Current-pressure (distributed-lag) macro-model index with past changes counted up to a cap of K = 4, 8 or 12 quarters, all divided by the 4-quarter yardstick
(INDEX_QA.md answers 28-29). FRB/US paths: old design (VAR expectations, persistent shifts, funds rate fixed in partials; policy rate direct effect), as answer 8.
    CP_K(t) = [ sum_{m} Phi_j(min((m+1)/3, K))' dx_{t-m} ] / G(4)        (a change made m months ago counts with its cumulative FRB/US effect at its age, capped at K quarters)
    Static (eventual pressure, main) = Phi(4)' x_t / G(4)
CP_4 equals the static index for a configuration that has been in place at least 4 quarters. For K = 8 or 12, an old configuration reads Phi(K)' x / G(4), not the static value.
Monthly mapping (assumed): a change m months old has been in place (m+1)/3 quarters; quarterly responses interpolated linearly. History before 1990 treated as one old change, so results from 1998.
Usage: python experimental/ms_fci/macro_model_dl_caps.py
Outputs: macro_model_dl_caps_monthly.csv, macro_model_dl_caps.png
"""
import os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import macro_model_dl as DL

COLS0 = ["policy rate", "10-year", "mortgage spread", "BBB spread", "equities", "dollar"]


def cp(x, P, G4, K, cols):
    D = x[cols].diff(); D.iloc[0] = x[cols].iloc[0]
    D = D.values
    M = 3 * K
    w = np.array([DL.phi_at(P[cols], min((m + 1) / 3, K)).values for m in range(M)])
    wK = DL.phi_at(P[cols], K).values
    out = np.zeros(len(D))
    for t in range(len(D)):
        acc = sum(D[t - m] @ w[m] for m in range(min(M, t + 1)))
        if t >= M:
            acc += D[:t - M + 1].sum(axis=0) @ wK              # changes older than K quarters: full capped effect
        out[t] = acc / G4
    return pd.Series(out, index=x.index)


def main():
    x, comp = DL.levels_data()
    x = x.loc["1990-01":]
    P, G = DL.paths("base")
    print("cumulative effect per unit / G(4), by quarter (funds-rate pp per unit):")
    print(pd.DataFrame({f"q{K}": DL.phi_at(P, K) / G[4] for K in (2, 4, 8, 12)}).round(4).to_string())
    out = {}
    for hp, cols in (("", COLS0), ("+HP", COLS0 + ["house prices"])):
        out[f"static{hp}"] = pd.Series(x[cols].values @ DL.phi_at(P[cols], 4).values / G[4], index=x.index)
        for K in (4, 8, 12):
            out[f"CP_{K}{hp}"] = cp(x, P, G[4], K, cols)
    D = pd.DataFrame(out)
    D.to_csv(os.path.join(HERE, "macro_model_dl_caps_monthly.csv"), float_format="%.4f", index_label="month")
    S = D.loc["1998-01":]
    print("\nFrom 1998, no house prices: sd, mean, latest; correlation with the static index (levels, 12-month changes)")
    for c in ("static", "CP_4", "CP_8", "CP_12"):
        print(f"  {c:7s} sd {S[c].std():.2f}  mean {S[c].mean():+.2f}  latest {S[c].iloc[-1]:+.2f}  corr {S[c].corr(S['static']):.2f} / {S[c].diff(12).corr(S['static'].diff(12)):.2f}")
    print("\nSelected months (pp of funds rate, not demeaned; static is demeaned 1990-2026 by construction of the levels):")
    sel = [pd.Period(p, "M") for p in ("2000-12", "2003-06", "2008-12", "2009-12", "2013-06", "2020-12", "2022-10", "2023-10", "2024-12")] + [S.index[-1]]
    print(S.loc[sel, ["static", "CP_4", "CP_8", "CP_12", "static+HP", "CP_4+HP", "CP_8+HP", "CP_12+HP"]].round(2).to_string())
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 1, figsize=(13, 10), sharex=True)
    t = S.index.to_timestamp()
    for ax, hp in zip(axes, ("", "+HP")):
        ax.plot(t, S[f"static{hp}"], color="black", lw=1.6, label="Eventual pressure: static index (4-quarter weights)")
        for K, c in ((4, "#1f5fa8"), (8, "#ff7f0e"), (12, "#d62728")):
            ax.plot(t, S[f"CP_{K}{hp}"], color=c, lw=1.3, label=f"Current pressure: past changes counted up to {K} quarters")
        ax.axhline(0, color="gray", lw=0.8); ax.grid(alpha=0.25); ax.set_ylabel("pp of funds rate (4-quarter yardstick)")
        ax.set_title(f"Macro-model index, {'without' if hp == '' else 'with'} house prices", fontsize=11)
        ax.legend(loc="upper left", fontsize=8, frameon=False)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "macro_model_dl_caps.png"), dpi=130)


if __name__ == "__main__":
    main()
