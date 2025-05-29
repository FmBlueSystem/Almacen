#!/usr/bin/env python3
"""
Almacena - Punto de entrada principal
"""

import sys
from PyQt6.QtWidgets import QApplication

def main():
    """Función principal de la aplicación"""
    app = QApplication(sys.argv)
    
    # TODO: Inicializar ventana principal
    print("Almacena - Sistema iniciado")
    
    # TODO: Mostrar ventana principal
    # window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main()) 