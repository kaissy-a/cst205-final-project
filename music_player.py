"""
Person 4 deliverable: Give the user the ability to create playlists and add image filters (negative, chroma key) to playlist covers using lists, dictionaries, and PIL/Pillow.
Notes:
- Apple Music integration is owned by Person 2; here we only manage local metadata.
- Data is persisted to playlists.json in the working directory.
- Images processed with Pillow; chroma key makes a selected color transparent.
"""
from __future__ import annotations
import json
import os
import sys
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional, Tuple

from PIL import Image, ImageOps

from PySide6.QtCore import Qt, QSize
from PySide.QtGui import QAction, AIcon, QColor
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QHBoxLayout,
    QVBoxLayout,
    QFormLayout,
    QMessageBox,
    QSpinBox,
    QColorDialog,
    QComboBox,
    QTextEdit,
    QSplitter,
    QGroupBox,
)

DATA_FILE = "playlists.json"
OUTPUT_DIR = "processed_covers"
SUPPORTED_EXTS = {".png", ".jpg", ".jpeg"}

#datamodels
@dataclass
class Track:
    title: str
    artist: str
    preview_url: str = ""

@dataclass
class Playlist:
    name: str
    description: str = ""
    cover_image_path: str = ""
    processed_image_path: str = ""
    tracks: List[Track] = field(default_factory=list)

@dataclass
class AppState:
    playlists: List[Playlist] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {"playlists": [asdict(p) for p in self.playlists]}

@staticmethod
def from_dict(d: Dict) -> "AppState":
    pls: List[Playlist] = []
    for p in d.get("playlists", []):
        tracks = [Track(**t) for t in p.get("tracks", [])]
        pls.append(Playlist(
            name=p.get("name, "Untitled"),
            description=p.get("description", ""),
            cover_image_path=p.get("cover_image_path", ""),
            processed_image_path=p.get("processed_image_path", ""),
            tracks=tracks,
        ))
    return AppState(playlists=pls)

#Persistencehelpers

def load_state() -> AppState:
    if not os.path.exists(DATA_FILE):
        return AppState()
    with open(DATA_FILE, "r", encoding="utf-8) as f:
        data = json.load(f)
    return AppState.from_dict(data)

def save_state(state: AppState) -> None:
    with open(DATA_FILE, "W", encoding="utf-8) as f:
        json.dump(state.to_dict(), f, indent=2)

#ImageFiltering(Pillow)

def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def negative_filter(img: Image.Image) -> Image.Image:
        if img.mode in ("RGBA", "LA"):
            rgb = img.convert("RGB")
            inv = ImageOps.invert(rgb).convert("RGBA")
            inv.putalpha(img.split()[-1])
            return inv
        return ImageOps.invert(img.convert("RGB"))
        

def chroma_key_filter(img: Image.Image, key_rgb: Tuple[int, int, int], threshold: int = 40) -> Image.Image:


"""
Makes pixels similar to key_rgb transparent.
threshold: 0-255 — higher removes a broader range.
"""
img = img.convert("RGBA")
r, g, b, a = img.split()
src = img.load()
w, h = img.size
key_r, key_g, key_b = key_rgb
out = Image.new("RGBA", (w, h))
dst = out.load()

for y in range(h):
    for x in range(w):
        pr, pg, pb, pa = src[x, y]
        dist = abs(pr - key_r) + abs(pg - key_g) + abs(pb - key_b)
        if dist <= threshold:
            # Make transparent
            dst[x, y] = (pr, pg, pb, 0)
        else:
            dst[x, y] = (pr, pg, pb, pa)
    return out
        
def save_processed(img: Image.Image, base_name: str) -> str:
    ensure_output_dir()
    out_path = os.path.join(OUTPUT_DIR, f"{base_name}.png")
    img.save(out_path, "PNG")
    return out_path

# UI
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Playlist Creator — Person 4")
        self.setMinimumSize(1000, 600)

        self.state = load_state()
        self.current_index: Optional[int] = None
        self.current_chroma_color: Tuple[int, int, int] = (0, 255, 0)

        self._build_ui()
        self._populate_list()

    #UIConstruction
    def _build_ui(self):
        splitter = QSplitter()

        #Left
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        self.playlist_list = QListWidget()
        self.playlist_list.currentRowChanged.connect(self._on_select_playlist)

        btn_new = QPushButton("New Playlist")
        btn_new.clicked.connect(self._new_playlist)
        btn_delete = QPushButton("Delete Playlist")
        btn_delete.clicked.connect(self._delete_playlist)

        left_layout.addWidget(self.playlist_list)
        left_layout.addWidget(btn_new)
        left_layout.addWidget(btn_delete)

        #Right
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        #MetaBox
        meta_group = QGroupBox("Playlist Details")
        form = QFormLayout(meta_group)
        self.name_edit = QLineEdit()
        self.desc_edit = QTextEdit()
        self.desc_edit.setFixedHeight(80)
        form.addRow("Name", self.name_edit)
        form.addRow("Description", self.desc_edit)

        save_meta_btn = QPushButton("Save Details")
        save_meta_btn.clicked.connect(self._save_meta)

        #CoverControls
        cover_group = QGroupBox("Cover Image & Filters")
        cover_layout = QVBoxLayout(cover_group)
        self.cover_label = QLabel("No cover image selected")
        self.cover_label.setFixedHeight(220)
        self.cover_label.setAlignment(Qt.AlignCenter)
        self.cover_label.setStyleSheet("border: 1px solid #ccc;")

        btn_choose_cover = QPushButton("Choose Cover Image...")
        btn_choose_cover.clicked.connect(self._choose_cover)

        #FilterControls
        filter_row = QHBoxLayout()
        self.filter_selector = QComboBox()
        self.filter_selector.addItems(["None", "Negative", "Chroma Key"])

        self.threshold_spin = QSpinBox()
        self.threshold_spin.setRange(0, 255)
        self.threshold_spin.setValue(40)
        self.threshold_spin.setPrefix("Threshold: ")

        btn_pick_color = QPushButton("Pick Chroma Color…")
        btn_pick_color.clicked.connect(self._pick_chroma_color)

        btn_apply_filter = QPushButton("Apply Filter")
        btn_apply_filter.clicked.connect(self._apply_filter)

        filter_row.addWidget(self.filter_selector)
        filter_row.addWidget(self.threshold_spin)
        filter_row.addWidget(btn_pick_color)
        filter_row.addWidget(btn_apply_filter)
        
        cover_layout.addWidget(self.cover_label)
        cover_layout.addWidget(btn_choose_cover)
        cover_layout.addLayout(filter_row)

        #Tracks box
        tracks_group = QGroupBox("Tracks (local metada)")
        tracks_layout = QVBoxLayout(tracks_group)
        self.tracks_list = QListWidget()
        track_form = QHBoxLayout()
        self.track_title = QLineEdit(); self.track_title.setPlaceholderText("Title")
        self.track_artist = QLineEdit(); self.track_artist.setPlaceholderText("Artist")
        self.track_preview = QLineEdit(); self.track_preview.setPlaceholderText("Preview URL (from API)")
        btn_add_track = QPushButton("Add Track")
        btn_add_track.clicked.connect(self._add_track)
        btn_remove_track = QPushButton("Remove Selected")
        btn_remove_track.clicked.connect(self._remove_track)

        track_form.addWidget(self.track_title)
        track_form.addWidget(self.track_artist)
        track_form.addWidget(self.track_preview)
        track_form.addWidget(btn_add_track)
        track_form.addWidget(btn_remove_track)

        tracks_layout.addWidget(self.tracks_list)
        tracks_layout.addLayout(track_form)
        
        
        right_layout.addWidget(meta_group)
        right_layout.addWidget(save_meta_btn)
        right_layout.addWidget(cover_group)
        right_layout.addWidget(tracks_group)
        
        
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(1, 2)
        self.setCentralWidget(splitter)

        #Menu
        save_action = QAction("Save All", self)
        save_action.triggered.connect(self._save_all)
        self.menuBar().addAction(save_action)

        #StateHelpers
        def _populate_list(self):
            self.playlist_list.clear()
            for p in self.state.playlists:
                item = QListWidgetItem(p.name)
                self.playlist_list.addItem(item)
            if self.state.playlists:
                self.playlist_list.setCurrentRow(0)

        def _refresh_details(self):
            idx = self.current_index
            if idx is None or idx < 0 or idx >= len(self.state.playlists):
                self.name_edit.setText("")
                self.desc_edit.setPlainText("")
                self.cover_label.setText("No cover image selected")
                self.cover_label.setPixmap(None)
                self.tracks_list.clear()
                return
            p = self.state.playlists[idx]
            self.name_edit.setText(p.name)
            self.desc_edit.setPlainText(p.description)
            self._update_cover_label(p.processed_image_path or p.cover_image_path)
            self._refresh_tracks(p)

        def _refresh_tracks(self, p: Playlist):
            self.tracks_list.clear()
            for t in p.tracks:
                self.tracks_list.addItem(f"{t.title} — {t.artist}")


        def _update_cover_label(self, path: str):
            if not path or not os.path.exists(path):
                self.cover_label.setText("No cover image selected")
                self.cover_label.setPixmap(None)
                return
            from PySide6.QtGui import QPixmap
            pix = QPixmap(path)
            if not pix.isNull():
                scaled = pix.scaled(self.cover_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.cover_label.setPixmap(scaled)

        #Slots
        

        
        

        
        
        
        
        
        

        
        




















