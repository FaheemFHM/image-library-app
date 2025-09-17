
import sys
import re
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout,
    QLabel, QScrollArea, QSizePolicy, QTableWidget, QTableWidgetItem, QHeaderView
)

from PyQt5.QtGui import QPixmap

from PyQt5.QtCore import Qt, QDateTime, pyqtSignal

from components.StyledWidgets import StyledWidget
from components.Sidebar import Sidebar
from components.InputWidgets import (
    TextInput, TextButton, IconButton, IconToggleButton
)
from components.TagList import TagList
from components.Slideshow import SlideShow

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
        
        self.tag_list = TagList(read_only=True)
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
        if filename:
            self.old_name.setText(filename)
            filename += self.extension

        # tags
        new_tags = [tag.tag_name for tag in self.tag_list.tags if tag.is_active]
        if set(self.original_tags) != set(new_tags):
            self.original_tags = new_tags.copy()
        else:
            new_tags = None
        
        # signal
        self.do_apply.emit(self.data['id'], filename, new_tags)
        self.my_cell.update_cell(filename, new_tags)
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

    def set_data(self, data, all_tags, my_cell):
        self.data = data.copy()
        self.my_cell = my_cell
        
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

class GalleryCellTable(QTableWidget):
    def __init__(self, data=None, width=None, row_height=24, parent=None):
        super().__init__(parent)
        self.row_height = row_height
        self.headers = []

        # No headers
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)

        # No scrollbars
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # No selection
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSelectionMode(QTableWidget.NoSelection)

        # Stretch columns
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        if width:
            self.setFixedWidth(width)

        if data:
            self.set_data(data)

    def set_data(self, data):
        self.clear()
        self.setRowCount(len(data))
        self.setColumnCount(len(data[0]) if data else 0)
        self.headers = [row[0] for row in data if row]

        for row_idx, row in enumerate(data):
            for col_idx, value in enumerate(row):
                self.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
            self.setRowHeight(row_idx, self.row_height)

        total_height = self.row_height * self.rowCount()
        self.setFixedHeight(total_height)

    def set_rows(self, headers):
        visible_rows = 0
        for row in range(self.rowCount()):
            item = self.item(row, 0)
            if item and item.text() in headers:
                self.setRowHidden(row, False)
                visible_rows += 1
            else:
                self.setRowHidden(row, True)

        total_height = self.row_height * visible_rows
        self.setFixedHeight(total_height)

    def hide_row(self, row_index):
        self.setRowHidden(row_index, True)

    def show_row(self, row_index):
        self.setRowHidden(row_index, False)

    def update_cell(self, row, col, new_value):
        if not self.item(row, col):
            self.setItem(row, col, QTableWidgetItem(str(new_value)))
        else:
            self.item(row, col).setText(str(new_value))

class GalleryCell(StyledWidget):
    edit_cell = pyqtSignal(object, object)
    
    def __init__(self, record, window, spacing=10, footer_height=32, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_Hover, True)
        self.setMouseTracking(True)

        self.data = record
        self.image_path = record['filepath']
        self.image_id = record['id']
        self.window = window
        self.spacing = spacing

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
        
        self.label_name = QLabel(self.data['filename'])

        self.edit_button = IconButton("../icons/edit.png", 20, footer_height)
        self.edit_button.setVisible(False)
        self.edit_button.clicked.connect(lambda: self.edit_cell.emit(self.data, self))

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
        
        # Details Table
        table_data = []
        table_data.append(["Dimensions", f"{self.data.get('height') or 0} * {self.data.get('width') or 0}"])
        filesize = self.data.get('filesize') or 0
        table_data.append(["Filesize", f"{filesize // 1000} KB"])
        table_data.append(["Camera Model", str(self.data.get('camera_model') or 'N/A')])
        table_data.append(["Times Viewed", str(self.data.get('times_viewed') or 0)])
        table_data.append(["Duration Viewed", str(self.data.get('time_viewed') or 0)])
        table_data.append(["Date Captured", str(self.data.get('date_captured') or 'Unknown')])
        table_data.append(["Date Added", str(self.data.get('date_added') or 'Unknown')])
        self.details = GalleryCellTable(table_data, width=self.width, parent=self)
        layout.addWidget(self.details)

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

    def update_cell(self, filename, new_tags):
        if filename:
            self.data['filename'] = filename
            self.label_name.setText(self.data['filename'])
        if new_tags is not None:
            self.data['tags'] = new_tags.copy()

    def update_details(self, details):
        self.details.set_rows(details)
        self.details.hide() if not details else self.details.show()

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

        # table
        self.details.setFixedWidth(width)
        self.details.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for col in range(self.details.columnCount()):
            self.details.horizontalHeader().resizeSection(col, width // self.details.columnCount())

class Gallery(StyledWidget):
    edit_cell = pyqtSignal(object, object)
    
    def __init__(self, columns=3, columns_max=10, spacing=10, parent=None):
        super().__init__(parent)

        self.columns = columns
        self.columns_max = columns_max
        self.spacing = spacing
        self.cell_count = 0
        self.cells = []
        self.cell_width = 10
        self.cells_max = 30
        self.parent = parent
        self.details = []

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

    def update_details(self, detail=None):
        if detail:
            if detail in self.details:
                self.details.remove(detail)
            else:
                self.details.append(detail)
        for cell in self.cells:
            cell.update_details(self.details)

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

        self.parent.call_worker(
            "apply_filters",
            self.filters,
            self.filters_active,
            context="populate_gallery"
        )

    def add_cell(self, widget):
        row = self.cell_count // self.columns
        col = self.cell_count % self.columns
        self.grid_layout.addWidget(widget, row, col, alignment=Qt.AlignTop | Qt.AlignLeft)
        self.cells.append(widget)
        self.cell_count += 1
        widget.edit_cell.connect(self.edit_cell.emit)

    def set_columns(self, val, do_set=True):
        if do_set:
            self.columns = max(1, min(val, self.columns_max))
        else:
            self.columns = max(1, min(self.columns + val, self.columns_max))
        self.resize()

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
