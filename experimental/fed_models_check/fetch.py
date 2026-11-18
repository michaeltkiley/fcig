"""Download the staff forecast documents for every scheduled FOMC meeting, 2006-2010 and 2016-2020: Greenbook Part 1 (to April 2010) and Tealbook A
(from June 2010), from the Board's historical-materials pages. PDFs go to ../../raw/fed_docs/ (gitignored); the list to docs.csv."""
import re, subprocess, csv
from pathlib import Path
HERE = Path(__file__).resolve().parent; RAW = HERE.parents[1] / "raw" / "fed_docs"; RAW.mkdir(parents=True, exist_ok=True)
BASE = "https://www.federalreserve.gov"
rows = []
for y in list(range(2006, 2011)) + list(range(2016, 2021)):
    html = subprocess.run(["curl", "-sS", "-m", "60", f"{BASE}/monetarypolicy/fomchistorical{y}.htm"], capture_output=True, text=True).stdout
    links = sorted(set(re.findall(r'href="(/monetarypolicy/files/FOMC(\d{8})(gbpt1|tealbooka)\d{8}\.pdf)"', html, flags=re.I)))
    for path, meet, kind in links:
        out = RAW / Path(path).name
        if not out.exists():
            subprocess.run(["curl", "-sS", "-m", "120", "-o", str(out), BASE + path], check=True)
        rows.append(dict(year=y, meeting=meet, kind=kind.lower(), file=out.name, url=BASE + path))
    print(y, len(links))
with open(HERE / "docs.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
