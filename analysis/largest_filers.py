import sys
import analysis_utils
import json

start_date = sys.argv[1]
end_date = sys.argv[2]

date_range = analysis_utils.days_in_range(start_date, end_date)

orgs = {}

contributions = []

for date in date_range:
	f = open("data/org_defs_{0}.json".format(date))
	for line in f:
		line = json.loads(line)
		
		name = ''
		if 'COMMITTEE NAME' in line:
			name = line['COMMITTEE NAME'] + ' ' + line['FORM TYPE'] + ' ' + line['FILER COMMITTEE ID NUMBER']
		elif '5. JOINT FUND PARTICIPANT CMTTE NAME' in line:
			name = line['5. JOINT FUND PARTICIPANT CMTTE NAME'] + ' ' + line['FORM TYPE'] + ' ' + line['FILER COMMITTEE ID NUMBER']
		elif 'ORGANIZATION NAME' in line:
			name = line['ORGANIZATION NAME'] + ' ' + line['FORM TYPE'] + ' ' + line['FILER COMMITTEE ID NUMBER']
		elif 'PCC COMMITTEE NAME' in line:
			name = line['PCC COMMITTEE NAME'] + ' ' + line['FORM TYPE']+ ' ' + line['FILER CANDIDATE ID NUMBER']

		if not name:
			continue

		if '17(e) Total Contributions' in line:
			contributions.append([float(line['17(e) Total Contributions']), name])

for line in sorted(contributions):
	print("{1} {0}".format(*line))
