# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

This project uses **uv** (not Poetry) as the package manager. Python 3.14+ is required.

### Development Commands

```bash
# Install dependencies
uv sync

# Run development server with hot-reload
uv run uvicorn src.presentation.main:app --reload

# Alternative: use the dev script (if configured in pyproject.toml)
uv run dev
```

### Testing

```bash
# Run all tests
uv run pytest

# Run tests with coverage report
uv run pytest --cov=src --cov-report=html

# Run specific test types
uv run pytest tests/unit/ -v
uv run pytest tests/integration/ -v

# Run a single test file
uv run pytest tests/unit/test_specific_file.py -v

# Run a single test function
uv run pytest tests/unit/test_file.py::test_function_name -v
```

### Code Quality

```bash
# Lint code with ruff
uv run ruff check src/ tests/

# Auto-fix linting issues
uv run ruff check --fix src/ tests/

# Type checking with mypy
uv run mypy src/

# Format code
uv run ruff format src/ tests/
```

### Database

```bash
# Create database (MySQL)
CREATE DATABASE car_rental_reservations CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Run migrations (if using Alembic)
uv run alembic upgrade head

# Create new migration
uv run alembic revision --autogenerate -m "description"
```

### Workers (Background Tasks)

Note: Workers are currently not implemented but are planned for processing outbox events.

```bash
# Future commands (when implemented)
uv run worker-outbox      # Process outbox events
uv run worker-cleanup     # Clean up idempotency keys
```

## Architecture Overview

This is a **Clean Architecture** car rental reservations system with strict layer separation and dependency inversion.

### Layer Structure

```
PRESENTATION → APPLICATION → DOMAIN
                ↑
         INFRASTRUCTURE
```

**Dependency Rule**: Inner layers never depend on outer layers. Infrastructure and Presentation depend on Domain through interfaces (Ports).

### Key Architectural Patterns

1. **Clean Architecture**: 4 layers with strict dependency rules
2. **Domain-Driven Design**: Rich domain model with aggregates, value objects, and domain events
3. **Repository Pattern**: Data access abstracted through Protocol interfaces
4. **Unit of Work Pattern**: Coordinate multiple repositories in ACID transactions
5. **Outbox Pattern**: Reliable event publishing (events saved in same transaction as aggregate)
6. **Factory Pattern**: SupplierFactory dynamically instantiates supplier clients
7. **Strategy Pattern**: BaseSupplierClient + concrete implementations (LocalizaClient, etc.)

### Domain Layer (`src/domain/`)

**Aggregate Root**: `Reservation` (in `entities/reservation.py`)
- Owns: `drivers`, `contacts`, `pricing_items` (one-to-many relationships)
- Enforces: State transitions via state machine, driver age validation (21+ years)
- Collects: Domain events (`ReservationCreated`, `ReservationConfirmed`)
- Business methods: `create()`, `add_driver()`, `confirm_with_supplier()`, `mark_as_paid()`

**Value Objects**: `ReservationStatus`, `PaymentStatus` (enums in `value_objects/`)
- State machine validates transitions: PENDING → CONFIRMED → COMPLETED

**Domain Services**: `PricingCalculator`, `ReservationCodeGenerator` (in `services/`)
- Pure business logic that doesn't belong to a single entity

**Domain Events**: `ReservationCreated`, `ReservationConfirmed` (in `events/`)
- Collected by aggregate, published after transaction commits via outbox

**Key Rule**: Domain layer has ZERO dependencies on outer layers. No imports from application, infrastructure, or presentation.

### Application Layer (`src/application/`)

**Use Cases** (in `use_cases/`):
- `CreateReservationUseCase`: Main flow - create reservation, charge payment, confirm with supplier, publish events
- `GetReservationUseCase`: Retrieve by ID or code
- `ListReservationsUseCase`: Query with filters
- `SearchAvailabilityUseCase`: Query suppliers for available vehicles

**DTOs** (in `dto/`):
- Anti-corruption layer between HTTP requests and domain
- `CreateReservationDTO.from_request()` converts Pydantic schema → DTO

**Ports (Interfaces)** (in `ports/`):
- `UnitOfWork`: Transaction coordinator
- `ReservationRepository`, `PaymentRepository`, etc.: Data access interfaces
- `SupplierGateway`: External supplier integration interface
- `PaymentGateway`: Payment processor interface (Stripe)
- `ReceiptGenerator`: PDF generation interface

All ports are **Protocols** (structural subtyping), not ABCs.

### Infrastructure Layer (`src/infrastructure/`)

**Persistence** (`persistence/`):
- `database.py`: SQLAlchemy async session factory
- `repositories/`: Concrete implementations of repository interfaces
  - Map between ORM models and domain entities
  - Use eager loading (`selectinload()`) to prevent N+1 queries
- `unit_of_work.py`: SQLAlchemyUnitOfWork coordinates repos in single transaction

**External Integrations** (`external/`):
- `payments/stripe_client.py`: StripePaymentGateway implementation
  - Uses `asyncio.to_thread()` because Stripe SDK is synchronous
  - Handles all Stripe errors (CardError, RateLimitError, etc.)
- `suppliers/`: Supplier integration factory
  - `supplier_factory.py`: Registry pattern, returns supplier client by ID
  - `base_supplier_client.py`: Abstract base with retry logic, auth, HTTP client
  - `localiza_client.py`: Concrete implementation for LOCALIZA (OAuth2)

**Document Generation** (`documents/`):
- `receipt_generator.py`: PDF generation using WeasyPrint + Jinja2 templates

### Presentation Layer (`src/presentation/`)

**FastAPI Routes** (`api/v1/`):
- `POST /api/v1/reservations`: Create reservation
- `GET /api/v1/reservations/{id}`: Get reservation
- `GET /api/v1/availability`: Search available vehicles
- `POST /api/v1/webhooks/stripe`: Stripe webhooks

**Middleware** (`middleware/`):
- `error_handler.py`: Maps domain exceptions → HTTP status codes
  - 402: PaymentFailedError
  - 404: ReservationNotFoundError
  - 503: SupplierConfirmationError

**Dependency Injection**:
- Use FastAPI `Depends()` for injecting UnitOfWork, gateways, etc.
- Example: `deps: Annotated[ReservationDependencies, Depends(get_reservation_dependencies)]`

## Critical Implementation Details

### Transaction Management (Unit of Work)

Always use `async with self.uow` to ensure proper transaction handling:

```python
async with self.uow:
    try:
        # Multiple operations across repos
        reservation = await self.uow.reservations.save(...)
        payment = await self.uow.payments.save(...)
        await self.uow.outbox.create(...)

        await self.uow.commit()  # All or nothing
    except Exception:
        await self.uow.rollback()  # Automatic in __aexit__
        raise
```

**Lazy Loading**: Repositories are created only when accessed (e.g., `self.uow.reservations`).

### Outbox Pattern for Events

Domain events MUST be saved in the same transaction as the aggregate:

```python
# 1. Collect events from aggregate
events = reservation.clear_events()

# 2. Save to outbox (same transaction!)
for event in events:
    await self.uow.outbox.create(
        event_type=event.event_type,
        aggregate_type="RESERVATION",
        aggregate_id=reservation.id,
        payload=event.payload or {}
    )

# 3. Commit once (atomic)
await self.uow.commit()
```

**Worker Processing** (not yet implemented): A background worker will poll `outbox_events` table and publish events to message broker/webhooks.

### State Machine Validation

State transitions are validated via `state_machine.py`. Never bypass the state machine:

```python
# CORRECT: Use domain method
reservation.confirm_with_supplier(supplier_code, confirmed_at)

# WRONG: Direct assignment bypasses validation
reservation.status = ReservationStatus.CONFIRMED  # Don't do this!
```

### Supplier Integration

Suppliers are accessed via factory pattern:

```python
# Get supplier client dynamically by ID
supplier_gateway = await supplier_factory.get_supplier(supplier_id=1)

# Call supplier API
result = await supplier_gateway.create_reservation(reservation_data)
```

**Adding New Suppliers**:
1. Create new client class inheriting from `BaseSupplierClient`
2. Implement abstract methods: `_authenticate()`, `search_availability()`, `create_reservation()`
3. Register in `SupplierFactory.__init__()` or `get_supplier()`

### Payment Flow

Stripe payments are processed with proper error handling:

```python
payment_result = await payment_gateway.charge(
    amount=dto.price,
    currency=dto.currency_code,
    payment_method_id=dto.payment_method_id,  # From Stripe.js (pm_xxx)
    description=f"Reserva {reservation_code}",
    metadata={"reservation_id": str(reservation.id)}
)

if not payment_result.success:
    raise PaymentFailedError(payment_result.error_message)
```

**Important**: If payment succeeds but supplier confirmation fails, implement refund logic (currently logged as TODO).

### Decimal Precision

All monetary amounts use `Decimal` (never `float`):

```python
from decimal import Decimal

price = Decimal("99.99")  # CORRECT
price = 99.99             # WRONG - float loses precision
```

### Async/Await

This is an async codebase. Always use `async def` and `await`:

```python
# CORRECT
async def execute(self, dto: CreateReservationDTO):
    reservation = await self.uow.reservations.save(reservation)
    await self.uow.commit()

# WRONG - will not work
def execute(self, dto: CreateReservationDTO):
    reservation = self.uow.reservations.save(reservation)  # Missing await
```

## Testing Strategy

- **Unit Tests** (`tests/unit/`): Test domain logic in isolation (no DB, no external APIs)
- **Integration Tests** (`tests/integration/`): Test with real DB and mocked external services
- **Test Fixtures**: Use `pytest` fixtures for common setup (UoW, repos, test data)

Mock external services (Stripe, suppliers) in tests to avoid hitting real APIs.

## Environment Variables

Required variables (see `.env.example`):

```bash
# Database
DATABASE_URL=mysql+aiomysql://user:pass@localhost/car_rental_reservations

# Redis (for caching/idempotency)
REDIS_URL=redis://localhost:6379/0

# Stripe
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# Suppliers
LOCALIZA_API_URL=https://api.localiza.com
LOCALIZA_API_KEY=xxx
LOCALIZA_API_SECRET=xxx
```

## Common Tasks

### Adding a New Use Case

1. Create use case in `src/application/use_cases/`
2. Define DTO in `src/application/dto/`
3. Inject UnitOfWork and required gateways in `__init__()`
4. Implement `execute()` method with transaction handling
5. Map domain exceptions to application-level exceptions
6. Add endpoint in `src/presentation/api/v1/`

### Adding a New Domain Entity

1. Create entity in `src/domain/entities/`
2. Use `@dataclass` and factory method `create()`
3. Add business methods (not just getters/setters)
4. Collect domain events in `_events` list
5. Add ORM model in `src/infrastructure/persistence/models.py`
6. Create repository protocol in `src/application/ports/repositories.py`
7. Implement repository in `src/infrastructure/persistence/repositories/`

### Extending State Machine

Edit `src/domain/services/state_machine.py` to add valid state transitions. State transitions are centralized here.

## Troubleshooting

### Import Errors

This project uses absolute imports from `src/`. If imports fail, ensure:
- You're running commands with `uv run`
- `PYTHONPATH` includes project root (usually automatic with uv)

### Database Connection Issues

- Verify MySQL is running: `mysql -u user -p`
- Check `DATABASE_URL` in `.env`
- Ensure database exists and charset is `utf8mb4`

### Async Errors

- All I/O operations must use `await` (database, HTTP requests, Redis)
- Use `asyncio.to_thread()` for synchronous libraries (like Stripe SDK)
- Never mix sync and async code without proper bridging

## Code Style

- **Line length**: 100 characters (ruff configured)
- **Type hints**: Required for all functions (`mypy` strict mode)
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Docstrings**: Module-level docstrings required, function docstrings for public APIs
- **Imports**: Sorted and organized by ruff (stdlib → third-party → local)
