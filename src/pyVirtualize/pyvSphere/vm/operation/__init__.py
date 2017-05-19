__author__ = 'rramchandani'


from .file import FileOperations
from .process import ProcessOperations
from .power import PowerOperations
from .snapshot import SnapshotOperations

from .admin import AdminOperations
from .vmutils import VMUtils


class Operations(object):

    def __init__(self, vim, **kwargs):
        for clsname, cls in {'file': FileOperations, 'process': ProcessOperations, 'power': PowerOperations,
                             'snapshot': SnapshotOperations, 'admin': AdminOperations,
                             'vmutils': VMUtils}.items():
            _ = cls(vim, **kwargs)
            setattr(self, clsname, _)
