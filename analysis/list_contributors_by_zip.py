import json
import sys
import analysis_utils

start_date = sys.argv[1]
end_date = sys.argv[2]
committee = sys.argv[3]

date_range = analysis_utils.days_in_range(start_date, end_date)

exclude_forms = ["F3", "SB", "SD"]

donation_by_state = dict()

for date in date_range:
    f = open("data/filings_{0}.json".format(date))
    for line in f:
        if committee.lower() in line.lower():

            line = json.loads(line)

            if "FORM TYPE" not in line:
                continue


            exclude = False
            for form in exclude_forms:
                exclude = exclude or line["FORM TYPE"].startswith(form)

            if exclude:
                continue

            if "FILER COMMITTEE ID NUMBER" in line and line["FILER COMMITTEE ID NUMBER"] == committee:
                
                key = 'CONTRIBUTION AMOUNT {F3L Bundled}'
                if key in line:
                    amount = line[key]
                else:
                    continue

                state = line["CONTRIBUTOR STATE"]
                city = line["CONTRIBUTOR CITY"]
                zipcode = line["CONTRIBUTOR ZIP"]
                key = "{0},{1},{2}".format(state, city, zipcode)
                if key not in donation_by_state:
                    donation_by_state[key] = 0
                donation_by_state[key] += float(amount)


for k in sorted(donation_by_state.keys()):
    print("{0}, {1}".format(k, donation_by_state[k]))
