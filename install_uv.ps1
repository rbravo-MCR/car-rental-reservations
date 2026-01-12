# Script de instalación de uv para Windows
# Ejecutar con: powershell -ExecutionPolicy Bypass -File install_uv.ps1

Write-Host "=== Instalando uv ===" -ForegroundColor Cyan

# Instalar uv
Write-Host "`nDescargando e instalando uv..." -ForegroundColor Yellow
irm https://astral.sh/uv/install.ps1 | iex

# Verificar instalación
Write-Host "`n=== Verificando instalación ===" -ForegroundColor Cyan
& uv --version

# Sincronizar dependencias
Write-Host "`n=== Sincronizando dependencias ===" -ForegroundColor Cyan
Write-Host "Instalando dependencias de producción y desarrollo..." -ForegroundColor Yellow
& uv sync --extra dev

# Verificar Python
Write-Host "`n=== Verificando Python ===" -ForegroundColor Cyan
& uv run python --version

# Verificar paquetes instalados
Write-Host "`n=== Verificando paquetes ===" -ForegroundColor Cyan
& uv run python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"
& uv run python -c "import sqlalchemy; print(f'SQLAlchemy: {sqlalchemy.__version__}')"
& uv run python -c "import stripe; print(f'Stripe: {stripe.__version__}')"

# Ejecutar script de verificación
Write-Host "`n=== Ejecutando verificación completa ===" -ForegroundColor Cyan
& uv run python test_setup.py

Write-Host "`n=== Instalación completada ===" -ForegroundColor Green
Write-Host "`nPróximos pasos:" -ForegroundColor Cyan
Write-Host "  1. Ejecutar verificación: uv run python test_setup.py" -ForegroundColor White
Write-Host "  2. Ejecutar tests: uv run pytest" -ForegroundColor White
Write-Host "  3. Ejecutar app: uv run uvicorn src.presentation.main:app --reload" -ForegroundColor White
Write-Host "  4. Ver comandos disponibles en UV_MIGRATION.md" -ForegroundColor White
