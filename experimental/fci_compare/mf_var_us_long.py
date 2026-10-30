"""
ECB-method VAR (mf_var_us.py) on long samples with a recursive (Cholesky) funds-rate yardstick (INDEX_QA.md answer 39).
Samples and variables:
    1960  financial variables available from 1960: policy rate (FEDFUNDS), 10-year (GS10), Baa spread (BAA - GS10), equities (100 ln CAPE)
    1973  all six: adds mortgage spread (MORTGAGE30US monthly average - GS10) and real broad dollar (100 ln; TWEXBPA 1973-2005 spliced to RTWEXBGS from 2006)
    Macro: core PCE inflation gap (12-month, less 2), unemployment gap (UNRATE less CBO NROU interpolated). Sample to 2025-12, all 2020 months excluded.
    FRED series are monthly averages. CAPE: Shiller (raw/shiller_cape.csv, to 2023-09) spliced in logs to the project's CAPE (end of month) from 1990 by the mean overlap ratio.
    The Baa spread stands in for the BBB spread in both samples (ICE BBB starts 1996).
    Financial variables demeaned over the estimation sample. Lags by BIC (1-6); 6 lags reported as a check.
Model: as mf_var_us.py (financial variables enter the macro equations only through F = alpha'Z; financial equations unrestricted; alpha by ML).
Yardstick (recursive): Cholesky ordering inflation gap, unemployment gap, policy rate, other financial variables. A funds-rate shock has no same-month effect on the macro
    variables and moves the other financial variables by the Cholesky column (scaled to 1 pp on the funds rate). The funds rate is held +1 pp for 12 months by a sequence of
    such shocks; later effects through the VAR. Effect = -2 x unemployment gap at month 12.
Weights: variable j held +1 for 12 months, others at baseline, divided by the yardstick.
Inputs not in git: raw FEDFUNDS, GS10, BAA, MORTGAGE30US, TWEXBPA, RTWEXBGS, PCEPILFE, UNRATE, NROU (FRED); raw/shiller_cape.csv (Shiller ie_data.xls, CAPE column).
Usage: python experimental/fci_compare/mf_var_us_long.py
Outputs: mf_var_us_long.csv (weights), mf_var_us_long_monthly.csv (indexes)
"""
import os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "experimental", "ms_fci"))
import mf_var_us as V
import macro_model_dl as DL


def fm(name, how="mean"):
    s = V.fred_m(name)
    s = s.resample("MS").mean() if how == "mean" else s
    s.index = s.index.to_period("M")
    return s


def financial():
    gs10 = fm("GS10")
    cs = pd.read_csv(os.path.join(ROOT, "raw", "shiller_cape.csv")); cs.index = pd.PeriodIndex(cs.month, freq="M"); lc = np.log(cs.cape)
    x, _ = DL.levels_data()                                             # project CAPE: x["equities"] = 100 ln CAPE, demeaned; recover undemeaned via the overlap
    import path_fci as PF
    PF.L.REAL10 = False; PF.L.RSTAR = False
    X, _ = PF.L.build()
    pc = X.lncape.resample("ME").last(); pc.index = pc.index.to_period("M")
    ov = lc.index.intersection(pc.index)
    shift = float((pc.loc[ov] - lc.loc[ov]).mean())
    cape = pd.concat([lc.loc[:pc.index[0] - 1] + shift, pc])
    old = fm("TWEXBPA"); new = fm("RTWEXBGS")
    k = float(np.log(new.loc["2006-01":"2006-12"]).mean() - np.log(old.loc["2006-01":"2006-12"]).mean())
    usd = pd.concat([np.log(old.loc[:"2005-12"]) + k, np.log(new.loc["2006-01":])])
    return pd.DataFrame({"policy rate": fm("FEDFUNDS"), "10-year": gs10, "mortgage spread": fm("MORTGAGE30US") - gs10, "Baa spread": fm("BAA") - gs10,
                         "equities": 100 * cape, "dollar": 100 * usd})


def recursive_yardstick(v, H=36, months=12):
    A = v.companion(); n = len(v.names); k = v.names.index("policy rate"); p = v.p
    L = np.linalg.cholesky(v.Om)
    imp = L[:, k] / L[k, k]
    y = np.zeros((H + p, n))
    for t in range(H):
        pred = sum(A[l] @ y[p + t - 1 - l] for l in range(p))
        eps = (1.0 - pred[k]) if t < months else 0.0
        y[p + t] = pred + imp * eps
    return y[p:], imp


def main():
    F = financial()
    M = V.macro_data(False)
    rows, idx = [], {}
    for label, start, cols in (("1960, 4 variables", "1960-01", ["policy rate", "10-year", "Baa spread", "equities"]),
                               ("1973, 6 variables", "1973-01", ["policy rate", "10-year", "mortgage spread", "Baa spread", "equities", "dollar"])):
        Z = F[cols].loc[start:"2025-12"].dropna()
        Z = Z - Z.loc[: "2025-12"].drop(index=[t for t in Z.index if t.year == 2020]).mean()
        Mm = M.loc[start:]
        first = str(pd.Period(start, "M") + 6)
        nz = len(cols)
        starts = [np.r_[0.5, 0.5, np.full(nz - 2, 0.1)] * np.r_[1, 1, [(-0.05 if c == "equities" else 1.0) for c in cols[2:]]],
                  np.r_[1.0, np.full(nz - 1, 0.05)]]
        bic = {}
        fits = {}
        for p in range(1, 7):
            v = V.MFVAR(Mm, Z, p, start=start, first=first).fit(starts)
            bic[p] = -2 * v.ll + v.nparams() * np.log(v.T); fits[p] = v
            print(f"[{label}] p={p}: T {v.T}, logL {v.ll:.1f}, BIC {bic[p]:.1f}", flush=True)
        pb = min(bic, key=bic.get)
        for p in sorted({pb, 6}):
            v = fits[p]
            se = v.alpha_se()
            y, imp = recursive_yardstick(v)
            ui = v.names.index("unemployment gap"); nm = v.nm
            du = y[11, ui]
            w = {c: float(v.partial(j)[11, ui] / du) for j, c in enumerate(cols)}
            tag = "BIC" if p == pb else "6 lags"
            print(f"\n[{label}, p={p} ({tag})] alpha: " + ", ".join(f"{c} {a:+.3f} ({s:.3f})" for c, a, s in zip(cols, v.alpha, se)))
            print("   recursive same-month effects of +1 pp funds rate: " + ", ".join(f"{c} {imp[nm + i]:+.3f}" for i, c in enumerate(cols)))
            print("   yardstick: unemployment gap months 1,6,12,18,24,36:", np.round(y[[0, 5, 11, 17, 23, 35], ui], 3), "| index F months 1,6,12,24:", np.round(y[[0, 5, 11, 23], nm:] @ v.alpha, 3))
            print("   financial variables at month 12:", dict(zip(cols, np.round(y[11, nm:], 3))))
            print(f"   output equivalent at month 12: {-2 * du:+.3f}% (FRB/US -0.45%); weights: " + ", ".join(f"{c} {wj:+.4f}" for c, wj in w.items()))
            for c in cols:
                rows.append(dict(sample=label, lags=p, choice=tag, variable=c, alpha=v.alpha[cols.index(c)], alpha_se=se[cols.index(c)], weight=w[c], yardstick_u_m12=du))
            idx[f"{label}, p={p}"] = (Z * pd.Series(w)).sum(axis=1)
    pd.DataFrame(rows).to_csv(os.path.join(HERE, "mf_var_us_long.csv"), float_format="%.5f", index=False)
    pd.DataFrame(idx).to_csv(os.path.join(HERE, "mf_var_us_long_monthly.csv"), float_format="%.4f", index_label="month")


if __name__ == "__main__":
    main()
