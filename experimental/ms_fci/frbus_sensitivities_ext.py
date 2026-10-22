"""
EXTENSION of frbus_sensitivities.py (unchanged): three more partial experiments for the macro-model levels index (policy rate, mortgage spread, house prices), same design.

Same FRB/US set-up (VAR expectations, steady-state baseline 2040Q1, 24 quarters), same exogenized list FIXED (policy rate, bill rate and the 5-, 10- and 30-year yields, mortgage and car-loan
rates, BBB spread, required return on equity and stock wealth, real exchange rate, oil), shocking one thing at a time; yardstick = the GDP effect of a 1 pp full-transmission hike
(taken from frbus_sensitivities.csv).
    rshort   +1 pp on the policy rate AND the 3-month bill rate (the short end), everything else in FIXED held at baseline; the VAR expectations (the 28 z-variables) respond, so this includes
             the effect of the funds rate as an input to expected inflation and activity (rff enters the expectations VAR)
    rshort_direct   the same with all 28 z expectation aggregates also held at baseline: the direct effect of the short rate, which is tiny (checked 22 Oct 2026)
    rme      +1 pp on the mortgage rate with the 10-year held fixed (= a mortgage spread shock)
    phouse   +10 % on the house price index (phouse; household housing wealth follows), everything else in FIXED held at baseline
Also prints the full-hike spillovers at q4 and a sum-of-partials check over the enlarged set.
Setup as in frbus_sensitivities.py (Python 3.9 venv with pyfrbus); output frbus_sensitivities_ext.csv.
Usage: venv39/bin/python experimental/ms_fci/frbus_sensitivities_ext.py
"""
import os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import frbus_sensitivities as F


def main():
    F.get_package()
    from pyfrbus.frbus import Frbus
    from pyfrbus.load_data import load_data
    data = load_data(os.path.join(F.RAW, "data_only_package", "LONGBASE.TXT"))
    frbus = Frbus(os.path.join(F.RAW, "pyfrbus", "models", "model.xml"))
    start = pd.Period("2040Q1"); end = start + 23
    data.loc[start:end, "dfpdbt"] = 0
    data.loc[start:end, "dfpsrp"] = 1
    base = frbus.init_trac(start, end, data)
    CURVE = ["rtb", "rg5", "rg10", "rg30"]; PASS = ["rme", "rcar"]; OTHER = ["rbbbp", "req", "wpsn", "fpxr", "poil"]
    FIXED = ["rff"] + CURVE + PASS + OTHER
    gdp = lambda s, s0: 100 * np.log(s.loc[start:end, "xgdp"] / s0.loc[start:end, "xgdp"]).values
    ref = pd.read_csv(os.path.join(HERE, "frbus_sensitivities.csv"), index_col=0)

    def run_with(exo, vars_, shift, mult=False):
        frbus.exogenize(exo)
        d0 = base.copy(); d1 = base.copy()
        for v in vars_:
            d1.loc[start:end, v] = d1.loc[start:end, v] * (1 + shift) if mult else d1.loc[start:end, v] + shift
        s0 = frbus.solve(start, end, d0); s1 = frbus.solve(start, end, d1)
        return s0, s1
    out = {}
    s0, s1 = run_with(FIXED, ["rff", "rtb"], 1.0)
    out["rshort"] = (gdp(s1, s0), 1.0)
    import re as _re
    xml = open(os.path.join(F.RAW, "pyfrbus", "models", "model.xml")).read()
    Zv = [v for v in _re.findall(r"<variable>\s*<name>([a-z0-9_]+)</name>", xml) if v.startswith("z") and v in base.columns]
    s0, s1 = run_with(FIXED + Zv, ["rff", "rtb"], 1.0)
    out["rshort_direct"] = (gdp(s1, s0), 1.0)
    s0, s1 = run_with(FIXED, ["rme"], 1.0)
    out["rme"] = (gdp(s1, s0), 1.0)
    s0, s1 = run_with(FIXED + ["phouse"], ["phouse"], 0.10, mult=True)
    out["phouse"] = (gdp(s1, s0), 100 * np.log(1.10))
    rows = {}
    for k, (g, unit) in out.items():
        r = {"unit_size": unit}
        for q, i in (("q4", 3), ("q8", 7), ("q12", 11)):
            gpu = g[i] / unit
            r[f"gdp_{q}"] = g[i]; r[f"gdp_per_unit_{q}"] = gpu
            r[f"ffr_eq_{q}"] = gpu / float(ref.loc["rff", f"gdp_per_unit_{q}"])
        rows[k] = r
    t = pd.DataFrame(rows).T
    t.to_csv(os.path.join(HERE, "frbus_sensitivities_ext.csv"), float_format="%.5f", index_label="variable")
    pd.set_option("display.width", 200)
    print(t[["unit_size", "gdp_q4", "gdp_q8", "gdp_q12", "ffr_eq_q4", "ffr_eq_q8", "ffr_eq_q12"]].round(4).to_string())
    print("\nFunds-rate equivalent (pp) per unit: rshort per +1 pp on the policy and bill rates; rme per +1 pp mortgage spread; phouse per +1 % house price")
    # full hike spillovers and a sum-of-partials check
    frbus.exogenize(["rff"])
    d0 = base.copy(); d1 = base.copy(); d1.loc[start:end, "rff"] += 1.0
    f0 = frbus.solve(start, end, d0); f1 = frbus.solve(start, end, d1)
    gF = gdp(f1, f0)
    q = start + 3
    sp = {"rff": f1.loc[q, "rff"] - f0.loc[q, "rff"], "rtb": f1.loc[q, "rtb"] - f0.loc[q, "rtb"], "rg10": f1.loc[q, "rg10"] - f0.loc[q, "rg10"],
          "rg5": f1.loc[q, "rg5"] - f0.loc[q, "rg5"], "rg30": f1.loc[q, "rg30"] - f0.loc[q, "rg30"],
          "mortgage spread": (f1.loc[q, "rme"] - f1.loc[q, "rg10"]) - (f0.loc[q, "rme"] - f0.loc[q, "rg10"]),
          "BBB spread": f1.loc[q, "rbbbp"] - f0.loc[q, "rbbbp"], "stocks %": 100 * np.log(f1.loc[q, "wpsn"] / f0.loc[q, "wpsn"]),
          "dollar %": 100 * np.log(f1.loc[q, "fpxr"] / f0.loc[q, "fpxr"]), "house prices %": 100 * np.log(f1.loc[q, "phouse"] / f0.loc[q, "phouse"])}
    print("\nFull 1 pp hike, spillovers at q4:", {k: round(float(v), 2) for k, v in sp.items()})
    # partial sums with the existing per-unit effects (original and extension); policy+short end and curve handled separately
    per = lambda v, qq: float(ref.loc[v, f"gdp_per_unit_{qq}"])
    for qq, i in (("q4", 3), ("q8", 7), ("q12", 11)):
        parts = {"short end (with VAR expectations)": sp["rff"] * float(t.loc["rshort", f"gdp_per_unit_{qq}"]), "short end (direct)": sp["rff"] * float(t.loc["rshort_direct", f"gdp_per_unit_{qq}"]), "10-year (parallel curve)": sp["rg10"] * per("rg10", qq),
                 "mortgage spread": sp["mortgage spread"] * float(t.loc["rme", f"gdp_per_unit_{qq}"]), "BBB spread": sp["BBB spread"] * per("rbbbp", qq),
                 "stocks": -sp["stocks %"] * per("req", qq), "dollar": sp["dollar %"] * per("fpxr", qq), "house prices": sp["house prices %"] * float(t.loc["phouse", f"gdp_per_unit_{qq}"])}
        tot_exp = sum(v for k, v in parts.items() if k != "short end (direct)"); tot_dir = sum(v for k, v in parts.items() if k != "short end (with VAR expectations)")
        print(f"  {qq}: full hike GDP {gF[i]:+.3f}; sum of partials with the short end incl. expectations {tot_exp:+.3f}, with the direct short end {tot_dir:+.3f}; parts: " + ", ".join(f"{k} {v:+.3f}" for k, v in parts.items()))


if __name__ == "__main__":
    main()
