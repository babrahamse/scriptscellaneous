import json

worktable = []


with open('input.txt', 'r', encoding='utf8') as f:
    for line in f:
        worktable.append(str(line).strip('\n').split('\t', maxsplit=1))
    f.close()

for count, row in enumerate(worktable):
    row_repl = str(row[1]).replace('\t', ' ')
    worktable[count][1] = row_repl

parsetable = []

for count, row in enumerate(worktable):
    entry_to_add = {'iid': str(count),
                    'oclc_id': row[0],
                    'parsetext': row[1].split(' ')}
    parsetable.append(entry_to_add)


# normalize parsetable entries
for count, row in enumerate(parsetable):
    stripchars = r'();:[]&"'
    replchars = r'.-/,'
    current_parse = row['parsetext']
    new_parse = []
    # print(current_parse)
    for tcount, term in enumerate(current_parse):
        newterm = str(term).lower()
        newterm = newterm.strip()
        x_newterm = ''
        for c in newterm:
            if c in stripchars:
                pass
            elif c in replchars:
                x_newterm += ' '
            else:
                x_newterm += c
            # print(f'old: {newterm} ;  new: {x_newterm}')
        if '  ' in newterm:
            newterm.replace('  ', ' ')

        if ' ' in x_newterm:
            newterm = x_newterm.split(' ')
        else:
            newterm = x_newterm

        if type(newterm) is list:
            for t in newterm:
                new_parse.append(t)
        else:
            new_parse.append(newterm)

    while '' in new_parse:
        new_parse.remove('')

    parsetable[count]['parsetext'] = new_parse

with open('parsetable.json', 'w', encoding='utf8') as f:
    json.dump(parsetable, f)
    f.close()

