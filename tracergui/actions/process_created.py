import struct
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget

from tracergui.actions.action import Action
from tracergui.evaluator import evalme

class MyDialog(QMainWindow):
    def __init__(self, parent=None):
        super(MyDialog, self).__init__(parent)

        self.content = QTextEdit()

        btn = QPushButton()
        self.n = 0
        btn.clicked.connect(self.next)

        widget = QWidget()
        widget.setLayout(QVBoxLayout())
        widget.layout().addWidget(btn)
        widget.layout().addWidget(self.content)

        self.setCentralWidget(widget)

        self.load(0)

    def next(self, a):
        self.n += 1
        self.load(self.n)


    def load(self, n):
        f = open("/tmp/rep/139987621609472_32", "rb")
        size = struct.unpack("i", f.read(4))[0]

        f.seek(n * size)

        self.content.setText(f.read(size).decode('utf-8'))


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


        mmaps = QTableWidget()
        mmaps.setColumnCount(2)
        mmaps.setHorizontalHeaderItem(0, QTableWidgetItem("Variable"))
        mmaps.setRowCount(len(self.process['mmap_content']))
        mmaps.clicked.connect(self.viewClicked)


        for row, mmap in enumerate(self.process['mmap_content']):
            mmaps.setItem(row, 0, QTableWidgetItem("{}".format(mmap['address'])))
            mmaps.setItem(row, 1, QTableWidgetItem("test"))
            self.mmap = mmap



        window.addTab(cmdline, "Command")
        window.addTab(table, "Environments")
        window.addTab(mmaps, "Mmaps")

        d = MyDialog(window)
        d.show()

    def viewClicked(self, index):
        #d = MyDialog(window)
        #d.show()
        pass


    def apply_filter(self, query):
        return evalme(query, process=self.process)

    def __repr__(self):
        return "[%d] created %d" % (self.process['pid'], self.parent['pid'] if self.parent else 0)
