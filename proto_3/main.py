

import sys
import re
from pathlib import Path
import random
import time

from database import MediaDatabase

from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow,
    QHBoxLayout, QVBoxLayout, QGridLayout, QFormLayout,
    QLabel, QPushButton, QLineEdit, QSpinBox, QComboBox, QCheckBox,
    QTextEdit, QScrollArea, QFrame, QStackedWidget,
    QTabWidget, QToolBar, QAction, QSizePolicy, QFileDialog, QMessageBox,
    QDateTimeEdit, QSlider, QDialog
)

from PyQt5.QtGui import (
    QIcon, QPixmap, QFont, QCursor, QColor, QPainter, QPalette
)

from PyQt5.QtCore import (
    Qt, QSize, QTimer, QDateTime, QDate, QTime,
    QPropertyAnimation, QPoint, QRect, QObject,
    pyqtSignal
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

        self.do_loop = True
        self.do_shuffle = False

        central_widget = QWidget()
        central_widget.setObjectName("central_widget")
        self.setCentralWidget(central_widget)

        central_layout = QHBoxLayout()
        central_layout.setContentsMargins(self.grid_spacing, self.grid_spacing, self.grid_spacing, self.grid_spacing)
        central_layout.setSpacing(self.grid_spacing)
        central_widget.setLayout(central_layout)

        self.widgets_search = []
        self.widgets_sort = []
        self.widgets_filter = []

        self.db = MediaDatabase()
        self.db.add_tag_to_images("Landscape", [4, 5, 6, 7])

        # Sidebar 1
        self.sidebar1 = Sidebar()
        self.sidebar1.add_header("Search", 32)

        subheader = self.sidebar1.add_subheader("Filename", height=24, filter_key="filename")
        self.widgets_search.append(subheader)
        subheader.toggled.connect(self.update_filter_active)
        widget = TextInput("Enter Query...", filter_key="filename")
        widget.on_filter_changed.connect(self.update_filter)
        self.widgets_search.append(widget)
        self.sidebar1.add_widget(widget, 24)

        subheader = self.sidebar1.add_subheader("ID", height=24, filter_key="id")
        self.widgets_search.append(subheader)
        subheader.toggled.connect(self.update_filter_active)
        widget = IntInput(max_val=999999999, filter_key="id")
        widget.on_filter_changed.connect(self.update_filter)
        self.widgets_search.append(widget)
        self.sidebar1.add_widget(widget, 24)

        self.sidebar1.add_spacer(self.grid_spacing)
        
        self.sidebar1.add_header("Sort", 32)
        
        widget = Dropdown(["Name", "ID", "Size", "Height", "Width",
                           "Times Viewed", "Duration Viewed",
                           "Date Captured", "Date Added"],
                          values=["filename", "id", "filesize", "height", "width",
                                  "times_viewed", "time_viewed",
                                  "date_captured", "date_added"],
                          filter_key="sort_value")
        widget.on_filter_changed.connect(self.update_filter)
        self.widgets_sort.append(widget)
        self.sidebar1.add_widget(widget, 24)
        
        widget = SplitIconToggleButton("Asc", "../icons/toggle_off.png",
                                       "../icons/toggle_on.png", "Desc",
                                       filter_key="sort_dir")
        widget.on_filter_changed.connect(self.update_filter)
        self.widgets_sort.append(widget)
        self.sidebar1.add_widget(widget, 24)
        
        self.sidebar1.add_spacer(self.grid_spacing)
        
        self.sidebar1.add_header("Filters", 32)
        
        subheader = self.sidebar1.add_subheader("Favourite", height=24, filter_key="is_favourite")
        self.widgets_filter.append(subheader)
        subheader.toggled.connect(self.update_filter_active)
        widget = Dropdown(["Any", "Favourites", "Non-Favourites"],
                          values=[None, True, False],
                          filter_key="is_favourite")
        widget.on_filter_changed.connect(self.update_filter)
        self.widgets_filter.append(widget)
        self.sidebar1.add_widget(widget, 24)
        
        subheader = self.sidebar1.add_subheader("File Type", height=24, filter_key="type")
        self.widgets_filter.append(subheader)
        subheader.toggled.connect(self.update_filter_active)
        my_array = ["Any"] + self.db.get_unique_values("type")
        my_array = [x for x in my_array if x is not None]
        widget = Dropdown(my_array, filter_key="type")
        widget.on_filter_changed.connect(self.update_filter)
        self.widgets_filter.append(widget)
        self.sidebar1.add_widget(widget, 24)
        
        subheader = self.sidebar1.add_subheader("Format", height=24, filter_key="format")
        self.widgets_filter.append(subheader)
        subheader.toggled.connect(self.update_filter_active)
        my_array = ["Any"] + self.db.get_unique_values("format")
        my_array = [x for x in my_array if x is not None]
        widget = Dropdown(my_array, filter_key="format")
        widget.on_filter_changed.connect(self.update_filter)
        self.widgets_filter.append(widget)
        self.sidebar1.add_widget(widget, 24)
        
        subheader = self.sidebar1.add_subheader("Camera", height=24, filter_key="camera_model")
        self.widgets_filter.append(subheader)
        subheader.toggled.connect(self.update_filter_active)
        my_array = ["Any"] + self.db.get_unique_values("camera_model")
        my_array = [x for x in my_array if x is not None]
        widget = Dropdown(my_array, filter_key="camera_model")
        widget.on_filter_changed.connect(self.update_filter)
        self.widgets_filter.append(widget)
        self.sidebar1.add_widget(widget, 24)
        
        subheader = self.sidebar1.add_subheader("File Size", height=24, filter_key="filesize")
        self.widgets_filter.append(subheader)
        subheader.toggled.connect(self.update_filter_active)
        widget = RangeInput(0, 999999999, filter_key="filesize")
        widget.on_filter_changed.connect(self.update_filter)
        self.widgets_filter.append(widget)
        self.sidebar1.add_widget(widget, 24)
        
        subheader = self.sidebar1.add_subheader("Image Height", height=24, filter_key="height")
        self.widgets_filter.append(subheader)
        subheader.toggled.connect(self.update_filter_active)
        widget = RangeInput(0, 999999999, filter_key="height")
        widget.on_filter_changed.connect(self.update_filter)
        self.widgets_filter.append(widget)
        self.sidebar1.add_widget(widget, 24)
        
        subheader = self.sidebar1.add_subheader("Image Width", height=24, filter_key="width")
        self.widgets_filter.append(subheader)
        subheader.toggled.connect(self.update_filter_active)
        widget = RangeInput(0, 999999999, filter_key="width")
        widget.on_filter_changed.connect(self.update_filter)
        self.widgets_filter.append(widget)
        self.sidebar1.add_widget(widget, 24)
        
        subheader = self.sidebar1.add_subheader("Times Viewed", height=24, filter_key="times_viewed")
        self.widgets_filter.append(subheader)
        subheader.toggled.connect(self.update_filter_active)
        widget = RangeInput(0, 999999999, filter_key="times_viewed")
        widget.on_filter_changed.connect(self.update_filter)
        self.widgets_filter.append(widget)
        self.sidebar1.add_widget(widget, 24)
        
        subheader = self.sidebar1.add_subheader("Duration Viewed", height=24, filter_key="time_viewed")
        self.widgets_filter.append(subheader)
        subheader.toggled.connect(self.update_filter_active)
        widget = RangeInput(0, 999999999, filter_key="time_viewed")
        widget.on_filter_changed.connect(self.update_filter)
        self.widgets_filter.append(widget)
        self.sidebar1.add_widget(widget, 24)
        
        subheader = self.sidebar1.add_subheader("Date Captured", height=24, filter_key="date_captured")
        self.widgets_filter.append(subheader)
        subheader.toggled.connect(self.update_filter_active)
        widget = DateTimeRangeInput(height=24, filter_key="date_captured")
        widget.on_filter_changed.connect(self.update_filter)
        self.widgets_filter.append(widget)
        self.sidebar1.add_widget(widget)
        
        subheader = self.sidebar1.add_subheader("Date Added", height=24, filter_key="date_added")
        self.widgets_filter.append(subheader)
        subheader.toggled.connect(self.update_filter_active)
        widget = DateTimeRangeInput(height=24, filter_key="date_added")
        widget.on_filter_changed.connect(self.update_filter)
        self.widgets_filter.append(widget)
        self.sidebar1.add_widget(widget)
        
        self.sidebar1.add_spacer(self.grid_spacing)
        
        self.sidebar1.add_header("Reset", 32)
        
        widget = TextButton("Search", height="expanding")
        widget.clicked.connect(lambda: self.reset_filters("search"))
        self.sidebar1.add_widget(widget, 24)
        
        widget = TextButton("Sort", height="expanding")
        widget.clicked.connect(lambda: self.reset_filters("sort"))
        self.sidebar1.add_widget(widget, 24)
        
        widget = TextButton("Filter", height="expanding")
        widget.clicked.connect(lambda: self.reset_filters("filter"))
        self.sidebar1.add_widget(widget, 24)
        
        widget = TextButton("Tags", height="expanding")
        widget.clicked.connect(lambda: self.reset_filters("tags"))
        self.sidebar1.add_widget(widget, 24)
        
        widget = TextButton("All", height="expanding")
        widget.clicked.connect(lambda: self.reset_filters("all"))
        self.sidebar1.add_widget(widget, 24)
        
        # Sidebar 2
        self.sidebar2 = Sidebar()
        
        self.sidebar2.add_header("Tags", 32)

        self.tag_filter_mode = Dropdown(["Any", "All", "Exact", "None"],
                          values=["any", "all", "exact", "none"],
                          filter_key="tag_mode")
        self.tag_filter_mode.on_filter_changed.connect(self.update_filter)
        self.tag_filter_mode.setObjectName("tag_filter_mode")
        self.sidebar2.add_widget(self.tag_filter_mode, 24)
        
        self.tag_list = TagList()
        self.all_tags = self.db.get_all_tags()
        for tag in self.all_tags:
            widget = self.tag_list.add_tag(tag)
            widget.on_filter_changed.connect(self.update_filter_tags)
        self.sidebar2.add_widget(self.tag_list)

        widget = InputWithIcon("Add Tag...", "../icons/plus.png", 32, 20)
        widget.submit.connect(self.add_tag)
        self.sidebar2.add_widget(widget)

        self.sidebar2.add_spacer(self.grid_spacing)

        button = TextButton("Apply", height="fixed")
        button.setObjectName("apply_button")
        button.setFixedHeight(200)
        button.clicked.connect(self.apply_filters)
        self.sidebar2.add_widget(button)
        
        #self.sidebar2.add_stretch()

        # Media Control Bar
        self.media_controls = MediaControlBar(do_loop=self.do_loop,
                                              do_shuffle=self.do_shuffle,
                                              parent=self)
        self.media_controls.setObjectName("media_control_bar")

        # Main Section
        self.main_content = StyledWidget()
        self.main_content.setObjectName("main_content")
        self.main_content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        main_layout = QVBoxLayout(self.main_content)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Gallery
        self.gallery = Gallery(columns=4, parent=self)
        self.gallery.edit_cell.connect(self.open_gallery_edit)
        main_layout.addWidget(self.gallery)

        # Gallery Cell Edit
        self.gallery_edit = GalleryCellEdit(spacing=self.grid_spacing, parent=self)
        self.gallery_edit.do_apply.connect(self.apply_gallery_edit)
        self.gallery_edit.close_edit.connect(self.close_gallery_edit)
        main_layout.addWidget(self.gallery_edit)

        # Slideshow
        self.slideshow = SlideShow(
            do_loop=self.do_loop,
            do_shuffle=self.do_shuffle
        )
        main_layout.addWidget(self.slideshow)

        # Add to central layout
        central_layout.addWidget(self.media_controls)
        central_layout.addWidget(self.sidebar1)
        central_layout.addWidget(self.sidebar2)
        central_layout.addWidget(self.main_content)

        # Other
        self.media_controls.update_slider(self.slideshow.get_speed_settings())
        self.showMaximized()

        self.apply_filters()

    def open_gallery_edit(self, data):
        self.gallery.hide()
        self.sidebars_toggle(True, False, False)
        self.gallery_edit.show()
        self.gallery_edit.set_data(data, sorted(self.all_tags))

    def apply_gallery_edit(self, image_id, filename, tags):
        if filename:
            self.db.set_image_filename(image_id, filename)
        if tags is not None:
            self.db.set_image_tags(image_id, tags)

    def close_gallery_edit(self):
        self.gallery_edit.hide()
        self.sidebars_toggle(True, True, True)
        self.gallery.show()

    def add_tag(self, tag):
        added = self.db.add_tag(tag)
        if added:
            widget = self.tag_list.add_tag(tag, insert_alpha=True)
            widget.on_filter_changed.connect(self.update_filter_tags)
            self.all_tags.append(tag)
        else:
            print(f"Failed to add tag: {tag}")

    def apply_filters(self):
        self.gallery.populate_gallery()
        self.slideshow.set_image_paths(self.gallery.get_image_paths())

    def update_filter_active(self, filter_key, value):
        if filter_key in self.gallery.filters_active:
            self.gallery.filters_active[filter_key] = value
        else:
            print("Filter key does not exist.")

    def update_filter(self, filter_key, value):
        if filter_key in self.gallery.filters:
            self.gallery.filters[filter_key] = value
        else:
            print("Filter key does not exist.")
            
    def update_filter_tags(self, tag, is_active):
        tags = self.gallery.filters.setdefault("tags", [])

        if is_active:
            if tag not in tags:
                tags.append(tag)
        else:
            if tag in tags:
                tags.remove(tag)

    def reset_filters(self, val=""):
        match val:
            case "search":
                for widget in self.widgets_search:
                    widget.reset()
            case "sort":
                for widget in self.widgets_sort:
                    widget.reset()
            case "filter":
                for widget in self.widgets_filter:
                    widget.reset()
            case "tags":
                for widget in self.tag_list.tags:
                    widget.reset()
                self.tag_filter_mode.reset()
            case "all":
                for widget in self.widgets_search + self.widgets_sort + self.widgets_filter + self.tag_list.tags:
                    widget.reset()
                self.tag_filter_mode.reset()
            case _:
                print(f"Unknown reset value")
    
    def slideshow_controls(self, do_stop=False):
        if do_stop:
            self.stop()
        elif not self.slideshow.is_open:
            self.play()
        elif self.slideshow.is_playing:
            self.pause()
        else:
            self.resume()

    def play(self):
        self.gallery.hide()
        self.sidebars_toggle(True, False)
        self.slideshow.show()
        self.slideshow.play()
        self.media_controls.set_play_icon(False)

    def pause(self):
        self.slideshow.pause()
        self.media_controls.set_play_icon(True)

    def stop(self):
        self.slideshow.stop()
        self.slideshow.hide()
        self.sidebars_toggle(True, True)
        self.gallery.show()
        self.media_controls.set_play_icon(True)

    def resume(self):
        self.slideshow.resume()
        self.media_controls.set_play_icon(False)

    def restart(self):
        self.slideshow.restart()

    def set_slideshow_speed(self, val):
        self.slideshow.change_speed(val)

    def sidebars_toggle(self, do_set=False, do_show=False, media_bar=None):
        if not do_set:
            do_show = not self.sidebar1.isVisible()

        for sidebar in [self.sidebar1, self.sidebar2]:
            if sidebar:
                sidebar.setVisible(do_show)

        if media_bar in [True, False]:
            self.media_controls.setVisible(media_bar)

    def set_loop(self, val):
        self.slideshow.set_loop(val)
    
    def set_shuffle(self, val):
        self.slideshow.set_shuffle(val)

    def toggle_favourite(self, image_id, toggled):
        self.db.toggle_favourite(image_id, toggled)

class GalleryCellEdit(StyledWidget):
    close_edit = pyqtSignal()
    do_apply = pyqtSignal(int, str, object)
    
    def __init__(self, spacing=0, parent=None):
        super().__init__(parent)

        # Main Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(spacing)

        # Image
        self.image_label = QLabel()
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setScaledContents(False)
        self.pixmap = QPixmap()

        # Sidebar
        self.sidebar = Sidebar()

        # Name Input
        self.sidebar.add_header("Name", 32)

        self.sidebar.add_subheader_flat("Old", height=24)
        self.old_name = QLabel("filename")
        self.old_name.setAlignment(Qt.AlignCenter)
        self.sidebar.add_widget(self.old_name, 24)

        self.sidebar.add_subheader_flat("New", height=24)
        self.input_name = TextInput("Input New Filename", filter_key="filename")
        self.input_name.setProperty("class", "clear_spacing")
        self.input_name.setAlignment(Qt.AlignCenter)
        self.sidebar.add_widget(self.input_name, 24)
        
        self.sidebar.add_spacer(spacing)

        # Tag List
        self.sidebar.add_header("Tags", 32)
        
        self.tag_list = TagList(anim=False)
        self.sidebar.add_widget(self.tag_list)
        
        self.sidebar.add_spacer(spacing)

        # Button Options
        self.sidebar.add_header("Options", 32)
        
        widget = TextButton("Apply")
        widget.clicked.connect(self.apply_edits)
        self.sidebar.add_widget(widget, 24)

        widget = TextButton("Revert")
        widget.clicked.connect(self.revert_edits)
        self.sidebar.add_widget(widget, 24)
        
        widget = TextButton("Back")
        widget.clicked.connect(self.close_edits)
        self.sidebar.add_widget(widget, 24)

        # Update Layout
        layout.addWidget(self.image_label)
        layout.addWidget(self.sidebar)
        
        self.setLayout(layout)
        self.hide()

    def apply_edits(self):
        # filename
        filename = self.sanitise_filename(self.input_name.text())
        if filename is not None:
            filename += self.extension
            self.old_name.setText(filename)
        print("empty" if not filename else filename)

        # tags
        new_tags = [tag.tag_name for tag in self.tag_list.tags if tag.is_active]
        if set(self.original_tags) != set(new_tags):
            self.original_tags = new_tags.copy()
        else:
            new_tags = None
        
        # signal
        self.do_apply.emit(self.data['id'], filename, new_tags)
        self.revert_edits()

    def sanitise_filename(self, name):
        name = name.strip()
        
        invalid_chars = r'[<>:"/\\|?*].'
        if re.search(invalid_chars, name):
            return None

        if not name:
            return None

        return name

    def revert_edits(self):
        self.input_name.reset()
        self.toggle_tags(self.original_tags)
    
    def close_edits(self):
        self.revert_edits()
        self.close_edit.emit()

    def set_data(self, data, all_tags):
        self.data = data.copy()
        
        self.set_image(data['filepath'])
        
        path_object = Path(data['filename'])
        self.old_name.setText(path_object.stem)
        self.extension = path_object.suffix

        self.original_tags = self.data['tags'].copy()
        self.refresh_tags(all_tags)
        self.toggle_tags(self.data['tags'])

    def refresh_tags(self, all_tags):
        self.tag_list.clear_tags()
        for tag in all_tags:
            self.tag_list.add_tag(tag)
    
    def toggle_tags(self, my_list):
        for tag in self.tag_list.tags:
            tag.set_active(True if tag.tag_name in my_list else False)
    
    def set_image(self, filepath):
        pixmap = QPixmap(filepath)
        if pixmap.isNull():
            return
        self.pixmap = pixmap
        scaled = self.pixmap.scaled(
            self.image_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled)

    def resizeEvent(self, event):
        if self.pixmap.isNull():
            return
        scaled = self.pixmap.scaled(
            self.image_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled)
        super().resizeEvent(event)

class GalleryCell(StyledWidget):
    edit_cell = pyqtSignal(object)
    
    def __init__(self, record, window, spacing=10, footer_height=32, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_Hover, True)
        self.setMouseTracking(True)

        self.data = record
        self.image_path = record['filepath']
        self.image_id = record['id']
        self.window = window

        self.pixmap = QPixmap(self.image_path)
        self.width = 10

        # Main Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(spacing)
        self.setLayout(layout)

        # Image
        self.pixmap = QPixmap(self.image_path)
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

        self.label_id = QLabel(str(self.image_id))

        label_spacer = QLabel("     -     ")

        #self.label_name = QLabel(Path(self.image_path).name)
        self.label_name = QLabel(self.data['filename'])

        self.edit_button = IconButton("../icons/edit.png", 20, footer_height)
        self.edit_button.setVisible(False)
        self.edit_button.clicked.connect(lambda: self.edit_cell.emit(self.data))

        self.fav_button = IconToggleButton("../icons/heart_white.png", "../icons/heart_red.png", 24, footer_height)
        self.fav_button.setVisible(False)
        self.fav_button.toggled.connect(self.toggle_favourite)
        if self.data["is_favourite"]:
            self.fav_button.setChecked(True)

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
        self.check_visibility()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.check_visibility()
        super().leaveEvent(event)

    def check_visibility(self):
        hovered = self.underMouse()
        self.edit_button.setVisible(hovered)
        self.fav_button.setVisible(hovered or self.fav_button.isChecked())
        
    def toggle_favourite(self):
        self.check_visibility()
        self.window.toggle_favourite(self.image_id, self.fav_button.isChecked())

    def set_cell_width(self, width):
        self.width = width
        self.setFixedWidth(width)
        self.image_label.setFixedSize(width, width)

        if not self.pixmap.isNull():
            scaled = self.pixmap.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled)

class Gallery(StyledWidget):
    edit_cell = pyqtSignal(object)
    
    def __init__(self, columns=3, spacing=10, parent=None):
        super().__init__(parent)

        self.columns = columns
        self.spacing = spacing
        self.cell_count = 0
        self.cells = []
        self.cell_width = 10
        self.cells_max = 30
        self.parent = parent

        date_time= QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")

        self.filters = {
            "id": 27,
            "filename": "",
            "is_favourite": True,
            "type": "Any",
            "format": "Any",
            "camera_model": "Any",
            "filesize_min": 0,
            "filesize_max": 0,
            "height_min": 0,
            "height_max": 0,
            "width_min": 0,
            "width_max": 0,
            "times_viewed_min": 0,
            "times_viewed_max": 0,
            "time_viewed_min": 0,
            "time_viewed_max": 0,
            "date_captured_min": None,
            "date_captured_max": None,
            "date_added_min": None,
            "date_added_max": None,
            "sort_value": "id",
            "sort_dir": False,
            "tags": [],
            "tag_mode": "any"
        }

        self.filters_default = {
            "id": 0,
            "filename": "",
            "is_favourite": None,
            "type": "Any",
            "format": "Any",
            "camera_model": "Any",
            "filesize_min": 0,
            "filesize_max": 0,
            "height_min": 0,
            "height_max": 0,
            "width_min": 0,
            "width_max": 0,
            "times_viewed_min": 0,
            "times_viewed_max": 0,
            "time_viewed_min": 0,
            "time_viewed_max": 0,
            "date_captured_min": date_time,
            "date_captured_max": date_time,
            "date_added_min": date_time,
            "date_added_max": date_time,
            "sort_value": "id",
            "sort_dir": False,
            "tags": [],
            "tag_mode": "any"
        }

        self.filters_active = {
            "id": False,
            "filename": False,
            "is_favourite": False,
            "type": False,
            "format": False,
            "camera_model": False,
            "filesize": False,
            "height": False,
            "width": False,
            "times_viewed": False,
            "time_viewed": False,
            "date_captured": False,
            "date_added": False
        }

        # Outer layout
        self.container = QVBoxLayout(self)
        self.container.setContentsMargins(0, 0, 0, 0)
        self.container.setSpacing(0)

        # Scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
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

    def get_image_paths(self):
        paths = []
        for cell in self.cells:
            paths.append(cell.image_path)
        return paths

    def clear_grid_layout(self, grid_layout):
        [w.setParent(None) or w.deleteLater() for i in reversed(range(grid_layout.count())) if (w := grid_layout.itemAt(i).widget())]
        self.cell_count = 0
        self.cells = []

    def populate_gallery(self):
        self.clear_grid_layout(self.grid_layout)

        image_records = self.parent.db.apply_filters(self.filters, self.filters_active)
        
        i = 0
        for record in image_records:
            if i >= self.cells_max:
                break
            self.add_cell(GalleryCell(record, window=self.parent, parent=self))
            i += 1

        self.update_cell_sizes()

    def add_cell(self, widget):
        row = self.cell_count // self.columns
        col = self.cell_count % self.columns
        self.grid_layout.addWidget(widget, row, col, alignment=Qt.AlignTop | Qt.AlignLeft)
        self.cells.append(widget)
        self.cell_count += 1
        widget.edit_cell.connect(self.edit_cell.emit)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resize()

    def resize(self):
        self.get_cell_sizes()
        self.update_cell_sizes()
        
    def get_cell_sizes(self):
        total_width = self.scroll_area.viewport().width()
        margins = self.grid_layout.contentsMargins()
        spacing = self.grid_layout.spacing()
        available_width = total_width - margins.left() - margins.right() - spacing * (self.columns - 1)
        self.cell_width = available_width // self.columns

    def update_cell_sizes(self):
        for cell in self.cells:
            cell.set_cell_width(self.cell_width)

class SlideShow(QWidget):
    image_changed = pyqtSignal(str)
    
    def __init__(self, image_paths=[],
                 interval=1000, min_speed=250, max_speed=10000, increment=250,
                 do_loop=True, do_shuffle=False, parent=None):
        super().__init__(parent)
        self.original_images = image_paths
        self.shuffled_images = []
        self.current_index = 0
        self.interval = interval
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.increment = increment
        self.loop = do_loop
        self.shuffle = do_shuffle
        self.is_open = False
        self.is_playing = False

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_image)
        self.timer.setInterval(self.interval)

        # Setup UI
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setScaledContents(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.image_label)

        self.image_changed.connect(self.set_image)

        self.setLayout(layout)

        self.hide()

    def get_speed_settings(self):
        return [self.min_speed, self.max_speed, self.increment, self.interval]

    def set_image(self, image_path):
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.image_label.setPixmap(pixmap.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation))
        else:
            self.image_label.clear()

    def resizeEvent(self, event):
        if not self.image_label.pixmap() is None:
            pixmap = self.image_label.pixmap()
            self.image_label.setPixmap(pixmap.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation))
        super().resizeEvent(event)
    
    def set_image_paths(self, image_paths):
        self.original_images = image_paths[:]
        self.current_index = 0
        self.shuffled_images = []

    def set_interval(self, ms):
        ms = max(self.min_speed, min(ms, self.max_speed))
        self.interval = ms
        self.timer.setInterval(ms)

    def set_loop(self, loop):
        self.loop = loop

    def set_shuffle(self, shuffle):
        self.shuffle = shuffle

    def get_first_image(self):
        if not self.original_images:
            return None

        self.current_index = 0
        if self.shuffle:
            self.shuffled_images = self.original_images[:]
            random.shuffle(self.shuffled_images)
            return self.shuffled_images[self.current_index]
        else:
            return self.original_images[self.current_index]

    def play(self):
        current_image = self.get_first_image()
        if not current_image:
            return
        self.show()
        self.image_changed.emit(current_image)
        self.is_open = True
        self.is_playing = True
        self.timer.start(self.interval)

    def restart(self):
        current_image = self.get_first_image()
        if not current_image:
            return
        self.image_changed.emit(current_image)
        self.is_open = True
        self.is_playing = True
        self.timer.start(self.interval)

    def stop(self):
        self.timer.stop()
        self.is_open = False
        self.is_playing = False
        self.current_index = 0
        self.hide()

    def pause(self):
        self.timer.stop()
        self.is_open = True
        self.is_playing = False

    def resume(self):
        if not self.is_playing and self.original_images:
            self.timer.start()
            self.is_open = True
            self.is_playing = True

    def change_speed(self, ms):
        ms = max(self.min_speed, min(ms, self.max_speed))
        
        self.interval = ms
        self.timer.setInterval(ms)
        
        if self.is_playing:
            remaining = self.timer.remainingTime()
            
            if remaining > ms:
                self.timer.start(ms)
            else:
                self.timer.start(remaining)

    def next_image(self):
        if not self.is_playing or not self.is_open or not self.original_images:
            return

        images = self.shuffled_images if self.shuffle else self.original_images
        next_index = self.current_index + 1

        if next_index >= len(images):
            if self.loop:
                if self.shuffle:
                    random.shuffle(self.shuffled_images)
                    images = self.shuffled_images
                next_index = 0
            else:
                self.window().media_controls.set_play_icon(True)
                self.stop()
                return

        self.current_index = next_index
        current_image = images[self.current_index]
        self.image_changed.emit(current_image)

class VerticalSlider(StyledWidget):
    def __init__(self, val_min=250, val_max=10000, val_step=250, val_start=500):
        super().__init__()
        
        layout = QVBoxLayout()

        self.val_step = val_step

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)

        self.slider = QSlider(Qt.Vertical)
        self.slider.setTickPosition(QSlider.TicksBothSides)

        self.update_slider([val_min, val_max, val_step, val_start])

        self.slider.valueChanged.connect(self.change_speed)

        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        self.setLayout(layout)

    def format_value(self, val):
        formatted = f"{val:.2f}"
        return formatted.rstrip('0').rstrip('.') if '.' in formatted else formatted

    def change_speed(self, value):
        step = self.val_step
        snapped_val = round(value / step) * step

        if snapped_val != value:
            self.slider.blockSignals(True)
            self.slider.setValue(snapped_val)
            self.slider.blockSignals(False)

        self.label.setText(self.format_value(snapped_val / 1000))

        self.window().set_slideshow_speed(snapped_val)

    def update_slider(self, settings):
        val_min, val_max, val_step, val_start = settings
        
        self.val_step = val_step

        self.slider.setMinimum(val_min)
        self.slider.setMaximum(val_max)
        self.slider.setTickInterval(val_step)
        self.slider.setSingleStep(val_step)
        self.slider.setPageStep(val_step)
        self.slider.setValue(val_start)

class InputWithIcon(StyledWidget):
    submit = pyqtSignal(str)
    
    def __init__(self, placeholder="", icon_path="",
                 height=None, icon_size=16, parent=None):
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
        self.button.clicked.connect(self._on_submit)
        layout.addWidget(self.button)

    def _on_submit(self):
        val = self.text_input.text()
        if val == "":
            return
        self.submit.emit(val)
        self.reset()

    def reset(self):
        self.text_input.clear()

class TagRow(StyledWidget):
    on_filter_changed = pyqtSignal(str, bool)
    
    def __init__(self, tag_name, height=32, anim=True, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setObjectName("tag_row")
        self.anim = anim
        
        self.tag_name = tag_name
        self.is_active = False

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
        self.tag_button.clicked.connect(self.toggle_active)
        layout.addWidget(self.tag_button)

        self.edit_button = QPushButton()
        self.edit_button.setIcon(QIcon("../icons/edit.png"))
        self.edit_button.setIconSize(QSize(16, 16))
        self.edit_button.setFixedSize(height, height)
        self.edit_button.setCursor(Qt.PointingHandCursor)
        self.edit_button.hide()
        layout.addWidget(self.edit_button)

    def enterEvent(self, event):
        if not self.anim:
            event.ignore()
            return
        self.delete_button.show()
        self.edit_button.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self.anim:
            event.ignore()
            return
        self.delete_button.hide()
        self.edit_button.hide()
        super().leaveEvent(event)

    def toggle_active(self):
        self.set_active(not self.is_active)

    def set_active(self, val: bool):
        self.is_active = val
        self.tag_button.setObjectName("tag_row_button" if self.is_active else "")
        self.tag_button.style().unpolish(self.tag_button)
        self.tag_button.style().polish(self.tag_button)
        self.tag_button.update()
        self.on_filter_changed.emit(self.tag_name, self.is_active)

    def reset(self):
        self.set_active(False)

class TagList(StyledWidget):
    def __init__(self, anim=True, parent=None):
        super().__init__(parent)

        self.tags = []
        self.anim = anim

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

    def add_tag(self, tag_name, insert_alpha=False):
        tag_row = TagRow(tag_name, anim=self.anim)
        self.tags.append(tag_row)
        
        if insert_alpha:
            insert_index = 0
            for i in range(self.content_layout.count() - 1):
                item = self.content_layout.itemAt(i)
                widget = item.widget()
                if isinstance(widget, TagRow):
                    existing_name = widget.tag_name
                    if existing_name.lower() > tag_name.lower():
                        break
                insert_index += 1
            self.content_layout.insertWidget(insert_index, tag_row)
        else:
            self.content_layout.insertWidget(self.content_layout.count() - 1, tag_row)

        return tag_row

    def clear_tags(self):
        for i in reversed(range(self.content_layout.count() - 1)):
            item = self.content_layout.itemAt(i)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
        self.tags.clear()

class Dropdown(QComboBox):
    on_filter_changed = pyqtSignal(str, object)
    
    def __init__(self, items=None, values=None,
                 width=None, height=None,
                 filter_key=None, parent=None):
        super().__init__(parent)
        self.setProperty("class", "dropdown")
        self.setCursor(Qt.PointingHandCursor)
        self.filter_key = filter_key
        self.values = values

        if items:
            self.addItems(items)
        if width:
            self.setFixedWidth(width)
        if height:
            self.setFixedHeight(height)
        if filter_key is not None:
            self.currentIndexChanged.connect(self._on_change)

    def _on_change(self, index):
        value = self.itemText(index) if self.values is None else self.values[index]
        self.on_filter_changed.emit(self.filter_key, value)

    def reset(self):
        self.setCurrentIndex(0)
        
class TextInput(QLineEdit):
    on_filter_changed = pyqtSignal(str, object)
    
    def __init__(self, placeholder="",
                 height=None, width=None,
                 filter_key=None, parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setProperty("class", "text_input")
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setCursor(Qt.IBeamCursor)
        self.filter_key = filter_key

        if width:
            self.setFixedWidth(width)
        if height:
            self.setFixedHeight(height)

        self.textChanged.connect(self._on_change)

    def _on_change(self, text):
        self.on_filter_changed.emit(self.filter_key, text)

    def reset(self):
        self.clear()

class TextButton(StyledButton):
    def __init__(self, text, height=None, parent=None):
        super().__init__(text=text, parent=parent)
        if height is not None:
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed if height == "fixed" else QSizePolicy.Expanding)

class DateTimeRangeInput(StyledWidget):
    on_filter_changed = pyqtSignal(str, object)
    
    def __init__(self, height=None, filter_key=None, parent=None):
        super().__init__(parent)
        self.setProperty("class", "datetime_range_input")
        self.filter_key = filter_key

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.start_input = QDateTimeEdit()
        self.start_input.setCalendarPopup(True)
        if height is not None:
            self.start_input.setFixedHeight(height)
        self.start_input.setDateTime(QDateTime.currentDateTime())

        self.end_input = QDateTimeEdit()
        self.end_input.setCalendarPopup(True)
        if height is not None:
            self.end_input.setFixedHeight(height)
        self.end_input.setDateTime(QDateTime.currentDateTime())
        
        self.start_input.dateTimeChanged.connect(self._on_change)
        self.end_input.dateTimeChanged.connect(self._on_change)

        layout.addWidget(self.start_input)
        layout.addWidget(self.end_input)

    def _on_change(self, _):
        if self.start_input.dateTime() > self.end_input.dateTime():
            if self.sender() is self.start_input:
                self.end_input.setDateTime(self.start_input.dateTime())
            else:
                self.start_input.setDateTime(self.end_input.dateTime())

        self.on_filter_changed.emit(self.filter_key + "_min", self.start_input.dateTime().toString("yyyy-MM-dd HH:mm:ss"))
        self.on_filter_changed.emit(self.filter_key + "_max", self.end_input.dateTime().toString("yyyy-MM-dd HH:mm:ss"))

    def get_range(self):
        return self.start_input.dateTime(), self.end_input.dateTime()

    def set_range(self, start_datetime, end_datetime):
        self.start_input.setDateTime(start_datetime)
        self.end_input.setDateTime(end_datetime)

    def reset(self):
        now = QDateTime.currentDateTime()
        self.start_input.setDateTime(now)
        self.end_input.setDateTime(now)

class RangeInput(QWidget):
    on_filter_changed = pyqtSignal(str, object)
    
    def __init__(self, min_val=0, max_val=100, height=None, filter_key=None, parent=None):
        super().__init__(parent)

        self.min_val = min_val
        self.max_val = max_val
        self.filter_key = filter_key

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

        self.min_input.valueChanged.connect(self._on_change)
        self.max_input.valueChanged.connect(self._on_change)

        layout.addWidget(self.min_input)
        layout.addWidget(self.max_input)

    def _on_change(self, _):
        sender = self.sender()
        if self.min_input.value() > self.max_input.value():
            if sender is self.min_input:
                self.max_input.setValue(self.min_input.value())
            else:
                self.min_input.setValue(self.max_input.value())

        self.on_filter_changed.emit(self.filter_key + "_min", self.min_input.value())
        self.on_filter_changed.emit(self.filter_key + "_max", self.max_input.value())

    def get_range(self):
        return self.min_input.value(), self.max_input.value()

    def set_range(self, min_value, max_value):
        self.min_input.setValue(min_value)
        self.max_input.setValue(max_value)

    def reset(self):
        self.set_range(self.min_val, self.min_val)

class IntInput(QWidget):
    on_filter_changed = pyqtSignal(str, object)
    
    def __init__(self, min_val=0, max_val=100, height=None, filter_key=None, parent=None):
        super().__init__(parent)
        self.filter_key = filter_key
        self.min_val = min_val
        self.max_val = max_val

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignCenter)

        self.input = QSpinBox()
        self.set_range(min_val, max_val)
        self.input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.input.valueChanged.connect(self._on_change)

        if height is not None:
            self.input.setFixedHeight(height)

        self.input.setValue(min_val)
        layout.addWidget(self.input)

    def _on_change(self, value):
        self.on_filter_changed.emit(self.filter_key, value)

    def get_value(self):
        return self.input.value()

    def set_range(self, min_value=None, max_value=None):
        self.min_val = min_value if min_value is not None else self.min_val
        self.max_val = max_value if max_value is not None else self.max_val
        if self.min_val > self.max_val:
            self.min_val = self.max_val
        self.input.setRange(self.min_val, self.max_val)

    def reset(self):
        self.input.setValue(self.min_val)

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

    def reset(self):
        self.setChecked(False)

class SplitIconToggleButton(QPushButton):
    on_filter_changed = pyqtSignal(str, object)
    
    def __init__(self, left_text, icon_off_path,
                 icon_on_path, right_text,
                 icon_size=24, height=None,
                 filter_key=None, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setProperty("class", "split_icon_toggle_button")
        self.filter_key = filter_key

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
        self.on_filter_changed.emit(self.filter_key, checked)

    def reset(self):
        self.setChecked(False)

class MediaControlBar(StyledWidget):
    def __init__(self, width=50, do_loop=True, do_shuffle=False, parent=None):
        super().__init__(parent)

        self.setProperty("class", "sidebar")
        self.setFixedWidth(width)
        self.parent = parent
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        # Button Options
        self.play_button = IconToggleButton("../icons/play.png", "../icons/pause.png")
        self.play_button.clicked.connect(lambda: self.window().slideshow_controls(False))
        layout.addWidget(self.play_button, alignment=Qt.AlignHCenter)
        
        button = IconButton("../icons/stop.png")
        button.clicked.connect(lambda: self.window().slideshow_controls(True))
        layout.addWidget(button, alignment=Qt.AlignHCenter)

        button = IconButton("../icons/restart.png")
        layout.addWidget(button, alignment=Qt.AlignHCenter)
        button.clicked.connect(lambda: self.window().restart())

        self.add_spacer(self.parent.grid_spacing)

        self.slider = VerticalSlider()
        self.layout().addWidget(self.slider, alignment=Qt.AlignHCenter)

        self.add_spacer(self.parent.grid_spacing)

        button = IconButton("../icons/fastest_forwards.png")
        layout.addWidget(button, alignment=Qt.AlignHCenter)

        button = IconButton("../icons/fastest_backwards.png")
        layout.addWidget(button, alignment=Qt.AlignHCenter)

        button = IconButton("../icons/skip_forwards.png")
        layout.addWidget(button, alignment=Qt.AlignHCenter)

        button = IconButton("../icons/skip_backwards.png")
        layout.addWidget(button, alignment=Qt.AlignHCenter)

        self.add_spacer(self.parent.grid_spacing)

        button = IconToggleButton("../icons/loop_off.png", "../icons/loop_on.png")
        button.setChecked(do_loop)
        button.update_icon(do_loop)
        button.toggled.connect(lambda checked: self.window().set_loop(checked))
        layout.addWidget(button, alignment=Qt.AlignHCenter)

        button = IconToggleButton("../icons/shuffle_off.png", "../icons/shuffle_on.png")
        button.setChecked(do_shuffle)
        button.update_icon(do_shuffle)
        button.toggled.connect(lambda checked: self.window().set_shuffle(checked))
        layout.addWidget(button, alignment=Qt.AlignHCenter)

        self.add_spacer(self.parent.grid_spacing)
        
        self.layout().addStretch()

    def add_spacer(self, height=10):
        spacer = StyledWidget()
        spacer.setObjectName("media_spacer")
        spacer.setFixedHeight(height)
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.layout().addWidget(spacer)

    def set_play_icon(self, val):
        self.play_button.update_icon(not val)

    def update_slider(self, settings):
        self.slider.update_slider(settings)

class SidebarSubHeader(QPushButton):
    toggled = pyqtSignal(str, bool)

    def __init__(self, title, filter_key="", height=None, parent=None):
        super().__init__(title, parent)
        self.filter_key = filter_key
        self.is_active = False

        self.setCursor(Qt.PointingHandCursor)
        self.setFlat(True)
        self.setStyleSheet("text-align: center;")
        self.setProperty("class", "sidebar_sub_header")

        if height is not None:
            self.setFixedHeight(height)

        self.clicked.connect(self.toggle_active)

    def toggle_active(self):
        self.is_active = not self.is_active
        self.setProperty(
            "class",
            "sidebar_sub_header_active" if self.is_active else "sidebar_sub_header"
        )
        self.style().unpolish(self)
        self.style().polish(self)

        self.toggled.emit(self.filter_key, self.is_active)

    def reset(self):
        if self.is_active:
            self.toggle_active()

class Sidebar(StyledWidget):
    def __init__(self, parent=None, width=200, spacing=0):
        super().__init__(parent)

        self.setProperty("class", "sidebar")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(spacing)
        self.setLayout(layout)
        
        self.setFixedWidth(width)

        self.widgets = []
    
    def add_header(self, title, height=None, class_name="sidebar_header"):
        header = QLabel(title)
        header.setProperty("class", class_name)
        header.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        if height is not None:
            header.setFixedHeight(height)
        self.layout().addWidget(header)

    def add_subheader(self, title, filter_key="", height=None):
        subheader = SidebarSubHeader(title, filter_key=filter_key, parent=self)
        self.layout().addWidget(subheader)
        return subheader

    def add_subheader_flat(self, title, height=None):
        self.add_header(title, height=height, class_name="sidebar_sub_header")

    def add_spacer(self, height=10):
        spacer = StyledWidget()
        spacer.setObjectName("media_spacer")
        spacer.setFixedHeight(height)
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.layout().addWidget(spacer)

    def add_widget(self, widget, height=None):
        if height is not None:
            widget.setFixedHeight(height)

        self.widgets.append(widget)
        self.layout().addWidget(widget)

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
