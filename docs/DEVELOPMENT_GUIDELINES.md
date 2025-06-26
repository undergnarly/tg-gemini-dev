# Development Guidelines & Best Practices

Этот документ определяет архитектурные принципы, стандарты кодирования и процессы, используемые в этом проекте. Все участники (включая AI-агентов) должны неукоснительно следовать этим правилам.

---

## 3.1 Architectural Philosophy

*   **Ports & Adapters (Hexagonal Architecture)** – Внешние слои (Telegram, FastAPI, CLI-инструменты) зависят *только* от контрактов домена/сервисов, но не наоборот. Это обеспечивает изоляцию бизнес-логики от деталей реализации.
*   **Service Modules** – Каждый сервис находится в `services/<name>/` и предоставляет четкий интерфейс через `service.py`. Инфраструктурный код, специфичный для сервиса, остается внутри его модуля.
*   **Agents as Plugins** – Каждый агент или инструмент является самодостаточным модулем в `agents/`. Регистрация нового агента требует редактирования только `crew_graph.py`.

---

## 3.2 Coding Standards

| Language | Formatter                   | Linter                         | Typing              |
| -------- | --------------------------- | ------------------------------ | ------------------- |
| Python   | **black** (PEP 8, 120 cols) | **ruff** (error, style, isort) | `mypy --strict`     |
| Go       | `go fmt`                    | `golangci-lint`                | native generics     |
| JS/TS    | `eslint` + `prettier`       | eslint‑airbnb                  | full TS strict mode |

*Все CI пайплайны **должны падать** при любой ошибке линтера или типизации.*

---

## 3.3 Dependency Management

*   **Python** – `Poetry` с точными версиями зависимостей (`poetry.lock` должен быть закоммичен).
*   **Go** – `Go modules` с файлом `go.sum`.
*   **JS/TS** – `pnpm` с файлом `pnpm-lock.yaml`.

---

## 3.4 Testing Rules

1.  **Coverage ≥ 90 %** для ключевых модулей (`pytest --cov=services,agents`).
2.  **Структура тестов**:
    *   `tests/unit` – Чистая логика, без ввода-вывода (IO).
    *   `tests/integration` – Взаимодействие с Docker-контейнерами, базами данных, sandbox'ами.
    *   `tests/e2e` – Полный сквозной сценарий от Telegram до получения URL (запускается в CI только по ночам).
3.  **Bug-Fix Workflow**: Каждое исправление бага **обязано** сопровождаться тестом, который падает до исправления и проходит после.

---

## 3.5 Git & CI Workflow

1.  **Conventional Commits**: Все коммиты должны следовать спецификации (`feat: ...`, `fix: ...`, `docs: ...`, `chore: ...` и т.д.).
2.  **CI/CD Flow**:
    *   Разработка ведется в feature-ветках.
    *   Pull Request в `main` запускает автоматические проверки: `lint`, `type-check`, `pytest`, `docker-compose up -d && scripts/quick_demo.sh`.
    *   Если тесты проходят и агент-ревьюер одобряет PR, он автоматически сливается и тегируется (`vMAJOR.MINOR.PATCH`).

---

## 3.6 Modularity & Extensibility

*   **Новый язык?** Создается новый слой в Docker-образе для sandbox, не изменяя существующие слои.
*   **Новый сервис?** Создается через скрипт `scripts/new_service.py <name>`, который автоматически генерирует структуру, тесты и хуки для CI.
*   **Общие утилиты** живут в `libs/common/`. Прямые импорты между сервисами (`services/<name_A>` -> `services/<name_B>`) запрещены. Взаимодействие только через API или брокер сообщений.

---

## 3.7 Observability Conventions

*   **Structured logs (JSON)**: Используем `loguru` для Python и `zap` для Go.
*   **Trace IDs**: Trace ID должен пробрасываться от самого первого запроса (в Telegram) через все внутренние вызовы для сквозного трейсинга.

---

## 3.8 Security Practices

*   **Секреты**: Никогда не коммитить секреты. Использовать переменные окружения через HashiCorp Vault (prod) или SOPS (dev). Все секреты должны ротироваться каждые 90 дней.
*   **Sandbox Egress**: Весь исходящий трафик из sandbox'а запрещен по умолчанию. Разрешения выдаются явно через AppArmor/SELinux профили. Ограничения ресурсов: CPU 2 cores, RAM 4GB, disk 10GB.
*   **SAST/DAST**: `semgrep` для статического анализа + `OWASP ZAP` для динамического анализа в CI.
*   **Dependencies**: Еженедельное сканирование через `Snyk`/`Trivy` на уязвимости.
*   **Rate Limiting**: 10 req/min per user, 100 req/min global. Реализация через Redis + sliding window.

---

## 3.9 Documentation

*   **Публичная документация**: Находится в `docs/` и собирается с помощью `MkDocs` с темой `Material`.
*   **Architecture Decision Records (ADR)**: Каждый сервис может иметь директорию `ADR` для документирования важных архитектурных решений.

---

## 3.10 AI Agent Development Guidelines

### Prompt Engineering
*   **Structured Prompts**: Используйте шаблоны с чёткими разделами (Context, Task, Constraints, Output Format).
*   **Few-shot Examples**: Включайте 2-3 примера желаемого поведения в промпты.
*   **Version Control**: Все промпты хранятся в `agents/prompts/` с версионированием.
*   **Testing**: Каждый промпт должен иметь тесты с expected outputs.

### Agent Design Principles
*   **Single Responsibility**: Каждый агент решает одну конкретную задачу.
*   **Fail Gracefully**: Агенты должны возвращать понятные ошибки, не падать.
*   **Cost Awareness**: Логируйте токены и стоимость каждого вызова LLM.
*   **Timeout Handling**: Максимум 30 секунд на вызов, с retry стратегией.

### LLM Best Practices
*   **Model Selection**: Используйте самую лёгкую модель, достаточную для задачи.
*   **Response Caching**: Кэшируйте идентичные запросы на 24 часа.
*   **Fallback Chain**: Primary model → Secondary model → Cached response → Error.
*   **Rate Limit Handling**: Exponential backoff с jitter.

### Tool Development
*   **Input Validation**: Строгая валидация всех параметров через Pydantic.
*   **Idempotency**: Инструменты должны быть идемпотентными где возможно.
*   **Error Context**: Включайте достаточный контекст для debugging.
*   **Resource Limits**: CPU, memory, время выполнения должны быть ограничены.

---

## 3.11 Debugging & Troubleshooting

### Local Development
*   **Debug Mode**: `DEBUG=true` включает verbose logging и отключает rate limits.
*   **Mock LLMs**: Используйте `MOCK_LLM=true` для тестирования без API calls.
*   **Request Replay**: Сохраняйте failed requests для replay в `data/debug/`.

### Production Debugging
*   **Correlation IDs**: Каждый request имеет уникальный ID для трейсинга.
*   **Debug Headers**: `X-Debug-Mode: true` для получения расширенной информации.
*   **Sampling**: 1% requests логируются с полным payload для анализа.

---

> **Золотое правило:** *Никогда не импортируй между слоями (домен <> инфраструктура) и тесты должны быть зелеными перед слиянием. Расширяй систему, добавляя модули, а не изменяя ядро.* 