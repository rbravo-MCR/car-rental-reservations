# Car Rental Reservations - Avances del Proyecto

## 📋 Información General

**Proyecto**: Sistema Global de Reservas de Renta de Autos
**Tecnología**: Python 3.12+ con FastAPI
**Arquitectura**: Hexagonal (Ports & Adapters) + DDD
**Base de Datos**: MySQL con SQLAlchemy (Async)
**Fecha de Inicio**: 2025
**Estado**: En Desarrollo Activo

---

## 🎯 Objetivos del Sistema

Sistema de alta concurrencia para gestionar reservas de renta de autos a nivel global, integrando múltiples proveedores (suppliers) y procesamiento de pagos.

### Características Principales
- ✅ Búsqueda de disponibilidad multi-proveedor
- ✅ Creación de reservas con procesamiento de pagos
- ✅ Generación automática de recibos PDF
- ✅ Sistema de eventos para integraciones
- ✅ Transaccional con Unit of Work pattern
- ✅ APIs RESTful documentadas

---

## 📁 Estructura del Proyecto

```
car-rental-reservations/
├── src/
│   ├── config/                    # Configuración y settings
│   ├── domain/                    # Capa de Dominio (DDD)
│   │   ├── entities/             # Entidades del dominio
│   │   ├── value_objects/        # Value Objects
│   │   ├── events/               # Domain Events
│   │   ├── services/             # Domain Services
│   │   └── exceptions/           # Domain Exceptions
│   ├── application/              # Capa de Aplicación
│   │   ├── dto/                  # Data Transfer Objects
│   │   ├── ports/                # Interfaces (Ports)
│   │   └── use_cases/            # Casos de Uso
│   ├── infrastructure/           # Capa de Infraestructura
│   │   ├── persistence/          # Repositorios SQLAlchemy
│   │   ├── external/             # Clientes externos
│   │   │   ├── suppliers/       # Integración con proveedores
│   │   │   └── payments/        # Integración con Stripe
│   │   └── documents/            # Generación de PDFs
│   └── presentation/             # Capa de Presentación
│       ├── api/v1/               # Endpoints FastAPI
│       └── schemas/              # Pydantic Schemas
├── tests/                        # Tests unitarios e integración
├── pyproject.toml               # Configuración Poetry
└── README.md                    # Documentación principal
```

---

## ✅ Componentes Completados

### 1. Configuración (5 archivos)
- ✅ `settings.py` - Configuración con Pydantic Settings
- ✅ `database.py` - Configuración de conexión MySQL
- ✅ `logging.py` - Configuración de Structlog
- ✅ `pyproject.toml` - Gestión de dependencias con Poetry
- ✅ `.env` - Variables de entorno

### 2. Capa de Dominio (21+ archivos)

#### Entidades
- ✅ `Reservation` - Aggregate Root principal
- ✅ `Driver` - Información de conductores
- ✅ `Contact` - Contactos del cliente
- ✅ `PricingItem` - Items de pricing
- ✅ `Payment` - Entidad de pagos

#### Value Objects
- ✅ `ReservationStatus` - Estados de reserva (PENDING, CONFIRMED, CANCELLED, COMPLETED, FAILED)
- ✅ `PaymentStatus` - Estados de pago (UNPAID, PENDING, PAID, FAILED, REFUNDED)

#### Domain Events
- ✅ `ReservationCreated` - Evento de creación de reserva
- ✅ `ReservationConfirmed` - Evento de confirmación
- ✅ `PaymentProcessed` - Evento de pago procesado

#### Domain Services
- ✅ `PricingCalculator` - Cálculo de precios y comisiones
- ✅ `ReservationCodeGenerator` - Generación de códigos únicos (ULID)
- ✅ `StateMachine` - Máquina de estados para transiciones

#### Domain Exceptions
- ✅ `PaymentFailedError` - Error en procesamiento de pagos
- ✅ `ReservationCreationError` - Error al crear reserva
- ✅ `SupplierConfirmationError` - Error de confirmación con proveedor
- ✅ `InvalidStateTransitionError` - Transición de estado inválida

### 3. Capa de Aplicación (15 archivos)

#### DTOs (Data Transfer Objects)
- ✅ `AvailabilitySearchDTO` - Búsqueda de disponibilidad
- ✅ `AvailabilityResultDTO` - Resultado de disponibilidad
- ✅ `CreateReservationDTO` - Creación de reserva
- ✅ `ReservationResultDTO` - Resultado de reserva
- ✅ `GetReservationDTO` - Obtener reserva por código
- ✅ `ListReservationsDTO` - Listar reservas
- ✅ `PaymentDTO` - Procesamiento de pagos

#### Ports (Interfaces)
- ✅ `UnitOfWork` - Patrón Unit of Work
- ✅ `ReservationRepository` - Repositorio de reservas
- ✅ `PaymentRepository` - Repositorio de pagos
- ✅ `CustomerRepository` - Repositorio de clientes
- ✅ `SupplierRepository` - Repositorio de proveedores
- ✅ `OfficeRepository` - Repositorio de oficinas
- ✅ `OutboxRepository` - Repositorio de outbox pattern
- ✅ `SupplierRequestRepository` - Repositorio de solicitudes a proveedores
- ✅ `SupplierGateway` - Gateway para proveedores externos
- ✅ `PaymentGateway` - Gateway para procesamiento de pagos
- ✅ `ReceiptGenerator` - Generador de recibos
- ✅ `EventBus` - Bus de eventos

#### Use Cases (Casos de Uso)
- ✅ `SearchAvailabilityUseCase` - Búsqueda de disponibilidad
- ✅ `CreateReservationUseCase` - Creación de reserva completa
- ✅ `GetReservationUseCase` - Obtener detalles de reserva
- ✅ `ListReservationsUseCase` - Listar reservas con filtros

### 4. Capa de Infraestructura (15+ archivos)

#### Persistence (SQLAlchemy)
- ✅ `database.py` - Configuración de SQLAlchemy async
- ✅ `models.py` - Modelos de base de datos
- ✅ `SQLAlchemyUnitOfWork` - Implementación de Unit of Work
- ✅ `SQLAlchemyReservationRepository` - Repositorio de reservas
- ✅ `SQLAlchemyPaymentRepository` - Repositorio de pagos
- ✅ `SQLAlchemyCustomerRepository` - Repositorio de clientes
- ✅ `SQLAlchemySupplierRepository` - Repositorio de proveedores
- ✅ `SQLAlchemyOfficeRepository` - Repositorio de oficinas
- ✅ `SQLAlchemyOutboxRepository` - Repositorio de outbox
- ✅ `SQLAlchemySupplierRequestRepository` - Repositorio de solicitudes

#### External Integrations
##### Suppliers
- ✅ `BaseSupplierClient` - Cliente base abstracto
- ✅ `LocalizaClient` - Cliente para Localiza (principal proveedor)
- ✅ `SupplierFactory` - Factory pattern para suppliers

##### Payments
- ✅ `StripePaymentGateway` - Integración con Stripe

##### Documents
- ✅ `WeasyPrintReceiptGenerator` - Generación de PDFs con WeasyPrint

#### Idempotency
- ✅ `IdempotencyStore` - Almacenamiento de claves de idempotencia

### 5. Capa de Presentación (8+ archivos)

#### API v1 (FastAPI)
- ✅ `health.py` - Endpoints de health checks
  - `GET /health` - Health check básico
  - `GET /health/detailed` - Health check detallado
  - `GET /health/ready` - Readiness probe (Kubernetes)
  - `GET /health/live` - Liveness probe (Kubernetes)

- ✅ `availability.py` - Endpoints de disponibilidad
  - `POST /api/v1/availability` - Búsqueda de vehículos disponibles
  - `GET /api/v1/availability/health` - Health check del servicio

- ✅ `reservations.py` - Endpoints de reservas
  - `POST /api/v1/reservations` - Crear nueva reserva
  - `GET /api/v1/reservations/{code}` - Obtener reserva por código
  - `GET /api/v1/reservations` - Listar reservas (paginado)

#### Pydantic Schemas
- ✅ `AvailabilitySearchRequest` - Request de búsqueda
- ✅ `VehicleAvailabilityResponse` - Response de disponibilidad
- ✅ `CreateReservationRequest` - Request de creación
- ✅ `ReservationResponse` - Response de creación
- ✅ `ReservationDetailResponse` - Response detallada
- ✅ `ErrorResponse` - Response de errores

#### Middleware
- ✅ `ErrorHandler` - Manejo global de errores

---

## 🔧 Tecnologías y Dependencias

### Core
- **Python**: 3.12+
- **FastAPI**: 0.115.0+ - Framework web moderno y rápido
- **Uvicorn**: 0.32.0+ - ASGI server con soporte para hot reload

### Database & ORM
- **SQLAlchemy**: 2.0.36+ (con soporte asyncio)
- **aiomysql**: 0.2.0+ - Driver async para MySQL
- **Alembic**: 1.14.0+ - Migraciones de base de datos

### Validation & Serialization
- **Pydantic**: 2.10.0+ (con email extras)
- **Pydantic Settings**: 2.6.0+ - Gestión de configuración

### External Services
- **Stripe**: 11.3.0+ - Procesamiento de pagos
- **httpx**: 0.28.0+ - Cliente HTTP async

### Documents & Templates
- **WeasyPrint**: 62.3+ - Generación de PDFs
- **Jinja2**: 3.1.4+ - Templates HTML

### Utilities
- **structlog**: 24.4.0+ - Logging estructurado
- **python-jose**: 3.3.0+ (con cryptography) - JWT tokens
- **passlib**: 1.7.4+ (con bcrypt) - Hashing de passwords
- **python-dateutil**: 2.9.0+ - Utilidades de fechas
- **ulid-py**: 1.1.0+ - Generación de ULIDs
- **python-multipart**: 0.0.9+ - Soporte para multipart forms

### Caching & Queues
- **redis**: 5.2.0+ (con hiredis) - Cache y message broker

### Development
- **pytest**: 8.3.0+ - Testing framework
- **pytest-asyncio**: 0.24.0+ - Soporte async para pytest
- **pytest-cov**: 6.0.0+ - Coverage de tests
- **faker**: 33.1.0+ - Generación de datos de prueba
- **ruff**: 0.8.0+ - Linter y formatter
- **mypy**: 1.13.0+ - Type checking
- **ipython**: 8.30.0+ - Shell interactivo

---

## 🏗️ Patrones de Diseño Implementados

### Arquitectónicos
1. **Hexagonal Architecture (Ports & Adapters)**
   - Separación clara entre dominio, aplicación e infraestructura
   - Dependencias apuntan hacia el dominio

2. **Domain-Driven Design (DDD)**
   - Aggregate Roots (Reservation)
   - Value Objects (Status enums)
   - Domain Events
   - Domain Services
   - Repository Pattern

3. **CQRS (Command Query Responsibility Segregation)**
   - Separación de comandos (CreateReservation) y queries (GetReservation, ListReservations)

### De Comportamiento
1. **Unit of Work Pattern**
   - Coordinación de transacciones entre múltiples repositorios
   - Rollback automático en caso de error

2. **Repository Pattern**
   - Abstracción del acceso a datos
   - Implementación con SQLAlchemy

3. **Factory Pattern**
   - SupplierFactory para crear instancias de suppliers dinámicamente

4. **Strategy Pattern**
   - Diferentes estrategias de suppliers (Localiza, Europcar, etc.)

5. **Observer Pattern (Event Bus)**
   - Emisión de eventos de dominio
   - Suscriptores para reaccionar a eventos

### Tácticos
1. **Dependency Injection**
   - Inyección de dependencias en use cases
   - FastAPI Depends para gestión de dependencias

2. **DTO (Data Transfer Object)**
   - Transferencia de datos entre capas
   - Validación con Pydantic

3. **Outbox Pattern**
   - Garantía de consistencia eventual
   - Publicación confiable de eventos

4. **Idempotency Pattern**
   - Uso de X-Idempotency-Key header
   - Prevención de operaciones duplicadas

---

## 🔒 Características de Seguridad

- ✅ Validación de entrada con Pydantic
- ✅ Type hints completos para type safety
- ✅ Manejo centralizado de errores
- ✅ Logging estructurado con structlog
- ✅ Prevención de SQL injection (SQLAlchemy ORM)
- ✅ Headers de idempotencia para operaciones críticas
- ✅ Transacciones con rollback automático

---

## 📊 Métricas del Proyecto

### Archivos por Capa
```
✅ Config:         5 archivos
✅ Domain:        25+ archivos
✅ Application:   15 archivos
✅ Infrastructure:15+ archivos
✅ Presentation:   8+ archivos
───────────────────────────────
Total:           68+ archivos
```

### Líneas de Código (Aproximado)
- Domain Layer: ~2,500 líneas
- Application Layer: ~1,500 líneas
- Infrastructure Layer: ~2,000 líneas
- Presentation Layer: ~800 líneas
- **Total: ~6,800+ líneas de código**

---

## 🚀 Flujos Principales Implementados

### 1. Flujo de Búsqueda de Disponibilidad
```
Cliente → API → UseCase → SupplierGateway → Supplier Externo
                    ↓
              UnitOfWork (consulta offices)
                    ↓
              Mapper → Response
```

### 2. Flujo de Creación de Reserva
```
Cliente → API → UseCase
              ↓
        1. Generar código único (ULID)
        2. Crear entidad Reservation
        3. Procesar pago (Stripe)
        4. Confirmar con Supplier
        5. Generar recibo PDF
        6. Persistir en BD (UnitOfWork)
        7. Emitir eventos de dominio
              ↓
        Response con detalles completos
```

### 3. Flujo de Consulta de Reserva
```
Cliente → API → UseCase
              ↓
        Repository → BD
              ↓
        Mapper → Response
```

---

## 🔄 Integraciones Externas

### Proveedores de Vehículos (Suppliers)
- ✅ **Localiza** - Principal proveedor implementado
- 🚧 Europcar - Pendiente
- 🚧 Rently Network - Pendiente

### Procesamiento de Pagos
- ✅ **Stripe** - Procesamiento de tarjetas

### Generación de Documentos
- ✅ **WeasyPrint** - Generación de recibos PDF

---

## 📝 Convenciones del Código

### Nomenclatura
- **Clases**: PascalCase
- **Funciones/Métodos**: snake_case
- **Constantes**: UPPER_SNAKE_CASE
- **Variables privadas**: _prefijo_underscore

### Type Hints
- Uso completo de type hints en todo el código
- Compatibilidad con mypy en modo estricto

### Documentación
- Docstrings en formato Google Style
- Type hints en lugar de documentar tipos en docstrings

### Logging
- Uso de structlog para logging estructurado
- Contexto rico en logs (IDs, códigos, etc.)

---

## 🧪 Testing (Pendiente de Implementación)

### Cobertura Objetivo
- Unit Tests: 80%+
- Integration Tests: 70%+
- E2E Tests: Flujos críticos

### Estructura de Tests
```
tests/
├── unit/
│   ├── domain/
│   ├── application/
│   └── infrastructure/
├── integration/
│   ├── api/
│   └── database/
└── e2e/
    └── flows/
```

---

## 🐛 Correcciones y Mejoras Recientes

### Sesión Actual de Correcciones

#### 1. Configuración y Dependencias
- ✅ Instalación de `structlog` con Poetry
- ✅ Corrección de `pyproject.toml` (sección scripts mal formateada)
- ✅ Configuración de entorno virtual de Poetry

#### 2. Deprecaciones de Python
- ✅ Reemplazo de `datetime.utcnow()` por `datetime.now(UTC)` en:
  - `health.py`
  - `availability_schemas.py`
  - `reservations.py`

#### 3. Arquitectura y Tipos
- ✅ Eliminación de campos redundantes en `AvailabilitySearchDTO`
- ✅ Corrección de tipos de retorno en `UnitOfWork` (interfaces vs implementaciones)
- ✅ Uso de `cast()` para compatibilidad de protocolos en:
  - `availability.py` (1 ubicación)
  - `reservations.py` (3 ubicaciones)

#### 4. Archivos de Dominio Creados
- ✅ **Excepciones de Dominio**:
  - `payment_errors.py` - Errores de pagos
  - `reservation_errors.py` - Errores de reservas
  - `supplier_errors.py` - Errores de proveedores

- ✅ **Value Objects**:
  - `reservation_status.py` - Enums de estados (hereda de `str, Enum`)

#### 5. Validaciones y Robustez
- ✅ Verificaciones de `reservation.id` para evitar valores `None`
- ✅ Type annotations explícitas en listas (`list[ReservationDetailResponse]`)
- ✅ Manejo de casos edge en listado de reservas

#### 6. Type Safety
- ✅ Todos los errores de Pylance resueltos
- ✅ Compatibilidad completa con type checkers (mypy/Pylance)
- ✅ Inferencia de tipos mejorada en toda la codebase

---

## 🚧 Próximos Pasos

### Alta Prioridad
1. **Tests**
   - Implementar tests unitarios para domain layer
   - Tests de integración para repositories
   - Tests E2E para flujos principales

2. **Migraciones de Base de Datos**
   - Crear migraciones Alembic iniciales
   - Scripts de seed data para desarrollo

3. **Documentación API**
   - Swagger/OpenAPI automático (FastAPI)
   - Ejemplos de requests/responses
   - Guía de integración

4. **CI/CD**
   - GitHub Actions para tests
   - Linting automático (ruff)
   - Type checking (mypy)

### Media Prioridad
5. **Autenticación & Autorización**
   - JWT tokens
   - Roles y permisos
   - Rate limiting

6. **Observabilidad**
   - Métricas con Prometheus
   - Tracing distribuido
   - Dashboards

7. **Integraciones Adicionales**
   - Más proveedores (Europcar, etc.)
   - Email notifications (SendGrid)
   - SMS notifications (Twilio)

### Baja Prioridad
8. **Optimizaciones**
   - Caching con Redis
   - Query optimization
   - Connection pooling

9. **Features Avanzados**
   - Cancelaciones
   - Modificaciones de reservas
   - Seguros adicionales
   - Conductores adicionales

---

## 📞 Información de Contacto

**Proyecto**: Car Rental Reservations
**Desarrollador**: Rafael
**Email**: rafael@mexicocarrental.com
**Arquitectura**: Hexagonal + DDD
**Framework**: FastAPI + SQLAlchemy

---

## 📄 Licencia

Proyecto privado - Todos los derechos reservados

---

## 📚 Referencias y Documentación

### Arquitectura y Patrones
- [Hexagonal Architecture - Alistair Cockburn](https://alistair.cockburn.us/hexagonal-architecture/)
- [Domain-Driven Design - Eric Evans](https://www.domainlanguage.com/ddd/)
- [Clean Architecture - Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

### Frameworks y Librerías
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Structlog Documentation](https://www.structlog.org/)

### Best Practices
- [Python Type Hints - PEP 484](https://peps.python.org/pep-0484/)
- [Async/Await - PEP 492](https://peps.python.org/pep-0492/)
- [12 Factor App](https://12factor.net/)

---

**Última Actualización**: 2026-01-08
**Versión del Documento**: 1.0.0
