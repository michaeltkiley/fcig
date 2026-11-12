#!/bin/sh
# Rerun: about 4 minutes on 4 cores. Writes only out/.
cd "$(dirname "$0")" && export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python 01_var.py && python 02_levelflow.py && python 03_stance.py && python 04_ladder.py && python 05_table.py
