"""Step 6. Would a monthly proxy VAR look like the data if the estimated model were true?  (lib/simulate.py describes the design)
   python3 06_proxy_simulation.py [--sims 1000]
The data-generating process is the r*-gap model with the FCI (the paper's baseline). Each simulated sample has the data's calendar and announcement days (369 months) and is analysed with
the 2-year yield and FCI in r*-gap form and in nominal and real form (the r*-gap series plus the actual expected-inflation and r* terms): the proxy VAR with and without the FCI, and the window-impact estimator. Output: results/proxy_sim_<step>.csv (one row per sample) and results/proxy_sim_summary.csv
(data value, true value, simulated median and 5th/95th percentiles, share of simulated samples at or below the data value; for yes/no quantities the simulated frequency)."""
import os, argparse
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np, pandas as pd
import cases as CS
from lib import simulate as SM
from lib.paths import RESULTS

ap = argparse.ArgumentParser(); ap.add_argument("--sims", type=int, default=1000); a = ap.parse_args()
rows = []
dg, sims = SM.run(S=a.sims)
for step in ("rstar", "nom", "real"):
    df = sims[step]; df.round(5).to_csv(RESULTS / f"proxy_sim_{step}.csv", index=False)
    obs = {sys_: pd.read_csv(RESULTS / f"monthly_{step}_{f}_1996-01.csv") for sys_, f in (("nofci", 0), ("fci", step))}
    def dat(sys_, ident, var, h, col="r"):
        d = obs[sys_]; return float(d[(d.lags == 12) & (d.ident == ident) & (d["var"] == var) & (d.h == h)].iloc[0][col])
    def add(system, q, data, truth, sim, binary=False):
        sim = np.asarray(sim, float)
        rows.append(dict(step=step, system=system, quantity=q, data=data, truth=truth, sim_median=float(np.nanmedian(sim)), sim_p05=float(np.nanpercentile(sim, 5)), sim_p95=float(np.nanpercentile(sim, 95)),
                         share_le_data=float(np.nanmean(sim <= data)) if not binary else np.nan, sim_freq=float(np.nanmean(sim)) if binary else np.nan, binary=int(binary)))
    for sys_ in ("nofci", "fci"):
        d = obs[sys_]; F = float(d[(d.lags == 12)].F.iloc[0]); add(sys_, "F", F, np.nan, df[f"{sys_}_F"])
        for v, h in (("u", 12), ("P", 24)):
            add(sys_, f"{v}{h} estimate", dat(sys_, "P1", v, h), dg.truth[(v, h)], df[f"{sys_}_{v}{h}"])
            add(sys_, f"{v}{h} set unbounded", dat(sys_, "P1", v, h, "unbounded"), np.nan, df[f"{sys_}_{v}{h}_unb"], binary=True)
    add("nofci", "u12 estimate negative", float(dat("nofci", "P1", "u", 12) < 0), np.nan, (df["nofci_u12"] < 0).astype(float), binary=True)
    add("nofci", "u12 set bounded and below zero", float((dat("nofci", "P1", "u", 12, "hi") < 0) and not dat("nofci", "P1", "u", 12, "unbounded")), np.nan, ((df["nofci_u12_hi"] < 0) & (df["nofci_u12_unb"] == 0)).astype(float), binary=True)
    add("fci", "impact on FCI per +1 pp 2-year", float(obs["fci"][(obs["fci"].lags == 12)].impact_fci.iloc[0]), dg.truth_fci, df["fci_impact_fci"])
    for v, h in (("u", 12), ("P", 24)):
        add("we", f"{v}{h} window impact (window units)", dat("fci", "WE", v, h), dg.truth_window[(v, h)], df[f"fci_we_{v}{h}"])
S = pd.DataFrame(rows); S.to_csv(RESULTS / "proxy_sim_summary.csv", index=False, float_format="%.4f")
print(S[S.step == "rstar"].round(2).drop(columns=["step", "binary"]).to_string(index=False))

# ---------------------------------------------------------------- the paper's estimator (daily-block model) on the same simulated samples
dg, D = SM.run_daily(S=a.sims); D.round(5).to_csv(RESULTS / "daily_sim.csv", index=False)
drows = []
for form in ("rstar", "nom", "real"):
    for fci in (0, 1):
        obs = pd.read_csv(RESULTS / f"{form}_{form if fci else 0}_upi_1996-01_all_in.csv"); obs = obs[obs.lags == 12]
        sim = D[(D.form == form) & (D.fci == fci)]
        for v, h in SM.DTARGETS:
            data = float(obs[obs["var"] == v].iloc[0][f"r{h}"]); x = sim[f"{v}{h}"].values
            drows.append(dict(form=form, fci=fci, quantity=f"{v}{h}", data=data, truth=float(dg.s0[h, 0 if v == "u" else 1]), sim_median=float(np.median(x)), sim_p05=float(np.percentile(x, 5)),
                              sim_p95=float(np.percentile(x, 95)), share_le_data=float(np.mean(x <= data)), data_in_90=int(np.percentile(x, 5) <= data <= np.percentile(x, 95))))
DS = pd.DataFrame(drows); DS.to_csv(RESULTS / "daily_sim_summary.csv", index=False, float_format="%.4f")
print(DS.round(2).to_string(index=False))
