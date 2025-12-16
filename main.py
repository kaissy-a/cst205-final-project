import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, 
    QHBoxLayout, QVBoxLayout, QSlider, QFileDialog, QComboBox, QLineEdit
)
from PySide6.QtCore import Slot, QUrl, Qt
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from __feature__ import snake_case, true_property
from PIL import Image
from visual_effects import createDynamicBackground
import requests
from apple_music_api import searched_songs


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
        manage_btn = QPushButton("Manage Playlists")
        vbox.add_widget(manage_btn)
        manage_btn.clicked.connect(self.open_playlist_manager)

        self.visual_effects_btn = QPushButton("Visual Effects Demo")
        vbox.add_widget(self.visual_effects_btn)
        self.visual_effects_btn.clicked.connect(self.open_visual_effects_demo)

    #opens visual effects demo
    @Slot()
    def open_visual_effects_demo(self):
        # example uses image already in file folder
        image = Image.open("album_cover.jpg")
        createDynamicBackground(image, sample=600, size=(400,400), blur=100, debug=True)

    
    #opens playlist manager
    @Slot()
    def open_playlist_manager(self):
        from music_player import MainWindow
        self.playlist_manager = MainWindow()
        self.playlist_manager.show()

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
        if index >= 0 and index < len(self.song_list):
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
        self.open_button = QPushButton("Choose Audio File")
        self.image_open_button = QPushButton("Choose Image File")
        self.status_label = QLabel("No audio file selected")
        self.image_status_label = QLabel("No image file selected")

        # connecting API
        self.search_button = QPushButton("Search Apple Music API")
        self.search_input = QLineEdit()
        self.search_input.setplaceholdertext = "Enter song..."
        layout = QVBoxLayout()
        self.open_button.clicked.connect(self.open_file)
        self.search_button.clicked.connect(self.search_apple_music_api)
        layout.add_widget(self.open_button)
        layout.add_widget(self.image_open_button)
        layout.add_widget(self.status_label)
        layout.add_widget(self.image_status_label)
        layout.add_widget(QLabel("OR "))
        layout.add_widget(self.search_input)
        layout.add_widget(self.search_button)
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
    @Slot()
    def open_image_file(self):
        file_path, _ = QFileDialog.get_open_file_name( self, "Open Image", "", "Image Files (*.png, *.jpg)")
        
        if not file_path:
            return

        self.image_status_label.text = f"Selected: {file_path.split('/')[-1]}"
        
    @Slot()
    def search_apple_music_api(self):
        search_text = self.search_input.text
        if len(search_text) == 0:
                    self.status_label.text = "Type a song!"
                    return


        songs = searched_songs(search_text, limit=3)

        if songs:
            result_text = f"Found {len(songs)} songs:"
            for song in songs:
                result_text = result_text + f"{song['artist']} - {song['title']}"

            self.status_label.text = result_text
        else:
            self.status_label.text = "Song not found."


main = MyWindow()
main.show()
sys.exit(app.exec())