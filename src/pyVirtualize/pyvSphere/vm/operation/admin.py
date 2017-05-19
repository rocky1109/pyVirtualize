__author__ = 'rramchandani'

from ._base import BaseOperation
from .file import FileOperations
from .process import ProcessOperations


class VimBase:

    vmomi_object = None
    service_instance = None
    credentials = dict()


class AdminOperations(FileOperations, ProcessOperations):

    def execute_process_using_ps_tools(self, program, arguments=(), admin_credentials='admin', user_credentials='user'):
        """
        Starts a program in the guest operating system using Admin credentials.
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
        
        :param admin_credentials: (str)
         Specify the credentials type string for Administrator.
         Which was added using 'set_credentials' function.
         If string is left empty, it will find the 'default' credentials type and will use them.
         And if it doesn't find any, then it will raise an Exception.
        
        :param user_credentials: (str)
         Specify the credentials type string for User.
         Which was added using 'set_credentials' function.
         If string is left empty, it will find the 'default' credentials type and will use them.
         And if it doesn't find any, then it will raise an Exception.
        """
        prog_path = "C:\\temp\\temp.bat"
        try:
            admin_creds = self.credentials[admin_credentials]
        except KeyError:
            raise KeyError("No such credentials type was found.")

        arguments = " ".join(arguments)
        program = program + " " + arguments

        execution_string = """

cmdkey.exe /add:%COMPUTERNAME%.%USERDOMAIN%.com /user:"{0}" /pass:"{1}"

C:\PSTools\PsExec.exe -accepteula -u "{0}" -p "{1}" {2}

cmdkey.exe /delete:%COMPUTERNAME%.%USERDOMAIN%.com
                """.format(admin_creds['username'], admin_creds['password'], program)

        self.create_remote(prog_path, contents=execution_string, credentials=user_credentials)
        self.execute(prog_path, credentials=user_credentials)
        self.delete_remote(prog_path, credentials=user_credentials)
