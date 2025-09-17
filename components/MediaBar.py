
from PyQt5.QtWidgets import QVBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt

from components.StyledWidgets import StyledWidget
from components.InputWidgets import (
    IconToggleButton, IconButton, VerticalSlider
)

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
        layout.addWidget(button, alignment=Qt.AlignHCenter)

        self.add_spacer(self.parent.grid_spacing)

        self.slider = VerticalSlider()
        self.layout().addWidget(self.slider, alignment=Qt.AlignHCenter)

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
        return spacer

    def set_play_icon(self, val):
        self.play_button.update_icon(not val)

    def update_slider(self, settings):
        self.slider.update_slider(settings)
