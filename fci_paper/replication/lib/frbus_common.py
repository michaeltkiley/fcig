"""Shared FRB/US set-up for steps 00 and 22_policy_shock (same as experimental/ms_fci/frbus_paths.py): steady-state baseline from 2040Q1, fiscal settings as in the Board's demos,
VAR expectations, and the exogenized lists of the partial experiments."""
import re
import numpy as np, pandas as pd
from .frbus_env import LONGBASE, MODEL, ensure_package
ensure_package()
from pyfrbus.frbus import Frbus
from pyfrbus.load_data import load_data

START = pd.Period("2040Q1")
CURVE = ["rtb", "rg5", "rg10", "rg30"]; PASS = ["rme", "rcar"]; OTHER = ["rbbbp", "req", "wpsn", "fpxr", "poil"]
FIXED = ["rff"] + CURVE + PASS + OTHER


class Model:
    def __init__(self, hsolve=32):
        self.data = load_data(str(LONGBASE)); self.frbus = Frbus(str(MODEL))
        self.start = START; self.end = START + hsolve + 7
        self.data.loc[self.start:self.end, "dfpdbt"] = 0
        self.data.loc[self.start:self.end, "dfpsrp"] = 1
        self.base = self.frbus.init_trac(self.start, self.end, self.data)
        xml = open(MODEL).read()
        self.Zv = [v for v in re.findall(r"<variable>\s*<name>([a-z0-9_]+)</name>", xml) if v.startswith("z") and v in self.base.columns]

    def run(self, exo, vars_, shift, mult=False, temporary=False):
        self.frbus.exogenize(list(exo))
        d0 = self.base.copy(); d1 = self.base.copy(); last = self.start if temporary else self.end
        for v in vars_:
            d1.loc[self.start:last, v] = d1.loc[self.start:last, v] * (1 + shift) if mult else d1.loc[self.start:last, v] + shift
        return self.frbus.solve(self.start, self.end, d0), self.frbus.solve(self.start, self.end, d1)

    def gdp(self, s1, s0, H=32):
        return 100 * np.log(s1.loc[self.start:self.start + H - 1, "xgdp"] / s0.loc[self.start:self.start + H - 1, "xgdp"]).values
