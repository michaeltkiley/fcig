"""
FRB/US growth sensitivities of five financial variables, in federal funds rate equivalents.

Reconstructs the approach reported (by a third-party summary, unverified) for a Morgan Stanley financial conditions index built from the
10-year Treasury yield, S&P 500 returns, BBB credit spreads, the dollar and oil: each variable's effect on growth is estimated in FRB/US and
the combined effect is expressed as an equivalent change in the federal funds rate. See notes/morgan_stanley_fci.md.

Experiments (the Federal Reserve Board's public FRB/US model, VAR expectations, from the steady-state baseline in LONGBASE, 2040Q1 onward as in
the Board's demos): hold the funds rate (rff) and the other financial variables at baseline, make one persistent shock, and record the effect on
real GDP (log difference of xgdp from baseline, percent):
    rff   +1 pp                                       (policy rate)
    rg10  +1 pp   10-year Treasury yield; the mortgage rate and the BBB yield follow (BBB spread, rbbbp, held fixed)
    rbbbp +1 pp   BBB corporate bond spread over the 10-year
    req   +1 pp   required return on equity; the response of household stock wealth (wpsn) at impact gives the % stock price move
    fpxr  +10 %   real exchange rate, trade weighted (up = dollar appreciation)
    poil  +10 %   price of imported oil
The funds-rate equivalent of a shock at horizon q is its GDP effect at quarter q divided by the GDP effect of the 1 pp funds rate shock, per unit
(percentage point, or percent). Horizons: q4 (growth over the first year), q8 and q12.

Setup (FRB/US's Python package pins old libraries, so use an isolated environment):
    uv venv --python 3.9 venv39
    uv pip install --python venv39/bin/python "pandas<3,>=2.1" scipy numpy "sympy==1.3" symengine networkx multiprocess lxml matplotlib
    venv39/bin/python analysis/frbus_sensitivities.py
The script downloads pyfrbus.zip and data_only_package.zip from federalreserve.gov to raw/frbus/ (not committed).
Output: analysis/frbus_sensitivities.csv
"""
import os, sys, io, zipfile, urllib.request
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
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
    frbus.exogenize(["rff", "rg10", "rbbbp", "req", "fpxr", "poil"])   # hold the funds rate and the other financial variables fixed

    def run(var, shift, mult=False):
        d = base.copy()
        d.loc[start:end, var] = d.loc[start:end, var] * (1 + shift) if mult else d.loc[start:end, var] + shift
        return frbus.solve(start, end, d)

    sim0 = run("rff", 0.0)
    shocks = [("rff", 1.0, False, "pp"), ("rg10", 1.0, False, "pp"), ("rbbbp", 1.0, False, "pp"),
              ("req", 1.0, False, "stock"), ("fpxr", 0.10, True, "pct"), ("poil", 0.10, True, "pct")]
    gdp = lambda s: 100 * np.log(s.loc[start:end, "xgdp"] / sim0.loc[start:end, "xgdp"]).values
    out = {}
    for var, shift, mult, kind in shocks:
        sim = run(var, shift, mult)
        g = gdp(sim)
        if kind == "stock":
            unit = -100 * np.log(sim.loc[start, "wpsn"] / sim0.loc[start, "wpsn"])      # % fall in stock wealth at impact
        elif kind == "pct":
            unit = 100 * np.log(sim.loc[start, var] / sim0.loc[start, var])             # % change at impact
        else:
            unit = shift
        out[var] = dict(kind=kind, unit_size=float(unit), gdp_q4=g[3], gdp_q8=g[7], gdp_q12=g[11])
    t = pd.DataFrame(out).T
    for q in ("q4", "q8", "q12"):
        t[f"gdp_per_unit_{q}"] = t[f"gdp_{q}"].astype(float) / t["unit_size"].astype(float)
    ref = t.loc["rff"]
    for q in ("q4", "q8", "q12"):
        # funds rate equivalent (pp) of one unit: +1 pp (rates, spreads), 1% fall in stocks, +1% dollar, +1% oil
        t[f"ffr_eq_{q}"] = t[f"gdp_per_unit_{q}"] / ref[f"gdp_per_unit_{q}"]
    t.to_csv(os.path.join(HERE, "frbus_sensitivities.csv"), float_format="%.5f", index_label="variable")
    pd.set_option("display.width", 200)
    print(t[["kind", "unit_size", "gdp_q4", "gdp_q8", "gdp_q12", "ffr_eq_q4", "ffr_eq_q8", "ffr_eq_q12"]].astype({"unit_size": float}).round(3).to_string())
    print("\nFunds-rate equivalent (pp) per unit: rff = 1 pp; rg10 and rbbbp per +1 pp; req row per 1% FALL in stock wealth; fpxr per 1% dollar rise; poil per 1% oil rise")


if __name__ == "__main__":
    main()
