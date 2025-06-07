"""
Placeholder para la vista de Playlists.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class PlaylistView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel("Vista de Playlists (Placeholder)")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        self.setObjectName("playlistView")

    def get_minimum_size(self):
        return self.sizeHint()

    def get_preferred_size(self):
        return self.sizeHint()

    def refresh(self):
        print(f"[{self.__class__.__name__}] Refresh solicitado.")

    def cleanup(self):
        print(f"[{self.__class__.__name__}] Cleanup solicitado.")

    def on_scale_changed(self, scale_factor: float):
        # En un futuro, ajustar tamaños de fuente, etc.
        print(f"[{self.__class__.__name__}] Scale changed: {scale_factor}")

    def on_theme_changed(self, is_dark: bool):
        # En un futuro, ajustar colores específicos del tema si es necesario
        print(f"[{self.__class__.__name__}] Theme changed: Dark={is_dark}")
