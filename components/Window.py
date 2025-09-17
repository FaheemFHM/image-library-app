
import sys
import random

from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow,
    QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy
)

from PyQt5.QtGui import QIcon

from PyQt5.QtCore import (
    Qt, QSize, QTimer, QMetaObject, Q_ARG, QThread, pyqtSignal
)

from components.Sidebar import Sidebar
from components.InputWidgets import (
    TextInput, IntInput, Dropdown, SplitIconToggleButton, RangeInput,
    DateTimeRangeInput, TextButton
)
from components.TagList import TagList
from components.MediaBar import MediaControlBar
from components.StyledWidgets import StyledWidget
from components.Gallery import (
    Gallery, GalleryCell, GalleryCellEdit
)
from components.Slideshow import SlideShow
from components.Database import DatabaseWorker

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
        
        self.db = DatabaseWorker("database.db")
        self.db.results_ready.connect(self.handle_results)
        self.db.error.connect(self.handle_error)
        
        self.db_thread = QThread()
        self.db.moveToThread(self.db_thread)
        self.db_thread.start()

        # Sidebar 1
        self.sidebar1 = Sidebar()
        
        self.sidebar1.add_header("Search", 32)

        self.sidebar1.add_spacer(self.grid_spacing)

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

        self.sidebar1.add_spacer(self.grid_spacing)
        
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

        self.sidebar1.add_spacer(self.grid_spacing)

        # Favourite
        subheader = self.sidebar1.add_subheader("Favourite", height=24, filter_key="is_favourite")
        self.widgets_filter.append(subheader)
        subheader.toggled.connect(self.update_filter_active)
        widget = Dropdown(["Favourites", "Non-Favourites"],
                          values=[True, False],
                          filter_key="is_favourite")
        widget.on_filter_changed.connect(self.update_filter)
        self.widgets_filter.append(widget)
        self.sidebar1.add_widget(widget, 24)
        
        # File Type
        subheader = self.sidebar1.add_subheader("File Type", height=24, filter_key="type")
        self.widgets_filter.append(subheader)
        subheader.toggled.connect(self.update_filter_active)
        self.call_worker("get_unique_values", "type", context="filter_type")

        # Format
        subheader = self.sidebar1.add_subheader("Format", height=24, filter_key="format")
        self.widgets_filter.append(subheader)
        subheader.toggled.connect(self.update_filter_active)
        self.call_worker("get_unique_values", "format", context="filter_format")

        # Camera
        subheader = self.sidebar1.add_subheader("Camera", height=24, filter_key="camera_model")
        self.widgets_filter.append(subheader)
        subheader.toggled.connect(self.update_filter_active)
        self.call_worker("get_unique_values", "camera_model", context="filter_camera")
        
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

        self.sidebar1.add_spacer(self.grid_spacing)
        
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

        self.sidebar2.add_spacer(self.grid_spacing)

        # Tag Mode
        self.tag_filter_mode = Dropdown(["Any", "All", "Exact", "None"],
                          values=["any", "all", "exact", "none"],
                          filter_key="tag_mode")
        self.tag_filter_mode.on_filter_changed.connect(self.update_filter)
        self.tag_filter_mode.setObjectName("tag_filter_mode")
        self.sidebar2.add_widget(self.tag_filter_mode, 24)

        # Tag List
        self.tag_list = TagList()
        self.tag_list.on_delete.connect(self.delete_tag)
        self.tag_list.on_add.connect(self.add_tag)
        self.tag_list.on_edit.connect(self.edit_tag)
        self.sidebar2.add_widget(self.tag_list)
        self.call_worker("get_all_tags", context="all_tags")

        self.sidebar2.add_spacer(self.grid_spacing)
        self.sidebar2.add_header("Other", 32)
        self.sidebar2.add_spacer(self.grid_spacing)

        # Details
        self.sidebar2.add_subheader_flat("Details", 24)
        items = ["Dimensions", "Filesize", "Camera Model", "Times Viewed",
                 "Duration Viewed", "Date Captured", "Date Added"]
        for item in items:
            btn = TextButton(item, toggle_class="tag_row_button", height="fixed")
            btn.on_toggle.connect(lambda _, i=item: self.update_details(i))
            self.sidebar2.add_widget(btn, 24)
        
        self.sidebar2.add_spacer(self.grid_spacing)

        # Columns
        self.sidebar2.add_subheader_flat("Columns", 24)
        gallery_cols_max, gallery_cols = 7, 4
        col_input = IntInput(min_val=1, max_val=gallery_cols_max, val=gallery_cols_max)
        col_input.on_filter_changed.connect(self.edit_columns)
        self.sidebar2.add_widget(col_input, 24)
        
        self.sidebar2.add_spacer(self.grid_spacing)

        # Apply Filters
        button = TextButton("Apply", height="fixed")
        button.setObjectName("apply_button")
        button.setFixedHeight(128)
        button.clicked.connect(self.apply_filters)
        self.sidebar2.add_widget(button)

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
        self.gallery = Gallery(columns=gallery_cols_max, columns_max=gallery_cols_max, parent=self)
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
        self.gallery.update_details()
        col_input.set_value(gallery_cols)

    def call_worker(self, method_name, *args, **kwargs):
        context = kwargs.pop("context", None)
        QMetaObject.invokeMethod(
            self.db,
            "run_task",
            Qt.QueuedConnection,
            Q_ARG(str, method_name),
            Q_ARG(object, args),
            Q_ARG(object, kwargs),
            Q_ARG(object, context)
        )

    def handle_results(self, method_name, result, context=None):
        match method_name:
            case "add_tag":
                if result:
                    widget = self.tag_list.add_tag(context, insert_alpha=True)
                    widget.on_filter_changed.connect(self.update_filter_tags)
                    self.all_tags.append(context)
                else:
                    print(f"Failed to add tag: {context}")

            case "get_unique_values":
                match context:
                    case "filter_type":
                        self.add_filter_dropdown("type", result)
                    case "filter_format":
                        self.add_filter_dropdown("format", result)
                    case "filter_camera":
                        self.add_filter_dropdown("camera_model", result)

            case "rename_tag":
                if result:
                    _, old_tag, new_tag = context
                    self.all_tags = [new_tag if t == old_tag else t for t in self.all_tags]
                    self.tag_list.close_edit(new_tag)

            case "remove_tag_by_name":
                if result:
                    _, tag_name = context
                    self.all_tags.remove(tag_name)
                    self.tag_list.delete_tag(tag_name)
                    if not self.all_tags:
                        self.gallery.filters['tags'].clear()

            case "apply_filters" if context == "populate_gallery":
                image_records = result
                print(f"[DEBUG] Got {len(image_records)} records from DB")
                
                self.gallery.clear_grid_layout(self.gallery.grid_layout)

                i = 0
                for record in image_records:
                    if i >= self.gallery.cells_max:
                        break
                    self.gallery.add_cell(GalleryCell(record, window=self, parent=self.gallery))
                    i += 1

                self.gallery.update_cell_sizes()
                self.gallery.update_details()
                self.slideshow.set_image_paths(self.gallery.get_image_paths())
                print("[DEBUG] Populated gallery")

            case "get_all_tags":
                self.populate_tags(result)

    def handle_error(self, method_name, error_message, context=None):
        """
        Handles errors from the DatabaseWorker.

        Parameters:
            method_name (str): The name of the DB method that failed.
            error_message (str): The exception or error string.
            context (optional): Any extra context passed when calling the worker.
        """
        print(f"[DB ERROR] Method: {method_name}, Context: {context}, Error: {error_message}")

    def add_filter_dropdown(self, filter_key, items):
        items = [x for x in items if x is not None]
        dropdown = Dropdown(items, filter_key=filter_key)
        dropdown.on_filter_changed.connect(self.update_filter)
        self.widgets_filter.append(dropdown)

        layout = self.sidebar1.layout()
        for i in range(layout.count()):
            item = layout.itemAt(i).widget()
            if getattr(item, "filter_key", None) == filter_key:
                layout.insertWidget(i + 1, dropdown)
                break

    def populate_tags(self, tags):
        self.all_tags = tags
        for tag in tags:
            widget = self.tag_list.add_tag(tag)
            widget.on_filter_changed.connect(self.update_filter_tags)

    def open_gallery_edit(self, data, cell):
        self.gallery.hide()
        self.sidebars_toggle(True, False, False)
        self.gallery_edit.show()
        self.gallery_edit.set_data(data, sorted(self.all_tags), cell)

    def apply_gallery_edit(self, image_id, filename, tags):
        if filename:
            self.call_worker("set_image_filename", image_id, filename)
        if tags is not None:
            self.call_worker("set_image_tags", image_id, tags)

    def close_gallery_edit(self):
        self.gallery_edit.hide()
        self.sidebars_toggle(True, True, True)
        self.gallery.show()

    def update_details(self, detail):
        self.gallery.update_details(detail)

    def edit_columns(self, _, amount):
        self.gallery.set_columns(amount)

    def add_tag(self, tag):
        self.call_worker("add_tag", tag)
    
    def edit_tag(self, old_tag, new_tag):
        self.call_worker("rename_tag", old_tag, new_tag, context=("edit_tag", old_tag, new_tag))


    def delete_tag(self, tag):
        tag_name = tag.tag_name
        self.call_worker("remove_tag_by_name", tag_name, context=("delete_tag", tag_name))

    def apply_filters(self):
        self.gallery.populate_gallery()

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
        self.call_worker("toggle_favourite", image_id, toggled, context=("toggle_favourite", image_id, toggled))
