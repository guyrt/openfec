# Find committees that give to each other.

import json
import sys
import analysis_utils

start_date = sys.argv[1]
end_date = sys.argv[2]
committee = sys.argv[3]

date_range = analysis_utils.days_in_range(start_date, end_date)


# get orgs
orgs = {}
for date in date_range:
    f = open("data/org_defs_{0}.json".format(date))
    for line in f:
        line = json.loads(line)
        try:
            value = analysis_utils.organization_to_string(line)
            key = analysis_utils.key_for_org(line)
        except analysis_utils.NoNameInLine:
        	continue
        else:
            orgs[line[key]] = value


print("Finding links to {0}".format(orgs[committee]))
print()


for date in date_range:
    f = open("data/filings_{0}.json".format(date))
    for line in f:
        if committee in line:
#            print(line)
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

