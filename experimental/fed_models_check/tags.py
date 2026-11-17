"""Tealbook A scenarios carry the model in their title, e.g. 'Global Market Correction [SIGMA]'. Count the tagged scenario titles by model for every
Tealbook (June 2010 on); Greenbooks (to April 2010) state one model for all scenarios in the section's first sentence (see model_mentions.csv)."""
import re, csv
from pathlib import Path
from collections import Counter
HERE = Path(__file__).resolve().parent; TXT = HERE.parents[1] / "raw" / "fed_txt"
TAG = re.compile(r"^\s{0,30}([A-Z][^\[\]]{3,90}?)\s*\[([A-Za-z/\-0-9 ,&]+(?:\s*(?:and|,)\s*[A-Za-z/\-0-9 ]+)*)\]\s*$")
rows = []
for d in csv.DictReader(open(HERE / "docs.csv")):
    if d["kind"] != "tealbooka": continue
    L = (TXT / d["file"].replace(".pdf", ".txt")).read_text(errors="ignore").splitlines()
    seen = {}
    for l in L:
        m = TAG.match(l)
        if m and not re.search(r"percent|Percent|\d{4}", m.group(1)):
            seen.setdefault(m.group(1).strip(), m.group(2).strip())
    for title, model in seen.items():
        rows.append(dict(year=d["year"], meeting=d["meeting"], scenario=title, model=model))
with open(HERE / "tealbook_scenarios.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["year", "meeting", "scenario", "model"]); w.writeheader(); w.writerows(rows)
c = Counter(r["model"] for r in rows if int(r["year"]) >= 2016); print("2016-20 scenarios by model tag:", c.most_common(), "total", sum(c.values()))
c10 = Counter(r["model"] for r in rows if int(r["year"]) == 2010); print("2010 Tealbooks:", c10.most_common())
per = Counter(r["meeting"] for r in rows); print("meetings with tags:", len(per), "of", sum(1 for d in csv.DictReader(open(HERE / 'docs.csv')) if d['kind']=='tealbooka'))
