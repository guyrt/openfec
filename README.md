

Download the Data
==================

Use python script download_fec_data.py to unpack data from the fec locally. Call the function like

    python ./etl/download_fec_data.py ./metadata/fecdefs.json YYYYmmDD YYYYmmDD [azure]

This will download every day's filings in the range (inclusive) and unzip all the files to the ./data folder within your repo.
You'll get two kinds of files: org_defs_YYYYMMDD.json list all header rows. filings_YYYYMMDD.json list all remaining rows in files from that day.

Adding azure as the fourth argument will cause an upload to an azure blob as specified in ./etl/azureblob/upload_file_to_blob.py. This is helpful
for larger analysis where a spark cluster is necessary.

There is also a library to upload to Azure DocumentDB. This is a good starting place to make a searchable data source, but I didn't hook it to the download_fec_data path.

Building the FEC file definition map.
================================

I got the xlsx from http://www.fec.gov/finance/disclosure/ftpefile.shtml. Download the file defns zip and unpack the full definitions spreadsheet.

In the metadata folder, use clean_version_map.py to create fecdefs.json from fec_version_map.xlsx

After some initial investigation, I made the choice to clean up some field names. In particular, I replace all spaces with underscores to make SQL operations easier.
I also remove periods. Some fields like "5. COMMITTEE TYPE" didn't read in SparkSQL even with backticks, so I removed the period. For similar reasons, I chose
to remove "/" characters from mappings.

Other Data:
===========

In addition to the raw filings, I've written parsers for the following sources:

**List all committees and candidates**

`python ./etl/download_fec_mappingfiles.py [azure]`

Download the list of candidates and committees from FEC. This list is updated in place on FEC webpage, so my downloader also overwrites. 
The committee file links to candidates via CAND_ID field. There is another file that lists all connections between committees that I haven't gotten to yet (contributions welcome).

**Zip Code to Congressional District**

`python ./etl/zcta_to_district.py [azure]`

Create a helper csv that maps zipcode tabulation areas to House districts. This is not a 1:1 mapping, and it doesn't include states with only one House seat (i.e. at-large seats). 
Requires pandas.

**Zip code to county**

`python ./etl/zcta_to_county.py [azure]`

Create a helper csv that maps zipcode tabulation area to State/County. This can be helpful for printing.


Local Examples
==============

The analysis folder contains some usage examples from local data. To be honest, I got a little ways with this approach
before deciding to implement azure upload so I could use spark. There is a great deal of ETL that would need to be done
 to make this data easy to use locally.

*analysis_utils.py* A few utilities to help parse the data. In particular, attempts to handle the nasty keys that this data
 produces to produce at least somewhat sensible descriptions of organizations and their behavior.

*find_committee_pairings.py* Find connections from one Committee to another.

*find_organizations.py* Find organization by searching for keyword. This searches the entire contents of org_defs*.json (the header row for every downloaded file) for the keyword you input, but you can input multiple words. Keep in mind that not all candidates list their entire name in the filing.



