#!/bin/sh
# about 1 minute; fixed seed. Reads ../../replication/{data,results} and ../data; writes out/ only.
cd "$(dirname "$0")" && python3 run_tests.py 500 > out/run.log 2>&1 && python3 summarize.py > /dev/null
