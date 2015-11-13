import sys
import analysis_utils
import json

start_date = sys.argv[2]
end_date = sys.argv[3]
election_code = sys.argv[1]

date_range = analysis_utils.days_in_range(start_date, end_date)

key = "ELECTION CODE {was RPTPGI}"

orgs = {}
for date in date_range:
	f = open("data/org_defs_{0}.json".format(date))
	for line in f:
		line = json.loads(line)
		if key in line and line[key] == election_code:
			if 'COMMITTEE NAME' in line:
				print(line['COMMITTEE NAME'] + ' ' + line['FORM TYPE'] + ' ' + line['FILER COMMITTEE ID NUMBER'])
			elif '5. JOINT FUND PARTICIPANT CMTTE NAME' in line:
				print(line['5. JOINT FUND PARTICIPANT CMTTE NAME'] + ' ' + line['FORM TYPE'] + ' ' + line['FILER COMMITTEE ID NUMBER'])
			elif 'ORGANIZATION NAME' in line:
				print(line['ORGANIZATION NAME'] + ' ' + line['FORM TYPE'] + ' ' + line['FILER COMMITTEE ID NUMBER'])
			elif 'PCC COMMITTEE NAME' in line:
				print(line['PCC COMMITTEE NAME'] + ' ' + line['FORM TYPE']+ ' ' + line['FILER CANDIDATE ID NUMBER'])
