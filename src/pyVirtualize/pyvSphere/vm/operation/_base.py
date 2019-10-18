__author__ = 'rramchandani'

import time

from pyVmomi import vim
from pyVirtualize.utils.exceptions import TimeOutException

import pyVirtualize.utils.exceptions as exceps

TIMEOUT = 600 #seconds, i.e 10 mins.


class BaseOperation(object):

    def __init__(self, vim, timeout=None, **kwargs):
        self.vmomi_object = vim.vmomi_object
        self.service_instance = vim.service_instance
        self.credentials = vim.credentials
        self._timeout_seconds = timeout if timeout and (isinstance(timeout, int) or isinstance(timeout, float))\
                                else TIMEOUT

    def _is_tools_installed(self):
        tools_status = self.vmomi_object.guest.toolsStatus
        if tools_status == 'toolsNotInstalled' or \
                        tools_status == 'toolsNotRunning':
            return False
        return True

    def _wait_for_power_on(self, wait_for_guest_ready=False):
        if wait_for_guest_ready:
            self._timeout(self._is_guest_operations_ready)
        else:
            self._timeout(self._is_guest_powered_on)

    def _wait_for_power_off(self):
        self._timeout(self._is_guest_powered_off)

    def _wait_for_guest_operations_ready(self):
        self._timeout(self._is_guest_operations_ready)

    @staticmethod
    def _wait_for_task_to_complete(task):
        while True:
            state = task.info.state
            if state == 'running':
                time.sleep(5)
            elif state != 'success':
                raise exceps.TaskExecutionFailed
            else:
                break

    def _wait_for_process_terminate_in_guest(self, pid, creds):
        start_time = time.time()
        while True:
            current_time = time.time()
            if not self._is_process_exists_in_gos(pid, creds):
                break
            elif current_time - start_time >= self._timeout_seconds:
                raise TimeOutException
            else:
                time.sleep(5)

    def _timeout(self, condition_func, *args):
        start_time = time.time()
        while True:
            current_time = time.time()
            if condition_func(*args):
                break
            elif current_time - start_time >= self._timeout_seconds:
                break
            else:
                time.sleep(5)

    def _is_guest_powered_off(self):
        return True if self.vmomi_object.runtime.powerState == "poweredOff" else False

    def _is_guest_powered_on(self):
        try:
            return True if self.vmomi_object.runtime.powerState == "poweredOn" else False
        except:
            return False

    def _is_guest_operations_ready(self):
        return True if self.vmomi_object.guest.interactiveGuestOperationsReady else False

    def _precheck_for_operations(self):
        if not self._is_tools_installed():
            if not self.upgrade_vm_tools():
                raise Exception

    def _guest_os_name(self):
        return self.vmomi_object.summary.config.guestFullName

    def _is_process_exists_in_gos(self, pid, creds):
        pid = int(pid)
        content = self.service_instance.RetrieveContent()
        pm = content.guestOperationsManager.processManager
        #creds = self._get_auth()

        res = pm.ListProcessesInGuest(self.vmomi_object, creds, pids=[pid])

        if not res:
            return False

        res = res[0]
        return False if isinstance(res.exitCode, int) and res.exitCode >= 0 else True

    def _get_auth(self, interactive=True, type_=None):
        if type_ is None:
            for cred_type in self.credentials.keys():
                if self.credentials[cred_type]['default'] == True:
                    type_ = cred_type
                    break

        if not self.credentials.get(type_) and type_ is not None:
            raise Exception("No credential type '{0}' found.".format(type))

        cred = self.credentials[type_]

        return vim.vm.guest.NamePasswordAuthentication(
            username=cred['username'],
            password=cred['password'],
            interactiveSession=interactive
        )

    def upgrade_vm_tools(self):
        self.vmomi_object.UpgradeTools()
        self._timeout(self._is_tools_installed)

    def _get_obj(self, vimtype, name=None, not_found_return_none=False):
        content = self.service_instance.RetrieveContent()
        obj = None
        container = content.viewManager.CreateContainerView(
            content.rootFolder, vimtype, True
        )

        if name is None: return container.view

        found = False

        for c in container.view:
            if name:
                if c.name == name:
                    obj = c
                    found = True
                    break
            else:
                obj = c
                break
        if not found:
            return None if not_found_return_none else []
        return obj

    def _get_snapshot_list(self):
        _ = self.vmomi_object.snapshot
        if not _:
            return dict()

        snapshots = _.rootSnapshotList
        snapshot_list = {}

        def func(snapshots):
            for snapshot in snapshots:
                snapshot_list[snapshot.name] = snapshot.snapshot
                if snapshot.childSnapshotList:
                    func(snapshots=snapshot.childSnapshotList)
            return snapshot_list

        return func(snapshots=snapshots)
