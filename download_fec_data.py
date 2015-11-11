# ftp://ftp.fec.gov/FEC/electronic/

import urllib.request as request
from datetime import datetime, timedelta
import os
from subprocess import call
import sys
from zipfile import ZipFile

mindate_s = sys.argv[1]
maxdate_s = sys.argv[2]

mindate = datetime.strptime(mindate_s, "%Y%m%d")
maxdate = datetime.strptime(maxdate_s, "%Y%m%d")

try:
    os.mkdir("data")
except WindowsError:
    # Can't recreate same dir.
    pass

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

    # process each file
    for zipfile in z.namelist():
        pass
