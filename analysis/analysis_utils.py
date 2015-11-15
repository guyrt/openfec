from datetime import datetime, timedelta


class NoNameInLine(Exception):
	pass


def reverse_lookup(d, value):
    for k, v in d.items():
        if v == value:
            return k
    raise KeyError("Can't find {0} as value.".format(value))


def days_in_range(start, end):
    mindate = datetime.strptime(start, "%Y%m%d")
    maxdate = datetime.strptime(end, "%Y%m%d")

    num_days_to_pull = (maxdate - mindate).days
    return [datetime.strftime(mindate + timedelta(days=i), "%Y%m%d") for i in range(num_days_to_pull + 1)]


def key_for_org(line):
    key = ''
    if 'FILER COMMITTEE ID NUMBER' in line:
        key = 'FILER COMMITTEE ID NUMBER'
    else:
        key = 'FILER CANDIDATE ID NUMBER'

    return key


def organization_to_string(line):
    value = ''
    if 'COMMITTEE NAME' in line:
        value = line['COMMITTEE NAME']
    elif '5. JOINT FUND PARTICIPANT CMTTE NAME' in line:
        value = line['5. JOINT FUND PARTICIPANT CMTTE NAME']
    elif 'ORGANIZATION NAME' in line:
        value = line['ORGANIZATION NAME'] 
    elif 'PCC COMMITTEE NAME' in line:
        value = line['PCC COMMITTEE NAME'] 

    if not value:
        raise NoNameInLine()

    value += ' ' + line['FORM TYPE']

    if '5. PARTY CODE' in line:
        value += ' (' + line['5. PARTY CODE'] + ')'

    key = key_for_org(line)
    value += ' ' + line[key]

    return value