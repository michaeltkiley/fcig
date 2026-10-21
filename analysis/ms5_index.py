"""
Five-variable financial conditions index in federal funds rate equivalents (a reconstruction; see notes/morgan_stanley_fci.md).

    FFReq(t) = s10 * d(10-yr yield, pp) + sBBB * d(BBB spread, pp) - sS * 100 dln(S&P 500) + sD * 100 dln(broad dollar)
               + sO * 100 dln(WTI oil),     all changes from a base date,

with the sensitivities s from FRB/US (analysis/frbus_sensitivities.csv: the GDP effect of each variable relative to that of the funds
rate, at the q4, q8 or q12 horizon). Positive = tighter. Divide by 0.25 for "25 bp hike equivalents".

Data: FRED DGS10, ICE BofA BBB option-adjusted spread (history/bbb_oas.csv, FRED BAMLC0A4CBBB), S&P 500 (history/sp500.csv, FRED SP500),
the Fed's broad dollar index DTWEXBGS extended with the ICE dollar index (history/dxy.csv) and then held, and WTI (FRED DCOILWTICO).
The Morgan Stanley index is not published, so this is a stand-in built from the described method. The date of the Iran conflict is not
established here, so the output scans base dates; it also compares with the SF Fed proxy funds rate (raw/proxy-funds-rate-data.xlsx if present).

Usage:  python analysis/ms5_index.py [--horizon q4|q8|q12]   (run analysis/frbus_sensitivities.py first)
Outputs: analysis/ms5_index_daily.csv (contributions to the change since BASE, in pp of funds rate equivalent)
"""
import os, sys
import numpy as np, pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from fcig_replicate import fetch, fred, read_hist, extend_dollar, hold, RAW

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "2026-02-27"
HORIZON = sys.argv[sys.argv.index("--horizon") + 1] if "--horizon" in sys.argv else "q4"


def wti():
    p = os.path.join(RAW, "DCOILWTICO.csv")
    body = fetch("https://fred.stlouisfed.org/graph/fredgraph.csv?id=DCOILWTICO")
    if body is not None:
        open(p, "wb").write(body)
    return fred("DCOILWTICO")


def inputs():
    y10 = fred("DGS10")
    oas = read_hist("bbb_oas.csv")
    sp = read_hist("sp500.csv")
    usd = fred("DTWEXBGS")
    usd, _ = extend_dollar(usd, read_hist("dxy.csv"))
    end = max(y10.index[-1], sp.index[-1], oas.index[-1])
    idx = sp["2025-06-01":].index
    X = pd.DataFrame(index=idx)
    for name, s in (("y10", y10), ("bbb", oas), ("sp", sp), ("usd", usd), ("oil", wti())):
        X[name] = hold(s, end).reindex(idx, method="ffill")
    return X.dropna()


def contributions(X, base, S):
    b = X.loc[:base].iloc[-1]
    d = X.loc[base:]
    out = pd.DataFrame({
        "10-yr": S["rg10"] * (d.y10 - b.y10),
        "BBB spread": S["rbbbp"] * (d.bbb - b.bbb),
        "Equities": -S["req"] * 100 * np.log(d.sp / b.sp),      # stocks up = looser
        "Dollar": S["fpxr"] * 100 * np.log(d.usd / b.usd),
        "Oil": S["poil"] * 100 * np.log(d.oil / b.oil),
    })
    out["Total"] = out.sum(axis=1)
    return out


def main():
    s = pd.read_csv(os.path.join(HERE, "frbus_sensitivities.csv"), index_col=0)
    S = s[f"ffr_eq_{HORIZON}"].to_dict()
    print(f"sensitivities (funds-rate pp per unit, {HORIZON}):", {k: round(v, 3) for k, v in S.items() if k != "rff"})
    X = inputs()
    print("inputs through", X.index[-1].date(), "| latest:", X.iloc[-1].round(2).to_dict())
    C = contributions(X, BASE, S)
    C.to_csv(os.path.join(HERE, "ms5_index_daily.csv"), float_format="%.4f", index_label="date")

    print(f"\nChange since {BASE} in funds-rate equivalents (pp; 25 bp hikes in brackets):")
    for d in ("2026-04-01", "2026-05-01", "2026-06-01", "2026-07-01", "2026-07-10", "2026-07-20", "2026-08-31", "2026-09-30", str(C.index[-1].date())):
        r = C.loc[:d].iloc[-1]
        print(f"  {d}: total {r.Total:+.2f} ({r.Total / 0.25:+.1f})  | " + "  ".join(f"{k} {v:+.2f}" for k, v in r.drop("Total").items()))

    print("\nBase-date scan: change to 2026-07-10 (hikes of 25 bp) for several base dates:")
    for b in ("2026-01-30", "2026-02-13", "2026-02-27", "2026-03-06", "2026-03-13", "2026-03-27", "2026-04-10"):
        r = contributions(X, b, S).loc[:"2026-07-10"].iloc[-1]
        print(f"  from {b}: {r.Total:+.2f} ({r.Total / 0.25:+.1f})")

    p = os.path.join(RAW, "proxy-funds-rate-data.xlsx")
    proxy = None
    if os.path.exists(p):
        w = pd.read_excel(p, sheet_name="Weekly", skiprows=1, names=["date", "ffr", "proxy"]).assign(date=lambda x: pd.to_datetime(x.date)).set_index("date")
        print("\nSF Fed proxy funds rate change since", BASE, "(pp): ", {d: round(float(w.proxy[:d].iloc[-1] - w.proxy[:BASE].iloc[-1]), 2) for d in ("2026-07-10", "2026-10-09")})
        proxy = (w.proxy[BASE:] - w.proxy[:BASE].iloc[-1])
    plot(C, proxy)


def plot(C, proxy):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    pal = {"10-yr": "#1f77b4", "BBB spread": "#d62728", "Equities": "#2ca02c", "Dollar": "#9467bd", "Oil": "#ff7f0e"}
    fig, ax = plt.subplots(figsize=(10, 4.8))
    pos = np.zeros(len(C)); neg = np.zeros(len(C))
    for k, c in pal.items():
        v = C[k].values
        ax.fill_between(C.index, np.where(v >= 0, pos, neg), np.where(v >= 0, pos, neg) + v, color=c, alpha=0.75, lw=0, label=k)
        pos, neg = pos + np.clip(v, 0, None), neg + np.clip(v, None, 0)
    ax.plot(C.index, C.Total, "k-", lw=1.6, label="total (five-variable stand-in)")
    if proxy is not None:
        ax.plot(proxy.index, proxy.values, color="#555555", ls="--", lw=1.3, label="SF Fed proxy funds rate (change)")
    ax.axhline(0, color="k", lw=0.6)
    ax.set_ylabel(f"pp of funds rate equivalent since {BASE}")
    ax2 = ax.secondary_yaxis("right", functions=(lambda y: y / 0.25, lambda y: y * 0.25)); ax2.set_ylabel("25 bp hike equivalents")
    ax.set_title(f"Five-variable index from FRB/US sensitivities ({HORIZON}); positive = tighter", fontsize=10)
    ax.legend(fontsize=7, ncol=2, frameon=False, loc="upper left")
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "ms5_index.png"), dpi=130)


if __name__ == "__main__":
    main()
