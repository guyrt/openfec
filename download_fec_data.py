# ftp://ftp.fec.gov/FEC/electronic/

import urllib.request as request
from datetime import datetime, timedelta
import os
from subprocess import call
import sys
from zipfile import ZipFile
from json import dumps

from fecparser import FecFileParser

if len(sys.argv) < 3:
	print("Usage: python download_fec_data.py fecdefs.json 20151103 [20151104]")
	print("This would download and process all FEC data for Nov 3 and Nov 4.")

mindate_s = sys.argv[2]
maxdate_s = sys.argv[3] if len(sys.argv) > 3 else mindate_s

print("Running from {0} to {1}".format(mindate_s, maxdate_s))

mindate = datetime.strptime(mindate_s, "%Y%m%d")
maxdate = datetime.strptime(maxdate_s, "%Y%m%d")

try:
    os.mkdir("data")
except WindowsError:
    # Can't recreate same dir.
    pass


# set up file handles
filehandles = dict()
org_defs = dict()


# perform pull
num_days_to_pull = (maxdate - mindate).days
for i in range(num_days_to_pull + 1):
    date_str = datetime.strftime(mindate + timedelta(days=i), "%Y%m%d")
    
    # Pull file
    url = "ftp://ftp.fec.gov/FEC/electronic/{0}.zip".format(date_str)
    ziploc = "data/{0}.zip".format(date_str)
    unziploc = "data/{0}".format(date_str)
    r = request.urlopen(url)
    f = open(ziploc, 'wb')
    f.write(r.read())
    f.close()

    # unzip
    z = ZipFile(ziploc)
    z.extractall(unziploc)

    # open files
    if date_str not in filehandles:
        filehandles[date_str] = open("data/filings.json", 'w')
        org_defs[date_str] = open("data/org_defs.json", 'w')

    # process each file
    fec_defs = open(sys.argv[1])
    for fecfile in z.namelist():
        parser = FecFileParser(fec_defs, date_str)
        for line in parser.processfile(open("data/{0}/{1}".format(date_str, fecfile))):
            filehandles[date_str].writeline(dumps(line))
        org_defs[date_str].writeline(dumps(parser.organization_information))

