__author__ = 'rramchandani'


class Datastore(object):

    def __init__(self, vmomi_object):
        self.vmomi_object = vmomi_object

    @property
    def totalCapacity(self):
        return int(self.vmomi_object.summary.capacity / 1024)

    @property
    def freeSpace(self):
        return int(self.vmomi_object.summary.freeSpace / 1024)

    @property
    def storageType(self):
        return self.vmomi_object.summary.type

    @property
    def url(self):
        return self.vmomi_object.summary.url

    @property
    def name(self):
        return self.vmomi_object.name

    @property
    def accessible(self):
        return self.vmomi_object.summary.accessible
