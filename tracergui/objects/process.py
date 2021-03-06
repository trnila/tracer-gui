from tracergui.objects.descriptor import Descriptor
from tracergui.objects.object import Object


class Process(Object):
    def __init__(self, system, data, parent=None):
        self.system = system
        self.data = data
        self.parent = parent

        self.data['descriptors'] = [Descriptor(self, i) for i in self.data['descriptors']]

    def __getitem__(self, item):
        return self.data[item]

    def __contains__(self, item):
        return item in self.data
