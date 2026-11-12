"""Step 19 helpers: the Philadelphia Fed SPF panel (median forecasts of the unemployment rate and real GDP four quarters ahead) aligned to the survey deadline.
Files: data/spf/medianlevel.xlsx, data/spf/spf-release-dates.txt (see data/spf/SOURCES.md)."""
import re, warnings
import numpy as np, pandas as pd
from .config import DATA
from .stance_core import fred

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")


def deadlines():
    out, yr = {}, None
    for ln in open(DATA / "spf" / "spf-release-dates.txt"):
        m = re.match(r"^\s*(\d{4})\s+Q([1-4])\s+(\d+)/(\d+)/(\d\d)", ln)
        m2 = re.match(r"^\s+Q([1-4])\s+(\d+)/(\d+)/(\d\d)", ln)
        if m: yr = int(m[1]); q = int(m[2]); mo, dy, yy = int(m[3]), int(m[4]), int(m[5])
        elif m2 and yr: q = int(m2[1]); mo, dy, yy = int(m2[2]), int(m2[3]), int(m2[4])
        else: continue
        out[(yr, q)] = pd.Timestamp(year=1900 + yy if yy >= 50 else 2000 + yy, month=mo, day=dy)
    return out


def panel():
    """One row per survey from 1990Q2. info = last complete month before the deadline month (e.g. a deadline of 22 Nov: October); targets: quarter q+4 of the survey quarter q."""
    dl = deadlines()
    xl = pd.ExcelFile(DATA / "spf" / "medianlevel.xlsx")
    U = xl.parse("UNEMP").set_index(["YEAR", "QUARTER"]); R = xl.parse("RGDP").set_index(["YEAR", "QUARTER"])
    u = fred("UNRATE"); uq = u.groupby(u.index.asfreq("Q")).mean()
    g = pd.read_csv(DATA / "GDPC1.csv"); g = pd.Series(g.GDPC1.values, index=pd.PeriodIndex(pd.to_datetime(g.observation_date), freq="Q")); lg = 100 * np.log(g)
    rows = []
    for (y, q), d in sorted(dl.items()):
        if (y, q) not in U.index: continue
        sq = pd.Period(f"{y}Q{q}", "Q"); tq = sq + 4
        rows.append(dict(survey=str(sq), deadline=d.date().isoformat(), info_month=str(d.to_period("M") - 1), u_last=U.loc[(y, q), "UNEMP1"], u_fc=U.loc[(y, q), "UNEMP6"],
                         u_real=uq.get(tq, np.nan), gdp_fc=100 * np.log(R.loc[(y, q), "RGDP6"] / R.loc[(y, q), "RGDP2"]),
                         gdp_real=(lg.get(tq, np.nan) - lg.get(sq, np.nan))))
    P = pd.DataFrame(rows)
    P["u_err"] = P.u_real - P.u_fc; P["gdp_err"] = P.gdp_real - P.gdp_fc; P["u_fc_change"] = P.u_fc - P.u_last
    return P
