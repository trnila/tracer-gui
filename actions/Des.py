from PyQt5 import QtCore
from PyQt5.QtGui import QTextBlockUserData
from PyQt5.QtGui import QTextCursor
from PyQt5.QtGui import QTextDocument
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QTextEdit

from Evaluator import evalme
from Hex import MYHex, Single
from actions.Action import Action


class Item(QTextBlockUserData):
    def __init__(self, i):
        super().__init__()
        self.backtrace = i

    def __repr__(self):
        return str(self.i)

class Des(Action):
    def __init__(self, descriptor):
        super().__init__(None)
        self.descriptor = descriptor
        self.content = None

    def _get_file_id(self):
        raise NotImplementedError()

    def generate(self, dot_writer):
        raise NotImplementedError()

    def gui(self, window):
        if self.content:
            edit = QTextEdit()
            edit.setText(self.content)
            window.addTab(edit, "Content")
            return

        content = self.descriptor.process.system.read_file(self._get_file_id()).decode('utf-8', 'ignore')

        stri = ""
        start = 0
        colors = ['red', 'blue']
        col = 0
        edit = QTextEdit()

        def menu(point):
            def doit(b):
                print('ok', b)

            menu = QMenu(window)
            a = QAction("Show backtrace", window)
            a.triggered.connect(doit)
            menu.addAction(a)

            data = edit.cursorForPosition(point).block().userData()
            print(data.backtrace)
            # edit.cursorForPosition(edit.mapToGlobal(point)).insertText('test')
            menu.exec_(edit.mapToGlobal(point))

        doc = QTextDocument()
        cur = QTextCursor(doc)

        rea = []
        for operation in self.descriptor['operations']:
            if operation['type'] in ['read', 'write']:
                backtrace = "\n".join([fn['location'] for fn in operation['backtrace']]).strip()
                stri += '<span style="color:%s" title="%s">%s</span>' % (
                    colors[col % len(colors)],
                    backtrace,
                    content[start:start + operation['size']]
                )

                si = Single(content[start:start + operation['size']])
                si.backtrace = operation['backtrace']
                rea.append(si)

                # frame = QTextBlockFormat()
                # frame.setBackground(QtCore.Qt.red)
                # cur.insertBlock(frame)
                # cur.insertFrame(QTextFrameFormat())
                cur.insertText(content[start:start + operation['size']])
                cur.block().setUserData(Item(backtrace))

                start += operation['size']
                col += 1

        stri += content[start:]

        edit.setReadOnly(True)
        edit.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        edit.customContextMenuRequested.connect(menu)
        edit.setDocument(doc)

        # window.addTab(edit, "Content")
        # window.addTab(X(), "Content")
        window.addTab(MYHex(rea), "f")

    def apply_filter(self, query):
        return evalme(query, descriptor=self.descriptor) and evalme(query, process=self.descriptor.process)
