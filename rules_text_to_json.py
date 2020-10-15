# converts rules saved as a tab-delimited text file to JSON rules for ts-parser
import json
import csv

in_filename = 'd_rules.txt'
out_filename = 'd_rules.json'
intable = []
outtable = []
with open(in_filename, 'r', encoding='utf8') as f:
    r = csv.reader(f, delimiter='\t')
    for row in r:
        intable.append(row)
    f.close()

print(intable)

for row in intable:
    row_to_append = (row[0:2])
    row_to_append.append(list(row[2:]))
    outtable.append(row_to_append)

print(outtable)

with open(out_filename, 'w', encoding='utf8') as f:
    json.dump(outtable, f)
    f.close()

