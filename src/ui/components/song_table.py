"""
Tabla de canciones con Material Design 3
"""

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal

class SongTable(QFrame):
    """Tabla de canciones Material Design 3"""
    
    # Señales
    song_selected = pyqtSignal(dict)  # Información de la canción seleccionada
    song_double_clicked = pyqtSignal(dict)  # Canción para reproducir
    
    # Columnas (Añadida columna para indicador de reproducción al inicio)
    COLUMNS = [
        "",  # Indicador de reproducción
        "Título",
        "Artista",
        "Álbum",
        "Género",
        "BPM"
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("tableContainer")
        
        self.current_page = 1
        self.items_per_page = 50
        self.total_items = 0
        self.currently_playing_row = -1 # Fila de la canción en reproducción
        
        self.init_ui()
        
    def init_ui(self):
        """Inicializar interfaz"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(0)
        
        # Tabla
        self.table = QTableWidget()
        self.table.setObjectName("dataTable")
        
        # Configurar columnas
        self.table.setColumnCount(len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels(self.COLUMNS)
        
        # Ajustar cabeceras
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed) # Indicador
        header.resizeSection(0, 24) # Ancho para el indicador
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Título
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Artista
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Álbum
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Género
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)  # BPM
        
        # Configurar selección
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        # Eventos
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        layout.addWidget(self.table)
        
    def clear(self):
        """Limpiar tabla"""
        self.table.setRowCount(0)
        self.total_items = 0
        self.currently_playing_row = -1 # Resetear indicador
        
    def load_songs(self, songs: list, total_items: int = None):
        """
        Cargar canciones en la tabla
        
        Args:
            songs: Lista de canciones
            total_items: Total de items disponibles (para paginación)
        """
        self.clear()
        
        if total_items is not None:
            self.total_items = total_items
            
        # Agregar filas
        for song in songs:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Crear items
            # Item vacío para el indicador de reproducción
            indicator_item = QTableWidgetItem("")
            indicator_item.setFlags(indicator_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)

            items = [
                indicator_item, # Celda para el indicador
                QTableWidgetItem(str(song.title)),
                QTableWidgetItem(str(song.artist)),
                QTableWidgetItem(str(song.album)),
                QTableWidgetItem(str(song.genre)),
                QTableWidgetItem(str(song.bpm or ""))
            ]
            
            # Configurar alineación
            items[5].setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter) # BPM (ahora en índice 5)
            
            # Guardar datos completos en el item de Título (índice 1)
            title_item = items[1]
            title_item.setData(Qt.ItemDataRole.UserRole, {
                'title': song.title,
                'artist': song.artist,
                'album': song.album,
                'genre': song.genre,
                'bpm': song.bpm,
                'file_path': str(song.file_path) # Asegurarse que song.file_path existe
            })
            
            # Agregar items a la fila
            for col, item in enumerate(items):
                self.table.setItem(row, col, item)
                
    def get_current_song(self) -> dict:
        """Obtener información de la canción seleccionada"""
        items = self.table.selectedItems()
        if not items:
            return None
            
        row = items[0].row()
        # Los datos de la canción están en el item de Título (columna 1)
        return self.table.item(row, 1).data(Qt.ItemDataRole.UserRole)
        
    def on_selection_changed(self):
        """Manejar cambio de selección"""
        song = self.get_current_song()
        if song:
            self.song_selected.emit(song)
            
    def on_item_double_clicked(self, item):
        """Manejar doble click en item"""
        # El item clickeado puede ser cualquiera de la fila.
        # Necesitamos obtener los datos de la canción de la columna de Título.
        song_data = self.table.item(item.row(), 1).data(Qt.ItemDataRole.UserRole)
        if song_data:
            self.song_double_clicked.emit(song_data)
            
    def set_currently_playing_song(self, song_data_to_play: dict):
        """
        Marcar la canción que se está reproduciendo actualmente en la tabla.
        
        Args:
            song_data_to_play: Diccionario con los datos de la canción (debe incluir 'file_path').
        """
        # Limpiar indicador anterior
        if self.currently_playing_row >= 0 and self.currently_playing_row < self.table.rowCount():
            self.table.item(self.currently_playing_row, 0).setText("")
            # Opcional: resetear el icono si usas QIcon
            # self.table.item(self.currently_playing_row, 0).setIcon(QIcon())

        self.currently_playing_row = -1

        if not song_data_to_play or 'file_path' not in song_data_to_play:
            return

        # Encontrar la fila de la canción
        for row in range(self.table.rowCount()):
            item_data = self.table.item(row, 1).data(Qt.ItemDataRole.UserRole)
            if item_data and item_data.get('file_path') == song_data_to_play.get('file_path'):
                self.table.item(row, 0).setText("▶️") # O usar un QIcon
                # self.table.item(row, 0).setIcon(QIcon(PLAYING_NOW_ICON_PATH))
                self.currently_playing_row = row
                break
                
    def clear_playing_indicator(self):
        """Limpiar el indicador de la canción en reproducción."""
        if self.currently_playing_row >= 0 and self.currently_playing_row < self.table.rowCount():
            self.table.item(self.currently_playing_row, 0).setText("")
            # self.table.item(self.currently_playing_row, 0).setIcon(QIcon())
        self.currently_playing_row = -1

    def get_pagination_info(self) -> tuple:
        """
        Obtener información de paginación
        
        Returns:
            tuple: (página actual, items por página, total de items)
        """
        return (self.current_page, self.items_per_page, self.total_items)
        
    def set_page(self, page: int):
        """Establecer página actual"""
        self.current_page = page
        
    def get_total_pages(self) -> int:
        """Obtener total de páginas"""
        return (self.total_items + self.items_per_page - 1) // self.items_per_page
