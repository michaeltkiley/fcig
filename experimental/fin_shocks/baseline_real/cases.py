"""The case list of Note B with the real version as the baseline (fin_shocks/baseline_real, FS-A85; edit here; 03_estimate.py, 05_tradeoff.py and the reports read it).
Every case is run without the FCI and with the FCI in the matching form, with the 2-year yield and the federal funds rate in the daily block. No deterministic trend except panel F2 (natural cubic spline).
A case is (form, fci, macro, start, end, t2020, trend); see lib/model.py."""
FORMS = {"nom": "Nominal", "real": "Real", "rstar": "r*-gap", "kiley": "r*-gap (Kiley)"}
FCI_LABEL = {0: "none", "cmp": "components", "cmpE": "equities free", "cmpR": "index", "nom": "nominal", "real": "real", "rstar": "r*-gap", "kiley": "r*-gap (Kiley)", "baa": "real + Baa spread", "baa0": "none (Baa spread)", "jkw": "r*-gap (JK weights)", "calY": "r*-gap (Y weights)", "calB": "r*-gap (FRB/US weights)", "calG": "r*-gap (GS weights)"}

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

VERSIONS = ("nom", "real")          # FS-A85 D2: two steps in the main text; the r*-gap step is a panel of the final section (D11)
ALL2 = sum([pair(f, f) for f in VERSIONS], [])
# baseline_real (FS-A85, 18 Nov 2026): every case has the federal funds rate in the daily block (ext "" = the new baseline; ext "noff" = the 2-year-only model of fin_shocks/baseline).
PANELS = [
 panel("B", "Baseline from 1996: 2-year yield and funds rate, monthly equations from 1996, March-December 2020 dropped, no trend",
       "Nominal and real 2-year yield and funds rate; the FCI is the matching index in each case. The real pair is the headline.", ALL2),
 panel("B73", "Baseline from 1973: 2-year yield and funds rate, monthly equations from 1973, March-December 2020 dropped, no trend",
       "As the 1996 baseline; months before 1990 use monthly series in place of the daily data; the daily block and the shocks are those of 1996 on.", [{**c, **S73} for c in ALL2]),
 # ---- the six core robustness tests (FS-A85 D6, revised by D10-D11)
 *both("R1", "2020 left in (no dummies)", "Nominal and real. March-December 2020 kept in the monthly and the daily equations.", [{**c, "t2020": "in"} for c in ALL2]),
 *both("R2", "industrial production as a monthly variable",
       "Nominal and real. Monthly system u, inflation, IP (IP = 100 x log INDPRO; treated like u and inflation, also in the daily block's regressors); responses shown for u and the price level. FS-A99: the excess bond premium is no longer in the paper.",
       sum([pair(f, f, macro="u,pi,ip") for f in VERSIONS], [])),
 *both("R3", "Bauer-Swanson orthogonalized surprise", "Nominal and real. The surprise is the Bauer-Swanson (2023) orthogonalized measure, available for FOMC announcements through 2019; later announcements are dropped from the window impact.",
       sum([pair(f, f, shock="bs") for f in VERSIONS], [])),
 # 6 lags: every case is estimated at 6 and 12 lags (no separate panel)
 *both("R5", "without the funds rate (2-year yield only in the daily block)", "Nominal and real. The model of the earlier baseline: the funds rate is not in the daily block or the monthly equations.",
       sum([pair(f, f, ext="noff") for f in VERSIONS], [])),
 panel("R6", "monthly equations from 1985", "Nominal and real. As the baselines, with the monthly equations from January 1985 (months before 1990 from the monthly series).", [{**c, "start": "1985-01"} for c in ALL2]),
 # ---- the final section (FS-A85 D11): slow-moving rates and financial conditions
 *both("F1", "r*-gap step (Laubach-Williams r*)", "2-year yield and funds rate less expected inflation and LW r*; the FCI in the r*-gap form (earnings-yield gap less r*).", pair("rstar", "rstar")),
 *both("F2", "cubic spline trend", "Nominal and real. A natural cubic spline in time (knots at the first and last estimation months and at the NBER business-cycle peaks inside) in every monthly equation.",
       sum([pair(f, f, trend="spline") for f in VERSIONS], [])),
 # ---- appendix (kept from the earlier list where they still apply; real version)
 *both("A1", "sample ends in December 2019", "Real. All equations, monthly and daily.", pair("real", "real", end=2019, t2020="in")),
 *both("A2", "daily Baa-10-year spread in the daily block", "Real. The daily Baa-10-year Treasury spread enters the daily block next to the rates (and the FCI); its impact is its announcement-day change on the surprise; months before the daily data (1986) use the monthly series. Without the FCI: the rates and the spread (FS-A106).", [dict(form="real", fci="baa0"), dict(form="real", fci="baa")]),
 *both("A3", "Jarocinski-Karadi sign-restricted surprise", "Real. The Nakamura-Steinsson surprise kept only for announcements in which the 2-year yield and the S\\&P 500 move in opposite directions in the window.", pair("real", "real", shock="jk")),
 *both("A4", "the 1-year yield in place of the 2-year", "Nominal and real. The 1-year Treasury yield replaces the 2-year (the funds rate stays); responses per +1 pp on the 1-year yield in the window.",
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

# Short row labels and the groups of the 12-lag tables (each test from 1996 (<id>) and from 1973 (<id>73)); appendix tables are per panel.
_BASE_SHORT = {"R1": "2020 left in", "R2": "IP added", "R3": "Bauer-Swanson surprise", "R5": "Without the funds rate", "R6": "From 1985",
               "F1": "r*-gap (LW)", "F2": "Cubic spline trend", "A1": "Ends 2019", "A2": "Baa spread in the daily block", "A3": "Jarocinski-Karadi surprise", "A4": "1-year yield"}
SHORT = {"B": "Baseline, 1996", "B73": "Baseline, 1973", **{k: v + ", 1996" for k, v in _BASE_SHORT.items()}, **{k + "73": v + ", 1973" for k, v in _BASE_SHORT.items()}}
SHORT["R6"] = "Monthly equations from 1985"
def _both(*ids): return [x for k in ids for x in (k, k + "73")]
GROUPS = {"B": ["B", "B73"], "R": _both("R1", "R2", "R3", "R5") + ["R6"], "F": _both("F1", "F2"), "A": _both("A1", "A2", "A3", "A4")}
GROUP_TITLE = {"B": "Baselines: monthly equations from 1996 and from 1973, March-December 2020 dropped", "R": "robustness tests", "F": "slow-moving rates: the r*-gap step and a spline trend",
               "A": "further tests (appendix)"}
def panel_by_id(pid): return next(p for p in PANELS if p["id"] == pid)
GROUP_NOTE = {"B": "Nominal and real 2-year yield and funds rate; the FCI is the index in the matching form in each case. March-December 2020 dropped from the monthly and daily equations (values still enter as lags). From 1973: monthly series in place of daily data before 1990.",
              "R": "2020 left in: no month dummies. IP added: industrial production as a further monthly variable. Bauer-Swanson: orthogonalized surprise, announcements through 2019. Without the funds rate: the 2-year yield is the only rate in the daily block. From 1985: monthly equations from January 1985. Lag length: every case at 6 lags in the appendix tables.",
              "F": "r*-gap: rates less expected inflation and Laubach-Williams r*, the FCI in the r*-gap form. Spline: natural cubic spline in time in every monthly equation, knots at the first and last estimation months and at NBER peaks inside.",
              "A": "Ends 2019: all equations. Baa: daily Baa-10-year spread in the daily block. Jarocinski-Karadi: surprise kept when the 2-year yield and the S\\&P 500 move in opposite directions. 1-year yield: replaces the 2-year; its rows are per +1 pp on the 1-year yield in the window."}

# Monthly VAR benchmarks (lib/monthly.py): every step without and with the FCI in the same form, on monthly averages (FS-A76: one data type), March-December 2020 dropped,
# from 1996 and from 1973 (months before the daily data use the monthly series, as in the main model). The instrument (NS surprise) exists from 1996 only.
MONTHLY_STARTS = ("1996-01", "1973-01")
MONTHLY = [dict(step=s, fci=f, start=st) for st in MONTHLY_STARTS for s in ("nom", "real") for f in (0, s)]          # baseline_real: the funds rate in every system (lib/monthly.py)
def monthly_id(m): return f"monthly_{m['step']}_{m['fci']}_{m['start']}"
