"""
Ventana principal con Material Design 3
"""

import logging
import time
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QStackedWidget, QMenuBar,
    QMenu, QStatusBar, QApplication, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, QSize, QEvent
from PyQt6.QtGui import QAction, QFontDatabase, QResizeEvent, QIcon

from ..styles.theme import MD3Theme
from ..styles.color_scheme import get_theme_colors
from ..config import UIConfig
from ..components.navigation_rail import NavigationRail
from ..components.playback_panel import PlaybackPanel
from ..components.content_views.library_view import LibraryView
from ..components.content_views.playlist_view import PlaylistView
from ..components.content_views.settings_view import SettingsView
from src.services.music_service import MusicService
from src.services.audio_service import AudioService
from src.database.connection import DatabaseConnection, DatabaseConnectionError, DatabaseTimeoutError
from src.views.base_view import BaseView
from src.utils.error_handler import LoadingCircuitBreaker, ErrorHandler



class MainWindow(QMainWindow):
    """Ventana principal de la aplicación"""
    
    def __init__(self, db_connection: DatabaseConnection, parent=None):
        super().__init__(parent)
        
        # Servicios
        self.db = db_connection # Usar la conexión inyectada
        self.music_service = MusicService(self.db)
        self.audio_service = AudioService(self)
        
        # Estado
        self.current_scale = 1.0
        self._force_exit = False  # Flag para control de salida
        self._is_initial_loading = False # Flag para la carga inicial
        self.current_search_filters = {'title': '', 'artist': '', 'genre': ''} # Inicializar filtros
        
        # Control de recursión y manejo de errores
        self._loading_circuit_breaker = LoadingCircuitBreaker(cooldown=2.0)
        self._logger = ErrorHandler.setup_logging(__name__)
        
        print("[MainWindow] Iniciando configuración...")
        self.init_ui()
        self.setup_theme()
        
        # Establecer tamaño inicial
        self.resize(1280, 720)
        self.show()
        
        print("[MainWindow] Configuración completada.")
        # Cargar datos de la biblioteca para poblar NavigationRail y mostrar vista inicial
        self._is_initial_loading = True
        self.load_library_data()
        self._is_initial_loading = False
        
    def init_ui(self):
        """Inicializar interfaz"""
        self.setWindowTitle("Almacena - Sistema de Gestión")
        
        # Establecer dimensiones base
        width, height = UIConfig.get_base_resolution()
        self.setMinimumSize(width // 2, height // 2)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Crear componentes principales
        self.create_menu_bar()
        self.setup_main_layout()
        self.create_status_bar()
        
    def setup_main_layout(self):
        """Configurar layout principal"""
        # Container principal
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Navigation Rail
        self.nav_rail = NavigationRail()
        self.nav_rail.navigation_changed.connect(self.on_navigation_changed)
        layout.addWidget(self.nav_rail)
        
        # Área de contenido
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Stack de contenido
        self.content_stack = QStackedWidget()
        
        # Vistas principales
        # Vista de biblioteca
        self.library_view = LibraryView(audio_service=self.audio_service)
        self.library_view.search_changed.connect(self.on_search_changed)
        self.library_view.song_selection_changed.connect(self.on_song_selection_changed)
        self.library_view.song_double_clicked.connect(self.on_song_double_clicked)
        self.library_view.page_changed_requested.connect(self.on_library_page_changed)
        self.content_stack.addWidget(self.library_view)
        
        self.playlist_view = PlaylistView()
        self.content_stack.addWidget(self.playlist_view)
        
        self.settings_view = SettingsView()
        self.content_stack.addWidget(self.settings_view)
        
        content_layout.addWidget(self.content_stack)
        
        # Panel de reproducción
        self.playback_panel = PlaybackPanel()
        self.connect_playback_panel_signals()
        content_layout.addWidget(self.playback_panel)
        
        # Ajustar el estiramiento del layout para que el panel de reproducción tenga un tamaño fijo
        # y el contenido se estire.
        content_layout.setStretch(0, 1)  # content_stack se estira
        content_layout.setStretch(1, 0)  # playback_panel no se estira (tamaño fijo)
        
        layout.addWidget(content_area)
        
        # Splitter para redimensionamiento
        layout.setStretch(0, 1)  # Navigation rail
        layout.setStretch(1, 4)  # Contenido
        
        # Agregar al layout central
        self.centralWidget().layout().addWidget(container)
        
    def connect_playback_panel_signals(self):
        """Conectar señales entre AudioService y PlaybackPanel."""
        if not self.audio_service or not self.playback_panel:
            print("[MainWindow] Error: AudioService o PlaybackPanel no inicializados para conectar señales.")
            return

        # Conectar acciones de PlaybackPanel a AudioService
        # Conectar controles básicos
        self.playback_panel.play_requested.connect(self.audio_service.resume)
        self.playback_panel.pause_requested.connect(self.audio_service.pause)
        self.playback_panel.seek_requested.connect(self.audio_service.seek)
        self.playback_panel.volume_change_requested.connect(self.audio_service.set_volume)
        
        # Conectar controles de navegación
        self.playback_panel.previous_requested.connect(self.audio_service.play_previous)
        self.playback_panel.next_requested.connect(self.audio_service.play_next)

        # Conectar señales de AudioService a slots de PlaybackPanel
        # Conectar señales de estado
        self.audio_service.playback_state_changed.connect(self.playback_panel.update_playback_state)
        self.audio_service.song_progress_updated.connect(self.playback_panel.update_progress)
        self.audio_service.current_song_changed.connect(self.playback_panel.update_current_song)
        
        # Conectar señales de navegación
        self.audio_service.previous_available.connect(self.playback_panel.prev_button.setEnabled)
        self.audio_service.next_available.connect(self.playback_panel.next_button.setEnabled)
        
        # Conectar error de audio a la status bar
        self.audio_service.error_occurred.connect(self.show_audio_error)
        
    def create_menu_bar(self):
        """Crear barra de menú"""
        menubar = self.menuBar()
        
        # Menú Archivo
        file_menu = menubar.addMenu("&Archivo")
        
        import_menu = file_menu.addMenu("&Importar")
        
        folder_action = QAction("&Carpeta", self)
        folder_action.setShortcut("Ctrl+Shift+O")
        folder_action.triggered.connect(self.import_folder)
        import_menu.addAction(folder_action)
        
        files_action = QAction("&Archivos", self)
        files_action.setShortcut("Ctrl+O")
        files_action.triggered.connect(self.import_files)
        import_menu.addAction(files_action)
        
        file_menu.addSeparator()
        
        self.exit_action = QAction("&Salir", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(self._handle_exit)
        file_menu.addAction(self.exit_action)
        
        # Menú Ver
        view_menu = menubar.addMenu("&Ver")
        
        theme_menu = view_menu.addMenu("&Tema")
        
        light_action = QAction("&Claro", self)
        light_action.setCheckable(True)
        light_action.setChecked(not UIConfig.is_dark_theme())
        light_action.toggled.connect(self.on_theme_changed)
        theme_menu.addAction(light_action)
        
        dark_action = QAction("&Oscuro", self)
        dark_action.setCheckable(True)
        dark_action.setChecked(UIConfig.is_dark_theme())
        theme_menu.addAction(dark_action)
        
        # Menú Ayuda
        help_menu = menubar.addMenu("&Ayuda")
        
        about_action = QAction("&Acerca de", self)
        help_menu.addAction(about_action)
        
    def create_status_bar(self):
        """Crear barra de estado"""
        status_bar = QStatusBar()
        status_bar.showMessage("Listo")
        self.setStatusBar(status_bar)
        
    def setup_theme(self):
        """Configurar tema Material Design 3"""
        is_dark = UIConfig.is_dark_theme()
        colors = get_theme_colors(is_dark)
        self.setStyleSheet(MD3Theme.get_stylesheet(colors=colors, is_dark=is_dark))
        
        # Cargar fuente
        font_path = UIConfig.FONT_PATH
        font_family_to_set = UIConfig.FONT_FAMILY # Fuente por defecto
        
        if font_path.exists():
            font_id = QFontDatabase.addApplicationFont(str(font_path))
            if font_id != -1:
                # La fuente se cargó correctamente
                loaded_font_families = QFontDatabase.applicationFontFamilies(font_id)
                if loaded_font_families:
                    font_family_to_set = loaded_font_families[0]
                    print(f"[MainWindow] Fuente '{font_family_to_set}' cargada desde: {font_path}")
                else:
                    print(f"[MainWindow] Error: QFontDatabase.applicationFontFamilies devolvió una lista vacía para font_id {font_id} desde {font_path}")
            else:
                # Error al cargar la fuente
                print(f"[MainWindow] Error: No se pudo cargar la fuente desde: {font_path}. Se usará la fuente por defecto '{UIConfig.FONT_FAMILY}'.")
        else:
            print(f"[MainWindow] Archivo de fuente no encontrado en: {font_path}. Se usará la fuente por defecto '{UIConfig.FONT_FAMILY}'.")
            
        # Aplicar fuente a la aplicación
        app = QApplication.instance()
        if app:
            current_font = app.font()
            current_font.setFamily(font_family_to_set)
            app.setFont(current_font)
    
    def update_library_filters_and_songs(self):
        """Actualiza los desplegables de filtros y recarga las canciones en LibraryView
           respetando los filtros y página actuales."""
        try:
            print("[MainWindow] Actualizando filtros de la biblioteca...")
            artists = self.music_service.get_distinct_artists()
            genres = self.music_service.get_distinct_genres()
            total_songs_global = self.music_service.get_total_songs_count()
            
            stats = {
                'total_songs': total_songs_global, 
                'artists': artists,
                'genres': genres,
                'years': [] 
            }
            self.library_view.update_filters(stats)

            # Actualizar NavigationRail con iconos
            if hasattr(self.nav_rail, 'update_library_stats'):
                library_icon = QApplication.style().standardIcon(QApplication.style().StandardPixmap.SP_ComputerIcon)
                playlist_icon = QApplication.style().standardIcon(QApplication.style().StandardPixmap.SP_DriveDVDIcon)
                settings_icon = QApplication.style().standardIcon(QApplication.style().StandardPixmap.SP_FileDialogDetailedView)
                self.nav_rail.update_library_stats(stats, library_icon, playlist_icon, settings_icon)

            # Recargar las canciones usando los filtros actuales y la página actual de LibraryView
            self._logger.info(f"Recargando canciones para la página: {self.library_view.current_page} con filtros: {self.current_search_filters}")
            self.load_songs_for_library_view(page=self.library_view.current_page)
            
        except (DatabaseConnectionError, DatabaseTimeoutError) as e:
            # Manejo específico de errores de base de datos - NO usar QMessageBox modal
            error_msg = ErrorHandler.handle_db_error(self._logger, e, "updating library filters")
            self.statusBar().showMessage(error_msg, 5000)
            
        except Exception as e:
            # Manejo de errores generales - NO usar QMessageBox modal
            error_msg = ErrorHandler.handle_general_error(self._logger, e, "updating library filters")
            self.statusBar().showMessage(error_msg, 5000)

    def load_library_data(self):
        """Cargar datos iniciales de la biblioteca (filtros y primera página)."""
        try:
            self._logger.info("Cargando datos iniciales de la biblioteca (filtros y primera página)...")
            # update_library_filters_and_songs se encargará de:
            # 1. Poblar los desplegables de filtro (artistas, géneros).
            # 2. Llamar a load_songs_for_library_view con la página actual de LibraryView (que será 1 por defecto)
            #    y los filtros actuales (que estarán vacíos por defecto en self.current_search_filters).
            self.update_library_filters_and_songs()
            
        except Exception as e:
            error_msg = ErrorHandler.handle_general_error(self._logger, e, "loading initial library data")
            self.statusBar().showMessage(error_msg, 5000)
    
    def reset_loading_errors(self):
        """Resetear el estado de errores para permitir nuevos intentos de carga"""
        self._loading_circuit_breaker.reset_error_state()
        self._logger.info("Circuit breaker error state reset")
        self.statusBar().showMessage("Estado de errores reiniciado. Puede intentar cargar datos nuevamente.", 3000)
            
    def on_navigation_changed(self, section_key: str, item_key: str):
        """Cambiar vista según la navegación. Usa item_key para la lógica."""
        # Limpiar recursos de la vista actual si es una BaseView
        current_view_widget = self.content_stack.currentWidget()
        if isinstance(current_view_widget, BaseView):
            print(f"[MainWindow] Limpiando vista actual: {current_view_widget.__class__.__name__}")
            current_view_widget.cleanup()

        # Determinar la vista a mostrar basándose en section_key o item_key
        # El NavigationRail emite el 'section_key' como la categoría principal (ej. 'library')
        # y 'item_key' como el subítem (ej. 'all_songs') o el mismo que section_key si es un ítem de nivel superior.

        target_widget = None
        status_message = f"Vista: {item_key}"

        if section_key == "library": 
            target_widget = self.library_view
            if not self._is_initial_loading: # Solo cargar si no es la carga inicial
                self.load_library_data()
            status_message = self.tr("Biblioteca")
        elif section_key == "playlists": 
            target_widget = self.playlist_view
            status_message = self.tr("Playlists")
        elif section_key == "settings": # O item_key si es un clic directo en "Configuración"
            target_widget = self.settings_view
            status_message = self.tr("Configuración")
        else:
            print(f"[MainWindow] Sección/item de navegación desconocido: section_key={section_key}, item_key={item_key}")
            # Podríamos querer mostrar una vista por defecto o no hacer nada
            # Por ahora, si no se reconoce, no cambiamos de vista y dejamos un mensaje.
            self.statusBar().showMessage(f"Navegación no reconocida: {item_key}")
            return # Salir si no se reconoce

        if target_widget:
            self.content_stack.setCurrentWidget(target_widget)
            # Refrescar la nueva vista actual si es una BaseView
            if isinstance(target_widget, BaseView):
                print(f"[MainWindow] Refrescando nueva vista: {target_widget.__class__.__name__}")
                target_widget.refresh()
            
            self.update_component_sizes() # Asegurar que los tamaños se recalculan
            self.statusBar().showMessage(status_message)
        else:
            print(f"[MainWindow] No se encontró un widget para section_key={section_key}, item_key={item_key}")

    def on_search_changed(self, title: str, artist: str, genre: str):
        """Manejar cambio en filtros de búsqueda, cargar página 1 de resultados."""
        # La LibraryView ya resetea su current_page a 1 al emitir search_changed
        self.current_search_filters = {'title': title, 'artist': artist, 'genre': genre}
        self.load_songs_for_library_view(page=1) # Cargar página 1 con los nuevos filtros
            
    def on_library_page_changed(self, page: int):
        """Manejar solicitud de cambio de página desde LibraryView."""
        self.load_songs_for_library_view(page=page)

    def load_songs_for_library_view(self, page: int):
        """Carga canciones en LibraryView para una página específica."""
        # Implements Dart AI Task: Refactor long load method

        if not self._loading_circuit_breaker.start_loading():
            self._logger.warning(f"Load request for page {page} blocked by circuit breaker")
            return

        try:
            title = self.current_search_filters.get('title', "")
            artist = self.current_search_filters.get('artist', "")
            genre = self.current_search_filters.get('genre', "")
            per_page = self.library_view.items_per_page

            songs, total_items = self._fetch_songs(page, title, artist, genre, per_page)
            self._update_library_view(songs, total_items, page)
            self._loading_circuit_breaker.finish_loading(success=True)

        except (DatabaseConnectionError, DatabaseTimeoutError) as e:
            self._loading_circuit_breaker.finish_loading(success=False)
            self._handle_db_error(e, page)

        except Exception as e:
            self._loading_circuit_breaker.finish_loading(success=False)
            self._handle_general_error(e, page)

    def _fetch_songs(self, page: int, title: str, artist: str, genre: str, per_page: int):
        """Obtener canciones aplicando filtros"""
        if title or artist or genre:
            return self.music_service.search_songs(title, artist, genre, page, per_page)
        songs, _ = self.music_service.get_songs(page, per_page)
        total = self.music_service.get_total_songs_count()
        return songs, total

    def _update_library_view(self, songs: list, total_items: int, page: int):
        """Actualizar vista de biblioteca con los datos cargados"""
        self.library_view.load_songs(songs, total_items)
        self.statusBar().showMessage(
            f"Mostrando página {page}. {len(songs)} canciones (de {total_items} encontradas)."
        )

    def _handle_db_error(self, error: Exception, page: int):
        """Mostrar mensajes de error de base de datos"""
        error_msg = ErrorHandler.handle_db_error(self._logger, error, f"loading page {page}")
        self.statusBar().showMessage(error_msg, 5000)

    def _handle_general_error(self, error: Exception, page: int):
        """Mostrar mensajes de error genéricos"""
        error_msg = ErrorHandler.handle_loading_error(self._logger, error, page)
        self.statusBar().showMessage(error_msg, 5000)

    def on_song_selection_changed(self, selected_songs: list[dict], selected_index: int):
        """
        Manejar cambio en la selección de canciones.
        Actualiza la lista de reproducción con las canciones disponibles.
        """
        if not selected_songs:
            return
            
        self.audio_service.set_playlist(selected_songs, selected_index)
        
    def on_song_double_clicked(self, song_data: dict):
        """
        Manejar doble clic en una canción.
        Reproduce la canción seleccionada.
        """
        if song_data:
            self.audio_service.play_song(song_data)
        
    def on_theme_changed(self, use_light: bool):
        """Cambiar tema de la aplicación"""
        UIConfig.set_dark_theme(not use_light)
        self.setup_theme()
        # Actualizar componentes
        self.nav_rail.update_theme()
        self.library_view.update_theme()
        self.playlist_view.update_theme()
        self.settings_view.update_theme()
        self.playback_panel.update_theme()
        
    def import_folder(self):
        """Importar carpeta de música"""
        folder_path = QFileDialog.getExistingDirectory(self, self.tr("Seleccionar Carpeta de Música"), "")
        if folder_path:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            try:
                imported, failed = self.music_service.import_folder(folder_path)
                self.statusBar().showMessage(self.tr(f"{imported} canciones importadas, {failed} fallaron."), 5000)
                self.update_library_filters_and_songs()
            except FileNotFoundError as e:
                QMessageBox.warning(self, self.tr("Error"), str(e))
                self.statusBar().showMessage(self.tr(f"Error al importar: {e}"), 5000)
            except Exception as e:
                QMessageBox.critical(self, self.tr("Error"), self.tr(f"Ocurrió un error inesperado: {e}"))
                self.statusBar().showMessage(self.tr(f"Error inesperado al importar: {e}"), 5000)
            finally:
                QApplication.restoreOverrideCursor()
        
    def import_files(self):
        """Importar archivos de música"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            self.tr("Seleccionar Archivos de Música"),
            "",
            self.tr("Archivos de Audio (*.mp3 *.wav *.m4a *.flac);;Todos los archivos (*.*)")
        )
        
        if file_paths:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            try:
                imported, failed = self.music_service.import_files(file_paths)
                
                self.statusBar().showMessage(
                    self.tr(f"{imported} archivos importados, {failed} fallaron."),
                    5000
                )
                
                self.update_library_filters_and_songs()
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    self.tr("Error"),
                    self.tr(f"Error importando archivos: {e}")
                )
                self.statusBar().showMessage(self.tr(f"Error en importación: {e}"), 5000)
            finally:
                QApplication.restoreOverrideCursor()
        
    def resizeEvent(self, event: QResizeEvent):
        """Manejar cambio de tamaño de la ventana"""
        super().resizeEvent(event)
        
        # Calcular nueva escala
        width = event.size().width()
        height = event.size().height()
        self.current_scale = UIConfig.get_scale_factor(width, height)
        
        # Actualizar tamaños de componentes
        self.update_component_sizes()
        
    def update_component_sizes(self):
        """Actualizar tamaños de componentes según escala"""
        # Navigation rail
        nav_width = UIConfig.scale_size(280, self.width(), self.height())
        self.nav_rail.setFixedWidth(nav_width)
        
        # Ajustes de tamaño para otros componentes
        self.playback_panel.setFixedHeight(UIConfig.scale_size(100, self.width(), self.height()))
        
        # Ajustar tamaños de texto
        font_size = UIConfig.scale_size(12, self.width(), self.height())
        app = QApplication.instance()
        if app:
            current_font = app.font()
            current_font.setPointSize(font_size)
            app.setFont(current_font)

    def show_audio_error(self, error_message: str):
        """Muestra un mensaje de error de audio en la barra de estado."""
        self.statusBar().showMessage(f"Error de audio: {error_message}", 7000)

    def _handle_exit(self):
        """Manejador para la acción de salir del menú"""
        print("[MainWindow] Saliendo por acción del menú...")
        self._force_exit = True  # Marcar que es una salida intencional
        self.close()  # Esto disparará el closeEvent
        
    def closeEvent(self, event):
        """Manejar evento de cierre para limpiar servicios."""
        print("[MainWindow] closeEvent recibido")
        print("[MainWindow] Es cierre forzado:", self._force_exit)
        
        if not self._force_exit:
            # Si no es un cierre forzado, mostrar diálogo de confirmación
            reply = QMessageBox.question(
                self,
                "Confirmar salida",
                "¿Está seguro que desea salir de la aplicación?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                print("[MainWindow] Cancelando cierre por usuario...")
                event.ignore()
                self._force_exit = False
                return
            else:
                print("[MainWindow] Usuario confirmó el cierre")
                self._force_exit = True
                
        # Proceder con el cierre solo si está marcado como forzado
        if self._force_exit:
            print("[MainWindow] Cerrando aplicación...")
            if hasattr(self, 'audio_service') and self.audio_service:
                self.audio_service.cleanup()
            event.accept()
        else:
            print("[MainWindow] Ignorando cierre no autorizado")
            event.ignore()
