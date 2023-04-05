import re
from .Google_Core import Create_Service
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

client_secret_file = 'credentials.json'
api_name = 'drive'
api_version = 'v3'
scopes = ['https://www.googleapis.com/auth/drive']


class GDrive(object):
    def __init__(
            self,
            client_secret_file: str,
            api_name: str = 'drive',
            api_version: str = 'v3',
            scopes: list = ['https://www.googleapis.com/auth/drive'],
    ) -> None:

        self.CLIENT_SECRET_FILE = client_secret_file
        self.API_NAME = api_name
        self.API_VERSION = api_version
        self.SCOPES = scopes
        self.service = self.__create_service()

    def __call__(self):
        return self.service

    def __create_service(self):
        return Create_Service(
            self.CLIENT_SECRET_FILE,
            self.API_NAME,
            self.API_VERSION,
            self.SCOPES,
        )

    def _get_file_metadata(
            self,
            file_id: str,
            fields: str = None,
    ):
        try:
            file_metadata = self.service.files().get(
                fileId=file_id,
                fields=fields,
            ).execute()
            return file_metadata

        except HttpError as e:
            print(e)

    def _check_folder_exists(
            self,
            folder_name: str,
            parent_folder_id: str = None,
    ):

        """
        check if the folder exists
        and return the folder_id
        """

        query = f"name='{folder_name}'" \
                " and mimeType='application/vnd.google-apps.folder'"
        # " and trashed=false and parents='{parent_folder_id}'"
        if parent_folder_id:
            query += f" and trashed=false and parents='{parent_folder_id}'"

        fields = "files(id)"

        try:
            folder = self.service.files().list(
                q=query,
                fields=fields
            ).execute().get('files', [])

            if folder:
                return folder

            return

        except HttpError as e:
            print(e)

    def _folder_to_copy(
            self,
            # file_link: str,
            folder_name: str,
            parent_folder_id: str = None,
    ):

        """
        return the folder_id to clone files to its own drive
        """

        folder = self._check_folder_exists(
            folder_name=folder_name,
            parent_folder_id=parent_folder_id,
        )

        if not folder:
            ...
            folder = self.create_folder(
                folder_name=folder_name,
                parent_folder_id=parent_folder_id,
            )

        return folder

    def copy_file(
            self,
            file_link: str,
            folder_name: str,
            parent_folder_id: str = None,
    ):
        """
        Copy a file to a specific folder
        and return the new file id
        """

        file_id = re.search(r'1([a-zA-Z0-9_-]+)', file_link).group(0)
        folder = self._folder_to_copy(
            folder_name=folder_name,
            parent_folder_id=parent_folder_id,
        )
        file = self.service.files().get(
            fileId=file_id,
        ).execute()

        new_file = {
            'name': file['name'],
            'parents': [folder],
        }

        try:
            copy_file = self.service.files().copy(
                fileId=file_id,
                body=new_file,
            ).execute()

            return copy_file.get('id')

        except HttpError as e:
            print(e)

    def get_file(
            self,
            file_id: str,
            file_name: str,
    ):
        """
        File download for local access
        """

        try:
            file_metadata = self._get_file_metadata(
                file_id=file_id,
                fields='name, id, mimeType, fullFileExtension',
            )
            file_content = self.service.files().get_media(
                fileId=file_id,
            ).execute()

            with open(
                    f"{file_name}.{file_metadata['fullFileExtension']}",
                    'wb',
            ) as f:
                f.write(file_content)

            return {
                'name': file_metadata['name'],
                'id': file_metadata['id'],
                'mimeType': file_metadata['mimeType'],
                'fullFileExtension': file_metadata['fullFileExtension'],
            }

        except HttpError as e:
            print(e)

    def upload_file(
            self,
            file: str,
            folder_id: str = None,
    ):
        file_metadata = {
            'name': file,
        }
        if folder_id:
            file_metadata['parents'] = [folder_id]

        try:
            media = MediaFileUpload(
                filename=file,
                resumable=True,
            )

            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id',
            ).execute()

            return file.get('id')
        except HttpError as e:
            print(e)

        pass

    def create_folder(
            self,
            folder_name: str,
            parent_folder_id: str = None,
    ):
        """
        Create folder in own drive

        param:
        :folder_name - Name of folder
        :parent_folder_id - (optional) Create a folder inside another folder

        return:
            Folder ID
        """

        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
        }
        if parent_folder_id:
            folder_metadata['parents'] = [parent_folder_id]

        try:
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id',
            ).execute()
            print(f'Folder {folder_name} is created')

            return folder.get('id')

        except HttpError as e:
            print(e)

    def folder_files(
            self,
            folder_id: str,
    ):
        """
        Return files that are in a specific folder
        """

        try:
            query = f"'{folder_id}' in parents and trashed=false"
            fields = "nextPageToken, files(id, name, mimeType, fullFileExtension)"
            results = self.service.files().list(
                q=query,
                fields=fields,
            ).execute()
            return results.get('files', [])
        except HttpError as e:
            print(e)


if __name__ == "__main__":
    drive = GDrive(client_secret_file, api_name, api_version, scopes)
    print(dir(drive()))
    # drive.create_folder('something else', '1FWcjww09qOHAjFb86PSFf3IZJB129ep7')
    # print(drive.folder_files('11fgw2lZeNGECHftVID8kx48S6c6RSr-Y'))
    # print(drive.get_file('1-56fCVb-CIrVaEOGB-XNwiDrOm_q_Qf8', 'hogwarts'))