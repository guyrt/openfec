"""
Download the zcta to county file (many to many relationship)
"""

import requests
import sys

use_azure = len(sys.argv) > 1 and sys.argv[1] == 'azure'

file_loc = "http://www2.census.gov/geo/docs/maps-data/data/rel/zcta_county_rel_10.txt"

# Get file locally
r = requests.get(file_loc)

local_file = open("data/zcta_to_county.csv", 'w')
local_file.write(r.text)
local_file.close()

if use_azure:
    print("Uploading to azure")
    from azureblob.upload_file_to_blob import BlobUploader
    blob_upload = BlobUploader(make_container_public=True)

    blob_upload.put_json_file(open("data/zcta_to_county.csv", 'r'), "raw_mappings/zcta_to_county.csv")
