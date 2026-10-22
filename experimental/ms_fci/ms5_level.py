"""
Level version of the five-variable funds-rate-equivalent index: deviations of each variable from its 1990 to latest average, times the FRB/US
sensitivities (experimental/ms_fci/frbus_sensitivities.csv), summed. Positive = tighter than average conditions; units are pp of funds rate.

    level(t) = s10 * (y10 - mean) + sBBB * (BBB spread - mean) - sS * 100 (ln CAPE - mean) + sD * 100 (ln real dollar - mean)
               + sO * 100 (ln real WTI - mean)

Stationary transforms: stocks as the valuation multiple (CAPE from fcig_gs_daily.csv; the FRB/US stock shock moves the required return with earnings
fixed, i.e. valuation), the dollar in real terms (the FRB/US real exchange rate fpxr, the variable the dollar sensitivity was estimated on, put on a daily footing with the
nominal broad dollar), oil in real terms (WTI over the FRB/US PCE price level), the BBB spread as is, and the 10-year either nominal (default) or real
(less FRB/US ptr, the SPF 10-year expected PCE inflation, --real10). FRB/US history comes from federalreserve.gov (data_only_package), so FRED is only
needed for daily WTI (a saved copy is used when FRED is down). The sensitivities come from local shocks around a steady state, so applying them to large deviations over decades is a linear
extrapolation. Validation: the index plus the average funds rate should track the effective funds rate before 2008 and the SF Fed proxy funds rate after.

Real-rate adjustments: --rstar measures the 10-year as the real yield gap to Kiley's r* (kiley_rstar.csv in this folder, copied from the r* repo; one-sided
estimate, --twosided for the smoothed one); --erp removes from the equity valuation (100 ln CAPE) the part explained by the real 10-year yield, using the FRB/US
stock equation (25% on the price per 1 pp of required return). NOT RECOMMENDED: in the data the valuation has no stable relation with the real
10-year yield (daily 1990-2026 slope -1.2% per pp, s.e. 2.7; monthly changes ~0; by sub-period -17% to +24%), so the model's mapping overstates the
adjustment and pushes the 2009-2012 equity term to +2.4 to +3.1 pp of tightening. Kept for comparison only.

Usage:  python experimental/ms_fci/ms5_level.py [--horizon q4|q8|q12] [--real10] [--rstar] [--erp] [--source fred|frbus]
Outputs: experimental/ms_fci/ms5_level_daily[_variant].csv, experimental/ms_fci/ms5_level[_variant].png (variant suffix: _real10, _rstar, plus _erp)
"""
import os, sys
import numpy as np, pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from fcig_replicate import fetch, fred, hold, RAW

HERE = os.path.dirname(os.path.abspath(__file__))
HORIZON = sys.argv[sys.argv.index("--horizon") + 1] if "--horizon" in sys.argv else "q4"
REAL10 = "--real10" in sys.argv
RSTAR = "--rstar" in sys.argv        # 10-year as the real yield gap to the equilibrium real rate r*
ERP = "--erp" in sys.argv            # equities as the equity risk premium (earnings yield less the real 10-year) instead of the CAPE multiple
RSTAR_COL = "rstar_2side" if "--twosided" in sys.argv else "rstar_1side"
TAG = ("_rstar" if RSTAR else "_real10" if REAL10 else "") + ("_erp" if ERP else "")
START = "1990-01-02"
SOURCE = sys.argv[sys.argv.index("--source") + 1] if "--source" in sys.argv else "fred"   # fred (default) or frbus


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


def monthly_to_daily(m, idx, extrapolate=False):
    """Monthly series (stamped at the month start; value taken as mid-month) interpolated in time to the daily index; after the last month held, or
    for a price level grown at its last 12-month rate."""
    m = m.dropna().copy()
    m.index = m.index + pd.Timedelta(days=14)
    s = np.log(m) if extrapolate else m
    d = s.reindex(s.index.union(idx)).interpolate("time").reindex(idx)
    if extrapolate:
        g = (s.iloc[-1] - s.iloc[-13]) / (s.index[-1] - s.index[-13]).days
        d = d.where(idx <= s.index[-1], s.iloc[-1] + g * (idx - s.index[-1]).days.values)
        return np.exp(d).bfill()
    return d.ffill().bfill()


def build():
    G = pd.read_csv(os.path.join(ROOT, "fcig_gs_daily.csv"), parse_dates=["date"]).set_index("date")
    idx = G.loc[START:].index
    X = pd.DataFrame(index=idx)
    X["y10"], X["bbb"], X["ffr"] = G.x_y10, G.x_bbb, G.x_ffr
    X["lncape"] = np.log(G.x_cape)
    H = frbus_history()
    nom = G.x_usd
    # quarterly FRB/US real-exchange-rate ratio (fpxr over the quarterly mean of the nominal broad dollar)
    nq = nom.groupby(nom.index.to_period("Q")).mean()
    nq.index = nq.index.to_timestamp() + pd.Timedelta(days=45)
    ratio_q = (H.fpxr / nq.reindex(H.index)).dropna()
    ratio = to_daily(ratio_q, nom.index, log=True).bfill()
    if SOURCE == "fred":
        # FRED real broad dollar (RTWEXBGS, 2006 on) over the nominal monthly mean; before 2006 the FRB/US ratio, level-matched over 2006-2010
        real = get("RTWEXBGS")
        nm = nom.groupby(nom.index.to_period("M")).mean()
        nm.index = nm.index.to_timestamp()
        rm = (real / nm.reindex(real.index)).dropna()
        rm_d = monthly_to_daily(rm, nom.index)
        ov = (nom.index >= "2006-03-01") & (nom.index <= "2010-12-31")
        scale = float(rm_d[ov].mean() / ratio[ov].mean())
        ratio = ratio.where(nom.index < real.index[0] + pd.Timedelta(days=45), np.nan).mul(scale).fillna(rm_d)
        price = monthly_to_daily(get("CPIAUCSL"), idx, extrapolate=True)
        einf = monthly_to_daily(get("EXPINF10YR"), idx)
    else:
        price = to_daily(H.pcnia.dropna(), idx, log=True, extrapolate_growth=True).bfill()
        einf = to_daily(H.ptr.dropna(), idx).bfill()
    X["lnrusd"] = np.log(nom * ratio).reindex(idx)
    wti = hold(get("DCOILWTICO"), idx[-1]).reindex(idx, method="ffill").clip(lower=5.0)   # WTI was negative on 20 Apr 2020
    X["lnroil"] = np.log(wti / price)
    real10 = X.y10 - einf
    X["real10"] = real10
    r = pd.read_csv(os.path.join(HERE, "kiley_rstar.csv"), index_col=0)[RSTAR_COL]   # Kiley r*, quarterly, from the r* repo
    r.index = pd.PeriodIndex(r.index, freq="Q").to_timestamp() + pd.Timedelta(days=45)
    X["rstar"] = to_daily(r.dropna(), idx).bfill()
    X["einf"] = einf
    if RSTAR:
        X["y10"] = real10 - X.rstar                                 # real 10-year yield gap to r*
    elif REAL10:
        X["y10"] = real10
    return X.dropna(), G


def level(X, S, req_pct_per_pp=None):
    m = X.mean()
    C = pd.DataFrame({
        "10-yr": S["rg10"] * (X.y10 - m.y10),
        "BBB spread": S["rbbbp"] * (X.bbb - m.bbb),
        # stock valuation in % (100 ln CAPE); with --erp the part explained by real rates is removed (FRB/US: ln price = ... - 0.25 * required return,
        # required return = real long rate + premium), leaving the equity-premium part, so real rates are not counted in both the 10-year and equity terms
        "Equities": -S["req"] * (100 * (X.lncape - m.lncape) + (req_pct_per_pp * (X.real10 - m.real10) if ERP else 0.0)),
        "Dollar": S["fpxr"] * 100 * (X.lnrusd - m.lnrusd),
        "Oil": S["poil"] * 100 * (X.lnroil - m.lnroil),
    })
    C["Total"] = C.sum(axis=1)
    return C


def main():
    sens = pd.read_csv(os.path.join(HERE, "frbus_sensitivities.csv"), index_col=0)
    S = sens[f"ffr_eq_{HORIZON}"].to_dict()
    req_pct_per_pp = float(sens.loc["req", "unit_size"])   # % fall in stock wealth per +1 pp on the required return (about 25)
    X, G = build()
    C = level(X, S, req_pct_per_pp)
    C.to_csv(os.path.join(HERE, f"ms5_level_daily{TAG}.csv"), float_format="%.4f", index_label="date")
    print(f"{HORIZON}, 10-year {'real gap to r* (' + RSTAR_COL + ')' if RSTAR else 'real' if REAL10 else 'nominal'}, equities {'CAPE valuation net of real rates' if ERP else 'CAPE valuation'}; sample {X.index[0].date()} to {X.index[-1].date()}")
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
    gap = (X.ffr - X.einf - X.rstar)                      # real policy rate less r*: the policy stance relative to neutral
    print("  vs real policy rate gap (EFFR - expected inflation - r*): corr %+.2f (1990-2026), %+.2f (1990-2008), %+.2f (2009-2015), %+.2f (2016-2019), %+.2f (2022-2026)" % tuple(
        np.corrcoef(C.Total[a:b], gap[a:b])[0, 1] for a, b in (("1990", "2026"), ("1990", "2008-11"), ("2009", "2015"), ("2016", "2019"), ("2022", "2026"))))
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
    fig.tight_layout(); fig.savefig(os.path.join(HERE, f"ms5_level{TAG}.png"), dpi=130)


if __name__ == "__main__":
    main()
