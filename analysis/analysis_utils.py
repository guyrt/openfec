from datetime import datetime, timedelta


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
