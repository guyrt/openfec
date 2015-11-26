import pydocumentdb.document_client as doc_client
from pydocumentdb.errors import HTTPFailure
from documentdb_config import *

import sys
import json

client = doc_client.DocumentClient("https://openfecdata.documents.azure.com:443/", {'masterKey': "lK9nAjaEnVcXOIM6gS3334bjH3Nps3AR827CbyIawTo0tfbjKwZR7uTN7i91/vKEmbaN7iCScqhOKBx5URyarw=="})

try:
	collection = client.ReadCollection(DB_COLLECTION_ID)
except HTTPFailure:
	print("Did you forget to run setup_documentdb.py?")
	raise

upload_file = sys.argv[1]

print("Uploading " + upload_file)

for line in open(upload_file):
	linej = json.loads(line)
	doc = client.CreateDocument(collection['_self'], linej)

print("done!")