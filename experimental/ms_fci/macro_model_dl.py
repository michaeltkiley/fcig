"""
Distributed-lag macro-model index (DYNAMICS_PLAN.md, step 1b-1c), monthly, pp of funds rate, higher = tighter.

Uses the FRB/US cumulative GDP responses Phi_j(q) to a persistent unit shift in variable j (frbus_paths.csv) and the yardstick G(q) (frbus_hike_paths.csv, full 1 pp hike).
Monthly responses: a change of age m months has been in place (m+1)/3 quarters; Phi is interpolated linearly in quarters with Phi(0) = 0.
    STATIC_K  = Phi(K)' x_t / G(K)                                       (K = 4 reproduces macro_model_levels.py exactly in the base design)
    DL_K      = [ sum_{m < 3K} Phi((m+1)/3)' dx_{t-m} + Phi(K)' x_{t-3K} ] / G(K)
                effects assumed complete after K quarters; equals STATIC_K when x has been constant for K quarters (weighting note, Prop. 5)
    NYT_K     = STATIC_K - DL_K = sum_{m < 3K} [Phi(K) - Phi((m+1)/3)]' dx_{t-m} / G(K)   (recent moves not yet transmitted)
    GI        = sum_{m < 36} [Phi((m+1)/3 + 4) - Phi((m+1)/3)]' dx_{t-m} / G(4)   growth impulse over the next 4 quarters from the last 3 years of changes (FCI-G form; 1-year lookback: m < 12)
Designs: base = the weights of macro_model_levels.py (z expectations free, short rate with z fixed); zfixed = z expectations held fixed for every variable (one definition).
Variables (as in macro_model_levels.py, without house prices; with house prices as a second version): policy rate, 10-year, mortgage spread, BBB spread, equities (100 ln CAPE),
real dollar (100 ln), house prices (100 ln price-to-rent).
Usage: python experimental/ms_fci/macro_model_dl.py
Outputs: macro_model_dl_monthly.csv, macro_model_dl.png, macro_model_dl_fcig.png
"""
import os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import macro_model_levels as M

EXP = {"policy rate": "rshort", "10-year": "rg10", "mortgage spread": "rme", "BBB spread": "rbbbp", "equities": "req", "dollar": "fpxr", "house prices": "phouse"}


def me(s):
    s = s.resample("ME").last(); s.index = s.index.to_period("M"); return s


def paths(design):
    p = pd.read_csv(os.path.join(HERE, "frbus_paths.csv"))
    p = p[p["shape"] == "persistent"]
    out = {}
    for v, e in EXP.items():
        d = "zfixed" if (design == "zfixed" or e == "rshort") else "zfree"
        g = p[(p.design == d) & (p.experiment == e)].sort_values("quarter").gdp_per_unit.values
        out[v] = np.concatenate([[0.0], g])                  # index = quarters 0..32
    hk = pd.read_csv(os.path.join(HERE, "frbus_hike_paths.csv")).sort_values("quarter").gdp.values
    return pd.DataFrame(out), np.concatenate([[0.0], hk])


def phi_at(P, q):
    """Cumulative response at (fractional) quarter q for each variable (interpolated)."""
    qs = np.arange(len(P))
    return pd.Series({v: np.interp(q, qs, P[v].values) for v in P.columns})


def levels_data():
    """Monthly demeaned levels of each variable in its own units (recovered from the macro-model components and their q4 weights)."""
    comp, X, G = M.components(False, verbose=False)
    base = pd.read_csv(os.path.join(HERE, "frbus_sensitivities.csv"), index_col=0)["ffr_eq_q4"]
    ext = pd.read_csv(os.path.join(HERE, "frbus_sensitivities_ext.csv"), index_col=0)["ffr_eq_q4"]
    W = {"policy rate": ext["rshort_direct"], "10-year": base["rg10"], "mortgage spread": ext["rme"], "BBB spread": base["rbbbp"], "equities": -base["req"], "dollar": base["fpxr"], "house prices": ext["phouse"]}
    x = me(comp).apply(lambda c: c / W[c.name])
    return x, comp


def build(x, P, G, K, cols):
    T = len(x); dx = x[cols].diff()
    dx.iloc[0] = x[cols].iloc[0]                             # the initial level counts as a change in the distant past
    phiK = phi_at(P[cols], K)
    static = x[cols].values @ phiK.values / G[K]
    w = np.array([phi_at(P[cols], min((m + 1) / 3, K)).values for m in range(3 * K)])          # 3K x n
    dl = np.zeros(T); gi = np.zeros(T); gi1 = np.zeros(T)
    wgi = np.array([(phi_at(P[cols], (m + 1) / 3 + 4) - phi_at(P[cols], (m + 1) / 3)).values for m in range(36)])
    D = dx.values; L = x[cols].values
    for t in range(T):
        acc = 0.0
        for m in range(min(3 * K, t + 1)):
            acc += D[t - m] @ w[m]
        if t - 3 * K >= 0:
            acc += L[t - 3 * K] @ phiK.values
        else:
            pass                                             # before 3K months of history: the initial level is in D[0] with the weight of its age
        dl[t] = acc / G[K]
        gi[t] = sum(D[t - m] @ wgi[m] for m in range(min(36, t + 1))) / G[4]
        gi1[t] = sum(D[t - m] @ wgi[m] for m in range(min(12, t + 1))) / G[4]
    idx = x.index
    return pd.Series(static, idx), pd.Series(dl, idx), pd.Series(gi, idx), pd.Series(gi1, idx)


def main():
    x, comp = levels_data()
    x = x.loc["1990-01":]
    cols0 = ["policy rate", "10-year", "mortgage spread", "BBB spread", "equities", "dollar"]
    cols1 = cols0 + ["house prices"]
    out = {}
    for design in ("base", "zfixed"):
        P, G = paths(design)
        print(f"\n[{design}] weights per unit, Phi(K)/G(K), pp of funds rate:")
        print(pd.DataFrame({f"K={K}": phi_at(P, K) / G[K] for K in (1, 2, 4, 8, 12, 16, 24)}).round(4).to_string())
        for hp, cols in (("", cols0), ("+HP", cols1)):
            for K in (4, 8, 12):
                st, dl, gi, gi1 = build(x, P, G, K, cols)
                out[f"{design}{hp}|STATIC_{K}"] = st; out[f"{design}{hp}|DL_{K}"] = dl
                if K == 4:
                    out[f"{design}{hp}|GI_3yr"] = gi; out[f"{design}{hp}|GI_1yr"] = gi1
    D = pd.DataFrame(out)
    # check: STATIC_4 in the base design equals the macro-model levels index (monthly, demeaned)
    ref = me(comp.drop(columns="house prices").sum(axis=1)).loc[D.index]
    print(f"\ncheck STATIC_4 (base) vs macro_model_levels: max abs diff {np.abs(D['base|STATIC_4'] - ref).max():.2e}")
    D.to_csv(os.path.join(HERE, "macro_model_dl_monthly.csv"), float_format="%.4f", index_label="month")
    S = D.loc["1998-01":]                                   # first 8 years use an approximate pre-1990 history
    print("\nFrom 1998 (no house prices, base design): sd, latest, and correlation with STATIC_4")
    for c in [c for c in S if c.startswith("base|")]:
        print(f"  {c:16s} sd {S[c].std():.2f}  latest {S[c].iloc[-1]:+.2f}  corr levels {S[c].corr(S['base|STATIC_4']):.2f}  12m chg {S[c].diff(12).corr(S['base|STATIC_4'].diff(12)):.2f}")
    for K in (4, 8, 12):
        nyt = S[f"base|STATIC_{K}"] - S[f"base|DL_{K}"]
        print(f"  not-yet-transmitted (STATIC_{K} - DL_{K}): sd {nyt.std():.2f}, max abs {nyt.abs().max():.2f} ({nyt.abs().idxmax()}), latest {nyt.iloc[-1]:+.2f}")
    # by-variable not-yet-transmitted, K = 12, latest and at selected dates
    P, G = paths("base")
    for K in (12,):
        rows = {}
        for v in cols0:
            st, dl, _, _ = build(x, P, G, K, [v])
            rows[v] = (st - dl)
        R = pd.DataFrame(rows).loc["1998-01":]
        print(f"\nnot yet transmitted by variable (K={K}), selected months:")
        print(R.loc[[pd.Period(p, 'M') for p in ("2008-12", "2009-06", "2020-04", "2022-10", "2023-10", "2025-04", str(R.index[-1]))]].round(2).to_string())
    # FCI-G comparison
    f1 = pd.read_csv(os.path.join(ROOT, "raw", "fed_monthly_1yr.csv"), parse_dates=["date"]).set_index("date").iloc[:, 0]; f1.index = f1.index.to_period("M")
    f3 = pd.read_csv(os.path.join(ROOT, "raw", "fed_monthly_3yr.csv"), parse_dates=["date"]).set_index("date").iloc[:, 0]; f3.index = f3.index.to_period("M")
    J = pd.concat({"FCI-G 1yr": f1 / 0.4525, "FCI-G 3yr": f3 / 0.4525, "GI_1yr": S["base|GI_1yr"], "GI_3yr": S["base|GI_3yr"],
                   "STATIC_4 12m chg": S["base|STATIC_4"].diff(12), "DL_12": S["base|DL_12"]}, axis=1).dropna()
    print(f"\nFCI-G comparison ({J.index[0]}..{J.index[-1]}), correlations:\n" + J.corr().round(2).to_string())
    print("sd:", J.std().round(2).to_dict())
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    t = S.index.to_timestamp()
    fig, axes = plt.subplots(2, 1, figsize=(13, 10), sharex=True)
    axes[0].plot(t, S["base|STATIC_4"], color="#d62728", lw=1.4, label="Static levels index (q4 weights; current macro-model index)")
    axes[0].plot(t, S["base|DL_12"], color="#1f5fa8", lw=1.4, label="Distributed-lag index (FRB/US dynamics, effects complete after 12 quarters)")
    axes[0].plot(t, S["base|STATIC_12"], color="#7f7f7f", lw=1.0, ls="--", label="Static levels index (q12 weights)")
    axes[0].set_title("Macro-model index: static levels vs distributed lag, pp of funds rate (no house prices)", fontsize=11)
    axes[1].plot(t, S["base|STATIC_12"] - S["base|DL_12"], color="black", lw=1.3, label="Not yet transmitted (static q12 minus distributed lag)")
    axes[1].set_title("Effect of recent moves not yet transmitted to output, pp of funds rate", fontsize=11)
    for ax in axes:
        ax.axhline(0, color="gray", lw=0.8); ax.grid(alpha=0.25); ax.legend(loc="upper right", fontsize=9, frameon=False); ax.set_ylabel("pp of funds rate")
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "macro_model_dl.png"), dpi=130)
    fig, ax = plt.subplots(figsize=(13, 6))
    tj = J.index.to_timestamp()
    ax.plot(tj, J["FCI-G 1yr"], color="#1f5fa8", lw=1.4, label="FCI-G, 1-year lookback (official) / 0.4525")
    ax.plot(tj, J["GI_1yr"], color="#d62728", lw=1.4, label="Growth impulse from the FRB/US partial paths, 1-year lookback")
    ax.axhline(0, color="gray", lw=0.8); ax.grid(alpha=0.25); ax.legend(loc="upper right", fontsize=9, frameon=False); ax.set_ylabel("pp of funds rate")
    ax.set_title(f"FCI-G and the growth-impulse form of the macro-model index (corr {J['FCI-G 1yr'].corr(J['GI_1yr']):.2f})", fontsize=11)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "macro_model_dl_fcig.png"), dpi=130)


if __name__ == "__main__":
    main()
