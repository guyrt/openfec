from operator import itemgetter
import json
import sys
import analysis_utils

start_date = sys.argv[1]
end_date = sys.argv[2]
target_state = sys.argv[3]

date_range = analysis_utils.days_in_range(start_date, end_date)

exclude_forms = ["F", "SC/", "SC1/", "SC2/", "SB", "SD", "SE", "SF"] # not contributions. For instance, SE is expendenture, SC/ is loan

donation_by_state = dict()

for date in date_range:
    f = open("data/filings_{0}.json".format(date))
    for line in f:
        if target_state.lower() in line.lower():

            line = json.loads(line)

            if "FORM TYPE" not in line:
                continue

            exclude = False
            for form in exclude_forms:
                exclude = exclude or line["FORM TYPE"].startswith(form)

            if exclude:
                continue

            if "FILER COMMITTEE ID NUMBER" in line:
                try:
                    state = line["CONTRIBUTOR STATE"]
                except:
                    print(line["FORM TYPE"])
                    continue
                if state == target_state:
                    
                    key = 'CONTRIBUTION AMOUNT {F3L Bundled}'
                    if key in line:
                        amount = line[key]
                    else:
                        continue

                    key = line["FILER COMMITTEE ID NUMBER"]

                    if key not in donation_by_state:
                        donation_by_state[key] = 0
                    donation_by_state[key] += float(amount)


for k, v in sorted(donation_by_state.items(), key=itemgetter(1)):
    print("{0}, {1}".format(k, v))
