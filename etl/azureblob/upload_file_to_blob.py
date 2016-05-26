from azure.storage.blob import BlockBlobService, PublicAccess, ContentSettings
from .blob_config import BLOB_CONTAINER, BLOB_ACCOUNTKEY, BLOB_ACCOUNTNAME


class BlobUploader(object):

    def __init__(self, blob_container=None, make_container_public=False):
        """
        Class to handle uploading to an azure blob connection.

        :param make_container_public: True iff you are okay with public read access to your data. Useful for teaching a course
        :return:
        """
        self.blob_container = blob_container or BLOB_CONTAINER
        self.blob_service = BlockBlobService(account_name=BLOB_ACCOUNTNAME, account_key=BLOB_ACCOUNTKEY)
        # if make_container_public:
        #     self.blob_service.create_container(BLOB_CONTAINER, public_access=PublicAccess)
        # else:
        #     self.blob_service.create_container(BLOB_CONTAINER)

    def put_json_file(self, file_obj, filename):
        """
        Put a file into azure blob store.

        Allows user to specify format. For example, once could use:
        <prefix>/YYYYMMDD.json
        """
        file_obj.seek(0)
        self.blob_service.create_blob_from_path(
            self.blob_container, 
            filename, 
            file_obj.name, 
            content_settings=ContentSettings(content_type="text/json")
        )
