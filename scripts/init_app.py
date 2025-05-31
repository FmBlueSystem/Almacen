#!/usr/bin/env python3
"""
Script de inicialización de la aplicación
Crea los directorios necesarios y verifica la configuración
"""

import os
import sys
import shutil
from pathlib import Path

# Agregar directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.utils.config import config

def setup_directories():
    """Crear directorios necesarios"""
    dirs = [
        Path(config.database_path).parent,
        Path(config.database_backup_path),
        Path(config.log_file).parent,
        root_dir / "assets" / "icons",
        root_dir / "assets" / "images",
        root_dir / "assets" / "translations"
    ]
    
    for directory in dirs:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✓ Directorio creado/verificado: {directory}")

def setup_env_file():
    """Crear archivo .env si no existe"""
    env_file = root_dir / ".env"
    env_example = root_dir / "env.example"
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print(f"✓ Archivo .env creado desde env.example")
    elif not env_file.exists():
        print("⚠ No se encontró env.example para crear .env")
    else:
        print("✓ Archivo .env ya existe")

def verify_python_version():
    """Verificar versión de Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("⚠ Se requiere Python 3.10 o superior")
        return False
    print(f"✓ Versión de Python correcta: {sys.version.split()[0]}")
    return True

def verify_requirements():
    """Verificar que los requirements están instalados"""
    try:
        import PyQt6
        import mutagen
        import sqlite3
        import dotenv
        print("✓ Todas las dependencias requeridas están instaladas")
        return True
    except ImportError as e:
        print(f"⚠ Falta dependencia: {e}")
        print("Ejecute: pip install -r requirements.txt")
        return False

def main():
    """Función principal"""
    print("=== Inicializando Almacena ===")
    
    # Verificar versión de Python
    if not verify_python_version():
        return 1
    
    # Verificar requirements
    if not verify_requirements():
        return 1
    
    # Crear directorios
    setup_directories()
    
    # Configurar .env
    setup_env_file()
    
    print("\n=== Inicialización completada ===")
    print("\nPuede ejecutar la aplicación con: python main.py")
    return 0

if __name__ == "__main__":
    sys.exit(main())
