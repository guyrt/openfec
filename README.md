

Download the Data
==================

Use python script download_fec_data.py to unpack data from the fec locally. Call the function like

    python ./download_fec_data.py fecdefs.json YYYYmmDD [YYYYmmDD]

This will download every day's filings in the range (inclusive) and unzip all the files to the ./data folder within your repo.


Building the FEC file definition map.
================================

I got the xlsx from http://www.fec.gov/finance/disclosure/ftpefile.shtml. Download the file defns zip and unpack the full definitions spreadsheet.

Use clean_version_map.py to create fecdefs.json from fec_version_map.xlsx

