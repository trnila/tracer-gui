from PyQt5.QtWidgets import QTextBrowser

from tracergui import maps
from tracergui import utils
from tracergui.actions.des import Des
from tracergui.evaluator import evalme


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

            content_link = ""
            if self.find_region(item['region_id']):
                content_link = "<a href='#{}'>Show content</a>".format(item['region_id'])

            return "0x%X - 0x%X (%s) %s %s %s %s" % (
                item['address'],
                item['address'] + item['length'],
                utils.format_bytes(item['length']),
                maps.mmap_prots.format(item['prot']),
                maps.mmap_maps.format(item['flags']),
                [r(i) for i in item['regions']],
                content_link
            )

        value = "\n".join(map(_format_mmap, self.descriptor['mmap']))

        edit = QTextBrowser()
        edit.setHtml(value)
        edit.anchorClicked.connect(self.on_anchor_clicked)

        window.addTab(edit, "Content")

    def on_anchor_clicked(self, url):
        region_id = int(url.toString()[1:])
        self.window.widgets['region'].set_region(self.find_region(region_id))

    def apply_filter(self, query):
        return evalme(query, descriptor=self.descriptor, type='mmap') and evalme(query, process=self.descriptor.process)

    def __repr__(self):
        return "[%d] mmap" % self.descriptor.process['pid']

    def find_region(self, id):
        for region in self.process.data.get('regions', []):
            if id == region['region_id']:
                return region

        return None
