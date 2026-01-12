#!/bin/bash
# Script de instalación de uv para Linux/macOS
# Ejecutar con: bash install_uv.sh

set -e

echo "=== Instalando uv ==="

# Instalar uv
echo -e "\nDescargando e instalando uv..."
curl -LsSf https://astral.sh/uv/install.sh | sh

# Agregar uv al PATH de la sesión actual
export PATH="$HOME/.cargo/bin:$PATH"

# Verificar instalación
echo -e "\n=== Verificando instalación ==="
uv --version

# Sincronizar dependencias
echo -e "\n=== Sincronizando dependencias ==="
echo "Instalando dependencias de producción y desarrollo..."
uv sync --extra dev

# Verificar Python
echo -e "\n=== Verificando Python ==="
uv run python --version

# Verificar paquetes instalados
echo -e "\n=== Verificando paquetes ==="
uv run python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"
uv run python -c "import sqlalchemy; print(f'SQLAlchemy: {sqlalchemy.__version__}')"
uv run python -c "import stripe; print(f'Stripe: {stripe.__version__}')"

# Ejecutar script de verificación
echo -e "\n=== Ejecutando verificación completa ==="
uv run python test_setup.py

echo -e "\n=== Instalación completada ==="
echo -e "\nPróximos pasos:"
echo "  1. Ejecutar verificación: uv run python test_setup.py"
echo "  2. Ejecutar tests: uv run pytest"
echo "  3. Ejecutar app: uv run uvicorn src.presentation.main:app --reload"
echo "  4. Ver comandos disponibles en UV_MIGRATION.md"
