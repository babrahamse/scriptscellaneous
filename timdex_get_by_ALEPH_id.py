# import
import pytimdex as pt
import csv
import secrets as s

# open file & build id list:
def read_file(filename='input.txt'):
    file_contents = []
    with open(filename, 'r') as f:
        read = csv.reader(f, delimiter='\t')
        for row in read:
            file_contents.append(row)
    return file_contents

def write_to_file(filename, table_to_write):
    with open(filename, 'w', encoding='latin-1')as f:
        write = csv.writer(f, delimiter='\t', lineterminator='\n')
        write.writerows(table_to_write)
    return True



def try_to_add(record, output_field):
    print(record)
    try:
        if type(output_field) is str:
            out = record[output_field]

        elif type(output_field) is list:

            field_len = len(output_field)

            if field_len == 2:
                out = record[output_field[0]][output_field[1]]

            elif field_len == 3:
                print(output_field)
                out = record[output_field[0]][output_field[1]][output_field[2]]
                print(out)
            else:
                out = 'invalid field request'
    except KeyError:
            out = (
                (output_field if type(output_field) is str else output_field[0])
                + ' not in record'
            )

    out = pt.strip_final_punct(out)
    return out

# script begins
#
ids = read_file()
print(ids)

# create td object
token = pt.authenticate(**s.timdex_keys)
q = pt.query(token)
print(q)

# get records
for id in ids:
    q.get(id, 'a')
print(q.results)

# go through results & add relevant fields to output table
#
output_table = []
output_fields = ['id', 'source_link', 'title', ['imprint',0], ['isbns', 0], ['contributors', 0, 'value'], 'physical_description']
for record in q.results:
    row_to_add = []
    for field in output_fields:
        row_to_add.append(try_to_add(record, field))
    output_table.append(row_to_add)

bool = write_to_file('output.txt', output_table)
print(bool)

