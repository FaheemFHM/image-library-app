

import sys
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

        # Sidebar 1
        self.sidebar1 = Sidebar()
        self.sidebar1.add_header("Search", 32)
        self.sidebar1.add_widget(TextInput("Enter Query..."), 24)
        self.sidebar1.add_widget(SplitIconToggleButton("Name", "../icons/toggle_off.png", "../icons/toggle_on.png", "ID"), 24)
        self.sidebar1.add_spacer(self.grid_spacing)
        
        self.sidebar1.add_header("Sort", 32)
        self.sidebar1.add_widget(Dropdown(["Date", "Name", "ID", "Size", "Height", "Width"]), 24)
        self.sidebar1.add_widget(SplitIconToggleButton("Asc", "../icons/toggle_off.png", "../icons/toggle_on.png", "Desc"), 24)
        self.sidebar1.add_spacer(self.grid_spacing)
        
        self.sidebar1.add_header("Filters", 32)
        
        subheader = self.sidebar1.add_subheader("Favourite", height=24, filter_key="is_favourite")
        widget = Dropdown(["Any", "Favourites", "Non-Favourites"], filter_key="is_favourite")
        self.sidebar1.add_widget(widget, 24)
        
        subheader = self.sidebar1.add_subheader("File Type", height=24, filter_key="type")
        widget = Dropdown(["Any", "Images", "Videos"], filter_key="type")
        self.sidebar1.add_widget(widget, 24)
        
        subheader = self.sidebar1.add_subheader("Format", height=24, filter_key="format")
        widget = Dropdown(["Any", "PNG", "JPEG", "VIDEO", "MP3"], filter_key="format")
        self.sidebar1.add_widget(widget, 24)
        
        subheader = self.sidebar1.add_subheader("Camera", height=24, filter_key="camera_model")
        widget = Dropdown(["Any", "Samsung", "Nokia 7.2", "Apple"], filter_key="camera_model")
        self.sidebar1.add_widget(widget, 24)
        
        subheader = self.sidebar1.add_subheader("File Size", height=24, filter_key="filesize")
        widget = RangeInput(0, 999999999, filter_key="filesize")
        self.sidebar1.add_widget(widget, 24)
        
        subheader = self.sidebar1.add_subheader("Image Height", height=24, filter_key="height")
        widget = RangeInput(0, 99999, filter_key="height")
        self.sidebar1.add_widget(widget, 24)
        
        subheader = self.sidebar1.add_subheader("Image Width", height=24, filter_key="width")
        widget = RangeInput(0, 99999, filter_key="width")
        self.sidebar1.add_widget(widget, 24)
        
        subheader = self.sidebar1.add_subheader("Times Viewed", height=24, filter_key="times_viewed")
        widget = RangeInput(0, 99999999, filter_key="times_viewed")
        self.sidebar1.add_widget(widget, 24)
        
        subheader = self.sidebar1.add_subheader("Duration Viewed", height=24, filter_key="time_viewed")
        widget = RangeInput(0, 99999999, filter_key="time_viewed")
        self.sidebar1.add_widget(widget, 24)
        
        subheader = self.sidebar1.add_subheader("Date Captured", height=24, filter_key="exif_date")
        self.sidebar1.add_widget(DateTimeRangeInput(24))
        
        subheader = self.sidebar1.add_subheader("Date Added", height=24, filter_key="added_on")
        self.sidebar1.add_widget(DateTimeRangeInput(24))
        self.sidebar1.add_spacer(self.grid_spacing)
        
        self.sidebar1.add_header("Reset", 32)
        self.sidebar1.add_widget(TextButton("Search"), 24)
        self.sidebar1.add_widget(TextButton("Sort"), 24)
        self.sidebar1.add_widget(TextButton("Filter"), 24)
        self.sidebar1.add_widget(TextButton("Tags"), 24)
        self.sidebar1.add_widget(TextButton("All"), 24)
        self.sidebar1.add_spacer(self.grid_spacing)
        
        self.sidebar1.add_stretch()
        
        # Sidebar 2
        self.sidebar2 = Sidebar()
        
        self.sidebar2.add_header("Tags", 32)
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
        self.sidebar2.add_widget(tag_list)
        self.sidebar2.add_widget(InputWithIcon("Add Tag...", "../icons/plus.png", 32, 20))

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
        
        self.db = MediaDatabase()
        #self.db.create_tables()
        #self.db.populate_media()

        main_layout.addWidget(self.gallery)

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

        self.gallery.populate_gallery()
    
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
        self.slideshow.show()
        self.sidebars_toggle(True, False)
        self.slideshow.play()
        self.media_controls.set_play_icon(False)

    def pause(self):
        self.slideshow.pause()
        self.media_controls.set_play_icon(True)

    def stop(self):
        self.slideshow.stop()
        self.sidebars_toggle(True, True)
        self.slideshow.hide()
        self.gallery.show()
        self.media_controls.set_play_icon(True)

    def resume(self):
        self.slideshow.resume()
        self.media_controls.set_play_icon(False)

    def restart(self):
        self.slideshow.restart()

    def set_slideshow_speed(self, val):
        self.slideshow.change_speed(val)

    def sidebars_toggle(self, do_set=False, do_show=False):
        if not do_set:
            do_show = not self.sidebar1.isVisible()

        for sidebar in [self.sidebar1, self.sidebar2]:
            if sidebar:
                sidebar.setVisible(do_show)

    def set_loop(self, val):
        self.slideshow.set_loop(val)
    
    def set_shuffle(self, val):
        self.slideshow.set_shuffle(val)

    def toggle_favourite(self, image_id, toggled):
        self.db.toggle_favourite(image_id, toggled)

class GalleryCell(StyledWidget):
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

        self.label_name = QLabel(Path(self.image_path).name)

        self.edit_button = IconButton("../icons/edit.png", 20, footer_height)
        self.edit_button.setVisible(False)
        #self.edit_button.clicked.connect(self.edit_popup)

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
        self.cells_max = 40
        self.parent = parent

        self.search_names = True
        self.sort_asc = True

        self.filters = {
            "id": 27,
            "filename": "IMG_20220715_112916.jpg",
            "is_favourite": True,
            "type": "image",
            "format": "JPEG",
            "camera_model": "Nokia 7.2",
            "filesize_min": None,
            "filesize_max": None,
            "height_min": None,
            "height_max": None,
            "width_min": None,
            "width_max": None,
            "times_viewed_min": None,
            "times_viewed_max": None,
            "time_viewed_min": None,
            "time_viewed_max": None,
            "date_captured_min": None,
            "date_captured_max": None,
            "date_added_min": None,
            "date_added_max": None
        }

        self.filters_active = {
            "id": True,
            "filename": False,
            "is_favourite": True,
            "type": False,
            "format": True,
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

    def clear_grid_layout(self, grid_layout):
        [w.setParent(None) or w.deleteLater() for i in reversed(range(grid_layout.count())) if (w := grid_layout.itemAt(i).widget())]

    def populate_gallery(self):
        self.clear_grid_layout(self.grid_layout)

        image_records = self.parent.db.apply_filters(self.filters, self.filters_active)
        
        i = 0
        for record in image_records:
            if i >= self.cells_max:
                return
            self.add_cell(GalleryCell(record, window=self.parent, parent=self))
            i += 1

        if self.cell_count < self.columns:
            self.grid_layout.setColumnStretch(self.columns, 1)
            self.grid_layout.setRowStretch(1, 1)

    def add_cell(self, widget):
        row = self.cell_count // self.columns
        col = self.cell_count % self.columns
        self.grid_layout.addWidget(widget, row, col, alignment=Qt.AlignTop | Qt.AlignLeft)
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
        selected = self.tag_button.objectName() != "tag_row_button"
        if selected:
            self.tag_button.setObjectName("tag_row_button")
        else:
            self.tag_button.setObjectName("")
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
    def __init__(self, items=None, width=None, height=None, filter_key=None, parent=None):
        super().__init__(parent)
        self.setProperty("class", "dropdown")
        self.setCursor(Qt.PointingHandCursor)
        self.filter_key = filter_key
        
        if items:
            self.addItems(items)
        if width:
            self.setFixedWidth(width)
        if height:
            self.setFixedHeight(height)
        if filter_key is not None:
            self.currentIndexChanged.connect(self._on_change)

    def _on_change(self, index):
        value = self.itemText(index)
        
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

class DateTimeRangeInput(StyledWidget):
    def __init__(self, height=None, filter_key=None, parent=None):
        super().__init__(parent)
        self.setProperty("class", "datetime_range_input")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # --- Start Date/Time ---
        self.start_input = QDateTimeEdit()
        self.start_input.setCalendarPopup(True)
        if height is not None:
            self.start_input.setFixedHeight(height)
        self.start_input.setDateTime(QDateTime.currentDateTime())

        # --- End Date/Time ---
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

    def get_range(self):
        return self.start_input.dateTime(), self.end_input.dateTime()

    def set_range(self, start_datetime, end_datetime):
        self.start_input.setDateTime(start_datetime)
        self.end_input.setDateTime(end_datetime)

class RangeInput(QWidget):
    def __init__(self, min_val=0, max_val=100, height=None, filter_key=None, parent=None):
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

        self.min_input.valueChanged.connect(self._on_change)
        self.max_input.valueChanged.connect(self._on_change)

        layout.addWidget(self.min_input)
        layout.addWidget(self.max_input)

    def _on_change(self, _):
        if self.min_input.value() > self.max_input.value():
            if self.sender() is self.min_input:
                self.max_input.setValue(self.min_input.value())
            else:
                self.min_input.setValue(self.max_input.value())

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

        self.clicked.connect(self._on_clicked)

    def _on_clicked(self):
        self.toggle_active()

    def toggle_active(self):
        self.is_active = not self.is_active
        self.setProperty(
            "class",
            "sidebar_sub_header_active" if self.is_active else "sidebar_sub_header"
        )
        self.style().unpolish(self)
        self.style().polish(self)

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
    
    def add_header(self, title, height=None):
        header = QLabel(title)
        header.setProperty("class", "sidebar_header")
        header.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        if height is not None:
            header.setFixedHeight(height)
        self.layout().addWidget(header)

    def add_subheader(self, title, filter_key="", height=None):
        subheader = SidebarSubHeader(title, filter_key=filter_key)
        self.layout().addWidget(subheader)
        return subheader

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
