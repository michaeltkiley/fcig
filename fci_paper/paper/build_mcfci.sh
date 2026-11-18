#!/bin/sh
# Build the new version (MCFCI paper): pdflatex, bibtex, pdflatex twice (reads ../replication/report/).
cd "$(dirname "$0")" && pdflatex -interaction=nonstopmode mcfci.tex && bibtex mcfci && pdflatex -interaction=nonstopmode mcfci.tex && pdflatex -interaction=nonstopmode mcfci.tex
