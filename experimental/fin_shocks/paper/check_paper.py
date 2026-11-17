"""Sync check for a Note B draft without a TeX engine: every number macro resolves, every \\input exists, every \\ref has a \\label, every citation key is in references.bib.
   python3 check_paper.py [mp_transmission_session_integration.tex]     (exit status 1 if anything is missing)"""
import re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
tex = HERE / (sys.argv[1] if len(sys.argv) > 1 else "mp_transmission_session_integration.tex"); src = tex.read_text()
body = re.sub(r"(?<!\\)%.*", "", src)                                                  # drop comments
inputs = re.findall(r"\\input\{([^}]+)\}", body); bad = []
files = {}
for f in inputs:
    p = (HERE / f).with_suffix(".tex") if not f.endswith(".tex") else HERE / f
    if not p.exists(): bad.append(f"missing input: {f}")
    else: files[f] = p.read_text()
defined = set()
for t in files.values(): defined |= set(re.findall(r"\\csname (bl[a-z]*:[^\\]+)\\endcsname", t))
used = re.findall(r"\\(bl|blabs|bllo|blhi|blsig)\{([^}]+)\}", body + "".join(t for f, t in files.items() if "numbers" not in f))
for cmd, key in used:
    if f"{cmd}:{key}" not in defined: bad.append(f"undefined macro: \\{cmd}{{{key}}}")
alltext = body + "".join(files.values())
labels = set(re.findall(r"\\label\{([^}]+)\}", alltext))
for r in set(re.findall(r"\\(?:ref|eqref)\{([^}]+)\}", alltext)):
    if r not in labels: bad.append(f"undefined reference: {r}")
bib = (HERE / "references.bib").read_text(); keys = set(re.findall(r"@\w+\{([^,\s]+),", bib))
for grp in re.findall(r"\\cite[a-z]*\*?(?:\[[^\]]*\])*\{([^}]+)\}", alltext):
    for k in grp.split(","):
        if k.strip() not in keys: bad.append(f"citation not in references.bib: {k.strip()}")
for f in re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", body):
    if not (HERE / f).exists(): bad.append(f"missing figure: {f}")
print(f"{tex.name}: {len(used)} macro uses, {len(inputs)} inputs, {len(labels)} labels; {len(sorted(set(bad)))} problems")
for b in sorted(set(bad)): print("  ", b)
sys.exit(1 if bad else 0)
