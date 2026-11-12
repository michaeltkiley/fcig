#!/bin/sh
cd "$(dirname "$0")" && python3 01_paths.py && python3 02_index.py && python3 03_figure.py
