# TODO - Pendientes del Proyecto Car Rental Reservations

**Última Actualización**: 2026-01-08
**Versión**: 1.0.0

---

## 📊 Resumen de Estado

| Categoría | Total | Completadas | Pendientes | Progreso |
|-----------|-------|-------------|------------|----------|
| **Testing** | 20 | 0 | 20 | 0% |
| **Base de Datos** | 8 | 2 | 6 | 25% |
| **Documentación** | 10 | 2 | 8 | 20% |
| **Features Core** | 15 | 10 | 5 | 67% |
| **Integraciones** | 12 | 3 | 9 | 25% |
| **DevOps/CI/CD** | 10 | 0 | 10 | 0% |
| **Seguridad** | 8 | 2 | 6 | 25% |
| **Performance** | 6 | 0 | 6 | 0% |
| **Observabilidad** | 8 | 1 | 7 | 12% |

**Total General**: 97 tareas | 20 completadas | 77 pendientes | **21% completado**

---

## 🔴 PRIORIDAD CRÍTICA (P0)

### Testing

#### Unit Tests
- [ ] **Tests de Domain Layer**
  - [ ] `Reservation` entity tests
    - [ ] Test state transitions (PENDING → CONFIRMED → COMPLETED)
    - [ ] Test invalid state transitions (should raise `InvalidStateTransitionError`)
    - [ ] Test pricing calculations
    - [ ] Test domain event emission
  - [ ] `Driver` entity tests
  - [ ] `Contact` entity tests
  - [ ] `PricingItem` entity tests
  - [ ] `Payment` entity tests

  - [ ] Value Objects tests
    - [ ] `ReservationStatus` enum tests
    - [ ] `PaymentStatus` enum tests

  - [ ] Domain Services tests
    - [ ] `PricingCalculator` tests (cálculo de comisiones, impuestos, descuentos)
    - [ ] `ReservationCodeGenerator` tests (unicidad, formato ULID)
    - [ ] `StateMachine` tests (transiciones válidas/inválidas)

- [ ] **Tests de Application Layer**
  - [ ] Use Cases tests
    - [ ] `SearchAvailabilityUseCase` tests (con mocks de supplier)
    - [ ] `CreateReservationUseCase` tests (flujo completo)
    - [ ] `GetReservationUseCase` tests
    - [ ] `ListReservationsUseCase` tests (paginación, filtros)

  - [ ] DTOs validation tests
    - [ ] `AvailabilitySearchDTO` validation
    - [ ] `CreateReservationDTO` validation

#### Integration Tests
- [ ] **Repository Integration Tests**
  - [ ] `SQLAlchemyReservationRepository` tests con BD real
  - [ ] `SQLAlchemyPaymentRepository` tests
  - [ ] `SQLAlchemyCustomerRepository` tests
  - [ ] Unit of Work transaction tests (commit/rollback)

- [ ] **External Services Integration Tests**
  - [ ] Stripe payment gateway tests (con Stripe test mode)
  - [ ] Localiza supplier client tests (con mock server)
  - [ ] WeasyPrint PDF generation tests

#### End-to-End Tests
- [ ] **Critical Flows E2E**
  - [ ] Flujo completo: Búsqueda → Crear Reserva → Ver Reserva
  - [ ] Flujo de pago fallido (handling de errores)
  - [ ] Flujo de supplier no disponible
  - [ ] Flujo de idempotencia (mismo request 2 veces)

**Meta**: **80%+ de cobertura en código crítico**

---

### Base de Datos

- [ ] **Migraciones con Alembic**
  - [ ] Migración inicial: Crear todas las tablas
    - [ ] Tabla `reservations`
    - [ ] Tabla `payments`
    - [ ] Tabla `customers`
    - [ ] Tabla `drivers`
    - [ ] Tabla `contacts`
    - [ ] Tabla `pricing_items`
    - [ ] Tabla `suppliers`
    - [ ] Tabla `offices`
    - [ ] Tabla `outbox_events`
    - [ ] Tabla `supplier_requests`
    - [ ] Tabla `idempotency_keys`

  - [ ] Índices para performance
    - [ ] Index en `reservations.reservation_code` (UNIQUE)
    - [ ] Index en `reservations.customer_id`
    - [ ] Index en `reservations.created_at`
    - [ ] Index en `reservations.status`
    - [ ] Index en `payments.reservation_id`
    - [ ] Index en `idempotency_keys.key` (UNIQUE)
    - [ ] Index en `outbox_events.processed_at`

  - [ ] Foreign keys y constraints
    - [ ] FK: `reservations.customer_id` → `customers.id`
    - [ ] FK: `reservations.supplier_id` → `suppliers.id`
    - [ ] FK: `payments.reservation_id` → `reservations.id`
    - [ ] CHECK: `reservations.pickup_datetime < dropoff_datetime`
    - [ ] CHECK: `payments.amount > 0`

- [ ] **Seed Data para Desarrollo**
  - [ ] Script de seed para suppliers (Localiza, Europcar, etc.)
  - [ ] Script de seed para offices (ubicaciones de prueba)
  - [ ] Script de seed para customers de prueba
  - [ ] Script de seed para car categories

- [ ] **Database Configuration**
  - [ ] Connection pooling configurado (min/max connections)
  - [ ] Query timeout configurado
  - [ ] Read replicas para queries (opcional, futuro)

---

### Documentación API

- [ ] **OpenAPI/Swagger Documentation**
  - [x] Swagger UI automático (incluido con FastAPI)
  - [ ] Ejemplos completos en todos los endpoints
  - [ ] Documentación de códigos de error
  - [ ] Documentación de headers (X-Idempotency-Key, etc.)

- [ ] **README.md Completo**
  - [ ] Instrucciones de instalación paso a paso
  - [ ] Configuración de variables de entorno (.env.example)
  - [ ] Comandos para correr el proyecto
  - [ ] Comandos para correr tests
  - [ ] Guía de contribución

- [ ] **Guías de Integración**
  - [ ] Guía para integrar nuevos suppliers
  - [ ] Guía para agregar nuevos payment gateways
  - [ ] Guía de arquitectura (diagramas C4)

---

## 🟠 PRIORIDAD ALTA (P1)

### Features Core Pendientes

- [ ] **Gestión de Reservas - Features Adicionales**
  - [ ] **Cancelación de Reservas**
    - [ ] Use case: `CancelReservationUseCase`
    - [ ] Endpoint: `DELETE /api/v1/reservations/{code}`
    - [ ] Lógica de reembolso según política
    - [ ] Notificación al supplier
    - [ ] Emisión de evento `ReservationCancelled`

  - [ ] **Modificación de Reservas**
    - [ ] Use case: `UpdateReservationUseCase`
    - [ ] Endpoint: `PATCH /api/v1/reservations/{code}`
    - [ ] Validación de cambios permitidos
    - [ ] Recalcular precios si cambian fechas
    - [ ] Confirmación con supplier

  - [ ] **Extras y Add-ons**
    - [ ] Agregar seguros adicionales
    - [ ] Agregar conductores adicionales (entity `Driver`)
    - [ ] Agregar GPS, sillas de bebé, etc.
    - [ ] Recalcular pricing con extras

- [ ] **Customer Management**
  - [ ] Use case: `CreateCustomerUseCase`
  - [ ] Use case: `GetCustomerUseCase`
  - [ ] Use case: `UpdateCustomerUseCase`
  - [ ] Endpoints completos de customers
  - [ ] Validación de email único
  - [ ] Historial de reservas por customer

- [ ] **Availability - Mejoras**
  - [ ] Búsqueda multi-supplier en paralelo (asyncio.gather)
  - [ ] Cache de resultados de disponibilidad (Redis, TTL: 5 min)
  - [ ] Filtros adicionales (precio, categoría, transmisión, etc.)
  - [ ] Ordenamiento de resultados (precio, rating, etc.)

---

### Integraciones Externas

- [ ] **Suppliers Adicionales**
  - [ ] **Europcar Client**
    - [ ] Implementar `EuropcarClient` heredando de `BaseSupplierClient`
    - [ ] Mapeo de respuestas Europcar a DTOs
    - [ ] Manejo de errores específicos de Europcar
    - [ ] Tests de integración

  - [ ] **Rently Network Client**
    - [ ] Implementar `RentlyNetworkClient`
    - [ ] Integración con API de Rently
    - [ ] Tests de integración

  - [ ] **Budget Client**
    - [ ] Implementar `BudgetClient`
    - [ ] Integración con API de Budget

- [ ] **Email Notifications**
  - [ ] Integración con SendGrid o similar
  - [ ] Template de confirmación de reserva
  - [ ] Template de cancelación
  - [ ] Template de recordatorio (1 día antes del pickup)
  - [ ] Queue de emails con Celery o similar

- [ ] **SMS Notifications**
  - [ ] Integración con Twilio
  - [ ] SMS de confirmación con código de reserva
  - [ ] SMS de recordatorio

- [ ] **Webhooks**
  - [ ] Endpoint para recibir webhooks de Stripe (payment.succeeded, payment.failed)
  - [ ] Validación de firma de Stripe
  - [ ] Procesamiento async de webhooks

---

### Seguridad

- [ ] **Autenticación**
  - [ ] Implementar JWT tokens con `python-jose`
  - [ ] Endpoint: `POST /api/v1/auth/login`
  - [ ] Endpoint: `POST /api/v1/auth/register`
  - [ ] Endpoint: `POST /api/v1/auth/refresh`
  - [ ] Middleware de autenticación
  - [ ] Hash de passwords con `passlib[bcrypt]`

- [ ] **Autorización**
  - [ ] Roles: `customer`, `admin`, `agent`
  - [ ] Permisos por role
  - [ ] Dependency `get_current_user()`
  - [ ] Dependency `require_role(["admin"])`

- [ ] **Rate Limiting**
  - [ ] Implementar rate limiting por IP
  - [ ] Diferentes límites por endpoint
  - [ ] Rate limit más bajo para crear reservas (prevenir abuse)
  - [ ] Usar Redis para contador de requests

- [ ] **Input Validation & Sanitization**
  - [x] Validación con Pydantic (ya implementado)
  - [ ] Sanitización de strings (XSS prevention)
  - [ ] Validación de CORS origins
  - [ ] Content Security Policy headers

---

## 🟡 PRIORIDAD MEDIA (P2)

### DevOps & CI/CD

- [ ] **GitHub Actions**
  - [ ] Workflow de CI para tests
    - [ ] Run tests on push/PR
    - [ ] Upload coverage reports
    - [ ] Fail si cobertura < 80%

  - [ ] Workflow de linting
    - [ ] Run `ruff check`
    - [ ] Run `ruff format --check`
    - [ ] Run `mypy` for type checking

  - [ ] Workflow de build
    - [ ] Build Docker image
    - [ ] Push to Docker Hub/ECR
    - [ ] Tag con versión semántica

- [ ] **Docker**
  - [ ] `Dockerfile` para producción (multi-stage build)
  - [ ] `docker-compose.yml` para desarrollo local
    - [ ] Service: API (FastAPI)
    - [ ] Service: MySQL
    - [ ] Service: Redis
    - [ ] Service: Mailhog (para emails en dev)

  - [ ] `.dockerignore` file
  - [ ] Health checks en containers

- [ ] **Deployment**
  - [ ] Scripts de deploy a staging
  - [ ] Scripts de deploy a producción
  - [ ] Rollback strategy
  - [ ] Blue-green deployment o canary

- [ ] **Infrastructure as Code**
  - [ ] Terraform para AWS/GCP
  - [ ] Kubernetes manifests
  - [ ] Helm charts

---

### Observabilidad

- [ ] **Logging Mejorado**
  - [x] Structlog implementado (básico)
  - [ ] Configurar diferentes niveles por ambiente (DEBUG en dev, INFO en prod)
  - [ ] Logging de requests/responses (middleware)
  - [ ] Logging de queries SQL lentas
  - [ ] Correlación IDs para tracing

- [ ] **Metrics**
  - [ ] Integración con Prometheus
  - [ ] Métricas de negocio
    - [ ] Total de reservas creadas
    - [ ] Total de reservas canceladas
    - [ ] Revenue total
    - [ ] Tasa de conversión
  - [ ] Métricas técnicas
    - [ ] Request rate
    - [ ] Error rate
    - [ ] Response time percentiles (p50, p95, p99)
    - [ ] Database connection pool usage

- [ ] **Distributed Tracing**
  - [ ] Integración con Jaeger o Zipkin
  - [ ] Trace de requests entre servicios
  - [ ] Trace de queries a BD
  - [ ] Trace de llamadas a suppliers externos

- [ ] **Dashboards**
  - [ ] Grafana dashboard con métricas clave
  - [ ] Dashboard de health status
  - [ ] Dashboard de errores (agrupados por tipo)

- [ ] **Alertas**
  - [ ] Alertas de error rate > threshold
  - [ ] Alertas de response time > threshold
  - [ ] Alertas de disponibilidad de BD
  - [ ] Alertas de suppliers down
  - [ ] Integración con PagerDuty/Slack

---

### Performance & Optimization

- [ ] **Caching**
  - [ ] Implementar caching de disponibilidad con Redis (TTL: 5 min)
  - [ ] Cache de datos de suppliers (información estática)
  - [ ] Cache de offices
  - [ ] Cache invalidation strategy

- [ ] **Database Optimization**
  - [ ] Query optimization (usar EXPLAIN)
  - [ ] N+1 queries prevention
  - [ ] Eager loading de relaciones
  - [ ] Database read replicas para queries pesadas

- [ ] **Connection Pooling**
  - [ ] Configurar pool size óptimo para SQLAlchemy
  - [ ] Pool size para Redis
  - [ ] Timeout configuration

- [ ] **Async Everywhere**
  - [ ] Revisar que todo I/O sea async
  - [ ] Usar `asyncio.gather()` para llamadas paralelas
  - [ ] Background tasks con FastAPI BackgroundTasks

- [ ] **API Response Optimization**
  - [ ] Paginación eficiente en list endpoints
  - [ ] Cursor-based pagination para datasets grandes
  - [ ] GraphQL layer (opcional, futuro)

- [ ] **Load Testing**
  - [ ] Load tests con Locust o k6
  - [ ] Establecer baseline de performance
  - [ ] Identificar bottlenecks

---

### Features Avanzados

- [ ] **Search & Filters**
  - [ ] Full-text search en reservas (por customer, código, etc.)
  - [ ] Filtros avanzados en listado de reservas
  - [ ] Elasticsearch integration (opcional)

- [ ] **Reports & Analytics**
  - [ ] Reporte de ventas por periodo
  - [ ] Reporte de reservas por supplier
  - [ ] Reporte de revenue por car category
  - [ ] Export a CSV/Excel

- [ ] **Admin Panel**
  - [ ] Dashboard de admin
  - [ ] Gestión de suppliers
  - [ ] Gestión de offices
  - [ ] Gestión de car categories
  - [ ] Gestión de usuarios/agents

- [ ] **Multi-tenancy**
  - [ ] Soporte para múltiples marcas/tenants
  - [ ] Aislamiento de datos por tenant
  - [ ] Configuración por tenant

- [ ] **Internationalization (i18n)**
  - [ ] Soporte multi-idioma (EN, ES, PT)
  - [ ] Traducción de mensajes de error
  - [ ] Formato de fechas/monedas por locale

---

## 🟢 PRIORIDAD BAJA (P3)

### Nice to Have

- [ ] **Promociones y Descuentos**
  - [ ] Sistema de cupones
  - [ ] Descuentos por volumen
  - [ ] Promociones temporales

- [ ] **Loyalty Program**
  - [ ] Puntos por reserva
  - [ ] Canje de puntos
  - [ ] Tiers de clientes (bronze, silver, gold)

- [ ] **Reviews & Ratings**
  - [ ] Clientes pueden dejar reviews de suppliers
  - [ ] Rating promedio por supplier
  - [ ] Moderation de reviews

- [ ] **Chat Support**
  - [ ] Chat en vivo con soporte
  - [ ] Integración con Intercom o similar
  - [ ] Chatbot básico con FAQs

- [ ] **Mobile App**
  - [ ] API optimizada para mobile
  - [ ] Push notifications
  - [ ] Deep linking

- [ ] **Analytics Avanzado**
  - [ ] Google Analytics integration
  - [ ] Facebook Pixel
  - [ ] Attribution tracking

---

## 📝 Deuda Técnica Identificada

### High Priority Tech Debt

1. **Idempotency Implementation**
   - [ ] Implementar storage de idempotency keys
   - [ ] Implementar check en `CreateReservationUseCase`
   - [ ] TTL para keys (24 horas)

2. **Error Handling Consistency**
   - [ ] Estandarizar formato de error responses
   - [ ] Custom exception classes para todos los casos
   - [ ] Error codes consistentes

3. **Domain Events Processing**
   - [ ] Implementar event bus real (no solo logging)
   - [ ] Workers para procesar eventos del outbox
   - [ ] Retry logic para eventos fallidos

4. **Configuration Management**
   - [ ] Centralizar todas las configs en `settings.py`
   - [ ] Validation de environment variables
   - [ ] Secrets management (AWS Secrets Manager, Vault, etc.)

### Medium Priority Tech Debt

5. **Type Hints Completeness**
   - [x] Type hints en API layer (completado)
   - [ ] Type hints en todos los tests
   - [ ] Mypy en modo estricto sin ignores

6. **Code Comments & Docstrings**
   - [ ] Docstrings en todos los métodos públicos
   - [ ] Docstrings en formato Google Style
   - [ ] Comments en lógica compleja

7. **Logging Standardization**
   - [x] Structlog implementado
   - [ ] Log levels consistentes
   - [ ] Sensitive data masking en logs

### Low Priority Tech Debt

8. **Code Duplication**
   - [ ] Refactor código duplicado en mappers
   - [ ] Helpers comunes para validaciones

9. **Magic Numbers**
   - [ ] Extraer magic numbers a constants
   - [ ] Config file para business rules

---

## 🎯 Roadmap por Sprints

### Sprint 1 (2 semanas) - Testing Foundation
- [ ] Unit tests de Domain Layer
- [ ] Integration tests de Repositories
- [ ] Setup de CI/CD básico
- [ ] Coverage report

### Sprint 2 (2 semanas) - Database & Deployment
- [ ] Migraciones de Alembic
- [ ] Seed data
- [ ] Docker setup
- [ ] Deploy a staging

### Sprint 3 (2 semanas) - Security
- [ ] Autenticación JWT
- [ ] Autorización por roles
- [ ] Rate limiting
- [ ] Security audit

### Sprint 4 (2 semanas) - Features Core
- [ ] Cancelación de reservas
- [ ] Customer management completo
- [ ] Email notifications

### Sprint 5 (2 semanas) - Observability
- [ ] Metrics con Prometheus
- [ ] Dashboards en Grafana
- [ ] Alertas configuradas
- [ ] Distributed tracing

### Sprint 6+ (2 semanas c/u) - Integraciones & Optimización
- [ ] Suppliers adicionales (Europcar, Budget)
- [ ] Performance optimization
- [ ] Caching layer
- [ ] Features avanzados

---

## 📊 Métricas de Éxito

### Testing
- ✅ **Goal**: 80%+ de cobertura en domain y application layers
- ✅ **Goal**: 100% de flujos críticos con E2E tests

### Performance
- ✅ **Goal**: API response time p95 < 200ms
- ✅ **Goal**: Soporte de 1000 req/s con auto-scaling
- ✅ **Goal**: Database query time p95 < 50ms

### Reliability
- ✅ **Goal**: 99.9% uptime (SLA)
- ✅ **Goal**: < 0.1% error rate
- ✅ **Goal**: MTTR (Mean Time To Recovery) < 15 min

### Security
- ✅ **Goal**: Zero critical vulnerabilities
- ✅ **Goal**: Pasar auditoría de seguridad
- ✅ **Goal**: OWASP Top 10 compliance

---

## 🤝 Contribuciones

### Para Contribuir
1. Tomar una tarea de este TODO
2. Crear branch: `feature/nombre-feature` o `fix/nombre-fix`
3. Implementar con tests
4. PR con descripción detallada
5. Code review
6. Merge a main

### Checklist para PRs
- [ ] Código con type hints
- [ ] Tests unitarios agregados
- [ ] Tests de integración (si aplica)
- [ ] Documentación actualizada
- [ ] CHANGELOG.md actualizado
- [ ] Sin warnings de mypy
- [ ] Sin issues de ruff
- [ ] Coverage no disminuye

---

## 📞 Contacto

**Questions?** Contactar a: rafael@mexicocarrental.com

**Project Board**: (Link a Jira/GitHub Projects cuando esté configurado)

---

**Nota**: Este documento es un living document y debe actualizarse constantemente a medida que se completan tareas y se identifican nuevas necesidades.

**Versión**: 1.0.0
**Última Actualización**: 2026-01-08
