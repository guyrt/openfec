"""
Download, parse to JSON, and upload to azure the mapping files found at
http://www.fec.gov/finance/disclosure/ftpdet.shtml#a2015_2016

Pay particular attention to the mapping html pages, which help with some of the cryptic codes used as keys.

"""
import os
import urllib.request as request
import requests
from zipfile import ZipFile
from json import dumps


sources = {
    'committee': {
        'data': 'ftp://ftp.fec.gov/FEC/2016/cm16.zip',
        'mapping': 'http://www.fec.gov/finance/disclosure/metadata/cm_header_file.csv'
    },
    'candidate': {
        'data': 'ftp://ftp.fec.gov/FEC/2016/cn16.zip',
        'mapping': 'http://www.fec.gov/finance/disclosure/metadata/cn_header_file.csv'
    }
}


def pull_ftp_data(server_file, local_file):
    # Pull file from server
    print(server_file)
    r = request.urlopen(server_file)
    f = open(local_file, 'wb')
    f.write(r.read())
    f.close()


def pull_http_data(server_file):
    # Pull file from server
    print(server_file)
    r = requests.get(server_file)
    return r.text



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


def to_json(mapping, raw_file_name, clean_file_name):
    in_file_obj = open(raw_file_name, 'r')
    out_file_obj = open(clean_file_name, 'w')
    for line in in_file_obj:
        line = line.strip().split('|')
        line_dict = {k: v for k, v in zip(mapping, line)}
        out_file_obj.write(dumps(line_dict))
        out_file_obj.write("\n")


# For each data element, pull the data itself and the header. Combine to form JSON then upload.

if __name__ == "__main__":
    import sys
    azure = len(sys.argv) > 1 and sys.argv[1] == "azure"
    blob_upload = None
    if azure:
        print("Upload to azure")
        from azureblob.upload_file_to_blob import BlobUploader
        blob_upload = BlobUploader(make_container_public=True)
    else:
        print("No azure upload requested. Pulling locally only.")

    for key, files in sources.items():
        print("Downloading " + key)
        local_zip_file = "{0}/{1}.zip".format(tmp_data_folder, key)
        local_unzip_dir = "{0}/{1}".format(tmp_data_folder, key)
        pull_ftp_data(files['data'], local_zip_file)
        mapping = pull_http_data(files['mapping']).strip()

        mapping = mapping.split(',')

        # unzip the data
        z = ZipFile(local_zip_file)
        z.extractall(local_unzip_dir)
        for unzipfile in z.namelist():
            clean_file = "{0}/{1}.txt".format(clean_data_folder, key)
            to_json(mapping, "{0}/{1}".format(local_unzip_dir, unzipfile), clean_file)

            if blob_upload:
                print("Uploading to azure blob.")
                blob_upload.put_json_file(open(clean_file, 'r'), "raw_mappings/{0}.json".format(key))
