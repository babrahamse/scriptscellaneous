import json
import datetime
end_list = []
now = datetime.datetime.now()
timestamp = datetime.datetime.timestamp(now)

class Log:
    def __init__(self):
        self.log = []
        self.filename = f'log_{timestamp}.txt'
    def upd(self, text):
        # update log
        with open(self.filename, 'a') as f:
            f.write(f'{text}\n')
        f.close()

def detect_date(term):
    l.upd(f'checking for date, term: {term}')
    centuries = ['18', '19', '20']

    if term[0] == 'c':
        term = term[1:]

    try:
        isitaninteger = int(term)
    except:
        l.upd(f'term is not numeric')
        return False

    if len(term) != 4:
        l.upd('term not 4 chars long')
        return False

    if term[0:2] not in centuries:
        l.upd(f'{term[0:2]} does not indicate century')
        return False

    l.upd('this is a valid date')
    return term

def detect_dropwords(term):
    gen_x_rules = (i for i in rules if i[0][0:1] == 'x')
    gen_crit_rules = (i for i in gen_x_rules if i[2][0] == term)
    rule_list = list(gen_crit_rules)
    if len(rule_list) == 0:
        return False
    else:
        for r in rule_list:
            l.upd(r)
        return f'delete {term}'

def detect_term(term, index):
    l.upd('searching term against rules...')
    skip = 0
    gen_rules = (i for i in rules if i[0][0:1] != 'x')
    rule_list = list(i for i in gen_rules if term in i[2])

    def return_term_type(rule):
        if rule[0:1] == 'd':
            return 'dept'
        else:
            return 'degree'

    if rule_list:
        l.upd(rule_list)
        if len(rule_list) == 1:
            l.upd(f'1 rule found for term: {term}')
            l.upd(rule_list[0])
            skip = (len(rule_list[0][2]) - 1)
            l.upd(f'{rule_list[0][1]}')
            return rule_list[0][1], skip, return_term_type(rule_list[0][0])
        else:
            rule_list = list(i for i in rule_list if i[2][0] == term)
            rule_list.sort(key=lambda x: len(x[2]), reverse=True)
            for rule in rule_list:
                l.upd(f'processing rule {count}: {rule}')
                len_to_get_from_parsetext = len(rule[2])
                len_of_new_parse = len(new_parse)
                if (len_to_get_from_parsetext + index) > len_of_new_parse:
                    l.upd('not in the set')
                    continue
                parsetext_snippet = new_parse[index: index + len_to_get_from_parsetext]
                l.upd(f'parsetext reads: {parsetext_snippet}')

                if parsetext_snippet == rule[2]:
                    l.upd('rule matches parsetext')
                    return rule[1], (len_to_get_from_parsetext - 1), return_term_type(rule_list[0][0])
                else:
                    l.upd('rule and parse text do not match')
            else:
                l.upd('no matching rules')
                return False, 0, False
    else:
        l.upd(f'no rules found for term: {term}')
        return False, 0, False


l = Log()
l.upd(f'Log generated {datetime.datetime.now()}\n\n')

#try:
# generate rules
l.upd('loading rulesets... ')
rules = []
rulesets = (
    ('departments', {'filename': 'd_rules.json'}),
    ('degrees', {'filename': 'g_rules.json'}),
    ('dumpfile', {'filename': 'x_rules.json'})
)


for ruleset in rulesets:
    l.upd(f'loading {ruleset[0]}')
    with open(file=ruleset[1]['filename']) as f:
        rules.extend(json.load(f))
    f.close()

# load parsetable
l.upd('load parse table ...')
with open('parsetable.json', 'r', encoding='utf8') as f:
    parsetable = json.load(f)
    f.close()

l.upd(f'parse table loaded: {len(parsetable)} rows.')

output = []


for count, row in enumerate(parsetable):
    print(f'processing record {count}...')
    l.upd(f'\t\tPROCESSING RECORD {count}')
    skip = 0
    l.upd(f'processing row {count} of parse table')
    l.upd(f'data: {row}')

    output_dict = {}
    output_dict.update({'iid': row['iid'], 'oclc_id': row['oclc_id']})
    l.upd(f'adding identifiers: {output_dict}')

    # remove stopwords
    new_parse = list(i for i in row['parsetext'] if not detect_dropwords(i))
    l.upd(f'new parse list: {new_parse}')


    for p_index, parseterm in enumerate(new_parse):
        l.upd(f'processing parse term: {parseterm}')

        if skip > 0:
            skip -= 1
            l.upd(f'skipping {parseterm}')
        else:
            # check for dates
            get_date = detect_date(parseterm)
            if get_date:
                l.upd(f'adding date: "{get_date}"')
                output_dict.update({'date': get_date})
                continue
            else:
                l.upd(f'"{parseterm}" is not a date')

            get_term, skip, termtype = detect_term(parseterm, p_index)

            if get_term:
                l.upd(f'adding {termtype}: {get_term}')
                output_dict.update({termtype: get_term})
                continue
            else:
                l.upd(f'not a {termtype}: {parseterm}')


            l.upd(f'**unrecognized term**: {parseterm}')
            try:
                output_dict['unrecognized'].append(parseterm)
            except KeyError:
                output_dict.update({'unrecognized': [parseterm]})


        l.upd(f'adding data: {output_dict}')
    end_list.append(output_dict)
    output_dict = {}
l.upd(end_list)

with open('parse_results.json', 'w', encoding='utf8') as f:
    json.dump(end_list, f)
    f.close()
#except:
    l.upd(f'process terminated at {datetime.datetime.now()}')
    l.upd(f'last row updated: {count}')

