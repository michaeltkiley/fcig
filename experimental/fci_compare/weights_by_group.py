"""
Weights of the macro-model index, the market-based index (NS), GS (replication) and FCI-G by the project's variable groups, in funds-rate pp (tighter positive), on a common "spread basis":
rates (policy rate, 10-year Treasury, mortgage spread over the 10-year, BBB spread over the 10-year), equities, dollar, other (house prices).
  per unit: pp of funds rate per +1 pp (rates, spreads) or per +1 % (equities, dollar, house prices)
  per 1 sd: the same times the 1990-2026 standard deviation of the variable (daily series; house-price ratio monthly), i.e. how much a typical move counts.
FCI-G: the weight on a change that has just occurred (row 0 of the Fed's multipliers, 0.0999 per pp for the funds rate etc.; weights decline with the age of the change over the 3-year lookback)
divided by the FRB/US yardstick 0.4525. The Fed's rates are levels of the funds rate, 10-year, mortgage rate and BBB yield (each holding the others fixed); to put them on the spread basis the 10-year
weight (spreads held fixed) = w10 + w_mortgage + w_BBB, the mortgage spread weight = w_mortgage, the BBB spread weight = w_BBB.
GS: published weights (4.4/45.1/39.6/4.9/6.0) times kappa = 0.945. Market-based (NS weights from the event window; units pp of an NS unit) times 0.983 funds-rate pp per NS unit.
Macro-model: q4 FRB/US weights (policy rate direct 0.0085).
Usage: python experimental/fci_compare/weights_by_group.py        Output: weights_by_group.csv
"""
import os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "experimental", "path_fci"))
import path_fci as P
import path_fci_gss_ns as Q
import fcig_replicate as R


def main():
    ev = P.events(P.USMPD)
    d = ev.dropna(subset=Q.FUT + ["UST2Y"] + list(Q.ENDOG.values())).reset_index(drop=True)
    gss, ns, _, _ = Q.gss_ns(d)
    wn = pd.Series(Q.estimate(d, ns, True)[0], index=list(Q.ENDOG))
    P.L.REAL10 = False; P.L.RSTAR = False
    X, G = P.L.build()
    mort = R.fred("MORTGAGE30US").reindex(X.index, method="ffill")
    hp = np.log(R.splice_level(R.zillow(), R.fred("CSUSHPISA"))); oer = np.log(P.L.get("CUSR0000SEHC"))
    hp = hp - oer.reindex(hp.index.union(oer.index)).sort_index().ffill().reindex(hp.index)
    sd = {"policy rate": X.ffr.std(), "10-year": X.y10.std(), "mortgage spread": (mort - G.x_y10.reindex(X.index)).std(), "BBB spread": X.bbb.std(),
          "equities": 100 * X.lncape.std(), "dollar": 100 * X.lnrusd.std(), "house prices": 100 * hp.loc["1990":].std()}
    base = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "frbus_sensitivities.csv"), index_col=0)["ffr_eq_q4"]
    ext = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "frbus_sensitivities_ext.csv"), index_col=0)["ffr_eq_q4"]
    k, ns_fr, yard = 0.945, 0.983, 0.4525
    m = -pd.read_csv(os.path.join(ROOT, "multipliers.csv")).values
    m[:, 4:6] *= -1
    f = dict(zip(["ffr", "y10", "mort", "bbb", "stock", "house", "usd"], m[0]))            # tightening-positive weight on a change that has just occurred
    fcig = {"policy rate": f["ffr"] / yard, "10-year": (f["y10"] + f["mort"] + f["bbb"]) / yard, "mortgage spread": f["mort"] / yard, "BBB spread": f["bbb"] / yard,
            "equities": f["stock"] / yard, "dollar": f["usd"] / yard, "house prices": f["house"] / yard}
    W = pd.DataFrame({
        "Macro model": {"policy rate": ext["rshort_direct"], "10-year": base["rg10"], "mortgage spread": ext["rme"], "BBB spread": base["rbbbp"], "equities": -base["req"], "dollar": base["fpxr"], "house prices": ext["phouse"]},
        "Market-based (NS)": {"10-year": wn["10-yr"] * ns_fr, "equities": wn["Equities (ln CAPE)"] * ns_fr, "dollar": wn["Dollar (ln real)"] * ns_fr},
        "GS": {"policy rate": 0.044 * k, "10-year": 0.451 * k, "BBB spread": 0.396 * k, "equities": -0.049 * k, "dollar": 0.060 * k},
        "FCI-G (impact weight)": fcig}).reindex(["policy rate", "10-year", "mortgage spread", "BBB spread", "equities", "dollar", "house prices"])
    grp = pd.Series({"policy rate": "rates", "10-year": "rates", "mortgage spread": "rates", "BBB spread": "rates", "equities": "equities", "dollar": "dollar", "house prices": "other"})
    sdv = pd.Series(sd)
    pd.set_option("display.width", 200)
    out = W.copy(); out.insert(0, "group", grp)
    print("Weights per unit (funds-rate pp per +1 pp, or per +1 % for equities, dollar, house prices):")
    print(out.round(3).to_string())
    print("\nsd of each variable (1990-2026):", {k: round(float(v), 2) for k, v in sd.items()})
    S = W.mul(sdv, axis=0)
    o2 = S.copy(); o2.insert(0, "group", grp)
    print("\nWeights per 1 sd of the variable (funds-rate pp):")
    print(o2.round(2).to_string())
    par = pd.DataFrame({c: [W.loc[["policy rate", "10-year"], c].sum()] for c in W}, index=["rates: parallel +1 pp in the policy rate and the 10-year, spreads fixed"])
    print("\nRates group, parallel move:\n", par.round(3).to_string())
    out.to_csv(os.path.join(HERE, "weights_by_group.csv"), float_format="%.4f", index_label="variable")


if __name__ == "__main__":
    main()
