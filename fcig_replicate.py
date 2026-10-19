"""
Replicate the Federal Reserve Board's Financial Conditions Impulse on Growth (FCI-G) from public data.

Method: Ajello, Cavallo, Favara, Peterman, Schindler & Sinha (2023), "A New Index to Measure
U.S. Financial Conditions," FEDS Notes, Technical Appendix, with the Fed's published weights
(multipliers.csv from the Fed's code release; Table 1 of the note).

    FCI-G_t = sum_j sum_{i=0}^{T-1} w_i^j * dX^j_{t-3i months},   T = 12 (baseline) or 4 (one-year lookback)

    dX for rates and yields : 3-month average of daily values minus the previous 3-month average (pp)
    dX for stocks, houses   : 100 * 3-month log change in the level (%)
    dX for the dollar       : 100 * log change in the 3-month average level (%)

Inputs (public):
    FFR       FRED DFF                 effective federal funds rate
    10Y       FRED DGS10               10-year Treasury yield
    Mortgage  FRED MORTGAGE30US        Freddie Mac PMMS 30-year fixed (weekly)
    BBB       FRED BAMLC0A4CBBBEY      ICE BofA BBB effective yield; FRED shows only ~3 years, so the
                                       history is kept in history/bbb_ice.csv and earlier changes use
                                       Moody's Baa (FRED DBAA)
    Stocks    Dow Jones U.S. Total Stock Market Index (Yahoo ^DWCF), kept in history/dwcf.csv;
              before 1995 the S&P 500 (history/gspc_pre1995.csv). Days not yet available from Yahoo
              are filled with S&P 500 changes (FRED SP500) and replaced when Yahoo data arrive.
    Houses    Zillow ZHVI, United States, mid-tier, smoothed and seasonally adjusted (from 2000);
              Case-Shiller national (FRED CSUSHPISA) before 2000
    Dollar    Nominal broad dollar (FRED DTWEXBGS), earlier TWEXB and TWEXBMTH

Usage:
    python fcig_replicate.py            # download, update history, write outputs
    python fcig_replicate.py --offline  # recompute from files already in raw/ and history/
Outputs: data.json (for index.html), fcig_replication_daily.csv, fcig_replication_monthly.csv
"""
import argparse, datetime as dt, json, os, re, time, urllib.request
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RAW, HIST = os.path.join(HERE, "raw"), os.path.join(HERE, "history")
COLS = ["FFR", "10Yr Treasury", "Mortgage Rate", "BBB", "Stock Market", "House Prices", "Dollar"]
DAILY_START = "2020-01-01"  # earliest comparison date offered on the page

FRED_IDS = ["DFF", "DGS10", "MORTGAGE30US", "BAMLC0A4CBBBEY", "DBAA", "DTWEXBGS", "TWEXB", "TWEXBMTH",
            "CSUSHPISA", "SP500"]
FEDN = "https://www.federalreserve.gov/econres/notes/feds-notes/"
REQUIRED = {f"{i}.csv": f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={i}" for i in FRED_IDS}
REQUIRED.update({
    "zhvi.csv": "https://files.zillowstatic.com/research/public_csvs/zhvi/Metro_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv",
    "fed_monthly_3yr.csv": FEDN + "fci_g_public_monthly_3yr.csv",
    "fed_monthly_1yr.csv": FEDN + "fci_g_public_monthly_1yr.csv",
})
OPTIONAL = {
    "y_DWCF.json": "https://query2.finance.yahoo.com/v8/finance/chart/%5EDWCF?range=3mo&interval=1d",
    "fomc.html": "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
}
# Fallback when Yahoo's data API rate-limits: the quote page shows the latest close.
YAHOO_QUOTE = ("y_DWCF_quote.html", "https://finance.yahoo.com/quote/%5EDWCF/")
UA = "fcig-replication/1.0 (+https://michaeltkiley.github.io/fcig/)"  # FRED rejects generic browser UAs
UA_YAHOO = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

# Weights signed so that tightening raises the index; rows are quarters back 0..11.
W_ALL = -pd.read_csv(os.path.join(HERE, "multipliers.csv")).values  # 20 rows: beta_{i+4} - beta_i
W_ALL[:, 4:6] *= -1  # the Fed's code enters stock and house-price changes with the opposite sign
W = W_ALL[:12]


# ---------------------------------------------------------------- download

def fetch(url, tries=3, timeout=30):
    ua = UA_YAHOO if "yahoo" in url else UA
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": ua})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read()
            if len(body) < 200:
                raise ValueError(f"response too short ({len(body)} bytes)")
            return body
        except Exception as e:
            print(f"    attempt {k + 1} failed: {e}", flush=True)
            if k + 1 < tries:
                time.sleep(5 * (k + 1))
    return None


def download():
    os.makedirs(RAW, exist_ok=True)
    failed = []
    for fn, url in list(REQUIRED.items()) + list(OPTIONAL.items()):
        t = time.time()
        body = fetch(url)
        if body is None:
            print(f"  {fn:24s} FAILED", flush=True)
            if fn in REQUIRED:
                failed.append(fn)
            continue
        with open(os.path.join(RAW, fn + ".tmp"), "wb") as f:
            f.write(body)
        os.replace(os.path.join(RAW, fn + ".tmp"), os.path.join(RAW, fn))
        print(f"  {fn:24s} {len(body):>9,d} bytes  {time.time() - t:4.1f}s", flush=True)
    if not os.path.exists(os.path.join(RAW, "y_DWCF.json")) or os.path.getmtime(os.path.join(RAW, "y_DWCF.json")) < time.time() - 3600:
        fn, url = YAHOO_QUOTE
        body = fetch(url, tries=2)
        if body is not None:
            with open(os.path.join(RAW, fn), "wb") as f:
                f.write(body)
            print(f"  {fn:24s} {len(body):>9,d} bytes", flush=True)
    if failed:
        raise SystemExit(f"download failed for required inputs: {', '.join(failed)}")


# ---------------------------------------------------------------- inputs

def fred(i):
    d = pd.read_csv(os.path.join(RAW, f"{i}.csv"), na_values=["."])
    return pd.Series(d.iloc[:, 1].values, index=pd.to_datetime(d.iloc[:, 0]), dtype=float).dropna()


def read_hist(name):
    d = pd.read_csv(os.path.join(HIST, name))
    return pd.Series(d.iloc[:, 1].values, index=pd.to_datetime(d.iloc[:, 0]), dtype=float).dropna()


def write_hist(name, s, col):
    s.rename(col).rename_axis("date").to_frame().to_csv(os.path.join(HIST, name), date_format="%Y-%m-%d", float_format="%.4f")


def update_history():
    """Merge freshly downloaded ICE BBB and Dow Jones Total Market data into the stored histories."""
    bbb = read_hist("bbb_ice.csv")
    new = fred("BAMLC0A4CBBBEY")
    bbb = new.combine_first(bbb).sort_index()
    write_hist("bbb_ice.csv", bbb, "bbb_ice")
    p = os.path.join(RAW, "y_DWCF.json")
    if os.path.exists(p) and os.path.getmtime(p) > time.time() - 6 * 3600:
        try:
            j = json.load(open(p))["chart"]["result"][0]
            idx = (pd.to_datetime(j["timestamp"], unit="s").tz_localize("UTC")
                   .tz_convert("America/New_York").normalize().tz_localize(None))
            y = pd.Series(j["indicators"]["quote"][0]["close"], index=idx, dtype=float).dropna()
            y = y[~y.index.duplicated(keep="last")]
            dw = read_hist("dwcf.csv")
            write_hist("dwcf.csv", y.combine_first(dw).sort_index(), "dwcf")
        except Exception as e:
            print("  Yahoo data unusable:", e)
    else:
        q = quote_close()
        if q is not None:
            dw = read_hist("dwcf.csv")
            if q[0] not in dw.index or abs(dw.loc[q[0]] - q[1]) > 0.01:
                dw.loc[q[0]] = q[1]
                write_hist("dwcf.csv", dw.sort_index(), "dwcf")
            print(f"  Dow Jones Total Market close from quote page: {q[0].date()} {q[1]:,.2f}")


def quote_close():
    """(date, close) from Yahoo's quote page, only when it shows a completed session ("At close")."""
    p = os.path.join(RAW, YAHOO_QUOTE[0])
    if not os.path.exists(p) or os.path.getmtime(p) < time.time() - 6 * 3600:
        return None
    t = open(p, encoding="utf-8", errors="ignore").read()
    price = re.search(r'data-testid="qsp-price"[^>]*>\s*([0-9][0-9,]*\.[0-9]+)', t)
    when = re.search(r"At close:\s*([A-Z][a-z]+) (\d{1,2}) at", t)
    if not (price and when and when.group(1) in MONTHS):
        return None
    today = dt.date.today()
    d = dt.date(today.year, MONTHS[when.group(1)], int(when.group(2)))
    if d > today:  # December close read in January
        d = d.replace(year=today.year - 1)
    return pd.Timestamp(d), float(price.group(1).replace(",", ""))


def stocks():
    """Dow Jones Total Market, spliced with the S&P 500 before 1995 and extended with S&P 500 changes."""
    dw, sp_old, sp = read_hist("dwcf.csv"), read_hist("gspc_pre1995.csv"), fred("SP500")
    s = splice_level(dw, sp_old)
    tail = sp[sp.index > dw.index[-1]]
    proxy_from = None
    if len(tail) and dw.index[-1] in sp.index:
        s = pd.concat([s, dw.iloc[-1] * tail / sp.loc[dw.index[-1]]])
        proxy_from = tail.index[0]
    return s, proxy_from


def zillow():
    z = pd.read_csv(os.path.join(RAW, "zhvi.csv"))
    r = z[z.RegionName == "United States"].iloc[0, 5:].astype(float)
    r.index = pd.to_datetime(r.index)
    return r.dropna()


def splice_level(primary, back):
    b = back[back.index <= primary.index[0]]
    return pd.concat([b[b.index < primary.index[0]] * primary.iloc[0] / b.iloc[-1], primary])


def splice_diff(primary, back):
    b = back[back.index <= primary.index[0]]
    return pd.concat([b[b.index < primary.index[0]] + primary.iloc[0] - b.iloc[-1], primary])


def series():
    stk, proxy_from = stocks()
    S = {
        "FFR": ("avg", fred("DFF")),
        "10Yr Treasury": ("avg", fred("DGS10")),
        "Mortgage Rate": ("avg", fred("MORTGAGE30US")),
        "BBB": ("avg", splice_diff(read_hist("bbb_ice.csv"), fred("DBAA"))),
        "Stock Market": ("loglevel", stk),
        "House Prices": ("loglevel", splice_level(zillow(), fred("CSUSHPISA"))),
        "Dollar": ("logavg", splice_level(splice_level(fred("DTWEXBGS"), fred("TWEXB")), fred("TWEXBMTH"))),
    }
    return S, proxy_from


def hold(s, end):
    """Carry the last value forward on business days up to `end`."""
    d = pd.bdate_range(s.index[-1] + pd.Timedelta(days=1), end)
    return pd.concat([s, pd.Series(s.iloc[-1], index=d)])


def extend_dollar(usd, dxy):
    """Extend the broad dollar past FRED's lag with ICE dollar index (DXY) changes, once saved DXY closes
    overlap the FRED data. Returns (series, first extended date or None); callers then hold the last value."""
    if dxy is None or not len(dxy):
        return usd, None
    both = dxy.index.intersection(usd.index)
    tail = dxy[dxy.index > usd.index[-1]]
    if not len(both) or not len(tail):
        return usd, None
    ext = usd.loc[both[-1]] * tail / dxy.loc[both[-1]]
    return pd.concat([usd, ext]), tail.index[0]


def fill(S, end, dxy=None):
    """Carry each input forward to `end` (the last equity trading day) with a simple rule, so series that
    publish with a lag or less often than daily are not left out of the latest averages:
      FFR, 10Y, BBB          constant at the last value
      Dollar                 ICE dollar index changes once saved closes overlap FRED's data, then constant
      Mortgage rate          10-year Treasury plus the average of the last four weekly spreads, on the
                             Thursdays (the PMMS day) after the last survey
      House prices           monthly, at the trailing six-month average growth rate, for each month-end
                             up to `end`
    Real observations are never changed; only dates after each series' last observation are added."""
    S = dict(S)
    end = pd.Timestamp(end)
    for c in ("FFR", "10Yr Treasury", "BBB"):
        S[c] = (S[c][0], hold(S[c][1], end))
    k, s = S["Dollar"]
    S["Dollar"] = (k, hold(extend_dollar(s, dxy)[0], end))
    y10 = S["10Yr Treasury"][1]
    k, m = S["Mortgage Rate"]
    spread = (m - y10.reindex(m.index)).dropna().iloc[-4:].mean()
    thu = pd.date_range(m.index[-1] + pd.Timedelta(days=7), end, freq="7D")
    S["Mortgage Rate"] = (k, pd.concat([m, y10.reindex(thu) + spread]))
    k, h = S["House Prices"]
    g = np.log(h).diff().iloc[-6:].mean()
    me = pd.date_range(h.index[-1] + pd.offsets.MonthEnd(1), end, freq="ME")
    if len(me):
        S["House Prices"] = (k, pd.concat([h, pd.Series(h.iloc[-1] * np.exp(g * np.arange(1, len(me) + 1)), index=me)]))
    return S


# ---------------------------------------------------------------- index

def changes_at(S, d):
    """Three-month changes for each variable over the 12 quarters ending at date d (rows i = 0..11)."""
    d = pd.Timestamp(d)
    month_end = (d + pd.offsets.BDay(1)).month != d.month or d == d + pd.offsets.MonthEnd(0)
    if month_end:  # like the Fed's code, month-end dates step back to calendar month-ends
        ends = [d - pd.DateOffset(months=3 * i) + pd.offsets.MonthEnd(0) for i in range(14)]
    else:
        ends = [d - pd.DateOffset(months=3 * i) for i in range(14)]
    out = np.full((12, 7), np.nan)
    for j, c in enumerate(COLS):
        kind, s = S[c]
        for i in range(12):
            hi, mid, lo = ends[i], ends[i + 1], ends[i + 2]
            if kind == "loglevel":
                a, b = s[:hi], s[:mid]
                if len(b) and s.index[0] <= mid:
                    out[i, j] = 100 * (np.log(a.iloc[-1]) - np.log(b.iloc[-1]))
            elif s.index[0] <= lo:
                cur = s[(s.index > mid) & (s.index <= hi)].mean()
                prev = s[(s.index > lo) & (s.index <= mid)].mean()
                out[i, j] = cur - prev if kind == "avg" else 100 * (np.log(cur) - np.log(prev))
    return out


def fci_at(S, d):
    """FCI-G (effect on growth over the next four quarters) and the "next year" measure: the effect
    of the same past changes on growth in the following four quarters, if financial variables hold
    where they are. Row i of the weights is beta_{i+4} - beta_i, so the next-year weight on a change
    made i quarters ago is row i + 4 (beta_{i+8} - beta_{i+4})."""
    D = changes_at(S, d)
    r = {}
    for T, k in ((12, "3yr"), (4, "1yr")):
        comp = (D[:T] * W[:T]).sum(axis=0)
        nxt = (D[:T] * W_ALL[4:T + 4]).sum(axis=0)
        r[k] = [comp.sum()] + list(comp)
        r[k + "_next"] = [nxt.sum()] + list(nxt)
    return r


def fed(k):
    f = pd.read_csv(os.path.join(RAW, f"fed_monthly_{k}.csv"))
    f.index = pd.to_datetime(f.iloc[:, 0]).dt.strftime("%Y-%m")
    f = f.iloc[:, 1:]
    f.columns = ["FCI-G"] + COLS
    return f


# ---------------------------------------------------------------- FOMC calendar

MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July",
                                      "August", "September", "October", "November", "December"], 1)}


def fomc_meetings():
    """Meeting start dates, refreshed from the Fed's calendar page when it was downloaded."""
    path = os.path.join(HERE, "fomc_meetings.json")
    stored = json.load(open(path)) if os.path.exists(path) else []
    p = os.path.join(RAW, "fomc.html")
    found = []
    if os.path.exists(p):
        t = open(p, encoding="utf-8", errors="ignore").read()
        for m in re.finditer(r"(\d{4}) FOMC Meetings", t):
            year = int(m.group(1))
            seg = t[m.end(): t.find("FOMC Meetings", m.end()) if t.find("FOMC Meetings", m.end()) > 0 else None]
            for mon, days in re.findall(r"fomc-meeting__month[^>]*>\s*<strong>([^<]+)</strong>.*?"
                                        r"fomc-meeting__date[^>]*>([^<]+)<", seg, re.S):
                mon1 = mon.split("/")[0].strip()
                d1 = re.match(r"\s*(\d+)", days)
                if mon1 in MONTHS and d1 and "notation" not in days.lower():
                    found.append(f"{year}-{MONTHS[mon1]:02d}-{int(d1.group(1)):02d}")
    meetings = sorted(set(stored) | set(found))
    meetings = [m for m in meetings if m >= "2024-01-01"]
    with open(path, "w") as f:
        json.dump(meetings, f, indent=0)
    return meetings


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true", help="skip downloads; use files in raw/")
    a = ap.parse_args()
    if not a.offline:
        print("Downloading inputs")
        download()
    update_history()
    S, proxy_from = series()
    asof = {k: s.index[-1].strftime("%Y-%m-%d") for k, (_, s) in S.items()}
    asof["House Prices"] = zillow().index[-1].strftime("%Y-%m")
    dxy_p = os.path.join(HIST, "dxy.csv")  # daily closes saved by fcig_gs.py
    S = fill(S, S["Stock Market"][1].index[-1], read_hist("dxy.csv") if os.path.exists(dxy_p) else None)
    names = ["FCI-G"] + COLS
    keys = [f"{k}|{c}" for k in ("3yr", "1yr") for c in names]
    dkeys = keys + [f"{k}|next year|{c}" for k in ("3yr", "1yr") for c in names]

    # monthly, 1990 to the latest complete or current month
    last_day = S["Stock Market"][1].index[-1]
    months = pd.period_range("1990-01", last_day.strftime("%Y-%m"), freq="M")
    mrows = []
    for p in months:
        d = min(p.to_timestamp(how="end").normalize(), last_day)
        r = fci_at(S, d)
        mrows.append([str(p)] + r["3yr"] + r["1yr"])
    M = pd.DataFrame(mrows, columns=["month"] + keys).set_index("month")
    F = {k: fed(k) for k in ("3yr", "1yr")}
    out = M.copy()
    for k in F:
        for c in names:
            out[f"{k}|{c}|fed"] = F[k][c].reindex(out.index)
    out.to_csv(os.path.join(HERE, "fcig_replication_monthly.csv"), float_format="%.5f")

    # daily, trading days since DAILY_START
    days = S["Stock Market"][1].loc[DAILY_START:].index
    drows = []
    for d in days:
        r = fci_at(S, d)
        drows.append([d.strftime("%Y-%m-%d")] + r["3yr"] + r["1yr"] + r["3yr_next"] + r["1yr_next"])
    pd.DataFrame(drows, columns=["date"] + dkeys).to_csv(os.path.join(HERE, "fcig_replication_daily.csv"),
                                                         index=False, float_format="%.5f")

    fed_rows = []
    for m in F["3yr"].index:
        if m in F["1yr"].index:
            fed_rows.append([m] + list(F["3yr"].loc[m]) + list(F["1yr"].loc[m]))
    complete = [r for r in mrows if r[0] < last_day.strftime("%Y-%m")
                or (last_day + pd.offsets.BDay(1)).month != last_day.month]
    rnd = lambda r: [r[0]] + [round(float(x), 4) for x in r[1:]]
    data = {
        "generated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "asof": asof,
        "stock_proxy_from": proxy_from.strftime("%Y-%m-%d") if proxy_from is not None else None,
        "meetings": fomc_meetings(),
        "daily": [rnd(r) for r in drows],
        "rep_m": [rnd(r) for r in complete],
        "fed_m": [rnd(r) for r in fed_rows],
    }
    path = os.path.join(HERE, "data.json")
    try:
        old = json.load(open(path))
    except Exception:
        old = {}
    if {k: v for k, v in old.items() if k != "generated"} == json.loads(json.dumps({k: v for k, v in data.items() if k != "generated"})):
        print("Data unchanged; data.json left as is")
    else:
        with open(path, "w") as f:
            json.dump(data, f, separators=(",", ":"))

    # validation summary
    print(f"\nLatest ({drows[-1][0]}): 3-yr {drows[-1][1]:.3f}, 1-yr {drows[-1][9]:.3f}")
    for k in ("3yr", "1yr"):
        j = M[[f"{k}|{c}" for c in names]].set_axis(names, axis=1).join(F[k], rsuffix="_fed", how="inner").dropna()
        for since in ("1990-01", "2024-01"):
            e = (j.loc[since:, "FCI-G"] - j.loc[since:, "FCI-G_fed"])
            print(f"{k} since {since}: RMSE {np.sqrt((e ** 2).mean()):.4f}, max {e.abs().max():.4f}, n={len(e)}")


if __name__ == "__main__":
    main()
