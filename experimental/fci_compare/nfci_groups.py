"""
NFCI and ANFCI by the project's groups (rates incl. the policy rate, Treasury and credit/corporate/mortgage spreads; equities; dollar; other), in the transmission-lens
unit (pp of the 2-year yield per NS unit: each contribution divided by the index's weekly response to NS surprises, as in transmission_v3.py).
Source: Chicago Fed weekly contributions of the 105 indicators (api.data.chicagofed.org/NFCI/contributions-data-series-xlsx.xlsx, saved as raw/nfci_contributions.xlsx;
current vintage). The contributions sum to the index (checked). ANFCI also has a macroeconomic-adjustment contribution, kept as its own group.
Mapping (indicator mnemonics, Key sheet):
    rates / policy and Treasury:  FFR, D2, D10, SPR210, SPR23M
    rates / money-market, swap and credit spreads: SWAP2, SWAP10, SWAP3M, TED, TERM, LIBID, REPO, REPOGCF, RTERM, CBILL, CTERM, ABCP, A2P2, MLIQ10,
          BAA, HY, CTF, CMBS, CTMBS, CTABS, AABS, ABSSPREAD, MINC, JINC, CBCAR, CBPER, MSWAP, LIG, LHY
    equities: EQRET, W500, MCAP, FINS
    dollar:   USD
    other:    all remaining indicators (volatility, quantities and issuance, leverage and balance sheets, surveys, delinquencies, repo fails, house and property prices)
Usage: python experimental/fci_compare/nfci_groups.py
Output: nfci_groups_monthly.csv (columns "<index>|<group>")
"""
import os
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
POLICY_TSY = ["FFR", "D2", "D10", "SPR210", "SPR23M"]
SPREADS = ["SWAP2", "SWAP10", "SWAP3M", "TED", "TERM", "LIBID", "REPO", "REPOGCF", "RTERM", "CBILL", "CTERM", "ABCP", "A2P2", "MLIQ10",
           "BAA", "HY", "CTF", "CMBS", "CTMBS", "CTABS", "AABS", "ABSSPREAD", "MINC", "JINC", "CBCAR", "CBPER", "MSWAP", "LIG", "LHY"]
EQ = ["EQRET", "W500", "MCAP", "FINS"]
USD = ["USD"]
CONV = {"NFCI": 0.097, "ANFCI": 0.185}          # weekly response to a 1-unit NS surprise (transmission_v3.py)


def groups(cols):
    g = {}
    for c in cols:
        g[c] = ("rates: policy and Treasury" if c in POLICY_TSY else "rates: spreads" if c in SPREADS else "equities" if c in EQ else "dollar" if c in USD
                else "macro adjustment" if c == "Macro" else "other")
    return g


def main():
    path = os.path.join(ROOT, "raw", "nfci_contributions.xlsx")
    out = {}
    for nm in ("NFCI", "ANFCI"):
        d = pd.read_excel(path, nm)
        d["Date"] = pd.to_datetime(d.Date); d = d.set_index("Date")
        g = groups(d.columns)
        G = d.T.groupby(pd.Series(g)).sum().T
        tot = pd.read_csv(os.path.join(ROOT, "raw", f"{nm}.csv"), index_col=0, parse_dates=True).iloc[:, 0]
        j = pd.concat([G.sum(axis=1), tot], axis=1).dropna()
        print(f"{nm}: {d.shape[1]} indicators; contributions sum vs published index: max abs diff {float((j.iloc[:, 0] - j.iloc[:, 1]).abs().max()):.3f} over {len(j)} weeks")
        cnt = pd.Series(g).value_counts().to_dict()
        print("   indicators per group:", cnt)
        M = G.resample("ME").last(); M.index = M.index.to_period("M")
        M = M.loc["1990-01":"2026-10"] / CONV[nm]
        M = M - M.mean()
        print("   sd by group (2-year-yield pp, monthly 1990-2026):", M.std().round(2).to_dict())
        print("   latest", M.index[-1], M.iloc[-1].round(2).to_dict(), "total", round(float(M.iloc[-1].sum()), 2))
        for c in M:
            out[f"{nm}|{c}"] = M[c]
    pd.DataFrame(out).to_csv(os.path.join(HERE, "nfci_groups_monthly.csv"), float_format="%.4f", index_label="month")


if __name__ == "__main__":
    main()
