
# id.loc harvester script
# takes terms, searches id.loc
# converts results into json
# v.0.1 2019-11-10
# by ben abrahamse, (c)2019 mit libraries
import requests as r
import xml.etree.ElementTree as et
import json
from fuzzywuzzy import fuzz as fz

filepath = 'C:/Users/babraham/Desktop/python data files/'  # set your local filepath here
inputfile = filepath + 'input.txt'  # name of input file


ns_xhtml = '{http://www.w3.org/1999/xhtml}'

# load search_terms from file

search_terms = []
with open(inputfile, 'r') as f:
    for line in f:
        search_terms.append(line.replace('\n', ''))
    f.close()

# main loop
# loop through search_terms[] and for each, query id.loc, process results & append to output.json
#
output = []  # [{'search': '', 'results': [{'heading': '', 'uri': '', 'match': 0}]}]
best_output = []  # [{'search': '', 'heading': '', 'uri': '']

for term in search_terms:
    output.append({'search': term, 'results': []})
    term_url_string = term.replace(' ', '+')
    term_url = 'http://id.loc.gov/search/?q=' + term_url_string + '&q=cs%3Ahttp%3A%2F%2Fid.loc.gov%2Fauthorities%2Fnames'

    results = r.get(term_url)
    results_text = results.text
    tree = et.fromstring(results_text)

    treelist = tree.iter(tag=(ns_xhtml + 'body'))
    for element in treelist:
        subtreelist = element.iter(tag = (ns_xhtml + 'a'))
        for subelement in subtreelist:
            i = subelement.get('title')
            if i != False:
                if i == 'Click to view record':
                    output[-1]['results'].append({
                        'heading': subelement.text,
                        'uri': subelement.attrib['href'],
                        'match': fz.ratio(term, subelement.text)})

for search in output:
    search['results'] = sorted(search['results'], key=lambda x : x['match'], reverse=True)
    try:
        best_output.append(
            {'search': search['search'],
             'heading': search['results'][0]['heading'],
             'uri': search['results'][0]['uri']})
    except:
        best_output.append({'search': search['search'],
        'heading': '<no record found>', 'uri': '<no record found>'})

with open(filepath+'best_output.txt', 'w') as f:
    for row in best_output:
        for key in row:
            f.write(row[key])
            f.write('\t')
        f.write('\n')
f.close()

with open(filepath+'best_output.json', 'w') as f:
        json.dump(best_output, f)
f.close()

with open(filepath+'output.json', 'w') as f:
    json.dump(output, f)
f.close()