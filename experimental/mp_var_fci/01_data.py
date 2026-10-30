"""Step 1 of MP_QA.md. Monthly data set for the monetary-policy-shock VAR with the market index.

Reuses the replication package (fci_note/replication): unemployment gap, funds rate, expected inflation, r*, the indexes in three cases
(nominal, real, r*-gap), and the Nakamura-Steinsson (NS) policy-news factor of the USMPD events. Adds (retrieved from FRED, saved in data/):
core PCE price index (PCEPILFE), 2-year Treasury yield (GS2, robustness policy variable), and the inputs of the Bauer-Swanson-style purge
(payrolls PAYEMS, 3-month bill DTB3, WTI DCOILWTICO), used in step 3.

Inflation (MP-A5, MP-A7): raw monthly core PCE, annualized: 1200 * (ln P_t - ln P_{t-1}); no gap, no smoothing.
Policy variable (MP-A1): funds rate. Three versions are built for each index case so that "like for like" can be decided later (open question MP-Q7):
ffr (nominal funds rate), ffr_real (less 1-year expected inflation), ffr_rstar (real, less r*), i.e. cases.inputs(...)["policy"].
Indexes: market (level), gs (level), fcig_1yr; market forward impetus (12-lag VAR) from the replication package, per case.
NS instrument: monthly sum of the NS factor over the events of the month (0 in months without an event); events as in the note (unscheduled no-move events
and March-April 2020 dropped). Counts are reported by era.
2020 is not altered here; the dummies are built where the VARs are estimated.
Usage: python 01_data.py [--refresh]   (downloads from FRED only if a file is missing or --refresh)
Output: data/mp_monthly.csv, data/<FRED>.csv, 01_data.log
"""
import re, sys, subprocess
from pathlib import Path
import numpy as np, pandas as pd

HERE = Path(__file__).resolve().parent
REP = HERE.parents[1] / "fci_note" / "replication"
sys.path.insert(0, str(REP))
from fci import data as D0, cases, indexes as I          # noqa: E402

DATA = HERE / "data"
START, END = "1973-01", "2026-09"
FRED_CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={}&cosd=1950-01-01"
FRED_TXT = "https://fred.stlouisfed.org/data/{}.txt"      # fallback: HTML table of the series, which FRED truncates at 1000 rows (fine for short series only)
UA = "fcig-replication/1.0 (+https://michaeltkiley.github.io/fcig/)"   # FRED rejects generic browser user agents


def _curl(url):
    return subprocess.run(["curl", "-sS", "-L", "--http1.1", "-m", "120", "-A", UA, url], capture_output=True, text=True).stdout


def fetch_fred(name, refresh=False):
    """Save the FRED series as data/<name>.csv (observation_date, name) and return it as a Series."""
    f = DATA / f"{name}.csv"
    if refresh or not f.exists():
        rows = []
        txt = _curl(FRED_CSV.format(name)).strip().splitlines()
        for ln in txt[1:]:
            a, _, b = ln.partition(",")
            if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", a) and re.fullmatch(r"-?[0-9.]+", b) and b != ".":
                rows.append((a, b))
        if len(rows) < 100:                                         # CSV endpoint unavailable: use the HTML table
            html = _curl(FRED_TXT.format(name))
            rows = [r for r in re.findall(r"<tr[^>]*>\s*<th[^>]*>\s*([0-9]{4}-[0-9]{2}-[0-9]{2})\s*</th>\s*<td[^>]*>\s*([-0-9.]+)\s*</td>", html) if r[1] != "."]
            if len(rows) >= 1000:
                raise SystemExit(f"{name}: HTML table is truncated at 1000 rows; CSV endpoint needed")
        if len(rows) < 100:
            raise SystemExit(f"FRED download of {name} failed ({len(rows)} rows)")
        pd.DataFrame(rows, columns=["observation_date", name]).to_csv(f, index=False)
    d = pd.read_csv(f)
    return pd.Series(d[name].values.astype(float), index=pd.to_datetime(d["observation_date"]))


def monthly(s):
    return s.groupby(s.index.to_period("M")).mean()


def main():
    refresh = "--refresh" in sys.argv
    D = D0.load()                                       # replication package monthly data (1958-2026)
    pce = fetch_fred("PCEPILFE", refresh); gs2 = fetch_fred("GS2", refresh)
    for n in ("PAYEMS", "DTB3", "DCOILWTICO"):
        fetch_fred(n, refresh)
    out = pd.DataFrame(index=pd.period_range(START, END, freq="M"))
    P = monthly(pce)
    out["pi_core"] = 1200 * np.log(P).diff()
    out["u_gap"] = D.u_gap
    out["ffr"] = D.ffr
    out["gs2"] = monthly(gs2)
    for case in cases.CASES:
        X = cases.inputs(D, "rstar" if case == "rstar" else case)
        out[f"ffr_{case}"] = X["policy"]
        I_ = D0.read(f"indexes_{case}.csv"); F_ = D0.read(f"flow_{case}.csv")
        out[f"market_{case}"] = I_.market; out[f"gs_{case}"] = I_.gs; out[f"fcig1_{case}"] = I_.fcig_1yr
        out[f"mkt_fi12_{case}"] = F_.forward_impetus_p12
    ev = I.events()
    ev["m"] = ev.Date.dt.to_period("M")
    out["ns"] = ev.groupby("m").ns.sum().reindex(out.index).fillna(0.0)
    out["n_events"] = ev.groupby("m").size().reindex(out.index).fillna(0).astype(int)
    out["d2020"] = (out.index.year == 2020).astype(int)
    out = out.loc[START:END]
    out.index.name = "month"
    out.to_csv(DATA / "mp_monthly.csv", float_format="%.5f")

    print(f"mp_monthly.csv: {out.shape[0]} months x {out.shape[1]} columns, {out.index[0]} to {out.index[-1]}")
    print("\nFirst/last valid month and mean/sd by column:")
    for c in out.columns:
        s = out[c].dropna()
        print(f"  {c:18s} {str(s.index[0])} {str(s.index[-1])}  n={len(s):4d}  mean {s.mean():8.3f}  sd {s.std():7.3f}")
    print("\nNS instrument: events and months with an event, by era")
    for lab, a, b in (("1994-2007", "1994-01", "2007-12"), ("2008-2015", "2008-01", "2015-12"), ("2016-2019", "2016-01", "2019-12"), ("2020", "2020-01", "2020-12"), ("2021-2026", "2021-01", "2026-09"), ("1994-2026", "1994-01", "2026-09")):
        s = out.loc[a:b]
        print(f"  {lab:10s} events {int(s.n_events.sum()):4d}  months with event {int((s.n_events > 0).sum()):3d} of {len(s):3d}  sd(ns, monthly) {s.ns.std():.3f}  max|ns| {s.ns.abs().max():.3f}")
    print("\nChecks:")
    print("  pi_core: mean %.2f, sd %.2f, min %.2f, max %.2f (annualized %%)" % (out.pi_core.mean(), out.pi_core.std(), out.pi_core.min(), out.pi_core.max()))
    print("  pi_core 2020-03..2020-06:", out.loc["2020-03":"2020-06", "pi_core"].round(2).tolist())
    print("  ffr below 0.25 in %d months (zero-lower-bound months: %s)" % ((out.ffr < 0.25).sum(), ", ".join(str(p) for p in out.index[(out.ffr < 0.25)][[0, -1]])))
    print("  first month with no missing values in the main block:", out[["pi_core", "u_gap", "ffr", "market_rstar"]].dropna().index[0])
    print("  correlation of ns with market_rstar monthly change (1994-2026): %.2f" % out.loc["1994-01":, "ns"].corr(out.market_rstar.diff().loc["1994-01":]))
    print("\nTiming check: correlation of the monthly NS sum with monthly changes (1994-2026), by lead of the change (0 = same month, 1 = next month)")
    s94 = out.loc["1994-01":]
    for lab, x in (("market_rstar", out.market_rstar), ("ffr", out.ffr), ("gs2", out.gs2), ("u_gap", out.u_gap), ("pi_core", out.pi_core)):
        d = x.diff()
        print("  %-13s" % lab + "  ".join("lead %d: %+.2f" % (k, s94.ns.corr(d.shift(-k).loc["1994-01":])) for k in (0, 1, 2)))
    print("  (market_rstar is a monthly average, so a mid-month surprise enters the same and the next month's change)")


if __name__ == "__main__":
    main()
