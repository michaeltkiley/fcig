"""
Expected inflation for the real case (REAL_QA.md R1-R3): Cleveland Fed model expectations (EXPINF1YR, EXPINF10YR; monthly from 1982) spliced before 1982
to the Livingston Survey 12-month CPI inflation expectation (Philadelphia Fed, median, "G_BP_To_12M", semiannual June/December, linearly interpolated to
months), level-adjusted to each Cleveland horizon by the mean gap over 1982-01..1984-12.
Inputs (not in git): raw/EXPINF1YR.csv, raw/EXPINF10YR.csv (FRED), raw/livingston_median_growth.xlsx (Philadelphia Fed MedianGrowthRate.xlsx, sheet CPI).
Usage: python experimental/real_case/expinf.py
Outputs: expinf_monthly.csv (einf_1y, einf_10y, livingston_12m, flags), expinf.png
"""
import os
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def fred(name):
    d = pd.read_csv(os.path.join(ROOT, "raw", f"{name}.csv"))
    s = pd.Series(pd.to_numeric(d.iloc[:, 1], errors="coerce").values, index=pd.to_datetime(d.iloc[:, 0])).dropna()
    s.index = s.index.to_period("M"); return s


def build():
    lv = pd.read_excel(os.path.join(ROOT, "raw", "livingston_median_growth.xlsx"), "CPI").set_index("Date")["G_BP_To_12M"].dropna()
    lv.index = pd.to_datetime(lv.index).to_period("M")
    idx = pd.period_range(lv.index[0], "2026-12", freq="M")
    lvm = lv.reindex(idx).interpolate(limit_area="inside")
    out = {"livingston_12m": lvm}
    win = slice("1982-01", "1984-12")
    for lab, name in (("einf_1y", "EXPINF1YR"), ("einf_10y", "EXPINF10YR")):
        c = fred(name)
        shift = float((c.loc[win] - lvm.loc[win]).mean())
        s = pd.concat([lvm.loc[:c.index[0] - 1] + shift, c])
        out[lab] = s
        out[f"{lab}_shift"] = pd.Series(shift, index=s.index)
        print(f"{lab}: Cleveland from {c.index[0]}, Livingston shifted by {shift:+.2f} pp before then (mean gap 1982-84)")
    D = pd.DataFrame(out).loc["1960-01":]
    D["spliced"] = (D.index < pd.Period("1982-01", "M")).astype(int)
    return D


def main():
    D = build()
    D.to_csv(os.path.join(HERE, "expinf_monthly.csv"), float_format="%.4f", index_label="month")
    print(D.loc[["1973-01", "1975-01", "1980-01", "1981-12", "1982-01", "1990-01", "2000-01", "2020-01", "2026-09"], ["livingston_12m", "einf_1y", "einf_10y"]].round(2).to_string())
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(13, 5.5))
    t = D.index.to_timestamp()
    ax.plot(t, D.einf_1y, color="#1f5fa8", lw=1.3, label="1-year expected inflation (Cleveland from 1982; spliced Livingston before)")
    ax.plot(t, D.einf_10y, color="#d62728", lw=1.3, label="10-year expected inflation (Cleveland from 1982; spliced Livingston before)")
    ax.plot(t, D.livingston_12m, color="gray", lw=0.9, ls="--", label="Livingston 12-month CPI expectation (unadjusted)")
    ax.axvline(pd.Timestamp("1982-01-01"), color="black", lw=0.8, ls=":")
    ax.grid(alpha=0.25); ax.set_ylabel("percent"); ax.legend(fontsize=9, frameon=False)
    ax.set_title("Expected inflation for the real case", fontsize=11)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "expinf.png"), dpi=130)


if __name__ == "__main__":
    main()
