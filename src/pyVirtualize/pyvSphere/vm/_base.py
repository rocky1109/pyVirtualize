__author__ = 'rramchandani'


from .operation import Operations


class VimBase:

    def __init__(self, vmomi_object=None, service_instance=None, credentials=None):
        self.vmomi_object = vmomi_object
        self.service_instance = service_instance
        self.credentials = dict() if credentials is None else credentials


class Details:

    def __init__(self, vobj):
        self._vobj = vobj

    @property
    def runtime(self):
        """
        :return: *vim.vm.RuntimeInfo*, the runtime details of the current machine.
        |    (vim.vm.RuntimeInfo) {
        |       dynamicType = <unset>,
        |       dynamicProperty = (vmodl.DynamicProperty) [],
        |       device = (vim.vm.DeviceRuntimeInfo) [
        |          (vim.vm.DeviceRuntimeInfo) {
        |             dynamicType = <unset>,
        |             dynamicProperty = (vmodl.DynamicProperty) [],
        |             runtimeState = (vim.vm.DeviceRuntimeInfo.VirtualEthernetCardRuntimeState) {
        |                dynamicType = <unset>,
        |                dynamicProperty = (vmodl.DynamicProperty) [],
        |                vmDirectPathGen2Active = false,
        |                vmDirectPathGen2InactiveReasonVm = (str) [],
        |                vmDirectPathGen2InactiveReasonOther = (str) [
        |                   'vmNptIncompatibleNetwork'
        |                ],
        |                vmDirectPathGen2InactiveReasonExtended = <unset>,
        |                reservationStatus = <unset>
        |             },
        |             key = 4000
        |          }
        |       ],
        |       host = 'vim.HostSystem:host-14',
        |       connectionState = 'connected',
        |       **powerState** = 'poweredOn',
        |       faultToleranceState = 'notConfigured',
        |       dasVmProtection = <unset>,
        |       toolsInstallerMounted = false,
        |       suspendTime = <unset>,
        |       bootTime = 2017-02-17T14:39:35.245193Z,
        |       suspendInterval = 0L,
        |       question = <unset>,
        |       memoryOverhead = <unset>,
        |       maxCpuUsage = 9196,
        |       maxMemoryUsage = 4096,
        |       numMksConnections = 0,
        |       recordReplayState = 'inactive',
        |       cleanPowerOff = <unset>,
        |       needSecondaryReason = <unset>,
        |       onlineStandby = false,
        |       minRequiredEVCModeKey = <unset>,
        |       consolidationNeeded = false,
        |       offlineFeatureRequirement = (vim.vm.FeatureRequirement) [
        |          (vim.vm.FeatureRequirement) {
        |             dynamicType = <unset>,
        |             dynamicProperty = (vmodl.DynamicProperty) [],
        |             key = 'cpuid.lm',
        |             featureName = 'cpuid.lm',
        |             value = 'Bool:Min:1'
        |          }
        |       ],
        |       featureRequirement = (vim.vm.FeatureRequirement) [
        |          (vim.vm.FeatureRequirement) {
        |             dynamicType = <unset>,
        |             dynamicProperty = (vmodl.DynamicProperty) [],
        |             key = 'cpuid.SSE3',
        |             featureName = 'cpuid.SSE3',
        |             value = 'Bool:Min:1'
        |          },...
        |       ],
        |       featureMask = (vim.host.FeatureMask) [],
        |       vFlashCacheAllocation = 0L,
        |       paused = false,
        |       snapshotInBackground = false,
        |       quiescedForkParent = <unset>
        |    }
        """
        return self._vobj.summary.runtime

    @property
    def guest(self):
        """
        :return: *vim.vm.Summary.GuestSummary*, the guest details of the current machine.
        |    (vim.vm.Summary.GuestSummary) {
        |       dynamicType = <unset>,
        |       dynamicProperty = (vmodl.DynamicProperty) [],
        |       guestId = 'windows7_64Guest',
        |       **guestFullName** = 'Microsoft Windows 7 (64-bit)',
        |       toolsStatus = 'toolsOk',
        |       toolsVersionStatus = 'guestToolsCurrent',
        |       toolsVersionStatus2 = 'guestToolsCurrent',
        |       toolsRunningStatus = 'guestToolsRunning',
        |       **hostName** = 'W7x64',
        |       **ipAddress** = '10.112.19.116'
        |    } 
        """
        return self._vobj.summary.guest

    @property
    def config(self):
        """
        :return: *vim.vm.Summary.ConfigSummary*, the config details of the current machine.
        |    (vim.vm.Summary.ConfigSummary) {
        |       dynamicType = <unset>,
        |       dynamicProperty = (vmodl.DynamicProperty) [],
        |       **name** = 'Jenkins',
        |       **template** = false,
        |       vmPathName = '[datastore1] Jenkins/Jenkins.vmx',
        |       memorySizeMB = 4096,
        |       cpuReservation = 0,
        |       memoryReservation = 0,
        |       numCpu = 4,
        |       numEthernetCards = 1,
        |       numVirtualDisks = 1,
        |       uuid = '420c6ef6-eef0-03ff-20f2-5d2479b2afdc',
        |       instanceUuid = '500ce065-5f5b-17fa-fa8f-d7033e548ecb',
        |       guestId = 'windows7_64Guest',
        |       guestFullName = 'Microsoft Windows 7 (64-bit)',
        |       annotation = '',
        |       product = <unset>,
        |       installBootRequired = false,
        |       ftInfo = <unset>,
        |       managedBy = <unset>
        |    } 
        """
        return self._vobj.summary.config

    @property
    def storage(self):
        """
        :return: *vim.vm.Summary.StorageSummary*, the storage details of the current machine.
        |    (vim.vm.Summary.StorageSummary) {
        |       dynamicType = <unset>,
        |       dynamicProperty = (vmodl.DynamicProperty) [],
        |       committed = 38614424818L,
        |       uncommitted = 239075873L,
        |       unshared = 34120663040L,
        |       timestamp = 2017-05-18T09:16:22.357187Z
        |    } 
        """
        return self._vobj.summary.storage

    def __repr__(self):
        return "<{0}_Details: runtime, guest, config, storage>".format(self.config.name)


class VirtualMachine(object):

    def __init__(self, vmomi_obj, service_instance, **kwargs):
        self.vim = VimBase()
        self.vim.vmomi_object = vmomi_obj
        self.vim.service_instance = service_instance
        self._operations = None
        self._dirty = False
        self.details = Details(vmomi_obj)

        self.timeout = kwargs.get('timeout', None)

    def set_credentials(self, username, password, credentials_type, default=False):
        """
        Adds the credentials for the Guest operations on this virtual machine.
        :param username: (str) Guest username. ex: domain_name\\user_name
        :param password: (str) Guest password.
        :param credentials_type: (any immutable) A dictionary key which helps to different credentials for the system. 
        :param default: (bool) If specified then for all the guest operation these credentials will be used by default.
         Unless with the operation one specifies the *credential_type* with it.
         
        | **Examples**
        | >> vm.set_credentials(username="myDomain\\domainUser", password="secret", credentials_type="user", default=True)
        | >> vm.set_credentials(username="myDomain\\domainAdmin", password="secret", credentials_type="admin")
        """
        self._dirty = True
        self.vim.credentials[credentials_type] = {'username': username, 'password': password, 'default': default}

    @property
    def operations(self):
        """
        Set of operations supported over Virtual machine.
        """
        if not self._operations or self._dirty:
            self._operations = Operations(self.vim, timeout=self.timeout)
            self._dirty = False
        return self._operations

    def __repr__(self):
        return "<VirtualMachine: {0}>".format(self.vim.vmomi_object.name)
