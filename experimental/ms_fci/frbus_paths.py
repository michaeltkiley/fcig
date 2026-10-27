"""
FRB/US GDP paths, quarters 1-32, for the partial experiments behind the macro-model levels index (DYNAMICS_PLAN.md, step 1a).
Same set-up and exogenized lists as frbus_sensitivities.py / _ext.py (VAR expectations, steady-state baseline from 2040Q1, fiscal settings as in the Board's demos).
For each financial variable, two shock shapes:
    persistent  the variable is shifted in every quarter (as in the existing sensitivities; response at q = Phi_q, the cumulative response)
    temporary   the variable is shifted in the first quarter only (response at q = phi_q, the one-period response); linearity check: Phi_q = sum_{i<=q} phi_i
Two expectation designs:
    zfree   the 28 VAR expectation aggregates (z-variables) respond (the design of the existing partials, except rshort_direct)
    zfixed  the z-variables are held at baseline in every partial experiment (one definition for all, open item 4; matches rshort_direct)
The yardstick (rff, full transmission, z free) is always run as in the original; its financial spillover paths by quarter are saved too (FRB/US psi_h).
Experiments and units: rshort (policy + bill rate, +1 pp), rg10 (5-, 10-, 30-year parallel, +1 pp; mortgage and car-loan rates follow), rme (mortgage spread, +1 pp),
rbbbp (+1 pp), req (equities: per 1% FALL in stock wealth at impact in the persistent experiment), fpxr (real dollar, per 1% rise), phouse (per 1% rise).
Usage: <venv39>/bin/python experimental/ms_fci/frbus_paths.py
Outputs: frbus_paths.csv (design, experiment, shape, quarter 1-32, gdp per unit, funds-rate equivalent against the hike at the same quarter), frbus_hike_paths.csv
"""
import os, sys, re
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import frbus_sensitivities as F

H = 32


def main():
    F.get_package()
    from pyfrbus.frbus import Frbus
    from pyfrbus.load_data import load_data
    data = load_data(os.path.join(F.RAW, "data_only_package", "LONGBASE.TXT"))
    frbus = Frbus(os.path.join(F.RAW, "pyfrbus", "models", "model.xml"))
    start = pd.Period("2040Q1"); end = start + H + 7
    data.loc[start:end, "dfpdbt"] = 0
    data.loc[start:end, "dfpsrp"] = 1
    base = frbus.init_trac(start, end, data)
    CURVE = ["rtb", "rg5", "rg10", "rg30"]; PASS = ["rme", "rcar"]; OTHER = ["rbbbp", "req", "wpsn", "fpxr", "poil"]
    FIXED = ["rff"] + CURVE + PASS + OTHER
    xml = open(os.path.join(F.RAW, "pyfrbus", "models", "model.xml")).read()
    Zv = [v for v in re.findall(r"<variable>\s*<name>([a-z0-9_]+)</name>", xml) if v.startswith("z") and v in base.columns]
    gdp = lambda s, s0: 100 * np.log(s.loc[start:start + H - 1, "xgdp"] / s0.loc[start:start + H - 1, "xgdp"]).values

    def run(exo, vars_, shift, mult=False, temporary=False):
        frbus.exogenize(list(exo))
        d0 = base.copy(); d1 = base.copy()
        last = start if temporary else end
        for v in vars_:
            d1.loc[start:last, v] = d1.loc[start:last, v] * (1 + shift) if mult else d1.loc[start:last, v] + shift
        return frbus.solve(start, end, d0), frbus.solve(start, end, d1)

    # yardstick and its spillover paths
    f0, f1 = run(["rff"], ["rff"], 1.0)
    gF = gdp(f1, f0)
    q = slice(start, start + H - 1)
    hike = pd.DataFrame({"quarter": np.arange(1, H + 1), "gdp": gF,
                         "rff": (f1.loc[q, "rff"] - f0.loc[q, "rff"]).values, "rtb": (f1.loc[q, "rtb"] - f0.loc[q, "rtb"]).values,
                         "rg10": (f1.loc[q, "rg10"] - f0.loc[q, "rg10"]).values,
                         "mortgage spread": ((f1.loc[q, "rme"] - f1.loc[q, "rg10"]) - (f0.loc[q, "rme"] - f0.loc[q, "rg10"])).values,
                         "rbbbp": (f1.loc[q, "rbbbp"] - f0.loc[q, "rbbbp"]).values,
                         "stocks %": 100 * np.log(f1.loc[q, "wpsn"] / f0.loc[q, "wpsn"]).values,
                         "dollar %": 100 * np.log(f1.loc[q, "fpxr"] / f0.loc[q, "fpxr"]).values,
                         "house prices %": 100 * np.log(f1.loc[q, "phouse"] / f0.loc[q, "phouse"]).values})
    hike.to_csv(os.path.join(HERE, "frbus_hike_paths.csv"), float_format="%.5f", index=False)
    print("full hike GDP q4/q8/q12:", np.round(gF[[3, 7, 11]], 4), "(frbus_sensitivities.csv: -0.4525, -0.9456, -1.4302)")

    # (name, shocked vars, shift, mult, exogenized list, unit kind)
    EXP = [("rshort", ["rff", "rtb"], 1.0, False, FIXED),
           ("rg10", ["rg5", "rg10", "rg30"], 1.0, False, [v for v in FIXED if v not in PASS]),
           ("rme", ["rme"], 1.0, False, FIXED),
           ("rbbbp", ["rbbbp"], 1.0, False, FIXED),
           ("req", ["req"], 1.0, False, [v for v in FIXED if v != "wpsn"]),
           ("fpxr", ["fpxr"], 0.10, True, FIXED),
           ("phouse", ["phouse"], 0.10, True, FIXED + ["phouse"])]
    rows = []
    for design in ("zfree", "zfixed"):
        for name, vars_, shift, mult, exo in EXP:
            exo = list(exo) + (Zv if design == "zfixed" else [])
            unit = None
            for shape in ("persistent", "temporary"):
                s0, s1 = run(exo, vars_, shift, mult, temporary=(shape == "temporary"))
                g = gdp(s1, s0)
                if unit is None:          # unit from the persistent experiment
                    unit = (-100 * np.log(s1.loc[start, "wpsn"] / s0.loc[start, "wpsn"])) if name == "req" else (100 * np.log(1 + shift) if mult else shift)
                sign = -1.0 if name == "req" else 1.0          # equities: per 1% FALL -> report per 1% RISE below
                for i in range(H):
                    rows.append(dict(design=design, experiment=name, shape=shape, quarter=i + 1, gdp_per_unit=sign * g[i] / unit, ffr_eq=sign * g[i] / unit / gF[i]))
            print(f"{design:6s} {name:7s} unit {unit:.3f}: persistent ffr_eq q4/q8/q12 " +
                  " / ".join(f"{r['ffr_eq']:+.4f}" for r in rows if r["design"] == design and r["experiment"] == name and r["shape"] == "persistent" and r["quarter"] in (4, 8, 12)))
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(HERE, "frbus_paths.csv"), float_format="%.6f", index=False)
    # linearity check: persistent response vs cumulated temporary responses
    print("\nlinearity check (max abs diff, persistent minus cumulated temporary, gdp per unit, quarters 1-32):")
    for (d, e), g in out.groupby(["design", "experiment"]):
        p = g[g["shape"] == "persistent"].sort_values("quarter").gdp_per_unit.values
        t = g[g["shape"] == "temporary"].sort_values("quarter").gdp_per_unit.values.cumsum()
        print(f"  {d:6s} {e:7s} {np.abs(p - t).max():.5f} (max |persistent| {np.abs(p).max():.4f})")


if __name__ == "__main__":
    main()
