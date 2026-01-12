# Migración de Poetry a uv

## ✅ Cambios realizados

1. Convertido `pyproject.toml` de formato Poetry a formato estándar PEP 621
2. Cambiado build backend de `poetry-core` a `hatchling`
3. Creado archivo `.python-version` para especificar Python 3.12

## 📦 Instalación de uv

### Windows (PowerShell):
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Linux/macOS:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Con pip:
```bash
pip install uv
```

## 🚀 Comandos para usar uv

### Sincronizar dependencias (equivalente a `poetry install`):
```bash
# Instalar dependencias de producción
uv sync

# Instalar con dependencias de desarrollo
uv sync --extra dev
```

### Agregar dependencias (equivalente a `poetry add`):
```bash
# Producción
uv add fastapi

# Desarrollo
uv add --dev pytest
```

### Remover dependencias (equivalente a `poetry remove`):
```bash
uv remove package-name
```

### Ejecutar comandos en el entorno virtual (equivalente a `poetry run`):
```bash
uv run python script.py
uv run pytest
uv run uvicorn src.presentation.main:app --reload
```

### Actualizar dependencias (equivalente a `poetry update`):
```bash
uv lock --upgrade
uv sync
```

### Crear entorno virtual manualmente:
```bash
uv venv
```

### Ejecutar script con uv:
```bash
uv run python -m src.presentation.main
```

## 🔄 Migración paso a paso

1. **Respaldar archivos de Poetry** (opcional):
   ```bash
   mv poetry.lock poetry.lock.bak
   ```

2. **Inicializar uv**:
   ```bash
   uv sync --extra dev
   ```

3. **Verificar instalación**:
   ```bash
   uv run python --version
   uv run python -c "import fastapi; print(fastapi.__version__)"
   ```

4. **Ejecutar tests**:
   ```bash
   uv run pytest
   ```

5. **Ejecutar aplicación**:
   ```bash
   uv run uvicorn src.presentation.main:app --reload
   ```

## 📊 Comparación Poetry vs uv

| Comando | Poetry | uv |
|---------|--------|-----|
| Instalar deps | `poetry install` | `uv sync` |
| Agregar dep | `poetry add pkg` | `uv add pkg` |
| Remover dep | `poetry remove pkg` | `uv remove pkg` |
| Ejecutar cmd | `poetry run cmd` | `uv run cmd` |
| Actualizar | `poetry update` | `uv lock --upgrade && uv sync` |
| Shell | `poetry shell` | `source .venv/bin/activate` (Linux/Mac)<br>`uv run` (recomendado) |

## 🎯 Ventajas de uv

- ⚡ **10-100x más rápido** que Poetry
- 🔒 **Lock file determinístico** (.uv.lock)
- 🐍 **Gestión de versiones de Python** integrada
- 📦 **Compatible con pip, poetry y otros** formatos
- 🚀 **Instalación instantánea** de paquetes
- 💾 **Caché global** para ahorrar espacio

## 🗑️ Limpieza (opcional)

Después de verificar que todo funciona con uv, puedes eliminar:

```bash
# Eliminar archivos de Poetry
rm poetry.lock.bak
rm -rf .venv  # Si quieres recrear con uv

# Poetry ya no es necesario
pip uninstall poetry
```

## 📝 Notas

- El archivo `pyproject.toml` ahora usa el estándar PEP 621
- uv crea un archivo `uv.lock` en lugar de `poetry.lock`
- El entorno virtual se crea en `.venv` por defecto
- Todas las herramientas (ruff, mypy, pytest) siguen funcionando igual
