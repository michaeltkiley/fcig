"""
Output-lens market index from the preferred variant of mkt_output_variants.py ((iii) real 10-year, 12-month flows, 1973-2025, h = 12):
    OL_t = sum_j (v_j / a) * [x_j(t) - x_j(t-12)]   (market-index units; a flow measure, like FCI-G)
compared with the market index's own 12-month change, the macro-model EP_4 12-month change and FCI-G (1-year lookback / 0.4525).
Usage: python experimental/market_macro/mkt_output_index.py
"""
import os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import mkt_output as MO
import mkt_output_variants as MV


def main():
    R = pd.read_csv(os.path.join(HERE, "mkt_output_variants.csv"))
    r = R[(R.variant == "(iii) real 10y, 12m flows") & (R["sample"] == "1973-2025") & (R.h == 12)].iloc[0]
    v = np.array([r[f"v/a {k}"] for k in MO.VARS])
    print("output-lens weights (market units, flows): " + ", ".join(f"{k} {v[i]:+.4f}" for i, k in enumerate(MO.VARS)) + f";  market w: " + ", ".join(f"{k} {MO.W[i]:+.4f}" for i, k in enumerate(MO.VARS)))
    D, X = MV.build(True)
    dX = X.diff(12)
    OL = pd.Series(dX.values @ v, index=X.index, name="output-lens flow")
    MK = pd.Series(dX.values @ MO.W, index=X.index, name="market index 12m change (real 10y)")
    mm = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "macro_model_v3_monthly.csv"), index_col=0); mm.index = pd.PeriodIndex(mm.index, freq="M")
    f1 = pd.read_csv(os.path.join(ROOT, "raw", "fed_monthly_1yr.csv"), parse_dates=["date"]).set_index("date").iloc[:, 0]; f1.index = f1.index.to_period("M")
    J = pd.concat([OL, MK, mm["EP_4"].diff(12).rename("EP_4 12m change"), (f1 / 0.4525).rename("FCI-G 1yr")], axis=1).loc["1990-01":].dropna()
    pd.set_option("display.width", 200)
    print("\n1990-2026 correlations:\n" + J.corr().round(2).to_string())
    print("sd:", J.std().round(2).to_dict())
    print("latest:", J.iloc[-1].round(2).to_dict(), J.index[-1])
    pd.concat([OL, MK], axis=1).to_csv(os.path.join(HERE, "mkt_output_flow_index.csv"), float_format="%.4f", index_label="month")


if __name__ == "__main__":
    main()
