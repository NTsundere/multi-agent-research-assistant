Multi-Agent Research Assistant

Production-ready мультиагентная система на LangGraph: Supervisor + Researcher + Analyst + Writer. Работает полностью локально через Ollama, без внешних API, без VPN.

Возможности

    Мультиагентная оркестрация через LangGraph Supervisor

    Три специализированных агента: Researcher (web search), Analyst (calculator), Writer (report)

    Tool calling: DuckDuckGo search и калькулятор на numexpr

    Short-term memory через SqliteSaver checkpointer

    Retry-политики и обработка ошибок

    FastAPI API с JSON-логированием

    Docker + docker-compose

    CI/CD через GitHub Actions

    Работает полностью локально (Ollama + qwen2.5:7b)

Архитектура

Пользователь отправляет POST-запрос на /research. FastAPI передаёт его в LangGraph-графа, где Supervisor решает, какой агент должен действовать следующим. Researcher ищет факты в интернете, Analyst считает числа через калькулятор, Writer генерирует финальный Markdown-отчёт. Результаты сохраняются в SQLite для поддержки multi-turn диалогов через thread_id.

Схема графа: START → Supervisor → Researcher или Analyst или Writer → Supervisor → ... → FINISH

Быстрый старт

Требования:

    Python 3.9 или выше

    Ollama (ollama.com/download)

    Модель qwen2.5:7b

Шаг 1. Установи Ollama и модель:

ollama pull qwen2.5:7b

Шаг 2. Установи зависимости:

pip install -r requirements.txt

Шаг 3. Настрой .env:

Скопируй .env.example в .env. По умолчанию там уже стоит OLLAMA_MODEL=qwen2.5:7b.

Шаг 4. Запусти API:

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

Шаг 5. Отправь запрос:

POST на http://localhost:8000/research с JSON-телом: query (что исследовать) и thread_id (для сохранения контекста диалога).

Пример ответа:

final_report содержит Markdown-отчёт. research_notes и analysis содержат промежуточные результаты агентов. thread_id возвращается для продолжения диалога.

Структура проекта

Папка app содержит: main.py (FastAPI эндпоинты), config.py (Pydantic-настройки), llm.py (фабрика Ollama-модели), schemas.py (Pydantic-схемы), logger.py (JSON-логирование).

Папка app/tools содержит: calculator.py (калькулятор на numexpr), web_search.py (поиск через DuckDuckGo).

Папка app/agents содержит: researcher.py, analyst.py, writer.py — три ReAct-агента.

Папка app/graph содержит: state.py (состояние графа), supervisor.py (логика Supervisor), graph.py (сборка StateGraph).

Папка tests содержит тесты инструментов. Папка .github/workflows содержит CI-workflow.

Технологический стек

Оркестрация агентов: LangGraph. LLM: Ollama qwen2.5:7b. API: FastAPI, Uvicorn. Инструменты: duckduckgo-search, numexpr. Память: SQLite через langgraph-checkpoint-sqlite. Логирование: структурированный JSON. Контейнеризация: Docker, docker-compose. CI/CD: GitHub Actions.

Известные ограничения

Модель qwen2.5:7b на CPU работает медленно — один research-запрос занимает 5–15 минут в зависимости от количества шагов. Для ускорения можно использовать GPU (Ollama автоматически подхватит CUDA/ROCm) или уменьшить модель до qwen2.5:3b. Supervisor иногда возвращает FINISH раньше времени — добавлен fallback: если final_report пустой, возвращается analysis.