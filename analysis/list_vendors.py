import json
import sys
import analysis_utils

start_date = sys.argv[1]
end_date = sys.argv[2]
committee = sys.argv[3]

date_range = analysis_utils.days_in_range(start_date, end_date)

vender_amount = dict()

for date in date_range:
    f = open("data/filings_{0}.json".format(date))
    for line in f:
        if committee.lower() in line.lower():

            line = json.loads(line)

            if "FORM TYPE" not in line or line["FORM TYPE"] != "SB23":
                continue

            if analysis_utils.line_from_org(line, committee):
                
                amount_key = 'EXPENDITURE AMOUNT {F3L Bundled}'
                if amount_key in line:
                    amount = line[amount_key]
                else:
                    continue

                purpose = line["EXPENDITURE PURPOSE DESCRIP"]
                org = line["PAYEE ORGANIZATION NAME"]
                key = "{0},{1}".format(purpose, org)
                if key not in vender_amount:
                    vender_amount[key] = 0
                vender_amount[key] += float(amount)

for k in sorted(vender_amount.keys()):
    print("{0}, {1}".format(k, vender_amount[k]))
