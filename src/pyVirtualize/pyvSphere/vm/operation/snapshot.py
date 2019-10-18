__author__ = 'rramchandani'


from ._base import BaseOperation


class SnapshotOperations(BaseOperation):
    """
    SnapshotOperations provides APIs to manipulate the snapshot operations on the Virtual Machine.
    """
    
    def create(self, name, desc="", memory=True, quiesce=False):
        """
        Creates a new snapshot of this virtual machine. 
        As a side effect, this updates the current snapshot.
        Snapshots are not supported for Fault Tolerance primary and secondary virtual machines.
        Any % (percent) character used in this name parameter must be escaped, 
        unless it is used to start an escape sequence. 
        Clients may also escape any other characters in this name parameter.
        
        :param name: (str)
         The name for this snapshot. The name need not be unique for this virtual machine.
         
        :param desc: (str, optional)
         A description for this snapshot. If omitted, a default description may be provided.
         
        :param memory: (bool, optional)
         If TRUE, a dump of the internal state of the virtual machine (basically a memory dump) 
         is included in the snapshot. 
         Memory snapshots consume time and resources, and thus take longer to create. 
         When set to FALSE, the power state of the snapshot is set to powered off. 
         `capabilities`_ indicates whether or not this virtual machine supports this operation.
         Default: 'True'
         
        :param quiesce: (bool, optional)
         If TRUE and the virtual machine is powered on when the snapshot is taken, 
         VMware Tools is used to quiesce the file system in the virtual machine. 
         This assures that a disk snapshot represents a consistent state of the guest file systems. 
         If the virtual machine is powered off or VMware Tools are not available, the quiesce flag is ignored.
        """
        task_ = self.vmomi_object.CreateSnapshot_Task(
            name=name, description=desc, memory=memory, quiesce=quiesce
        )
        self._wait_for_task_to_complete(task=task_)

    def revert(self, name):
        """
        Change the execution state of the virtual machine to the state of this snapshot.
        
        :param name: (str)
         Name of the snapshot.
        """
        snapshots = self._get_snapshot_list()
        if name not in snapshots:
            raise ValueError("Snapshot '{0}' doesn't exists.".format(name))
        snapshot = snapshots.get(name)
        task_ = snapshot.RevertToSnapshot_Task()
        self._wait_for_task_to_complete(task=task_)

    def revert_to_current(self):
        """
        Change the execution state of the virtual machine to the state of current snapshot.
        """
        snapshot = self.vmomi_object.snapshot.currentSnapshot
        task_ = snapshot.RevertToSnapshot_Task()
        self._wait_for_task_to_complete(task=task_)

    def remove(self, name):
        """
        Removes the specified snapshot from the machine.

        :param name: (str)
         Name of the snapshot.
        """
        snapshots = self._get_snapshot_list()
        if not snapshots.has_key(name):
            raise ValueError("Snapshot '{0}' doesn't exists.".format(name))
        snapshot = snapshots.get(name)
        task_ = snapshot.RemoveSnapshot_Task(False)
        self._wait_for_task_to_complete(task=task_)

    def remove_current(self):
        """
        Removes the current snapshot from the machine.
        """
        snapshot = self.vmomi_object.snapshot.currentSnapshot
        task_ = snapshot.RemoveSnapshot_Task()
        self._wait_for_task_to_complete(task=task_)

    def remove_all(self):
        """
        Removes all snapshots from the machine.
        """
        for snapshot in self._get_snapshot_list():
            task_ = snapshot.RemoveSnapshot_Task()
            self._wait_for_task_to_complete(task=task_)
