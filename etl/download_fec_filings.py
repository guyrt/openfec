# ftp://ftp.fec.gov/FEC/electronic/
import urllib.request as request

from datetime import datetime, timedelta
import os
import sys
from zipfile import ZipFile
from json import dumps

from fecparser import FecFileParser

"""
Define a few functions and two global variables that we'll need to handle upload.
"""

# set up file handles
filehandles = dict()
org_defs = dict()


def pull_data(date_str, tmp_data_folder, fake=False):
    # Pull file
    url = "ftp://ftp.fec.gov/FEC/electronic/{0}.zip".format(date_str)
    ziploc = "{1}/{0}.zip".format(date_str, tmp_data_folder)
    unziploc = "{1}/{0}".format(date_str, tmp_data_folder)
    if not fake:
        r = request.urlopen(url)
        f = open(ziploc, 'wb')
        f.write(r.read())
        f.close()
    return ziploc, unziploc


def local_store_unzipped_folder(zip_obj):
    # open files
    if date_str not in filehandles:
        filehandles[date_str] = open("{1}/filings_{0}.json".format(date_str, clean_data_folder), 'w')
        org_defs[date_str] = open("{1}/org_defs_{0}.json".format(date_str, clean_data_folder), 'w')

    # process each file
    fec_defs = open(sys.argv[1])
    for fecfile in zip_obj.namelist():
        print("Processing " + fecfile)
        parser = FecFileParser(fec_defs, date_str)
        for line in parser.processfile(open("{2}/{0}/{1}".format(date_str, fecfile, tmp_data_folder)), fecfile):
            filehandles[date_str].write(dumps(line) + "\n")
        org_defs[date_str].write(dumps(parser.organization_information) + "\n")

    return filehandles


"""
Run the program.
"""

if len(sys.argv) < 3:
    print("Usage: python download_fec_filings.py fecdefs.json 20151103 20151104 [azure]")
    print("This would download and process all FEC data for Nov 3 and Nov 4.")

mindate_s = sys.argv[2]
maxdate_s = sys.argv[3]

blob_upload = None
if len(sys.argv) > 4 and sys.argv[4] == 'azure':
    print("Will upload to Azure")
    from azureblob.upload_file_to_blob import BlobUploader
    blob_upload = BlobUploader(make_container_public=True)
else:
    print("No azure upload requested.")

print("Running from {0} to {1}".format(mindate_s, maxdate_s))

mindate = datetime.strptime(mindate_s, "%Y%m%d")
maxdate = datetime.strptime(maxdate_s, "%Y%m%d")


tmp_data_folder = "./tmp_data"
clean_data_folder = "./data"


try:
    os.mkdir(tmp_data_folder)
except WindowsError:
    # Can't recreate same dir.
    pass

try:
    os.mkdir(clean_data_folder)
except WindowsError:
    # Can't recreate same dir.
    pass


# perform pull
num_days_to_pull = (maxdate - mindate).days
for i in range(num_days_to_pull + 1):
    date_str = datetime.strftime(mindate + timedelta(days=i), "%Y%m%d")
    print("Parsing " + date_str)
    ziplocation, unziplocation = pull_data(date_str, tmp_data_folder)

    # unzip
    z = ZipFile(ziplocation)
    z.extractall(unziplocation)

    local_store_unzipped_folder(z)

if blob_upload:
    for filedate, fileobj in filehandles.items():
        print("Uploading main data for {0}".format(filedate))
        blob_upload.put_json_file(fileobj, "raw_filings/{0}.json".format(filedate))

    print("Uploading headers")
    for filedate, fileobj in org_defs.items():
        blob_upload.put_json_file(fileobj, "raw_headers/{0}.json".format(filedate))
