"""
FRB/US growth sensitivities of five financial variables, in federal funds rate equivalents.

Reconstructs the approach reported (by a third-party summary, unverified) for a Morgan Stanley financial conditions index built from the
10-year Treasury yield, S&P 500 returns, BBB credit spreads, the dollar and oil: each variable's effect on growth is estimated in FRB/US and
the combined effect is expressed as an equivalent change in the federal funds rate. See experimental/ms_fci/NOTES.md.

Experiments (the Federal Reserve Board's public FRB/US model, VAR expectations, from the steady-state baseline in LONGBASE, 2040Q1 onward as in
the Board's demos). One persistent shock to one variable at a time. In the partial experiments stocks (req, wpsn), the dollar (fpxr), oil (poil) and the BBB spread
(rbbbp) are held at baseline except their own, since each is a separate index variable, and the funds rate is held fixed; the yardstick, a funds-rate hike,
is run with full transmission to all of them. Effect on real GDP (log difference of xgdp from baseline, percent):
    rff        +1 pp  policy rate with FULL transmission (nothing else held fixed): the yardstick, i.e. what a hike does
    rff_curve  +1 pp  policy rate with the curve responding but stocks, dollar, oil and the BBB spread held fixed (partial hike; alternative yardstick)
    rg10       +1 pp  parallel move in the 5-, 10- and 30-year Treasury yields (the 10-year stands for the long end); mortgage rate and BBB yield
                      follow, the BBB spread is unchanged
    rg10_alone +1 pp  the 10-year only, with the 5- and 30-year unchanged (a kink in the curve; equity valuation depends on the 30-year, not the
                      10-year, so this moves nothing else); an alternative reading
    rbbbp      +1 pp  BBB corporate bond spread over the 10-year
    req        +1 pp  required return on equity; stock wealth (wpsn) responds (wealth and cost-of-capital channels), its fall at impact is the unit
    fpxr       +10 %  real exchange rate, trade weighted (up = dollar appreciation)
    poil       +10 %  price of imported oil
The funds-rate equivalent of a shock at horizon q is its (partial) GDP effect at quarter q divided by the GDP effect of the 1 pp full-transmission
funds-rate hike, per unit
(percentage point, or percent). Horizons: q4 (growth over the first year), q8 and q12.

Setup (FRB/US's Python package pins old libraries, so use an isolated environment):
    uv venv --python 3.9 venv39
    uv pip install --python venv39/bin/python "pandas<3,>=2.1" scipy numpy "sympy==1.3" symengine networkx multiprocess lxml matplotlib
    venv39/bin/python experimental/ms_fci/frbus_sensitivities.py
The script downloads pyfrbus.zip and data_only_package.zip from federalreserve.gov to raw/frbus/ (not committed).
Output: experimental/ms_fci/frbus_sensitivities.csv
"""
import os, sys, io, zipfile, urllib.request
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
RAW = os.path.join(ROOT, "raw", "frbus")
BASE_URL = "https://www.federalreserve.gov/econres/files/"


def get_package():
    os.makedirs(RAW, exist_ok=True)
    for z, marker in (("pyfrbus.zip", "pyfrbus"), ("data_only_package.zip", "data_only_package")):
        if not os.path.exists(os.path.join(RAW, marker)):
            req = urllib.request.Request(BASE_URL + z, headers={"User-Agent": "Mozilla/5.0"})
            zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(req, timeout=120).read())).extractall(RAW)
    sys.path.insert(0, os.path.join(RAW, "pyfrbus"))


def main():
    get_package()
    from pyfrbus.frbus import Frbus
    from pyfrbus.load_data import load_data
    data = load_data(os.path.join(RAW, "data_only_package", "LONGBASE.TXT"))
    frbus = Frbus(os.path.join(RAW, "pyfrbus", "models", "model.xml"))
    start = pd.Period("2040Q1")
    end = start + 23
    data.loc[start:end, "dfpdbt"] = 0      # fiscal settings as in the Board's demos
    data.loc[start:end, "dfpsrp"] = 1
    base = frbus.init_trac(start, end, data)
    # One consistent design. Stocks (req, wpsn), the dollar (fpxr), oil (poil) and the BBB spread (rbbbp) are held at baseline in every experiment
    # except their own, because each is a separate variable in the index. Rates that are not index variables (5- and 30-year Treasuries, the
    # mortgage rate, car loans, the BBB yield = 10-year + spread) respond as the model implies, or move with the shock where stated.
    # Financial conditions held at baseline (exogenized) in every partial experiment except the shocked variable:
    #   policy rate rff; 3-month bill rtb; Treasury curve rg5, rg10, rg30; mortgage rate rme; new car loan rate rcar; BBB spread rbbbp (so the BBB yield
    #   rbbb = rbbbp + rg10 is fixed too); required return on equity req and household stock wealth wpsn; real exchange rate fpxr; oil price poil.
    # rme and rcar are the pass-through of the long-rate shock (they follow rg10 and rg5), so they are free in that experiment and fixed in the others.
    CURVE = ["rtb", "rg5", "rg10", "rg30"]
    PASS = ["rme", "rcar"]
    OTHER = ["rbbbp", "req", "wpsn", "fpxr", "poil"]
    FIXED = ["rff"] + CURVE + PASS + OTHER                 # everything fixed (BBB spread, dollar and oil experiments)
    PARTIAL_HIKE = ["rff"] + OTHER                         # partial hike: curve, mortgage and car loan rates respond, stocks/dollar/spread/oil fixed
    gdp = lambda s, s0: 100 * np.log(s.loc[start:end, "xgdp"] / s0.loc[start:end, "xgdp"]).values
    EXOGLISTS = {}

    def solver(exo, label):
        EXOGLISTS[label] = list(exo)
        frbus.exogenize(exo)

        def run(vars_, shift, mult=False):
            d = base.copy()
            for v in (vars_ if isinstance(vars_, (list, tuple)) else [vars_]):
                d.loc[start:end, v] = d.loc[start:end, v] * (1 + shift) if mult else d.loc[start:end, v] + shift
            return frbus.solve(start, end, d)
        return run

    out = {}

    def record(name, kind, g, unit):
        out[name] = dict(kind=kind, unit_size=float(unit), gdp_q4=g[3], gdp_q8=g[7], gdp_q12=g[11])

    # policy rate, FULL transmission (the yardstick): +1 pp in the funds rate with nothing else held fixed, so the whole curve, mortgage and
    # corporate yields, stocks, the dollar, spreads and oil all respond as the model implies. This is what a hike does.
    run = solver(["rff"], "rff (full transmission)")
    s0 = run("rff", 0.0)
    sF = run("rff", 1.0)
    gF = gdp(sF, s0)
    record("rff", "pp", gF, 1.0)
    spill = {c: float(sF.loc[start + 3, c] - s0.loc[start + 3, c]) for c in ("rg5", "rg10", "rg30", "rme", "rbbb", "rbbbp")}
    spill["stocks_pct"] = float(100 * np.log(sF.loc[start + 3, "wpsn"] / s0.loc[start + 3, "wpsn"]))
    spill["dollar_pct"] = float(100 * np.log(sF.loc[start + 3, "fpxr"] / s0.loc[start + 3, "fpxr"]))
    spill["oil_pct"] = float(100 * np.log(sF.loc[start + 3, "poil"] / s0.loc[start + 3, "poil"]))
    # policy rate with the curve responding but stocks, dollar, oil and the BBB spread held fixed (the partial hike)
    run = solver(PARTIAL_HIKE, "rff_curve (partial hike)")
    s0 = run("rff", 0.0)
    gC = gdp(run("rff", 1.0), s0)
    record("rff_curve", "pp", gC, 1.0)
    # 10-year: a parallel +1 pp move in the 5-, 10- and 30-year yields (the 10-year stands for the long end); the mortgage rate and the BBB
    # yield follow (spread unchanged). The alternative, the 10-year alone with the 5- and 30-year unchanged, is reported as rg10_alone.
    run = solver([v for v in FIXED if v not in PASS], "rg10 (parallel long rates)")
    s0 = run("rff", 0.0)
    record("rg10", "pp", gdp(run(["rg5", "rg10", "rg30"], 1.0), s0), 1.0)
    run = solver([v for v in FIXED if v not in PASS], "rg10_alone")
    s0 = run("rff", 0.0)
    record("rg10_alone", "pp", gdp(run("rg10", 1.0), s0), 1.0)
    # BBB spread, dollar, oil: policy rate fixed, everything else fixed
    for var, shift, mult, kind in (("rbbbp", 1.0, False, "pp"), ("fpxr", 0.10, True, "pct"), ("poil", 0.10, True, "pct")):
        run = solver(FIXED, f"{var} (everything fixed)")
        s0 = run("rff", 0.0)
        record(var, kind, gdp(run(var, shift, mult), s0), 100 * np.log(1 + shift) if kind == "pct" else shift)
    # equities: shock the required return on equity (req), stock wealth (wpsn) free to respond (wealth and cost-of-capital channels); the % fall
    # in stock wealth at impact is the unit
    run = solver([v for v in FIXED if v != "wpsn"], "req (stock wealth free)")
    s0 = run("rff", 0.0)
    sim = run("req", 1.0)
    record("req", "stock", gdp(sim, s0), -100 * np.log(sim.loc[start, "wpsn"] / s0.loc[start, "wpsn"]))
    out = {k: out[k] for k in ("rff", "rff_curve", "rg10", "rg10_alone", "rbbbp", "req", "fpxr", "poil")}
    t = pd.DataFrame(out).T
    for q in ("q4", "q8", "q12"):
        t[f"gdp_per_unit_{q}"] = t[f"gdp_{q}"].astype(float) / t["unit_size"].astype(float)
    ref, refc = t.loc["rff"], t.loc["rff_curve"]
    for q in ("q4", "q8", "q12"):
        # funds rate equivalent (pp) of one unit against a full-transmission hike (default); *_curve: against the partial hike
        t[f"ffr_eq_{q}"] = t[f"gdp_per_unit_{q}"] / ref[f"gdp_per_unit_{q}"]
        t[f"ffr_eq_curve_{q}"] = t[f"gdp_per_unit_{q}"] / refc[f"gdp_per_unit_{q}"]
    t.to_csv(os.path.join(HERE, "frbus_sensitivities.csv"), float_format="%.5f", index_label="variable")
    # do the partial effects add up to the full hike? Apply the q4 spillovers of the full hike to the partial per-unit effects.
    per = lambda v, q: float(t.loc[v, f"gdp_per_unit_{q}"])
    print("\nSpillovers of a 1 pp full-transmission hike at q4:", {k: round(v, 2) for k, v in spill.items()})
    for q, gi in (("q4", 3), ("q8", 7), ("q12", 11)):
        parts = {"policy rate and Treasury curve": float(t.loc["rff_curve", f"gdp_{q}"]),
                 "stocks": -spill["stocks_pct"] * per("req", q), "dollar": spill["dollar_pct"] * per("fpxr", q),
                 "BBB spread": spill["rbbbp"] * per("rbbbp", q), "oil": spill["oil_pct"] * per("poil", q)}
        print(f"  {q}: full hike GDP {gF[gi]:+.3f}; sum of partials {sum(parts.values()):+.3f} = " + ", ".join(f"{k} {v:+.3f}" for k, v in parts.items()))
    print("\nexoglists used:")
    for k, v in EXOGLISTS.items():
        print(f"  {k}: {v}")
    pd.set_option("display.width", 200)
    print(t[["kind", "unit_size", "gdp_q4", "gdp_q8", "gdp_q12", "ffr_eq_q4", "ffr_eq_q8", "ffr_eq_q12", "ffr_eq_curve_q4"]].astype({"unit_size": float}).round(3).to_string())
    print("\nFunds-rate equivalent (pp) per unit: rff = 1 pp; rg10 and rbbbp per +1 pp; req row per 1% FALL in stock wealth; fpxr per 1% dollar rise; poil per 1% oil rise")


if __name__ == "__main__":
    main()
