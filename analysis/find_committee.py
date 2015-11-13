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
		if 'COMMITTEE NAME' in line:
			orgs[line['FILER COMMITTEE ID NUMBER']] = 'COMMITTEE NAME ' + line['COMMITTEE NAME'] + ' ' + line['FORM TYPE'] + ' ' + line['FILER COMMITTEE ID NUMBER']
		elif '5. JOINT FUND PARTICIPANT CMTTE NAME' in line:
			orgs[line['FILER COMMITTEE ID NUMBER']] = 'JOINT FUND PARTICIPANT CMTTE NAME ' + line['5. JOINT FUND PARTICIPANT CMTTE NAME'] + ' ' + line['FORM TYPE'] + ' ' + line['FILER COMMITTEE ID NUMBER']
		elif 'ORGANIZATION NAME' in line:
			orgs[line['FILER COMMITTEE ID NUMBER']] = 'ORGANIZATION NAME ' + line['ORGANIZATION NAME'] + ' ' + line['FORM TYPE'] + ' ' + line['FILER COMMITTEE ID NUMBER']
		elif 'PCC COMMITTEE NAME' in line:
			orgs[line['FILER CANDIDATE ID NUMBER']] = 'PCC COMMITTEE NAME ' + line['PCC COMMITTEE NAME'] + ' ' + line['FORM TYPE']+ ' ' + line['FILER CANDIDATE ID NUMBER']


for date in date_range:
    f = open("data/filings_{0}.json".format(date))
    for line in f:
    	if committee in line:
#    		print(line)
    		line = json.loads(line)
    		if "FILER COMMITTEE ID NUMBER" in line and line["FILER COMMITTEE ID NUMBER"] != committee:
    			com = line['FILER COMMITTEE ID NUMBER']
    			print(orgs.get(com, com) + ' ' + line['CONTRIBUTION AGGREGATE{F3L Semi-annual Bundled}'])

