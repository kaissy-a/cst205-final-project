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
    









