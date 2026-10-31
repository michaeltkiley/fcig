"""Step 8. Summary metrics from credit_augmented.csv (06): for each system, (a) spread across identification schemes at 12 months in FULL-S1 with the funds rate (Cholesky policy-last, proxy with MP1, proxy with NS), and with the 2-year
(Cholesky, proxy NS, proxy ED4); (b) spread across samples for the Cholesky response (FULL-S1, FULL-S2, CH window), funds rate and 2-year. Unemployment gap, pp per +25 bp at 12 months. Output: 08_summary_metrics.log"""
import pandas as pd, numpy as np
d = pd.read_csv("credit_augmented.csv")
SYS = ["base", "+index", "+EBP", "+index+EBP", "+NFCI", "+index+NFCI", "+ANFCI"]
def get(sample, pol, inst, sysn, col):
    r = d[(d["sample"] == sample) & (d.policy == pol) & (d.inst == inst) & (d.system == sysn)]
    return float(r[col].iloc[0]) if len(r) else np.nan
print("(a) Spread across identification schemes, FULL-S1, u12 (pp per +25 bp)")
print("    system        | funds rate: Chol / proxy-MP1 / proxy-NS  range | 2-year: Chol / proxy-NS / proxy-ED4  range")
for s in SYS:
    a = [get("FULL-S1", "ffr", "MP1", s, "chol_last_12"), get("FULL-S1", "ffr", "MP1", s, "u12"), get("FULL-S1", "ffr", "ns", s, "u12")]
    b = [get("FULL-S1", "gs2", "ns", s, "chol_last_12"), get("FULL-S1", "gs2", "ns", s, "u12"), get("FULL-S1", "gs2", "ED4", s, "u12")]
    print(f"    {s:12s}  | {a[0]:+.2f} / {a[1]:+.2f} / {a[2]:+.2f}   {max(a) - min(a):.2f}         | {b[0]:+.2f} / {b[1]:+.2f} / {b[2]:+.2f}    {max(b) - min(b):.2f}")
print("\n(b) Spread across samples for the Cholesky response (policy ordered last), u12")
print("    system        | funds rate: FULL-S1 / FULL-S2 / CH  range | 2-year: FULL-S1 / FULL-S2  difference")
for s in SYS:
    a = [get("FULL-S1", "ffr", "MP1", s, "chol_last_12"), get("FULL-S2", "ffr", "MP1", s, "chol_last_12"), get("CH", "ffr", "MP1", s, "chol_last_12")]
    b = [get("FULL-S1", "gs2", "ns", s, "chol_last_12"), get("FULL-S2", "gs2", "ns", s, "chol_last_12")]
    print(f"    {s:12s}  | {a[0]:+.2f} / {a[1]:+.2f} / {a[2]:+.2f}   {max(a) - min(a):.2f}          | {b[0]:+.2f} / {b[1]:+.2f}   {abs(b[0] - b[1]):.2f}")
print("\n(c) Spread across samples for the proxy-SVAR with MP1 (funds rate): FULL-S1 / CH window")
for s in SYS:
    a = [get("FULL-S1", "ffr", "MP1", s, "u12"), get("CH", "ffr", "MP1", s, "u12")]
    print(f"    {s:12s}  | {a[0]:+.2f} / {a[1]:+.2f}   difference {abs(a[0] - a[1]):.2f}")
