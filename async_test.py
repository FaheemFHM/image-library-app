from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import QThread, QMetaObject, Qt, Q_ARG

from database import MediaDatabase
from database import DatabaseWorker

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Async Media Loader")
        layout = QVBoxLayout(self)

        # --- Thread + Worker ---
        self.thread = QThread()
        self.worker = DatabaseWorker("database.db")
        self.worker.moveToThread(self.thread)

        # When the thread starts, initialize DB inside that thread
        self.thread.started.connect(self.worker.init_db)
        self.thread.start()

        # Connect worker signals
        self.worker.results_ready.connect(self.handle_results)
        self.worker.error.connect(self.handle_error)

        # UI
        self.button = QPushButton("Load first media")
        self.button.clicked.connect(self.load_media)
        layout.addWidget(self.button)

        self.label = QLabel("Waiting...")
        layout.addWidget(self.label)

    def load_media(self):
        # Example: call get_first_media(limit=5, media_type='image')
        QMetaObject.invokeMethod(
            self.worker,
            "run_task",
            Qt.QueuedConnection,
            Q_ARG(str, "get_first_media"),
            Q_ARG(tuple, (5, "image")),
            Q_ARG(dict, {})  # kwargs empty here
        )
        print("async")

    def handle_results(self, method_name, result):
        if method_name == "get_first_media":
            self.label.setText(f"Got {len(result)} items")
            print(result)
        else:
            self.label.setText(f"{method_name} returned: {result}")
            print(f"{method_name} returned: {result}")

    def handle_error(self, method_name, message):
        self.label.setText(f"Error in {method_name}: {message}")
        print(f"Error in {method_name}: {message}")


if __name__ == "__main__":
    app = QApplication([])
    win = MainWindow()
    win.show()
    app.exec_()
