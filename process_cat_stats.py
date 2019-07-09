import json

# load data from file
data_file = '2019_production.json'
write_file = 'output.txt'

with open(data_file, 'r') as f:
    raw_stats = json.load(f)
f.close()

# create output table
output_table = []
output_table.append([])
template = [
    ['!', 'barton_id', 'str'], ['a', 'cat_signature', 'str'], ['d', 'cat_date', 'str'], ['i', 'cat_name'],
    ['b', 'cat_action', 'str'], ['c', 'local_action', 'str'], ['e', 'cat_project', 'str'], ['j', 'rec_type', 'str'],
    ['k', 'rec_bibLvl', 'str'], ['l', 'rec_format', 'str'], ['m', 'rec_encl', 'str'], ['o', 'rec_rules', 'str'],
    ['p', 'rec_origin', 'str'], ['q', 'pc_coll', 'str'], ['r', 'pc_format', 'str'], ['s', 'pc_count', 'int'],
    ['w', 'pcadd_format', 'str'], ['x', 'pccadd_count', 'ind'], ['z', 'cat_notes', 'str']
            ]

for item in template:
    output_table[0].append(item[1])


for curr_rec in raw_stats['rows']:
    row_to_append = [None] * len(template)
    # print(row_to_append)
    for curr_col in curr_rec:
        curr_val = curr_rec[curr_col]
        if curr_val == 'None':
            pass
        else:
            if str(curr_val)[0] == '0':
                row_to_append[0] = curr_val
            elif str(curr_val)[0] == '[':
                sf = curr_val[1]
                for count, i in enumerate(template):
                    if sf == i[0]:
                        row_to_append[count] = curr_val[4:]
    output_table.append(row_to_append)

# write to output file
with open(write_file, 'w') as f:
    for row in output_table:
        for col in row:
            if type(col) is str:
                f.write(col + '\t')
            else:
                f.write('\t')
        f.write('\n')
    f.close()
