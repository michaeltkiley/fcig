"""Bridge from the market index to the FRB/US index (step 18): stage terms of F - M for one case, exact by linearity.
With x the demeaned inputs, w_M the market weights, b the FRB/US weights at 4 quarters (Phi(4)/G(4)), psi the responses and w_B = b / (b'psi):
  F - M = (w_B - w_M)'x3 [weights; per asset]  +  (b - w_B)'x3 = (b'psi - 1) w_B'x3 [scale]  +  b_policy x_policy  +  b_bbb x_bbb + b_mort x_mort [spreads]  +  b_house x_house [housing]."""
import numpy as np
from .indexes import frbus_paths, phi_at
from .agree_core import mbb

STAGES = ["w_y10", "w_eq", "w_usd", "scale", "policy", "spread_bbb", "spread_mortgage", "house"]
COLS = ["y10", "equities", "dollar", "policy", "bbb_spread", "mortgage_spread", "house"]


def frbus_b(h=4):
    P, G = frbus_paths()
    return (phi_at(P, h) / G[h]).reindex(["policy", "y10", "mortgage_spread", "bbb_spread", "equities", "dollar", "house"])


def stage_terms(Xv, bF, wM, psi):
    """Xv: T x 7 array in COLS order (demeaned). bF: Series of FRB/US weights. Returns T x 8 array of stage terms (STAGES order)."""
    b3 = np.array([bF["y10"], bF["equities"], bF["dollar"]]); x3 = Xv[:, :3]
    wB = b3 / (b3 @ psi)
    out = np.empty((len(Xv), 8))
    out[:, :3] = x3 * (wB - wM)
    out[:, 3] = x3 @ (b3 - wB)
    out[:, 4] = Xv[:, 3] * bF["policy"]; out[:, 5] = Xv[:, 4] * bF["bbb_spread"]
    out[:, 6] = Xv[:, 5] * bF["mortgage_spread"]; out[:, 7] = Xv[:, 6] * bF["house"]
    return out


def cov_shares(S, G):
    """Cov(stage, G) / Var(G) for each column of S (they sum to 1 when G = S.sum(1))."""
    Gc = G - G.mean(); return ((S - S.mean(0)).T @ Gc) / (Gc @ Gc)
