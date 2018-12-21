import network
from .conf import module_name


name = 'padl.' + module_name
print('Module: ' + name)
module = __import__(name)
sub_module = getattr(module, module_name)
DbTransaction = sub_module.DbTransaction


class Job(network.Job):
    def get_iso_class(self):
        return DbTransaction
