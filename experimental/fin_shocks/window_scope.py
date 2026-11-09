"""Scope of the window impact in Note B (FS-A39), in response to the risk-appetite / non-yield literature
(Boehm-Kroner 2024; Bauer-Schmeling-Schrimpf 2026; Boehm-Kim-Kroner 2026).
(1) R2 of window moves (2-year, 10-year, S&P 500, DXY, FCI) on the NS surprise, 252 events.
(2) The window ratio b_F by state (prior-day VIX quartiles, prior-month EBP quartiles) and by subperiod; 90% intervals from 1000 event resamples.
(3) Tracing the part of the window FCI move NOT explained by the surprise (residual eta_F): impact b = (0, sd(eta_F)) on the announcement day,
    no 2-year move, through the note's model (daily HAR block + monthly u, core PCE, quadratic trend), nominal and r*-gap, 3/6/12 lags,
    200 draws (events and monthly residuals resampled, regressors fixed, daily block fixed). The residual also contains non-policy news.
Usage: python3 window_scope.py [--force]. Output: window_scope.csv, window_scope.log"""
import os, sys, numpy as np, pandas as pd
OUT, LOG = "window_scope.csv", "window_scope.log"
FORCE = "--force" in sys.argv
DRAWS, LAGS, HS = 200, (3, 6, 12), (12, 24)


def slope(y, x):
    x = x - x.mean(); return float(np.sum((y - y.mean()) * x) / np.sum(x * x))


def main():
    import midas_core as MC, midas_bs as MB
    from mf_common import EV, fred
    rng = np.random.default_rng(39)
    idx0 = MC.event_index("NS"); _, _, idx0 = MC.slopes(idx0, "NS"); ev = EV.iloc[idx0].reset_index(drop=True); s = ev.ns.values
    rows, log = [], [f"Window scope. {len(ev)} announcements {ev.Date.min().date()}..{ev.Date.max().date()}.\n", "(1) R2 of window moves on the NS surprise (with constant)"]
    for nm, col in (("2-year", "UST2Y"), ("10-year", "UST10Y"), ("S&P 500", "SP500"), ("DXY", "DXY"), ("FCI", "idx_win")):
        y = ev[col].values; ok = ~np.isnan(y); r2 = np.corrcoef(y[ok], s[ok])[0, 1] ** 2
        rows.append(dict(part="r2", item=nm, value=r2)); log.append(f"   {nm:8s} R2 {r2:.2f}  (n={ok.sum()})")
    bF = lambda e: slope(e.idx_win.values, e.ns.values) / slope(e.UST2Y.values, e.ns.values)
    def ci(e):
        d = [bF(e.iloc[rng.integers(0, len(e), len(e))]) for _ in range(1000)]; return np.percentile(d, [5, 95])
    vix = fred("VIXCLS").dropna(); ebp = MC.MAC["ebp"]
    ev["vix"] = [vix[vix.index < d].iloc[-1] for d in ev.d]
    ev["ebp"] = [ebp.get(d.to_period("M") - 1, np.nan) for d in ev.d]
    log.append(f"\n(2) Window ratio b_F (FCI per pp 2-year), 90% interval from event resampling. Full sample {bF(ev):.2f}")
    for st in ("vix", "ebp"):
        q1, q3 = ev[st].quantile([0.25, 0.75])
        for lab, e in (("lowest quartile", ev[ev[st] <= q1]), ("highest quartile", ev[ev[st] >= q3])):
            lo, hi = ci(e); rows.append(dict(part="bF_state", item=f"{st} {lab}", value=bF(e), lo=lo, hi=hi, n=len(e)))
            log.append(f"   {st.upper():4s} {lab:16s} {bF(e):.2f} [{lo:.2f},{hi:.2f}] n={len(e)}")
    for lab, a, b in (("1996-2007", "1996", "2007-12-31"), ("2008-2019", "2008", "2019-12-31"), ("2020-2026", "2020", "2026-12-31"), ("2020-2023", "2020", "2023-12-31")):
        e = ev[(ev.Date >= a) & (ev.Date <= b)]; lo, hi = ci(e)
        rows.append(dict(part="bF_period", item=lab, value=bF(e), lo=lo, hi=hi, n=len(e))); log.append(f"   {lab:21s} {bF(e):.2f} [{lo:.2f},{hi:.2f}] n={len(e)}")
    def resid_sd(e):
        y, x = e.idx_win.values, e.ns.values; b = slope(y, x); r = y - y.mean() - b * (x - x.mean()); return float(r.std(ddof=2))
    sd0 = resid_sd(ev); rows.append(dict(part="eta_sd", item="sd(eta_F)", value=sd0))
    log.append(f"\n(3) Residual window FCI move: s.d. {sd0:.2f} index units (policy-news FCI move per pp 2-year: {bF(ev):.2f}). Responses to a 1-s.d. residual move, no 2-year move.")
    MC.TREND = True; pos0 = MC.positions(idx0)
    def trace(Bd, C, L, b, pos):
        m = sum(w * MB.simulate(Bd, C, 2, 2, L, b, k0, n0)[0] for k0, n0, w in pos); m[:, 1] = np.cumsum(m[:, 1]) / 12; return m
    for step in ("nom", "rstar"):
        Bd = MC.har_block(step, 1, ["u", "pi"])
        for L in LAGS:
            X, Y = MC.macro_data(step, 1, ["u", "pi"], L); C = np.linalg.lstsq(X, Y, rcond=None)[0]; fit = X @ C; res = Y - fit
            p = trace(Bd, C, L, np.array([0.0, sd0]), pos0); dr = []
            for _ in range(DRAWS):
                ib = rng.choice(idx0, len(idx0), replace=True); Cb = np.linalg.lstsq(X, fit + res[rng.integers(0, len(res), len(res))], rcond=None)[0]
                dr.append(trace(Bd, Cb, L, np.array([0.0, resid_sd(EV.iloc[ib])]), MC.positions(ib)))
            dr = np.array(dr); txt = []
            for j, v in enumerate(("u", "P")):
                for h in HS:
                    lo, hi = np.percentile(dr[:, h, j], [5, 95]); lo68, hi68 = np.percentile(dr[:, h, j], [16, 84])
                    rows.append(dict(part="trace", item=f"{step} L{L} {v} {h}", step=step, lags=L, var=v, h=h, value=p[h, j], lo=lo, hi=hi, lo68=lo68, hi68=hi68))
                    txt.append(f"{v}{h} {p[h, j]:+.2f}[{lo:+.2f},{hi:+.2f}]")
            log.append(f"   {step:5s} {L:2d} lags: " + "  ".join(txt))
    pd.DataFrame(rows).to_csv(OUT, index=False, float_format="%.4f"); open(LOG, "w").write("\n".join(log) + "\n")


PAPER = {"r2_y2": 0.80, "r2_y10": 0.32, "r2_sp": 0.31, "r2_dxy": 0.34, "r2_fci": 0.48, "eta_sd": 0.06,
         "bF_lo": 0.87, "bF_hi": 1.17, "u12_lo": 0.03, "u12_hi": 0.03, "P24_r_lo": -0.03, "P24_r_hi": -0.02}
COMCSV = "midas_core_nom-0_nom-1_rstar-0_rstar-1_trend_upiipcom.csv"
PAPER_COM = {"u12_lo": 0.16, "u12_hi": 0.25, "P24_lo": -0.62, "P24_hi": -0.30, "com24_lo": 2.68, "com24_hi": 7.23}


def star(v, lo, hi, lo68=None, hi68=None):
    return f"${v:+.2f}" + ("^{**}$" if lo > 0 or hi < 0 else ("^{\\dagger}$" if lo68 is not None and (lo68 > 0 or hi68 < 0) else "$"))


def report():
    d = pd.read_csv(OUT); g = lambda part, item: d[(d.part == part) & (d.item == item)].iloc[0]
    tr = d[d.part == "trace"]
    comp = {"r2_y2": g("r2", "2-year").value, "r2_y10": g("r2", "10-year").value, "r2_sp": g("r2", "S&P 500").value, "r2_dxy": g("r2", "DXY").value,
            "r2_fci": g("r2", "FCI").value, "eta_sd": g("eta_sd", "sd(eta_F)").value,
            "bF_lo": d[d.part == "bF_period"].value.min(), "bF_hi": d[d.part == "bF_period"].value.max(),
            "u12_lo": tr[(tr["var"] == "u") & (tr.h == 12)].value.min(), "u12_hi": tr[(tr["var"] == "u") & (tr.h == 12)].value.max(),
            "P24_r_lo": tr[(tr["var"] == "P") & (tr.h == 24) & (tr.step == "rstar")].value.min(), "P24_r_hi": tr[(tr["var"] == "P") & (tr.h == 24) & (tr.step == "rstar")].value.max()}
    c = pd.read_csv(COMCSV); cr = c[(c.rate == "rstar") & (c.fci.astype(str) == "1")]
    pick = lambda v, h: cr[cr["var"] == v][f"r{h}"]
    comp2 = {"u12_lo": pick("u", 12).min(), "u12_hi": pick("u", 12).max(), "P24_lo": pick("P", 24).min(), "P24_hi": pick("P", 24).max(),
             "com24_lo": pick("com", 24).min(), "com24_hi": pick("com", 24).max()}
    for P, C in ((PAPER, comp), (PAPER_COM, comp2)):
        for k, v in P.items(): print(f"{'OK' if abs(v - C[k]) < 0.0051 else 'MISMATCH'} {k}: paper {v:+.2f}, computed {C[k]:+.3f}")
    L = [r"\begin{tabular}{lcccccc}\toprule", r"\multicolumn{7}{l}{\textit{A. Share of each window move explained by the surprise ($R^2$)}}\\",
         " & ".join(["", "2-year", "10-year", "S\\&P 500", "DXY", "FCI", ""]) + r"\\",
         " & ".join([""] + [f"{g('r2', n).value:.2f}" for n in ("2-year", "10-year", "S&P 500", "DXY", "FCI")] + [""]) + r"\\\midrule",
         r"\multicolumn{7}{l}{\textit{B. Window FCI move per percentage point on the two-year yield, $b_F$ [90 percent interval]}}\\"]
    for part in ("bF_state", "bF_period"):
        for _, r in d[d.part == part].iterrows():
            nm = r["item"].replace("vix", "VIX,").replace("ebp", "EBP,") if part == "bF_state" else r["item"].replace("-", "--")
            L.append(f"\\multicolumn{{3}}{{l}}{{{nm} ({int(r.n)} announcements)}} & \\multicolumn{{4}}{{l}}{{{r.value:.2f} [{r.lo:.2f}, {r.hi:.2f}]}}\\\\")
    L += [r"\midrule", r"\multicolumn{7}{l}{\textit{C. Response to a one-standard-deviation window FCI move not explained by the surprise}}\\",
          r" & \multicolumn{3}{c}{Unemployment, 12 months} & \multicolumn{3}{c}{Price level, 24 months}\\", r"Step & 3 & 6 & 12 & 3 & 6 & 12\\"]
    for st, nm in (("nom", "Nominal"), ("rstar", "$r^*$-gap")):
        row = [nm]
        for v, h in (("u", 12), ("P", 24)):
            for Lg in LAGS:
                x = tr[(tr.step == st) & (tr["var"] == v) & (tr.h == h) & (tr.lags == Lg)].iloc[0]; row.append(star(x.value, x.lo, x.hi, x.lo68, x.hi68))
        L.append(" & ".join(row) + r"\\")
    L.append(r"\bottomrule\end{tabular}"); open("paper/tables/tabA_scope.tex", "w").write("\n".join(L) + "\n")
    M = [r"\begin{tabular}{ll" + "c" * 6 + "}\\toprule", r" & & \multicolumn{3}{c}{Nominal} & \multicolumn{3}{c}{$r^*$-gap}\\", r"Response & FCI & 3 & 6 & 12 & 3 & 6 & 12\\\midrule"]
    for v, h, nm in (("u", 12, "Unemployment gap, 12 months"), ("P", 24, "Core PCE price level, 24 months"), ("ip", 12, "Industrial production, 12 months"), ("com", 24, "Commodity prices, 24 months")):
        for f in ("0", "1"):
            row = [nm if f == "0" else "", "included" if f == "1" else "none"]
            for st in ("nom", "rstar"):
                for Lg in LAGS:
                    x = c[(c.rate == st) & (c.fci.astype(str) == f) & (c["var"] == v) & (c.lags == Lg)].iloc[0]
                    row.append(star(x[f"r{h}"], x[f"lo{h}"], x[f"hi{h}"], x[f"lo68_{h}"], x[f"hi68_{h}"]))
            M.append(" & ".join(row) + r"\\")
    M.append(r"\bottomrule\end{tabular}"); open("paper/tables/tabA_com.tex", "w").write("\n".join(M) + "\n")


if __name__ == "__main__":
    if os.path.exists(OUT) and not FORCE: print(f"{OUT} exists; use --force to rerun")
    else: main()
    print(open(LOG).read()); report()
