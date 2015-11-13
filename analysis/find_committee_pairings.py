# Find committees that give to each other.

import json
import sys
import analysis_utils

committee = sys.argv[1]
start_date = sys.argv[2]
end_date = sys.argv[3]

date_range = analysis_utils.days_in_range(start_date, end_date)


# get orgs
orgs = {}
for date in date_range:
	f = open("data/org_defs_{0}.json".format(date))
	for line in f:
		line = json.loads(line)
		value = ''
		if 'COMMITTEE NAME' in line:
			value = line['COMMITTEE NAME']
		elif '5. JOINT FUND PARTICIPANT CMTTE NAME' in line:
			value = line['5. JOINT FUND PARTICIPANT CMTTE NAME']
		elif 'ORGANIZATION NAME' in line:
			value = line['ORGANIZATION NAME'] 
		elif 'PCC COMMITTEE NAME' in line:
			value = line['PCC COMMITTEE NAME'] 

		if not value:
			continue

		value += ' ' + line['FORM TYPE'] 

		if '5. PARTY CODE' in line:
			value += ' (' + line['5. PARTY CODE'] + ')'

		key = ''
		if 'FILER COMMITTEE ID NUMBER' in line:
			key = 'FILER COMMITTEE ID NUMBER'
			value += ' ' + line[key]
		else:
			key = 'FILER CANDIDATE ID NUMBER'
			value += ' ' + line[key]

		orgs[line[key]] = value

print("Finding links to {0}".format(orgs[committee]))
print()


for date in date_range:
    f = open("data/filings_{0}.json".format(date))
    for line in f:
    	if committee in line:
#    		print(line)
    		line = json.loads(line)
    		if "FILER COMMITTEE ID NUMBER" in line and line["FILER COMMITTEE ID NUMBER"] != committee:

    			relationship = analysis_utils.reverse_lookup(line, committee)

    			com = line['FILER COMMITTEE ID NUMBER']

    			prefix = line["FORM TYPE"] + ' ' + relationship + ' for '

    			if 'CONTRIBUTION AGGREGATE{F3L Semi-annual Bundled}' in line:
    				suffix = ' ' + line['CONTRIBUTION AGGREGATE{F3L Semi-annual Bundled}']
    			elif 'EXPENDITURE AMOUNT {F3L Bundled}' in line:
    				suffix = ' ' + line['EXPENDITURE AMOUNT {F3L Bundled}']
    			else:
    				suffix = ''

    			print(prefix + orgs.get(com, com) + suffix)

