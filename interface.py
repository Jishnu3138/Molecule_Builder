from PySide6.QtWidgets import QApplication, QWidget
import sys

print("Hello World")

app = QApplication(sys.argv)

window = QWidget()
window.show()

app.exec()