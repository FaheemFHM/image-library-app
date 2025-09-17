
import re

from PyQt5.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QPushButton, QLineEdit,
    QScrollArea, QSizePolicy
)

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize, pyqtSignal

from components.StyledWidgets import StyledWidget
from components.InputWidgets import InputWithIcon

class TagRow(StyledWidget):
    on_filter_changed = pyqtSignal(str, bool)
    on_delete = pyqtSignal()
    on_edit = pyqtSignal()
    
    def __init__(self, tag_name, height=32, read_only=False, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setObjectName("tag_row")
        self.read_only = read_only
        
        self.tag_name = tag_name
        self.is_active = False
        self.is_editing = False

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
        self.delete_button.clicked.connect(self.on_delete.emit)
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
        self.edit_button.clicked.connect(self.on_edit.emit)
        layout.addWidget(self.edit_button)

    def enterEvent(self, event):
        if self.read_only:
            event.ignore()
            return
        self.delete_button.show()
        self.edit_button.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.read_only:
            event.ignore()
            return
        self.delete_button.hide()
        self.edit_button.hide()
        super().leaveEvent(event)

    def set_text(self, txt):
        self.tag_name = txt
        self.tag_button.setText(txt)

    def toggle_active(self):
        self.set_active(not self.is_active)

    def set_active(self, val: bool):
        self.is_active = val
        self.update_style()
        self.on_filter_changed.emit(self.tag_name, self.is_active)

    def set_editing(self, val: bool):
        self.is_editing = val
        self.update_style()

    def reset(self):
        self.is_editing = False
        self.set_active(False)

    def update_style(self):
        if self.is_editing:
            class_name = "tag_row_edit"
        elif self.is_active:
            class_name = "tag_row_button"
        else:
            class_name = ""

        self.tag_button.setObjectName(class_name)
        self.tag_button.style().unpolish(self.tag_button)
        self.tag_button.style().polish(self.tag_button)
        self.tag_button.update()

class TagEdit(StyledWidget):
    on_submit = pyqtSignal(str, str)
    
    def __init__(self, height=32, my_tag=None, parent=None):
        super().__init__(parent)
        self.my_tag = my_tag
        
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.cancel_button = QPushButton()
        self.cancel_button.setIcon(QIcon("../icons/cross.png"))
        self.cancel_button.setIconSize(QSize(20, 20))
        self.cancel_button.setFixedSize(height, height)
        self.cancel_button.setCursor(Qt.PointingHandCursor)
        self.cancel_button.clicked.connect(self.close)
        layout.addWidget(self.cancel_button)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Edit: tag")
        self.input_field.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.input_field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.input_field.setFixedHeight(height)
        layout.addWidget(self.input_field)

        self.submit_button = QPushButton()
        self.submit_button.setIcon(QIcon("../icons/tick.png"))
        self.submit_button.setIconSize(QSize(16, 16))
        self.submit_button.setFixedSize(height, height)
        self.submit_button.setCursor(Qt.PointingHandCursor)
        self.submit_button.clicked.connect(lambda: self.on_submit.emit(self.my_tag.tag_name, self.input_field.text()))
        layout.addWidget(self.submit_button)

        self.hide()

    def open(self, tag):
        if self.my_tag:
            self.close()
        self.my_tag = tag
        self.my_tag.set_editing(True)
        self.input_field.setPlaceholderText(f"Edit: {self.my_tag.tag_name}")
        self.input_field.setText(self.my_tag.tag_name)
        self.show()

    def close(self):
        self.my_tag.set_editing(False)
        self.my_tag = None
        self.hide()

class TagList(StyledWidget):
    on_delete = pyqtSignal(object)
    on_add = pyqtSignal(str)
    on_edit = pyqtSignal(str, str)
    
    def __init__(self, read_only=False, parent=None):
        super().__init__(parent)

        self.tags = []
        self.read_only = read_only

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

        self.tag_edit = TagEdit(parent=self)
        self.tag_edit.on_submit.connect(self.attempt_edit)
        layout.addWidget(self.tag_edit)

        if not self.read_only:
            self.tag_add = InputWithIcon("Add Tag...", "../icons/plus.png", 32, 20)
            self.tag_add.submit.connect(self.attempt_add)
            layout.addWidget(self.tag_add)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.setObjectName("tag_list")
        self.content_widget.setObjectName("tag_list_content")
        self.scroll_area.setObjectName("tag_list_scroll")

    def delete_tag(self, tag):
        self.tags.remove(tag)
        self.content_layout.removeWidget(tag)
        tag.setParent(None)
        tag.deleteLater()

    def attempt_add(self, new_name):
        new_name = self.sanitise(new_name)
        if not new_name:
            return
        self.on_add.emit(new_name)
    
    def attempt_edit(self, old_name, new_name):
        new_name = self.sanitise(new_name)
        if not new_name:
            return
        self.on_edit.emit(old_name, new_name)

    def add_tag(self, tag_name, insert_alpha=False):
        tag_row = TagRow(tag_name, read_only=self.read_only, parent=self)
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

        tag_row.on_delete.connect(lambda: self.on_delete.emit(tag_row))
        tag_row.on_edit.connect(lambda: self.open_edit(tag_row))
        return tag_row

    def clear_tags(self):
        for i in reversed(range(self.content_layout.count() - 1)):
            item = self.content_layout.itemAt(i)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
        self.tags.clear()

    def open_edit(self, tag):
        self.scroll_area.verticalScrollBar().setEnabled(False)
        self.tag_add.hide()
        self.tag_edit.open(tag)

    def close_edit(self, new_tag_name):
        self.tag_edit.my_tag.set_text(new_tag_name)
        self.tag_edit.close(new_tag_name)
        self.scroll_area.verticalScrollBar().setEnabled(True)
        self.tag_add.show()

    def sanitise(self, s):
        s = s.strip()

        if not s:
            return None

        s = re.sub(r"\s+", "_", s)

        disallowed_chars = [
            "!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "+", "=",
            "{", "}", "[", "]", "|", "\\", ":", ";", "\"", "'", "<", ">",
            ",", ".", "?", "/", "~", "`", "."
        ]
        s = "".join(c for c in s if c not in disallowed_chars)
        
        return s if s else None
