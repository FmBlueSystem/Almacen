"""
Vista de configuración con Material Design 3
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QLabel, QComboBox, QCheckBox
)
from PyQt6.QtCore import Qt, QSize

from src.views.base_view import BaseView
from ...config import UIConfig

class SettingsView(QWidget, BaseView):
    """Vista de configuración de la aplicación"""
    
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
        
        # Contenido con algunas opciones
        self.create_settings_content(layout)
        
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
        title = QLabel("Configuración")
        title.setObjectName("sectionTitle")
        header_layout.addWidget(title)
        
        layout.addWidget(header)
        
    def create_settings_content(self, layout):
        """Crear contenido de configuración"""
        container = QFrame()
        container.setObjectName("contentContainer")
        settings_layout = QVBoxLayout(container)
        settings_layout.setSpacing(24)
        
        # Sección de apariencia
        appearance = self.create_section("Apariencia", [
            {
                "label": "Tema",
                "widget": QComboBox,
                "options": ["Claro", "Oscuro", "Sistema"],
                "enabled": False
            },
            {
                "label": "Modo pantalla completa al inicio",
                "widget": QCheckBox,
                "enabled": True
            }
        ])
        settings_layout.addWidget(appearance)
        
        # Sección de reproducción
        playback = self.create_section("Reproducción", [
            {
                "label": "Fundido entre canciones",
                "widget": QCheckBox,
                "enabled": False
            },
            {
                "label": "Calidad de reproducción",
                "widget": QComboBox,
                "options": ["Alta", "Media", "Baja"],
                "enabled": False
            }
        ])
        settings_layout.addWidget(playback)
        
        # Sección de biblioteca
        library = self.create_section("Biblioteca", [
            {
                "label": "Carpeta de música",
                "widget": QLabel,
                "text": "No configurada",
                "enabled": False
            },
            {
                "label": "Buscar actualizaciones al inicio",
                "widget": QCheckBox,
                "enabled": False
            }
        ])
        settings_layout.addWidget(library)
        
        layout.addWidget(container)
        layout.addStretch()
        
    def create_section(self, title: str, items: list) -> QFrame:
        """
        Crear sección de configuración
        
        Args:
            title: Título de la sección
            items: Lista de items de configuración
            
        Returns:
            QFrame: Contenedor de la sección
        """
        section = QFrame()
        section.setObjectName("settingsSection")
        layout = QVBoxLayout(section)
        
        # Título de sección
        section_title = QLabel(title)
        section_title.setObjectName("settingsSectionTitle")
        layout.addWidget(section_title)
        
        # Items de configuración
        for item in items:
            item_frame = QFrame()
            item_layout = QHBoxLayout(item_frame)
            
            # Etiqueta
            label = QLabel(item["label"])
            label.setObjectName("settingsLabel")
            item_layout.addWidget(label)
            
            item_layout.addStretch()
            
            # Widget de control
            if item["widget"] == QComboBox:
                control = QComboBox()
                control.addItems(item["options"])
            elif item["widget"] == QCheckBox:
                control = QCheckBox()
            elif item["widget"] == QLabel:
                control = QLabel(item["text"])
                control.setObjectName("settingsValue")
            
            control.setEnabled(item["enabled"])
            item_layout.addWidget(control)
            
            layout.addWidget(item_frame)
            
        return section
        
    def on_scale_changed(self, scale_factor: float):
        """Manejar cambio de escala"""
        # Actualizar tamaños según escala
        margin = int(24 * scale_factor)
        spacing = int(16 * scale_factor)
        
        self.layout().setContentsMargins(margin, margin, margin, margin)
        self.layout().setSpacing(spacing)
        
        # Actualizar espaciado de secciones
        for section in self.findChildren(QFrame, "settingsSection"):
            section.layout().setSpacing(int(12 * scale_factor))
            
        # Actualizar tamaños de controles
        for combo in self.findChildren(QComboBox):
            height = int(32 * scale_factor)
            combo.setFixedHeight(height)
            
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
