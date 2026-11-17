"""The case list: the baseline and robustness tables of Note B (edit here; 03_estimate.py, 04_tradeoff.py and 05_report.py read it).
Every case is run without the FCI and with the FCI in the matching form. No deterministic trend except Section 4.2c-d (natural cubic spline).
A case is (form, fci, macro, start, end, t2020, trend); see lib/model.py."""
FORMS = {"nom": "Nominal", "real": "Real", "rstar": "r*-gap", "kiley": "r*-gap (Kiley)"}
FCI_LABEL = {0: "none", "cmp": "components", "cmpE": "equities free", "cmpR": "index", "nom": "nominal", "real": "real", "rstar": "r*-gap", "kiley": "r*-gap (Kiley)", "baa": "r*-gap + Baa spread", "jkw": "r*-gap (JK weights)", "calY": "r*-gap (Y weights)", "calB": "r*-gap (FRB/US weights)", "calG": "r*-gap (GS weights)"}

def pair(form, with_fci, **kw):
    """The same rate without and with the FCI."""
    return [dict(form=form, fci=0, **kw), dict(form=form, fci=with_fci, **kw)]

def panel(pid, title, notes, cases):
    """Defaults (FS-A76, 17 Nov 2026): March-December 2020 dropped (month dummies) in every case; monthly equations from 1996 unless stated."""
    base = dict(macro="u,pi", start="1996-01", end=None, t2020="out", trend="none")
    return dict(id=pid, title=title, notes=notes, cases=[{**base, **c} for c in cases])

S73 = dict(start="1973-01")
def both(pid, title, notes, cases):
    """The same panel from 1996 (pid) and from 1973 (pid + '73'): every robustness case is run from both baselines (FS-A76, D-A28)."""
    return [panel(pid, title + ", start 1996", notes, cases), panel(pid + "73", title + ", start 1973", notes, [{**c, **S73} for c in cases])]

VERSIONS = ("nom", "real", "rstar")
ALL3 = sum([pair(f, f) for f in VERSIONS], [])
PANELS = [
 panel("B", "Baseline from 1996: monthly equations from 1996, March-December 2020 dropped, no trend",
       "Nominal, real and r*-gap 2-year yield; the FCI is the matching index in each case. The r*-gap pair is the headline.", ALL3),
 panel("B73", "Baseline from 1973: monthly equations from 1973, March-December 2020 dropped, no trend",
       "As the 1996 baseline; months before 1990 use monthly series in place of the daily data; the daily block and the shocks are those of 1996 on.", [{**c, **S73} for c in ALL3]),
 *both("R1a", "2020 left in (no dummies)", "All three versions. March-December 2020 kept in the monthly and the daily equations.", [{**c, "t2020": "in"} for c in ALL3]),
 # sample ending in 2019: no 2020 data, so the 2020 treatment does not matter; kept at t2020="in" so that the stored results (and their bootstrap seeds) are reused
 *both("R1c", "sample ends in December 2019", "r*-gap only. All equations, monthly and daily.", pair("rstar", "rstar", end=2019, t2020="in")),
 *both("R2a", "Kiley r*", "2-year minus expected inflation minus Kiley's r*; the FCI is built with Kiley's r* (same adjustment in rate and FCI).", pair("kiley", "kiley")),
 *both("R2c", "real 2-year and real FCI with a cubic spline trend",
       "No r* measure: the trend is a natural cubic spline in time (knots at the sample ends and at the NBER business-cycle peaks inside the sample), estimated in every monthly equation.",
       pair("real", "real", trend="spline")),
 *both("R3a", "excess bond premium as a third monthly variable",
       "r*-gap. Monthly system u, inflation, EBP (EBP treated like u and inflation; responses shown for u and the price level).", pair("rstar", "rstar", macro="u,pi,ebp")),
 *both("R3c", "daily Baa-10-year spread in the daily block",
       "r*-gap. The daily Baa-10-year Treasury spread enters the daily block next to the 2-year yield and the FCI, and its lagged monthly average enters the monthly equations; its impact is its announcement-day change on the surprise (no intraday series).",
       pair("rstar", "baa")),
 *both("R4", "the FCI replaced by its three weighted components",
       "The 10-year yield, equity valuation and the real dollar, each multiplied by its weight, enter the daily and monthly equations separately, in the same version as the 2-year yield; each has its own window impact. Replaces the FCI, so the same step without the FCI is the baseline row.",
       [dict(form=f, fci="cmp") for f in VERSIONS]),
 *both("R4c", "the components with common daily dynamics",
       "The daily block is that of the three components in all three versions, so the versions differ only in the monthly equations: one variable (the FCI built from the components), or equities separately with the 10-year yield and the dollar as one variable.",
       [dict(form=f, fci=k) for f in VERSIONS for k in ("cmpR", "cmpE")]),
 *both("R5a", "Bauer-Swanson orthogonalized surprise", "r*-gap. The surprise is the Bauer-Swanson (2023) orthogonalized measure, available for FOMC announcements through 2019; later announcements are dropped from the window impact. Monthly equations and daily block as in the baseline.",
       pair("rstar", "rstar", shock="bs")),
 *both("R5b", "Jarocinski-Karadi sign-restricted surprise", "r*-gap. The Nakamura-Steinsson surprise kept only for announcements in which the 2-year yield and the S\\&P 500 move in opposite directions in the window (Jarocinski and Karadi 2020).",
       pair("rstar", "rstar", shock="jk")),
 *both("R5c", "FCI weights estimated on the Jarocinski-Karadi subset", "r*-gap. The weights of the index are estimated by the same GLS regression on the announcements in which the 2-year yield and the S\\&P 500 move in opposite directions; the surprise is the Nakamura-Steinsson surprise at all 252 announcements. Record only (FS-A72).",
       pair("rstar", "jkw")),
 *both("R5d", "FCI weights and surprise both from the Jarocinski-Karadi subset", "r*-gap. As (c), with the surprise restricted to the Jarocinski-Karadi subset as in (b). Record only (FS-A72).",
       pair("rstar", "jkw", shock="jk")),
 *both("R6", "four calibrations of the index weights (r*-gap)", "The FCI is built with the weights of the companion paper's other calibrations of the same three assets: market weights with the two-year yield as the policy signal (Y), FRB/US weights (B) and the published Goldman Sachs weights (G); each has its own window and ordinary-day loading. The baseline is the market weighting with the futures factor (F).",
       [dict(form="rstar", fci=k) for k in ("calY", "calB", "calG")]),
 *both("R7", "industrial production as a third monthly variable", "All three versions. Monthly system u, inflation, IP (IP = 100 x log INDPRO, treated like u and inflation, also in the daily block's regressors); responses shown for u, the price level and IP.",
       sum([pair(f, f, macro="u,pi,ip") for f in VERSIONS], [])),
 *both("R8", "the federal funds rate in the daily block", "All three versions. The funds rate, in the same version as the 2-year yield, is a third daily variable and enters the monthly equations; on the announcement day it moves by the window move of current-month fed funds futures (MP1) per +1 pp on the 2-year yield.",
       sum([pair(f, f, ext="ff") for f in VERSIONS], [])),
 *both("R9", "the 1-year yield in place of the 2-year", "All three versions. The 1-year Treasury yield replaces the 2-year in the daily block and the monthly equations; responses per +1 pp on the 1-year yield in the window (the 2-year's window move times the ratio of their announcement-day responses).",
       sum([pair(f, f, ext="1y") for f in VERSIONS], [])),
]

def spec(c):
    """The case as stored in the result files."""
    return dict(form=c["form"], fci=c["fci"], macro=c["macro"], start=c["start"], end=c["end"] or "", t2020=c["t2020"], trend=c["trend"], shock=c.get("shock", "ns"), **({"ext": c["ext"]} if c.get("ext") else {}))

def case_id(c):
    return "_".join([c["form"], str(c["fci"]), c["macro"].replace(",", ""), c["start"], str(c["end"] or "all"), c["t2020"]] + ([] if c["trend"] == "none" else [c["trend"]]) + ([] if c.get("shock", "ns") == "ns" else [c["shock"]]) + ([c["ext"]] if c.get("ext") else []))

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
         "R3a": "EBP added", "R3b": "EBP added, start 1973", "R3c": "Baa spread in the daily block", "R4": "Components", "R4b": "Components, start 1973", "R5a": "Bauer-Swanson surprise", "R5b": "Jarocinski-Karadi surprise", "R5c": "Jarocinski-Karadi weights", "R5d": "Jarocinski-Karadi weights and surprise"}
GROUPS = {"B": ["B"], "R1": ["R1a", "R1b", "R1c", "R1d", "R1e"], "R2": ["R2a", "R2b", "R2c", "R2d"], "R3": ["R3a", "R3b", "R3c"], "R4": ["R4", "R4b"], "R5": ["R5a", "R5b"]}
GROUP_TITLE = {"B": "Baseline: 1996 to the present, all data in, no trend", "R1": "sample (r*-gap 2-year yield and FCI)",
               "R2": "the r* adjustment and trends", "R3": "excess bond premium (r*-gap)", "R4": "the FCI replaced by its three weighted components", "R5": "alternative surprises (r*-gap)"}
def panel_by_id(pid): return next(p for p in PANELS if p["id"] == pid)
GROUP_NOTE = {"B": "Nominal, real and r*-gap 2-year yield; the FCI is the index of Kiley (2026) in the matching form in each case.",
              "R1": "Start 1973: monthly equations from 1973, with monthly series in place of daily data before 1990. 2020 dropped: March to December 2020 removed from the monthly and daily equations (2020 values still enter as lags). Ends 2019: all equations, monthly and daily.",
              "R2": "Kiley r*: 2-year minus expected inflation minus Kiley's r*, with the index of Kiley (2026) built with the same r*. Real, spline trend: real 2-year and real FCI with a natural cubic spline trend (knots at the sample ends and at NBER business-cycle peaks inside the sample) in every monthly equation, in place of any r* measure.",
              "R3": "EBP added: the excess bond premium is a third monthly variable, treated like unemployment and inflation (u, inflation, EBP system); responses shown for u and the price level. Baa spread: the daily Baa-10-year spread enters the daily block next to the yield and the FCI, with its announcement-day response as impact.",
              "R5": "Bauer-Swanson: orthogonalized surprise of Bauer and Swanson (2023), announcements through 2019. Jarocinski-Karadi: Nakamura-Steinsson surprise kept when the 2-year yield and the S\\&P 500 move in opposite directions in the window. The window impact and the bootstrap use the events with a surprise.",
              "R4": "Components: the 10-year yield, equity valuation and real dollar, each multiplied by its weight, enter separately in the daily and monthly equations in the same version as the 2-year yield, each with its own window impact (the three impacts sum to the FCI's). Baseline rows without the FCI are in the baseline table."}

# Monthly VAR benchmarks (lib/monthly.py): every step without and with the FCI in the same form, on monthly averages (FS-A76: one data type), March-December 2020 dropped,
# from 1996 and from 1973 (months before the daily data use the monthly series, as in the main model). The instrument (NS surprise) exists from 1996 only.
MONTHLY_STARTS = ("1996-01", "1973-01")
MONTHLY = [dict(step=s, fci=f, start=st) for st in MONTHLY_STARTS for s in ("nom", "real", "rstar") for f in (0, s)]
def monthly_id(m): return f"monthly_{m['step']}_{m['fci']}_{m['start']}"
