# Project Plan: Autonomous Telegram-Driven Dev Platform

Этот документ является "живым" таск-трекером для проекта. Используйте `- [x]` для обозначения выполненных задач.

---

## Phase 0: Foundation & Infrastructure (The Bedrock)

*Цель: Создать прочный фундамент для разработки. Настроить все инструменты, CI/CD и структуру проекта. Кода для бизнес-логики на этом этапе не будет.*

- [ ] **1. Project Scaffolding**
    - [ ] Создать структуру директорий (`infrastructure/`, `services/`, `agents/`, и т.д.).
    - [ ] Инициализировать Git-репозиторий.
    - [ ] Создать `README.md` (первоначальная версия).
    - [ ] Создать `.gitignore`, учитывающий Python, Go, Node.js и системные файлы.
    - [ ] Создать данный файл `PROJECT_PLAN.md`.
    - [ ] Создать `DEVELOPMENT_GUIDELINES.md`.
    - [ ] Создать `TECHNICAL_SPEC.md`.

- [ ] **2. Development Environment**
    - [ ] Инициализировать `poetry` для управления зависимостями Python (`pyproject.toml`).
    - [ ] Добавить и настроить `black`, `ruff`, `mypy`.
    - [ ] Создать `Makefile` с командами: `install`, `lint`, `test`, `type-check`, `run`.

- [ ] **3. Dockerization**
    - [ ] Создать `docker-compose.yml` для локальной разработки.
    - [ ] Добавить сервисы: `postgres` (с `pgvector`), `redis`.
    - [ ] Добавить сервисы для наблюдаемости: `loki`, `prometheus`, `grafana`.
    - [ ] Подготовить базовый `Dockerfile` для будущих Python-сервисов.

- [ ] **4. CI/CD Pipeline**
    - [ ] Создать workflow для GitHub Actions (`.github/workflows/ci.yml`).
    - [ ] Настроить шаги: checkout, setup python, install dependencies.
    - [ ] Добавить шаги для `lint`, `type-check`, `test` (пока без реальных тестов).
    - [ ] Добавить security scanning (Trivy для Docker, Semgrep для кода).
    - [ ] Настроить запуск CI на каждый push в `main` и на pull request'ы.

- [ ] **5. Security Foundation**
    - [ ] Создать `.env.example` с описанием всех переменных.
    - [ ] Настроить SOPS для локальной разработки.
    - [ ] Создать базовые AppArmor профили для sandbox.
    - [ ] Добавить pre-commit hooks для security checks.

---

## Phase 1: MVP (The "Hello, World!" E2E Flow)

*Цель: Реализовать минимальный сквозной сценарий: запрос -> обработка в sandbox -> получение URL. Доказать, что основная идея работает.*

- [ ] **1. API Gateway Service**
    - [ ] Создать сервис в `services/api_gateway/` на FastAPI.
    - [ ] Реализовать эндпоинт `POST /tasks` для приема задач.
    - [ ] Реализовать эндпоинт `GET /tasks/{id}/stream` (WebSocket) для стриминга прогресса.
    - [ ] Интегрировать с Redis Streams для публикации задач в очередь.
    - [ ] Добавить сервис в `docker-compose.yml`.

- [ ] **2. Worker Service & Sandbox Execution**
    - [ ] Создать базовый сервис-worker в `services/worker/`.
    - [ ] Настроить прослушивание очереди задач из Redis.
    - [ ] Интегрировать E2B SDK.
    - [ ] Реализовать логику: запуск sandbox -> выполнение команды (`echo "Hello from CrewAI" > index.html && python -m http.server 8000`) -> получение URL.
    - [ ] Добавить сервис в `docker-compose.yml`.

- [ ] **3. Demo & Testing**
    - [ ] Создать скрипт `scripts/quick_demo.sh` для демонстрации E2E-потока.
    - [ ] Написать интеграционный тест (`tests/integration/test_mvp.py`), который запускает `quick_demo.sh` и проверяет результат.
    - [ ] Обновить CI-пайплайн для запуска `docker-compose` и интеграционного теста.

- [ ] **4. Documentation**
    - [ ] Заполнить `README.md`: как запустить проект, переменные окружения, архитектура MVP.

---

## Phase 2: Intent Router & Smart Dispatching

*Цель: Научить систему понимать намерения пользователя и выбирать оптимальный путь выполнения, чтобы не задействовать тяжелый пайплайн для простых задач.*

- [ ] **1. Intent Router Agent**
    - [ ] Разработать агент для классификации запросов (простая команда vs. сложная задача).
    - [ ] Интегрировать его в `worker` как первую точку входа.
- [ ] **2. Lightweight Shell-Agent**
    - [ ] Создать обертку вокруг Open Interpreter для прямого выполнения shell-команд.
    - [ ] Обеспечить передачу контекста (история, текущая директория).
- [ ] **3. Answer Synthesizer Agent**
    - [ ] Разработать агент для сбора и обобщения результатов.
    - [ ] Реализовать формирование структурированного ответа (статус, шаги, результат).
- [ ] **4. Testing**
    - [ ] Написать интеграционные тесты для обеих веток маршрутизации.

---

## Phase 3: Multi-Agent Brain (CrewAI Integration)

*Цель: Заменить простую логику worker'а на полноценную систему с несколькими агентами CrewAI.*

- [ ] **1. CrewAI Scaffolding**
    - [ ] Структурировать `agents/` с разделением на роли (Planner, Coder, etc.).
    - [ ] Создать `crew_graph.py` для определения состава и взаимодействия агентов.
    - [ ] Определить базовые инструменты для агентов в `agents/tools/`.

- [ ] **2. Agent Implementation**
    - [ ] Реализовать агента `Planner`.
    - [ ] Реализовать агента `Coder` с инструментом для редактирования файлов.
    - [ ] Реализовать агента `Executor` с инструментом для выполнения команд в shell.

- [ ] **3. Integration with Worker**
    - [ ] Подключить Dev-пайплайн (CrewAI) как "сложную" ветку в `Intent Router`.
    - [ ] Настроить передачу контекста (задача от пользователя) в CrewAI.
    - [ ] Настроить стриминг логов выполнения CrewAI через WebSocket API Gateway в `Answer Synthesizer`.

---

## Phase 4: Knowledge Base & Persistence (RAG)

*Цель: Дать агентам "память" и возможность обучаться на основе предыдущих запусков.*

- [ ] **1. RAG Tool**
    - [ ] Создать `agents/tools/rag.py`.
    - [ ] Реализовать функции для сохранения и извлечения информации из `PostgreSQL + pgvector`.
    - [ ] Подключить этот инструмент к агентам (в первую очередь к `Planner` и `Coder`).

- [ ] **2. Data Persistence**
    - [ ] Настроить сохранение диалогов, успешных решений и фрагментов кода в базу данных.
    - [ ] Реализовать логику пополнения RAG-базы после успешного выполнения задачи.

---

## Phase 5: Full Telegram Integration

*Цель: Подключить Telegram-бот как основной пользовательский интерфейс.*

- [ ] **1. Telegram Bot Service**
    - [ ] Создать сервис в `services/telegram_bot/` на `python-telegram-bot`.
    - [ ] Реализовать обработку команд (`/start`, `/new_task`).
    - [ ] Настроить аутентификацию (Telegram ID + JWT) при общении с API Gateway.
    - [ ] Интегрировать с API Gateway: отправка задачи и получение стрима обновлений.

- [ ] **2. User Experience**
    - [ ] Реализовать стриминг прогресса выполнения задачи в чат Telegram.
    - [ ] Отправка финального URL или результата в чат. 