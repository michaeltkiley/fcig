"""Tealbooks 2016-2020: count scenarios by the model tag in their headings ('Recession [FRB/US]', 'EME Turbulence (SIGMA)'). A scenario can name
several models. Writes tealbook_scenarios_2016_2020.csv."""
import re, csv, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent; TXT = HERE.parents[1] / "raw" / "fed_txt"
NAMES = {"FRB/US": r"FRB/US", "SIGMA": r"\bSIGMA\b", "EDO": r"\bEDO\b", "GEMUS": r"\bGEMUS\b", "NY Fed DSGE (DGS)": r"Del Negro|\bDGS\b",
         "Smets-Wouters": r"Smets|\bSW\b", "Gertler-Karadi": r"Gertler[–-]Karadi|Gertler and Karadi", "Gertler-Sala-Trigari": r"Sala|\bGST\b",
         "US-FLM": r"US-FLM", "NK/SIR": r"NK/SIR", "MQS-LM": r"MQS"}
rows = []
for d in csv.DictReader(open(HERE / "docs.csv")):
    if d["kind"] != "tealbooka" or int(d["year"]) < 2016: continue
    seen = {}
    for line in (TXT / d["file"].replace(".pdf", ".txt")).read_text(errors="ignore").splitlines():
        m = re.search(r"^\s*([A-Z][A-Za-z\-’'/, ]{3,90}?)\s*[\[(]([^\[\]()]{2,60})[\])]\s*$", line)
        if m:
            ms = [k for k, p in NAMES.items() if re.search(p, m.group(2))]
            if ms: seen.setdefault(m.group(1).strip(), ms)
    rows += [(d["meeting"], t, ms) for t, ms in seen.items()]
with open(HERE / "tealbook_scenarios_2016_2020.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["meeting", "scenario", "models"]); [w.writerow([a, b, "; ".join(m)]) for a, b, m in rows]
n = len(rows); c = collections.Counter(k for r in rows for k in r[2])
print("Tealbooks with tagged headings:", len({r[0] for r in rows}), "of 40; tagged scenarios:", n)
print("scenarios naming each model:", c.most_common())
print("FRB/US alone:", round(sum(r[2] == ["FRB/US"] for r in rows) / n, 2), "; FRB/US involved:", round(c["FRB/US"] / n, 2))
