# pyVirtualize
A python interface to access and manage VMware vSphere and ~Horizon View~.

pyVirtualize is build over pyVmomi, hence it has ability to perform all the operations what vSphere client is able to.
Not only vSphere, but pyVirtualize ~provides an interface for VMware Horizon View session management~.

pyVirtualize provides easy interfaces to:

- Connect to VMWare's ESX, ESXi, Virtual Center, Virtual Server hosts and View Connnection server.
- Query hosts, datacenters, resource pools, virtual machines and perform various operations over them.
- VMs operations: power, file, process, snapshot, admin, utilities
- ~Horizon View: desktop, farms, rdsh, -pool management, querying connection and more.~


An of course, you can use it to access all the API through python.

## Installation

Clone the project in your local directory.
```
git clone https://github.com/rocky1109/pyVirtualize.git
cd pyVirtualize
```

Now install/build it using **setup.py** file as
```
python setup.py install
```

Or, install it using *pip*, as
```
pip install pyVirtualize
```

## Example
```python
>> from pyVirtualize.pyvSphere import vSphere
>> vsphere = vSphere(address='10.112.67.60', username='administrator@vsphere.local', password='Secured')
>> vsphere.login()
>>
>> vsphere.Datacenters
{'datacenter1': 'vim.Datacenter:datacenter-2', 'datacenter2': 'vim.Datacenter:datacenter-7'}
>>
>> vsphere.VirtualMachines
{'W7x64': 'VirtualMachine:vm-295', 'W7x32': 'vim.VirtualMachine:vm-183', ... }
>>
>> vm = vsphere.VirtualMachines['W7x64']
>>
>> vm.set_credentials(username="myDomain\\myUsername", password="secret", credentials_type="user", default=True)
>>
>> vm.operations.snapshot.revert_to_current()
>> vm.operations.power.power_on()
>> vm.operations.file.upload("/path/towards/my/src/file", "/path/towards/my/dest/file")

```

Read more at [ReadTheDocs](http://pyvirtualize.readthedocs.io/en/latest/), which has entire documentation, examples and more!

PS: *Guys, SDKs for Horizon View had to be got down for confidential reasons. Sorry for any inconvenience caussed.*
