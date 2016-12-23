import socket

from objects.Object import Object


class Descriptor(Object):
    def __init__(self, process, data):
        self.data = data
        self.process = process

    def __getitem__(self, item):
        return self.data[item]

    def __contains__(self, item):
        return item in self.data

    def get_id(self):
        if self['type'] == 'file':
            return "%s_%s" % (self.process.system.resource_path, self['path'])

        if self['type'] == 'pipe':
            return "%s_%s" % (id(self.process.system), self['pipe_id'])

        if self['type'] == 'socket' and self['domain'] in [socket.AF_INET, socket.AF_INET6]:
            try:
                parts = sorted([
                    self['local']['address'],
                    str(self['local']['port']),
                    self['remote']['address'],
                    str(self['remote']['port']),
                ])

                return "socket_%s" % (":".join(parts))
            except:
                pass

        return self.get_label()

    def get_label(self):
        if self['type'] == 'socket':
            if self['domain'] == socket.AF_UNIX:
                return "unix:%s" % (self['remote'])

            if self['domain'] in [socket.AF_INET, socket.AF_INET6] and self['local']:  # TODO: quickfix
                if self['remote'] is None:
                    return "%s:%d" % (self['local']['address'], self['local']['port'])

                return "%s:%d\\n<->\\n%s:%d" % (
                    self['local']['address'], self['local']['port'],
                    self['remote']['address'], self['remote']['port']
                )
            return "socket: %s #%s" % (self['domain'], self['socket_id'])

        if self['type'] == 'file':
            return self['path']

        if self['type'] == 'pipe':
            return 'pipe: %d' % self['pipe_id']
