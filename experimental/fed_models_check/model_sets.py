"""Set of models used for the alternative scenarios in each Greenbook Part 1 / Tealbook A. Sources within the scenarios section (from its explanatory
sentence to the 'Assessment of Key Macroeconomic Risks' exhibit, at most 60,000 characters): (i) scenario headings tagged with a
model, '[SIGMA]' or '(FRB/US, SIGMA)', anywhere in the document; (ii) sentences that mention a scenario and say it is simulated, generated, run or uses a model.
Hand codes (HAND) for documents whose section the automatic pass cannot parse, each with the text it rests on."""
import re, csv, json
from pathlib import Path
HERE = Path(__file__).resolve().parent; TXT = HERE.parents[1] / "raw" / "fed_txt"
NAMES = {"FRB/US": r"FRB/US", "SIGMA": r"\bSIGMA\b", "EDO": r"\bEDO\b", "GEMUS": r"\bGEMUS\b",
         "NY Fed DSGE (DGS)": r"Del Negro|\bDGS\b|Federal Reserve Bank of New York that|New York DSGE", "Smets-Wouters": r"Smets|\bSW model",
         "Gertler-Karadi": r"Gertler[–-]Karadi|Gertler and Karadi", "Gertler-Sala-Trigari": r"Sala|\bGST\b", "search-matching DSGE": r"search and matching frictions",
         "US-FLM": r"US-FLM", "NK/SIR": r"NK/SIR", "MQS-LM": r"MQS"}
START = ["using simulations of the FRB/US model", "simulations of staff models", "scenarios simulated using", "scenarios are simulated", "scenarios use simulations"]
HAND = json.load(open(HERE / "hand_codes.json")) if (HERE / "hand_codes.json").exists() else {}
out = []
for d in csv.DictReader(open(HERE / "docs.csv")):
    t = (TXT / d["file"].replace(".pdf", ".txt")).read_text(errors="ignore")
    hits = [m.start() for s in START for m in [re.search(r"\s+".join(map(re.escape, s.split())), t)] if m]
    i = min(hits) if hits else -1
    if i < 0:
        seg = ""
    else:
        ends = [m.start() for m in re.finditer(r"Assessment\s+of\s+Key\s+Macroeconomic\s+Risks|ASSESSMENT\s+OF\s+KEY", t) if m.start() > i + 500]
        seg = t[max(0, i - 300):(min(ends) if ends and min(ends) < i + 60000 else i + 40000)]
    flat = re.sub(r"\s+", " ", seg)
    found = set()
    for line in t.splitlines():                                    # scenario headings carry the model tag; read them anywhere in the document
        m = re.search(r"^\s*[A-Z][A-Za-z\-’'/, ]{3,90}[\[(]([^\[\]()]{2,60})[\])]\s*$", line)
        if m:
            for k, p in NAMES.items():
                if re.search(p, m.group(1)): found.add(k)
    for s in re.split(r"(?<=\.)\s", flat):
        if re.search(r"scenario|alternatives? to the baseline|risks to the", s, re.I) and re.search(r"simulat|generat|\brun\b|\buses?\b|using|implemented", s, re.I):
            if re.search(r"stochastic simulations|Confidence Intervals Based on", s, re.I): continue
            for k, p in NAMES.items():
                if re.search(p, s): found.add(k)
    if d["kind"] == "gbpt1" and re.search(r"simulations\s+of\s+the\s+FRB/US\s+model", t):   # Greenbooks: one model for all scenarios, named in the first sentence
        found.add("FRB/US")
    src = "auto"
    if d["meeting"] in HAND:
        found = set(HAND[d["meeting"]]["models"]); src = "hand: " + HAND[d["meeting"]]["text"]
    out.append(dict(year=d["year"], meeting=d["meeting"], kind=d["kind"], n_models=len(found), models="; ".join(sorted(found)), source=src))
with open(HERE / "model_sets.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
for r in out:
    print(r["meeting"], r["kind"][:4], r["n_models"], r["models"])
