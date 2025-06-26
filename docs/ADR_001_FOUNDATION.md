# ADR-001: Foundation Architecture Decisions

**Status:** Accepted  
**Date:** Январь 2025  
**Decision makers:** Principal AI Architect, Team Lead

## Context

Мы создаём автономную платформу для разработки через Telegram с использованием AI-агентов. Необходимо заложить прочный фундамент, который позволит масштабировать систему без переписывания ядра.

## Key Decisions

### 1. Hexagonal Architecture (Ports & Adapters)

**Decision:** Использовать гексагональную архитектуру для изоляции бизнес-логики от внешних зависимостей.

**Rationale:**
- Позволяет легко заменять компоненты (например, Telegram на Discord)
- Упрощает тестирование через mock-адаптеры
- Обеспечивает чёткие границы между слоями

**Consequences:**
- (+) Высокая модульность и тестируемость
- (+) Легко добавлять новые интерфейсы
- (-) Требует дополнительных абстракций
- (-) Может показаться over-engineering для MVP

### 2. Python 3.12 + FastAPI для Core Services

**Decision:** Использовать Python 3.12 с FastAPI для всех основных сервисов.

**Rationale:**
- Отличная поддержка async/await
- Автоматическая генерация OpenAPI документации
- Богатая экосистема для AI/ML
- Pydantic для валидации данных

**Consequences:**
- (+) Быстрая разработка
- (+) Хорошая производительность для I/O-bound задач
- (-) GIL может быть узким местом для CPU-bound операций
- (-) Требует careful memory management для long-running процессов

### 3. Docker + gVisor для Sandbox

**Decision:** Использовать Docker с gVisor runtime для изоляции выполнения кода.

**Rationale:**
- gVisor обеспечивает дополнительный уровень изоляции
- Совместимость с существующими Docker-образами
- Проверенное решение в production

**Alternatives considered:**
- Firecracker: слишком low-level для MVP
- Kubernetes Jobs: избыточно для single-node deployment
- Native containers: недостаточная изоляция

**Consequences:**
- (+) Сильная изоляция без overhead полной виртуализации
- (+) Простота использования через Docker API
- (-) Некоторый performance overhead (~10-15%)
- (-) Не все syscalls поддерживаются

### 4. SQLite → PostgreSQL Migration Path

**Decision:** Начать с SQLite для MVP, но проектировать с учётом миграции на PostgreSQL.

**Rationale:**
- SQLite достаточно для прототипа и разработки
- Нулевая конфигурация для быстрого старта
- SQLAlchemy абстрагирует различия

**Migration strategy:**
- Использовать SQLAlchemy ORM с самого начала
- Избегать SQLite-specific features
- Подготовить миграционные скрипты заранее

**Consequences:**
- (+) Быстрый старт без внешних зависимостей
- (+) Простое тестирование
- (-) Потребуется миграция для production
- (-) Нет concurrent writes в SQLite

### 5. Intent Router as First-Class Citizen

**Decision:** Сделать Intent Router центральным компонентом, а не afterthought.

**Rationale:**
- Критично для UX и эффективности использования ресурсов
- Позволяет оптимизировать простые запросы
- Собирает данные для улучшения классификации

**Implementation:**
- Phase 1: Regex-based rules
- Phase 2: ML-based classification (Claude Haiku)
- Phase 3: Fine-tuned model на собранных данных

**Consequences:**
- (+) Экономия ресурсов на простых задачах
- (+) Лучший UX через быстрые ответы
- (+) Данные для continuous improvement
- (-) Дополнительная сложность в MVP

### 6. Observability from Day One

**Decision:** Встроить observability (logs, metrics, traces) с первого дня.

**Rationale:**
- Критично для отладки distributed system
- Сложно добавить post-factum
- Необходимо для production readiness

**Stack:**
- Structured logging (JSON)
- OpenTelemetry для трейсинга
- Prometheus для метрик
- Grafana для визуализации

**Consequences:**
- (+) Visibility into system behavior
- (+) Быстрая диагностика проблем
- (-) Дополнительная инфраструктура
- (-) Performance overhead (~5%)

### 7. Security by Design

**Decision:** Интегрировать security practices в процесс разработки, а не добавлять позже.

**Measures:**
- SOPS для управления секретами
- AppArmor профили для sandbox
- Rate limiting с первой версии
- Security scanning в CI/CD

**Consequences:**
- (+) Избегаем накопления security debt
- (+) Compliance-ready архитектура
- (-) Замедляет initial development
- (-) Требует security expertise

## Summary

Эти решения формируют основу архитектуры, которая:
1. **Модульная** - легко расширять и изменять
2. **Безопасная** - security встроена, а не добавлена
3. **Наблюдаемая** - полная visibility с первого дня
4. **Pragmatic** - баланс между простотой MVP и будущими потребностями

## References

- [The Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [gVisor Documentation](https://gvisor.dev/)
- [OpenTelemetry Best Practices](https://opentelemetry.io/docs/best-practices/)
- [OWASP Security by Design](https://owasp.org/www-project-secure-coding-practices/) 