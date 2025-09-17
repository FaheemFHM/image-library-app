
from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5.QtCore import Qt, QSize

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
