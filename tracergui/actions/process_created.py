import os

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit

from tracergui.actions.action import Action
from tracergui.evaluator import evalme


class RegionWidget(QMainWindow):
    def __init__(self, parent=None):
        super(RegionWidget, self).__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../widgets/region2.ui'), self)
        self.next.clicked.connect(self.show_next)
        self.prev.clicked.connect(self.show_prev)
        self.num.editingFinished.connect(self.change_frame)

        self.frame = 0
        self.total_frames = 0

    def change_frame(self):
        self.frame = self.num.text()
        self.load(self.frame)

    def show_next(self, a):
        self.frame = min(self.frame + 1, self.total_frames)
        self.load(self.frame)

    def show_prev(self):
        self.frame = max(0, self.frame - 1)
        self.load(self.frame)

    def set_region(self, region):
        self.region = region
        self.frame = 0
        self.total_frames = int(os.path.getsize(region['content']) / region['captured_size']) - 1
        self.load(0)
        self.show()

    def load(self, n):
        f = open(self.region['content'], "r", errors='replace')
        size = self.region['captured_size']
        f.seek(n * size)
        self.content.setText(f.read(size))
        self.num.setValue(self.frame)


class ProcessCreated(Action):
    def __init__(self, system, process, parent=None):
        super().__init__(system)
        self.process = process
        self.parent = parent

    def generate(self, dot_writer):
        dot_writer.write_node(self.process['pid'], self.process['executable'], data=self, shape='rect')

        if self.parent:
            dot_writer.write_edge(self.parent['pid'], self.process['pid'])

    def gui(self, window, graph):
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderItem(0, QTableWidgetItem("Variable"))
        table.setHorizontalHeaderItem(1, QTableWidgetItem("Value"))
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setRowCount(len(self.process['env']))

        cmdline = QTextEdit()
        cmdline.setPlainText(' '.join(self.process['arguments']))

        row = 0
        for key, value in self.process['env'].items():
            table.setItem(row, 0, QTableWidgetItem(key))
            table.setItem(row, 1, QTableWidgetItem(value))
            row += 1

        window.addTab(cmdline, "Command")
        window.addTab(table, "Environments")

        if 'regions' in self.process and self.process['regions']:
            mmaps = QTableWidget()
            mmaps.setColumnCount(2)
            mmaps.setHorizontalHeaderItem(0, QTableWidgetItem("Variable"))
            mmaps.setRowCount(len(self.process['regions']))
            mmaps.clicked.connect(self.row_clicked)

            for row, mmap in enumerate(self.process['regions']):
                mmaps.setItem(row, 0, QTableWidgetItem("0x{:x}".format(mmap['address'])))
                mmaps.setItem(row, 1, QTableWidgetItem(str(mmap['size'])))

            window.addTab(mmaps, "Mmaps")

    def row_clicked(self, index):
        region = self.process['regions'][index.row()]
        if 'content' in region:
            self.window.widgets['region'].set_region(region)

    def apply_filter(self, query):
        return evalme(query, process=self.process)

    def __repr__(self):
        return "[%d] created %d" % (self.process['pid'], self.parent['pid'] if self.parent else 0)
