

Download the Data
==================

Use python script download_fec_data.py to unpack data from the fec locally. Call the function like

    python ./etl/download_fec_data.py ./metadata/fecdefs.json YYYYmmDD YYYYmmDD [azure]

This will download every day's filings in the range (inclusive) and unzip all the files to the ./data folder within your repo.
You'll get two kinds of files: org_defs_YYYYMMDD.json list all header rows. filings_YYYYMMDD.json list all remaining rows in files from that day.

Adding azure as the fourth argument will cause an upload to an azure blob as specified in ./etl/azureblob/upload_file_to_blob.py. This is helpful
for larger analysis where a spark cluster is necessary.


Building the FEC file definition map.
================================

I got the xlsx from http://www.fec.gov/finance/disclosure/ftpefile.shtml. Download the file defns zip and unpack the full definitions spreadsheet.

Use clean_version_map.py to create fecdefs.json from fec_version_map.xlsx

Examples
========

The analysis folder contains some usage examples.

*analysis_utils.py* A few utilities to help parse the data. 

*find_committee_pairings.py* Find connections from one Committee to another.

*find_organizations.py* Find organization by searching for keyword. This searches the entire contents of org_defs*.json (the header row for every downloaded file) for the keyword you input, but you can input multiple words. Keep in mind that not all candidates list their entire name in the filing.



