__author__ = 'rramchandani'

from pyVmomi import vim
from pyVirtualize.utils.exceptions import TimeOutException, ProgramNotExecuted

from ._base import BaseOperation


class ProcessOperations(BaseOperation):
    """
    ProcessOperations provides APIs to manipulate the guest operating system processes.
    """

    def execute(self, program, arguments="", cwd="", env_vars=None, start_minimized=False,
                wait_for_guest_ready=True, wait_for_program_to_exit=True,
                credentials=None, interactive=True):
        """
        Starts a program in the guest operating system.
        If program is not executed then it will raise an Exception ''

        :param program: (str) 
         The absolute path to the program to start.
         For Linux guest operating systems, /bin/bash is used to start the program.
         For Solaris guest operating systems, /bin/bash is used to start the program if it exists. 
         Otherwise /bin/sh is used. 
         If /bin/sh is used, then the process ID returned by StartProgramInGuest will be that of 
         the shell used to start the program, rather than the program itself, 
         due to the differences in how /bin/sh and /bin/bash work. 
         This PID will still be usable for watching the process 
         with ListProcessesInGuest to find its exit code and elapsed time.

        :param arguments: (str)
         The arguments to the program. 
         In Linux and Solaris guest operating systems, the program will be executed by a guest shell. 
         This allows stdio redirection, 
         but may also require that characters which must be escaped to the shell also be escaped on the command line provided.
         For Windows guest operating systems, prefixing the command with "cmd /c" can provide stdio redirection.

        :param cwd: (str)
         The absolute path of the working directory for the program to be run. 
         VMware recommends explicitly setting the working directory for the program to be run. 
         If this value is unset or is an empty string, the behavior depends on the guest operating system. 
         For Linux guest operating systems, if this value is unset or is an empty string, 
         the working directory will be the home directory of the user associated with the guest authentication. 
         For other guest operating systems, if this value is unset, the behavior is unspecified.

        :param env_vars: (str)
         An array of environment variables, specified in the guest OS notation 
         (eg PATH=c:bin;c:windowssystem32 or LD_LIBRARY_PATH=/usr/lib:/lib), 
         to be set for the program being run. 
         Note that these are not additions to the default environment variables; 
         they define the complete set available to the program. 
         If none are specified the values are guest dependent.

        :param start_minimized: (bool)
         This argument applies only for 'Windows' guests.
         Makes any program window start minimized.

        :param wait_for_guest_ready: (bool)
         This argument specifies, whether to check for Guest operation are ready before starting the program.
         If 'True', it halts execution until Guest is ready (or logged in, maybe using auto-logon),
         Else, it directly starts execution.

        :param wait_for_program_to_exit: (bool)
         This argument will wait until the programs gets executed and returns back some value.
         It can also be configured with a 'time-out' period, which will take value from parent VM object. 

        :param credentials: (str)
         Specify the credentials type string.
         Which was added using 'set_credentials' function.
         If string is left empty, it will find the 'default' credentials type and will use them.
         And if it doesn't find any, then it will raise an Exception.

        :param interactive: (bool) 
         This is set to true if the client wants an interactive session in the guest.

        :return:  vim.vm.guest.ProcessManager.ProcessInfo:
            Attributes:
                name (str): The process name

                pid (long): The process ID

                owner (str): The process owner

                cmdLine (str): The full command line

                startTime (datetime): The start time of the process

                endTime (datetime, optional): If the process was started using StartProgramInGuest then 
                 the process completion time will be available if queried within 5 minutes after it completes.

                exitCode (int, optional): If the process was started using StartProgramInGuest then 
                 the process exit code will be available if queried within 5 minutes after it completes.

        :raises:
            vim.fault.GuestOperationsFault:
                if there is an error processing a guest operation.

            vim.fault.InvalidState:
                if the operation cannot be performed because of the virtual machine's current state.

            vim.fault.TaskInProgress:
                if the virtual machine is busy.

            vim.fault.FileFault:
                if there is a file error in the guest operating system.

            vim.fault.GuestOperationsUnavailable:
                if the VM agent for guest operations is not running.

            vim.fault.InvalidPowerState:
                if the VM is not powered on.

            vim.fault.FileNotFound:
                if the program path does not exist.

            vim.fault.CannotAccessFile:
                if the program path cannot be accessed.

            vim.fault.GuestPermissionDenied:
                if the program path cannot be run because the guest authentication will not allow the operation.

            vim.fault.InvalidGuestLogin:
                if the the guest authentication information was not accepted.

            vim.fault.GuestComponentsOutOfDate:
                if the guest agent is too old to support the operation.

            vim.fault.OperationNotSupportedByGuest:
                if the operation is not supported by the guest OS.

            vim.fault.OperationDisabledByGuest:
                if the operation is not enabled due to guest agent configuration.

            pyVirtualize.utils.exceptions.ProgramNotExecuted

        """

        self._precheck_for_operations()

        if wait_for_guest_ready and not self._is_guest_operations_ready():
            self._wait_for_guest_operations_ready()

        content = self.service_instance.RetrieveContent()
        pm = content.guestOperationsManager.processManager
        creds = self._get_auth(type_=credentials, interactive=interactive)

        if creds is None:
            raise vim.fault.InvalidGuestLogin("The guest authentication information was not accepted,\
             or Invalid credentials.")

        if self._guest_os_name().__contains__("Windows"):
            ps = vim.vm.guest.ProcessManager.WindowsProgramSpec(
                programPath=program,
                arguments=arguments,
                startMinimized=start_minimized,
                workingDirectory=cwd,
                envVariables=env_vars
            )
        else:
            ps = vim.vm.guest.ProcessManager.ProgramSpec(
                programPath=program,
                arguments=arguments,
                workingDirectory=cwd,
                envVariables=env_vars
            )

        res = pm.StartProgramInGuest(self.vmomi_object, creds, ps)

        if not res > 0:
            # Program didn't executed!
            raise ProgramNotExecuted

        else:
            if wait_for_program_to_exit:
                # Program executed, now wait for process to complete or timeout after 'default_timeout' secs!
                self._wait_for_process_terminate_in_guest(res, creds)

        process_info = self.list_processes(pids=[res], credentials=credentials)
        process_info = process_info[0] if isinstance(process_info, list) else process_info

        return process_info

    def list_processes(self, pids=[], credentials=None, interactive=True):
        """
        List the processes running in the guest operating system, 
        plus those started by StartProgramInGuest that have recently completed.

        :param pids: (list)
         If set, only return information about the specified processes. 
         Otherwise, information about all processes are returned. 
         If a specified processes does not exist, nothing will be returned for that process.

        :param credentials: (str)
         Specify the credentials type string.
         Which was added using 'set_credentials' function.
         If string is left empty, it will find the 'default' credentials type and will use them.
         And if it doesn't find any, then it will raise an Exception.

        :return: [vim.vm.guest.ProcessManager.ProcessInfo]:
            The list running processes is returned in an array of `GuestProcessInfo`_ structures.
            Attributes:
                name (str): The process name

                pid (long): The process ID

                owner (str): The process owner

                cmdLine (str): The full command line

                startTime (datetime): The start time of the process

                endTime (datetime, optional): If the process was started using StartProgramInGuest then 
                 the process completion time will be available if queried within 5 minutes after it completes.

                exitCode (int, optional): If the process was started using StartProgramInGuest then 
                 the process exit code will be available if queried within 5 minutes after it completes.

        :raises:

            vim.fault.GuestOperationsFault:
                if there is an error processing a guest operation.

            vim.fault.InvalidState:
                if the operation cannot be performed because of the virtual machine's current state.

            vim.fault.TaskInProgress:
                if the virtual machine is busy.

            vim.fault.GuestOperationsUnavailable:
                if the VM agent for guest operations is not running.

            vim.fault.InvalidPowerState:
                if the VM is not powered on.

            vim.fault.GuestPermissionDenied:
                if there are insufficient permissions in the guest OS.

            vim.fault.InvalidGuestLogin:
                if the the guest authentication information was not accepted.

            vim.fault.GuestComponentsOutOfDate:
                if the guest agent is too old to support the operation.

            vim.fault.OperationNotSupportedByGuest:
                if the operation is not supported by the guest OS.

            vim.fault.OperationDisabledByGuest:
                if the operation is not enabled due to guest agent configuration.

        """
        self._precheck_for_operations()

        content = self.service_instance.RetrieveContent()
        pm = content.guestOperationsManager.processManager
        creds = self._get_auth(type_=credentials, interactive=interactive)

        if pids:
            res = pm.ListProcessesInGuest(self.vmomi_object, creds, pids=pids)
        else:
            res = pm.ListProcessesInGuest(self.vmomi_object, creds)

        return res

    def get_env_var(self, names="", credentials=None, interactive=True):
        """
        Reads an environment variable from the guest OS.
        If the authentication uses interactiveSession, 
        then the environment being read will be that of the user logged into the desktop. 
        Otherwise it's the environment of the system user.

        :param names: (str, optional) 
         The names of the variables to be read. If not set, then all the environment variables are returned.

        :param credentials: (str)
         Specify the credentials type string.
         Which was added using 'set_credentials' function.
         If string is left empty, it will find the 'default' credentials type and will use them.
         And if it doesn't find any, then it will raise an Exception.

        :param interactive: (bool) 
         This is set to true if the client wants an interactive session in the guest.

        :return: A string array containing the value of the variables, 
        or all environment variables if nothing is specified. 
        The format of each string is "name=value". 
        If any specified environment variable isn't set, then nothing is returned for that variable.

        :raises:

            vim.fault.GuestOperationsFault:
                if there is an error processing a guest operation.

            vim.fault.InvalidState:
                if the operation cannot be performed because of the virtual machine's current state.

            vim.fault.TaskInProgress:
                if the virtual machine is busy. accepted by the guest OS.

            vim.fault.GuestOperationsUnavailable:
                if the VM agent for guest operations is not running.

            vim.fault.InvalidPowerState:
                if the VM is not powered on.

            vim.fault.GuestPermissionDenied:
                if there are insufficient permissions in the guest OS.

            vim.fault.InvalidGuestLogin:
                if the the guest authentication information was not accepted.

            vim.fault.GuestComponentsOutOfDate:
                if the guest agent is too old to support the operation.

            vim.fault.OperationNotSupportedByGuest:
                if the operation is not supported by the guest OS.

            vim.fault.OperationDisabledByGuest:
                if the operation is not enabled due to guest agent configuration.
        """
        self._precheck_for_operations()

        content = self.service_instance.RetrieveContent()
        pm = content.guestOperationsManager.processManager
        creds = self._get_auth(type_=credentials, interactive=interactive)

        if names:
            res = pm.ReadEnvironmentVariableInGuest(self.vmomi_object, creds, names=names)
        else:
            res = pm.ReadEnvironmentVariableInGuest(self.vmomi_object, creds)

        return res
