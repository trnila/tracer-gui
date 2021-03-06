from tracergui.actions.des import Des
from tracergui.evaluator import evalme


class WriteDes(Des):
    def generate(self, dot_writer):
        dot_writer.write_edge(
            self.descriptor.process['pid'],
            self.descriptor.get_id(),
            data=self,
        )

    def _get_file_id(self):
        return self.descriptor['write_content']

    def type(self):
        return 'write'

    def __repr__(self):
        return "[%d] write: %s" % (self.descriptor.process['pid'], self.descriptor)

    def apply_filter(self, query):
        return evalme(query, descriptor=self.descriptor, type='write') and evalme(query,
                                                                                  process=self.descriptor.process)
