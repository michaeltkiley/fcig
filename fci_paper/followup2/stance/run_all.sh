#!/bin/sh
# Rerun: ~2 minutes. Writes only out/.
cd "$(dirname "$0")" && export PYTHONDONTWRITEBYTECODE=1
python 01_corr.py && python 02_insample_oos.py && python 03_episodes.py && python 04_episode_rank.py && python 05_components.py
