
"""
pyVirtualize
============
pyVirtualize is build over pyVmomi, hence it has ability to perform all the operations what vSphere client is able to.
Not only vSphere, but pyVirtualize provides an interface for VMware Horizon View session management.

pyVirtualize provides easy interfaces to:

- Connect to VMWare's ESX, ESXi, Virtual Center, Virtual Server hosts and View Connnection server.
- Query hosts, datacenters, resource pools, virtual machines and perform various operations over them.
- VMs operations: power, file, process, snapshot, admin, utilities
- Horizon View: desktop, farms, rdsh, -pool management, querying connection and more.


An of course, you can use it to access all the API through python.

"""

from . import pyvSphere
from pyvSphere import vSphere
from utils.winutils import Process, WinUtils


__all__ = ['pyvSphere', 'vSphere', 'Process', 'WinUtils']