__author__ = 'rramchandani'

from pyVmomi import vim, vmodl

from ._base import BaseOperation


class VMUtils(BaseOperation):

    def clone(self, template_name, vm_name, datacenter_name,
              resource_pool_cluster=None, host=None,
              is_template=False, snapshot=None, memory=False,
              datastore_name=None, vm_folder=None, power_on=False,
              changeSID=False, nw={}, identification={},
              timezone=40, autologon=False, autologonCount=1, autologonAdminPwd="",
              fullName=None, orgName=None):
        """
        Creates a clone of this virtual machine. 
        If the virtual machine is used as a template, this method corresponds to the deploy command.
        Any % (percent) character used in this name parameter must be escaped, 
        unless it is used to start an escape sequence. 
        Clients may also escape any other characters in this name parameter.
        The privilege required on the source virtual machine depends on the source and destination types:
            - source is virtual machine, destination is virtual machine - VirtualMachine.Provisioning.Clone
            - source is virtual machine, destination is template - VirtualMachine.Provisioning.CreateTemplateFromVM
            - source is template, destination is virtual machine - VirtualMachine.Provisioning.DeployTemplate
            - source is template, destination is template - VirtualMachine.Provisioning.CloneTemplate
                If customization is requested in the CloneSpec, then the VirtualMachine.Provisioning.Customize 
                privilege must also be held on the source virtual machine.
                The Resource.AssignVMToPool privilege is also required for the resource pool specified in the CloneSpec,
                if the destination is not a template. 
                The Datastore.AllocateSpace privilege is required on all datastores where the clone is created.
                 
        :param template_name: (str)
         Source VirtualMachine/Template name.
         
        :param vm_name: (str)
         The name of the new virtual machine.
                 
        :param datacenter_name: (str)
         Datacenter name on which source image resides.
         
        :param resource_pool_cluster: (str)
         Specify a Cluster name from which Resource pool will be picked.
         The resource pool to which this virtual machine should be attached. 
         For a relocate or clone operation to a virtual machine, if the argument is not supplied, 
         the current resource pool of virtual machine is used. 
         For a clone operation to a template, this argument is ignored. 
         For a clone operation from a template to a virtual machine, this argument is required.
        
        :param host: (str)
         The target host for the virtual machine. If not specified,
            - if resource pool is not specified, current host is used.
            - if resource pool is specified, and the target pool represents a stand-alone host, the host is used.
            - if resource pool is specified, and the target pool represents a DRS-enabled cluster, 
                a host selected by DRS is used.
            - if resource pool is specified and the target pool represents a cluster without DRS enabled, 
                an InvalidArgument exception be thrown.
        
        :param is_template: (bool, optional) 
         Specifies whether or not the new virtual machine should be marked as a template.
         Default, 'False'.
        
        :param snapshot: (str, optional) 
         Snapshot reference from which to base the clone.
         If this parameter is set, the clone is based off of the snapshot point. 
         This means that the newly created virtual machine will have the same configuration as the virtual machine 
         at the time the snapshot was taken.If this property is not set then 
         the clone is based off of the virtual machine's current configuration.
         Setting this is only supported if the host this virtual machine is currently residing on supports cloning from a snapshot point. 
         Such support does not need to exist on the destination host for the clone.
         Setting this is only supported if the virtual machine supports reporting snapshot configuration information. 
         See snapshotConfigSupported. 
         Such support does not need to exist on the destination host for the clone.
        
        :param memory: (bool, optional) 
         Flag indicating whether to retain a copy of the source virtual machine's memory state in the clone. 
         Retaining the memory state during clone results in a clone in suspended state with all network adapters removed to avoid network conflicts, 
         except those with a VirtualEthernetCard.addressType of "manual". 
         Users of this flag should take special care so that, 
         when adding a network adapter back to the clone, 
         the VM is not resumed on the same VM network as the source VM, 
         or else MAC address conflicts could occur. 
         When cloning between two hosts with different CPUs outside an EVC cluster, 
         users of this flag should be aware that vCenter does not verify CPU compatibility between the 
         clone's memory state and the target host prior to the clone operation, 
         so the clone may fail to resume until it is migrated to a host with a compatible CPU.
         This flag is ignored if the snapshot parameter is unset. 
         This flag only applies for a snapshot taken on a running or suspended virtual machine with the 'memory' parameter set to true, 
         because otherwise the snapshot has no memory state. 
         This flag defaults to false.
        
        :param datastore_name:  (str, optional)
         Name of the datastore where target image is going to reside.
         Default, first datastore alphabetically from the list will be selected.
         
        :param datastore_name:  (str, optional)
         The datastore where the virtual machine should be located. If not specified, the current datastore is used.
         
        :param vm_folder: (str, optional)
         Name of the folder under which image should be listed post deployment.
         Default, will be shown under root folder.
         
        :param power_on: (bool, optional)
         Power on the target VirtualMachine after deployment.
         Default, 'False' i.e. it won't power On.
         
        :param changeSID: (bool, optional) 
         The customization process should modify the machine's security identifier (SID).
          For Vista OS, SID will always be modified.
          
        :param identification: (dict, optional)
         The Identification data object type provides information needed to join a workgroup or domain.
         The Identification data object type maps to the Identification key in thesysprep.inf answer file. 
         These values are transferred into thesysprep.inf file that VirtualCenter stores on the target virtual disk.
         ex: {'domain': DOMAIN_NAME, 'admin': ADMIN_NAME, 'pwd': ADMIN_PWD}
         
        :param timezone: (int, optional)
         The time zone for the new virtual machine. 
         Numbers correspond to time zones listed in sysprep documentation at in Microsoft Technet.
         Default, 40 to IST time zone.
         
        :param autologon: (bool, optional)
         Flag to determine whether or not the machine automatically logs on as Administrator.
         
        :param autologonCount: (int, optional)
         If the AutoLogon flag is set, then the AutoLogonCount property specifies 
         the number of times the machine should automatically log on as Administrator. 
         Generally it should be 1, but if your setup requires a number of reboots, you may want to increase it.
          
        :param autologonAdminPwd: (str, optional)
         The new administrator password for the machine. 
         To specify that the password should be set to blank (that is, no password), set the password value to NULL.
          
        :param nw: (dict, optional)
         IP settings that are specific to a particular virtual network adapter. 
         {"ip": "x.x.x.x", "subnet": "x.x.x.x", "gateway": "x.x.x.x", "dns": [PRIMARY_DNS_IP, SECONDARY_DNS_IP]}
         
        :param fullName: (str, optional)
         User's full name.
         
        :param orgName: (str, optional)
         User's organization.
        
        """

        template = self._get_obj([vim.VirtualMachine], template_name)

        datacenter = self._get_obj([vim.Datacenter], datacenter_name)

        if vm_folder:
            destfolder = self._get_obj([vim.Folder], vm_folder)
        else:
            destfolder = datacenter.vmFolder

        #cluster = self._get_obj([vim.ClusterComputeResource], template.cluster[0].info.name)

        #resource_pool = cluster.resourcePool

        # Specification for moving or copying a virtual machine to a different datastore or host.
        if datastore_name:
            datastore = self._get_obj([vim.Datastore], datastore_name, not_found_return_none=True)
        else:
            datastore = None
            #datastore = self._get_obj([vim.Datastore], template.datastore[0].info.name)

        if resource_pool_cluster:
            _ = self._get_obj([vim.ResourcePool])
            resources = [i for i in _ if i.owner.name == resource_pool_cluster]
            resource = resources[0] if resources else None
        else:
            resource = None

        if host:
            on_host = self._get_obj([vim.HostSystem], host, not_found_return_none=True)
        else:
            on_host = None

        """
        resource = None
        if resource_pool is not None:
            resource_pools = self._get_obj([vim.ResourcePool])
            for resource_pool_ in resource_pools:
                if resource_pool_.parent.name == resource_pool:
                    resource = resource_pool_
                    break
        
        on_host = None
        if host is not None:
            hosts = self._get_obj([vim.HostSystem])
            for host_ in hosts:
                if host_.parent.name == host:
                    on_host = host_
                    break
        """

        relospec = vim.vm.RelocateSpec()
        if datastore is not None:
            relospec.datastore = datastore

        if on_host is not None:
            relospec.host = on_host

        if resource_pool_cluster is not None:
            relospec.pool = resource

        # Specification for a virtual machine cloning operation.
        clonespec = vim.vm.CloneSpec()
        clonespec.location = relospec
        clonespec.powerOn = power_on
        clonespec.template = is_template
        clonespec.memory = memory

        from_snapshot = self._get_snapshot_list().get(snapshot, None)
        if from_snapshot is None:
            clonespec.snapshot = from_snapshot

        # The Specification data object type contains information required to customize a virtual machine
        # when deploying it or migrating it to a new host.
        custom = vim.vm.customization
        spec = custom.Specification()
        sysprep = vim.vm.customization.Sysprep()

        if changeSID:
            options = vim.vm.customization.WinOptions
            spec.options = options()
            spec.options.changeSID = changeSID

        if fullName and orgName:
            user_data = vim.vm.customization.UserData()
            user_data.fullName = fullName
            user_data.orgName = orgName
            user_data.computerName = vim.vm.customization.FixedName(name=vm_name) #fixed_name

            sysprep.userData = user_data

        # Customization Identification data
        if identification and isinstance(identification, dict):
            identity = vim.vm.customization.Identification()
            domainName = identification.get('domain', '')
            workGroup = identification.get('workgroup', '')

            if domainName:
                # Password
                pwd = vim.vm.customization.Password()
                pwd.value = identification.get('password', 'ca$hc0w')
                pwd.plainText = True

                identity.joinDomain = domainName
                identity.domainAdmin = identification.get('admin', 'administrator')
                identity.domainAdminPassword = pwd
            elif workGroup:
                identity.joinDomain = workGroup

            sysprep.identification = identity

            # Gui Unattended
            gui = vim.vm.customization.GuiUnattended()
            gui.timeZone = timezone
            gui.autoLogon = 1 if autologon else 0

            if autologon:
                gui.autoLogonCount = autologonCount
                pwd = vim.vm.customization.Password()

                if not autologonAdminPwd:
                    autologonAdminPwd = identification.get('password', 'ca$hc0w')

                pwd.value = autologonAdminPwd
                pwd.plainText = True
                gui.password = pwd

            sysprep.guiUnattended = gui

        # Nic settings
        if nw and isinstance(nw, dict):
            nic = vim.vm.customization.AdapterMapping()
            adapter = vim.vm.customization.IPSettings()
            adapter.ip = vim.vm.customization.DhcpIpGenerator()

            _ = nw.get("ip")
            if _ is not None:
                fixed_ip = vim.vm.customization.FixedIp()
                fixed_ip.ipAddress = _
                adapter.ip = fixed_ip

            _ = nw.get("subnet")
            if _ is not None: adapter.subnetMask = _

            _ = nw.get("gateway")
            if _ is not None: adapter.gateway = _

            _ = nw.get("dns")
            if _ is not None: adapter.dnsServerList = _

            nic.adapter = adapter

            spec.nicSettingMap = [nic]

            spec.globalIPSettings = vim.vm.customization.GlobalIPSettings()
            _ = nw.get("dns")
            if _ is None: spec.globalIPSettings.dnsServerList = _

        spec.identity = sysprep

        clonespec.customization = spec

        task = template.CloneVM_Task(folder=destfolder, name=vm_name, spec=clonespec)
        self._wait_for_task_to_complete(task)
        return template
