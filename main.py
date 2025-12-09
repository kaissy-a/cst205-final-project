import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QHBoxLayout, QVBoxLayout, QSlider, QFileDialog
)
from PySide6.QtCore import Slot, QUrl, Qt
from PySide6.QtMultimedia import QMediaPlayer
from __feature__ import snake_case, true_property


app = QApplication([])


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()

        play = QPushButton("Playlists")
        upload = QPushButton("Upload")

        vbox = QVBoxLayout()
        vbox.add_widget(play)
        vbox.add_widget(upload)

        self.set_layout(vbox)

        play.clicked.connect(self.open_ply)
        upload.clicked.connect(self.open_up)

    @Slot()
    def open_ply(self):
        self.ply = Playlist()
        self.ply.show()

    @Slot()
    def open_up(self):
        self.upload = Upload()
        self.upload.show()


class Playlist(QWidget):
    def __init__(self):
        super().__init__()



        self.player = QMediaPlayer(self)


        self.open_button = QPushButton("Open File")
        self.play_pause_button = QPushButton("Play")


        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.set_range(0, 0)


        self.position_label = QLabel("0:00 / 0:00")


        controls = QHBoxLayout()
        controls.add_widget(self.open_button)
        controls.add_widget(self.play_pause_button)

        slider_row = QHBoxLayout()
        slider_row.add_widget(self.position_slider)
        slider_row.add_widget(self.position_label)

        layout = QVBoxLayout()
        layout.add_layout(controls)
        layout.add_layout(slider_row)

        self.set_layout(layout)

 
        self.user_dragging = False


        self.open_button.clicked.connect(self.open_file)
        self.play_pause_button.clicked.connect(self.toggle_play)

        self.player.positionChanged.connect(self.update_position)
        self.player.durationChanged.connect(self.update_duration)


        self.position_slider.sliderPressed.connect(self.slider_pressed)
        self.position_slider.sliderReleased.connect(self.slider_released)


    @Slot()
    def open_file(self):
        file, _ = QFileDialog.get_open_file_name(
            self, "Open Audio", "", "Audio Files (*.mp3 *.wav *.ogg)"
        )
        if not file:
            return

        try:
            self.player.set_source(QUrl.from_local_file(file))
        except Exception:
            self.player.set_media(QUrl.from_local_file(file))

        self.play_pause_button.set_text("Play")


    @Slot()
    def toggle_play(self):
        try:
            playing = self.player.playback_state == QMediaPlayer.PlayingState
        except Exception:
            playing = False

        if playing:
            self.player.pause()
            self.play_pause_button.set_text("Play")
        else:
            self.player.play()
            self.play_pause_button.set_text("Pause")


    @Slot(int)
    def update_position(self, pos):
        if not self.user_dragging:
            self.position_slider.set_value(pos)

        self.update_time_label(pos, self.player.duration)

    @Slot(int)
    def update_duration(self, dur):
        self.position_slider.set_range(0, dur)


    @Slot()
    def slider_pressed(self):
        self.user_dragging = True

    @Slot()
    def slider_released(self):
        self.user_dragging = False
        self.player.set_position(self.position_slider.value())

    def update_time_label(self, pos_ms, dur_ms):
        def fmt(ms):
            if ms is None:
                return "0:00"
            s = int(ms / 1000)
            return f"{s // 60}:{s % 60:02d}"

        self.position_label.set_text(f"{fmt(pos_ms)} / {fmt(dur_ms)}")


class Upload(QWidget):
    def __init__(self):
        super().__init__()
        test = QLabel("test")
        vbox = QVBoxLayout()
        vbox.add_widget(test)
        self.set_layout(vbox)


main = MyWindow()
main.show()
sys.exit(app.exec())
