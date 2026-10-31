"""Step 7b. Proxy-SVAR unemployment responses with raw, Greenbook-purged (GB) and Greenbook-purged + AR-removed (GB+AR) instruments (MAR). Systems: base, +EBP, +NFCI, +index.
Windows: CH (VAR 1993-07..2007-06, 6 lags) and 1994-2019 residuals (VAR 1994-01..2026-09, 12 lags). Response of the unemployment gap (pp) to +25 bp in the policy variable at 12 and 24 months, 95% Anderson-Rubin set.
Output: 07b_gb_proxy.log"""
import numpy as np, pandas as pd, warnings
from mpcommon import *
warnings.filterwarnings("ignore")
eb = pd.read_csv(HERE / "data/ebp.csv"); eb.index = pd.PeriodIndex(pd.to_datetime(eb.date), freq="M"); M["ebp"] = eb.ebp.reindex(M.index)
s = pd.read_csv(HERE.parents[1] / "fci_note/replication/data/NFCI.csv"); s = pd.Series(s.iloc[:, 1].values, index=pd.to_datetime(s.iloc[:, 0])); M["nfci"] = s.groupby(s.index.to_period("M")).mean().reindex(M.index)
ev = events(); G = pd.read_csv(HERE / "data/mp_instruments_gb.csv", index_col=0); G.index = pd.PeriodIndex(G.index, freq="M")
raw = {k: monthly_instruments(ev, (k,))[k] for k in ("MP1", "FF4", "ns", "ED4")}
SYS = {"base": [], "+index": ["market_rstar"], "+EBP": ["ebp"], "+NFCI": ["nfci"]}
H = 24

def cell(pv, k, sysname, win):
    cols = ["u_gap", "pi_core", pv] + SYS[sysname]; p = cols.index(pv)
    if win == "CH": args = dict(vstart="1993-07", vend="2007-06", lags=6); rend = "2007-06"
    else: args = dict(vstart="1994-01", vend="2026-09", lags=12); rend = "2019-12"
    r, e = var_resid(cols, args["vstart"], args["vend"], lags=args["lags"], rstart="1994-01"); e = e.loc[:rend]
    out = []
    for nm, z in (("raw", raw[k].where(raw[k].index <= pd.Period("2020-12", "M"), 0.0)), ("GB", G[f"{k}_gb"]), ("GB+AR", G[f"{k}_gbar"])):
        zz = z.reindex(e.index); Fr, Fh, _ = first_stage(e[pv], zz); FL, FC, b = lunsford_colombo(e, zz, pv)
        Phi = r.ma_rep(H); irf = np.einsum("hij,j->hi", Phi, b); ar = ar_set(Phi[:, 0, :], e.values, p, zz)
        f = lambda h: "unb" if not (np.isfinite(ar[h][0]) and np.isfinite(ar[h][1])) else f"({0.25 * ar[h][0]:+.2f},{0.25 * ar[h][1]:+.2f})"
        out.append(f"{nm}: F {Fr:4.1f} u12 {0.25 * irf[12, 0]:+.2f} {f(12):>14s}")
    print(f"  {pv:3s} {k:4s} {sysname:7s} | " + " | ".join(out))

for win in ("CH", "1994-2019"):
    print(f"\n== {win} window: u-gap response per +25 bp at 12 months, proxy-SVAR; 'unb' = unbounded 95% AR set ==")
    for pv, insts in (("ffr", ("MP1", "FF4")), ("gs2", ("ED4",))):
        if win == "CH" and pv == "gs2": continue
        for k in insts:
            for sysname in SYS:
                cell(pv, k, sysname, win)
