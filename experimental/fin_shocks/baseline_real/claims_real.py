"""Claims of the results of baseline_real (FS-A85), written from the new results on 18 Nov 2026 for the sign-off. Called by 07_report.py (check_claims). The text written in Phase 2
quotes only claims listed here; a claim added to the text is added here first. Each claim is one plain statement; check() returns the claims that no longer hold."""
import numpy as np, pandas as pd
import cases as CS
from lib.paths import RESULTS

H3 = (12, 24, 36)

def check(R, MON, SIM, B96, ROB):
    bad = []; chk = lambda name, ok: None if ok else bad.append(name)
    def g(f, fk, v, h, st="1996-01", **kw):
        c = dict(form=f, fci=0 if fk == "no" else f, **{**B96, "start": st, **kw}); d = R[CS.case_id(c)]; r = d[(d.lags == 12) & (d["var"] == v)].iloc[0]
        return r[f"r{h}"], r[f"lo{h}"] * r[f"hi{h}"] > 0, r[f"lo95_{h}"] * r[f"hi95_{h}"] > 0
    est = lambda *a, **k: g(*a, **k)[0]; sig = lambda *a, **k: g(*a, **k)[1]; sig5 = lambda *a, **k: g(*a, **k)[2]; T73 = "1973-01"; V = ("nom", "real")

    # ---- baselines from 1996
    chk("1996, rates alone (both versions): unemployment falls significantly (5%) at 12 and 24 m; the price level is not significant at 12, 24 or 36 m",
        all(est(f, "no", "u", h) < 0 and sig5(f, "no", "u", h) for f in V for h in (12, 24)) and not any(sig(f, "no", "P", h) for f in V for h in H3))
    chk("1996, real with the FCI: unemployment rises significantly (5%) at 12 and 24 m; the price level falls significantly at 24 m (5%) and 36 m (10%)",
        all(est("real", "yes", "u", h) > 0 and sig5("real", "yes", "u", h) for h in (12, 24)) and sig5("real", "yes", "P", 24) and est("real", "yes", "P", 36) < 0 and sig("real", "yes", "P", 36))
    chk("1996, nominal with the FCI: unemployment rises significantly at 12 m (10%) and 24 m (5%); the price level falls significantly at 24 m (10%), not at 36 m",
        sig("nom", "yes", "u", 12) and sig5("nom", "yes", "u", 24) and est("nom", "yes", "P", 24) < 0 and sig("nom", "yes", "P", 24) and not sig("nom", "yes", "P", 36))
    chk("1996: adding the FCI turns the unemployment response from a fall to a rise and deepens the price fall at 24 m, in both versions",
        all(est(f, "no", "u", 24) < 0 < est(f, "yes", "u", 24) and est(f, "yes", "P", 24) < est(f, "no", "P", 24) for f in V))
    chk("1996, with the FCI: the nominal and real responses at 24 m are within 0.05 of each other (u and P)", all(abs(est("nom", "yes", v, 24) - est("real", "yes", v, 24)) < 0.05 for v in ("u", "P")))
    # ---- baselines from 1973
    chk("1973, real with the FCI: unemployment rises significantly at 12 m (5%); the price level falls significantly at 12, 24, 36 m (5% at 24 and 36)",
        est("real", "yes", "u", 12, T73) > 0 and sig5("real", "yes", "u", 12, T73) and all(est("real", "yes", "P", h, T73) < 0 and sig("real", "yes", "P", h, T73) for h in H3) and all(sig5("real", "yes", "P", h, T73) for h in (24, 36)))
    chk("1973, real rates alone: the price level falls significantly at 24 and 36 m and unemployment does not fall", all(sig5("real", "no", "P", h, T73) and est("real", "no", "P", h, T73) < 0 for h in (24, 36)) and all(est("real", "no", "u", h, T73) > 0 for h in H3))
    chk("1973, nominal with the FCI: no response is significant", not any(sig("nom", "yes", v, h, T73) for v in ("u", "P") for h in H3))
    chk("1973, nominal rates alone: the price level is not significant; unemployment is significant only at 36 m, with the conventional sign", not any(sig("nom", "no", "P", h, T73) for h in H3) and sig("nom", "no", "u", 36, T73) and est("nom", "no", "u", 36, T73) > 0 and not any(sig("nom", "no", "u", h, T73) for h in (12, 24)))
    chk("1973: adding the FCI raises the 12-month unemployment response in both versions", all(est(f, "yes", "u", 12, T73) > est(f, "no", "u", 12, T73) for f in V))

    # ---- standard methods (no funds rate, as in the literature)
    LS = pd.read_csv(RESULTS / "lit_style.csv").query("lags == 12"); ls = lambda c, v, h: LS[(LS.case == c) & (LS["var"] == v) & (LS.h == h)].iloc[0]; lsig = lambda c, v, h: ls(c, v, h).lo * ls(c, v, h).hi > 0
    for c in ("chol_2y_1996", "proxy_2y_1996"):
        chk(f"{c}: unemployment falls significantly at 12 and 24 m; the price level is not significant", all(ls(c, "u", h).point < 0 and lsig(c, "u", h) for h in (12, 24)) and not any(lsig(c, "P", h) for h in H3))

    # ---- monthly VARs with the funds rate
    mo = lambda f, fk, i, v, h, st="1996-01": (lambda m: m[(m.lags == 12) & (m.ident == i) & (m["var"] == v) & (m.h == h)].iloc[0])(MON[CS.monthly_id(dict(step=f, fci=0 if fk == "no" else f, start=st))])
    chk("monthly proxy VAR with the FCI: first-stage F below 2 from both starts and both versions", all(mo(f, "yes", "P1", "u", 12, st).F < 2 for f in V for st in ("1996-01", T73)))
    chk("monthly proxy VAR without the FCI from 1996: unemployment falls significantly at 12 m in both versions", all(mo(f, "no", "P1", "u", 12).r < 0 and not mo(f, "no", "P1", "u", 12).unbounded and mo(f, "no", "P1", "u", 12).hi < 0 for f in V))
    chk("window-impact monthly VAR, real with the FCI: unemployment up and the price level down at 12 and 24 m from both starts; significant from 1973, not from 1996",
        all(mo("real", "yes", "WE", "u", h, st).r > 0 and mo("real", "yes", "WE", "P", h, st).r < 0 for h in (12, 24) for st in ("1996-01", T73))
        and all(mo("real", "yes", "WE", v, h, T73).lo * mo("real", "yes", "WE", v, h, T73).hi > 0 for v in ("u", "P") for h in (12, 24)) and not any(mo("real", "yes", "WE", v, h).lo * mo("real", "yes", "WE", v, h).hi > 0 for v in ("u", "P") for h in (12, 24)))
    chk("window-impact monthly VAR, real with the FCI: from 1996 about half the main model's responses (u 12 m and P 24 m); from 1973 the price fall is smaller than the model's and unemployment within 0.05",
        all(0.35 < mo("real", "yes", "WE", v, h).r / est("real", "yes", v, h) < 0.65 for v, h in (("u", 12), ("P", 24))) and abs(mo("real", "yes", "WE", "P", 24, T73).r) < abs(est("real", "yes", "P", 24, T73)) and abs(mo("real", "yes", "WE", "u", 12, T73).r - est("real", "yes", "u", 12, T73)) < 0.05)

    # ---- simulation (the real model as the true process)
    sm = lambda s, q: SIM[(SIM.system == s) & (SIM.quantity == q)].iloc[0]
    chk("simulation: the proxy VAR with the FCI is centred below the truth and its 90% range of u at 12 m covers zero and exceeds 1 pp", sm("proxy_fci", "u12").sim_median < sm("proxy_fci", "u12").truth and sm("proxy_fci", "u12").sim_p05 < 0 < sm("proxy_fci", "u12").sim_p95 and sm("proxy_fci", "u12").sim_p95 - sm("proxy_fci", "u12").sim_p05 > 1)
    chk("simulation: without the FCI the proxy VAR's median unemployment response has the wrong sign", sm("proxy_nofci", "u12").sim_median < 0 < sm("proxy_nofci", "u12").truth)
    chk("simulation: the window-impact range is narrower than the proxy VAR's and below the truth at the median (temporal aggregation)", sm("window", "u12").sim_p95 - sm("window", "u12").sim_p05 < sm("proxy_fci", "u12").sim_p95 - sm("proxy_fci", "u12").sim_p05 and sm("window", "u12").sim_median < sm("window", "u12").truth)
    # step 14 (FS-A92): the main model with and without the FCI on the same simulated samples
    chk("simulation, main model: with the FCI the median responses are within 0.1 of the truth (u 12 and 24 m, P 24 m)", all(abs(sm("main_fci", q).sim_median - sm("main_fci", q).truth) < 0.1 for q in ("u12", "u24", "P24")))
    chk("simulation, main model: without the FCI the median unemployment response has the wrong sign at 12 and 24 m, in more than two thirds of the samples", all(sm("main_nofci", q).sim_median < 0 and sm("main_nofci", q).share_wrong_sign > 2 / 3 for q in ("u12", "u24")))
    chk("simulation, main model: the difference (with less without the FCI) in unemployment is positive at 24 m in at least 99 percent of the samples, and the price-level difference negative in at least 90 percent", sm("main_diff", "u24").share_wrong_sign <= 0.01 and sm("main_diff", "P24").share_wrong_sign <= 0.10)
    chk("simulation, main model: the data's differences (u 24 m, P 24 m) lie inside the simulated 5-95 ranges, the unemployment difference above the median", all(sm("main_diff", q).sim_p05 <= sm("main_diff", q).data <= sm("main_diff", q).sim_p95 for q in ("u24", "P24")) and sm("main_diff", "u24").data > sm("main_diff", "u24").sim_median)
    chk("simulation: the data values lie inside the simulated 5-95 ranges", all(sm(a, b).sim_p05 <= sm(a, b).data <= sm(a, b).sim_p95 for a, b in (("proxy_fci", "F"), ("proxy_fci", "u12"), ("proxy_nofci", "u12"), ("window", "u12"))))

    # ---- the sacrifice ratio
    TT = pd.read_csv(RESULTS / "tradeoff.csv"); TT["fci"] = TT.fci.astype(str)
    k = lambda f, st, H: TT[(TT.form == f) & (TT.fci == f) & (TT.macro == "u,pi") & (TT.start == st) & TT.end.isna() & (TT.t2020 == "out") & (TT.trend == "none") & (TT["shock"] == "ns") & (TT.lags == 12) & (TT.H == H) & (TT["ext"].isna() if "ext" in TT else True)].iloc[0]
    chk("multiplier, real with the FCI: the 90% set is bounded and negative at 24 and 36 m from both starts", all(np.isfinite(k("real", st, H).k_lo) and k("real", st, H).k_hi < 0 for st in ("1996-01", T73) for H in (24, 36)))
    chk("multiplier, real with the FCI from 1996 at 24 m: sacrifice ratio between 1 and 1.4", 1 < abs(1 / k("real", "1996-01", 24).kappa) < 1.4)
    chk("multiplier, nominal from 1973: the set is unbounded (cumulative unemployment interval includes zero)", not np.isfinite(k("nom", T73, 24).k_lo))

    # ---- robustness (12 months; ROB from 07_report.rob_summary)
    tests = ("t2020", "ebpip", "bs", "L6", "noff", "s85")
    chk("robustness, real with the FCI: in every test and both samples unemployment rises and the price level falls at 12 m", all(ROB[("real", t, sx, "u")][0] > 0 and ROB[("real", t, sx, "P")][0] < 0 for t in tests for sx in ("", "73") if ("real", t, sx, "u") in ROB))
    chk("robustness, real with the FCI: the price level falls significantly at 12 m in every test from 1973, and from 1996 in every test except 6 lags and the 1985 start",
        all(ROB[("real", t, "73", "P")][1] for t in tests if ("real", t, "73", "P") in ROB) and all(ROB[("real", t, "", "P")][1] == (t not in ("L6", "s85")) for t in tests))
    chk("robustness, real with the FCI: unemployment at 12 m is significant except with 2020 left in (both samples), 6 lags from 1973 and the 1985 start",
        all(ROB[("real", t, sx, "u")][1] == ((t, sx) not in {("t2020", ""), ("t2020", "73"), ("L6", "73"), ("s85", "")}) for t in tests for sx in ("", "73") if ("real", t, sx, "u") in ROB))
    chk("robustness: the 1985 start is the weakest test (smallest responses of the real version at 12 m)", all(abs(ROB[("real", "s85", "", v)][0]) <= min(abs(ROB[("real", t, sx, v)][0]) for t in tests if t != "s85" for sx in ("", "73") if ("real", t, sx, v) in ROB and t != "t2020") for v in ("P",)))
    chk("robustness: Bauer-Swanson responses at least as large as the baseline's (real, both samples)", all(abs(ROB[("real", "bs", sx, v)][0]) >= abs(ROB[("real", "base", sx, v)][0]) - 0.005 for sx in ("", "73") for v in ("u", "P")))

    # ---- the final section
    chk("final section: the r*-gap step with the FCI has larger responses than the real baseline at 24 m (u and P), both samples",
        all(est("rstar", "yes", "u", 24, st) > est("real", "yes", "u", 24, st) and est("rstar", "yes", "P", 24, st) < est("real", "yes", "P", 24, st) for st in ("1996-01", T73)))
    chk("final section: with the spline trend, from 1996 no response with the FCI is significant at 24 m; from 1973 the real version's are (u and P)",
        not any(sig(f, "yes", v, 24, trend="spline") for f in V for v in ("u", "P")) and all(sig("real", "yes", v, 24, T73, trend="spline") for v in ("u", "P")))

    # ---- decomposition (Section 3.5)
    S = pd.read_csv(RESULTS / "decomp_shares.csv"); S["fci"] = S.fci.astype(str)
    sh = lambda m, era, src, v: float(S[(S["mode"] == "infer") & (S.fci == "real") & (S.model == m) & (S.h == 24) & (S.era == era) & (S.source == src)][v].iloc[0])
    chk("decomposition: measured surprises explain under 1 percent of the 24-month variance of unemployment and inflation (both models)", all(sh(m, "1996-2026", "measured", v) < 0.01 for m in (1996, 1973) for v in ("u", "pi")))
    chk("decomposition: policy-direction shocks 1990-2026 explain 3 to 12 percent of unemployment and 4 to 6 percent of inflation at 24 m", all(0.03 <= sh(m, "1990-2026", "daily_all", "u") < 0.12 and 0.04 <= sh(m, "1990-2026", "daily_all", "pi") < 0.06 for m in (1996, 1973)))

    # ---- further statements of paper/mp_transmission_real.tex (Phase 2)
    chk("1996: adding the FCI shifts u24 by 0.6 to 0.8 pp and P24 by -0.35 to -0.5 percent in both versions (text: about 0.7 and 0.4)",
        all(0.6 < est(f, "yes", "u", 24) - est(f, "no", "u", 24) < 0.8 and -0.5 < est(f, "yes", "P", 24) - est(f, "no", "P", 24) < -0.35 for f in V))
    chk("1973: real rates alone lower the price level at 24 m by at least as much as the 1996 baseline with the FCI, minus 0.05", est("real", "no", "P", 24, T73) <= est("real", "yes", "P", 24) + 0.05)
    chk("1973, real: adding the FCI moves the 24-month price fall by less than 0.1 (text: leaves it about where it is)", abs(est("real", "yes", "P", 24, T73) - est("real", "no", "P", 24, T73)) < 0.1)
    chk("1973, with the FCI: the nominal price fall at 24 m is less than half the real one", abs(est("nom", "yes", "P", 24, T73)) < 0.5 * abs(est("real", "yes", "P", 24, T73)))
    chk("multiplier, nominal from 1996 at 24 m: bounded set, point within 0.25 of the real one", np.isfinite(k("nom", "1996-01", 24).k_lo) and abs(k("nom", "1996-01", 24).kappa - k("real", "1996-01", 24).kappa) < 0.25)
    chk("decomposition: policy-direction shocks since 1990 account for 20 to 35 percent of the two-year yield's 24-month variance (both models)", all(0.2 < sh(m, "1990-2026", "daily_all", "pol") < 0.35 for m in (1996, 1973)))
    chk("decomposition: policy-direction shocks explain about 5 percent of inflation (4 to 6 percent, both models, since 1990)", all(0.04 <= sh(m, "1990-2026", "daily_all", "pi") < 0.06 for m in (1996, 1973)))
    PER = pd.read_csv(RESULTS / "persistence.csv"); pw = PER[(PER.base == "window plus later closes") & (~PER.controls)].set_index(["series", "measure"]); pp_ = PER[(PER.base == "pre-event close")].set_index(["series", "measure"])
    chk("persistence: for the yield the model lies inside the direct interval at 5, 22, 66 days and the first-month average", all(pw.loc[("y", m)].lo <= pw.loc[("y", m)].model <= pw.loc[("y", m)].hi for m in ("h5", "h22", "h66", "avg22")))
    chk("persistence: for the FCI the model lies below the direct interval at 5 days and for the first-month average, inside at 22 and 66 days; the 66-day interval contains a reversal and more than twice the model",
        pw.loc[("f", "h5")].model < pw.loc[("f", "h5")].lo and pw.loc[("f", "avg22")].model < pw.loc[("f", "avg22")].lo and all(pw.loc[("f", m)].lo <= pw.loc[("f", m)].model <= pw.loc[("f", m)].hi for m in ("h22", "h66")) and pw.loc[("f", "h66")].lo < 0 and pw.loc[("f", "h66")].hi > 2 * pw.loc[("f", "h66")].model)
    chk("persistence: from the close before the announcement the model lies inside the FCI intervals at 5 days and for the first-month average", all(pp_.loc[("f", m)].lo <= pp_.loc[("f", m)].model <= pp_.loc[("f", m)].hi for m in ("h5", "avg22")))
    chk("timing: with rates alone neither model raises unemployment at 24 m; adding the FCI raises it in both versions and both models", all(pd.read_csv(RESULTS / f"monthly_{f}_0_1996-01.csv").query("lags == 12 and ident == 'WE' and var == 'u' and h == 24").r.iloc[0] < 0 and est(f, "no", "u", 24) < 0 for f in V)
        and all(pd.read_csv(RESULTS / f"monthly_{f}_{f}_1996-01.csv").query("lags == 12 and ident == 'WE' and var == 'u' and h == 24").r.iloc[0] > pd.read_csv(RESULTS / f"monthly_{f}_0_1996-01.csv").query("lags == 12 and ident == 'WE' and var == 'u' and h == 24").r.iloc[0] for f in V))
    cr = lambda c: R[CS.case_id(c)].query("lags == 12").set_index("var")
    cE, cE0, cA = (dict(form="real", fci="real", **{**B96, "macro": "u,pi,ebp,ip"}), dict(form="real", fci=0, **{**B96, "macro": "u,pi,ebp,ip"}), dict(form="real", fci="baa", **B96))
    chk("credit: with the EBP (and IP) or the Baa spread, unemployment rises and the price level falls significantly at 24 m; with Baa the u interval includes zero and the price fall is larger than the baseline's",
        all(cr(c).loc["u"].r24 > 0 and cr(c).loc["P"].r24 < 0 and cr(c).loc["P"].lo24 * cr(c).loc["P"].hi24 > 0 for c in (cE, cA)) and cr(cA).loc["u"].lo24 < 0 and cr(cA).loc["P"].r24 < est("real", "yes", "P", 24))
    chk("credit: without the FCI, adding the EBP (and IP) turns the 24-month unemployment response positive", cr(cE0).loc["u"].r24 > 0 > est("real", "no", "u", 24))
    chk("robustness 1996, real: u at 12 m lowest with the 1985 start and highest with Bauer-Swanson", min(ROB[("real", t, "", "u")][0] for t in tests) == ROB[("real", "s85", "", "u")][0] and max(ROB[("real", t, "", "u")][0] for t in tests) == ROB[("real", "bs", "", "u")][0])
    chk("robustness, real without the funds rate: smaller responses from 1996 (u and P at 12 m)", all(abs(ROB[("real", "noff", "", v)][0]) < abs(ROB[("real", "base", "", v)][0]) for v in ("u", "P")))
    chk("robustness, real with 2020 left in: unemployment at 12 m below the baseline's in both samples, the price level within 0.1", all(ROB[("real", "t2020", sx, "u")][0] < ROB[("real", "base", sx, "u")][0] and abs(ROB[("real", "t2020", sx, "P")][0] - ROB[("real", "base", sx, "P")][0]) < 0.1 for sx in ("", "73")))
    chk("sample ending 2019, real with the FCI: from 1996 the price level does not fall at 24 m and unemployment rises; from 1973 the price level falls significantly", est("real", "yes", "P", 24, end=2019, t2020="in") > 0 and est("real", "yes", "u", 24, end=2019, t2020="in") > 0 and sig("real", "yes", "P", 24, T73, end=2019, t2020="in") and est("real", "yes", "P", 24, T73, end=2019, t2020="in") < 0)
    chk("Jarocinski-Karadi surprise (real with FCI): u24 within 0.1 and P24 within 0.1 of the baseline in both samples", all(abs(est("real", "yes", v, 24, st, shock="jk") - est("real", "yes", v, 24, st)) < 0.1 for v in ("u", "P") for st in ("1996-01", T73)))
    chk("6 lags, real from 1996: u at 24 m within 0.05 of 12 lags; P at 24 m 10 to 30 percent smaller", (lambda d6: abs(d6.loc["u"].r24 - est("real", "yes", "u", 24)) < 0.05 and 0.7 < d6.loc["P"].r24 / est("real", "yes", "P", 24) < 0.9)(R[CS.case_id(dict(form="real", fci="real", **B96))].query("lags == 6").set_index("var")))
    LG6 = [c for p_ in CS.PANELS if p_["id"][0] in "BR" for c in p_["cases"] if c["fci"] != 0]
    neg6 = [(CS.case_id(c), h) for c in LG6 for h in H3 if (lambda r: r[f"hi{h}"] < 0)(R[CS.case_id(c)].query("lags == 6 and var == 'u'").iloc[0])]
    chk("lags: with 6 lags only the nominal version from 1973 with 2020 left in shows a significant fall in unemployment (two horizons); none with 12 lags", len(neg6) == 2 and all(i.startswith("nom_nom_upi_1973-01_all_in") for i, _ in neg6))
    chk("final section: a linear trend explains more of the real FCI than of the version relative to r* since 1973 (macros tr:r:r2, tr:s:r2), and the spline fits more of the r* version than of the real version since 1996", _slow_ok())
    chk("final section: with the spline from 1973 the real responses with the FCI at 24 m are significant at the 5 percent level", all(sig5("real", "yes", v, 24, T73, trend="spline") for v in ("u", "P")))
    return bad

def _slow_ok():
    """Reads the macros written by 07_report (final_section) and 07b (gs_comparison)."""
    import re
    from lib.paths import REPORT
    txt = "".join((REPORT / f).read_text() for f in ("numbers.tex", "numbers_ext.tex") if (REPORT / f).exists())
    g = lambda k: float(re.search(r"csname bl:" + re.escape(k) + r"\\endcsname\{([-0-9.]+)\}", txt).group(1))
    return g("tr:r:r2") > g("tr:s:r2") + 20 and g("slow:rstar:idx") > g("slow:real:idx")
