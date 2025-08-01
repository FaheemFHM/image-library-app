
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow,
    QHBoxLayout, QVBoxLayout, QGridLayout, QFormLayout,
    QLabel, QPushButton, QLineEdit, QSpinBox, QComboBox, QCheckBox,
    QTextEdit, QScrollArea, QFrame, QStackedWidget,
    QTabWidget, QToolBar, QAction, QSizePolicy, QFileDialog, QMessageBox,
    QDateTimeEdit
)
from PyQt5.QtGui import (
    QIcon, QPixmap, QFont, QCursor, QColor, QPainter, QPalette
)
from PyQt5.QtCore import (
    Qt, QSize, QTimer, QDateTime, QDate, QTime, QPropertyAnimation, QPoint, QRect, pyqtSignal
)

tags = [
    "Home", "School", "Food", "Family", "Holidays",
    "Pets", "Car", "Work", "Travel", "Nature",
    "Friends", "Sports", "Events", "Art", "Technology"
]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Media Manager")
        self.setWindowIcon(QIcon("icons/app_icon.png"))

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Sidebar
        self.sidebar1 = QWidget()
        self.sidebar1.setProperty("class", "sidebar")
        self.sidebar1.setFixedWidth(200)
        sidebar_layout = QVBoxLayout()
        self.sidebar1.setLayout(sidebar_layout)

        # Sidebar Options
        header = QLabel("Search")
        header.setProperty("class", "sidebar_header")
        header.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(header)

        input_field = QLineEdit()
        input_field.setPlaceholderText("Enter Search Query...")
        sidebar_layout.addWidget(input_field)

        toggle = ToggleButton("Name", "ID")
        sidebar_layout.addWidget(toggle)

        header = QLabel("Sort")
        header.setProperty("class", "sidebar_header")
        header.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(header)

        dropdown = QComboBox()
        dropdown.addItems(["Date", "Name", "ID", "Size", "Height", "Width"])
        sidebar_layout.addWidget(dropdown)

        toggle = ToggleButton("Asc", "Desc")
        sidebar_layout.addWidget(toggle)

        header = QLabel("Tags")
        header.setProperty("class", "sidebar_header")
        header.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(header)

        tag_grid = TagGrid(tags)
        sidebar_layout.addWidget(tag_grid)

        sidebar_layout.addStretch()
        main_layout.addWidget(self.sidebar1)

        # Sidebar
        self.sidebar2 = QWidget()
        self.sidebar2.setProperty("class", "sidebar")
        self.sidebar2.setFixedWidth(200)
        sidebar_layout = QVBoxLayout()
        self.sidebar2.setLayout(sidebar_layout)

        # Sidebar Options
        header = QLabel("Filters")
        header.setProperty("class", "sidebar_header")
        header.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(header)

        header = QLabel("Favourite")
        header.setProperty("class", "sidebar_sub_header")
        header.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(header)

        dropdown = QComboBox()
        dropdown.addItems(["Any", "Favourites", "Non-Favourites"])
        sidebar_layout.addWidget(dropdown)

        header = QLabel("File Type")
        header.setProperty("class", "sidebar_sub_header")
        header.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(header)
        
        dropdown = QComboBox()
        dropdown.addItems(["Any", "Images", "Videos"])
        sidebar_layout.addWidget(dropdown)

        header = QLabel("Format")
        header.setProperty("class", "sidebar_sub_header")
        header.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(header)
        
        dropdown = QComboBox()
        dropdown.addItems(["Any", "PNG", "JPEG", "VIDEO", "MP3"])
        sidebar_layout.addWidget(dropdown)

        header = QLabel("Camera")
        header.setProperty("class", "sidebar_sub_header")
        header.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(header)
        
        dropdown = QComboBox()
        dropdown.addItems(["Any", "Samsung", "Nokia", "Apple"])
        sidebar_layout.addWidget(dropdown)
        
        header = QLabel("File Size")
        header.setProperty("class", "sidebar_sub_header")
        header.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(header)

        range_widget = RangeWidget(0, 999999999)
        sidebar_layout.addWidget(range_widget)
        
        header = QLabel("Image Height")
        header.setProperty("class", "sidebar_sub_header")
        header.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(header)
        
        range_widget = RangeWidget(0, 99999)
        sidebar_layout.addWidget(range_widget)
        
        header = QLabel("Image Width")
        header.setProperty("class", "sidebar_sub_header")
        header.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(header)
        
        range_widget = RangeWidget(0, 99999)
        sidebar_layout.addWidget(range_widget)
        
        header = QLabel("Times Viewed")
        header.setProperty("class", "sidebar_sub_header")
        header.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(header)
                
        range_widget = RangeWidget(0, 99999999)
        sidebar_layout.addWidget(range_widget)
        
        header = QLabel("Total Time Viewed")
        header.setProperty("class", "sidebar_sub_header")
        header.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(header)
                
        range_widget = RangeWidget(0, 99999999)
        sidebar_layout.addWidget(range_widget)
        
        header = QLabel("Date Captured")
        header.setProperty("class", "sidebar_sub_header")
        header.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(header)

        date_time = DateTimeInput(False)
        sidebar_layout.addWidget(date_time)

        date_time = DateTimeInput()
        sidebar_layout.addWidget(date_time)
        
        header = QLabel("Date Added")
        header.setProperty("class", "sidebar_sub_header")
        header.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(header)

        date_time = DateTimeInput(False)
        sidebar_layout.addWidget(date_time)

        date_time = DateTimeInput()
        sidebar_layout.addWidget(date_time)

        header = QLabel("Reset")
        header.setProperty("class", "sidebar_header")
        header.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(header)

        button = QPushButton("Search")
        sidebar_layout.addWidget(button)
        button = QPushButton("Sort")
        sidebar_layout.addWidget(button)
        button = QPushButton("Tags")
        sidebar_layout.addWidget(button)
        button = QPushButton("Filters")
        sidebar_layout.addWidget(button)

        sidebar_layout.addStretch()
        main_layout.addWidget(self.sidebar2)

        # Sidebar
        sidebar = QWidget()
        sidebar.setProperty("class", "sidebar")
        sidebar.setObjectName("slideshow_panel")
        sidebar.setFixedWidth(50)
        sidebar_layout = QVBoxLayout()
        sidebar.setLayout(sidebar_layout)

        # Sidebar Options
        button = MediaControlButton("icons/play.png", alt_icon="icons/pause.png")
        sidebar_layout.addWidget(button)
        button.clicked.connect(self.toggle_sidebars_hide)

        button = MediaControlButton("icons/stop.png")
        sidebar_layout.addWidget(button)
        button.clicked.connect(self.show_sidebars)


        button = MediaControlButton("icons/fast_forwards.png")
        sidebar_layout.addWidget(button)

        button = MediaControlButton("icons/fast_backwards.png")
        sidebar_layout.addWidget(button)

        button = MediaControlButton("icons/fastest_forwards.png")
        sidebar_layout.addWidget(button)

        button = MediaControlButton("icons/fastest_backwards.png")
        sidebar_layout.addWidget(button)

        button = MediaControlButton("icons/skip_forwards.png")
        sidebar_layout.addWidget(button)

        button = MediaControlButton("icons/skip_backwards.png")
        sidebar_layout.addWidget(button)

        button = MediaControlButton("icons/loop_off.png", alt_icon="icons/loop_on.png")
        sidebar_layout.addWidget(button)

        button = MediaControlButton("icons/shuffle_off.png", alt_icon="icons/shuffle_on.png")
        sidebar_layout.addWidget(button)

        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)
        
        # Main Content Area
        main_content = QWidget()
        main_content_layout = QVBoxLayout()
        main_content.setLayout(main_content_layout)

        main_content_layout.addWidget(QLabel("Main Content Area"))
        main_content_layout.addStretch()
        main_layout.addWidget(main_content)

        # Update Main Layout
        main_content.setSizePolicy(sidebar.sizePolicy().Expanding, sidebar.sizePolicy().Expanding)
        self.showMaximized()

    def toggle_sidebars_hide(self):
        if self.sidebar1.isVisible() or self.sidebar2.isVisible():
            self.sidebar1.hide()
            self.sidebar2.hide()

    def show_sidebars(self):
        if not self.sidebar1.isVisible() or not self.sidebar2.isVisible():
            self.sidebar1.show()
            self.sidebar2.show()


def load_stylesheet(path):
    with open(path, "r") as file:
        return file.read()

class MediaControlButton(QPushButton):
    def __init__(self, icon_path, alt_icon="", size=36, icon_size=24, parent=None):
        super().__init__(parent)

        self.icon_on = QIcon(alt_icon)
        self.icon_off = QIcon(icon_path)
        self.setIcon(self.icon_off)
        self.is_on = False
        
        self.setIconSize(QSize(icon_size, icon_size))
        self.setFixedSize(size, size)
        self.setProperty("class", "media_button")

        if alt_icon != "":
            self.clicked.connect(self.toggle)

    def toggle(self):
        self.is_on = not self.is_on
        self.setIcon(self.icon_on if self.is_on else self.icon_off)

    def is_checked(self):
        return self.is_on

    def set_checked(self, value: bool):
        self.is_on = value
        self.toggle_button.setChecked(value)
        self.toggle()
        
class DateTimeInput(QWidget):
    def __init__(self, use_current_time=True):
        super().__init__()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.datetime_edit = QDateTimeEdit()
        default_value = QDateTime(QDateTime.currentDateTime() if use_current_time else QDateTime(QDate(1950, 1, 1), QTime(0, 0, 0)))
        self.datetime_edit.setDateTime(default_value)
        self.datetime_edit.setCalendarPopup(True)

        layout.addWidget(self.datetime_edit)
        self.setLayout(layout)

class RangeWidget(QWidget):
    def __init__(self, min_value=0, max_value=9999):
        super().__init__()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # "From" Input
        self.from_spin = QSpinBox()
        self.from_spin.setRange(min_value, max_value)
        layout.addWidget(self.from_spin)

        # "To" Input
        self.to_spin = QSpinBox()
        self.to_spin.setRange(min_value, max_value)
        layout.addWidget(self.to_spin)
        
        self.setLayout(layout)

class TagGrid(QWidget):
    def __init__(self, tags, columns=2):
        super().__init__()

        layout = QVBoxLayout(self)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content_widget = QWidget()
        grid = QGridLayout(content_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        for index, tag in enumerate(tags):
            button = QPushButton(tag)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            row = index // columns
            col = index % columns
            grid.addWidget(button, row, col)

        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

class ToggleButton(QWidget):
    def __init__(self, left_text="Off", right_text="On", icon_on="icons/toggle_on.png", icon_off="icons/toggle_off.png"):
        super().__init__()

        self.icon_on = QIcon(icon_on)
        self.icon_off = QIcon(icon_off)
        self.is_on = False

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Left text label
        self.left_label = QLabel(left_text)
        layout.addWidget(self.left_label)
        
        # Toggle button in the middle
        self.toggle_button = QPushButton()
        self.toggle_button.setCheckable(True)
        self.toggle_button.setIcon(self.icon_off)
        self.toggle_button.setIconSize(QSize(32, 32))
        self.toggle_button.clicked.connect(self.toggle)
        layout.addWidget(self.toggle_button)
        
        # Right text label
        self.right_label = QLabel(right_text)
        layout.addWidget(self.right_label)

        layout.addStretch()
        self.setLayout(layout)

    def toggle(self):
        self.is_on = not self.is_on
        self.toggle_button.setIcon(self.icon_on if self.is_on else self.icon_off)

    def is_checked(self):
        return self.is_on

    def set_checked(self, value: bool):
        self.is_on = value
        self.toggle_button.setChecked(value)
        self.toggle()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    stylesheet = load_stylesheet("style.qss")
    app.setStyleSheet(stylesheet)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

