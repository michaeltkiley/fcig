"""
Level version of the five-variable funds-rate-equivalent index: deviations of each variable from its 1990 to latest average, times the FRB/US
sensitivities (analysis/frbus_sensitivities.csv), summed. Positive = tighter than average conditions; units are pp of funds rate.

    level(t) = s10 * (y10 - mean) + sBBB * (BBB spread - mean) - sS * 100 (ln CAPE - mean) + sD * 100 (ln real dollar - mean)
               + sO * 100 (ln real WTI - mean)

Stationary transforms: stocks as the valuation multiple (CAPE from fcig_gs_daily.csv; the FRB/US stock shock moves the required return with earnings
fixed, i.e. valuation), the dollar in real terms (the FRB/US real exchange rate fpxr, the variable the dollar sensitivity was estimated on, put on a daily footing with the
nominal broad dollar), oil in real terms (WTI over the FRB/US PCE price level), the BBB spread as is, and the 10-year either nominal (default) or real
(less FRB/US ptr, the SPF 10-year expected PCE inflation, --real10). FRB/US history comes from federalreserve.gov (data_only_package), so FRED is only
needed for daily WTI (a saved copy is used when FRED is down). The sensitivities come from local shocks around a steady state, so applying them to large deviations over decades is a linear
extrapolation. Validation: the index plus the average funds rate should track the effective funds rate before 2008 and the SF Fed proxy funds rate after.

Usage:  python analysis/ms5_level.py [--horizon q4|q8|q12] [--real10]
Outputs: analysis/ms5_level_daily.csv, analysis/ms5_level.png
"""
import os, sys
import numpy as np, pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from fcig_replicate import fetch, fred, hold, RAW

HERE = os.path.dirname(os.path.abspath(__file__))
HORIZON = sys.argv[sys.argv.index("--horizon") + 1] if "--horizon" in sys.argv else "q4"
REAL10 = "--real10" in sys.argv
START = "1990-01-02"


def get(i):
    """Saved FRED file, refreshed when FRED answers (it sometimes returns a maintenance page)."""
    p = os.path.join(RAW, f"{i}.csv")
    body = fetch(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={i}")
    if body is not None and body.startswith(b"observation_date"):
        open(p, "wb").write(body)
    return fred(i)


def frbus_history():
    """Quarterly FRB/US history (federalreserve.gov data_only_package): real exchange rate fpxr, PCE price level pcnia, 10-year expected PCE
    inflation ptr, stamped at mid-quarter."""
    p = os.path.join(RAW, "frbus", "data_only_package", "HISTDATA.TXT")
    if not os.path.exists(p):
        import io, zipfile, urllib.request
        os.makedirs(os.path.join(RAW, "frbus"), exist_ok=True)
        req = urllib.request.Request("https://www.federalreserve.gov/econres/files/data_only_package.zip", headers={"User-Agent": "Mozilla/5.0"})
        zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(req, timeout=120).read())).extractall(os.path.join(RAW, "frbus"))
    h = pd.read_csv(p, index_col=0)
    h.columns = [c.lower() for c in h.columns]
    h = h[["fpxr", "pcnia", "ptr"]].astype(float)
    h.index = pd.PeriodIndex(h.index, freq="Q").to_timestamp() + pd.Timedelta(days=45)
    return h.dropna(how="all")


def to_daily(q, idx, log=False, extrapolate_growth=False):
    """Mid-quarter values interpolated (linearly, or in logs) to the daily index; after the last quarter held, or grown at the recent rate."""
    s = np.log(q) if log else q
    d = s.reindex(s.index.union(idx)).interpolate("time").reindex(idx)
    if extrapolate_growth:
        last = s.index[-1]
        g = (s.iloc[-1] - s.iloc[-5]) / (s.index[-1] - s.index[-5]).days
        d = d.where(idx <= last, s.iloc[-1] + g * (idx - last).days.values)
    else:
        d = d.ffill()
    return np.exp(d) if log else d


def build():
    G = pd.read_csv(os.path.join(ROOT, "fcig_gs_daily.csv"), parse_dates=["date"]).set_index("date")
    idx = G.loc[START:].index
    X = pd.DataFrame(index=idx)
    X["y10"], X["bbb"], X["ffr"] = G.x_y10, G.x_bbb, G.x_ffr
    X["lncape"] = np.log(G.x_cape)
    H = frbus_history()
    # real dollar: the model's own real exchange rate (trade weighted); quarterly ratio of fpxr to the nominal broad dollar applied to the daily nominal
    nom = G.x_usd
    nq = nom.groupby(nom.index.to_period("Q")).mean()
    nq.index = nq.index.to_timestamp() + pd.Timedelta(days=45)
    ratio = (H.fpxr / nq.reindex(H.index)).dropna()
    X["lnrusd"] = np.log(nom * to_daily(ratio, nom.index, log=True).bfill()).reindex(idx)
    # real oil: WTI over the PCE price level (interpolated; after the last quarter grown at its recent rate)
    wti = hold(get("DCOILWTICO"), idx[-1]).reindex(idx, method="ffill").clip(lower=5.0)   # WTI was negative on 20 Apr 2020
    X["lnroil"] = np.log(wti / to_daily(H.pcnia.dropna(), idx, log=True, extrapolate_growth=True).bfill())
    if REAL10:
        X["y10"] = X.y10 - to_daily(H.ptr.dropna(), idx).bfill()
    return X.dropna(), G


def level(X, S):
    m = X.mean()
    C = pd.DataFrame({
        "10-yr": S["rg10"] * (X.y10 - m.y10),
        "BBB spread": S["rbbbp"] * (X.bbb - m.bbb),
        "Equities": -S["req"] * 100 * (X.lncape - m.lncape),
        "Dollar": S["fpxr"] * 100 * (X.lnrusd - m.lnrusd),
        "Oil": S["poil"] * 100 * (X.lnroil - m.lnroil),
    })
    C["Total"] = C.sum(axis=1)
    return C


def main():
    S = pd.read_csv(os.path.join(HERE, "frbus_sensitivities.csv"), index_col=0)[f"ffr_eq_{HORIZON}"].to_dict()
    X, G = build()
    C = level(X, S)
    C.to_csv(os.path.join(HERE, "ms5_level_daily.csv"), float_format="%.4f", index_label="date")
    print(f"{HORIZON}, 10-year {'real' if REAL10 else 'nominal'}; sample {X.index[0].date()} to {X.index[-1].date()}")
    print("averages:", {k: round(float(v), 3) for k, v in X.mean().items()})
    print("\\nlatest vs average (pp of funds rate): ", C.iloc[-1].round(2).to_dict())
    print("percentile of today's total in the sample: %.0f%%" % (100 * (C.Total < C.Total.iloc[-1]).mean()))
    print("\\nselected dates:")
    for d in ("1990-06-29", "1994-12-30", "2000-03-31", "2007-06-29", "2009-03-31", "2012-12-31", "2018-12-31", "2020-03-31", "2021-12-31", "2023-10-31", "2026-02-27", "2026-08-27", str(C.index[-1].date())):
        r = C.loc[:d].iloc[-1]
        print(f"  {d}: total {r.Total:+.2f} | " + "  ".join(f"{k} {v:+.2f}" for k, v in r.drop("Total").items()))
    # validation against the effective funds rate and the SF Fed proxy funds rate
    effr = X.ffr
    w = None
    pth = os.path.join(RAW, "proxy-funds-rate-data.xlsx")
    if os.path.exists(pth):
        w = pd.read_excel(pth, sheet_name="Weekly", skiprows=1, names=["date", "ffr", "proxy"]).assign(date=lambda x: pd.to_datetime(x.date)).set_index("date").proxy
    print("\\nvalidation (index + average funds rate versus the actual / SF Fed proxy funds rate):")
    for lab, a, b in (("EFFR, 1990-2008-11", "1990-01-01", "2008-11-30"), ("EFFR, 2016-2019", "2016-01-01", "2019-12-31"), ("EFFR, 2022-2026", "2022-01-01", "2026-12-31")):
        c = C.Total[a:b]; e = effr[a:b]
        fit = c + effr.mean()
        print(f"  {lab}: corr {np.corrcoef(c, e)[0, 1]:+.2f}, index + mean EFFR minus EFFR: mean {float((fit[a:b] - e).mean()):+.2f}, rmse {float(np.sqrt(((fit[a:b] - e) ** 2).mean())):.2f}")
    if w is not None:
        cw = C.Total.reindex(w.index, method="ffill").loc[w.index.intersection(C.index)]
        for lab, a, b in (("proxy, 1990-2026", "1990-01-01", "2026-12-31"), ("proxy, 2009-2015", "2009-01-01", "2015-12-31"), ("proxy, 2020-2026", "2020-01-01", "2026-12-31")):
            ww = w[a:b].dropna(); cc = cw.reindex(ww.index).dropna(); ww = ww.reindex(cc.index)
            print(f"  {lab}: corr {np.corrcoef(cc, ww)[0, 1]:+.2f}, index + mean EFFR minus proxy: mean {float((cc + effr.mean() - ww).mean()):+.2f}, rmse {float(np.sqrt(((cc + effr.mean() - ww) ** 2).mean())):.2f}")
    plot(C, effr, w)


def plot(C, effr, w):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    pal = {"10-yr": "#1f77b4", "BBB spread": "#d62728", "Equities": "#2ca02c", "Dollar": "#9467bd", "Oil": "#ff7f0e"}
    fig, ax = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
    a = ax[0]
    pos = np.zeros(len(C)); neg = np.zeros(len(C))
    for k, c in pal.items():
        v = C[k].values
        a.fill_between(C.index, np.where(v >= 0, pos, neg), np.where(v >= 0, pos, neg) + v, color=c, alpha=0.75, lw=0, label=k)
        pos, neg = pos + np.clip(v, 0, None), neg + np.clip(v, None, 0)
    a.plot(C.index, C.Total, "k-", lw=1.0, label="total")
    a.axhline(0, color="k", lw=0.5)
    a.set_ylabel("pp of funds rate vs 1990-2026 average"); a.legend(fontsize=7, ncol=3, frameon=False, loc="upper right")
    a.set_title("Five-variable index in funds-rate equivalents, level vs average (positive = tighter)", fontsize=10)
    b = ax[1]
    b.plot(C.index, C.Total + effr.mean(), "k-", lw=1.0, label="index + average funds rate")
    b.plot(effr.index, effr, color="#1f77b4", lw=0.9, label="effective funds rate")
    if w is not None:
        b.plot(w.index, w.values, color="#d62728", lw=0.9, ls="--", label="SF Fed proxy funds rate")
    b.set_ylabel("percent"); b.legend(fontsize=7, frameon=False)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "ms5_level.png"), dpi=130)


if __name__ == "__main__":
    main()
