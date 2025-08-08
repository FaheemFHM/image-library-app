
import sys
import os
import random
import time

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

class GalleryCell(QWidget):
    def __init__(self, image_path, cell_size, parent=None):
        super().__init__(parent)

        self.image_path = image_path
        self.image_id = os.path.splitext(os.path.basename(image_path))[0]
        self.cell_size = cell_size

        self.is_fav = False
        self.is_hovering = False

        # Heart icons
        self.icon_off = QIcon("icons/heart_white.png")
        self.icon_on = QIcon("icons/heart_red.png")

        self.original_pixmap = QPixmap(image_path)

        self.setMouseTracking(True)
        self.setProperty("class", "cell")

        self.init_ui()
        # Set fixed size here after image_label is created
        self.setFixedSize(self.cell_size, self.cell_size + 40)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setProperty("class", "cell_image")
        layout.addWidget(self.image_label)

        # Footer
        footer = QWidget()
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(10, 0, 10, 0)
        footer_layout.setSpacing(0)
        footer.setLayout(footer_layout)
        footer.setProperty("class", "cell_footer")

        self.label_id = QLabel(self.image_id)
        self.label_id.setProperty("class", "cell_id")

        self.label_spacer = QLabel("  -  ")

        self.label_name = QLabel(os.path.basename(self.image_path))
        self.label_name.setProperty("class", "cell_name")

        self.heart_button = QPushButton()
        self.heart_button.setCheckable(True)
        self.heart_button.setChecked(False)
        self.heart_button.setIconSize(QSize(24, 24))
        self.heart_button.setFixedSize(32, 32)
        self.heart_button.setProperty("class", "cell_fav_button")
        self.heart_button.clicked.connect(self.toggle)

        footer_layout.addWidget(self.label_id)
        footer_layout.addWidget(self.label_spacer)
        footer_layout.addWidget(self.label_name)
        footer_layout.addStretch()
        footer_layout.addWidget(self.heart_button)

        layout.addWidget(footer)

        self.update_image()
        self.update_heart_visibility()

    def update_image(self):
        """Rescale and update image based on current cell size."""
        target_size = self.cell_size
        if not self.original_pixmap.isNull():
            scaled = self.original_pixmap.scaled(
                target_size, target_size,
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled)
            self.image_label.setFixedSize(target_size, target_size)

    # Remove overriding setFixedSize to avoid early calls to update_image
    # Instead add a separate method to update size and image:

    def resize_cell(self, width, height):
        self.cell_size = min(width, height - 40)
        self.setFixedSize(width, height)
        self.update_image()

    def toggle(self):
        self.is_fav = not self.is_fav
        self.heart_button.setIcon(self.icon_on if self.is_fav else self.icon_off)
        self.update_heart_visibility()

    def is_checked(self):
        return self.is_fav

    def set_checked(self, value: bool):
        self.is_fav = value
        self.heart_button.setChecked(value)
        self.heart_button.setIcon(self.icon_on if value else self.icon_off)
        self.update_heart_visibility()

    def update_heart_visibility(self):
        if self.is_fav:
            self.heart_button.setIcon(self.icon_on)
        elif self.is_hovering:
            self.heart_button.setIcon(self.icon_off)
        else:
            self.heart_button.setIcon(QIcon())

    def enterEvent(self, event):
        self.is_hovering = True
        self.update_heart_visibility()

    def leaveEvent(self, event):
        self.is_hovering = False
        self.update_heart_visibility()

class GalleryManager(QWidget):
    def __init__(self, image_folder, min_cell_size=200, image_count=100, grid_spacing=10, parent=None):
        super().__init__(parent)

        self.image_folder = image_folder
        self.min_cell_size = min_cell_size
        self.grid_spacing = grid_spacing
        self.image_count = image_count
        self.cells = []

        self._setup_ui()

    def _setup_ui(self):
        # Main layout
        self.gallery_layout = QVBoxLayout()
        self.gallery_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.gallery_layout)

        # Scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.gallery_layout.addWidget(self.scroll_area)

        # Scroll content and grid
        self.scroll_content = QWidget()
        self.scroll_area.setWidget(self.scroll_content)

        self.grid_layout = QGridLayout()
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(self.grid_spacing)
        self.scroll_content.setLayout(self.grid_layout)

        # Watch for resize events
        self.scroll_area.viewport().installEventFilter(self)

        self.load_images()

    def load_images(self):
        self.cells.clear()
        
        files = [
            f for f in os.listdir(self.image_folder)
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))
        ]

        random.shuffle(files)
        image_files = [os.path.join(self.image_folder, f) for f in files[:self.image_count]]

        for path in image_files:
            cell = GalleryCell(path, self.min_cell_size)
            self.cells.append(cell)

        self.relayout_cells()

    def eventFilter(self, source, event):
        if source == self.scroll_area.viewport() and event.type() == QEvent.Resize:
            self.relayout_cells()
        return super().eventFilter(source, event)

    def relayout_cells(self):
        # Clear grid
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        # Determine available width and column count
        area_width = self.scroll_area.viewport().width()
        full_cell_size = self.min_cell_size + self.grid_spacing
        columns = max(1, area_width // full_cell_size)

        cell_width = (area_width - (columns + 1) * self.grid_spacing) // columns
        cell_size = max(self.min_cell_size, cell_width)

        for i, cell in enumerate(self.cells):
            cell.resize_cell(cell_size, cell_size + 40)
            row = i // columns
            col = i % columns
            self.grid_layout.addWidget(cell, row, col)

def load_stylesheet():
    with open("style.qss", "r") as f:
        return f.read()

# Example usage
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    image_folder = "C:/Users/fahee/Desktop/Image Manager/media"
    gallery = GalleryManager(
        image_folder=image_folder,
        min_cell_size=200,
        image_count=10,
        grid_spacing=10
    )
    
    gallery.setWindowTitle("Image Gallery")
    gallery.resize(800, 600)
    gallery.show()
    
    sys.exit(app.exec_())

