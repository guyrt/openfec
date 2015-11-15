import json
import sys
import analysis_utils

start_date = sys.argv[1]
end_date = sys.argv[2]
committee = sys.argv[3]

date_range = analysis_utils.days_in_range(start_date, end_date)

exclude_forms = ["F3", "SB", "SD"]

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

                t_id = line['TRANSACTION ID']
                contribution_date = line['CONTRIBUTION DATE']
                contribution_name = line['CONTRIBUTOR ORGANIZATION NAME']
                if contribution_name:
                    if 'DONOR COMMITTEE FEC ID' in line:
                        contribution_name += " (PAC: {0})".format(line['DONOR COMMITTEE FEC ID'])
                    else:
                        contribution_name += " (ORGANIZATION) "
                else:
                    contribution_name = line['CONTRIBUTOR FIRST NAME'] + ' ' + line['CONTRIBUTOR LAST NAME']


                address = []
                if "CONTRIBUTOR STREET 1" in line:
                    address.append(line["CONTRIBUTOR STREET 1"])
                    address.append(line["CONTRIBUTOR CITY"])
                    address.append(line["CONTRIBUTOR STATE"])
                    address.append(line["CONTRIBUTOR ZIP"])
                    
                if address:
                    contribution_name += ' from ' + ' '.join(address)

                form_type = line["FORM TYPE"]

                print("{4} - {0}: {1} gave {2} on {3}".format(t_id, contribution_name, amount, contribution_date, form_type))
