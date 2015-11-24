#!/bin/bash

# Sort the files
sort -o pterms.txt pterms.txt
sort -o rterms.txt rterms.txt
sort -o scores.txt scores.txt

# format the output files
python3 formatting.py reviews.txt rw.txt
python3 formatting.py pterms.txt pt.txt
python3 formatting.py rterms.txt rt.txt
python3 formatting.py scores.txt sc.txt

# Build the index files using appropriate indices
db_load -T -c duplicates=1 -t hash -f rw.txt rw.idx
db_load -T -c duplicates=1 -t btree -f pt.txt pt.idx
db_load -T -c duplicates=1 -t btree -f rt.txt rt.idx
db_load -T -c duplicates=1 -t btree -f sc.txt sc.idx
