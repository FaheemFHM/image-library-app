
import sys
from PyQt5.QtWidgets import QApplication

from components.Window import MainWindow

def load_stylesheet(path):
    with open(path, "r") as file:
        return file.read()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    stylesheet = load_stylesheet("style.qss")
    app.setStyleSheet(stylesheet)

    media_path = "../media"
    window = MainWindow(media_path)
    window.show()
    
    sys.exit(app.exec_())
