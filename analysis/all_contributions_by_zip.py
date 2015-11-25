import json
import sys
import analysis_utils

start_date = sys.argv[1]
end_date = sys.argv[2]
target_zip = sys.argv[3]

date_range = analysis_utils.days_in_range(start_date, end_date)

exclude_forms = ["F3", "SB", "SD"]

donation_by_zip = dict()

for date in date_range:
    f = open("data/filings_{0}.json".format(date))
    for line in f:
        if target_zip.lower() in line.lower():

            line = json.loads(line)

            if "FORM TYPE" not in line:
                continue

            exclude = False
            for form in exclude_forms:
                exclude = exclude or line["FORM TYPE"].startswith(form)

            if exclude:
                continue

            zipcode = line["CONTRIBUTOR ZIP"][:5]
            if "FILER COMMITTEE ID NUMBER" in line and zipcode == target_zip:
                
                key = 'CONTRIBUTION AMOUNT {F3L Bundled}'
                if key in line:
                    amount = line[key]
                else:
                    continue

                key = line["FILER COMMITTEE ID NUMBER"]
                if key not in donation_by_zip:
                    donation_by_zip[key] = 0
                donation_by_zip[key] += float(amount)


for k in sorted(donation_by_zip.keys()):
    print("{0}, {1}".format(k, donation_by_zip[k]))
