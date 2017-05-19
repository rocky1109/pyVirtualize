__author__ = 'rramchandani'

import ssl

from pyVim import connect
from pyVmomi import vim

from pyVirtualize.utils import exceptions
from pyVirtualize.utils.klasses import PersistableClass

from .datastore import Datastore
from .vm import VirtualMachine


class vSphere(PersistableClass):
    """
    Just like vSphere client, this class helps to access the vCenter Server and ultimately manages ESXi servers.
    
    :param address: (str)
     Server address of the ESXi / vCenter host.
         
    :param username: (str)
     Username to login with. [default = root]
         
    :param password: (str)
     Password to login with. [default = ca$hc0w]
         
    :param port: (int) 
     Port on which object should connect to host. [default = 443]
         
    | **Example**
    | >> from pyVirtualize.pyvSphere import vSphere
    | >> vsphere = vSphere(address='10.112.67.60', username='administrator@vsphere.local', password='Ca$hc0w1')
    | >> vsphere.login()
    | >>
    | >> vsphere.Datacenters
    | {'datacenter1': 'vim.Datacenter:datacenter-2', 'datacenter2': 'vim.Datacenter:datacenter-7'}
    | >>
    | >> vsphere.VirtualMachines
    | {'W7x64': 'VirtualMachine:vm-295', 'W7x32': 'vim.VirtualMachine:vm-183', ... }
    """

    def __init__(self, address, username='root', password='ca$hc0w', port=443, sslContext=None):
        self.address = address
        self.username = username
        self.password = password
        self.port = port

        if not sslContext:
            self.sslContext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            self.sslContext.verify_mode = ssl.CERT_NONE
        else:
            self.sslContext = sslContext

        self._apiType = ''

        self._vms = dict()
        self._datacenters = dict()
        self._hosts = dict()
        self._datastores = dict()

    @property
    def service_instance(self):
        """
        VMOMI ServiceInstance.
        """
        if self._service_instance is None:
            self.login()
        return self._service_instance

    def login(self):
        """
        Determine the most preferred API version supported by the specified VCenter server,
        then connect to the specified server using that API version, and logs into it. 
        """
        try:
            self._service_instance = connect.SmartConnect(host=self.address,
                                                          user=self.username,
                                                          pwd=self.password,
                                                          port=self.port,
                                                          sslContext=self.sslContext)
                                                         #connectionPoolTimeout=self.timeout)
        except Exception as err:
            raise err

    def logout(self):
        """
        Logs out from the specified VCenter server. 
        """
        try:
            self.service_instance.content.sessionManager.Logout()
        except:
            pass

    @property
    def apiType(self):
        """
        :return: (str)
         API Type of the specified server.  VirtualCenter/ESXi
        """
        if not self._apiType:
            self._apiType = self.service_instance.RetrieveContent().about.apiType
        return self._apiType

    @property
    def about(self):
        """
        :return: *vim.AboutInfo*, vmomi info object. 
        |    (vim.AboutInfo) {
        |        dynamicType = <unset>,
        |        dynamicProperty = (vmodl.DynamicProperty) [],
        |        name = 'VMware vCenter Server',
        |        fullName = 'VMware vCenter Server 6.0.0 build-3634794',
        |        vendor = 'VMware, Inc.',
        |        version = '6.0.0',
        |        build = '3634794',
        |        localeVersion = 'INTL',
        |        localeBuild = '000',
        |        osType = 'linux-x64',
        |        productLineId = 'vpx',
        |        apiType = 'VirtualCenter',
        |        apiVersion = '6.0',
        |        instanceUuid = '3c6c809d-eb71-4a4b-bd9d-23ca07928f51',
        |        licenseProductName = 'VMware VirtualCenter Server',
        |        licenseProductVersion = '6.0'
        |    }
        """
        return self.service_instance.RetrieveContent().about

    @property
    def Datacenters(self):
        """
        List of Datacenter objects.
        
        :return: dictionary object with key, value pair or Datacenter name and Datacenter object. 
        """
        if not self._datacenters:
            dcs = self._get_objects(vim.Datacenter)
            for dc in dcs:
                self._datacenters[dc.name] = dc
        return self._datacenters

    @property
    def Clusters(self):
        """
        List of Clusters objects.
        
        :return: dictionary object with key, value pair or Cluster name and Cluster object. 
        """
        return

    @property
    def Folders(self):
        return

    @property
    def Datastores(self):
        """
        List of Datastore objects.
        
        :return: dictionary object with key, value pair or Datastore name and Datastore object.
        """
        if not self._datastores:
            ds = self._get_objects(vim.Datastore)
            for d in ds:
                self._datastores[d.name] = Datastore(d)
        return self._datastores

    @property
    def Hosts(self):
        """
        List of Host objects.
        
        :return: dictionary object with key, value pair or Host name and Host object. 
        """
        if not self._hosts:
            hs = self._get_objects(vim.HostSystem)
            for h in hs:
                self._hosts[h.name] = h
        return self._hosts

    @property
    def Networks(self):
        return

    @property
    def ComputeResources(self):
        return

    @property
    def ResourcePools(self):
        return

    @property
    def VirtualMachines(self):
        """
        List of VirtualMachines objects.
        
        :return: dictionary object with key, value pair or VirtualMachine name and VirtualMachine object. 
        """
        if not self._vms:
            vms = self._get_objects(vim.VirtualMachine)
            for vm in vms:
                self._vms[vm.name] = VirtualMachine(vm, self.service_instance)
        return self._vms

    def rescan_virtual_machines(self):
        """
        Refreshes the *VirtualMachines* list associated to server.
        """
        vms = self._get_objects(vim.VirtualMachine)
        for vm in vms:
            if not self._vms.has_key(vm.name):
                self._vms[vm.name] = VirtualMachine(vm, self.service_instance)

    def _get_objects(self, views):
        content = self.service_instance.RetrieveContent()
        container = content.rootFolder
        viewType = [views]

        containerView = content.viewManager.CreateContainerView(container, viewType, recursive=True)
        children = containerView.view

        return children if isinstance(children, list) else [children]

    def create_new_datacenter(self, name):
        pass

    def create_new_folder(self, name):
        pass

    def __del__(self):
        self.logout()

    def __repr__(self):
        if self._service_instance is not None:
            return "<{0}-{1}>".format(self.apiType, self.address)
        else:
            return "<VirtualCenter-{0}>".format(self.address)


if __name__ == "__main__":
    vs = vSphere(address='10.112.67.60', username='administrator@vsphere.local', password='Ca$hc0w1')
    #vs = vSphere(address='10.112.19.17', username='root', password='ca$hc0w')
    vs.login()
    print("Datacenters:")
    print(vs.Datacenters)
    print("="*10)
    print("Datastores:")
    print(vs.Datastores)
    print("="*10)
    print("Hosts:")
    print(vs.Hosts)
    print("=" * 10)
    print("VMs:")
    print(vs.VirtualMachines)
    print("=" * 10)
