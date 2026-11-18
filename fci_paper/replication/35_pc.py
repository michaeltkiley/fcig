"""Step 35. Principal-component indexes against the policy-news index (new version, stage 3; FP-A68).

Statistical FCIs (the Chicago Fed NFCI and ANFCI) weight indicators by their common variation, not by policy or spending. This step shows, on this
package's own series, what that weighting does.
 (1) Own principal-component indexes: the first principal component of standardized monthly series, 1973-01 to END, r* step, for three panels:
     A = the three policy-news assets (10-year yield, equity valuation, real dollar); B = A + BBB and mortgage spreads; C = B + the policy rate.
     Loadings, the share of variance explained, the sign (tighter = higher spreads), and the correlation of each component with the market index (MCFCI)
     and the NFCI, in levels and 12-month changes; skewness 1990-2026.
 (2) The published NFCI and ANFCI on the three assets with and without the Baa spread (results/10_nfci_on_variables.csv, step 10), restated here.
Writes results/35_pc_loadings.csv, 35_pc_corr.csv, 35_nfci_regressions.csv, scalars_35_pc.csv."""
import numpy as np, pandas as pd
from scipy.stats import skew
from lib import data, cases
from lib.config import RES, START, END
from lib.report import Scalars

S = Scalars("35_pc")
X = cases.inputs(data.load(), "rstar").loc[START:END]
IX = pd.read_csv(RES / "indexes_rstar.csv", index_col=0); IX.index = pd.PeriodIndex(IX.index, freq="M")
PAN = {"A_three_assets": ["y10", "equities", "dollar"], "B_plus_spreads": ["y10", "equities", "dollar", "bbb_spread", "mortgage_spread"],
       "C_plus_policy": ["y10", "equities", "dollar", "bbb_spread", "mortgage_spread", "policy"]}
SIGN_ON = {"A_three_assets": ("equities", -1), "B_plus_spreads": ("bbb_spread", 1), "C_plus_policy": ("bbb_spread", 1)}   # tighter = lower equities / wider spreads
lrows, crows = [], []
for basis in ("level", "change12"):
    Xb = X if basis == "level" else X.diff(12)
    for name, cols in PAN.items():
        Z = Xb[cols].dropna(); Zs = (Z - Z.mean()) / Z.std()
        U, s, Vt = np.linalg.svd(Zs.values, full_matrices=False)
        load = Vt[0]; v, sg = SIGN_ON[name]
        if np.sign(load[cols.index(v)]) != sg:
            load = -load
        pc = pd.Series(Zs.values @ load, index=Z.index)
        share = float(s[0] ** 2 / (s ** 2).sum())
        for c, l in zip(cols, load):
            lrows.append(dict(basis=basis, panel=name, variable=c, loading=l)); S.add(f"load_{basis}_{name}_{c}", l)
        S.add(f"share_{basis}_{name}", share)
        mk = IX.market if basis == "level" else IX.market.diff(12)
        nf = IX.nfci if basis == "level" else IX.nfci.diff(12)
        j = pd.concat([pc.rename("pc"), mk.rename("market"), nf.rename("nfci")], axis=1).dropna()
        r = dict(basis=basis, panel=name, n=len(j), var_share=share, corr_market=j.pc.corr(j.market), corr_nfci=j.pc.corr(j.nfci),
                 skew_1990=float(skew(pc.loc["1990-01":].dropna())) if basis == "level" else np.nan)
        crows.append(r)
        for k in ("corr_market", "corr_nfci", "skew_1990"):
            S.add(f"{k}_{basis}_{name}", r[k])
L = pd.DataFrame(lrows); L.to_csv(RES / "35_pc_loadings.csv", index=False, float_format="%.4f")
C = pd.DataFrame(crows); C.to_csv(RES / "35_pc_corr.csv", index=False, float_format="%.4f")
N = pd.read_csv(RES / "10_nfci_on_variables.csv"); N.to_csv(RES / "35_nfci_regressions.csv", index=False, float_format="%.4f")
for _, r in N.iterrows():
    S.add(f"nfcireg_{r.basis}_{r.y}_{r.regressors.replace(' + ', '_plus_').replace(' ', '_')}_R2", r.R2)
print(L.pivot_table(index=["basis", "panel"], columns="variable", values="loading").round(2).to_string())
print(C.round(2).to_string(index=False))
print(N[["basis", "y", "regressors", "R2"]].round(2).to_string(index=False))
S.save()
