"""Route 2, all cases: shocks recovered from monthly VAR innovations, diagnostics, variance shares and historical decompositions (point estimates).
   python3 01_run.py
Writes results/summary.csv (one row per case), results/fevd.csv, results/hd_<case>.csv and results/shocks_<case>.csv for the cases with 12 lags."""
import itertools
import numpy as np, pandas as pd
import lib_r2 as R

OUT = R.Path(__file__).resolve().parent / "results"; OUT.mkdir(exist_ok=True)
SAMPLES = [("avg", "1973-01"), ("avg", "1996-01"), ("eom", "1990-01"), ("eom", "1996-01")]
ERAS = [("1974-01", "1979-09"), ("1979-10", "1984-12"), ("1985-01", "1995-12"), ("1996-01", "2007-12"), ("2008-01", "2019-12"), ("2020-01", "2026-09")]
POST = pd.Period("1996-01", "M")

def cid(c): return f"{c['step']}_{c['fci']}_{c['kind']}{c['start'][:4]}_L{c['L']}_{c['ident']}_{c['t2020']}"

def note_b_start(kind, start): return "1973-01" if (kind, start) == ("avg", "1973-01") else "1996-01"

def summarize(c):
    per, e, keep, K = c["per"], c["e"], c["keep"], c["K"]
    ok = (per >= R.Z_FIRST) & keep; z = R.ZFULL.reindex(per[ok]).fillna(0.0).values
    post = (per >= POST) & keep
    Sp = np.cov(c["U"][post].T)
    s2_up_post = 1.0 / float(c["b"] @ np.linalg.inv(Sp) @ c["b"])
    if c["ident"] == "WE2":
        Si = np.linalg.inv(Sp); s2_up_post = 1.0 / float(c["b"] @ Si @ c["b"] + c["b1"] @ Si @ c["b1"])
    s2_lo = float((R.ZFULL.reindex(per[post]).fillna(0.0) ** 2).mean())
    r2_0, r2_lead, p_lead, _ = R.lead_lag_test(c["U"], per, keep, 6)
    p_lag = R.lead_lag_test(c["U"], per, keep, 6, lags=True)[2]
    nb = R.note_b(c["step"], c["fci"], note_b_start(c["kind"], c["start"]), c["L"])["s0"]
    P = np.cumsum(c["r"][:, 1]) / 12
    row = dict(case=cid(c), step=c["step"], fci=c["fci"], kind=c["kind"], start=c["start"], L=c["L"], ident=c["ident"], t2020=c["t2020"],
               first=str(per[0]), n=int(keep.sum()), F=R.first_stage_F(c["U"], per, keep),
               **{f"b_{v}": c["b"][i] for i, v in enumerate(c["names"])},
               sd_e_full=float(np.sqrt(c["s2"])), sd_e_post_inv=float(np.sqrt(s2_up_post)), sd_z=float(np.sqrt(s2_lo)),
               var_ratio=float(s2_up_post / s2_lo),
               corr_e_z=float(np.corrcoef(e[ok], z)[0, 1]), slope_z_on_e=float(np.polyfit(e[ok], z, 1)[0]),
               r2_z_u=r2_0, r2_z_u_leads=r2_lead, p_leads=p_lead, p_lags=p_lag,
               **{f"var_u{h}": c["r"][h, 0] for h in (12, 24, 36)}, **{f"var_P{h}": P[h] for h in (12, 24, 36)},
               **{f"nb_u{h}": nb[h, 0] for h in (12, 24, 36)}, **{f"nb_P{h}": nb[h, 1] for h in (12, 24, 36)},
               **{f"var_pol{h}": c["r"][h, 2] for h in (0, 1, 6, 12)})
    for a, b in ERAS:
        m = (per >= pd.Period(a, "M")) & (per <= pd.Period(b, "M")) & keep
        row[f"sd_e_{a[:4]}"] = float(e[m].std()) if m.sum() > 6 else np.nan
    fe = []
    for lab, S, s2 in (("full_upper", c["S"], c["s2"]), ("post_upper", Sp, s2_up_post), ("post_lower", Sp, s2_lo)):
        f = R.fevd(c["T"], S, c["r"], s2)
        for h, v in f.items():
            fe.append(dict(case=cid(c), step=c["step"], fci=c["fci"], kind=c["kind"], start=c["start"], L=c["L"], ident=c["ident"], t2020=c["t2020"], bound=lab, h=h,
                           **{n: v[i] for i, n in enumerate(c["names"])}))
    return row, fe

def note_b_r(c):
    """Note B's responses (h = 0..36) as a matrix in the VAR's variables, for Route 1 with Note B's own model."""
    nb = R.note_b(c["step"], c["fci"], note_b_start(c["kind"], c["start"]), c["L"])
    return np.array([R.path_vector(c["step"], c["fci"], c["kind"], h, note_b_start(c["kind"], c["start"]), c["L"])[:c["K"]] for h in range(nb["s0"].shape[0])])

def series(c):
    per, K = c["per"], c["K"]
    z = R.ZFULL.reindex(per).fillna(0.0).values
    h2 = R.hd(c["r"], c["e"]); h1 = R.hd(c["r"], z); hnb = R.hd(note_b_r(c), z); sto = R.all_shocks(c["T"], c["U"], c["keep"])
    rows = []
    for i, n in enumerate(c["names"]):
        rows.append(pd.DataFrame(dict(month=per.astype(str), var=n, actual=c["Y"][:, i], stochastic=sto[:, i], route2=h2[:, i], route1_var=h1[:, i], route1_noteb=hnb[:, i])))
    pd.concat(rows).to_csv(OUT / f"hd_{cid(c)}.csv", index=False, float_format="%.5f")
    pd.DataFrame(dict(month=per.astype(str), e=c["e"], z=z, keep=c["keep"].astype(int))).to_csv(OUT / f"shocks_{cid(c)}.csv", index=False, float_format="%.5f")

if __name__ == "__main__":
    rows, fes = [], []
    for step, wf, (kind, start), L in itertools.product(("nom", "real", "rstar"), (False, True), SAMPLES, (3, 6, 12)):
        fci = step if wf else 0
        idents = ["WE", "P1"] + (["WE2"] if kind == "avg" else [])
        for ident in idents:
            for t2020 in (("in", "dummy") if L == 12 else ("in",)):
                c = R.run(step, fci, kind, start, L, ident, t2020)
                r, fe = summarize(c); rows.append(r); fes += fe
                if L == 12: series(c)
        print(step, fci, kind, start, L, flush=True)
    pd.DataFrame(rows).to_csv(OUT / "summary.csv", index=False, float_format="%.4f")
    pd.DataFrame(fes).to_csv(OUT / "fevd.csv", index=False, float_format="%.4f")
