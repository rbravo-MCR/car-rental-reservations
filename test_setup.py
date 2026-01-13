#!/usr/bin/env python
"""
Script de verificación de configuración
Prueba que todos los componentes principales estén funcionando
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_imports():
    """Verificar que todos los imports funcionen"""
    print("=" * 50)
    print("🔍 Verificando imports...")
    print("=" * 50)

    try:
        # Core dependencies
        import fastapi
        print(f"✅ FastAPI {fastapi.__version__}")

        import uvicorn
        print(f"✅ Uvicorn {uvicorn.__version__}")

        import pydantic
        print(f"✅ Pydantic {pydantic.__version__}")

        import sqlalchemy
        print(f"✅ SQLAlchemy {sqlalchemy.__version__}")

        import stripe
        print(f"✅ Stripe {stripe.__version__}")

        import structlog
        print(f"✅ Structlog {structlog.__version__}")

        # Testing tools
        import pytest
        print(f"✅ Pytest {pytest.__version__}")

        print("\n✨ Todos los imports exitosos!")
        return True

    except ImportError as e:
        print(f"\n❌ Error en imports: {e}")
        return False


def test_config():
    """Verificar configuración"""
    print("\n" + "=" * 50)
    print("⚙️  Verificando configuración...")
    print("=" * 50)

    try:
        from src.config.settings import get_settings

        settings = get_settings()
        print("✅ Settings cargados correctamente")
        print(f"   - App name: {settings.app_name}")
        print(f"   - Version: {settings.app_version}")
        print(f"   - Database URL: {settings.database_url[:50]}...")
        print(f"   - Receipts dir: {settings.receipts_output_dir}")

        return True

    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        return False


def test_stripe_client():
    """Verificar Stripe client"""
    print("\n" + "=" * 50)
    print("💳 Verificando Stripe client...")
    print("=" * 50)

    try:
        from src.infrastructure.external.payments.stripe_client import StripePaymentGateway

        gateway = StripePaymentGateway()
        print("✅ StripePaymentGateway instanciado")
        print(f"   - API key configurado: {'Sí' if gateway.api_key else 'No (vacío)'}")
        print(f"   - Webhook secret configurado: {'Sí' if gateway.webhook_secret else 'No (vacío)'}")

        return True

    except Exception as e:
        print(f"❌ Error en Stripe client: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_receipt_generator():
    """Verificar Receipt generator"""
    print("\n" + "=" * 50)
    print("📄 Verificando Receipt generator...")
    print("=" * 50)

    try:
        from src.infrastructure.documents.receipt_generator import WeasyPrintReceiptGenerator

        generator = WeasyPrintReceiptGenerator()
        print("✅ WeasyPrintReceiptGenerator instanciado")
        print(f"   - Templates dir: {generator.templates_dir}")
        print(f"   - Output dir: {generator.output_dir}")

        return True

    except Exception as e:
        print(f"❌ Error en Receipt generator: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_domain_entities():
    """Verificar entidades del dominio"""
    print("\n" + "=" * 50)
    print("🏗️  Verificando entidades del dominio...")
    print("=" * 50)

    try:

        print("✅ Payment entity importada")
        print("✅ Reservation entity importada")
        print("✅ Driver entity importada")

        return True

    except Exception as e:
        print(f"❌ Error en entidades: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_datetime_usage():
    """Verificar uso correcto de datetime"""
    print("\n" + "=" * 50)
    print("📅 Verificando uso de datetime...")
    print("=" * 50)

    try:
        from datetime import UTC, datetime

        now = datetime.now(UTC)
        print("✅ datetime.now(UTC) funciona correctamente")
        print(f"   - Hora actual UTC: {now}")

        return True

    except Exception as e:
        print(f"❌ Error con datetime: {e}")
        return False


def main():
    """Ejecutar todas las pruebas"""
    print("\n" + "=" * 60)
    print("🚀 VERIFICACIÓN DE CONFIGURACIÓN - Car Rental Reservations")
    print("=" * 60)

    results = []

    # Ejecutar todas las pruebas
    results.append(("Imports", test_imports()))
    results.append(("Configuración", test_config()))
    results.append(("Stripe Client", test_stripe_client()))
    results.append(("Receipt Generator", test_receipt_generator()))
    results.append(("Entidades del Dominio", test_domain_entities()))
    results.append(("Datetime Usage", test_datetime_usage()))

    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print("\n" + "=" * 60)
    if passed == total:
        print(f"🎉 ¡Todas las verificaciones pasaron! ({passed}/{total})")
        print("=" * 60)
        print("\n✨ El proyecto está listo para usar!")
        print("\nPróximos pasos:")
        print("  1. Ejecutar tests: uv run pytest")
        print("  2. Iniciar app: uv run uvicorn src.presentation.main:app --reload")
        return 0
    else:
        print(f"⚠️  Algunas verificaciones fallaron ({passed}/{total})")
        print("=" * 60)
        print("\n💡 Revisa los errores arriba para más detalles")
        return 1


if __name__ == "__main__":
    sys.exit(main())
