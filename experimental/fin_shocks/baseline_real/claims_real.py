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
    return bad
