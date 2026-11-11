"""House LaTeX style of the author's FOMC papers (fomc_evolution/PaperV3/paper/draft5_revised.tex), applied to the generated table files:
floats placed [tp], Title Case captions, notes under the table as \\begin{flushleft}\\footnotesize\\textit{Notes:} ...\\end{flushleft}. Idempotent."""
import re
from pathlib import Path

SMALL = {"a", "an", "the", "and", "but", "or", "nor", "for", "of", "on", "in", "to", "at", "by", "with", "from", "as", "vs", "vs.", "via", "per", "than", "that", "after", "into", "without", "when", "is"}

def title_case(s):
    """Title Case with lower-case function words; tokens containing math, commands, digits-with-symbols or capitals inside are left alone."""
    toks = re.split(r"(\s+)", s); out = []; first = True; prev_colon = False
    for tk in toks:
        if tk.isspace() or not tk: out.append(tk); continue
        core = re.sub(r"^[(\[`']+", "", tk); lead = tk[:len(tk) - len(core)]
        if any(c in core for c in "$\\^{}*") or (core[1:] != core[1:].lower()) or not re.search(r"[A-Za-z]", core): new = tk
        elif core.lower().rstrip(",.;:)") in SMALL and not first and not prev_colon: new = lead + core.lower()
        else: new = lead + "-".join((q[0].upper() + q[1:]) if q and q.lower() not in SMALL else q for q in core.split("-"))
        out.append(new); first = False; prev_colon = tk.endswith(":")
    return "".join(out)

def match_brace(s, i):
    """Index of the brace closing the one opened at s[i] == '{'."""
    d = 0
    for j in range(i, len(s)):
        if s[j] == "{": d += 1
        elif s[j] == "}":
            d -= 1
            if d == 0: return j
    raise ValueError("unbalanced")

def restyle(text):
    text = re.sub(r"\\begin\{table\}\[[a-zA-Z!]*\]", r"\\begin{table}[tp]", text)
    m = re.search(r"\\caption\{", text)
    if m:
        a = m.end() - 1; b = match_brace(text, a); text = text[:a + 1] + title_case(text[a + 1:b]) + text[b:]
    pat = r"\par\smallskip\parbox{"
    while pat in text:
        i = text.index(pat); j = text.index("{", i + len(pat) - 1)               # the width brace was opened inside pat; find the body brace after it
        w_end = match_brace(text, i + len(pat) - 1); k = text.index("{", w_end); e = match_brace(text, k)
        body = text[k + 1:e]; body = re.sub(r"^\s*\\scriptsize\s*", "", body)
        text = text[:i] + r"\begin{flushleft}\footnotesize\textit{Notes:} " + body.strip() + r"\end{flushleft}" + text[e + 1:]
    return text

def restyle_dir(d):
    for f in sorted(Path(d).glob("tab_*.tex")): f.write_text(restyle(f.read_text()))
