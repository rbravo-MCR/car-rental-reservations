# 🚀 Quick Start con uv

## Instalación rápida (Windows)

### Opción 1: Script automático (Recomendado)
```powershell
powershell -ExecutionPolicy Bypass -File install_uv.ps1
```

### Opción 2: Manual
```powershell
# 1. Instalar uv
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 2. Sincronizar dependencias
uv sync --extra dev

# 3. Verificar
uv run python --version
```

## Instalación rápida (Linux/macOS)

```bash
# Opción 1: Script automático
bash install_uv.sh

# Opción 2: Manual
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync --extra dev
uv run python --version
```

## Comandos principales

### Desarrollo
```bash
# Ejecutar aplicación
uv run uvicorn src.presentation.main:app --reload

# Ejecutar tests
uv run pytest

# Ejecutar tests con coverage
uv run pytest --cov=src --cov-report=html

# Linting
uv run ruff check .
uv run ruff format .

# Type checking
uv run mypy src/
```

### Gestión de dependencias
```bash
# Agregar dependencia de producción
uv add package-name

# Agregar dependencia de desarrollo
uv add --dev package-name

# Actualizar todas las dependencias
uv lock --upgrade
uv sync

# Ver dependencias instaladas
uv pip list
```

### Bases de datos (Alembic)
```bash
# Crear migración
uv run alembic revision --autogenerate -m "descripción"

# Aplicar migraciones
uv run alembic upgrade head

# Revertir migración
uv run alembic downgrade -1
```

## ¿Por qué uv?

- ⚡ **10-100x más rápido** que Poetry
- 🐍 Gestión de versiones de Python integrada
- 🔒 Lock file determinístico
- 💾 Caché global (ahorra espacio y tiempo)
- 🚀 Instalación instantánea de paquetes

## Estructura del proyecto

```
car-rental-reservations/
├── .python-version          # Python 3.14
├── pyproject.toml          # Configuración y dependencias
├── uv.lock                 # Lock file (generado por uv)
├── .venv/                  # Virtual environment
├── src/                    # Código fuente
├── tests/                  # Tests
└── alembic/                # Migraciones de BD
```

## Migración desde Poetry

✅ Ya completado:
- [x] pyproject.toml convertido a formato estándar
- [x] Build backend cambiado a hatchling
- [x] Python 3.14 configurado
- [x] Scripts de instalación creados

📝 Puedes eliminar (opcional):
```bash
# Una vez que verificaste que todo funciona
rm poetry.lock
pip uninstall poetry
```

## Más información

- 📚 Documentación completa: `UV_MIGRATION.md`
- 🌐 Docs oficiales de uv: https://docs.astral.sh/uv/
