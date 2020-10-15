import json
import csv
intable = []
outtable = []

rules_filename = 'd_rules.json'
out_filename = 'd_rules.txt'
with open(rules_filename, 'r') as f:
    intable = json.load(f)
f.close()

print(intable)

for row in intable:
    row_to_append = []
    row_to_append = row[0:2]
    for item in row[2]:
        row_to_append.append(item)
    print(row_to_append)
    outtable.append(row_to_append)

print(outtable)
with open(out_filename, 'w', encoding='utf8') as f:
    w = csv.writer(f, delimiter='\t', lineterminator='\n')
    w.writerows(outtable)
f.close()


