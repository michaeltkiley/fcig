"""Route 1 with Note B's own model (the lower bound): the historical contribution of the measured window surprises, sum_j r_j z_{t-j}, with r Note B's responses
(h = 0..36, monthly averages of the yield and FCI; u; inflation = 12 x change in the price level) and z the month's sum of policy news. Bands from Note B's own
bootstrap draws of the responses (model.estimate, block bootstrap, 500 draws; the measured surprises held fixed).
   python3 03_route1_draws.py
Writes results/route1_<step>_<fci>_<start>.npz (point and draws of the contributions, 1996-01 to 2026-09)."""
import numpy as np, pandas as pd
import lib_r2 as R

OUT = R.Path(__file__).resolve().parent / "results"
CASES = [("rstar", "rstar", "1996-01"), ("rstar", "rstar", "1973-01"), ("nom", 0, "1996-01"), ("rstar", 0, "1996-01")]
months = pd.period_range("1996-01", R.END, freq="M"); z = R.ZFULL.reindex(months).fillna(0.0).values

def to_r(s, f):
    """(H+1, 4): u, inflation (annual rate), yield, FCI from macro paths s (u, price level) and financial paths f."""
    pi = 12 * np.diff(np.r_[0.0, s[:, 1]])
    return np.column_stack([s[:, 0], pi, f])

for step, fci, start in CASES:
    est = next(R.M.estimate(step, fci, "u,pi", start, None, "in", "none", 500, (12,)))
    r0 = to_r(est["s0"], est["f0"]); rd = [to_r(est["sd"][b], est["fd"][b]) for b in range(len(est["sd"]))]
    h0 = R.hd(r0, z); hd = np.array([R.hd(r, z) for r in rd], dtype=np.float32)
    np.savez_compressed(OUT / f"route1_{step}_{fci}_{start[:4]}.npz", point=h0, draws=hd, months=months.astype(str).values, names=np.array(["u", "pi", "pol", "idx"][:r0.shape[1]]))
    print(step, fci, start, flush=True)
