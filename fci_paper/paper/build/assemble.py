"""Assemble fci_paper.tex from the head of the current tex (preamble through \\maketitle), the abstract, build/main_v5.tex and build/app_v5.tex."""
from pathlib import Path
B = Path(__file__).parent
cur = (B.parent / "fci_paper.tex").read_text()
head = cur.split("\\begin{abstract}")[0]
abstract = (B / "abstract_v5.tex").read_text()
main = (B / "main_v5.tex").read_text(); app = (B / "app_v5.tex").read_text()
bib = "\n\\bibliographystyle{aea}\n\\bibliography{references}\n\n\\FloatBarrier\n\\newpage\n"
(B.parent / "fci_paper.tex").write_text(head + abstract + main + bib + app + "\n\\end{document}\n")
