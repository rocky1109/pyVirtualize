__author__ = 'rramchandani'


from ._base import BaseOperation


class PowerOperations(BaseOperation):
    """
    PowerOperations provides APIs to manipulate the guest operating system power options.
    """

    def power_on(self, sync=True, wait_for_guest_ready=True):
        """
        Powers on this virtual machine.
        
        :param sync: (bool)
         When 'sync' is set to True, command will wait until VM is completely powered On.
         Else it will just trigger the power On and returns back.
        
        :param wait_for_guest_ready: (bool)
         When 'wait_for_guest_ready' is to True, command will wait until guest operations is ready i.e. logged-in successfully.
         Else it will return when it power's On completely.
         'wait_for_guest_ready' works when 'sync' is enabled/True.
         
        """
        self.vmomi_object.PowerOn()
        if sync: self._wait_for_power_on(wait_for_guest_ready)

    def power_off(self, sync=True):
        """
        Performs the hard power off on this virtual machine.

        :param sync: (bool)
         When 'sync' is set to True, command will wait until VM is completely powered Off.
         Else it wait just trigger the power Off and returns back.

        """
        self.vmomi_object.PowerOff()
        if sync: self._wait_for_power_off()

    def shutdown(self, sync=True):
        """
        Issues a command to the guest operating system asking it to perform a clean shutdown of all services.
        
        :param sync: (bool)
         When 'sync' is set to True, command will wait until VM is completely powered Off.
         Else it will just trigger the shutdown and returns back.
         
        """
        self.vmomi_object.ShutdownGuest()
        if sync: self._wait_for_power_off()

    def restart(self, sync=True):
        """
        Sends the restart command to guest operating system.
        
        :param sync: (bool)
         When 'sync' is set to True, command will wait until VM is completely powered Off and powered On back.
         Else it will just trigger the restart and returns back;; but it will wait till shutdown of the system atleast.
         
        """
        self.shutdown(sync=True)
        self.power_on(sync)

    def reset(self, sync=True):
        """
        Resets power on this virtual machine. 
        If the current state is poweredOn, then this method first performs powerOff(hard). 
        Once the power state is poweredOff, then this method performs powerOn(option).
        Although this method functions as a powerOff followed by a powerOn, 
        the two operations are atomic with respect to other clients, 
        meaning that other power operations cannot be performed until the reset method completes.
        
        :param sync: (bool)
         When 'sync' is set to True, command will wait until VM is completely powered Off and powered On back.
        :return: 
        """
        self.vmomi_object.ResetVM_Task()
        if sync: self._wait_for_power_on()
