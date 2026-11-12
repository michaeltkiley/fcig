"""How stable and how precise are activity-fitted weights, and how do they compare with the market and FRB/US weights?
12-month-ahead outcomes, each step and form, 1976-2025. Weights are shares of the oriented, standardized variables (sum 1), so that sets are comparable across units.
Activity-fitted = sign-constrained least squares (the sign that tightening should have), own lag and constant partialled out. Also unconstrained OLS with HAC t-statistics,
a Wald test that the OLS coefficients are proportional to the market (or FRB/US) weights, a moving-block bootstrap (24-month blocks, rows resampled jointly), and the
recursive path of the fitted shares. Writes results/act_weights.csv, act_paths.csv."""
import sys; sys.dont_write_bytecode = True
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np, pandas as pd, statsmodels.api as sm
from scipy.optimize import nnls
import common as c

D = c.load_monthly(); h = 12
mw = pd.read_csv(c.RES_IN / "market_weights.csv", index_col=0).weight.reindex(c.VARS).values
fw = pd.read_csv(c.RES_IN / "frbus_weights.csv", index_col=0).frbus_weight.reindex(c.VARS).values
J = pd.period_range(c.SAMPLE0, "2026-09", freq="M"); allidx = pd.period_range("1958-01", "2026-12", freq="M")
rng = np.random.default_rng(c.SEED)


def nnls_shares(Zs, y, own, sign):
    A = np.column_stack([np.ones(len(y))] + ([own] if own is not None else [])); P = A @ np.linalg.pinv(A)
    w, _ = nnls(Zs - P @ Zs, sign * (y - P @ y)); s = w.sum(); return (w / s if s > 0 else np.full(3, np.nan)), w


def block_idx(n, L):
    nb = int(np.ceil(n / L)); st = rng.integers(0, n - L + 1, nb); return np.concatenate([np.arange(s, s + L) for s in st])[:n]


rows, paths = [], []
for case in ("rstar", "real"):
    Z = c.three_vars(D, case)
    for form in ("level", "change"):
        Zo = c.to_form(Z * c.ORIENT, form)
        for oc, (y, own, valid) in c.outcomes(D, h).items():
            sg = c.OUTCOMES[oc]
            v = pd.Series(np.asarray(valid), index=allidx).reindex(J).values
            df = pd.DataFrame({"y": y.reindex(J).values, "own": own.reindex(J).values if own is not None else 0.0}, index=J)
            for k, vn in enumerate(c.VARS): df[vn] = Zo[vn].reindex(J).values
            df = df[v].dropna(); sd = df[c.VARS].std().values; Zs = ((df[c.VARS] - df[c.VARS].mean()) / sd).values
            o = df.own.values if own is not None else None
            ref = {"MKT": np.abs(mw) * sd / (np.abs(mw) * sd).sum(), "FRBUS": np.abs(fw) * sd / (np.abs(fw) * sd).sum()}
            pt, w0 = nnls_shares(Zs, df.y.values, o, sg)
            # OLS with HAC and Wald proportionality tests
            Xd = sm.add_constant(pd.DataFrame(np.column_stack(([o] if o is not None else []) + [Zs])), has_constant="add")
            r = sm.OLS(df.y.values, Xd).fit(cov_type="HAC", cov_kwds={"maxlags": c.HACLAG(h)})
            nb = 1 + (1 if o is not None else 0); b = np.asarray(r.params)[nb:]; tt = np.asarray(r.tvalues)[nb:]
            out = dict(step=case, form=form, outcome=oc, n=len(df), **{f"ols_t_{vn}": tt[j] for j, vn in enumerate(c.VARS)},
                       ols_joint_p=float(r.f_test(np.eye(len(r.params))[nb:]).pvalue))
            for nm, wref in (("MKT", mw), ("FRBUS", fw)):
                q = np.abs(wref) * sd; R = np.zeros((2, len(r.params))); R[0, nb + 1] = q[0]; R[0, nb] = -q[1]; R[1, nb + 2] = q[0]; R[1, nb] = -q[2]
                # b_j / q_j equal across j (signs: the oriented coefficients must share the market's orientation, which Zs already carries)
                out[f"wald_p_prop_{nm}"] = float(r.wald_test(R, use_f=False, scalar=True).pvalue)
            # block bootstrap of the shares
            bs = []
            for _ in range(c.NBOOT):
                ii = block_idx(len(df), c.BLOCK); s, w = nnls_shares(Zs[ii], df.y.values[ii], o[ii] if o is not None else None, sg); bs.append(np.r_[s, w.sum()])
            bs = np.array(bs); zero = np.isnan(bs[:, 0]).mean()
            for j, vn in enumerate(c.VARS):
                lo, hi = np.nanpercentile(bs[:, j], [5, 95]) if zero < 1 else (np.nan, np.nan)
                out.update({f"share_{vn}": pt[j], f"lo90_{vn}": lo, f"hi90_{vn}": hi, f"mkt_{vn}": ref["MKT"][j], f"frbus_{vn}": ref["FRBUS"][j]})
            out["boot_all_zero"] = zero; out["pt_all_zero"] = float(np.isnan(pt[0]))
            dist = lambda S, ref_: np.nanmean(np.abs(S - ref_).sum(axis=1))
            out["l1_to_mkt_boot_mean"] = dist(bs[:, :3], ref["MKT"]); out["l1_to_frbus_boot_mean"] = dist(bs[:, :3], ref["FRBUS"])
            out["l1_mkt_frbus"] = np.abs(ref["MKT"] - ref["FRBUS"]).sum()
            rows.append(out)
            # recursive path (expanding, training rows <= origin - h), annual origins
            if form == "change" or True:
                for yr in range(1995, 2026, 2):
                    t = pd.Period(f"{yr}-12", "M"); m = df.index <= t - h
                    if m.sum() < 120: continue
                    mu, s2 = df.loc[m, c.VARS].mean().values, df.loc[m, c.VARS].std().values
                    Zr = ((df.loc[m, c.VARS].values - mu) / s2); sh, w = nnls_shares(Zr, df.y.values[m], o[m] if o is not None else None, sg)
                    q = np.abs(mw) * s2; qf = np.abs(fw) * s2
                    paths.append(dict(step=case, form=form, outcome=oc, origin=yr, **{f"s_{vn}": sh[j] for j, vn in enumerate(c.VARS)}, strength=w.sum(),
                                      mkt_y10=(q / q.sum())[0], frbus_y10=(qf / qf.sum())[0]))
        print(case, form, flush=True)
pd.DataFrame(rows).to_csv(c.OUT / "act_weights.csv", index=False); pd.DataFrame(paths).to_csv(c.OUT / "act_paths.csv", index=False)
