"""
Navigation Rail con Material Design 3
"""

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, 
    QTreeWidget, QTreeWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal

class NavigationRail(QFrame):
    """Panel de navegación lateral Material Design 3"""
    
    navigation_changed = pyqtSignal(str, str)  # (section, item)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("navigationRail")
        self.init_ui()
        
    def init_ui(self):
        """Inicializar interfaz"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        self.create_header(layout)
        
        # Árbol de navegación
        self.create_navigation_tree(layout)
        
    def create_header(self, layout):
        """Crear header del panel"""
        header = QFrame()
        header.setObjectName("appHeader")
        header_layout = QVBoxLayout(header)
        
        # Título de la aplicación
        app_title = QLabel("Almacena")
        app_title.setObjectName("appTitle")
        header_layout.addWidget(app_title)
        
        layout.addWidget(header)
        
    def create_navigation_tree(self, layout):
        """Crear árbol de navegación"""
        self.nav_tree = QTreeWidget()
        self.nav_tree.setObjectName("navigationTree")
        self.nav_tree.setHeaderHidden(True)
        self.nav_tree.itemClicked.connect(self.on_item_clicked)
        
        layout.addWidget(self.nav_tree)
        
    def update_library_stats(self, stats: dict):
        """
        Actualizar estadísticas en el árbol de navegación
        
        Args:
            stats: Diccionario con estadísticas {
                'total_songs': int,
                'artists': list,
                'genres': list,
                'years': list
            }
        """
        self.nav_tree.clear()
        
        # Sección Biblioteca
        library = QTreeWidgetItem(self.nav_tree, ["Biblioteca"])
        library.setData(0, Qt.ItemDataRole.UserRole, "library")
        
        # Items de biblioteca con contadores
        items = [
            ("Todas las canciones", str(stats['total_songs'])),
            ("Artistas", str(len(stats['artists']))),
            ("Géneros", str(len(stats['genres']))),
            ("Años", str(len(stats['years'])))
        ]
        
        for text, count in items:
            item = QTreeWidgetItem(library, [f"{text} ({count})"])
            item.setData(0, Qt.ItemDataRole.UserRole, text.lower().replace(" ", "_"))
        
        # Sección Playlists
        playlists = QTreeWidgetItem(self.nav_tree, ["Playlists"])
        playlists.setData(0, Qt.ItemDataRole.UserRole, "playlists")
        
        playlist_items = [
            "Recientes",
            "Favoritos",
            "Más reproducidas"
        ]
        
        for text in playlist_items:
            item = QTreeWidgetItem(playlists, [text])
            item.setData(0, Qt.ItemDataRole.UserRole, text.lower().replace(" ", "_"))
        
        # Sección Configuración
        settings = QTreeWidgetItem(self.nav_tree, ["Configuración"])
        settings.setData(0, Qt.ItemDataRole.UserRole, "settings")
        
        self.nav_tree.expandAll()
        
    def on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Manejar click en item de navegación"""
        # Obtener sección padre
        parent = item.parent()
        if parent:
            section = parent.data(0, Qt.ItemDataRole.UserRole)
            item_id = item.data(0, Qt.ItemDataRole.UserRole)
        else:
            section = item.data(0, Qt.ItemDataRole.UserRole)
            item_id = "main"
            
        self.navigation_changed.emit(section, item_id)
