import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QHBoxLayout, QVBoxLayout, QSlider, QFileDialog, QComboBox
)
from PySide6.QtCore import Slot, QUrl, Qt
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from __feature__ import snake_case, true_property


app = QApplication([])

#main menu
class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        #layout a buttons from main menu
        play = QPushButton("Playlists")
        upload = QPushButton("Upload")

        vbox = QVBoxLayout()
        vbox.add_widget(play)
        vbox.add_widget(upload)

        self.set_layout(vbox)

        self.ply = None 

        play.clicked.connect(self.open_ply)
        upload.clicked.connect(self.open_up)
#opens playlist
    @Slot()
    def open_ply(self):
        if self.ply is None:
            self.ply = Playlist()
        self.ply.show()
#opens upload window
    @Slot()
    def open_up(self):
        self.upload = Upload(self)
        self.upload.show()
    #sends the selcted song path to the playlsit
    def add_song (self, file_path):
        if self.ply is None:
            self.ply = Playlist()

        self.ply.add_song(file_path)
        self.ply.show()
#playlist window 
class Playlist(QWidget):
    def __init__(self):
        super().__init__()
    #stores the files for songs
        self.song_list = []
#dropdown menu for the songs or any audio files
        self.song_dropdown = QComboBox()
        self.song_dropdown.currentIndexChanged.connect(self.load_selected_song)
        #playbutton
        self.play_pause_button = QPushButton("Play")

        #palybar
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.set_range(0, 0)


        self.position_label = QLabel("0:00 / 0:00")

        #control layout
        controls = QHBoxLayout()
        controls.add_widget(self.song_dropdown)
        controls.add_widget(self.play_pause_button)

        slider_row = QHBoxLayout()
        slider_row.add_widget(self.position_slider)
        slider_row.add_widget(self.position_label)

        layout = QVBoxLayout()
        layout.add_layout(controls)
        layout.add_layout(slider_row)
        #audio output
        self.audio_output = QAudioOutput()
        self.audio_output.volume = 0.5
        #media player for audio playback
        self.player = QMediaPlayer()
        self.player.audio_output = self.audio_output

        self.set_layout(layout)
        self.resize(800, 600)
 
        self.user_dragging = False
#buttons and signal connections
        self.play_pause_button.clicked.connect(self.toggle_play)

        self.player.positionChanged.connect(self.update_position)
        self.player.durationChanged.connect(self.update_duration)


        self.position_slider.sliderPressed.connect(self.slider_pressed)
        self.position_slider.sliderReleased.connect(self.slider_released)
   #adss song to playlist
    def add_song(self, file_path):
        self.song_list.append(file_path)
    #shows the file name in dropdown menu
        file_name = file_path.split("/")[-1]
        self.song_dropdown.add_item(file_name)
        #auto loads the first song thats added
        if self.song_dropdown.count == 1:
            self.set_media(file_path)
    #loads the song into the media player
    def set_media(self, file_path):
        self.player.source = QUrl.from_local_file(file_path)
        self.play_pause_button.text = "Play"
#loads chosen song
    @Slot(int)
    def load_selected_song(self, index):
        if index < 0 or index >= len(self.song_list):
            self.set_media(self.song_list[index])

#play and pause button
    @Slot()
    def toggle_play(self):
        try:
            playing = self.player.playback_state == QMediaPlayer.PlayingState
        except Exception:
            playing = False

        if playing:
            self.player.pause()
            self.play_pause_button.text = "Play"
        else:
            self.player.play()
            self.play_pause_button.text = "Pause"
#update slider
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
#converts miliseconds to seconds and minutes
    def update_time_label(self, pos_ms, dur_ms):
        def fmt(ms):
            if ms is None:
                return "0:00"
            s = int(ms / 1000)
            return f"{s // 60}:{s % 60:02d}"

        self.position_label.text = f"{fmt(pos_ms)} / {fmt(dur_ms)}"

#for tghte upload window

class Upload(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        #button to open files 
        self.open_button = QPushButton("Choose Audio FIle")
        self.status_label = QLabel("No file selected")

        layout = QVBoxLayout()
        layout.add_widget(self.open_button)
        layout.add_widget(self.status_label)
        self.set_layout(layout)

        self.open_button.clicked.connect(self.open_file)
#open files and sends teh file to main window 
    @Slot()
    def open_file(self):
        file_path, _ = QFileDialog.get_open_file_name( self, "Open Audio", "", "Audio Files (*.mp3, *.wav *.ogg)")
        
        if not file_path:
            return

        self.status_label.text = f"Selected: {file_path.split('/')[-1]}"
        self.main_window.add_song(file_path)

main = MyWindow()
main.show()
sys.exit(app.exec())
