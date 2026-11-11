"""Real-time Laubach-Williams r*: final data point of the one-sided column in each quarterly vintage of the NY Fed real-time file.
Usage: python 02_lw_realtime.py <path to Laubach_Williams_real_time_estimates.xlsx>  (downloaded from newyorkfed.org/research/policy/rstar)"""
import sys, re, pandas as pd
x = pd.ExcelFile(sys.argv[1]); rows = []
for s in x.sheet_names:
    if s == "LW Estimates": continue
    d = x.parse(s, header=None)
    txt = " ".join(str(v) for v in d.iloc[:4, 0].dropna())
    m = re.search(r"available on ([A-Za-z]+ \d+, \d{4})", txt)
    h = d.index[d[0].astype(str).str.strip() == "Date"][0]
    hdr = [str(v).strip() for v in d.iloc[h]]; j = hdr.index("rstar")
    body = d.iloc[h + 1:].dropna(subset=[0]); body = body[pd.to_datetime(body[0], errors="coerce").notna()]
    last = body.iloc[-1]
    rows.append(dict(vintage=s, release=pd.to_datetime(m.group(1)) if m else pd.NaT, final_obs=pd.to_datetime(last[0]).to_period("Q"),
                     rstar_rt=float(last[j]), rstar_lastvintage_for_obs=None))
R = pd.DataFrame(rows); R.to_csv("out/lw_realtime.csv", index=False); print(R.to_string())
