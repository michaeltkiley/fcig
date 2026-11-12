#!/bin/sh
set -e
cd "$(dirname "$0")"
python3 01_stability.py
python3 01b_var.py
python3 02_unit_restriction.py
python3 03_neutrality.py
