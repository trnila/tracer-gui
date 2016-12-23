from Evaluator import evalme
from actions.Des import Des


class ReadDes(Des):
    def generate(self, dot_writer):
        dot_writer.write_edge(
            self.descriptor.get_id(),
            self.descriptor.process['pid'],
            data=self,
        )

    def _get_file_id(self):
        return self.descriptor['read_content']

    def type(self):
        return 'read'

    def __repr__(self):
        return "[%d] read: %s" % (self.descriptor.process['pid'], self.descriptor)

    def apply_filter(self, query):
        return evalme(query, descriptor=self.descriptor, type='read') and evalme(query, process=self.descriptor.process)
