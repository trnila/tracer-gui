from PyQt5.QtWidgets import QTextEdit

from tracergui import maps
from tracergui import utils
from tracergui.Evaluator import evalme
from tracergui.actions.Des import Des


class Mmap(Des):
    def generate(self, dot_writer):
        dot_writer.write_biedge(
            self.descriptor.process['pid'],
            self.descriptor.get_id(),
            data=self
        )

    def gui(self, window, graph):
        file = open(self.descriptor['path'], 'rb')

        def _format_mmap(item):
            def r(range):
                start, stop = range.split('-', 2)
                start = int(start, 16) - item['address']
                stop = int(stop, 16) - item['address']

                file.seek(start)
                return file.read(stop - start).decode('utf-8', 'ignore')

            return "0x%X - 0x%X (%s) %s %s %s" % (
                item['address'],
                item['address'] + item['length'],
                utils.format_bytes(item['length']),
                maps.mmap_prots.format(item['prot']),
                maps.mmap_maps.format(item['flags']),
                [r(i) for i in item['regions']]
            )

        value = "\n".join(map(_format_mmap, self.descriptor['mmap']))

        edit = QTextEdit()
        edit.setText(value)

        window.addTab(edit, "Content")

    def apply_filter(self, query):
        return evalme(query, descriptor=self.descriptor, type='mmap') and evalme(query, process=self.descriptor.process)

    def __repr__(self):
        return "[%d] mmap" % self.descriptor.process['pid']
