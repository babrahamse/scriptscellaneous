from oclc_metadata_api_tools import *
import json
import csv

# script begins
search_terms = []
rpile = []
report = []
output = []


def print_and_dump(report, reportname):
    # print report
    reportHeaders = ['term', 'hit', 'score', 'rec_id', 'title', 'publisher', 'pub_year', 'pagination', 'enc_l',
                     'format', 'cat_lang', 'punct_rules', 'cat_rules', 'pcc', 'call_no', 'call_no_count', 'lcsh_count',
                     'rec_timestamp']

    with open(reportname+'.txt', 'w', encoding='utf-8') as f:

        for header in reportHeaders:
            f.write(header)
            f.write('\t')
        f.write('\n')
        for row in report:
            if row['hit'] == -1:
                f.write(row['term'] + '\t' + '<no record found>' + '\t' + str(row['score']) + '\n')
            else:
                dw = csv.DictWriter(f, reportHeaders, delimiter='\t', lineterminator='\n')
                dw.writerow(row)
    f.close()

    # dump as json
    with open(reportname + '.json', 'w') as f:
        json.dump(report, f)
    f.close()


with open('input.txt', 'r') as f:
    for line in f:
        search_terms.append('bn:'+ str(line).replace('\n', ''))

print(search_terms)

for n, s in enumerate(search_terms):
    records = get_records_by_sru(s)
    result = {'term': s, 'hits': len(records),
         'records': ('no records' if len(records) == 0 else {})}

    if len(records) != 0:
        for rec in records:
            rec_id = get_field(rec, '001')
            result['records'].update({rec_id: rec})


    rpile.append(result)

# print(rpile)
with open('rpile.json', 'w') as f:
    json.dump(rpile, f)
f.close()

# generate report from recordpile
report = []
for q in rpile:
    print(q)
    if q['hits'] == 0:
        report.append(
            {'term': q['term'], 'hit': -1, 'score': -99})
    else:
        keys = list(q['records'])
        for count, e in enumerate(keys):
            current_record = q['records'][e]
            report.append({
                'term': q['term'],
                'hit': count,
                'score': 0,
                'rec_id': get_field(current_record, '001'),
                'title': get_field(current_record, '245'),
                'publisher': get_varfield(current_record, '264', 'b'),
                'pub_year': get_fixed_field_value(current_record, '008', 7, 4),
                'pagination': get_varfield(current_record, '300', 'a'),
                'enc_l': str(get_fixed_field_value(current_record, **encl)).replace(' ', '#'),
                'format': str(get_fixed_field_value(current_record, '008', 23, 1)).replace(' ', '#'),
                'cat_lang': get_varfield(current_record, '040', 'b'),
                'punct_rules': str(get_fixed_field_value(current_record, **rules)).replace(' ', '#'),
                'cat_rules': get_varfield(current_record, '040', 'e'),
                'pcc': get_varfield(current_record, '042', 'a'),
                'call_no': get_field(current_record, '050'),
                'call_no_count': count_fields(current_record, '050'),
                'lcsh_count': count_fields(current_record, '6', ' 0'),
                'rec_timestamp': get_fixed_field_value(current_record, '008', 0, 6)
            })

# score report entries
encl_top = ['#', '1', '4', '7', '8']
encl_middle = ['I', 'K', 'L', 'M']
encl_bottom = ['3', 'J']

for count, row in enumerate(report):
    current_score = row['score']

    if current_score == -99:
        pass
    else:
        current_score -= 25 if row['cat_lang'] != 'eng' else 0
        current_score -= 25 if row['format'] != '#' else 0

        current_score += 25 if row['enc_l'] in encl_top and row['pcc'] == 'pcc' else 0
        current_score += 10 if row['enc_l'] in encl_top and row['pcc'] != 'pcc' else 0
        current_score += 5 if row['enc_l'] in encl_middle else 0
        current_score += 1 if row['enc_l'] in encl_bottom else 0

        bad_pagination = ['pages cm', 'pages cm.', '1 volume :']
        current_score -= 15 if row['pagination'] in bad_pagination else 0

        current_score -= 10 if row['lcsh_count'] == 0 else 0
        current_score -= 10 if row['call_no_count'] == 0 else 0
        current_score -= 5 if row['call_no_count'] > 1 else 0

        report[count]['score'] = current_score

# sort report
sortreport = []
for n, s in enumerate(search_terms):
    getrecs = list(i for i in report if i['term'] == s)
    print(getrecs)
    print(len(getrecs))

    if len(getrecs) == 1:
        add_to_sortreport = [getrecs[0]]
    else:
        add_to_sortreport = sorted(getrecs, key=lambda x: x['score'], reverse=True)

    sortreport.extend(add_to_sortreport)

report = sortreport
print_and_dump(report, 'full_rpt')

# get best records
best_records = []
for s in search_terms:
    append = list(i for i in report if i['term'] == s)[0]
    best_records.append(append)

print_and_dump(best_records, 'best_rpt')

