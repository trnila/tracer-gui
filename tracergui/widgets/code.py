from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QWidget

from tracergui.ui.code import Ui_code


class Code(QWidget, Ui_code):
    changed = pyqtSignal(bytes)

    def __init__(self, flags, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        self.setupUi(self)

        self.content.setPlainText("result = raw")
        self.toolButton.clicked.connect(self.execute)
        self.btn_load_file.clicked.connect(self.load_from_file)
        self.raw_content = b""

    def load_from_file(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        if dialog.exec_():
            file_name = dialog.selectedFiles()[0]
            with open(file_name) as f:
                self.content.setPlainText(f.read())

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
