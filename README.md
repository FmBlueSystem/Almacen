# Almacena 📦

Sistema de gestión moderno desarrollado en Python con PyQt6 y SQLite, diseñado para desarrollo asistido por IA.

## 🚀 Características

- **Interfaz moderna**: GUI con PyQt6 siguiendo Material Design 3
- **Base de datos robusta**: SQLite con sistema de migraciones versionadas
- **Arquitectura limpia**: Separación clara entre capas (UI, Views, Models, Services)
- **Configuración flexible**: Variables de entorno con python-dotenv
- **Testing completo**: Pytest con cobertura y testing de UI
- **CI/CD**: Pipeline automatizado con linting y validaciones
- **Desarrollo asistido por IA**: Documentación clara y prompts precisos

## 📋 Requisitos

- Python 3.13.3 o superior
- Sistema operativo: macOS, Windows, Linux
- Memoria RAM: 512MB mínimo

## 🛠️ Instalación

### 1. Clonar el repositorio
```bash
git clone <repository-url>
cd Almacena
```

### 2. Crear entorno virtual
```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# o
.venv\Scripts\activate     # Windows
```

### 3. Instalar dependencias
```bash
# Producción
pip install -r requirements.txt

# Desarrollo
pip install -r requirements-dev.txt
```

### 4. Configurar variables de entorno
```bash
cp env.example .env
# Editar .env con tu configuración
```

### 5. Inicializar base de datos
```bash
python scripts/init_db.py
```

### 6. Ejecutar aplicación
```bash
python main.py
```

## 🏗️ Estructura del Proyecto

```
Almacena/
├── .venv/                  # Entorno virtual
├── assets/                 # Recursos estáticos
│   ├── icons/             # Iconos de la aplicación
│   ├── images/            # Imágenes
│   └── translations/      # Archivos de traducción
├── data/                  # Base de datos
├── docs/                  # Documentación
├── logs/                  # Archivos de log
├── scripts/               # Scripts de utilidad
│   ├── init_db.py        # Inicializar base de datos
│   └── test_config.py    # Probar configuración
├── src/                   # Código fuente
│   ├── database/         # Acceso a datos
│   │   ├── connection.py # Conexión SQLite
│   │   └── migrations.py # Sistema de migraciones
│   ├── models/           # Modelos de datos
│   ├── services/         # Lógica de negocio
│   ├── ui/              # Componentes UI
│   ├── utils/           # Utilidades
│   │   └── config.py    # Configuración
│   └── views/           # Ventanas y diálogos
├── tests/               # Pruebas
│   ├── integration/     # Tests de integración
│   ├── ui/             # Tests de interfaz
│   └── unit/           # Tests unitarios
├── main.py             # Punto de entrada
├── requirements.in     # Dependencias producción
├── requirements-dev.in # Dependencias desarrollo
└── .env               # Variables de entorno
```

## 🔧 Comandos Útiles

### Gestión de dependencias
```bash
# Actualizar requirements.txt
pip-compile requirements.in

# Actualizar requirements-dev.txt
pip-compile requirements-dev.in

# Instalar nuevas dependencias
pip-sync requirements-dev.txt
```

### Base de datos
```bash
# Inicializar BD
python scripts/init_db.py

# Backup manual
cp data/almacena.db data/backups/backup_$(date +%Y%m%d_%H%M%S).db
```

### Testing
```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=src --cov-report=html

# Tests específicos
pytest tests/unit/
pytest tests/integration/
pytest tests/ui/
```

### Linting y formateo
```bash
# Formatear código
black src/ tests/

# Ordenar imports
isort src/ tests/

# Linting
flake8 src/ tests/
```

## 🌿 Flujo de Trabajo Git

### Estructura de ramas
- `main`: Producción estable
- `dev`: Desarrollo e integración
- `feature/*`: Nuevas funcionalidades

### Flujo recomendado
```bash
# Crear nueva funcionalidad
git checkout dev
git pull origin dev
git checkout -b feature/nueva-funcionalidad

# Desarrollar y hacer commits
git add .
git commit -m "feat: descripción del cambio"

# Merge a dev
git checkout dev
git merge feature/nueva-funcionalidad

# Cuando esté listo para producción
git checkout main
git merge dev
```

## ⚙️ Configuración

### Variables de entorno (.env)
```bash
# Base de datos
DATABASE_PATH=data/almacena.db
DATABASE_BACKUP_PATH=data/backups/

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/almacena.log

# Interfaz
THEME=dark
LANGUAGE=es
WINDOW_WIDTH=1200
WINDOW_HEIGHT=800

# Desarrollo
DEBUG=false
```

### Agregar nuevas migraciones
1. Editar `src/database/migrations.py`
2. Agregar nueva migración en `_get_all_migrations()`
3. Ejecutar `python scripts/init_db.py`

## 🧪 Testing

### Estrategia de testing
- **Unit tests**: Lógica de negocio y utilidades
- **Integration tests**: Base de datos y servicios
- **UI tests**: Interfaz de usuario con pytest-qt

### Estructura de tests
```python
# Ejemplo test unitario
def test_database_connection():
    db = DatabaseConnection(":memory:")
    assert db is not None

# Ejemplo test UI
def test_main_window(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    assert window.isVisible()
```

## 📝 Convenciones

### Commits
- `feat:` Nueva funcionalidad
- `fix:` Corrección de bugs
- `docs:` Documentación
- `test:` Tests
- `refactor:` Refactorización
- `style:` Formateo de código

### Código
- **PEP 8** para estilo de código
- **Type hints** en funciones públicas
- **Docstrings** para clases y métodos
- **Logging** en lugar de print()

## 🔒 Seguridad

### Variables sensibles
- Nunca versionar `.env` en Git
- Usar `env.example` como plantilla
- Generar claves únicas para producción
- Rotar credenciales regularmente

### Backups
- Backup automático antes de migraciones
- Backup manual antes de cambios importantes
- Almacenar backups fuera del proyecto

## 🤝 Contribución

1. Fork del repositorio
2. Crear rama feature
3. Desarrollar con tests
4. Asegurar que pasan todas las validaciones
5. Crear Pull Request

## 📄 Licencia

[Especificar licencia del proyecto]

## 👥 Autores

- **Freddy Molina** - *Desarrollo inicial* - fmolinam@gmail.com

## 🎯 Roadmap

- [ ] Interfaz principal con Material Design 3
- [ ] Sistema de internacionalización
- [ ] Pipeline CI/CD completo
- [ ] Pre-commit hooks
- [ ] Documentación con Sphinx
- [ ] Distribución con PyInstaller

---

Para más información, consultar la documentación en `docs/` o contactar al equipo de desarrollo. 