import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, 
    QHBoxLayout, QVBoxLayout, QSlider, QFileDialog, QComboBox, QLineEdit
)
from PySide6.QtCore import Slot, QUrl, Qt
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtGui import QPixmap
from __feature__ import snake_case, true_property
from PIL import Image
from PIL.ImageQt import ImageQt
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
#opens upload window
    @Slot()
    def open_up(self):
        self.upload = Upload(self)
        self.upload.show()
    #sends the selcted song path to the playlsit
    def add_song(self, file_path):
        if self.ply is None:
            self.ply = Playlist()

        self.ply.add_song(file_path)
        self.ply.show()
    def add_image(self,image):
        if self.ply is None:
            self.ply = Playlist()
        self.ply.add_image(image)
#playlist window 
class Playlist(QWidget):
    def __init__(self):
        super().__init__()
    #stores the files for songs
        self.song_list = []
    #image list
        self.image_list = []
#dropdown menu for the songs or any audio files
        self.song_dropdown = QComboBox()
        self.song_dropdown.currentIndexChanged.connect(self.load_selected_song)
        #playbutton
        self.play_pause_button = QPushButton("Play")
        self.image = QLabel()
        self.image.alignment = Qt.AlignCenter

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
        layout.add_widget(self.image)
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
    def add_image(self, image):
        self.image_list.append(image)
    #loads the song into the media player
    def set_media(self, file_path):
        self.player.source = QUrl.from_local_file(file_path)
        self.play_pause_button.text = "Play"
#loads chosen song
    @Slot(int)
    def load_selected_song(self, index):
        if index >= 0 and index < len(self.song_list):
            self.set_media(self.song_list[index])    
        #since image and song have same index, load image as well
        if index >= 0 and index < len(self.image_list):
            oldImage = Image.open(self.image_list[index])
            newImage = createDynamicBackground(oldImage, 1200, (400,400),120, False)
            qtImage = ImageQt(newImage)
            pixmap = QPixmap.from_image(qtImage)
            self.image.pixmap = pixmap

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
        self.current_songs = []
        self.window_title = "Search Music"

        #button to open files 
        self.open_button = QPushButton("Choose Audio File")
        self.image_open_button = QPushButton("Choose Image File")
        self.status_label = QLabel("No audio file selected")
        self.image_status_label = QLabel("No image file selected")

        # connecting API
        self.search_input = QLineEdit()
        self.search_input.setplaceholdertext = "Enter song or artitst name..."
        self.search_button = QPushButton("Search Apple Music API")

        # album cover displayed
        self.artwork_label = QLabel()
        self.artwork_label.set_fixed_size(400,600)
        self.artwork_label.text = "Album Artwork"

        # drop down of song list
        self.results_list = QComboBox()
        self.results_list.add_item("Select a song from search results...")

        # preview button to play song
        self.preview_button = QPushButton("Play Preview")
        self.preview_button.enabled = False

        layout = QVBoxLayout()
        layout.add_widget(self.open_button)
        layout.add_widget(self.status_label)

        layout.add_widget(self.image_open_button)
        layout.add_widget(self.image_status_label)

        self.set_layout(layout)
        layout.add_widget(QLabel("-- OR --"))
        layout.add_widget(self.search_input)
        layout.add_widget(self.search_button)

        # album cover display and song list dropdown
        layout.add_widget(self.artwork_label)
        layout.add_widget(self.results_list)


        self.open_button.clicked.connect(self.open_file)
        self.image_open_button.clicked.connect(self.open_image_file)
        self.search_button.clicked.connect(self.search_apple_music_api)
        self.preview_button.clicked.connect(self.toggle_playback)
        self.results_list.currentIndexChanged.connect(self.on_song_selected)

        self.preview_player = QMediaPlayer()
        self.preview_audio = QAudioOutput()
        layout.add_widget(self.preview_button)



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
        self.main_window.add_image(file_path)

    def preview(self, preview_url):
        if preview_url:
            self.preview_player.source = QUrl(preview_url)
            self.preview_button.enabled = True
            self.preview_button.text = "Play Preview"
        else:
            self.preview_button.enabled = False
    
    @Slot()
    def toggle_playback(self):
        """ Used to play/pause the preview audio"""
        try:
            playing = self.preview_player.playback_state == QMediaPlayer.PlayingState
        except Exception:
            playing = False

        if playing:
            self.player.pause()
            self.preview_button = "Play"
        else:
            self.player.play()
            self.preview_button = "Pause"
# all credits go to Andres, used his play and pause to set up preview player for apple music audio.
 # When user picks the song from dropdown menu
    def on_song_selected(self, index):
        if index > 0: 
            # We do this to convert from 1-based index to 0-based index
            song_index = index - 1
            if song_index >= 0 and song_index < len(self.current_songs):
                self.display_album_cover(index)

    def display_album_cover(self, song_index):
        if 0 <= song_index < len(self.current_songs):
            song = self.current_songs[song_index]
            
            # Grab the URL of the artwork
            picture_url = song['artwork_url']
            
            # Download
            response = requests.get(picture_url)
            
            # Check if download worked
            if response.status_code == 200:
                pixmap = QPixmap()
                loaded = pixmap.load_from_data(response.content)
                
                if loaded:
                    # Make it 100x100 pixels
                    pixmap = pixmap.scaled(100, 100)
                    
                    # Show it
                    self.artwork_label.pixmap = pixmap
                    
                    # Set up preview player
                    self.preview(song['preview_url'])
                else:
                    self.artwork_label.text = "Couldn't load image"
            else:
                self.artwork_label.text = "Couldn't download"
    def add_selected_playlist(self):
        index = self.results_list.current_index
        if 0 <= index < len(self.current_songs):
            song = self.current_songs[index]

            if 'preview_url' in song and song['preview_url']:
                self.main_window.add_song(song['preview_url'])
                self.status_label.text = f"Added to playlist: {song['artist']} - {song['title']}"


                    
            # Set up the preview player
            self.preview_player.source = QUrl.from_local_file(preview_url)
            song = self.current_songs[index]
            preview_url = song.get('preview_url')
            if preview_url:
                self.main_window.add_song(preview_url)
    @Slot()
    def search_apple_music_api(self):
        search_text = self.search_input.text
        if len(search_text) == 0:
                    self.status_label.text = "Type a song!"
                    return


        songs = searched_songs(search_text, limit=3)
        self.current_songs = songs
        if songs: 
            self.results_list.clear()
            self.results_list.add_item("Select a song from search...")
            result_text = f"Found {len(songs)} songs:"
            for song in songs:
                result_text = result_text + f"{song['artist']} - {song['title']}"
                self.results_list.add_item(result_text)

            self.status_label.text = f"found {len(songs)} songs. Select from dropdown."
        else:
            self.status_label.text = "Song(s) not found."


main = MyWindow()
main.show()
sys.exit(app.exec())