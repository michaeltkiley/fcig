"""
Convergence check for frbus_mce.py (model-consistent expectations): (1) are the yardstick and the 10-year experiment back at baseline at the end of the horizon;
(2) do the 4-, 8- and 12-quarter GDP effects change when the horizon is extended from 240 to 300 quarters. Same design as frbus_mce.py.
Usage: <venv39>/bin/python experimental/ms_fci/frbus_mce_check.py
"""
import os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import frbus_sensitivities as F
import frbus_mce as E


def main():
    F.get_package()
    from pyfrbus.frbus import Frbus
    from pyfrbus.load_data import load_data
    data0 = load_data(os.path.join(F.RAW, "data_only_package", "LONGBASE.TXT"))
    frbus = Frbus(os.path.join(F.RAW, "pyfrbus", "models", "model.xml"), mce="all")
    start = pd.Period("2040Q1")
    for NQ in (240, 300):
        end = start + NQ - 1
        data = data0.copy()
        data.loc[start:end, "dfpdbt"] = 0; data.loc[start:end, "dfpsrp"] = 1
        for v in ("dmptay", "dmptlr", "dmpex", "dmprr", "dmpalt", "dmptrsh"):
            data.loc[start:end, v] = 0
        data.loc[start:end, "dmpintay"] = 1
        base = frbus.init_trac(start, end, data)
        q4 = slice(start, start + 3)
        base["rff_traj"] = np.nan; base.loc[q4, "rff_traj"] = base.loc[q4, "rff"] + 1.0
        for name, exo, shift_vars, ctrl in (("yardstick", [], [], True), ("rg10", [v for v in E.FIXED if v not in E.PASS], ["rg5", "rg10", "rg30"], False)):
            frbus.exogenize(exo)
            d1 = base.copy()
            for v in shift_vars:
                d1.loc[q4, v] += 1.0
            s0 = frbus.solve(start, end, base.copy())
            s1 = frbus.mcontrol(start, end, d1, ["rff"], ["rff_traj"], ["rffintay_aerr"]) if ctrl else frbus.solve(start, end, d1)
            g = 100 * np.log(s1.loc[start:end, "xgdp"] / s0.loc[start:end, "xgdp"]).values
            dev = lambda v: np.abs((s1.loc[end - 7:end, v] - s0.loc[end - 7:end, v]).values).max()
            print(f"NQ={NQ} {name:9s}: GDP q4/q8/q12/q40 {g[3]:+.4f} / {g[7]:+.4f} / {g[11]:+.4f} / {g[39]:+.4f};  max |dev| last 8 quarters: GDP% {np.abs(g[-8:]).max():.5f}, "
                  f"rff {dev('rff'):.5f}, picxfe {dev('picxfe'):.5f}, rg10 {dev('rg10'):.5f};  max |GDP dev| quarters 100-140 {np.abs(g[99:140]).max():.5f}", flush=True)


if __name__ == "__main__":
    main()
