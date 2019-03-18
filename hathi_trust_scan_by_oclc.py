'''
Hathi Trust scan by OCLC
v.1
(c)2019 MIT Libraries

Given a file of OCLC numbers, queries Hathi Trust for matching copy. Returns URL and US rights statement as dict object.
Prints to file.

'''

import datetime as d
import requests as r

filename = 'output.txt'

def new_output_file(filename):
    with open(filename,'w') as f:
        write_to_file('Hathi report ' + str(d.datetime.now()),filename)
        write_to_file(['oclc', 'hathi status', 'url', 'rights'],filename)

def write_to_file(input, filename):
    with open(filename,'a') as f:
        if type(input) is list:
            for item in input:
                f.write(item)
                f.write('\t')
            f.write('\n')
        elif type(input) is dict:
            for key in input:
                f.write(key)
                f.write('\t')
                f.write(input[key]['status'])
                f.write('\t')
                f.write(input[key]['url'])
                f.write('\t')
                f.write(input[key]['rights'])
                f.write('\n')
        else:
            f.write(str(input))
            f.write('\n')
    f.close()


oclc_list = []
with open('input.txt','r') as f:
    for line in f:
        line_to_add = line.replace('\n','')
        oclc_list.append(line_to_add)
print(oclc_list)
f.close()

output = {}
submit_URL = lambda input : 'https://catalog.hathitrust.org/api/volumes/brief/oclc/' + input + '.json'
new_output_file(filename)

for count, row in enumerate(oclc_list):
    print('checking record ' + str(count) + ': '+row)
    entry_to_add = {}
    entry_to_add.update({row:{}})
    try:
        response = r.get(submit_URL(row)).json()
    except:
        response={'records':{}}
    if response['records'] == {}:
        entry_to_add[row].update({'status':'not in Hathi','url':'n/a','rights':'n/a'})
        print(entry_to_add)
    else:

        record_id = list(response['records'])[0]
        hathi_url = response['records'][record_id]['recordURL']
        hathi_rights = response['items'][0]['usRightsString']
        entry_to_add[row].update({'status':'in Hathi','url':hathi_url,'rights':hathi_rights})
        print(entry_to_add)
    output.update(entry_to_add)
    if (count % 100) == 0:
        print('writing to file ...')
        write_to_file(output,filename)
        output.clear()
write_to_file(output,filename)













