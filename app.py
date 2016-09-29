from PyQt5 import QtWidgets

from MainWindow import MainWindow

app = QtWidgets.QApplication([])
window = MainWindow()
window.setWindowTitle('GUI')
window.setFixedSize(1024, 768)
window.show()
app.exec_()
