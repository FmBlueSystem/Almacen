# Almacena - Sistema de Gestión de Audio

Aplicación de escritorio para gestionar y organizar archivos de audio, con soporte para importación de metadatos y visualización en modo pantalla completa.

## Características

- 🎵 Importación de archivos de audio (MP3, WAV, FLAC, M4A)
- 📊 Visualización en tabla con paginación
- 🔍 Búsqueda y filtrado por título, artista y género
- 🎨 Interfaz moderna con Material Design 3
- 📱 Modo pantalla completa adaptativo
- 🌍 Soporte para internacionalización
- 💾 Base de datos SQLite con respaldo

## Requisitos

- Python 3.10 o superior
- Sistema de ventanas compatible con Qt6
- Espacio en disco para base de datos
- Dependencias listadas en requirements.txt

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/usuario/almacena.git
cd almacena
```

2. Crear y activar entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Para desarrollo
```

4. Inicializar la aplicación:
```bash
python scripts/init_app.py
```

## Uso

1. Ejecutar la aplicación:
```bash
python main.py
```

2. La aplicación iniciará en modo pantalla completa
3. Usar los botones de la barra de herramientas para importar música
4. Utilizar los filtros para buscar canciones
5. La tabla se actualiza automáticamente y muestra la paginación

## Estructura del Proyecto

```
almacena/
├── assets/             # Recursos estáticos
│   ├── icons/         # Iconos de la aplicación
│   ├── images/        # Imágenes
│   └── translations/  # Archivos de traducción
├── data/              # Datos y base de datos
│   └── backups/      # Respaldos automáticos
├── docs/             # Documentación
├── logs/            # Registros de la aplicación
├── scripts/         # Scripts de utilidad
├── src/             # Código fuente
│   ├── database/   # Conexión y migraciones
│   ├── models/     # Modelos de datos
│   ├── services/   # Lógica de negocio
│   ├── ui/         # Archivos de interfaz
│   ├── utils/      # Utilidades
│   └── views/      # Vistas y controladores
└── tests/          # Pruebas automatizadas
```

## Desarrollo

Para contribuir al desarrollo:

1. Instalar dependencias de desarrollo:
```bash
pip install -r requirements-dev.txt
```

2. Activar pre-commit:
```bash
pre-commit install
```

3. Ejecutar pruebas:
```bash
pytest
```

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Tests específicos
pytest tests/unit/
pytest tests/integration/

# Tests de prevención de recursión
pytest tests/unit/test_recursion_prevention.py
pytest tests/integration/test_recursion_integration.py

# Con coverage
pytest --cov=src

# Demostración de corrección de RecursionError
python scripts/test_recursion_fix.py
```

## 🛡️ Corrección del RecursionError

Este proyecto incluye una corrección comprensiva para el `RecursionError: maximum recursion depth exceeded` que ocurría en el método `load_songs_for_library_view`.

### Problema Original
- **Causa:** `QMessageBox.critical()` modal interfería con el bucle de eventos de Qt
- **Síntoma:** Bucle recursivo durante manejo de errores de base de datos
- **Trigger:** Eventos `on_search_changed` que se re-disparaban durante modales

### Solución Implementada

#### 🔒 Circuit Breaker Pattern
- Previene re-entrada en operaciones de carga
- Implementa cooldown después de errores
- Permite reset manual del estado

#### ⏱️ Debouncing de Búsquedas
- Retrasa emisión de señales de búsqueda (300ms)
- Cancela búsquedas anteriores si llegan nuevas
- Previene llamadas excesivas a la base de datos

#### 📝 Logging Estructurado
- Reemplaza `traceback.print_exc()` con logging apropiado
- Manejo diferenciado de errores de DB vs errores generales
- Mensajes amigables para el usuario

#### 🚫 Eliminación de Modales Problemáticos
- Remueve `QMessageBox.critical()` de contextos de carga
- Usa barra de estado para mensajes de error
- Mantiene UI responsiva durante errores

### Archivos Principales de la Corrección
- `src/database/connection.py` - Excepciones personalizadas
- `src/utils/error_handler.py` - Circuit breaker y utilidades
- `src/ui/windows/main_window.py` - Control de re-entrada
- `src/ui/components/content_views/library_view.py` - Debouncing
- `tests/unit/test_recursion_prevention.py` - Tests unitarios
- `tests/integration/test_recursion_integration.py` - Tests de integración

### Verificación
```bash
# Ejecutar demostración de la corrección
python scripts/test_recursion_fix.py

# Ejecutar tests específicos de recursión
pytest tests/unit/test_recursion_prevention.py -v
pytest tests/integration/test_recursion_integration.py -v
```

Ver `recursion_error_fix_plan.md` para detalles completos del análisis y implementación.

## Configuración

La configuración se realiza mediante variables de entorno en el archivo `.env`:

```env
# Base de datos
DATABASE_PATH=data/almacena.db
DATABASE_BACKUP_PATH=data/backups/

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/almacena.log

# Interfaz
THEME=dark
LANGUAGE=es
```

## Licencia

Este proyecto está licenciado bajo los términos de la licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## Contribuir

1. Hacer fork del repositorio
2. Crear una rama para tu característica (`git checkout -b feature/AmazingFeature`)
3. Hacer commit de tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Hacer push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Soporte

Para reportar problemas o solicitar características, por favor usar el [sistema de issues](https://github.com/usuario/almacena/issues).
