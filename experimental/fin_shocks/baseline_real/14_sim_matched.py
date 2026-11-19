"""Step 14. The matched comparison when the estimated real model (with the FCI and the funds rate) is the true process (FS-A92; review of 19 Nov, item 1).
   python3 14_sim_matched.py [--sims 1000] [--lags 12]
The same simulated samples as step 6 (lib/simulate.py: same DGP, same seed, same draws). On each sample the main model of the paper is estimated twice, as in the data:
  with the FCI   : daily block in the 2-year yield, the FCI and the funds rate; monthly equations on lagged monthly averages of the three;
  without the FCI: daily block in the 2-year yield and the funds rate; monthly equations on lagged monthly averages of the two.
Both are started from the true window impact (2-year 1, FCI b_F, funds rate B_FF; without the FCI the FCI entry is dropped), so the window step is held fixed and only the
propagation is estimated, which is what the matched comparison varies. Responses are averaged over the data's event-position bins (as lib/model.irf). The simulated samples have
no 2020 episode, so nothing is dropped (as in step 6). Unit: +1 pp on the 2-year yield in the window.
Output: results/sim_matched_real.csv (one row per sample) and results/sim_matched_summary.csv (data estimate, true response, simulated median, 5th/95th percentiles,
share of samples at or below the data value)."""
import argparse, zlib
import numpy as np, pandas as pd
from lib import simulate as SM
from lib import model as M
from lib.daily import HAR, EV, positions
from lib.paths import RESULTS

ap = argparse.ArgumentParser(); ap.add_argument("--sims", type=int, default=1000); ap.add_argument("--lags", type=int, default=12); a = ap.parse_args(); LG = a.lags; sfx = "" if LG == 12 else f"_L{LG}"
dg = SM.DGP(L=LG); rng = np.random.default_rng(zlib.crc32(b"sim|real|real"))          # the seed of step 6: identical samples
m, fb, z, F = dg.simulate(a.sims, rng, keep_daily=True)
pos0 = positions(dg.idx0); nm = len(dg.months); K = 2
off = dg.T0 - 70; days = np.arange(70, F.shape[1])                                        # simulated days from January 1996
mon_of_day = np.searchsorted([b[0] - off for b in dg.bounds], days, side="right") - 1      # month index t of each simulated day

def fit_and_irf(Fs, ms, fbs, cols):
    """Estimate the daily block and the monthly equations on one simulated sample with the daily variables `cols`, then the response to the true window impact."""
    D = Fs[:, cols]; nd = len(cols); cs = np.vstack([np.zeros((1, nd)), np.cumsum(D, axis=0)])
    X = np.column_stack([np.ones(len(days))] + [(cs[days] - cs[days - h]) / h for h in HAR] + [ms[12 + mon_of_day - 1], ms[12 + mon_of_day]]); Y = D[days]
    Bd = np.linalg.lstsq(X, Y, rcond=None)[0]
    Xm = np.column_stack([np.ones(nm)] + [ms[12 - l:12 - l + nm] for l in range(1, LG + 1)] + [fbs[12 - l:12 - l + nm][:, cols] for l in range(1, LG + 1)])
    C = np.linalg.lstsq(Xm, ms[12:], rcond=None)[0]
    b = dg.b[cols]; mac = sum(w * M.simulate(Bd, C, K, nd, LG, b, k0, n0)[0] for k0, n0, w in pos0)
    return M.to_level(mac)

T = [("u", 12), ("u", 24), ("P", 24), ("P", 36)]; rows = []
for s in range(a.sims):
    A = fit_and_irf(F[s], m[s], fb[s], [0, 1, 2]); Cc = fit_and_irf(F[s], m[s], fb[s], [0, 2])
    r = {"sim": s}
    for v, h in T:
        j = 0 if v == "u" else 1; r[f"fci_{v}{h}"] = A[h, j]; r[f"nofci_{v}{h}"] = Cc[h, j]; r[f"diff_{v}{h}"] = A[h, j] - Cc[h, j]
    rows.append(r)
df = pd.DataFrame(rows); df.round(5).to_csv(RESULTS / f"sim_matched_real{sfx}.csv", index=False)

def dat(fci, v, h):
    d = pd.read_csv(RESULTS / f"real_{fci}_upi_1996-01_all_out.csv"); return float(d[(d.lags == LG) & (d["var"] == v)].iloc[0][f"r{h}"])
S = []
for v, h in T:
    dA, dC = dat("real", v, h), dat("0", v, h); tr = dg.truth[(v, h)] if (v, h) in dg.truth else float(dg.s0[h, 0 if v == "u" else 1])
    for sysname, data, truth in (("fci", dA, tr), ("nofci", dC, np.nan), ("diff", dA - dC, np.nan)):
        x = df[f"{sysname}_{v}{h}"].values
        S.append(dict(system=sysname, quantity=f"{v}{h}", data=data, truth=truth, sim_median=float(np.median(x)), sim_p05=float(np.percentile(x, 5)), sim_p95=float(np.percentile(x, 95)),
                      share_le_data=float(np.mean(x <= data)), share_wrong_sign=float(np.mean(x < 0) if v == "u" else np.mean(x > 0))))
S = pd.DataFrame(S); S.to_csv(RESULTS / f"sim_matched_summary{sfx}.csv", index=False, float_format="%.4f"); print(S.round(3).to_string(index=False))
