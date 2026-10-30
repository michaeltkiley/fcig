"""
FRB/US partial experiments under model-consistent expectations (user's design, 28 Oct 2026; INDEX_QA.md, answers 5-6).

Design
    expectations   model-consistent for all variables (Frbus(..., mce="all")); a VAR-expectations run with the same design is the bridge to the old weights
    policy         inertial Taylor (1999) rule in every experiment (dmpintay = 1, other rule switches 0, thresholds off)
    horizon        240 quarters from 2040Q1 (LONGBASE steady state), for convergence of the forward-looking solution
    yardstick      funds rate held 100 bp above baseline in quarters 1-4 (mcontrol on rff, instrument rffintay_aerr), then the rule with no shock; everything else endogenous
    partials       one financial variable shifted by one unit in quarters 1-4 and back to baseline afterwards (exogenous); the other financial variables are held at baseline
                   throughout (answer 6, option 3): 3-month bill, 5-, 10- and 30-year Treasury, mortgage and car-loan rates, BBB spread, required return on equity and
                   stock wealth, real dollar, oil, house prices. The funds rate follows the rule (it responds to the shock's effect on the economy).
        rshort   funds rate +1 pp above baseline in quarters 1-4 (mcontrol) and the bill rate +1 pp, others fixed (the direct effect of the short end)
        rg10     5-, 10- and 30-year +1 pp (mortgage and car-loan rates follow, as in the old design)
        rme      mortgage rate +1 pp (= mortgage spread, 10-year fixed)
        rbbbp    BBB spread +1 pp
        req      required return on equity +1 pp, stock wealth free; unit = % fall in stock wealth in quarter 1 (weights reported per 1% RISE)
        fpxr     real dollar +10% (per 1%);   phouse   house prices +10% (per 1%)
    weight = GDP effect per unit at quarter q / yardstick GDP effect at quarter q (q = 4 main; 8 and 12 robustness)
Old weights (frbus_sensitivities*.csv: VAR expectations, persistent shifts, funds rate fixed in partials) are printed for comparison.
Usage: <venv39>/bin/python experimental/ms_fci/frbus_mce.py
Outputs: frbus_mce.csv (weights), frbus_mce_paths.csv (GDP paths, quarters 1-40)
"""
import os, sys, time
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import frbus_sensitivities as F

NQ = 240
CURVE = ["rtb", "rg5", "rg10", "rg30"]; PASS = ["rme", "rcar"]
OTHER = ["rbbbp", "req", "wpsn", "fpxr", "poil", "phouse"]
FIXED = CURVE + PASS + OTHER                      # held at baseline in every partial except the shocked variable(s)
EXP = [("rshort", ["rtb"], 1.0, False, FIXED),
       ("rg10", ["rg5", "rg10", "rg30"], 1.0, False, [v for v in FIXED if v not in PASS]),
       ("rme", ["rme"], 1.0, False, FIXED),
       ("rbbbp", ["rbbbp"], 1.0, False, FIXED),
       ("req", ["req"], 1.0, False, [v for v in FIXED if v != "wpsn"]),
       ("fpxr", ["fpxr"], 0.10, True, FIXED),
       ("phouse", ["phouse"], 0.10, True, FIXED)]


def main():
    F.get_package()
    from pyfrbus.frbus import Frbus
    from pyfrbus.load_data import load_data
    data = load_data(os.path.join(F.RAW, "data_only_package", "LONGBASE.TXT"))
    start = pd.Period("2040Q1"); end = start + NQ - 1
    data.loc[start:end, "dfpdbt"] = 0
    data.loc[start:end, "dfpsrp"] = 1
    for v in ("dmptay", "dmptlr", "dmpex", "dmprr", "dmpalt", "dmptrsh"):
        data.loc[start:end, v] = 0
    data.loc[start:end, "dmpintay"] = 1
    q4 = slice(start, start + 3)
    gdp = lambda s, s0: 100 * np.log(s.loc[start:start + 39, "xgdp"] / s0.loc[start:start + 39, "xgdp"]).values
    results, paths = {}, {}
    for design, mce in (("VAR", None), ("MCE", "all")):
        t0 = time.time()
        frbus = Frbus(os.path.join(F.RAW, "pyfrbus", "models", "model.xml"), mce=mce)
        base = frbus.init_trac(start, end, data)
        base["rff_traj"] = np.nan
        base.loc[q4, "rff_traj"] = base.loc[q4, "rff"] + 1.0

        def solve(exo, shift_vars, shift, mult, control_rff):
            frbus.exogenize(list(exo))
            d0 = base.copy(); d1 = base.copy()
            for v in shift_vars:
                d1.loc[q4, v] = d1.loc[q4, v] * (1 + shift) if mult else d1.loc[q4, v] + shift
            s0 = frbus.solve(start, end, d0)
            s1 = frbus.mcontrol(start, end, d1, ["rff"], ["rff_traj"], ["rffintay_aerr"]) if control_rff else frbus.solve(start, end, d1)
            return s0, s1
        # yardstick
        s0, s1 = solve([], [], 0.0, False, True)
        gY = gdp(s1, s0)
        paths[(design, "yardstick")] = gY
        print(f"[{design}] yardstick: rff q1-q6 {np.round((s1.loc[start:start + 5, 'rff'] - s0.loc[start:start + 5, 'rff']).values, 2)}; GDP q4/q8/q12 {np.round(gY[[3, 7, 11]], 3)}; "
              f"rg10 q1 {float(s1.loc[start, 'rg10'] - s0.loc[start, 'rg10']):+.2f}, stocks q1 {float(100 * np.log(s1.loc[start, 'wpsn'] / s0.loc[start, 'wpsn'])):+.1f}%, "
              f"dollar q1 {float(100 * np.log(s1.loc[start, 'fpxr'] / s0.loc[start, 'fpxr'])):+.1f}%  ({time.time() - t0:.0f}s)", flush=True)
        for name, vars_, shift, mult, exo in EXP:
            s0, s1 = solve(exo, vars_, shift, mult, control_rff=(name == "rshort"))
            g = gdp(s1, s0)
            if name == "req":
                unit = -100 * np.log(s1.loc[start, "wpsn"] / s0.loc[start, "wpsn"]); g = -g
            else:
                unit = 100 * np.log(1 + shift) if mult else shift
            paths[(design, name)] = g / unit
            r = {"unit": unit}
            for q in (4, 8, 12):
                r[f"gdp_per_unit_q{q}"] = g[q - 1] / unit
                r[f"w_q{q}"] = g[q - 1] / unit / gY[q - 1]
            results[(design, name)] = r
            print(f"[{design}] {name:7s} unit {unit:6.3f}: weights q4/q8/q12 {r['w_q4']:+.4f} / {r['w_q8']:+.4f} / {r['w_q12']:+.4f}   rff q4 {float(s1.loc[start + 3, 'rff'] - s0.loc[start + 3, 'rff']):+.2f}  ({time.time() - t0:.0f}s)", flush=True)
        results[(design, "yardstick")] = {f"gdp_per_unit_q{q}": gY[q - 1] for q in (4, 8, 12)}
    T = pd.DataFrame(results).T
    T.index.names = ["design", "experiment"]
    T.to_csv(os.path.join(HERE, "frbus_mce.csv"), float_format="%.6f")
    pd.DataFrame({f"{d}|{e}": v for (d, e), v in paths.items()}, index=pd.Index(range(1, 41), name="quarter")).to_csv(os.path.join(HERE, "frbus_mce_paths.csv"), float_format="%.6f")
    # comparison with the old weights
    old = pd.read_csv(os.path.join(HERE, "frbus_sensitivities.csv"), index_col=0)
    ext = pd.read_csv(os.path.join(HERE, "frbus_sensitivities_ext.csv"), index_col=0)
    oldw = {"rshort": ext.loc["rshort_direct"], "rg10": old.loc["rg10"], "rme": ext.loc["rme"], "rbbbp": old.loc["rbbbp"], "req": old.loc["req"], "fpxr": old.loc["fpxr"], "phouse": ext.loc["phouse"]}
    rows = []
    for name in [e[0] for e in EXP]:
        for q in (4, 8, 12):
            rows.append(dict(experiment=name, q=q, old=float(oldw[name][f"ffr_eq_q{q}"]) * (-1 if name == "req" else 1), VAR_new_design=results[("VAR", name)][f"w_q{q}"], MCE=results[("MCE", name)][f"w_q{q}"]))
    C = pd.DataFrame(rows)
    pd.set_option("display.width", 200)
    print("\nWeights (pp of funds rate per unit): old (VAR expectations, persistent shifts, funds rate fixed) | same 4-quarter design with VAR expectations | MCE")
    print(C.round(4).to_string(index=False))
    print("\nYardstick GDP effect of the 1 pp hike: old (persistent) q4/q8/q12 -0.4525 / -0.9456 / -1.4302;  new VAR "
          + " / ".join(f"{results[('VAR', 'yardstick')][f'gdp_per_unit_q{q}']:+.4f}" for q in (4, 8, 12)) + ";  new MCE "
          + " / ".join(f"{results[('MCE', 'yardstick')][f'gdp_per_unit_q{q}']:+.4f}" for q in (4, 8, 12)))


if __name__ == "__main__":
    main()
