# 🚗 Car Rental Reservations API

Sistema global de reservas de autos con alta concurrencia, arquitectura limpia y procesamiento de pagos.

## 🏗️ Arquitectura

- **Clean Architecture** (Domain → Application → Infrastructure → Presentation)
- **FastAPI** con async/await
- **MySQL** con SQLAlchemy async
- **Redis** para cache e idempotencia
- **Stripe** para pagos
- **Outbox Pattern** para eventos

## 📋 Requisitos

- Python 3.12+
- Poetry
- MySQL 8.0+
- Redis 7+

## 🚀 Instalación

### 1. Clonar e instalar dependencias
```bash
git clone <repo-url>
cd car-rental-reservations
poetry install
```

### 2. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

### 3. Crear base de datos
```sql
CREATE DATABASE car_rental_reservations CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. Ejecutar migraciones (si usas Alembic)
```bash
poetry run alembic upgrade head
```

### 5. Ejecutar aplicación
```bash
# Modo desarrollo (con hot-reload)
poetry run dev

# O manualmente
poetry run uvicorn src.presentation.main:app --reload
```

La API estará disponible en: `http://localhost:8000`

Documentación interactiva: `http://localhost:8000/docs`

## 🧪 Testing
```bash
# Todos los tests
poetry run test

# Tests unitarios
poetry run pytest tests/unit/ -v

# Tests de integración
poetry run pytest tests/integration/ -v

# Con coverage
poetry run pytest --cov=src --cov-report=html
```

## 🔄 Workers
```bash
# Worker de outbox (procesa eventos)
poetry run worker-outbox

# Worker de limpieza (idempotency keys)
poetry run worker-cleanup
```

## 📁 Estructura del Proyecto
```
src/
├── config/              # Configuración
├── domain/              # Lógica de negocio (entities, value objects)
├── application/         # Casos de uso (use cases, DTOs)
├── infrastructure/      # Detalles técnicos (DB, APIs externas)
├── presentation/        # FastAPI endpoints
└── workers/             # Background workers
```

## 🔑 Variables de Entorno Principales

| Variable | Descripción |
|----------|-------------|
| `DATABASE_URL` | Conexión a MySQL |
| `REDIS_URL` | Conexión a Redis |
| `STRIPE_SECRET_KEY` | API key de Stripe |
| `SECRET_KEY` | Clave para JWT |

Ver `.env.example` para lista completa.

## 📚 Endpoints Principales

### Disponibilidad
- `GET /api/v1/availability` - Buscar vehículos disponibles

### Reservas
- `POST /api/v1/reservations` - Crear reserva con pago
- `GET /api/v1/reservations/{id}` - Consultar reserva
- `GET /api/v1/reservations` - Listar reservas

### Webhooks
- `POST /api/v1/webhooks/stripe` - Webhooks de Stripe
- `POST /api/v1/webhooks/suppliers/{supplier}` - Webhooks de proveedores

## 🏢 Proveedores Soportados

- LOCALIZA
- Europcar
- Centauro
- America Car Rental
- Infinity
- Rently Network

## 📊 Monitoreo

- Logs estructurados (JSON) via `structlog`
- Métricas en `/metrics` (si está habilitado)

## 🔒 Seguridad

- Autenticación JWT
- Rate limiting
- Idempotencia en requests críticos
- Validación estricta de inputs (Pydantic)

## 🤝 Contribuir

1. Fork el proyecto
2. Crear feature branch (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push al branch (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📝 Licencia

Propietario - Mexico Car Rental Platform

## 👥 Autor

Rafael - Senior Software Architect