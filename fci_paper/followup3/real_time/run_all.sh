#!/bin/sh
# needs network for steps 1-2: ALFRED (alfredgraph.csv, one vintage per call) and the NY Fed real-time LW file
set -e; cd "$(dirname "$0")"
python3 01_fetch.py                                   # raw/ (gitignored)
curl -sS --http1.1 -m 120 -L -o raw/lw_rt.xlsx https://www.newyorkfed.org/medialibrary/media/research/economists/williams/data/Laubach_Williams_real_time_estimates.xlsx
python3 02_lw_realtime.py raw/lw_rt.xlsx > /dev/null
python3 03_build_rt.py > /dev/null; python3 04_run.py > /dev/null; python3 05_summarise.py
