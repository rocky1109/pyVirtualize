__author__ = 'rramchandani'

import pickle
from .parsers import GenericParsers


class PersistableClass(object):

    def load(self, cls_file):
        with open(cls_file, "rb") as fh:
            _ = pickle.load(fh)
            for k, v in _.__dict__.items():
                setattr(self, k, v)

    def store(cls, cls_file):
        with open(cls_file, "wb+") as fh:
            pickle.dump(cls, fh)


class Variables(PersistableClass):

    def __init__(self, variable_file):
        gp = GenericParsers(file_path=variable_file)
        parsed_variables = gp.parse()

        if parsed_variables.has_key("variables"):

            for key, value in parsed_variables["variables"].items():

                if key.__contains__(" "):
                    key.replace(" ", "_")

                setattr(self, key, value)


import sys
from subprocess import check_call
try:
    if sys.hexversion > 0x03000000:
        import winreg
    else:
        import _winreg as winreg
except ImportError:
    pass


class Win32Environment(object):
    """Utility class to get/set windows environment variable"""

    def __init__(self, scope):
        self.scope = scope
        if scope == 'user':
            self.root = winreg.HKEY_CURRENT_USER
            self.subkey = 'Environment'
        else:
            self.root = winreg.HKEY_LOCAL_MACHINE
            self.subkey = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'

    def getenv(self, name):
        key = winreg.OpenKey(self.root, self.subkey, 0, winreg.KEY_READ)
        try:
            value, _ = winreg.QueryValueEx(key, name)
        except WindowsError:
            value = ''
        winreg.CloseKey(key)
        return value

    def setenv(self, name, value):
        # Note: for 'system' scope, you must run this as Administrator
        key = winreg.OpenKey(self.root, self.subkey, 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)
        winreg.CloseKey(key)
        # For some strange reason, calling SendMessage from the current process
        # doesn't propagate environment changes at all.
        # TODO: handle CalledProcessError (for assert)
        check_call('''\
"%s" -c "import win32api, win32con; assert win32api.SendMessage(win32con.HWND_BROADCAST, win32con.WM_SETTINGCHANGE, 0, 'Environment')"''' % sys.executable)

