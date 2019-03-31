# oclc apis
# a quick library for working with these apis
#
import secrets
import bs4 as soup
import requests as rq

def get_oclc_ids_from_search(search_term):
    oclc_ids = []
    submit_URL = ('http://www.worldcat.org/webservices/catalog/search/worldcat/opensearch?q=' +
                  search_term + '&count=100&wskey=' + secrets.OCLC_keys['search'])
    results = rq.get(submit_URL).text
    record = soup.BeautifulSoup(results)
    entries = record.findAll('entry')
    print('number of results=' + str(len(entries)))
    for count, entry in enumerate(entries):
        oclc_ids.append(entry.link['href'].split('/')[-1])
    return oclc_ids

def convert_marcxml_record_to_dict(marcxml_record, dictionary_label):
    # assemble fixed fields entries
    ffields = marcxml_record.findAll('controlfield')
    fixed_fields = {}

    # add LDR
    leader = marcxml_record.find('leader').text
    fixed_fields['ldr'] = leader

    for ffield in ffields:
            field_tag = ffield['tag']
            field_val = ffield.text
            fixed_fields.update({field_tag: field_val})

    # assemble variable fields entries
    tag_list = []
    variable_fields = {}
    current_variable_field = {}
    varfields = marcxml_record.findAll('datafield')

    for varfield in varfields:
        field_tag = varfield['tag']
        if field_tag in tag_list:
            n = 2
            new_field_tag = field_tag + '_' + str(n)
            while new_field_tag in tag_list:
                n += 1
                new_field_tag = new_field_tag[:-len(str(n-1))] + str(n)
            tag_list.append(new_field_tag)
            print(new_field_tag)
            field_tag = new_field_tag
        else:
            tag_list.append(field_tag)

        indicators = varfield['ind1'] + varfield['ind2']

        # get subfield values
        subfields = {}
        code_list = []
        for subfield in varfield:
            if subfield != '\n': # for some reason we are getting blank values in the iterator
                sfield_tag = subfield['code']
                sfield_val = subfield.string

                if sfield_tag in code_list:
                    n = 2
                    new_sfield_tag = sfield_tag + '_' + str(n)
                    while new_sfield_tag in code_list:
                        n += 1
                        new_sfield_tag = new_sfield_tag[:-len(str(n-1))] + str(n)
                    code_list.append(new_sfield_tag)
                    sfield_tag = new_sfield_tag
                else:
                    code_list.append(sfield_tag)
                subfields[sfield_tag] = sfield_val
        print(subfields)
        current_variable_field = {field_tag: {'indicators':indicators}}
        current_variable_field[field_tag].update(subfields)
        variable_fields.update(current_variable_field)

    output = {}
    output.update({'record_'+str(dictionary_label): {'fixed_fields': fixed_fields, 'variable_fields': variable_fields}})
    return output

def get_record(oclc_id):
    submit_URL = ('http://www.worldcat.org/webservices/catalog/content/' + oclc_id + '?wskey=' +
                  secrets.OCLC_keys['meta'])
    print(submit_URL)
    results = rq.get(submit_URL).text
    record = soup.BeautifulSoup(results)
    if record == True:
        print('Record retrieved.')
    return record

def get_from_variable(record, fieldtag, sfieldtag, repl_spaces = False, repl_space_char = '/'):
    output = '' # data in the field/subfield
    multiple_treatment = ('c','f')
    key = list(record)[0]

    try:
        if sfieldtag == '*':
            values = list(record[key]['variable_fields'][fieldtag])
            for sftag in values[1:]: # skip indicators in position 0
                output += (' ' + record[key]['variable_fields'][fieldtag][sftag])
                output = output.lstrip()
        else:
            if sfieldtag in ['\i','ind','indicators']:
                sfieldtag = 'indicators'
            output = record[key]['variable_fields'][fieldtag][sfieldtag]
    except KeyError:
        output = 'field not present'
        return output

    if repl_spaces == True:
        output = output.replace(' ', repl_space_char)
    return output

def record_report(record, report_format = 'c'):
    # prints to console a report of the record
    key = list(record)[0]
    ff_keys = list(record[key]['fixed_fields'])
    v_keys = list(record[key]['variable_fields'])
    if report_format == 'c':
        print('fields in record: ')
        print(key)
        print(ff_keys)
        print(v_keys)
    elif report_format == 'd':
        output = {}
        output['record_id'] = key
        output['fixed_fields'] = ff_keys
        output['variable_fields'] = v_keys
        return output

def get_from_fixed(record, fieldtag, start = 0, length = -1, repl_space = False, repl_space_char = '/'):
    output = '' # data in the fixed field
    try:
        key = list(record)[0]
        base_string = record[key]['fixed_fields'][fieldtag]
        if length == -1:
            length = len(base_string)
        output = base_string[start:(start + length)]
    except KeyError:
        output = 'field not present'
    return output

