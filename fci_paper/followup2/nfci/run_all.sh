#!/bin/sh
cd "$(dirname "$0")" && python3 01_joint.py && python3 02_oos.py && python3 03_decomp.py
