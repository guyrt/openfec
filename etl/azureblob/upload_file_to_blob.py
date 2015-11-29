from azure.storage.blob import BlobService
from .blob_config import *


class BlobUploader(object):

    def __init__(self, make_container_public=False):
        """
        Class to handle uploading to an azure blob connection.

        :param make_container_public: True iff you are okay with public read access to your data. Useful for teaching a course
        :return:
        """
        self.blob_service = BlobService(account_name=BLOB_ACCOUNTNAME, account_key=BLOB_ACCOUNTKEY)
        if make_container_public:
            self.blob_service.create_container(BLOB_CONTAINER, x_ms_blob_public_access="container")
        else:
            self.blob_service.create_container(BLOB_CONTAINER)

    def put_json_file(self, file_obj, filename):
        """
        Put a file into azure blob store.

        Allows user to specify format. For example, once could use:
        <prefix>/YYYYMMDD.json
        """
        file_obj.seek(0)
        self.blob_service.put_block_blob_from_path(BLOB_CONTAINER, filename, file_obj.name, x_ms_blob_content_type="text/json")