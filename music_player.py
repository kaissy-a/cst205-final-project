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

