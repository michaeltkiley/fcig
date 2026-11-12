#!/bin/sh
# Build the paper: pdflatex, bibtex, pdflatex twice (reads ../replication/report/).
cd "$(dirname "$0")" && pdflatex -interaction=nonstopmode fci_paper.tex && bibtex fci_paper && pdflatex -interaction=nonstopmode fci_paper.tex && pdflatex -interaction=nonstopmode fci_paper.tex
