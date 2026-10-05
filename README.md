Multi-Agent Research Assistant

Production-ready мультиагентная система на LangGraph: Supervisor + Researcher + Analyst + Writer. Работает полностью локально через Ollama, без внешних API.
Возможности

    Мультиагентная оркестрация через LangGraph

    Детерминированный Supervisor с fallback-стратегиями

    Три специализированных агента: Researcher (web search), Analyst (calculator), Writer (report)

    Tool calling: ddgs (DuckDuckGo) и калькулятор на numexpr

    Short-term memory через SqliteSaver checkpointer

    Обработка ошибок: при провале поиска пайплайн останавливается, не генерируя выдуманные данные

    FastAPI API с JSON-логированием

    Streamlit UI с интерактивной документацией

    Docker + docker-compose

    CI/CD через GitHub Actions

    Полностью локальный инференс через Ollama (qwen2.5:7b)

Архитектура

Пользователь отправляет POST-запрос на /research. FastAPI передаёт его в LangGraph-граф. Supervisor детерминированно определяет следующего агента на основе текущего состояния: если нет research — запускается Researcher, если нет analysis — Analyst, если нет final_report — Writer. Researcher ищет факты в интернете через ddgs, Analyst считает числа через numexpr, Writer генерирует Markdown-отчёт. Результаты сохраняются в SQLite для поддержки multi-turn диалогов через thread_id.

Схема графа:

START -> Supervisor -> Researcher -> Supervisor
                     -> Analyst    -> Supervisor
                     -> Writer     -> Supervisor -> FINISH

Обработка ошибок

Каждый агент имеет жёсткие guardrails:

    Researcher — если поиск не дал результатов, возвращает SEARCH_FAILED. Supervisor видит это и останавливает пайплайн.

    Analyst — если в research notes нет числовых данных, возвращает NO_NUMERIC_DATA_AVAILABLE. Не выдумывает числа.

    Writer — если analysis пуст или содержит NO_NUMERIC_DATA_AVAILABLE, игнорирует его. Не создаёт фейковые отчёты.

Это защищает от галлюцинаций: система честно сообщает "информация не найдена" вместо генерации выдуманных данных.
Быстрый старт
Требования

    Python 3.9 или выше

    Ollama (ollama.com/download)

    Модель qwen2.5:7b (4.7 GB)

Установи Ollama и модель
ollama pull qwen2.5:7b

Установи зависимости
pip install -r requirements.txt

Настрой .env
Copy-Item .env.example .env

По умолчанию стоит OLLAMA_MODEL=qwen2.5:7b.
Запусти API
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

Запусти Streamlit UI
В отдельном терминале:
python -m streamlit run app/ui.py

Открой в браузере http://localhost:8501
Streamlit UI

Веб-интерфейс с четырьмя вкладками:

    Запрос — форма ввода вопроса, прогресс выполнения, финальный отчёт, промежуточные результаты агентов, кнопка скачивания отчёта в Markdown

    История — все запросы текущей сессии с возможностью раскрыть детали

    Архитектура — схема графа агентов, компоненты системы, endpoints API

    О проекте — подробная документация: почему Ollama, почему запрос долгий, как работает fallback, ограничения, как воспроизвести проект

В сайдбаре: статус API (online/offline), текущая модель, Thread ID, кнопка нового диалога.
API
Health check
text

curl.exe http://localhost:8000/health

Ответ: {"status": "healthy", "model": "qwen2.5:7b"}
Research
curl.exe -X POST http://localhost:8000/research ^
  -H "Content-Type: application/json" ^
  -d "{\"query\": \"What are the top AI agent frameworks?\", \"thread_id\": \"abc123\"}"

Ответ содержит final_report (Markdown-отчёт), research_notes (заметки Researcher), analysis (анализ Analyst), thread_id.

Технологический стек
Слой	Технология
Оркестрация	LangGraph 0.2.x
LLM	Ollama + qwen2.5:7b
API	FastAPI, Uvicorn
UI	Streamlit
Инструменты	ddgs, numexpr
Память	SQLite через langgraph-checkpoint-sqlite
Логирование	JSON
Контейнеризация	Docker, docker-compose
CI/CD	GitHub Actions
Известные ограничения

Скорость. qwen2.5:7b на CPU обрабатывает запрос от 30 секунд до 5 минут в зависимости от количества шагов агента. Для ускорения: GPU (Ollama подхватит CUDA/ROCm) или уменьшение модели до qwen2.5:3b.

Контекстное окно. 32K токенов. При длинных диалогах контекст может переполниться. Обрезка истории через trim_messages не реализована.

Параллелизм. Агенты выполняются последовательно. На CPU это оправдано — параллельные вызовы только увеличивают общее время. На GPU имеет смысл добавить параллелизм через Send API LangGraph.

Retry-политики. Каждый узел графа не имеет собственного retry-механизма. Ошибка в одном агенте приводит к остановке пайплайна. Решение отложено из-за несовместимости API LangGraph 0.2.x с RetryPolicy.

Rate limiting ddgs. DuckDuckGo ограничивает количество запросов с одного IP. При частых запросах поиск может временно перестать возвращать результаты. Подождать 5-10 минут или сменить IP.
Что можно улучшить

    Заменить ddgs на Tavily API или SerpAPI (структурированные ответы, нет rate limiting)

    Добавить мониторинг через Langfuse (трейсы выполнения графа, стоимость вызовов)

    Добавить параллельный запуск агентов на GPU через Send API

    Добавить streaming ответа через Server-Sent Events

    Добавить RAG для источников (сохранение найденного в векторную базу)

    Поддержка нескольких LLM-провайдеров через абстракцию app/llm.py