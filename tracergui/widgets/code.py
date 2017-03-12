from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QWidget

from tracergui.ui.code import Ui_code
from tracergui.utils import read_file, save_file


class Code(QWidget, Ui_code):
    changed = pyqtSignal(bytes)

    def __init__(self, flags, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        self.setupUi(self)

        self.content.setPlainText("result = raw")
        self.toolButton.clicked.connect(self.execute)
        self.btn_load_file.clicked.connect(self.load_handler)
        self.saveButton.clicked.connect(self.save_handler)
        self.saveAsBtn.clicked.connect(self.save_as_handler)

        self.raw_content = b""
        self.filename = None

    @staticmethod
    def create_file_dialog():
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        return dialog

    def load_handler(self):
        dialog = self.create_file_dialog()
        if dialog.exec_():
            self.filename = dialog.selectedFiles()[0]
            self.content.setPlainText(read_file(self.filename))

    def save_as_handler(self):
        self.filename = None
        self.save_handler()

    def save_handler(self):
        if not self.filename:
            dialog = self.create_file_dialog()
            if dialog.exec_():
                self.filename = dialog.selectedFiles()[0]

        save_file(self.filename, self.content.toPlainText())

    def set_content(self, content):
        self.raw_content = content
        self.execute()

    def execute(self):
        try:
            env = {"result": "", "raw": self.raw_content}
            exec(self.content.toPlainText(), env)

            if isinstance(env['result'], str):
                env['result'] = env['result'].encode('utf-8')

            self.changed.emit(env['result'])
        except Exception as e:
            QMessageBox().critical(None, "Error", str(e.args))
