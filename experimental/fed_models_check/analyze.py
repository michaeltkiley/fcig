"""For each Greenbook Part 1 / Tealbook A: locate the alternative-scenarios section, record the sentence that names the model(s) used, and count model
names in the section (about 400 lines from the section start) and in the whole document. Text from pdftotext -layout (../../raw/fed_txt/)."""
import re, csv
from pathlib import Path
HERE = Path(__file__).resolve().parent; TXT = HERE.parents[1] / "raw" / "fed_txt"
MODELS = {"FRB/US": r"FRB/US", "SIGMA": r"\bSIGMA\b", "EDO": r"\bEDO\b", "FRB/Global": r"FRB/Global", "DSGE": r"\bDSGE\b",
          "staff models": r"staff(?:'s|’s)? models|models? (?:used|maintained) by the staff|suite of (?:staff )?models", "VAR": r"\bVARs?\b"}
START = re.compile(r"^\s*(Alternative Simulations|ALTERNATIVE SCENARIOS|Alternative Scenarios)\s*$")
docs = list(csv.DictReader(open(HERE / "docs.csv")))
out = []
for d in docs:
    L = (TXT / d["file"].replace(".pdf", ".txt")).read_text(errors="ignore").splitlines()
    full = "\n".join(L)
    # the section start: a heading followed within 6 lines by the explanatory sentence ("simulation" or "construct")
    s0 = None
    for i, l in enumerate(L):
        if START.match(l) and re.search(r"simulation|construct|scenario", " ".join(L[i + 1:i + 8]), re.I):
            s0 = i; break
    sec = "\n".join(L[s0:s0 + 400]) if s0 is not None else ""
    intro = " ".join(x.strip() for x in L[s0 + 1:s0 + 10]) if s0 is not None else ""
    m = re.search(r"[^.]*\b(?:model|models|simulations? of)\b[^.]*\.", intro)
    row = dict(year=d["year"], meeting=d["meeting"], kind=d["kind"], found=s0 is not None, intro_sentence=(m.group(0).strip() if m else intro[:200]))
    for k, p in MODELS.items():
        row[f"sec_{k}"] = len(re.findall(p, sec)); row[f"doc_{k}"] = len(re.findall(p, full))
    out.append(row)
with open(HERE / "model_mentions.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
for r in out:
    print(r["meeting"], r["kind"][:4], r["found"], "|", r["intro_sentence"][:170])
