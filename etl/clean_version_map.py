import pandas as pd
import json
import sys

outfile = sys.argv[1]

fec_map = dict()


def proc_row(row):
    version = row[0]
    form = row[1]
    if version not in fec_map:
        fec_map[version] = dict()
    if form not in fec_map[version]:
        fec_map[version][form] = []
    for x in range(2, len(row)):
        rowelt = row[x]
        if not pd.isnull(row[x]):
            _, name = rowelt.split('-', 1)
            fec_map[version][form].append(name)


df = pd.read_excel("fec_version_map.xlsx", sheetname="all versions", header=None)

df.apply(proc_row, axis=1)

strmap = json.dumps(fec_map)

f = open(outfile, "w")
f.write(strmap)
