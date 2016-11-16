from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit

from Evaluator import evalme
from actions.Action import Action


class ProcessCreated(Action):
    def __init__(self, system, process, parent=None):
        super().__init__(system)
        self.process = process
        self.parent = parent

    def generate(self, dot_writer):
        dot_writer.write_node(self.process['pid'], self.process['executable'], data=self, shape='rect')
        dot_writer.write_edge(self.parent['pid'], self.process['pid'])

    def gui(self, window):
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

    def apply_filter(self, query):
        return evalme(query, process=self.process)

    def __repr__(self):
        return "[%d] created %d" % (self.process['pid'], self.parent['pid'] if self.parent else 0)
