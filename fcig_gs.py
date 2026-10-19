"""
Goldman Sachs-style U.S. Financial Conditions Index (FCI) from public daily data.

Goldman's published approach (Hatzius, NY Fed, Feb 2019): a levels index, higher = tighter, with weights

    federal funds rate 4.4%, 10-year Treasury yield 45.1%, BBB corporate spread 39.6%,
    equity valuations (Shiller CAPE) 4.9%, trade-weighted dollar 6.0%

    FCI_t = 100 + sum_j (f_j(X_j,t) - mean_j),
    f = 0.044 FFR + 0.451 Y10 + 0.396 BBB_spread - 0.049 * 100 ln(CAPE) + 0.060 * 100 ln(USD)

Rates and spreads are in percentage points, CAPE and the dollar in log points x 100. The reference means
are taken over 2000-01-01 to 2025-12-31 and then frozen, so history does not revise as data arrive.
Goldman's exact normalization and its own dollar index are proprietary; the page validates the level
against published Goldman observations and the changes against the Fed's FCI-G.

Inputs (public):
    FFR      FRED DFF
    10Y      FRED DGS10
    BBB      ICE BofA BBB option-adjusted spread (FRED BAMLC0A4CBBB; FRED keeps ~3 years, so it is stored in
             history/bbb_oas.csv). Earlier: Moody's Baa yield less the 10-year (DBAA - DGS10), level-matched.
    CAPE     multpl.com's table of Shiller's CAPE (monthly, plus a current value). Daily CAPE = S&P 500 / E10,
             where E10 (ten-year average earnings) is backed out at monthly-average prices and interpolated;
             after the last anchor it grows at its trailing 12-month rate. Anchors: history/cape_e10.csv.
    S&P 500  FRED SP500 (stored in history/sp500.csv), then Yahoo's quote page for days FRED lacks; before
             Oct 2016 the Dow Jones Total Market / S&P 500 history in history/ (level-matched).
    Dollar   FRED DTWEXBGS (nominal broad), earlier DTWEXB and TWEXBMTH; days past FRED's lag are extended with
             ICE dollar index (DX-Y.NYB) changes from Yahoo's quote page once those overlap, else carried forward.

Usage:
    python fcig_gs.py            # download, update history, write outputs
    python fcig_gs.py --offline  # recompute from files already in raw/ and history/
Outputs: gs_data.json (for gs.html), fcig_gs_daily.csv
Validation: history/gs_nyfed_digitized.csv is Goldman's monthly FCI, 1990-Jul 2022, read from the vector chart in
the New York Fed's July 2022 Investor Advisory Committee presentation (tools/digitize_nyfed.py).
"""
import argparse, datetime as dt, json, os, re, time
import numpy as np, pandas as pd
from fcig_replicate import (HERE, RAW, HIST, MONTHS, fetch, fred, read_hist, write_hist, splice_level, extend_dollar, hold, hold,
                            splice_diff)

START = "1990-01-02"
NORM = ("2000-01-01", "2025-12-31")  # reference window for the means (frozen)
WEIGHTS = {"ffr": 0.044, "y10": 0.451, "bbb": 0.396, "cape": 0.049, "usd": 0.060}
LABELS = {"ffr": "Federal funds rate", "y10": "10-year Treasury yield", "bbb": "BBB corporate spread",
          "cape": "Equity valuation (CAPE)", "usd": "Trade-weighted dollar"}

FRED_IDS = ["DFF", "DGS10", "DBAA", "BAMLC0A4CBBB", "SP500", "DTWEXBGS", "DTWEXB", "TWEXBMTH"]
FRED_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="
QUOTES = {"q_GSPC.html": "https://finance.yahoo.com/quote/%5EGSPC/",
          "q_DXY.html": "https://finance.yahoo.com/quote/DX-Y.NYB/"}
MULTPL = ("multpl_cape.html", "https://www.multpl.com/shiller-pe/table/by-month")

# Goldman observations quoted in public material (see the page): (label, start, end, value, kind)
BENCH = [
    ("Mar 2023 (NYC Comptroller presentation, Bloomberg chart; exact date unverified)", "2023-03-01", "2023-03-31", 100.13, "range"),
    ("Jun 2023 (NYC Comptroller presentation, Bloomberg chart; exact date unverified)", "2023-06-01", "2023-06-30", 99.89, "range"),
    ("Calendar-year 2024 average (SanCap)", "2024-01-01", "2024-12-31", 99.15, "mean"),
]


# ---------------------------------------------------------------- download

def fresh(fn, minutes=30):
    p = os.path.join(RAW, fn)
    return os.path.exists(p) and os.path.getmtime(p) > time.time() - minutes * 60


def download():
    os.makedirs(RAW, exist_ok=True)
    jobs = [(f"{i}.csv", FRED_URL + i, True) for i in FRED_IDS]
    jobs += [(fn, u, False) for fn, u in list(QUOTES.items()) + [MULTPL]]
    failed = []
    for fn, url, required in jobs:
        if fresh(fn):
            continue
        body = fetch(url, tries=3 if required else 2)
        if body is None:
            print(f"  {fn:24s} FAILED", flush=True)
            if required:
                failed.append(fn)
            continue
        with open(os.path.join(RAW, fn + ".tmp"), "wb") as f:
            f.write(body)
        os.replace(os.path.join(RAW, fn + ".tmp"), os.path.join(RAW, fn))
        print(f"  {fn:24s} {len(body):>9,d} bytes", flush=True)
    if failed:
        raise SystemExit(f"download failed for required inputs: {', '.join(failed)}")


# ---------------------------------------------------------------- inputs

def quote(fn):
    """(date, price) from a Yahoo quote page when it shows a finished session or a past day, else None."""
    p = os.path.join(RAW, fn)
    if not os.path.exists(p) or os.path.getmtime(p) < time.time() - 6 * 3600:
        return None
    t = open(p, encoding="utf-8", errors="ignore").read()
    price = re.search(r'data-testid="qsp-price"[^>]*>\s*([0-9][0-9,]*\.[0-9]+)', t)
    when = re.search(r"(?:At close|As of):?\s*([A-Z][a-z]+) (\d{1,2}) at (\d{1,2}):\d\d:\d\d ([AP])M", t)
    if not (price and when and when.group(1) in MONTHS):
        return None
    today = dt.date.today()
    d = dt.date(today.year, MONTHS[when.group(1)], int(when.group(2)))
    if d > today:  # December close read in January
        d = d.replace(year=today.year - 1)
    hour = int(when.group(3)) % 12 + (12 if when.group(4) == "P" else 0)
    if d == today and hour < 16:  # intraday print, not a close
        return None
    return pd.Timestamp(d), float(price.group(1).replace(",", ""))


def stored(name, fresh_series, col, quote_fn=None):
    """Merge a freshly downloaded series (and a quote-page close) into history/<name> and return it."""
    p = os.path.join(HIST, name)
    s = read_hist(name) if os.path.exists(p) else pd.Series(dtype=float)
    if fresh_series is not None:
        s = fresh_series.combine_first(s)
    q = quote(quote_fn) if quote_fn else None
    if q is not None and q[0] not in s.index:
        s.loc[q[0]] = q[1]
        print(f"  {col}: close from quote page {q[0].date()} {q[1]:,.2f}")
    s = s.sort_index()
    write_hist(name, s, col)
    return s


def sp500():
    """S&P 500: stored FRED/quote closes; earlier the Dow Jones Total Market / S&P history, level-matched."""
    sp = stored("sp500.csv", fred("SP500"), "sp500", "q_GSPC.html")
    back = splice_level(read_hist("dwcf.csv"), read_hist("gspc_pre1995.csv"))
    return splice_level(sp, back)


def bbb_spread(y10):
    oas = stored("bbb_oas.csv", fred("BAMLC0A4CBBB"), "bbb_oas")
    baa = (fred("DBAA") - y10).dropna()
    return splice_diff(oas, baa), oas.index[-1]


def dollar():
    tm = fred("TWEXBMTH")
    tm.index = tm.index + pd.Timedelta(days=14)  # monthly averages sit mid-month
    s = splice_level(splice_level(fred("DTWEXBGS"), fred("DTWEXB")), tm)
    last = fred("DTWEXBGS").index[-1]
    dxy = stored("dxy.csv", None, "dxy", "q_DXY.html")
    return s, last, dxy


def multpl():
    p = os.path.join(RAW, MULTPL[0])
    if not os.path.exists(p):
        return None
    t = open(p, encoding="utf-8", errors="ignore").read()
    rows = re.findall(r"<td>\s*([A-Z][a-z]{2} \d+, \d{4})\s*</td>\s*<td>\s*(?:&#x2002;)?\s*([0-9]+\.[0-9]+)\s*</td>", t)
    if len(rows) < 1000:
        return None
    return pd.Series({pd.to_datetime(a): float(b) for a, b in rows}).sort_index()


def cape_anchors(px, m):
    """E10 anchors (ten-year average earnings in S&P price units), kind 'm' at mid-month from
    monthly-average prices (Shiller's convention) and 's' for a current spot value. Stored in history."""
    p = os.path.join(HIST, "cape_e10.csv")
    A = pd.read_csv(p, parse_dates=["date"]).set_index("date") if os.path.exists(p) else \
        pd.DataFrame(columns=["e10", "kind"], dtype=object)
    if m is not None:
        spot = m.index[-1]
        first = m[m.index.day == 1]
        mp = px.groupby(px.index.to_period("M")).agg(["mean", "count"])
        new = {}
        for d, v in first.items():
            per = d.to_period("M")
            if per < spot.to_period("M") and per in mp.index and mp.loc[per, "count"] >= 15:
                new[pd.Timestamp(per.year, per.month, 15)] = (mp.loc[per, "mean"] / v, "m")
        if spot in px.index and spot.day != 1:
            new[spot] = (px.loc[spot] / m.iloc[-1], "s")
        N = pd.DataFrame(new, index=["e10", "kind"]).T
        N.index = pd.to_datetime(N.index)
        A = pd.concat([A.drop(N.index, errors="ignore"), N])
        done = {d.to_period("M") for d in A.index[A.kind == "m"]}  # a finished month replaces its spot anchors
        A = A[~((A.kind == "s") & A.index.map(lambda d: d.to_period("M") in done) & (A.index != spot))]
    A = A.sort_index()
    A["e10"] = A["e10"].astype(float)
    A.rename_axis("date").to_csv(p, float_format="%.5f")
    return A


def e10_daily(A, idx):
    """Daily E10: log-linear interpolation between anchors; beyond the last anchor it grows at its
    trailing 12-month rate."""
    s = np.log(A.e10)
    t = (s.index - pd.Timestamp("1970-01-01")).days.values.astype(float)
    x = (idx - pd.Timestamp("1970-01-01")).days.values.astype(float)
    out = np.interp(x, t, s.values)
    past = x > t[-1]
    if past.any():
        k = np.searchsorted(t, t[-1] - 365)
        slope = (s.values[-1] - s.values[k]) / (t[-1] - t[k])
        out[past] = s.values[-1] + slope * (x[past] - t[-1])
    return np.exp(out), (A.index[-1], slope * 365 if past.any() else None)


def extrap_test(px, m, horizons=(1, 3)):
    """Out-of-sample check of the E10 rule: drop the last h months of anchors, extrapolate, compare."""
    mp = px.groupby(px.index.to_period("M")).mean()
    mm = m[m.index.day == 1]
    e10 = pd.Series({d: mp.get(d.to_period("M"), np.nan) / v for d, v in mm.items()}).dropna()
    e10 = e10[e10.index >= "1995-01-01"]
    out = {}
    for h in horizons:
        errs = []
        for i in range(24, len(e10) - h):
            past = np.log(e10.iloc[:i])
            slope = (past.iloc[-1] - past.iloc[max(0, i - 13)]) / 12
            errs.append(past.iloc[-1] + slope * h - np.log(e10.iloc[i - 1 + h]))
        out[h] = float(np.std(errs) * 100)
    return out


# ---------------------------------------------------------------- index

def f_terms(x):
    """Weighted terms, in index points, before subtracting reference means."""
    return pd.DataFrame({
        "ffr": WEIGHTS["ffr"] * x["ffr"],
        "y10": WEIGHTS["y10"] * x["y10"],
        "bbb": WEIGHTS["bbb"] * x["bbb"],
        "cape": -WEIGHTS["cape"] * 100 * np.log(x["cape"]),
        "usd": WEIGHTS["usd"] * 100 * np.log(x["usd"]),
    })


def build():
    ffr_s, y10_s = fred("DFF"), fred("DGS10")
    px = sp500()
    spread, oas_last = bbb_spread(y10_s)
    usd, usd_last, dxy = dollar()
    m = multpl()
    A = cape_anchors(px, m)
    idx = px.loc[START:].index  # equity trading days

    x = pd.DataFrame(index=idx)
    x["ffr"] = hold(ffr_s, idx[-1]).reindex(idx, method="ffill")
    x["y10"] = hold(y10_s, idx[-1]).reindex(idx, method="ffill")
    x["bbb"] = hold(spread, idx[-1]).reindex(idx, method="ffill")
    e10, (e10_last, e10_g) = e10_daily(A, idx)
    x["cape"] = px.loc[idx].values / e10
    usd, usd_ext = extend_dollar(usd, dxy)  # same rule as the FCI-G page: DXY changes, then constant
    u = usd.reindex(usd.index.union(idx)).interpolate("time").ffill().reindex(idx)
    x["usd"] = u
    x = x.dropna()

    f = f_terms(x)
    ref = f.loc[NORM[0]:NORM[1]].mean()
    c = f - ref
    fci = 100 + c.sum(axis=1)
    last = lambda s: s.index[-1].strftime("%Y-%m-%d")
    info = {
        "asof": {"ffr": last(ffr_s), "y10": last(y10_s), "bbb": oas_last.strftime("%Y-%m-%d"),
                 "cape": (m.index[-1].strftime("%Y-%m-%d") if m is not None else e10_last.strftime("%Y-%m-%d")),
                 "sp500": last(px), "usd": usd_last.strftime("%Y-%m-%d")},
        "usd_extended_from": usd_ext.strftime("%Y-%m-%d") if usd_ext is not None else None,
        "e10_last_anchor": e10_last.strftime("%Y-%m-%d"), "e10_growth": e10_g,
        "last": last(x),
    }
    return x, c, fci, ref, info, px, m, A


def stats(x, c, fci, px, m):
    d = fci.diff().dropna()
    sub = c.diff().loc["2020-01-01":]
    tot = fci.diff().loc["2020-01-01":]
    share = {k: float(np.cov(sub[k].dropna(), tot.loc[sub[k].dropna().index])[0, 1] / tot.var()) for k in c}
    h63 = c.rolling(63).sum().diff(63).loc["2000-01-01":] if False else (c - c.shift(63)).loc["2000-01-01":]
    sd63 = {k: float(h63[k].std()) for k in c}
    sd63["fci"] = float((fci - fci.shift(63)).loc["2000-01-01":].std())
    bench = []
    for lab, a, b, v, kind in BENCH:
        seg = fci.loc[a:b]
        bench.append({"label": lab, "start": a, "end": b, "published": v, "kind": kind,
                      "mean": float(seg.mean()), "min": float(seg.min()), "max": float(seg.max()),
                      "end_value": float(seg.iloc[-1])})
    # CAPE reconstruction against multpl's monthly values (Shiller's convention: monthly average)
    chk = None
    if m is not None:
        mm = m[(m.index.day == 1) & (m.index >= "1990-01-01") & (m.index < m.index[-1].replace(day=1))]
        av = x["cape"].groupby(x.index.to_period("M")).mean()
        e = pd.Series({d: np.log(av.get(d.to_period("M"), np.nan) / v) for d, v in mm.items()}).dropna()
        chk = {"n": int(len(e)), "rmse_pct": float(np.sqrt((e ** 2).mean()) * 100), "max_pct": float(e.abs().max() * 100)}
    return {"share_var_2020": share, "sd63": sd63, "daily_sd": float(d.loc["2020-01-01":].std()),
            "bench": bench, "cape_check": chk,
            "extrap_sd_pct": extrap_test(px, m) if m is not None else None}


def vs_fed(fci):
    """Month-end Goldman-style FCI against the Fed's FCI-G (published, from data.json written by fcig_replicate)."""
    p = os.path.join(HERE, "data.json")
    if not os.path.exists(p):
        return None, None
    fm = json.load(open(p)).get("fed_m")
    if not fm:
        return None, None
    fed = pd.Series({r[0]: r[1] for r in fm})
    g = fci.groupby(fci.index.to_period("M")).last()
    g.index = g.index.strftime("%Y-%m")
    j = pd.concat([g, fed], axis=1, join="inner").dropna().loc["2000-01":]
    j.columns = ["gs", "fed"]
    ch = j.diff(3).dropna()
    st = {"n": int(len(j)), "corr_level": float(j.corr().iloc[0, 1]), "corr_chg3": float(ch.corr().iloc[0, 1]),
          "corr_chg1": float(j.diff().dropna().corr().iloc[0, 1]), "last": j.index[-1], "since": j.index[0]}
    rows = [[k, round(a, 3), round(b, 3)] for k, a, b in zip(j.index, j.gs, j.fed)]
    return rows, st


def vs_goldman(fci, c):
    """Monthly-average replication against Goldman's monthly series digitized from the New York Fed chart
    (tools/digitize_nyfed.py). Goldman's series behaves like a monthly average, not a month-end value."""
    p = os.path.join(HIST, "gs_nyfed_digitized.csv")
    if not os.path.exists(p):
        return None, None
    g = pd.read_csv(p, index_col=0).iloc[:, 0]
    g.index = pd.PeriodIndex(g.index, freq="M")
    per = fci.index.to_period("M")
    rep, rep_end = fci.groupby(per).mean(), fci.groupby(per).last()
    j = pd.concat([g, rep], axis=1, join="inner").dropna()
    j.columns = ["gs", "rep"]
    e = j.rep - j.gs
    chg = lambda k: float(j.diff(k).dropna().corr().iloc[0, 1])
    je = pd.concat([g, rep_end], axis=1, join="inner").dropna()
    cm = c.groupby(per).mean().reindex(j.index)
    A = np.column_stack([cm.values, np.ones(len(j))])
    b = np.linalg.lstsq(A, (j.gs - 100).values, rcond=None)[0]
    by = e.groupby(e.index.year // 10 * 10).agg(["mean", "std"])
    st = {"n": int(len(j)), "first": str(j.index[0]), "last": str(j.index[-1]),
          "corr_level": float(j.corr().iloc[0, 1]), "corr_chg1": chg(1), "corr_chg3": chg(3),
          "corr_chg1_monthend": float(je.diff().dropna().corr().iloc[0, 1]),
          "mean_gap": float(e.mean()), "sd_gap": float(e.std()), "rmse_demeaned": float(np.sqrt(((e - e.mean()) ** 2).mean())),
          "slope": float(np.polyfit(j.gs, j.rep, 1)[0]),
          "coef": {k: float(v) for k, v in zip(c.columns, b[:-1])},
          "by_decade": {f"{int(d)}s": [float(r["mean"]), float(r["std"])] for d, r in by.iterrows()}}
    rows = [[str(k), round(float(a), 3), round(float(b_), 3)] for k, a, b_ in zip(j.index, j.gs, j.rep)]
    return rows, st


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true", help="skip downloads; use files in raw/")
    a = ap.parse_args()
    if not a.offline:
        print("Downloading inputs")
        download()
    x, c, fci, ref, info, px, m, A = build()
    st = stats(x, c, fci, px, m)
    vf, vst = vs_fed(fci)
    vg, vgst = vs_goldman(fci, c)

    out = pd.concat([fci.rename("fci"), c.add_prefix("c_"), x.add_prefix("x_")], axis=1)
    out.rename_axis("date").to_csv(os.path.join(HERE, "fcig_gs_daily.csv"), date_format="%Y-%m-%d", float_format="%.4f")

    rows = [[d.strftime("%Y-%m-%d"), round(r.ffr, 3), round(r.y10, 3), round(r.bbb, 3), round(r.cape, 2), round(r.usd, 3)]
            for d, r in zip(x.index, x.itertuples())]
    meetings = json.load(open(os.path.join(HERE, "fomc_meetings.json"))) if os.path.exists(os.path.join(HERE, "fomc_meetings.json")) else []
    data = {"generated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), **info,
            "weights": WEIGHTS, "labels": LABELS, "ref": {k: round(float(v), 5) for k, v in ref.items()},
            "norm": NORM, "meetings": meetings, "cols": ["date", "ffr", "y10", "bbb", "cape", "usd"], "rows": rows,
            "stats": st, "vs_fed": vf, "vs_fed_stats": vst, "vs_gs": vg, "vs_gs_stats": vgst}
    path = os.path.join(HERE, "gs_data.json")
    new = json.dumps(data, separators=(",", ":"))
    try:
        old = json.load(open(path))
        same = {k: v for k, v in old.items() if k != "generated"} == {k: v for k, v in data.items() if k != "generated"}
    except Exception:
        same = False
    if same:
        print("Data unchanged; gs_data.json left as is")
    else:
        open(path, "w").write(new)

    print(f"\nLatest ({info['last']}): FCI {fci.iloc[-1]:.2f}; contributions vs mean:",
          {k: round(float(v), 2) for k, v in c.iloc[-1].items()})
    print("as-of:", info["asof"], "| dollar extended from", info["usd_extended_from"],
          "| E10 anchor", info["e10_last_anchor"], "growth/yr", info["e10_growth"])
    for b in st["bench"]:
        print(f"  {b['label'][:40]:42s} published {b['published']:.2f}  replication mean {b['mean']:.2f} "
              f"[{b['min']:.2f}, {b['max']:.2f}]")
    print("  CAPE check", st["cape_check"], "| extrapolation sd %", st["extrap_sd_pct"])
    print("  vs Fed", vst)
    print("  vs Goldman (digitized)", {k: v for k, v in (vgst or {}).items() if k != "by_decade"})


if __name__ == "__main__":
    main()
