"""
NFCI and ANFCI in the real case (REAL_QA R13): published series unchanged, month-end, 1973-2026; zero 1973-2026 mean (main), 1990-2026 (check).
"_2y" columns divide by the weekly response to NS surprises (nominal-case conversion, answer 16: NFCI 0.097, ANFCI 0.185 per NS unit; agenda item 8 open).
Usage: python experimental/real_case/nfci_real.py
Output: nfci_real_monthly.csv
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CONV = {"NFCI": 0.097, "ANFCI": 0.185}


def main():
    out = {}
    for nm in CONV:
        d = pd.read_csv(os.path.join(ROOT, "raw", f"{nm}.csv"))
        s = pd.Series(pd.to_numeric(d.iloc[:, 1], errors="coerce").values, index=pd.to_datetime(d.iloc[:, 0])).dropna()
        s = s.resample("ME").last(); s.index = s.index.to_period("M"); s = s.loc["1973-01":"2026-10"]
        out[nm] = s - s.mean()
        out[f"{nm}_2y"] = out[nm] / CONV[nm]
        out[f"{nm}_2y_z90"] = (s - s.loc["1990-01":].mean()) / CONV[nm]
    R = pd.DataFrame(out)
    R.to_csv(os.path.join(HERE, "nfci_real_monthly.csv"), float_format="%.4f", index_label="month")
    mk = pd.read_csv(os.path.join(HERE, "market_real_monthly.csv"), index_col=0); mk.index = pd.PeriodIndex(mk.index, freq="M")
    for nm in CONV:
        k = pd.concat([R[f"{nm}_2y"], mk.MKT_real], axis=1).dropna()
        print(f"{nm}: sd {R[f'{nm}_2y'].std():.2f} (2-year units); latest {R[f'{nm}_2y'].iloc[-1]:+.2f} (1990 zero {R[f'{nm}_2y_z90'].iloc[-1]:+.2f}); "
              f"corr with real market index: levels {k.corr().iloc[0, 1]:.2f}, 12m {k.diff(12).corr().iloc[0, 1]:.2f}")
    sel = [pd.Period(m, "M") for m in ("1974-06", "1979-12", "1981-06", "1985-01", "1990-01", "2000-01", "2008-12", "2013-01", "2021-06", "2023-10", "2026-09")]
    print(R.loc[sel, ["NFCI_2y", "ANFCI_2y", "NFCI_2y_z90", "ANFCI_2y_z90"]].round(2).to_string())


if __name__ == "__main__":
    main()
