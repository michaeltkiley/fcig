"""The case list: the baseline and robustness tables of Note B (edit here; 03_estimate.py, 04_tradeoff.py and 05_report.py read it).
Every case is run without the FCI and with the FCI in the matching form. No deterministic trend except Robustness 2c-d (natural cubic spline).
A case is (form, fci, macro, start, end, t2020, trend); see lib/model.py."""
FORMS = {"nom": "Nominal", "real": "Real", "rstar": "r*-gap", "kiley": "r*-gap (Kiley)"}
FCI_LABEL = {0: "none", "cmp": "components", "nom": "nominal", "real": "real", "rstar": "r*-gap", "kiley": "r*-gap (Kiley)"}

def pair(form, with_fci, **kw):
    """The same rate without and with the FCI."""
    return [dict(form=form, fci=0, **kw), dict(form=form, fci=with_fci, **kw)]

def panel(pid, title, notes, cases):
    base = dict(macro="u,pi", start="1996-01", end=None, t2020="in", trend="none")
    return dict(id=pid, title=title, notes=notes, cases=[{**base, **c} for c in cases])

PANELS = [
 panel("B", "Baseline: 1996 to the present, all data in, no trend",
       "Nominal, real and r*-gap 2-year yield; the FCI is the matching index of Note A in each case.",
       sum([pair(f, f) for f in ("nom", "real", "rstar")], [])),
 panel("R1a", "Robustness 1a: monthly equations start in 1973", "r*-gap only. Pre-1990 months use monthly series in place of the daily data (see lib/model.py); shocks are the 252 announcements of 1996 on.",
       pair("rstar", "rstar", start="1973-01")),
 panel("R1b", "Robustness 1b: 2020 dropped from all equations, start 1996", "r*-gap only. March to December 2020 dropped from the monthly and the daily equations.",
       pair("rstar", "rstar", t2020="out")),
 panel("R1c", "Robustness 1c: 2020 dropped from all equations, start 1973", "r*-gap only.",
       pair("rstar", "rstar", start="1973-01", t2020="out")),
 panel("R1d", "Robustness 1d: sample ends in December 2019, start 1996", "r*-gap only. All equations, monthly and daily.",
       pair("rstar", "rstar", end=2019)),
 panel("R1e", "Robustness 1e: sample ends in December 2019, start 1973", "r*-gap only.",
       pair("rstar", "rstar", start="1973-01", end=2019)),
 panel("R2a", "Robustness 2a: Kiley r*, start 1996", "2-year minus expected inflation minus Kiley's r*; the FCI is Note A's index built with Kiley's r* (same adjustment in rate and FCI).",
       pair("kiley", "kiley")),
 panel("R2b", "Robustness 2b: Kiley r*, start 1973", "As 2a.", pair("kiley", "kiley", start="1973-01")),
 panel("R2c", "Robustness 2c: real 2-year and real FCI with a cubic spline trend, start 1996",
       "No r* measure: the trend is a natural cubic spline in time (knots at the sample ends and at the NBER business-cycle peaks inside the sample), estimated in every monthly equation.",
       pair("real", "real", trend="spline")),
 panel("R2d", "Robustness 2d: real 2-year and real FCI with a cubic spline trend, start 1973", "As 2c; knots at the NBER peaks of 1973, 1980, 1981, 1990, 2001, 2007 and 2020.",
       pair("real", "real", start="1973-01", trend="spline")),
 panel("R3a", "Robustness 3a: excess bond premium as a third monthly variable, start 1996",
       "r*-gap. Monthly system u, inflation, EBP (EBP treated like u and inflation; responses shown for u and the price level).",
       pair("rstar", "rstar", macro="u,pi,ebp")),
 panel("R3b", "Robustness 3b: excess bond premium as a third monthly variable, start 1973", "As 3a.",
       pair("rstar", "rstar", macro="u,pi,ebp", start="1973-01")),
]

PANELS.append(panel("R4", "Robustness 4: the FCI replaced by its three weighted components",
       "The 10-year yield, equity valuation and the real dollar, each multiplied by its weight, enter the daily and monthly equations separately, in the same step as the 2-year yield; each has its own window impact. Replaces the FCI, so the same step without the FCI is the baseline row.",
       [dict(form=f, fci="cmp") for f in ("nom", "real", "rstar")]))

PANELS.append(panel("R4b", "Robustness 4b: the FCI replaced by its three weighted components, start 1973", "As 4: monthly equations from 1973 (monthly series before 1990); the daily block is still estimated from 1996.",
       [dict(form=f, fci="cmp", start="1973-01") for f in ("nom", "real", "rstar")]))

PANELS.append(panel("R5a", "Robustness 5a: Bauer-Swanson orthogonalized surprise", "r*-gap. The surprise is the Bauer-Swanson (2023) orthogonalized measure, available for FOMC announcements through 2019; later announcements are dropped from the window impact. Monthly equations and daily block as in the baseline.",
       pair("rstar", "rstar", shock="bs")))
PANELS.append(panel("R5b", "Robustness 5b: Jarocinski-Karadi sign-restricted surprise", "r*-gap. The Nakamura-Steinsson surprise kept only for announcements in which the 2-year yield and the S&P 500 move in opposite directions in the window (Jarocinski and Karadi 2020).",
       pair("rstar", "rstar", shock="jk")))

def spec(c):
    """The case as stored in the result files."""
    return dict(form=c["form"], fci=c["fci"], macro=c["macro"], start=c["start"], end=c["end"] or "", t2020=c["t2020"], trend=c["trend"], shock=c.get("shock", "ns"))

def case_id(c):
    return "_".join([c["form"], str(c["fci"]), c["macro"].replace(",", ""), c["start"], str(c["end"] or "all"), c["t2020"]] + ([] if c["trend"] == "none" else [c["trend"]]) + ([] if c.get("shock", "ns") == "ns" else [c["shock"]]))

def unique_cases(panel_id=None):
    seen, out = set(), []
    for p in PANELS:
        if panel_id and p["id"] != panel_id: continue
        for c in p["cases"]:
            if case_id(c) not in seen: seen.add(case_id(c)); out.append(c)
    return out

# Short row labels and the sections of the main text (the 12-lag tables are grouped by section; appendix tables are per panel)
SHORT = {"B": "", "R1a": "Start 1973", "R1b": "2020 dropped", "R1c": "2020 dropped, start 1973", "R1d": "Ends 2019", "R1e": "Ends 2019, start 1973",
         "R2a": "Kiley r*", "R2b": "Kiley r*, start 1973", "R2c": "Real, spline trend", "R2d": "Real, spline trend, start 1973",
         "R3a": "EBP added", "R3b": "EBP added, start 1973", "R4": "Components", "R4b": "Components, start 1973", "R5a": "Bauer-Swanson surprise", "R5b": "Jarocinski-Karadi surprise"}
GROUPS = {"B": ["B"], "R1": ["R1a", "R1b", "R1c", "R1d", "R1e"], "R2": ["R2a", "R2b", "R2c", "R2d"], "R3": ["R3a", "R3b"], "R4": ["R4", "R4b"], "R5": ["R5a", "R5b"]}
GROUP_TITLE = {"B": "Baseline: 1996 to the present, all data in, no trend", "R1": "Robustness 1: sample (r*-gap 2-year yield and FCI)",
               "R2": "Robustness 2: the r* adjustment and trends", "R3": "Robustness 3: excess bond premium (r*-gap)", "R4": "Robustness 4: the FCI replaced by its three weighted components", "R5": "Robustness 5: alternative surprises (r*-gap)"}
def panel_by_id(pid): return next(p for p in PANELS if p["id"] == pid)
GROUP_NOTE = {"B": "Nominal, real and r*-gap 2-year yield; the FCI is Note A's index in the matching form in each case.",
              "R1": "Start 1973: monthly equations from 1973, with monthly series in place of daily data before 1990 (lib/model.py). 2020 dropped: March to December 2020 removed from the monthly and daily equations (2020 values still enter as lags). Ends 2019: all equations, monthly and daily.",
              "R2": "Kiley r*: 2-year minus expected inflation minus Kiley's r*, with Note A's index built with the same r*. Real, spline trend: real 2-year and real FCI with a natural cubic spline trend (knots at the sample ends and at NBER business-cycle peaks inside the sample) in every monthly equation, in place of any r* measure.",
              "R3": "The excess bond premium is a third monthly variable, treated like unemployment and inflation (u, inflation, EBP system); responses shown for u and the price level.",
              "R5": "Bauer-Swanson: orthogonalized surprise of Bauer and Swanson (2023), announcements through 2019. Jarocinski-Karadi: Nakamura-Steinsson surprise kept when the 2-year yield and the S&P 500 move in opposite directions in the window. The window impact and the bootstrap use the events with a surprise.",
              "R4": "Components: the 10-year yield, equity valuation and real dollar, each multiplied by its weight, enter separately in the daily and monthly equations in the same step as the 2-year yield, each with its own window impact (the three impacts sum to the FCI's). Baseline rows without the FCI are in the baseline table."}

# Monthly VAR benchmarks: every step without and with the FCI in the same form, on end-of-month series from 1996 (the main sample); the instrument (NS surprise) exists from 1996 only (lib/monthly.py).
# A 1973 start is not offered: the FCI is daily only from 1990, so an end-of-month FCI cannot be built before then.
MONTHLY_START = "1996-01"
MONTHLY = [dict(step=s, fci=f, start=MONTHLY_START) for s in ("nom", "real", "rstar") for f in (0, s)]
def monthly_id(m): return f"monthly_{m['step']}_{m['fci']}_{m['start']}"
