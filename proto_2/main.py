
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

def load_stylesheet(path):
    with open(path, "r") as file:
        return file.read()

class StyledWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_StyledBackground, True)

class StyledButton(QPushButton):
    def __init__(self, text="", icon=None, icon_size=QSize(24, 24), checkable=False, parent=None):
        super().__init__(text, parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setCheckable(checkable)
        self.setCursor(Qt.PointingHandCursor)

        if icon:
            self.setIcon(icon)
            self.setIconSize(icon_size)

class MainWindow(QMainWindow):
    def __init__(self, image_folder=None):
        super().__init__()
        
        self.setWindowTitle("Media Manager")
        self.setWindowIcon(QIcon("../icons/app_icon.png"))
        self.grid_spacing = 10

        central_widget = QWidget()
        central_widget.setObjectName("central_widget")
        self.setCentralWidget(central_widget)

        central_layout = QHBoxLayout()
        central_layout.setContentsMargins(self.grid_spacing, self.grid_spacing, self.grid_spacing, self.grid_spacing)
        central_layout.setSpacing(self.grid_spacing)
        central_widget.setLayout(central_layout)

        # Sidebar 1
        self.sidebar1 = Sidebar()
        
        section = SidebarSection("Search", 32)
        section.add_widget(TextInput("Enter Query..."), 24)
        section.add_widget(SplitIconToggleButton("Name", "../icons/toggle_off.png", "../icons/toggle_on.png", "ID"), 24)
        self.sidebar1.add_section(section)
        
        section = SidebarSection("Sort", 32)
        section.add_widget(Dropdown(["Date", "Name", "ID", "Size", "Height", "Width"]), 24)
        section.add_widget(SplitIconToggleButton("Asc", "../icons/toggle_off.png", "../icons/toggle_on.png", "Desc"), 24)
        self.sidebar1.add_section(section)
        
        section = SidebarSection("Filters", 32)
        section.add_subheader("Favourite", 24)
        section.add_widget(Dropdown(["Any", "Favourites", "Non-Favourites"]), 24)
        section.add_subheader("File Type", 24)
        section.add_widget(Dropdown(["Any", "Images", "Videos"]), 24)
        section.add_subheader("Format", 24)
        section.add_widget(Dropdown(["Any", "PNG", "JPEG", "VIDEO", "MP3"]), 24)
        section.add_subheader("Camera", 24)
        section.add_widget(Dropdown(["Any", "Samsung", "Nokia", "Apple"]), 24)
        section.add_subheader("File Size", 24)
        section.add_widget(RangeInput(0, 999999999), 24)
        section.add_subheader("Image Height", 24)
        section.add_widget(RangeInput(0, 99999), 24)
        section.add_subheader("Image Width", 24)
        section.add_widget(RangeInput(0, 99999), 24)
        section.add_subheader("Times Viewed", 24)
        section.add_widget(RangeInput(0, 99999999), 24)
        section.add_subheader("Duration Viewed", 24)
        section.add_widget(RangeInput(0, 99999999), 24)
        section.add_subheader("Date Captured", 24)
        section.add_widget(DateTimeInput(False), 24)
        section.add_widget(DateTimeInput(True), 24)
        section.add_subheader("Date Added", 24)
        section.add_widget(DateTimeInput(False), 24)
        section.add_widget(DateTimeInput(True), 24)
        self.sidebar1.add_section(section)

        section = SidebarSection("Reset", 32)
        section.add_widget(TextButton("Search"), 24)
        section.add_widget(TextButton("Sort"), 24)
        section.add_widget(TextButton("Filter"), 24)
        section.add_widget(TextButton("Tags"), 24)
        section.add_widget(TextButton("All"), 24)
        self.sidebar1.add_section(section)
        
        self.sidebar1.add_stretch()
        central_layout.addWidget(self.sidebar1)
        
        # Sidebar 2
        self.sidebar2 = Sidebar()
        
        section = SidebarSection("Tags", 32)
        tag_list = TagList()
        tag_list.add_tag("Nature")
        tag_list.add_tag("Holiday")
        tag_list.add_tag("Family")
        tag_list.add_tag("Friends")
        tag_list.add_tag("Travel")
        tag_list.add_tag("Work")
        tag_list.add_tag("Birthday")
        tag_list.add_tag("Pets")
        tag_list.add_tag("Food")
        tag_list.add_tag("Music")
        tag_list.add_tag("Sports")
        tag_list.add_tag("Art")
        tag_list.add_tag("School")
        tag_list.add_tag("Beach")
        tag_list.add_tag("Mountains")
        tag_list.add_tag("Sunset")
        tag_list.add_tag("City")
        tag_list.add_tag("Night")
        tag_list.add_tag("Events")
        tag_list.add_tag("Favorites")
        section.add_widget(tag_list)
        section.add_widget(InputWithIcon("Add Tag...", "../icons/plus.png", 32, 20))
        self.sidebar2.add_section(section)

        self.sidebar2.add_stretch()
        
        central_layout.addWidget(self.sidebar2)

        # Media Control Bar
        self.media_controls = MediaControlBar()
        self.media_controls.setObjectName("media_control_bar")
        central_layout.addWidget(self.media_controls)

        # Main Section
        self.main_content = StyledWidget()
        self.main_content.setObjectName("main_content")
        self.main_content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        main_layout = QVBoxLayout(self.main_content)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Gallery Grid
        self.gallery = Gallery(columns=4)

        media_folder = "../media"
        image_files = sorted([
            f for f in os.listdir(media_folder)
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif"))
        ])[:29][::-1]  # reversed first 29 files

        for i, filename in enumerate(image_files, start=1):
            full_path = os.path.join(media_folder, filename)
            cell = GalleryCell(
                image_path=full_path,
                id_text=str(i),
                parent = self.gallery
            )
            self.gallery.add_cell(cell)

        main_layout.addWidget(self.gallery)

        # Add main layout to central layout
        central_layout.addWidget(self.main_content)
        
        self.showMaximized()

    def sidebars_toggle(self, do_set=False, do_show=False):
        if not do_set:
            do_show = not self.sidebar1.isVisible()

        for sidebar in [self.sidebar1, self.sidebar2]:
            if sidebar:
                sidebar.setVisible(do_show)

class GalleryCell(StyledWidget):
    def __init__(self, image_path, id_text, spacing=10, footer_height=32, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_Hover, True)
        self.setMouseTracking(True)
        self.image_path = image_path
        self.pixmap = QPixmap(image_path)
        self.width = 10

        # Main Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(spacing)
        self.setLayout(layout)

        # Image
        self.pixmap = QPixmap(image_path)
        self.image_label = QLabel()
        self.image_label.setPixmap(self.pixmap)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedSize(self.width, self.width)
        layout.addWidget(self.image_label)

        # Footer
        footer = QWidget()
        self.footer_height = footer_height
        footer.setFixedHeight(footer_height)
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(10, 0, 0, 0)
        footer_layout.setSpacing(0)
        footer.setLayout(footer_layout)

        self.label_id = QLabel(id_text)

        label_spacer = QLabel("     -     ")

        self.label_name = QLabel(os.path.basename(image_path))

        self.edit_button = IconButton("../icons/edit.png", 20, footer_height)
        self.edit_button.setVisible(False)

        self.fav_button = IconToggleButton("../icons/heart_white.png", "../icons/heart_red.png", 24, footer_height)
        self.fav_button.setVisible(False)
        self.fav_button.toggled.connect(self._check_visibility)

        footer_layout.addWidget(self.label_id)
        footer_layout.addWidget(label_spacer)
        footer_layout.addWidget(self.label_name)
        footer_layout.addStretch()
        footer_layout.addWidget(self.edit_button)
        footer_layout.addWidget(self.fav_button)

        layout.addWidget(footer)

        # Styling
        self.image_label.setObjectName("cell_image")
        footer.setObjectName("cell_footer")
        self.label_id.setObjectName("cell_id")

    def enterEvent(self, event):
        self._check_visibility()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._check_visibility()
        super().leaveEvent(event)

    def _check_visibility(self):
        hovered = self.underMouse()
        toggled = self.fav_button.isChecked()
        self.edit_button.setVisible(hovered)
        self.fav_button.setVisible(hovered or toggled)

    def set_cell_width(self, width):
        self.width = width
        self.setFixedWidth(width)
        image_height = width + self.footer_height
        self.image_label.setFixedSize(width, image_height)

        if not self.pixmap.isNull():
            scaled = self.pixmap.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled)

class Gallery(StyledWidget):
    def __init__(self, columns=3, spacing=10, parent=None):
        super().__init__(parent)

        self.columns = columns
        self.spacing = spacing
        self.cell_count = 0
        self.cells = []
        self.cell_width = 10

        # Outer layout
        self.container = QVBoxLayout(self)
        self.container.setContentsMargins(0, 0, 0, 0)
        self.container.setSpacing(0)

        # Scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Content widget inside scroll area
        self.content_widget = QWidget()
        self.grid_layout = QGridLayout(self.content_widget)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(spacing)

        self.scroll_area.setWidget(self.content_widget)
        self.container.addWidget(self.scroll_area)

        # Styling
        self.setObjectName("gallery")
        self.scroll_area.setObjectName("gallery_border")
        self.content_widget.setObjectName("gallery_background")

    def add_cell(self, widget):
        row = self.cell_count // self.columns
        col = self.cell_count % self.columns
        self.grid_layout.addWidget(widget, row, col)
        self.cells.append(widget)
        self.cell_count += 1

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_cell_sizes()

    def update_cell_sizes(self):
        total_width = self.scroll_area.viewport().width()
        margins = self.grid_layout.contentsMargins()
        spacing = self.grid_layout.spacing()
        available_width = total_width - margins.left() - margins.right() - spacing * (self.columns - 1)
        self.cell_width = available_width // self.columns

        for cell in self.cells:
            cell.set_cell_width(self.cell_width)

class InputWithIcon(StyledWidget):
    def __init__(self, placeholder="", icon_path="", height=None, icon_size=16, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText(placeholder)
        if height is not None:
            self.text_input.setFixedHeight(height)
        self.text_input.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.text_input.setProperty("class", "text_input")
        layout.addWidget(self.text_input)

        self.button = QPushButton()
        self.button.setIcon(QIcon(icon_path))
        self.button.setCursor(QCursor(Qt.PointingHandCursor))
        if height is not None:
            self.button.setFixedSize(height, height)
        self.button.setIconSize(QSize(icon_size, icon_size))
        self.button.setProperty("class", "icon_button")
        layout.addWidget(self.button)

class TagRow(StyledWidget):
    def __init__(self, tag_name, height=32, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setObjectName("tag_row")

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.delete_button = QPushButton()
        self.delete_button.setIcon(QIcon("../icons/delete.png"))
        self.delete_button.setIconSize(QSize(16, 16))
        self.delete_button.setFixedSize(height, height)
        self.delete_button.setCursor(Qt.PointingHandCursor)
        self.delete_button.hide()
        layout.addWidget(self.delete_button)

        self.tag_button = QPushButton(tag_name)
        self.tag_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.tag_button.setFixedHeight(height)
        self.tag_button.setCursor(Qt.PointingHandCursor)
        self.tag_button.clicked.connect(self.toggle_tag_selected)
        layout.addWidget(self.tag_button)

        self.edit_button = QPushButton()
        self.edit_button.setIcon(QIcon("../icons/edit.png"))
        self.edit_button.setIconSize(QSize(16, 16))
        self.edit_button.setFixedSize(height, height)
        self.edit_button.setCursor(Qt.PointingHandCursor)
        self.edit_button.hide()
        layout.addWidget(self.edit_button)

    def enterEvent(self, event):
        self.delete_button.show()
        self.edit_button.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.delete_button.hide()
        self.edit_button.hide()
        super().leaveEvent(event)

    def toggle_tag_selected(self):
        if self.tag_button.objectName() == "tag_row_button":
            self.tag_button.setObjectName("")
        else:
            self.tag_button.setObjectName("tag_row_button")
        self.tag_button.style().unpolish(self.tag_button)
        self.tag_button.style().polish(self.tag_button)

class TagList(StyledWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.content_widget = StyledWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        self.content_layout.addStretch()

        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.setObjectName("tag_list")
        self.content_widget.setObjectName("tag_list_content")
        self.scroll_area.setObjectName("tag_list_scroll")

    def add_tag(self, tag_name):
        tag_row = TagRow(tag_name)
        self.content_layout.insertWidget(self.content_layout.count() - 1, tag_row)
        return tag_row

    def clear_tags(self):
        for i in reversed(range(self.content_layout.count() - 1)):
            item = self.content_layout.takeAt(i)
            widget = item.widget()
            if widget:
                widget.deleteLater()

class Dropdown(QComboBox):
    def __init__(self, items=None, width=None, height=None, parent=None):
        super().__init__(parent)
        self.setProperty("class", "dropdown")
        self.setCursor(Qt.PointingHandCursor)

        if items:
            self.addItems(items)

        if width:
            self.setFixedWidth(width)
        if height:
            self.setFixedHeight(height)

class TextInput(QLineEdit):
    def __init__(self, placeholder="", height=None, width=None, parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setProperty("class", "text_input")
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setCursor(Qt.IBeamCursor)

        if width:
            self.setFixedWidth(width)
        if height:
            self.setFixedHeight(height)

class TextButton(StyledButton):
    def __init__(self, text, parent=None):
        super().__init__(text=text, parent=parent)
        self.setFixedHeight(28)

class DateTimeInput(QWidget):
    def __init__(self, use_current_time=True, height=None, parent=None):
        super().__init__(parent)
        self.setProperty("class", "datetime_input")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.datetime_edit = QDateTimeEdit()
        self.datetime_edit.setCalendarPopup(True)
        if height is not None:
            self.datetime_edit.setFixedHeight(height)

        default_value = (
            QDateTime.currentDateTime()
            if use_current_time
            else QDateTime(QDate(1950, 1, 1), QTime(0, 0, 0))
        )
        self.datetime_edit.setDateTime(default_value)

        layout.addWidget(self.datetime_edit)

    def dateTime(self):
        return self.datetime_edit.dateTime()

    def setDateTime(self, datetime_obj):
        self.datetime_edit.setDateTime(datetime_obj)

class RangeInput(QWidget):
    def __init__(self, min_val=0, max_val=100, height=None, parent=None):
        super().__init__(parent)
        self.setProperty("class", "range_input")

        self.min_val = min_val
        self.max_val = max_val

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignCenter)

        self.min_input = QSpinBox()
        self.max_input = QSpinBox()

        for spinbox in (self.min_input, self.max_input):
            spinbox.setRange(min_val, max_val)
            spinbox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            if height is not None:
                spinbox.setFixedHeight(height)

        self.min_input.setValue(min_val)
        self.max_input.setValue(min_val)

        self.min_input.valueChanged.connect(self.on_min_changed)
        self.max_input.valueChanged.connect(self.on_max_changed)

        layout.addWidget(self.min_input)
        layout.addWidget(self.max_input)

    def on_min_changed(self, value):
        if value > self.max_input.value():
            self.max_input.setValue(value)

    def on_max_changed(self, value):
        if value < self.min_input.value():
            self.min_input.setValue(value)

    def get_range(self):
        return self.min_input.value(), self.max_input.value()

    def set_range(self, min_value, max_value):
        self.min_input.setValue(min_value)
        self.max_input.setValue(max_value)

class IconButton(StyledButton):
    def __init__(self, icon_path, icon_size=28, button_size=50, parent=None):
        super().__init__(parent)
        self.setIcon(QIcon(icon_path))
        self.setIconSize(QSize(icon_size, icon_size))
        self.setFixedSize(button_size, button_size)

class IconToggleButton(StyledButton):
    def __init__(self, icon_off_path, icon_on_path, icon_size=28, button_size=50, parent=None):
        super().__init__(parent)
        self.icon_off = QIcon(icon_off_path)
        self.icon_on = QIcon(icon_on_path)

        self.setCheckable(True)
        self.setIcon(self.icon_off)
        self.setIconSize(QSize(icon_size, icon_size))
        self.setFixedSize(button_size, button_size)

        self.toggled.connect(self.update_icon)

    def update_icon(self, checked):
        self.setIcon(self.icon_on if checked else self.icon_off)

class SplitIconToggleButton(QPushButton):
    def __init__(self, left_text, icon_off_path, icon_on_path, right_text, icon_size=24, height=None, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setProperty("class", "split_icon_toggle_button")

        self.icon_off = QIcon(icon_off_path)
        self.icon_on = QIcon(icon_on_path)
        self.icon_size = icon_size

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        if height is not None:
            self.setFixedHeight(height)

        self.label_left = QLabel(left_text)
        self.label_left.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_left.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.icon_label = QLabel()
        self.icon_label.setPixmap(self.icon_off.pixmap(self.icon_size, self.icon_size))
        self.icon_label.setAlignment(Qt.AlignCenter)

        self.label_right = QLabel(right_text)
        self.label_right.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_right.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        layout.addWidget(self.label_left)
        layout.addWidget(self.icon_label)
        layout.addWidget(self.label_right)

        self.toggled.connect(self.update_icon)

    def update_icon(self, checked):
        icon = self.icon_on if checked else self.icon_off
        self.icon_label.setPixmap(icon.pixmap(self.icon_size, self.icon_size))

class MediaControlBar(StyledWidget):
    def __init__(self, parent=None, width=50):
        super().__init__(parent)

        self.setProperty("class", "sidebar")
        self.setFixedWidth(width)
        self.parent = parent
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        # Button Options
        button = IconToggleButton("../icons/play.png", "../icons/pause.png")
        button.clicked.connect(self.do_play)
        layout.addWidget(button, alignment=Qt.AlignHCenter)
        
        button = IconButton("../icons/stop.png")
        button.clicked.connect(self.do_stop)
        layout.addWidget(button, alignment=Qt.AlignHCenter)

        button = IconButton("../icons/fast_forwards.png")
        layout.addWidget(button, alignment=Qt.AlignHCenter)

        button = IconButton("../icons/fast_backwards.png")
        layout.addWidget(button, alignment=Qt.AlignHCenter)

        button = IconButton("../icons/fastest_forwards.png")
        layout.addWidget(button, alignment=Qt.AlignHCenter)

        button = IconButton("../icons/fastest_backwards.png")
        layout.addWidget(button, alignment=Qt.AlignHCenter)

        button = IconButton("../icons/skip_forwards.png")
        layout.addWidget(button, alignment=Qt.AlignHCenter)

        button = IconButton("../icons/skip_backwards.png")
        layout.addWidget(button, alignment=Qt.AlignHCenter)

        button = IconToggleButton("../icons/loop_off.png", "../icons/loop_on.png")
        layout.addWidget(button, alignment=Qt.AlignHCenter)

        button = IconToggleButton("../icons/shuffle_off.png", "../icons/shuffle_on.png")
        layout.addWidget(button, alignment=Qt.AlignHCenter)

        self.layout().addStretch()

    def do_play(self):
        self.window().sidebars_toggle(True, False)

    def do_stop(self):
        self.window().sidebars_toggle(True, True)

class SidebarSection(StyledWidget):
    def __init__(self, title: str, height=None, spacing=0, parent=None):
        super().__init__(parent)

        self.setProperty("class", "sidebar_section")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(spacing)
        self.setLayout(layout)

        # Header
        header = QLabel(title)
        header.setProperty("class", "sidebar_header")
        header.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        if height is not None:
            header.setFixedHeight(height)
        layout.addWidget(header)

        # Contents
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(spacing)
        layout.addLayout(self.content_layout)

    def add_widget(self, widget, height=None):
        if height is not None:
            widget.setFixedHeight(height)
        self.content_layout.addWidget(widget)

    def add_subheader(self, title, height=None):
        subheader = QLabel(title)
        subheader.setProperty("class", "sidebar_sub_header")
        subheader.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        if height is not None:
            subheader.setFixedHeight(height)
        self.content_layout.addWidget(subheader)

    def add_spacer(self):
        spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.content_layout.addSpacerItem(spacer)

class Sidebar(StyledWidget):
    def __init__(self, parent=None, width=200, spacing=0):
        super().__init__(parent)

        self.setProperty("class", "sidebar")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(spacing)
        self.setLayout(layout)
        
        self.setFixedWidth(width)

        self.sections = []

    def add_section(self, section: SidebarSection):
        self.layout().addWidget(section)
        self.sections.append(section)

    def add_stretch(self):
        self.layout().addStretch()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    stylesheet = load_stylesheet("style.qss")
    app.setStyleSheet(stylesheet)

    media_path = "../media"
    window = MainWindow(media_path)
    window.show()
    
    sys.exit(app.exec_())
