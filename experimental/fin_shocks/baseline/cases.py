"""The case list for the baseline and robustness tables (edit here; run_all.py and make_report.py read it).
Every case is run without the FCI and with the FCI. No deterministic trend except Robustness 2c-f (quadratic and natural cubic spline). u gap and core PCE price level, 3/6/12 lags.
A case is (form, fci, macro, start, end, t2020, trend); see engine.py."""
FORMS = {"nom": "Nominal", "real": "Real", "rstar": "r*-gap", "kiley": "r*-gap (Kiley)"}
FCI_LABEL = {0: "none", "nom": "nominal", "real": "real", "rstar": "r*-gap", "kiley": "r*-gap (Kiley)"}

def pair(form, fci_with, **kw):
    """The same rate without and with the FCI."""
    return [dict(form=form, fci=0, **kw), dict(form=form, fci=fci_with, **kw)]

def panel(pid, title, notes, cases):
    base = dict(macro="u,pi", start="1994-02", end=None, t2020="in", trend="none")
    return dict(id=pid, title=title, notes=notes, cases=[{**base, **c} for c in cases])

PANELS = [
 panel("B", "Baseline: 1994 to the present, all data in, no trend",
       "Nominal, real and r*-gap 2-year yield; the FCI is the matching index of Note A in each case.",
       sum([pair(f, f) for f in ("nom", "real", "rstar")], [])),
 panel("R1a", "Robustness 1a: monthly equations start in 1973", "r*-gap only. Pre-1990 months use the spliced monthly series (FS-A29); shocks still 1996 on.",
       pair("rstar", "rstar", start="1973-01")),
 panel("R1b", "Robustness 1b: 2020 dropped from all equations, start 1994", "r*-gap only. March to December 2020 dropped from the monthly and the daily equations.",
       pair("rstar", "rstar", t2020="out")),
 panel("R1c", "Robustness 1c: 2020 dropped from all equations, start 1973", "r*-gap only.",
       pair("rstar", "rstar", start="1973-01", t2020="out")),
 panel("R1d", "Robustness 1d: sample ends in December 2019, start 1994", "r*-gap only. All equations, monthly and daily.",
       pair("rstar", "rstar", end=2019)),
 panel("R1e", "Robustness 1e: sample ends in December 2019, start 1973", "r*-gap only.",
       pair("rstar", "rstar", start="1973-01", end=2019)),
 panel("R2a", "Robustness 2a: Kiley r*, start 1994", "2-year minus expected inflation minus Kiley's r*; the FCI is Note A's index built with Kiley's r* (same adjustment in rate and FCI).",
       pair("kiley", "kiley")),
 panel("R2b", "Robustness 2b: Kiley r*, start 1973", "As 2a.", pair("kiley", "kiley", start="1973-01")),
 panel("R2c", "Robustness 2c: real 2-year and real FCI with a quadratic trend, start 1994",
       "No r* measure: the trend is a quadratic in time ($t$ and $t^2$, $t$ in decades from 2010), estimated in every monthly equation.",
       pair("real", "real", trend="quad")),
 panel("R2d", "Robustness 2d: real 2-year and real FCI with a quadratic trend, start 1973", "As 2c.",
       pair("real", "real", start="1973-01", trend="quad")),
 panel("R2e", "Robustness 2e: real 2-year and real FCI with a cubic spline trend, start 1994",
       "No r* measure: the trend is a natural cubic spline in time (knots at the sample ends and at the NBER business-cycle peaks inside the sample), estimated in every monthly equation.",
       pair("real", "real", trend="spline")),
 panel("R2f", "Robustness 2f: real 2-year and real FCI with a cubic spline trend, start 1973", "As 2e; knots at the NBER peaks of 1973, 1980, 1981, 1990, 2001, 2007 and 2020.",
       pair("real", "real", start="1973-01", trend="spline")),
 panel("R3a", "Robustness 3a: excess bond premium as a third monthly variable, start 1994",
       "r*-gap. Monthly system u, inflation, EBP (EBP treated like u and inflation; responses shown for u and the price level).",
       pair("rstar", "rstar", macro="u,pi,ebp")),
 panel("R3b", "Robustness 3b: excess bond premium as a third monthly variable, start 1973", "As 3a.",
       pair("rstar", "rstar", macro="u,pi,ebp", start="1973-01")),
]

def case_id(c):
    return "_".join([c["form"], str(c["fci"]), c["macro"].replace(",", ""), c["start"], str(c["end"] or "all"), c["t2020"]] + ([] if c["trend"] == "none" else [c["trend"]]))

def unique_cases():
    seen, out = set(), []
    for p in PANELS:
        for c in p["cases"]:
            if case_id(c) not in seen: seen.add(case_id(c)); out.append(c)
    return out
