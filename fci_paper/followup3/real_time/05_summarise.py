"""Revision statistics and Holm-adjusted primary family (Market, r*, du and pay, three forms: 6 tests; core PCE has no vintages before 2001 so no OOS)."""
from rt_common import *
from scipy import stats
V = versions(); rows = []
orig_Y, orig_C = V["rev"]
def comp(name, a, b, lo="1995-01", hi="2025-09"):
    d = pd.concat([a.rename("rt"), b.rename("rev")], axis=1).loc[lo:hi]; d = d[C.keep_mask(d.index)].dropna()
    rows.append(dict(variable=name, n=len(d), corr=d.corr().iloc[0, 1], rms_diff=float(np.sqrt(((d.rt - d.rev) ** 2).mean())), sd_rev=d.rev.std(), mean_diff=float((d.rt - d.rev).mean())))
for nm, (Y, CT) in (("rt1", V["rt1"]), ("rt2", V["rt2"])):
    for yn in ("du", "pay", "pi"):
        lo = "2002-06" if yn == "pi" else ("2011-04" if nm == "rt2" else "1995-01")
        comp(f"{nm}: outcome {yn}", Y[yn], orig_Y[yn], lo)
    comp(f"{nm}: unemployment gap level", CT["du"].u, orig_C["du"].u, "2011-04" if nm == "rt2" else "1995-01")
    comp(f"{nm}: payroll g12", CT["pay"].g12, orig_C["pay"].g12)
    comp(f"{nm}: core PCE p12", CT["pi"].p12, orig_C["pi"].p12, "2002-06")
rs = pd.concat([rstar_rt().rename("rt"), C.M["rstar LW"].rename("rev")], axis=1).dropna(); 
rows.append(dict(variable="r* LW real-time vs full-sample (2005-07+)", n=len(rs), corr=rs.corr().iloc[0, 1], rms_diff=float(np.sqrt(((rs.rt - rs.rev) ** 2).mean())), sd_rev=rs.rev.std(), mean_diff=float((rs.rt - rs.rev).mean())))
pd.DataFrame(rows).to_csv(OUT / "revisions.csv", index=False); print(pd.DataFrame(rows).round(3).to_string())
A = pd.read_csv(OUT / "A_stance.csv"); res = []
for v in ("rev", "rt1"):
    S = A[(A.step == "rstar") & (A.version == v)].copy(); S["p"] = 1 - stats.norm.cdf(S.cw_idx_given_ff)
    m = len(S); o = S.p.sort_values().index; run = 0; S["p_holm"] = np.nan
    for i, ix in enumerate(o): run = max(run, min(1, (m - i) * S.p[ix])); S.loc[ix, "p_holm"] = run
    res.append(S)
R = pd.concat(res)[["version", "outcome", "form", "n_oos", "rmse_idx_given_ff", "cw_idx_given_ff", "p", "p_holm"]]
R = R[R.form != "level"].round(3); R.to_csv(OUT / "primary_holm.csv", index=False); print(R.to_string())
