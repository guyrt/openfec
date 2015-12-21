"""
Download the zipcode tabulation area to congressional district mapping.
"""
import sys
import pandas as pd

zipcodes = 'http://www2.census.gov/geo/relfiles/cdsld13/natl/natl_zccd_delim.txt'
districts = 'http://www2.census.gov/geo/docs/reference/codes/files/national_cd113.txt'

# Get data
df_zip = pd.read_csv(zipcodes, skiprows=1)
df_zip.columns = ['State', 'ZCTA', 'District']
df_districts = pd.read_table(districts, delimiter='\s\s+', header=None, skiprows=1, engine='python')
df_districts.columns = ['STATE', 'STATEKEY', 'DISTRICT', 'DISTRICTNAME']

# get just state bits from districts.
states = df_districts.groupby('STATE').agg({'STATEKEY': max}).reset_index()

#
df_zip_withstates = df_zip.merge(states, left_on='State', right_on='STATEKEY', how='left')
df_zip_withstates = df_zip_withstates.icol(range(4))
df_zip_withstates.columns = ['state_code', "zcta", "district", "state"]
df_zip_withstates.to_csv("data/zip_to_district.csv", index=False)

azure = len(sys.argv) > 1 and sys.argv[1] == 'azure'

if azure:
    print("Uploading to azure")
    from azureblob.upload_file_to_blob import BlobUploader
    blob_upload = BlobUploader(make_container_public=True)

    blob_upload.put_json_file(open("data/zip_to_district.csv", 'r'), "raw_mappings/zip_to_district.csv")


