
import random

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer, pyqtSignal

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
            print("no original images")
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
