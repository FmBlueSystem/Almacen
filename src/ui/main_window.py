"""
Ventana principal de la aplicación con Material Design 3
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QFrame, QMenuBar, QStatusBar,
    QToolBar, QSplitter, QTreeWidget, QTextEdit
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon, QPalette, QColor, QFont

class MainWindow(QMainWindow):
    """Ventana principal con Material Design 3"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_material_theme()
        
    def init_ui(self):
        """Inicializar interfaz de usuario"""
        self.setWindowTitle("Almacena - Sistema de Gestión")
        self.setGeometry(100, 100, 1200, 800)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Crear componentes
        self.create_menu_bar()
        self.create_toolbar()
        self.create_content_area()
        self.create_status_bar()
        
    def create_menu_bar(self):
        """Crear barra de menú"""
        menubar = self.menuBar()
        
        # Menú Archivo
        file_menu = menubar.addMenu("&Archivo")
        
        new_action = QAction("&Nuevo", self)
        new_action.setShortcut("Ctrl+N")
        file_menu.addAction(new_action)
        
        open_action = QAction("&Abrir", self)
        open_action.setShortcut("Ctrl+O")
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("&Salir", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menú Ver
        view_menu = menubar.addMenu("&Ver")
        
        toggle_sidebar_action = QAction("&Barra lateral", self)
        toggle_sidebar_action.setCheckable(True)
        toggle_sidebar_action.setChecked(True)
        view_menu.addAction(toggle_sidebar_action)
        
        # Menú Ayuda
        help_menu = menubar.addMenu("&Ayuda")
        
        about_action = QAction("&Acerca de", self)
        help_menu.addAction(about_action)
        
    def create_toolbar(self):
        """Crear barra de herramientas"""
        toolbar = QToolBar("Principal")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.addToolBar(toolbar)
        
        # Botones de acción
        nuevo_btn = QPushButton("Nuevo")
        nuevo_btn.setObjectName("toolbarButton")
        toolbar.addWidget(nuevo_btn)
        
        toolbar.addSeparator()
        
        guardar_btn = QPushButton("Guardar")
        guardar_btn.setObjectName("toolbarButton")
        toolbar.addWidget(guardar_btn)
        
        toolbar.addSeparator()
        
        buscar_btn = QPushButton("Buscar")
        buscar_btn.setObjectName("toolbarButton")
        toolbar.addWidget(buscar_btn)
        
    def create_content_area(self):
        """Crear área de contenido principal"""
        # Splitter horizontal
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Panel lateral izquierdo
        sidebar = self.create_sidebar()
        splitter.addWidget(sidebar)
        
        # Área de contenido principal
        content_area = self.create_main_content()
        splitter.addWidget(content_area)
        
        # Configurar proporciones
        splitter.setSizes([300, 900])
        
        # Agregar al layout central
        self.centralWidget().layout().addWidget(splitter)
        
    def create_sidebar(self):
        """Crear panel lateral"""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFrameStyle(QFrame.Shape.StyledPanel)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Título
        title = QLabel("Navegación")
        title.setObjectName("sidebarTitle")
        layout.addWidget(title)
        
        # Árbol de navegación
        tree = QTreeWidget()
        tree.setObjectName("navigationTree")
        tree.setHeaderHidden(True)
        
        # Agregar elementos de ejemplo
        root_items = [
            "Dashboard",
            "Elementos",
            "Categorías",
            "Reportes",
            "Configuración"
        ]
        
        for item_text in root_items:
            tree.addTopLevelItem(tree.itemFromIndex(tree.model().index(0, 0)))
            
        layout.addWidget(tree)
        
        return sidebar
        
    def create_main_content(self):
        """Crear área de contenido principal"""
        content = QFrame()
        content.setObjectName("mainContent")
        
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Header del contenido
        header = QFrame()
        header.setObjectName("contentHeader")
        header_layout = QHBoxLayout(header)
        
        # Título de la página
        page_title = QLabel("Dashboard")
        page_title.setObjectName("pageTitle")
        header_layout.addWidget(page_title)
        
        header_layout.addStretch()
        
        # Botón de acción principal
        primary_btn = QPushButton("Agregar elemento")
        primary_btn.setObjectName("primaryButton")
        header_layout.addWidget(primary_btn)
        
        layout.addWidget(header)
        
        # Área de contenido scrollable
        content_area = QTextEdit()
        content_area.setObjectName("contentArea")
        content_area.setPlainText(
            "Bienvenido a Almacena\n\n"
            "Esta es el área principal donde se mostrará el contenido "
            "de la aplicación. El diseño sigue los principios de "
            "Material Design 3 con colores modernos y espaciado apropiado."
        )
        content_area.setReadOnly(True)
        layout.addWidget(content_area)
        
        return content
        
    def create_status_bar(self):
        """Crear barra de estado"""
        status_bar = QStatusBar()
        status_bar.showMessage("Listo")
        self.setStatusBar(status_bar)
        
    def setup_material_theme(self):
        """Configurar tema Material Design 3"""
        # Paleta de colores Material Design 3
        self.setStyleSheet("""
            /* Estilos globales */
            QMainWindow {
                background-color: #fef7ff;
                color: #1d1b20;
            }
            
            /* Barra de menú */
            QMenuBar {
                background-color: #fef7ff;
                color: #1d1b20;
                border-bottom: 1px solid #e7e0ec;
                padding: 4px;
            }
            
            QMenuBar::item {
                padding: 8px 16px;
                border-radius: 8px;
            }
            
            QMenuBar::item:selected {
                background-color: #e8def8;
            }
            
            /* Barra de herramientas */
            QToolBar {
                background-color: #fef7ff;
                border-bottom: 1px solid #e7e0ec;
                padding: 8px;
                spacing: 8px;
            }
            
            QPushButton#toolbarButton {
                background-color: #e8def8;
                color: #1d1b20;
                border: none;
                border-radius: 12px;
                padding: 8px 16px;
                font-weight: 500;
            }
            
            QPushButton#toolbarButton:hover {
                background-color: #d0bcff;
            }
            
            QPushButton#toolbarButton:pressed {
                background-color: #b69df8;
            }
            
            /* Panel lateral */
            QFrame#sidebar {
                background-color: #f7f2fa;
                border-right: 1px solid #e7e0ec;
            }
            
            QLabel#sidebarTitle {
                font-size: 16px;
                font-weight: 600;
                color: #1d1b20;
                margin-bottom: 16px;
            }
            
            QTreeWidget#navigationTree {
                background-color: transparent;
                border: none;
                outline: none;
            }
            
            QTreeWidget#navigationTree::item {
                padding: 12px;
                border-radius: 8px;
                margin: 2px 0px;
            }
            
            QTreeWidget#navigationTree::item:selected {
                background-color: #e8def8;
                color: #1d1b20;
            }
            
            QTreeWidget#navigationTree::item:hover {
                background-color: #f3edf7;
            }
            
            /* Contenido principal */
            QFrame#mainContent {
                background-color: #fef7ff;
            }
            
            QFrame#contentHeader {
                background-color: transparent;
                border-bottom: 1px solid #e7e0ec;
                padding-bottom: 16px;
                margin-bottom: 24px;
            }
            
            QLabel#pageTitle {
                font-size: 24px;
                font-weight: 600;
                color: #1d1b20;
            }
            
            QPushButton#primaryButton {
                background-color: #6750a4;
                color: #ffffff;
                border: none;
                border-radius: 20px;
                padding: 12px 24px;
                font-weight: 500;
                font-size: 14px;
            }
            
            QPushButton#primaryButton:hover {
                background-color: #7965af;
            }
            
            QPushButton#primaryButton:pressed {
                background-color: #5e4b99;
            }
            
            QTextEdit#contentArea {
                background-color: #ffffff;
                border: 1px solid #e7e0ec;
                border-radius: 12px;
                padding: 16px;
                font-size: 14px;
                line-height: 1.5;
            }
            
            /* Barra de estado */
            QStatusBar {
                background-color: #f7f2fa;
                color: #49454f;
                border-top: 1px solid #e7e0ec;
                padding: 4px 16px;
            }
        """)
        
        # Configurar fuente
        font = QFont("Segoe UI", 10)  # Fuente moderna
        self.setFont(font) 