
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QSpinBox, QComboBox, QSizePolicy, QDateTimeEdit, QSlider
)

from PyQt5.QtGui import QIcon, QCursor

from PyQt5.QtCore import Qt, QSize, QDateTime, pyqtSignal

from components.StyledWidgets import StyledButton
from components.StyledWidgets import StyledWidget

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
    on_toggle = pyqtSignal(str)
    
    def __init__(self, text, height=None, toggle_class=None, parent=None):
        super().__init__(text=text, parent=parent)
        if height is not None:
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed if height == "fixed" else QSizePolicy.Expanding)
        if toggle_class is not None:
            self.toggle_class = toggle_class
            self.is_active = False
            self.clicked.connect(self.toggle_active)

    def toggle_active(self):
        self.is_active = not self.is_active
        self.setObjectName(self.toggle_class if self.is_active else "")
        self.style().unpolish(self)
        self.style().polish(self)
        self.on_toggle.emit(self.text())
        
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
    
    def __init__(self, min_val=0, max_val=100, val=1, height=None, filter_key=None, parent=None):
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
        self.input.setValue(val)
        self.input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.input.valueChanged.connect(self._on_change)

        if height is not None:
            self.input.setFixedHeight(height)

        layout.addWidget(self.input)

    def _on_change(self, value):
        value = max(self.min_val, min(value, self.max_val))
        self.on_filter_changed.emit(self.filter_key, value)

    def get_value(self):
        return self.input.value()

    def set_value(self, value):
        value = max(self.min_val, min(value, self.max_val))
        self.input.setValue(value)

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
