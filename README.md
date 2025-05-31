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
