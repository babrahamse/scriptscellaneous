import requests as rq
import secrets
import xml.etree.ElementTree as et

marcxmlns = '{http://www.loc.gov/MARC21/slim}'
locns = '{http://www.loc.gov/zing/srw/}'

encl = {'fieldtag': 'ldr', 'v_start': 17, 'v_len': 1}
rules = {'fieldtag': 'ldr', 'v_start': 18, 'v_len': 1}

def replace_escape_chars(search_term):
    print(search_term)
    new_search_term = ''
    escape_characters = ((' ','%20'), ('!','%21'), ('"','%22'), ('#','%23'), ('$','%24'), ('%','%25'), ('&','%26'),
        ("'",'%27'), ('(','%28'), (')','%29'), ('*','%2A'), ('+','%2B'), (',','%2C'), ('-','%2D'), ('.','%2E'),
        (':','%3A'), (';','%3B'), ('<','%3C'), ('=','%3D'), ('>','%3E'), ('?','%3F'), ('@','%40'), ('[','%5B'),
        ('\\','%5C'), (']','%5D'), ('^','%5E'), ('_','%5F'), ('`','%60'), ('{','%7B'), ('|','%7C'), ('}','%7D'),
        ('~','%7E'), (' ','%7F'))
    ec_sig = ''
    for ec in escape_characters:
        ec_sig += ec[0]

    if type(search_term) is not str:
        return 'error: only works with type str'
    for count, char in enumerate(search_term):
        if char in ec_sig:
            for ec_char in escape_characters:
                if ec_char[0] == char:
                    new_search_term += ec_char[1]
                    break
        else:
            new_search_term += char
    print(new_search_term)
    return  new_search_term

def get_records_by_sru(*srus):
    '''docstring
    '''
    output = []
    record_data = []
    search_url = ''
    urls = {'base': 'http://www.worldcat.org/webservices/catalog/search/sru?query=',
            'and': '+and+'}
    search_url += urls['base']
    terms = {'am': ['access method', 'srw.am'], 'au': ['author', 'srw.au'],
             'cn': ['corporate/conference name', 'srw.cn'], 'gn': ['government document number', 'srw.gn'],
             'bn': ['isbn', 'srw.bn'], 'in': ['issn', 'srw.in'], 'kw': ['keyword', 'srw.kw'], 'ln': ['language', 'srw.ln'],
             'lc': ['lc classification number', 'srw.lc'], 'dn': ['lccn', 'srw.dn'],
             'mn': ['music/publisher number', 'srw.mn'], 'nt': ['notes', 'srw.nt'], 'no': ['oclc number', 'srw.no'],
             'pn': ['personal name', 'srw.pn'], 'pl': ['place of publication', 'srw.pl'], 'pb': ['publisher', 'srw.pb'],
             'se': ['series', 'srw.se'], 'sn': ['standard number', 'srw.sn'], 'su': ['subject', 'srw.su'],
             'ti': ['title', 'srw.ti'], 'dd': ['dewey classification number', 'srw.dd'], 'pc': ['dlc only', 'srw.pc'],
             'dt': ['document type (primary)', 'srw.dt'], 'la': ['language code (primary)', 'srw.la'],
             'cg': ['library holdings group', 'srw.cg'], 'li': ['library holdings', 'srw.li'],
             'mt': ['material type', 'srw.mt'], 'on': ['open digital limit', 'srw.on'], 'yr': ['year', 'srw.yr']}

    temp_list = []
    temp_list_sort_key = list(terms)

    for sru in srus:
        user_search_index, search_term = sru.split(':')
        search_index = terms[user_search_index][1] + '+all+'
        search_term_url = replace_escape_chars(search_term)
        search_term_url = '%22' + search_term_url + '%22'
        if search_index[4:6] not in temp_list_sort_key:
            return 'error: invalid sru index'

        temp_list.append([search_index, search_term_url])

    temp_list.sort(key=lambda x : temp_list_sort_key.index(x[0][4:6]))

    for count, query_chunk in enumerate(temp_list):
        if count == 0:
            pass
        else:
            search_url += urls['and']
        search_url += (query_chunk[0] + query_chunk[1])

    search_url += '&maximumRecords=100' \
                  '&servicelevel=full' \
                  '&frbrGrouping=off' \
                  '&wskey=' + secrets.OCLC_keys['search']

    print(search_url)

    results = rq.get(search_url).text
    result_set = et.fromstring(results)

    records = result_set[2]
    for marc_rec in records.iter('{http://www.loc.gov/MARC21/slim}record'):
        output.append(convert_to_majs(marc_rec))

    return output

def get_record(oclc_id):
    submit_URL = ('http://www.worldcat.org/webservices/catalog/content/' + oclc_id + '?wskey=' +
                  secrets.OCLC_keys['meta'])

    results = rq.get(submit_URL).text

    record = et.fromstring(results)

    return record

def convert_to_majs(record):
    converted = []

    for element in record:
        if element.tag == marcxmlns + 'leader':
            converted = [
                {'tag':'ldr',
                 'ind': None,
                 'val': element.text}]
        elif element.tag == marcxmlns + 'controlfield':
            converted.append({'tag': element.attrib['tag'], 'ind': None, 'val': element.text})
        elif element.tag == marcxmlns + 'datafield':
            subf_codes = list(i.attrib['code'] for i in element)
            subf_vals = list(i.text for i in element)

            vals_to_add = []
            for count, each_code in enumerate(subf_codes):
                vals_to_add.append(each_code + subf_vals[count])

            converted.append(
                {'tag': element.attrib['tag'],
                 'ind': (element.attrib['ind1'] + element.attrib['ind2']),
                 'val': vals_to_add}
            )

    return converted

def is_fixed(field):
    if field['ind'] is None:
        return True
    else:
        return False

def get_field(record, field_tag):
    # returns entire field as string, omitting subfield indicators, etc.
    # in case of multiple fields with same tag, returns the first
    out = ''
    try:
        getfield = list(i for i in record if i['tag'] == field_tag)[0]
    except:
        return '<no_field>'

    if is_fixed(getfield) == True:
        out = getfield['val']
    else:
        for n, x in enumerate(getfield['val']):
            out += (x[1:] if n == 0 else (' '+x[1:]))

    return out

def get_fixed_field_value(record, fieldtag, v_start, v_len):
    field_val = list(i for i in record if i['tag'] == fieldtag)[0]
    print(field_val)
    if field_val == False:
        raise Exception('field does not exist')
    if is_fixed(field_val) == False:
        raise Exception('not a fixed field')

    return field_val['val'][v_start:(v_start + v_len)]

def get_varfield(record, field_tag, sf_tag):
    # returns val of first instance of field/subfield as a str
    getfield = (i for i in record if i['tag'] == field_tag)
    try:
        field = list(getfield)[0]
    except:
        out = '<no_field>'
        return out

    getsfield = (i[1:] for i in field['val'] if i[0] == sf_tag)
    try:
        out = list(getsfield)[0]
    except:
        out = '<no_subfield>'
        return out

    return out

def count_fields(record, field_tag, ind=None):
    # returns a int count of all fields that match criteria
    count = 0
    tags_to_search = []
    tag_to_add = field_tag
    if len(tag_to_add) == 3:
        tags_to_search.append(tag_to_add)
    elif len(tag_to_add) == 2:
        for n in range(0, 10):
            new_tag = tag_to_add
            new_tag += str(n)
            tags_to_search.append(new_tag)
    elif len(tag_to_add) == 1:
        for n in range(0, 10):
            new_tag = tag_to_add
            new_tag += str(n)
            for o in range(0, 10):
                new_tag += str(o)
                tags_to_search.append(new_tag)
                new_tag = new_tag[0:2]

    for tag in tags_to_search:
        if ind == None:
            count += len(list(i for i in record if i['tag'] == tag))
        else:
            count += len(list(i for i in record if i['tag'] == tag and i['ind'] == ind))

    return count
