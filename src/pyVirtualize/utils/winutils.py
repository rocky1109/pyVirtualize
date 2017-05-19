__author__ = 'rramchandani'

import subprocess

try:
    from _winreg import HKEY_LOCAL_MACHINE, EnumValue, KEY_READ, KEY_WOW64_64KEY, \
        OpenKey
except ImportError:
    pass


class Process(object):
    """
    Utility to launch new processes
    """

    @staticmethod
    def start_process(cmd):
        msg = 'Launching process: ' + cmd
        p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, )
        out, err = p.communicate()
        if p.returncode != 0 or err:
            raise RuntimeError("%r failed, status code %s stdout %r stderr %r"
                               % (cmd, p.returncode, out, err))
        return out.strip()


class WinUtils(object):
    """
    Utilities to work with Windows OS
    """

    @staticmethod
    def read_reg(reg_key, reg_val):
        """
        Fetch registry given the reg key+value combo
        :param reg_key:
        :param reg_val:
        :return:
        """
        ret = None
        with OpenKey(HKEY_LOCAL_MACHINE, reg_key, 0, KEY_READ |
                KEY_WOW64_64KEY) \
                as key:
            desc, i = None, 0
            while not desc or desc[0] != reg_val:
                desc = EnumValue(key, i)
                i += 1
            ret = desc[1]
        return ret

    @staticmethod
    def map_drive(user, password, net_share):
        """
        Map given network share
        :param user:
        :param password:
        :param net_share:
        :return:
        """
        cmd = 'net use ' + net_share + ' ' + password + ' /u:' + user
        Process.start_process(cmd)

    @staticmethod
    def del_map_drive(net_share):
        """
        Delete the given network share
        :param net_share:
        :return:
        """
        cmd = 'net use ' + net_share + ' /del'
        Process.start_process(cmd)
