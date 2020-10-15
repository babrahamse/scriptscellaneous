import json
import csv

rules_filename = 'parse_results.json'
out_filename = 'parse_results.txt'
with open(rules_filename, 'r') as f:
    table = json.load(f)
    f.close()

headers = ['iid', 'oclc_id', 'date', 'dept', 'degree', 'unrecognized']

print(table)
with open(out_filename, 'w', encoding='utf8') as f:
    w = csv.DictWriter(f, headers, restval='*no term found*', delimiter='\t', lineterminator='\n')
    w.writeheader()
    w.writerows(table)
