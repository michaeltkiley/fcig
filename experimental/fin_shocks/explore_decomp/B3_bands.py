"""Part B3: 90% bands for the Route 2 variance shares and historical decomposition, from Note B's own bootstrap draws of its responses (A1: model from 1973, 12 lags, 500 draws).
The draws hold position-averaged responses to 36 months, so in this step every shock (daily or monthly) is aggregated to its month and enters with the position-averaged response,
truncated at 36 months; B2 gives the exact-position, 120-month point estimates. The shocks and the data's forecast-error variances are held fixed.
   python3 B3_bands.py  -> results_route2/bands_shares.csv, results_route2/bands_hd_<step>_<fci>.npz"""
import numpy as np, pandas as pd
import lib_r2 as R
import importlib.util
spec = importlib.util.spec_from_file_location("b2", R.Path(__file__).resolve().parent / "B2_route2.py"); import sys; sys.argv = ["x"]; B2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(B2)

OUT = B2.OUT; CORE = R.Path(__file__).resolve().parent / "results_core" / "draws"; MONTHS, NM = B2.MONTHS, B2.NM
OV = pd.read_csv(OUT / "overlap.csv")

def resp(s, f):
    pi = 12 * np.diff(np.r_[0.0, s[:, 1]]); return np.column_stack([s[:, 0], pi, f])

def monthly_shocks(step, fci):
    daily = pd.read_csv(OUT / f"daily_shocks_{step}_{fci}.csv"); daily["mp"] = pd.PeriodIndex(daily.month, freq="M")
    g = lambda col, sel: daily[sel].groupby("mp")[col].sum().reindex(MONTHS).fillna(0.0).values
    c = R.run(step, fci, "avg", "1973-01", 12, "WE", "in"); em = pd.Series(c["e"], index=c["per"]).reindex(MONTHS).fillna(0.0).values
    sc = float(OV[(OV.step == step) & (OV.fci.astype(str) == str(fci))].scale.iloc[0])
    d_all = g("s", daily.s.notna()); pre = np.where(MONTHS < pd.Period("1990-05", "M"), em, 0.0)
    return {"daily_all": d_all, "daily_other": g("s", daily.ann == 0), "daily_ann": g("s", daily.ann == 1), "measured": g("ns", daily.ann == 1),
            "spliced": sc * pre + d_all, "spliced_raw": pre + d_all}

def contrib(x, r, h=None):
    rr = r.copy()
    if h is not None: rr[h:] = 0.0
    return np.column_stack([np.convolve(x, rr[:, v])[:NM] for v in range(rr.shape[1])])

if __name__ == "__main__":
    rows = []
    for step in ("rstar", "nom", "real"):
        for fci in (step, 0):
            Z = np.load(CORE / f"{step}_{fci}_upi_1973-01_all_in_L12.npz", allow_pickle=True)
            r0 = resp(Z["s0"], Z["f0"]); rd = [resp(Z["sd"][b], Z["fd"][b]) for b in range(len(Z["sd"]))]; V = r0.shape[1]; names = ["u", "pi", "pol", "idx"][:V]
            S = monthly_shocks(step, fci)
            hd = {k: np.array([contrib(x, r) for r in rd], dtype=np.float32) for k, x in S.items() if k in ("spliced", "daily_all", "measured", "daily_other")}
            np.savez_compressed(OUT / f"bands_hd_{step}_{fci}.npz", months=MONTHS.astype(str).values, point={k: contrib(S[k], r0) for k in hd}, **hd)
            for h in (12, 24, 36):
                for era in B2.ERAS:
                    fev, _ = B2.data_fev(step, fci, h, era); lo, hi = map(lambda x: pd.Period(x, "M"), B2.ERAS[era]); m = (MONTHS >= lo) & (MONTHS <= hi)
                    for src, x in S.items():
                        if era == "1974-1989" and not src.startswith("spliced"): continue
                        p = contrib(x, r0, h)[m].var(axis=0) / fev; d = np.array([contrib(x, r, h)[m].var(axis=0) / fev for r in rd])
                        for i, n in enumerate(names):
                            rows.append(dict(step=step, fci=fci, h=h, era=era, source=src, var=n, point_avgpos=p[i], p5=np.percentile(d[:, i], 5), p50=np.percentile(d[:, i], 50), p95=np.percentile(d[:, i], 95)))
            print(step, fci, flush=True)
    pd.DataFrame(rows).to_csv(OUT / "bands_shares.csv", index=False, float_format="%.5f")
