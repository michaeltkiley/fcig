"""ARCHIVED (extended simulation, not used in the paper): needs baseline/ on PYTHONPATH and its cases.py; run from this folder with
   PYTHONPATH=../../baseline python3 run_simulation_extended.py --sims 1000
Step 6 of the baseline before trimming. Would the monthly estimators, and the paper's own model, look like the data if the estimated r*-gap model were the true process?  (lib/simulate.py describes the design)
   python3 06_proxy_simulation.py [--sims 1000] [--jobs 4]
The data-generating process is the r*-gap model with the FCI. Each simulated sample has the data's calendar and announcement days (369 months) and is analysed with the 2-year yield and FCI
in r*-gap form and in nominal and real form (the r*-gap series plus the actual expected-inflation and r* terms): (i) the monthly proxy VAR with and without the FCI and the window-impact monthly
estimator, (ii) the full daily-block model. Two resampling schemes for the innovations: independent draws, and blocks (12 months for the monthly residuals, 66 days for the daily residuals),
which keep serial dependence and volatility clustering. Output (suffix _block for the block scheme):
  results/proxy_sim_<form>[_block].csv, daily_sim[_block].csv                  one row per sample
  results/proxy_sim_summary[_block].csv                                         first-stage F, set boundedness, signs, FCI impact: data, true, simulated median and 5th/95th percentile
  results/monthly_irf_sim_summary[_block].csv, daily_sim_summary[_block].csv    responses of u and the price level at 12 and 24 months: data, true, simulated median, 5th/95th, share <= data"""
import os, argparse
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np, pandas as pd
import cases as CS
import simulate_extended as SM
from pathlib import Path
from lib.paths import RESULTS as BASE_RESULTS      # the baseline results (data estimates) are read from baseline/results
RESULTS = Path(__file__).resolve().parent / "results"   # outputs of this archived run

ap = argparse.ArgumentParser(); ap.add_argument("--sims", type=int, default=1000); ap.add_argument("--jobs", type=int, default=4); a = ap.parse_args()
FORMS = ("rstar", "nom", "real")
def stat_row(**kw):
    sim = np.asarray(kw.pop("sim"), float); data = kw["data"]; binary = kw.pop("binary", False)
    return dict(**kw, sim_median=float(np.nanmedian(sim)), sim_p05=float(np.nanpercentile(sim, 5)), sim_p95=float(np.nanpercentile(sim, 95)),
                share_le_data=np.nan if binary else float(np.nanmean(sim <= data)), sim_freq=float(np.nanmean(sim)) if binary else np.nan, binary=int(binary),
                data_in_90=int(np.nanpercentile(sim, 5) <= data <= np.nanpercentile(sim, 95)) if not binary else -1)

for block, suf in ((None, ""), ((12, 66), "_block")):
    dg, M, D = SM.run_sims(S=a.sims, block=block, jobs=a.jobs)
    D.round(5).to_csv(RESULTS / f"daily_sim{suf}.csv", index=False)
    diag, irf, dly = [], [], []
    for step in FORMS:
        df = M[M.form == step]; df.drop(columns="form").round(5).to_csv(RESULTS / f"proxy_sim_{step}{suf}.csv", index=False)
        obs = {s_: pd.read_csv(BASE_RESULTS / f"monthly_{step}_{f}_1996-01.csv") for s_, f in (("nofci", 0), ("fci", step))}
        def dat(s_, ident, var, h, col="r"):
            d = obs[s_]; return float(d[(d.lags == 12) & (d.ident == ident) & (d["var"] == var) & (d.h == h)].iloc[0][col])
        def add(system, q, data, truth, sim, binary=False): diag.append(stat_row(step=step, system=system, quantity=q, data=data, truth=truth, sim=sim, binary=binary))
        for s_ in ("nofci", "fci"):
            add(s_, "F", float(obs[s_][obs[s_].lags == 12].F.iloc[0]), np.nan, df[f"{s_}_F"])
            for v, h in (("u", 12), ("P", 24)):
                add(s_, f"{v}{h} estimate", dat(s_, "P1", v, h), dg.truth[(v, h)], df[f"{s_}_{v}{h}"])
                add(s_, f"{v}{h} set unbounded", dat(s_, "P1", v, h, "unbounded"), np.nan, df[f"{s_}_{v}{h}_unb"], binary=True)
        add("nofci", "u12 estimate negative", float(dat("nofci", "P1", "u", 12) < 0), np.nan, (df["nofci_u12"] < 0).astype(float), binary=True)
        add("nofci", "u12 set bounded and below zero", float((dat("nofci", "P1", "u", 12, "hi") < 0) and not dat("nofci", "P1", "u", 12, "unbounded")), np.nan,
            ((df["nofci_u12_hi"] < 0) & (df["nofci_u12_unb"] == 0)).astype(float), binary=True)
        add("fci", "impact on FCI per +1 pp 2-year", float(obs["fci"][obs["fci"].lags == 12].impact_fci.iloc[0]), dg.truth_fci, df["fci_impact_fci"])
        for v, h in (("u", 12), ("P", 24)): add("we", f"{v}{h} window impact (window units)", dat("fci", "WE", v, h), dg.truth_window[(v, h)], df[f"fci_we_{v}{h}"])
        # impulse-response-style table of the monthly estimators: proxy VAR (monthly-average units), window impact (window units)
        for system, ident, col, truth in (("proxy_fci", "P1", "fci", dg.truth), ("proxy_nofci", "P1", "nofci", dg.truth), ("window", "WE", "fci_we", dg.truth_window)):
            src = "fci" if system != "proxy_nofci" else "nofci"
            for v, h in SM.DTARGETS:
                x = df[f"fci_we_{v}{h}"] if system == "window" else df[f"{col}_{v}{h}"]
                irf.append(stat_row(form=step, system=system, quantity=f"{v}{h}", data=dat(src, ident, v, h), truth=float(truth[(v, h)]), sim=x))
        for fci in (0, 1):
            obs_d = pd.read_csv(BASE_RESULTS / f"{step}_{step if fci else 0}_upi_1996-01_all_in.csv"); obs_d = obs_d[obs_d.lags == 12]; sim = D[(D.form == step) & (D.fci == fci)]
            for v, h in SM.DTARGETS:
                dly.append(stat_row(form=step, fci=fci, quantity=f"{v}{h}", data=float(obs_d[obs_d["var"] == v].iloc[0][f"r{h}"]), truth=float(dg.s0[h, 0 if v == "u" else 1]), sim=sim[f"{v}{h}"].values))
    pd.DataFrame(diag).to_csv(RESULTS / f"proxy_sim_summary{suf}.csv", index=False, float_format="%.4f")
    pd.DataFrame(irf).to_csv(RESULTS / f"monthly_irf_sim_summary{suf}.csv", index=False, float_format="%.4f")
    pd.DataFrame(dly).to_csv(RESULTS / f"daily_sim_summary{suf}.csv", index=False, float_format="%.4f")
    print(f"== scheme: {'independent' if not block else 'blocks ' + str(block)}\n", pd.DataFrame(dly).round(2).drop(columns=["binary", "sim_freq"]).to_string(index=False))
