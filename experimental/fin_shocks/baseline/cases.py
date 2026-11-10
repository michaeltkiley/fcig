"""The case list for the baseline and robustness tables (edit here; run_all.py and make_report.py read it).
Every case is run without the FCI and with the FCI. No deterministic trends anywhere. u gap and core PCE price level, 3/6/12 lags.
A case is (form, fci, macro, start, end, t2020); see engine.py."""
FORMS = {"nom": "Nominal", "real": "Real", "rstar": "r*-gap", "kiley": "r*-gap (Kiley r*)", "ma8": "Minus 8-year average"}
FCI_LABEL = {0: "none", "nom": "nominal", "real": "real", "rstar": "r*-gap", "baa": "r*-gap + Baa spread"}

def pair(form, fci_with, **kw):
    """The same rate without and with the FCI."""
    return [dict(form=form, fci=0, **kw), dict(form=form, fci=fci_with, **kw)]

def panel(pid, title, notes, cases):
    base = dict(macro="u,pi", start="1994-02", end=None, t2020="in")
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
 panel("R2a", "Robustness 2a: Kiley r*, start 1994", "2-year minus expected inflation minus Kiley's r*; the FCI is the r*-gap index of Note A (Laubach-Williams).",
       pair("kiley", "rstar")),
 panel("R2b", "Robustness 2b: Kiley r*, start 1973", "As 2a.", pair("kiley", "rstar", start="1973-01")),
 panel("R2c", "Robustness 2c: 2-year minus its trailing 8-year average, start 1994",
       "The daily 8-year average needs eight years of daily data, so the daily block is estimated from 1998 on; the FCI is the r*-gap index of Note A.",
       pair("ma8", "rstar")),
 panel("R2d", "Robustness 2d: 2-year minus its trailing 8-year average, start 1973", "As 2c.", pair("ma8", "rstar", start="1973-01")),
 panel("R3a", "Robustness 3a: r*-gap FCI plus the Baa-10-year spread, start 1994",
       "The spread enters the daily block and responds on impact (event-day change per +1 pp 2-year). Only with the FCI.",
       [dict(form="rstar", fci="baa")]),
 panel("R3b", "Robustness 3b: excess bond premium as a third monthly variable, start 1994",
       "r*-gap. Monthly system u, inflation, EBP (EBP treated like u and inflation; responses shown for u and the price level).",
       pair("rstar", "rstar", macro="u,pi,ebp")),
 panel("R3c", "Robustness 3c: excess bond premium as a third monthly variable, start 1973", "As 3b.",
       pair("rstar", "rstar", macro="u,pi,ebp", start="1973-01")),
]

def case_id(c):
    return "_".join([c["form"], str(c["fci"]), c["macro"].replace(",", ""), c["start"], str(c["end"] or "all"), c["t2020"]])

def unique_cases():
    seen, out = set(), []
    for p in PANELS:
        for c in p["cases"]:
            if case_id(c) not in seen: seen.add(case_id(c)); out.append(c)
    return out
