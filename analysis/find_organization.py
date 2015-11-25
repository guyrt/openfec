# find organizations by word
import json
import sys
import analysis_utils

start_date = sys.argv[1]
end_date = sys.argv[2]

date_range = analysis_utils.days_in_range(start_date, end_date)

other_args = sys.argv[3:]

for date in date_range:
    f = open("data/org_defs_{0}.json".format(date))
    for line in f:
        line_l = line.lower()
        keep = True
        for arg in other_args:
            keep = keep and arg.lower() in line_l
            if not keep:
                break
        if keep:
            jline = json.loads(line)
            try:
                output = date + ": " + analysis_utils.organization_to_string(jline)
            except analysis_utils.NoNameInLine:
                print("Matched no print")
                break
            else:
                print(output)
