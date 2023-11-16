"""
INTRODUCTION
I and this library are in no way affiliated with Box, Inc.,
and its use is not endorsed by Box, Inc.
This library works within the scope of the functionality provided by Box, Inc.
and is merely a simplified use of the functionality provided.
If you have sufficient knowledge,
it is strongly recommended to use the SDK provided by Box, Inc.
* Box ® is a registered trademark of Box, Inc., and/or its affiliates
  in the United States and other countries

SUMMARY
I have extended Box SDK and added some functions.
I plan to grandually remove them form the library when similar processing is
supported by Box SDK

Typical usage example:
    box = Box(
        grant_type = 'JWT',
        jwt_config_filepath = 'hoge/fuga.json'
    )
    box.download_bytes(file_id=000000)
"""

import datetime
import os
import re
import urllib
from typing import Literal

import boxsdk

from wakalib.exceptions.exception import (ArgsError, FilePathDoesNotExists,
                                          FilePathIsNotFile)


class Box:
    """
    Extends Box SDK to provide various functions.
    """
    def __init__(
            self,
            grant_type: Literal['JWT'] = 'JWT',
            jwt_config_filepath: str | None = None,
        ) -> None:
        """
        ## Summary
        Initializes the Box object and
        performs necessary authentication and setup.

        ## Args:
        - grant_type (Literal['JWT'], optional):
            The type of grant used for authentication. Default is 'JWT'.
        - jwt_config_filepath (str | None, optional):
            The filepath to the JWT configuration file. Default is None.
        """
        if grant_type == 'JWT':
            if not jwt_config_filepath:
                raise ArgsError(
                    argument_name='jwt_config_filepath',
                    add=(
                        '"jwt_config_filepath" is required '
                        'when grant_type is set to "JWT"'
                    )
                )
            if not os.path.exists(jwt_config_filepath):
                raise FilePathDoesNotExists(file_path=jwt_config_filepath)
            if not os.path.isfile(jwt_config_filepath):
                raise FilePathIsNotFile(file_path=jwt_config_filepath)
            self.__client = boxsdk.Client(
                boxsdk.JWTAuth.from_settings_file(jwt_config_filepath)
            )
        else:
            raise ArgsError(
                argument_name='grant_type',
                add='Unsupported grant type.'
            )

    @property
    def client(self):  # pylint: disable=missing-function-docstring
        return self.__client

    def get_file_info(self, file_id: str) -> dict:
        """
        ## Summary
        Retrieves information about a specific file in Box.

        ## Args:
        - file_id (str) :
            The ID of the file in Box.

        ## Returns:
        - dict: _description_
        """
        file_object = self.client.file(file_id=file_id)
        return file_object._session.get(  # pylint: disable=protected-access
            url=file_object.get_url()
        ).json()

    def get_folder_info(self, folder_id: str) -> dict:
        """
        ## Summary
        Retrieves information about a specific folder in Box.

        ## Args:
        - folder_id (str) :
            Retrieves information about a specific folder in Box.

        ## Returns:
        - dict: _description_
        """
        folder_object = self.client.folder(folder_id==folder_id)
        return folder_object._session.get(  # pylint: disable=protected-access
            url=folder_object.get_url()
        ).json()

    def download_to_file(
            self,
            file_id: str,
            output_filepath: str
        ) -> None:
        """
        ## Summary
        Downloads a file from Box and saves it to the specified filepath.

        ## Args:
        - file_id (str) :
            he ID of the file in Box to download.
        - output_filepath (str) :
            File path of output destination, full path is more secure.
        - encoding (str, optional) :
            Defaults to 'utf-8'.
        """
        with open(file=output_filepath, mode='wb') as _file:
            self.client.file(file_id).download_to(_file)

    def download_bytes(self, file_id: str) -> bytes:
        """
        ## Summary
        Downloads a file from Box and returns its content as bytes.

        ## Args:
        - file_id (str) : The ID of the file in Box to download.

        ## Returns:
        - bytes : Bytes of the specified file.
        """
        return self.client.file(file_id=file_id).content()

    def upload(
            self,
            output_folderid: str,
            target_file_path: str,
            allow_update: bool = False
        ) -> str:
        """
        ## Summary
        Uploads a file to Box and returns the ID of the uploaded file.

        ## Args:
        - output_folderid (str) :
            The ID of the folder in Box where the file will be uploaded.
        - target_file_path (str) :
            The filepath of the file to upload.
        - allow_update (bool, optional) :
            Whether to allow updating an existing file. Default is False.

        # Returns:
        - str: Box file id
        """
        output_folder = self.client.folder(
            folder_id=output_folderid
        )
        items = output_folder.get_items()
        dict_item = {item.name: item.id for item in items}
        if os.path.getsize(filename=target_file_path) < 20000000:
            if dict_item.get(os.path.basename(target_file_path)):
                file_id = dict_item[os.path.basename(target_file_path)]
                if allow_update:
                    self.client.file(file_id).update_contents(target_file_path)
            else:
                file_id = output_folder.upload(target_file_path).id
            return file_id
        else:
            if dict_item.get(os.path.basename(target_file_path)):
                file_id = dict_item[os.path.basename(target_file_path)]
                if allow_update:
                    chunked_uploader = self.client.file(
                        file_id=file_id
                    ).get_chunked_uploader(
                        file_path=target_file_path
                    )
                    chunked_uploader.start()
            else:
                chunked_uploader = output_folder.get_chunked_uploader(
                    file_path=target_file_path
                )
                uploaded_file = chunked_uploader.start()
                file_id = uploaded_file.id
            return file_id

    def update(
            self,
            output_file_id: str,
            target_file_path: str
            ) -> None:
        """
        ## Description
        Updates the contents of a file in Box with
        the contents of the specified file.

        ## Args:
        - output_file_id (str) :
            The ID of the file in Box to update.
        - target_file_path (str) :
            The filepath of the file to update from.
        """
        output_file = self.client.file(output_file_id)
        if os.path.getsize(filename=target_file_path) < 20000000:
            output_file.update_contents(target_file_path)
        else:
            chunked_uploader = output_file.get_chunked_uploader(
                file_path=target_file_path
            )
            chunked_uploader.start()

    def create_folder(self, output_folder_id: str, folder_name: str) -> str:
        """
        ## Description
        Creates a new folder in Box and returns its ID.
        If the folder already exsits, its ID is returned.

        ## Args:
        - output_folder_id (str) :
            Parent Box folder id.
        - folder_name (str) :
            The name of the folder to create.

        ## Returns:
        - str: Box folder id
        """
        main_folder = self.client.folder(folder_id=output_folder_id)
        items = main_folder.get_items()
        dict_item = {item.name.lower(): item for item in items}
        if dict_item.get(folder_name.lower()):
            item = dict_item[folder_name]
            if item.type == 'folder':
                folder_id = item.id
            elif item.type == 'web_link':
                folder_id = str(item.url).split('/', maxsplit=-1)[-1]
        else:
            subfolder = main_folder.create_subfolder(folder_name)
            folder_id = subfolder.id
        return folder_id

    def move_folder(
            self,
            target_folder_id: str,
            destination_folder_id: str,
        ) -> None:
        """
        ## Summary
        Move a folder under another folder.

        ## Args:
        - target_folder_id (str) :
            Box folder ID you want to move.
        - destination_folder_id (str) :
            Destination folder.
        """
        self.client.folder(folder_id=target_folder_id).update_info(
            data={
                'parent': {
                    'id': destination_folder_id
                }
            }
        )

    def create_weblink(
            self,
            output_folder_id: str,
            link_uri: str,
            link_name: str,
            link_description: str
        ) -> None:
        """
        ## Summary
        Create Web Link (Object) in the specified folder.

        ## Args:
        - output_folder_id (str) : Output folder ID.
        - link_uri (str) : Web link URI.
        - link_name (str) : Web link name.
        - link_description (str) : Web link description.
        """
        self.client.folder(folder_id=output_folder_id).create_web_link(
            target_url=link_uri,
            name=link_name,
            description=link_description
        )

    def url_to_id(self, target_url: str) -> str:
        """
        ## Summary
        Convert Box URL to Box ID.

        ## Args:
        - target_url (str) : Box URL.
        ## Returns:
        - str: Box ID.
        """
        urlparse = urllib.parse.urlparse(target_url)
        pathparam = urlparse.path.split('/')[-1]
        if pathparam.isdecimal():
            return pathparam
        else:
            return self.client.get_shared_item(target_url).id

    def get_child_item_id(
            self,
            folder_id: str,
            regex_str: str
        ) -> str | None:
        """
        ## Description
        Finds item in the folder that fullmatch "regex_str" and return that ID.
        If it does not exsit, None is returned.
        Note: If multiple items exist, the first match is returned.

        ## Args:
        - folder_id (str) : Box folder ID.
        - regex_str (str) : Regex string.
        ## Returns:
        - str | None: Box folder ID or None.
        """
        for item in self.client.folder(folder_id=folder_id).get_items():
            if re.fullmatch(pattern=regex_str, string=item.name):
                res = item.id
                return res

    def get_parent_folder_id(
            self,
            object_id: str,
            id_type: Literal['file', 'folder']
        ) -> str:
        """
        ## Summary
        Returns the ID of its parent folder from BoxID.

        ## Args:
        - object_id (str) : Box object ID.
        - id_type (Literal['file', 'folder']): Object type.

        ## Returns:
        - str: Box folder ID.
        """
        if id_type == 'file':
            return self.client.file(
                file_id=object_id
            ).get().parent['id']
        elif id_type == 'folder':
            return self.client.folder(
                folder_id=object_id
            ).get().parent['id']

    def task_assign(
            self,
            file_id: str,
            assignee_box_userid: str,
            due: datetime.datetime,
            message: str
        ) -> None:
        """
        ## Summary
        Create tasks for files in the BOX and assign them to users.

        ## Args:
        - file_id (str) :
            Target Box file id.
        - assignee_box_userid (str) :
            User to be assigned.
        - due (datetime.datetime) :
            Task due date.
        - message (str) :
            Message at the time of assignment.
        """
        due_at = due.strftime('%Y-%m-%dT%H:%M:%S+09:00')
        file = self.client.file(file_id=file_id)
        # webhook = client.create_webhook(
        #     file,
        #     ['TASK_ASSIGNMENT.CREATED', 'TASK_ASSIGNMENT.UPDATED'],
        #     'http://192.168.221.220:11525/'
        # )
        task_object = file.create_task(message, due_at)
        user_object = self.client.user(user_id=assignee_box_userid)
        self.client.task(task_id=task_object.id).assign(user_object)
