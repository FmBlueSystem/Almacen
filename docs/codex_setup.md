# Entorno Codex

Para ejecutar las pruebas en la plataforma Codex, instala las dependencias de Python y librerías del sistema necesarias.

```bash
# Dependencias de Python
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install mutagen sqlite-utils

# Bibliotecas de sistema requeridas por PyQt6
apt-get update && apt-get install -y libegl1 libpulse0

# Ejecutar pytest en modo "offscreen" para evitar problemas de display
export QT_QPA_PLATFORM=offscreen
pytest
```

Esto evita errores como `ModuleNotFoundError: No module named 'dotenv'` o fallos al cargar la interfaz de Qt.
