"""
Navigation Rail con Material Design 3
"""

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, 
    QTreeWidget, QTreeWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

class NavigationRail(QFrame):
    """Panel de navegación lateral Material Design 3"""
    
    navigation_changed = pyqtSignal(str, str)  # (section, item)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("navigationRail")
        self._initialized = False
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
        
    def update_library_stats(self, stats: dict, 
                               library_icon: QIcon = None, 
                               playlist_icon: QIcon = None, 
                               settings_icon: QIcon = None):
        """
        Actualizar estadísticas en el árbol de navegación y aplicar iconos a secciones principales.
        
        Args:
            stats: Diccionario con estadísticas {
                'total_songs': int,
                'artists': list,
                'genres': list,
                'years': list
            }
            library_icon: QIcon para la sección Biblioteca
            playlist_icon: QIcon para la sección Playlists
            settings_icon: QIcon para la sección Configuración
        """
        self.nav_tree.clear()
        
        # Sección Biblioteca
        library = QTreeWidgetItem(self.nav_tree, ["Biblioteca"])
        library.setData(0, Qt.ItemDataRole.UserRole, "library")
        if library_icon:
            library.setIcon(0, library_icon)
            print(f"[NavigationRail] Icono para Biblioteca: {library.icon(0)}, ¿es nulo? {library.icon(0).isNull()}")
        
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
        if playlist_icon:
            playlists.setIcon(0, playlist_icon)
            print(f"[NavigationRail] Icono para Playlists: {playlists.icon(0)}, ¿es nulo? {playlists.icon(0).isNull()}")
        
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
        if settings_icon:
            settings.setIcon(0, settings_icon)
            print(f"[NavigationRail] Icono para Configuración: {settings.icon(0)}, ¿es nulo? {settings.icon(0).isNull()}")
        
        self.nav_tree.expandAll()

        # Seleccionar "Biblioteca" por defecto solo la primera vez
        if self.nav_tree.topLevelItemCount() > 0:
            library_item_to_select = self.nav_tree.topLevelItem(0)
            if library_item_to_select:
                self.nav_tree.setCurrentItem(library_item_to_select)
                if not self._initialized:
                    # Emitir la señal inicial para que MainWindow configure la vista
                    section_key = library_item_to_select.data(0, Qt.ItemDataRole.UserRole)
                    # Para un ítem de nivel superior, el item_key puede ser el mismo que section_key
                    self.navigation_changed.emit(section_key, section_key)
                    self._initialized = True

    def on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Manejar click en item de navegación"""
        # Obtener sección padre
        parent = item.parent()
        if parent:
            section_key = parent.data(0, Qt.ItemDataRole.UserRole)
            item_key = item.data(0, Qt.ItemDataRole.UserRole)
        else:
            # Item de nivel superior (Biblioteca, Playlists, Configuración)
            section_key = item.data(0, Qt.ItemDataRole.UserRole)
            item_key = section_key # Usar la section_key también como item_key para consistencia
            
        self.navigation_changed.emit(section_key, item_key)
