#!/usr/bin/env python3
"""
Script para probar la configuración con dotenv
"""

import sys
import logging
from pathlib import Path

# Agregar src al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.config import config

def setup_logging():
    """Configurar logging para el script"""
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """Función principal del script"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Probando configuración con dotenv")
    
    # Mostrar configuración cargada
    print("\n=== CONFIGURACIÓN CARGADA ===")
    config_dict = config.to_dict()
    
    for key, value in config_dict.items():
        print(f"{key}: {value}")
    
    # Probar configuración específica
    print(f"\n=== CONFIGURACIÓN ESPECÍFICA ===")
    print(f"Base de datos: {config.database_path}")
    print(f"Tema: {config.theme}")
    print(f"Idioma: {config.language}")
    print(f"Ventana: {config.window_width}x{config.window_height}")
    print(f"Debug: {config.debug}")
    
    # Probar configuración personalizada
    custom_value = config.get('CUSTOM_VAR', 'valor_por_defecto')
    print(f"Variable personalizada: {custom_value}")
    
    logger.info("Configuración probada exitosamente")

if __name__ == "__main__":
    main() 