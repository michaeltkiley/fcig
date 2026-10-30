"""
Macro-model indexes as specified in experimental/INDEX_QA.md (approved 29 Oct 2026), output lens, pp of funds rate.
FRB/US old design (answer 8): VAR expectations, persistent shifts, funds rate fixed in the partials; policy rate at its direct effect (expectations held fixed).
Paths: frbus_paths.csv / frbus_hike_paths.csv (cumulative GDP effect Phi_j(q) of a persistent unit shift, q = 1..32 quarters; G(q) for the full 1 pp hike).
Monthly mapping: a shift m months old has been in place (m+1)/3 quarters; quarterly responses interpolated linearly, Phi(0) = 0.
Variables (demeaned levels x~, 1990-2026 means; as macro_model_levels.py): policy rate, 10-year, mortgage spread, BBB spread, equities (100 ln CAPE), real dollar (100 ln);
version "+HP" adds house prices (100 ln price-to-rent).
    EP_K  eventual pressure (static):   Phi(K)' x~_t / G(K)                          K = 4 main; 8, 12 robustness
    CP_K  current pressure:             sum_{m=0}^{3K-1} phi_m' x~_{t-m} / G(K),   phi_m = Phi((m+1)/3) - Phi(m/3)   (one-period effects; they sum to Phi(K))
          (no pre-sample approximation: the first 3K-1 months are missing)
    GI_1yr, GI_3yr  growth over the next year (FCI-G form): sum_{m<L} [Phi((m+1)/3 + 4) - Phi((m+1)/3)]' dx_{t-m} / G(4),  L = 12 or 36 months
Check: EP_4 equals macro_model_levels.py.
Usage: python experimental/ms_fci/macro_model_v3.py
Outputs: macro_model_v3_monthly.csv, macro_model_v3_weights.csv
"""
import os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import macro_model_dl as DL

COLS0 = ["policy rate", "10-year", "mortgage spread", "BBB spread", "equities", "dollar"]


def lagsum(X, W):
    """sum_m W[m]' X_{t-m}; NaN until all lags are available."""
    T, M = len(X), len(W)
    out = np.full(T, np.nan)
    for t in range(M - 1, T):
        out[t] = sum(X[t - m] @ W[m] for m in range(M))
    return out


def main():
    x, comp = DL.levels_data()
    x = x.loc["1990-01":]
    P, G = DL.paths("base")
    out, wrows = {}, {}
    for hp, cols in (("", COLS0), ("+HP", COLS0 + ["house prices"])):
        X = x[cols].values
        for K in (4, 8, 12):
            phiK = DL.phi_at(P[cols], K)
            out[f"EP_{K}{hp}"] = X @ phiK.values / G[K]
            W = np.array([(DL.phi_at(P[cols], (m + 1) / 3) - DL.phi_at(P[cols], m / 3)).values for m in range(3 * K)]) / G[K]
            out[f"CP_{K}{hp}"] = lagsum(X, W)
            if hp == "+HP":
                wrows[f"EP_{K} (static weight)"] = phiK / G[K]
                for qq in range(K):
                    wrows[f"CP_{K} lag weight, quarter {qq + 1} (sum of its 3 months)"] = pd.Series(W[3 * qq:3 * qq + 3].sum(axis=0), index=cols)
        dX = x[cols].diff().values
        for lab, L in (("GI_1yr", 12), ("GI_3yr", 36)):
            Wg = np.array([(DL.phi_at(P[cols], (m + 1) / 3 + 4) - DL.phi_at(P[cols], (m + 1) / 3)).values for m in range(L)]) / G[4]
            out[f"{lab}{hp}"] = lagsum(np.nan_to_num(dX), Wg)
            out[f"{lab}{hp}"][:L] = np.nan
    D = pd.DataFrame(out, index=x.index)
    ref = DL.me(comp.drop(columns="house prices").sum(axis=1)).reindex(D.index)
    print(f"check EP_4 vs macro_model_levels.py: max abs diff {np.abs(D['EP_4'] - ref).max():.1e}")
    D.to_csv(os.path.join(HERE, "macro_model_v3_monthly.csv"), float_format="%.4f", index_label="month")
    Wt = pd.DataFrame(wrows).T
    Wt.to_csv(os.path.join(HERE, "macro_model_v3_weights.csv"), float_format="%.5f")
    pd.set_option("display.width", 220)
    print("\nweights (pp of funds rate per unit; equities and dollar per 1%, house prices per 1%):")
    print(Wt.round(4).to_string())
    S = D.loc["1993-01":]
    print("\nfrom 1993: mean, sd, latest")
    print(pd.DataFrame({"mean": S.mean(), "sd": S.std(), "latest": S.iloc[-1]}).round(2).T.to_string())


if __name__ == "__main__":
    main()
