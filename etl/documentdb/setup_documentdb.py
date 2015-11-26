# Set up the documentdb instance. Should only be run once (but can be run >1 time)

import pydocumentdb.document_client as doc_client
from pydocumentdb.errors import HTTPFailure
from documentdb_config import *

client = doc_client.DocumentClient(DB_HOST, {'masterKey': DB_MASTER_KEY})


# TODO - get or create database.
try:
	db = client.ReadDatabase(DB_ID)
	print("DB Already exists. Make sure documentdb_config.DB_ID equals {0}".format(db["_self"]))
except HTTPFailure:
	db = client.CreateDatabase({'id': DB_NAME})
	print("Created db. Replace documentdb_config.DB_ID with {0}".format(db["_self"]))

try:
	collection = client.ReadCollection(DB_COLLECTION_ID)
except HTTPFailure:
	collection = client.CreateCollection(db["_self"], {'id': ORG_COLLECTION}, {"offerType": 'S1'})
	print("Created collection. Replace documentdb_config.DB_COLLECTION_ID with {0}".format(collection["_self"]))

