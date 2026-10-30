"""Read the public source files in data/ and build one monthly data set (monthly averages)."""
from pathlib import Path
import warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

ROOT = Path(__file__).resolve().parents[1]
DATA, OUT = ROOT / "data", ROOT / "output"
START, END = "1973-01", "2026-09"          # sample and zero-point window (each variable demeaned over it)


def fred(name, how="mean"):
    """FRED csv -> monthly series (mean or last observation in the month), PeriodIndex."""
    d = pd.read_csv(DATA / f"{name}.csv")
    s = pd.Series(pd.to_numeric(d.iloc[:, 1], errors="coerce").values, index=pd.to_datetime(d.iloc[:, 0])).dropna()
    g = s.groupby(s.index.to_period("M"))
    return g.mean() if how == "mean" else g.last()


def monthly_csv(name, col):
    d = pd.read_csv(DATA / name)
    return pd.Series(d[col].values, index=pd.PeriodIndex(d.iloc[:, 0], freq="M"))


def splice_log(new, old, overlap):
    """Extend `new` back with `old`, shifted in logs by their mean log gap over `overlap`."""
    k = float(np.log(new.loc[overlap]).mean() - np.log(old.loc[overlap]).mean())
    return pd.concat([old.loc[:new.index[0] - 1] * np.exp(k), new])


def mid_quarter(q):
    """Quarterly values placed in the middle month of each quarter, linearly interpolated, last value held."""
    m = pd.Series(q.values, index=[p.asfreq("M", "s") + 1 for p in q.index])
    full = pd.period_range(m.index[0], END, freq="M")
    return m.reindex(full).interpolate(limit_area="inside").ffill()


def unemployment_gap():
    u = fred("UNRATE")
    n = pd.read_csv(DATA / "NROU.csv"); n = pd.Series(n.iloc[:, 1].values, index=pd.PeriodIndex(pd.to_datetime(n.iloc[:, 0]), freq="Q"))
    return u - mid_quarter(n).reindex(u.index)


def expected_inflation():
    """Cleveland Fed 1- and 10-year expectations from 1982; before, the Livingston 12-month CPI expectation (semiannual, interpolated),
    shifted to each Cleveland series by the mean gap over 1982-84 and blended over 1982 (Cleveland weight 1/12 in January to 1 in December)."""
    lv = pd.read_excel(DATA / "livingston_median_growth.xlsx", "CPI").set_index("Date")["G_BP_To_12M"].dropna()
    lv.index = pd.to_datetime(lv.index).to_period("M")
    lv = lv.reindex(pd.period_range(lv.index[0], END, freq="M")).interpolate(limit_area="inside")
    out = {}
    for lab, name in (("einf_1y", "EXPINF1YR"), ("einf_10y", "EXPINF10YR")):
        c = fred(name)
        k = float((c.loc["1982-01":"1984-12"] - lv.loc["1982-01":"1984-12"]).mean())
        s = pd.concat([lv.loc[:c.index[0] - 1] + k, c])
        for i, m in enumerate(pd.period_range("1982-01", "1982-12", freq="M")):
            s.loc[m] = (1 - (i + 1) / 12) * (lv.loc[m] + k) + (i + 1) / 12 * c.loc[m]
        out[lab] = s
    return pd.DataFrame(out)


def rstar():
    """One-sided r* (full-sample estimation): Laubach-Williams (main) and Kiley (check), quarterly -> monthly."""
    r = pd.read_csv(DATA / "rstar_onesided.csv", index_col=0); r.index = pd.PeriodIndex(r.index, freq="Q")
    return pd.DataFrame({"rstar LW": mid_quarter(r.LW_onesided.dropna()), "rstar Kiley": mid_quarter(r.Kiley_onesided.dropna())})


def cape():
    """Shiller CAPE, spliced in logs (1990-92) to the monthly average of the daily CAPE behind the repository's GS replication (Shiller E10, multpl.com)."""
    g = pd.read_csv(DATA / "gs_daily.csv", parse_dates=["date"]).set_index("date").cape
    new = g.groupby(g.index.to_period("M")).mean()
    return splice_log(new, monthly_csv("shiller_cape.csv", "cape"), slice("1990-01", "1992-12"))


def stock_prices():
    """S&P 500, monthly average: Shiller, then FRED SP500 (log splice over the overlap)."""
    sh = monthly_csv("shiller_sp500.csv", "sp500"); fr = fred("SP500")
    ov = fr.index.intersection(sh.index)
    return pd.concat([sh.loc[:fr.index[0] - 1] * float(np.exp(np.log(fr.loc[ov]).mean() - np.log(sh.loc[ov]).mean())), fr])


def house_prices():
    """Nominal house prices: Case-Shiller national (from 1987), Shiller's index (real x CPI) before; after the last month, the trailing 6-month growth rate."""
    cpi = fred("CPIAUCSL")
    sh = monthly_csv("shiller_home_price.csv", "real_home_price") * cpi
    cs = fred("CSUSHPISA")
    h = pd.concat([sh.loc[:cs.index[0] - 1] * float(cs.iloc[0] / sh.loc[cs.index[0]]), cs]).dropna()
    g = np.log(h).diff().iloc[-6:].mean()
    ext = pd.period_range(h.index[-1] + 1, END, freq="M")
    return pd.concat([h, pd.Series(h.iloc[-1] * np.exp(g * np.arange(1, len(ext) + 1)), index=ext)])


def dollar_real():
    return splice_log(fred("RTWEXBGS"), fred("TWEXBPA"), slice("2006-01", "2006-12"))


def dollar_nominal():
    return splice_log(fred("DTWEXBGS"), fred("TWEXBMTH"), slice("2006-01", "2006-12"))


def build():
    """All monthly inputs, 1958 onward (house prices need a 15-year history before 1973)."""
    D = pd.DataFrame({
        "ffr": fred("FEDFUNDS"), "y10": fred("GS10"), "baa": fred("BAA"), "mortgage": fred("MORTGAGE30US"),
        "cape": cape(), "sp500": stock_prices(), "house": house_prices(), "rent": fred("CUUR0000SEHA"), "cpi": fred("CPIAUCSL"),
        "usd_real": dollar_real(), "usd_nominal": dollar_nominal(), "u_gap": unemployment_gap()})
    D = D.join(expected_inflation()).join(rstar())
    for c in ("rent", "cpi", "u_gap"):                  # October 2025: no CPI or unemployment release (government shutdown); interpolated
        D[c] = D[c].interpolate(limit_area="inside")
    return D.loc["1958-01":END]


def load():
    d = pd.read_csv(OUT / "data_monthly.csv", index_col=0); d.index = pd.PeriodIndex(d.index, freq="M")
    return d


def read(name):
    d = pd.read_csv(OUT / name, index_col=0); d.index = pd.PeriodIndex(d.index, freq="M")
    return d
