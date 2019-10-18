__author__ = 'rramchandani'

import os
import requests
from pyVmomi import vim

from ._base import BaseOperation


class FileOperations(BaseOperation):
    """
    FileOperations provides APIs to manipulate the guest operating system file options.
    """

    def _upload_file(self, src, dest, credentials=None, overwrite=True):

        if not os.path.isfile(src):
            raise IOError("Local file '{0}' doesn't exists".format(src))

        with open(src, 'rb') as fhandler:
            _file = fhandler.read()

            file_attributes = vim.vm.guest.FileManager.WindowsFileAttributes()
            content = self.service_instance.RetrieveContent()
            file_manager = content.guestOperationsManager.fileManager

            cred = self._get_auth(type_=credentials)

            try:
                file_manager.MakeDirectoryInGuest(
                    vm=self.vmomi_object,
                    auth=cred,
                    directoryPath=os.path.dirname(dest),
                    createParentDirectories=True
                )
            except:
                # Directory already exists!
                pass

            url = file_manager.InitiateFileTransferToGuest(
                vm=self.vmomi_object,
                auth=cred,
                guestFilePath=dest,
                fileAttributes=file_attributes,
                fileSize=len(_file),
                overwrite=overwrite
            )

            # url = url.replace("*", self.address)

            response = requests.put(url, data=_file, verify=False)

            if response.status_code == requests.codes.ok:
                # log.info("File uploaded in '{0}'.".format(self.vm_obj.summary.config.name))
                pass
            else:
                _ = "File could not be uploaded. Response: {0}, Reason: {1}". \
                    format(response.status_code, response.content)

                raise IOError(_)

    def _upload_dir(self, src, dest, credentials=None):

        if os.path.isdir(src):
            for dirpath, dirs, files in os.walk(src):
                for file_ in files:
                    src_file = os.path.join(dirpath, file_)
                    dest_file = os.path.join(dest, os.path.relpath(src_file, src))
                    self._upload_file(src=src_file, dest=dest_file, credentials=credentials)

                for dir_ in dirs:
                    src_path = os.path.join(dirpath, dir_)
                    dest_path = os.path.join(dest, os.path.relpath(src_path, src))
                    self._upload_dir(src=src_path, dest=dest_path, credentials=credentials)

        elif os.path.isfile(src):
            dest_file = os.path.join(dest, os.path.basename(src))
            self._upload_file(src=src, dest=dest_file, credentials=credentials)

    def upload(self, src, dest, credentials=None, overwrite=True):
        """
        Uploads the file/directory into the guest operating system.
        In case of file it will 'pyVirtualize' requires the file path and 'dest' also requires the path specifying file name. 
        But when 'pyVirtualize' is path representing folder/directory then it will copy the contents of the directory recursively
        into specified 'dest' path.

        NOTE: It creates the directories automatically missing in the path. Also in case of file, then it overwrites in the 'dest'.

        :param src: (str)
         Valid source location that can be either file or directory.

        :param dest: (str)
         A destination location for file or directory respectively.

        :param credentials: (str)
         Specify the credentials type string.
         Which was added using 'set_credentials' function.
         If string is left empty, it will find the 'default' credentials type and will use them.
         And if it doesn't find any, then it will raise an Exception.

        :param overwrite: (bool)
         Overwrites the file if present on guest while upload.

        """

        if not (os.path.exists(src) or os.path.isfile(src) or os.path.isdir(src)):
            raise IOError("Source path '{0}' doesn't exists.".format(src))

        if os.path.isfile(src):
            self._upload_file(src=src, dest=dest, credentials=credentials, overwrite=overwrite)
        else:
            self._upload_dir(src=src, dest=dest, credentials=credentials)

    def _download_file(self, src, dest, credentials=None, overwrite=True):

        file_manager = self.service_instance.content.guestOperationsManager.fileManager

        file_transfer_info = file_manager.InitiateFileTransferFromGuest(
            vm=self.vmomi_object,
            auth=self._get_auth(type_=credentials),
            guestFilePath=src
        )

        url = file_transfer_info.url  # .replace('*', self.host_obj.address)

        response = requests.get(url=url, verify=False)

        if os.path.exists(dest):
            if overwrite:
                try:
                    self.delete_local(dest)
                except:
                    pass
            else:
                return

        if response.status_code == requests.codes.ok:
            if not os.path.exists(os.path.dirname(dest)):
                os.makedirs(os.path.dirname(dest))
            with open(dest, "wb+") as fhandler:
                fhandler.write(response.content)
        else:
            _ = "File was not downloaded. Response: {0}; Reason: {1}". \
                format(response.status_code, response.content)

            raise IOError(_)

    def _download_dir(self, src, dest, credentials=None):

        files, dirs = self.get_remote_dir_desc(src, credentials=credentials)

        for _file in files:
            src_file = os.path.join(src, _file)
            dest_file = os.path.join(dest, _file)
            self._download_file(src_file, dest_file, credentials=credentials)

        for _dir in dirs:
            src_path = os.path.join(src, _dir)
            dest_path = os.path.join(dest, _dir)
            self._download_dir(src_path, dest_path, credentials=credentials)

    def download(self, src, dest, credentials=None, overwrite=True):
        """
        Downloads the file/directory into the guest operating system.
        In case of file it will 'pyVirtualize' requires the file path and 'dest' also requires the path specifying file name. 
        But when 'pyVirtualize' is path representing folder/directory then it will copy the contents of the directory recursively
        into specified 'dest' path.

        NOTE: It creates the directories automatically missing in the path. Also in case of file, then it overwrites in the 'dest'.

        :param src: (str)
         Valid source location that can be either file or directory.

        :param dest: (str)
         A destination location for file or directory respectively.

        :param credentials: (str)
         Specify the credentials type string.
         Which was added using 'set_credentials' function.
         If string is left empty, it will find the 'default' credentials type and will use them.
         And if it doesn't find any, then it will raise an Exception.

        :param overwrite: (bool)
         Overwrites the file if present on local when download.

        """
        if not self.remote_path_exists(src, credentials=credentials):
            raise IOError("Remote path '{0}' doesn't exists to download.".format(src))

        if self._is_remote_path_file(src, credentials=credentials):
            self._download_file(src=src, dest=dest, credentials=credentials)
        else:
            self._download_dir(src=src, dest=dest, credentials=credentials)

    def list_dir_in_vm(self, path, credentials=None):
        """
        Returns information about files or directories in the guest.

        :param path: (str)
         The complete path to the directory or file to query.

        :param credentials: (str)
         Specify the credentials type string.
         Which was added using 'set_credentials' function.
         If string is left empty, it will find the 'default' credentials type and will use them.
         And if it doesn't find any, then it will raise an Exception.

        :return: 
            vim.vm.guest.FileManager.ListFileInfo:
                A `GuestListFileInfo` object containing information for all the matching files in the filePath and 
                the number of files left to be returned.

        """
        file_manager = self.service_instance.content.guestOperationsManager.fileManager

        return file_manager.ListFilesInGuest(
            vm=self.vmomi_object,
            auth=self._get_auth(type_=credentials),
            filePath=path
        )

    def get_remote_dir_desc(self, path, credentials=None):

        file_list = self.list_dir_in_vm(path, credentials)

        try:
            fi = [item.path for item in file_list.files if item.type == 'file']
        except:
            fi = []

        try:
            di = [item.path for item in file_list.files if item.type == 'directory']
        except:
            di = []

        if di.__contains__('.'):
            di.remove('.')
        if di.__contains__('..'):
            di.remove('..')

        return fi, di

    def _is_remote_path_dir(self, path, credentials=None):
        fi, di = self.get_remote_dir_desc(os.path.dirname(path), credentials)
        for d in di:
            if d == os.path.basename(path):
                return True

        return False

    def _is_remote_path_file(self, path, credentials=None):
        fi, di = self.get_remote_dir_desc(os.path.dirname(path), credentials)

        for f in fi:
            if f == os.path.basename(path):
                return True

        return False

    def remote_path_exists(self, path, credentials=None):
        """
        Return the presence of the path.

        :param path: (str)
         The complete path to the directory or file to query.

        :param credentials: (str)
         Specify the credentials type string.
         Which was added using 'set_credentials' function.
         If string is left empty, it will find the 'default' credentials type and will use them.
         And if it doesn't find any, then it will raise an Exception.

        :return: (bool) 'True' if path exists or else 'False' if it doesn't.

        """
        fi, di = self.get_remote_dir_desc(os.path.dirname(path), credentials)

        for f in fi:
            if f == os.path.basename(path):
                return True

        for d in di:
            if d == os.path.basename(path):
                return True
        return False

    def create_remote(self, path, contents=None, credentials=None):
        """

        :param path: 
        :param contents: 
        :param credentials: 
        :return: 
        """
        if contents is not None:

            with open(os.path.basename(path), "w+") as fh:
                fh.write(contents)
            self.move_remote(os.path.basename(path), path, credentials=credentials)
        else:

            content = self.service_instance.RetrieveContent()
            file_manager = content.guestOperationsManager.fileManager

            cred = self._get_auth(type_=credentials)

            file_manager.MakeDirectoryInGuest(
                vm=self.vmomi_object,
                auth=cred,
                directoryPath=os.path.dirname(path),
                createParentDirectories=True
            )

    def create_local(self, path, contents=None):

        if contents is not None:

            os.makedirs(os.path.dirname(path))
            with open(path, "w+") as fh:
                fh.write(contents)
        else:
            os.makedirs(path)

    def delete_remote(self, path, credentials=None):

        if not self.remote_path_exists(path, credentials=credentials):
            raise IOError("Remote path '{0}' was not found.".format(path))

        file_manager = self.service_instance.content.guestOperationsManager.fileManager
        try:
            file_manager.DeleteDirectoryInGuest(
                vm=self.vmomi_object,
                auth=self._get_auth(type_=credentials),
                directoryPath=path,
                recursive=True
            )
        except vim.fault.NotADirectory:
            file_manager.DeleteFileInGuest(
                vm=self.vmomi_object,
                auth=self._get_auth(type_=credentials),
                filePath=path
            )

    def delete_local(self, path):

        if os.path.isdir(path):
            import shutil
            shutil.rmtree(path)
        else:
            os.remove(path)

    def move_remote(self, src, dest, credentials=None):

        if not os.path.exists(src):
            raise IOError("Local path '{0}' doesn't exists.".format(src))

        if os.path.isfile(src):
            self._upload_file(src, dest, credentials)
        else:
            self._upload_dir(src, dest, credentials)

        self.delete_local(src)

    def move_local(self, src, dest, credentials=None):

        if not self.remote_path_exists(src):
            raise IOError("Remote path '{0}' doesn't exists in '{1}'.".format(src,
                                                                              self.vmomi_object.summary.config.name))

        if os.path.isfile(src):
            self._download_file(src, dest, credentials)
        else:
            self._download_dir(src, dest, credentials)
        self.delete_remote(src, credentials)
