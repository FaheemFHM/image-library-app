
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QSizePolicy
)

from PyQt5.QtCore import Qt, pyqtSignal

from components.StyledWidgets import StyledWidget

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
