"""
Vista de playlists con Material Design 3
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QLabel, QPushButton
)
from PyQt6.QtCore import Qt, QSize

from src.views.base_view import BaseView
from ...config import UIConfig

class PlaylistView(QWidget, BaseView):
    """Vista de playlists (en desarrollo)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Inicializar interfaz"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)
        
        # Header
        self.create_header(layout)
        
        # Contenido placeholder
        self.create_placeholder(layout)
        
    def get_minimum_size(self) -> QSize:
        """Obtener tamaño mínimo"""
        base_width, base_height = UIConfig.get_base_resolution()
        return QSize(base_width // 2, base_height // 2)
    
    def get_preferred_size(self) -> QSize:
        """Obtener tamaño preferido"""
        return QSize(*UIConfig.get_base_resolution())
        
    def create_header(self, layout):
        """Crear header de la vista"""
        header = QFrame()
        header.setObjectName("contentHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Título
        title = QLabel("Playlists")
        title.setObjectName("sectionTitle")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Botón de nueva playlist
        new_playlist = QPushButton("Nueva Playlist")
        new_playlist.setObjectName("primaryButton")
        new_playlist.setEnabled(False)  # Deshabilitado por ahora
        header_layout.addWidget(new_playlist)
        
        layout.addWidget(header)
        
    def create_placeholder(self, layout):
        """Crear contenido placeholder"""
        container = QFrame()
        container.setObjectName("contentContainer")
        
        placeholder_layout = QVBoxLayout(container)
        placeholder_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Icono placeholder
        icon = QLabel("🎵")
        icon.setObjectName("placeholderIcon")
        icon.setStyleSheet("""
            QLabel {
                font-size: 48px;
                margin-bottom: 16px;
            }
        """)
        placeholder_layout.addWidget(icon, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Mensaje
        message = QLabel("Funcionalidad de playlists en desarrollo")
        message.setObjectName("placeholderText")
        message.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #49454f;
            }
        """)
        placeholder_layout.addWidget(message, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(container)
        layout.addStretch()
        
    def on_scale_changed(self, scale_factor: float):
        """Manejar cambio de escala"""
        # Actualizar tamaños según escala
        margin = int(24 * scale_factor)
        spacing = int(16 * scale_factor)
        
        self.layout().setContentsMargins(margin, margin, margin, margin)
        self.layout().setSpacing(spacing)
        
        # Actualizar fuentes
        icon = self.findChild(QLabel, "placeholderIcon")
        if icon:
            font_size = int(48 * scale_factor)
            icon.setStyleSheet(f"""
                QLabel {{
                    font-size: {font_size}px;
                    margin-bottom: {spacing}px;
                }}
            """)
            
        message = self.findChild(QLabel, "placeholderText")
        if message:
            font_size = int(16 * scale_factor)
            message.setStyleSheet(f"""
                QLabel {{
                    font-size: {font_size}px;
                    color: #49454f;
                }}
            """)
        
    def on_theme_changed(self, is_dark: bool):
        """Manejar cambio de tema"""
        # La actualización del tema se maneja a nivel de estilos
        pass
        
    def refresh(self):
        """Actualizar vista"""
        self.update()
        
    def cleanup(self):
        """Limpiar recursos"""
        pass
