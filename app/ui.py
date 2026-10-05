import time
import uuid
import requests
import streamlit as st

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Multi-Agent Research Assistant",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        color: #6b7280;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        font-weight: 600;
        border: none;
        padding: 0.6rem 2rem;
        border-radius: 8px;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.8rem;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1.2rem;
    }
    .status-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .status-online { background: #d1fae5; color: #065f46; }
    .status-offline { background: #fee2e2; color: #991b1b; }
</style>
""", unsafe_allow_html=True)


st.markdown('<div class="main-header">Multi-Agent Research Assistant</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">'
    'Supervisor, Researcher, Analyst и Writer на LangGraph. Локальная LLM через Ollama.'
    '</div>',
    unsafe_allow_html=True,
)


with st.sidebar:
    st.header("Управление")

    try:
        r = requests.get(f"{API_URL}/health", timeout=3)
        health = r.json()
        st.markdown(
            '<span class="status-badge status-online">ONLINE</span>',
            unsafe_allow_html=True,
        )
        st.caption(f"Model: {health.get('model', 'n/a')}")
    except Exception:
        st.markdown(
            '<span class="status-badge status-offline">OFFLINE</span>',
            unsafe_allow_html=True,
        )
        st.error("API недоступен. Запусти:\npython -m uvicorn app.main:app --port 8000")

    st.markdown("---")
    st.subheader("Thread ID")
    st.caption("Одинаковый thread_id сохраняет контекст диалога между запросами.")

    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())[:8]

    thread_id = st.text_input(
        "Идентификатор диалога",
        value=st.session_state.thread_id,
        key="thread_input",
    )
    st.session_state.thread_id = thread_id

    if st.button("Новый диалог", use_container_width=True):
        st.session_state.thread_id = str(uuid.uuid4())[:8]
        st.session_state.history = []
        st.rerun()

    st.markdown("---")
    st.markdown("### Об агентах")
    st.markdown("""
    - Researcher — ищет факты в интернете
    - Analyst — считает и анализирует числа
    - Writer — пишет финальный отчёт
    - Supervisor — решает, кто работает дальше
    """)


if "history" not in st.session_state:
    st.session_state.history = []


tab1, tab2, tab3, tab4 = st.tabs(["Запрос", "История", "Архитектура", "О проекте"])


with tab1:
    st.subheader("Что будем исследовать?")

    with st.form("research_form"):
        query = st.text_area(
            "Вопрос",
            placeholder="Например: What are the top 3 AI agent frameworks in 2026 and their key differences?",
            height=100,
        )
        col1, col2 = st.columns([1, 4])
        with col1:
            submit = st.form_submit_button("Запустить исследование", use_container_width=True)

    if submit:
        if not query.strip():
            st.warning("Введи вопрос.")
        else:
            st.markdown("### Работа агентов")
            progress_placeholder = st.empty()

            with progress_placeholder.container():
                st.info("Supervisor определяет первого агента...")

            with st.spinner("Multi-agent pipeline работает. Это может занять несколько минут."):
                t0 = time.time()
                try:
                    response = requests.post(
                        f"{API_URL}/research",
                        json={"query": query, "thread_id": st.session_state.thread_id},
                        timeout=3600,
                    )
                    response.raise_for_status()
                    result = response.json()
                    elapsed = time.time() - t0

                    progress_placeholder.empty()
                    st.success(f"Готово за {elapsed:.0f} секунд")

                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Время", f"{elapsed:.0f} с")
                    c2.metric("Thread ID", result.get("thread_id", "-"))
                    c3.metric("Длина отчёта", f"{len(result.get('final_report', ''))} симв.")
                    c4.metric("Источников", "web + calc")

                    st.markdown("---")

                    st.markdown("### Финальный отчёт")
                    with st.container(border=True):
                        st.markdown(result.get("final_report", "-"))

                    with st.expander("Research Notes (Researcher)"):
                        st.markdown(result.get("research_notes", "-"))

                    with st.expander("Analysis (Analyst)"):
                        st.markdown(result.get("analysis", "-"))

                    report_md = result.get("final_report", "")
                    st.download_button(
                        "Скачать отчёт (Markdown)",
                        report_md,
                        file_name=f"report_{st.session_state.thread_id}.md",
                        mime="text/markdown",
                    )

                    st.session_state.history.append({
                        "query": query,
                        "result": result,
                        "elapsed": elapsed,
                        "time": time.strftime("%H:%M:%S"),
                    })

                except requests.exceptions.Timeout:
                    progress_placeholder.empty()
                    st.error("Таймаут. Локальная модель на CPU обрабатывает долго.")
                except Exception as e:
                    progress_placeholder.empty()
                    st.error(f"Ошибка: {e}")


with tab2:
    st.subheader("История запросов")

    if not st.session_state.history:
        st.info("Пока пусто. Запусти первый запрос во вкладке Запрос.")
    else:
        for i, item in enumerate(reversed(st.session_state.history), 1):
            with st.expander(
                f"{i}. {item['query'][:80]}... "
                f"({item['time']}, {item['elapsed']:.0f} с)"
            ):
                st.markdown("**Ответ:**")
                st.markdown(item["result"].get("final_report", "-"))

                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    st.caption("Research Notes")
                    st.text(item["result"].get("research_notes", "")[:500] + "...")
                with col2:
                    st.caption("Analysis")
                    st.text(item["result"].get("analysis", "")[:500] + "...")

        if st.button("Очистить историю"):
            st.session_state.history = []
            st.rerun()


with tab3:
    st.subheader("Как это работает")

    st.markdown("### Граф агентов")

    st.code(
        """
        START
          |
          v
        SUPERVISOR  <----------------+
          |                          |
    +-----+-----+                    |
    |     |     |                    |
    v     v     v                    |
  RESEAR ANALY WRITER                |
  CHER   ST                          |
    |     |     |                    |
    +-----+-----+--------------------+
                |
                v
               END
        """,
        language="text",
    )

    st.markdown("### Компоненты")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Агенты:**

        - Researcher — web search через DuckDuckGo
        - Analyst — вычисления через numexpr
        - Writer — генерация Markdown-отчёта

        **Оркестрация:**

        - Supervisor — LangGraph state machine
        - Детерминированный выбор следующего агента
        - Fallback при провале поиска
        """)

    with col2:
        st.markdown("""
        **Память:**

        - SQLite через SqliteSaver
        - Один thread_id = один диалог
        - Multi-turn conversations

        **Стек:**

        - LangGraph 0.2.x
        - Ollama + qwen2.5:7b
        - FastAPI + Uvicorn
        - Streamlit UI
        """)

    st.markdown("### Endpoints API")
    st.markdown("""
| Метод | Путь | Описание |
|-------|------|----------|
| GET | /health | Проверка статуса |
| POST | /research | Запуск исследования |
""")

    st.markdown("**Пример запроса:**")
    st.code(
        'curl -X POST http://localhost:8000/research '
        '-H "Content-Type: application/json" '
        '-d \'{"query": "What are the top AI agent frameworks?", "thread_id": "abc123"}\'',
        language="bash",
    )


with tab4:
    st.subheader("О проекте")
    st.caption("Подробности о технических решениях, ограничениях и компромиссах.")

    with st.expander("Почему Ollama, а не Gemini, Groq, OpenAI или OpenRouter"):
        st.markdown("""
Проект изначально разрабатывался с прицелом на облачные LLM-провайдеры. В процессе работы были
протестированы Gemini API, Groq API и OpenRouter. Каждый из них упёрся в ограничения, которые
делают их непригодными для воспроизводимого демонстрационного проекта.

**Gemini API.** Бесплатный тариф даёт 20 запросов в день на модель. Мультиагентный пайплайн
тратит минимум четыре вызова на один запрос пользователя (supervisor, researcher, analyst,
writer), плюс RAGAS-оценка добавляет ещё десять. Дневной лимит исчерпывается за два запроса.
Дополнительно модели Gemini 3.x требуют передачи thought_signature между шагами tool calling,
а текущая версия библиотеки langchain-google-genai для Python 3.9 не умеет это делать. Обновление
библиотеки требует Python 3.10 или выше, что несовместимо с текущим окружением.

**Groq API.** Ключи Groq работают только через VPN из ряда регионов. Требуются модели,
актуальные на текущий момент, потому что устаревшие версии отключают для бесплатных аккаунтов.
При тестировании был получен 403 Forbidden на уровне защиты Cloudflare, что не решается на
стороне кода.

**OpenAI и Anthropic.** Требуют привязки банковской карты и оплаты за токены. Не подходят
для проекта, который должен запускаться у любого пользователя без затрат.

**OpenRouter.** Агрегатор, работающий через VPN. Бесплатные модели имеют ограничения по
количеству запросов в минуту, что несовместимо с многошаговыми агентами.

**Ollama.** Локальный инференс. Работает без интернета после загрузки модели, без API-ключей,
без лимитов и без региональных блокировок. Единственный минус — скорость. На CPU модель
qwen2.5:7b обрабатывает один запрос от 30 секунд до 3 минут в зависимости от длины контекста.
""")

    with st.expander("Почему запрос может выполняться долго"):
        st.markdown("""
Время обработки одного запроса пользователя складывается из нескольких факторов.

**Количество вызовов LLM.** Мультиагентный пайплайн делает минимум четыре вызова: supervisor
определяет первого агента, researcher ищет информацию, supervisor запускает analyst, supervisor
запускает writer. Каждый вызов — отдельный запрос к модели. Если researcher делает несколько
итераций tool calling, количество вызовов растёт.

**Локальный инференс на CPU.** Ollama без GPU выполняет инференс qwen2.5:7b на процессоре.
Скорость генерации на CPU без аппаратного ускорения составляет порядка 5-15 токенов в секунду.
Развёрнутый ответ на 500 токенов занимает 30-90 секунд. Четыре вызова — это уже 2-6 минут.

**Tool calling.** Researcher выполняет web search через DuckDuckGo. Скорость ответа поисковика
варьируется от 0.5 до 5 секунд. Если запрос требует нескольких итераций поиска, время растёт.

**Контекст диалога.** Каждый следующий запрос в том же thread_id накапливает историю сообщений.
Модель обрабатывает весь контекст, что увеличивает время генерации. Для длинных диалогов
рекомендуется начинать новый thread.

**Ожидаемое время.** Простой вопрос — 30-60 секунд. Вопрос, требующий поиска в интернете —
1-3 минуты. Сложный многошаговый запрос с несколькими итерациями researcher — до 5 минут.

**Как ускорить.** Установить GPU и настроить Ollama на использование CUDA или ROCm. Уменьшить
модель до qwen2.5:3b (компромисс по качеству). Уменьшить max_tokens в конфигурации LLM.
""")

    with st.expander("Почему web search может не работать"):
        st.markdown("""
Researcher использует библиотеку ddgs, которая обращается к публичным эндпоинтам DuckDuckGo
без API-ключа. Это создаёт несколько проблем.

**Rate limiting.** DuckDuckGo ограничивает количество запросов с одного IP-адреса. При частых
запросах в течение короткого времени сервис начинает возвращать ошибку или пустой результат.
Временное решение — подождать 5-10 минут.

**Изменение HTML-структуры.** Библиотека парсит HTML-ответы поисковика. Если DuckDuckGo меняет
разметку, парсер перестаёт находить результаты. Библиотека обновляется, но с задержкой.

**Отсутствие результатов.** По узкоспециализированным, новым или очень специфичным запросам
DuckDuckGo может вернуть пустой список даже при работающем соединении. Это не ошибка, а
особенность поисковика.

**Устаревшая версия библиотеки.** Старая библиотека duckduckgo_search часто возвращает пустые
результаты. Новая ddgs работает стабильнее и не требует VPN. Если после установки ddgs поиск
всё равно не работает, проверьте версию: pip show ddgs.

**Как система обрабатывает это.** Researcher получает от web_search либо результаты, либо
сообщение об ошибке. При ошибке researcher возвращает строку SEARCH_FAILED. Supervisor видит
это и останавливает пайплайн, не запуская analyst и writer. Пользователь видит честное
сообщение о том, что информация не найдена, без выдуманных данных.

**Альтернативы.** Для production-сценариев используются Tavily API, SerpAPI или Brave Search API.
Они платные, но работают надёжнее и поддерживают структурированные ответы. Замена одного модуля
app/tools/web_search.py на другой API — задача на 20 строк кода.
""")
        
    with st.expander("Как VPN влияет на работу проекта"):
        st.markdown("""
VPN меняет исходящий IP-адрес. Для данного проекта это **не требуется**, но может помочь в
отдельных случаях.

**Web search через ddgs.** Библиотека ddgs работает из большинства регионов без VPN, включая
Беларусь. VPN не нужен для поиска. Более того, некоторые VPN-серверы уже заблокированы
DuckDuckGo из-за массового использования, и включение VPN может сделать поиск хуже, а не лучше.

**Ollama.** Локальный инференс. Не делает внешних запросов после загрузки модели. VPN не влияет
ни на скорость, ни на качество ответов.

**SQLite и FastAPI.** Локальные компоненты. VPN не влияет.

**Streamlit UI.** Работает в браузере на localhost. VPN не влияет.

**Когда VPN может помочь.** Если ddgs возвращает пустые результаты на протяжении длительного
времени из-за rate limiting по IP-адресу. В этом случае смена IP через VPN даст новый лимит
запросов. Также VPN помогает, если провайдер блокирует сам эндпоинт DuckDuckGo на сетевом уровне.

**Когда VPN мешает.** Некоторые VPN-серверы (особенно бесплатные и перегруженные) уже
заблокированы DuckDuckGo. В этом случае поиск будет работать хуже, чем без VPN. Если поиск
перестал работать после включения VPN — попробуйте выключить его и повторить запрос.

**Проверка.** Чтобы убедиться, что проблема в VPN, а не в библиотеке, выполните в PowerShell
команду проверки соединения с DuckDuckGo. Если с VPN возвращается ошибка, а без VPN — результат,
значит проблема в VPN-сервере, а не в проекте.
""")

    with st.expander("Архитектурные решения и компромиссы"):
        st.markdown("""
**Детерминированный supervisor вместо LLM-based.** Изначально supervisor использовал LLM для
принятия решения о следующем агенте. Qwen 2.5:7b часто отвечал неверно: пропускал шаги,
возвращал некорректные имена агентов, добавлял лишний текст перед JSON. Замена на детерминированную
логику (если нет research — запустить researcher, если нет analysis — запустить analyst, и так
далее) устранила проблему. Компромисс: система теряет гибкость в выборе порядка агентов, но
получает надёжность и предсказуемость.

**SqliteSaver вместо AsyncSqliteSaver.** AsyncSqliteSaver требует асинхронного графа, но
langgraph 0.2.x с SqliteSaver работает только в синхронном режиме. Решение: FastAPI-эндпоинт
вызывает граф через run_in_threadpool, что позволяет сохранить асинхронный HTTP-сервер и
синхронную логику графа.

**Пустые поля при каждом запросе.** SQLite хранит состояние диалога по thread_id. Без сброса
полей research_notes, analysis и final_report второй запрос в том же thread_id возвращал бы
старый результат. Решение: явная передача пустых значений при каждом вызове графа. Компромисс:
контекст диалога через messages сохраняется, а результаты агентов — нет.

**Отсутствие параллелизма между агентами.** Агенты выполняются последовательно, хотя могли бы
работать параллельно. Причина: Ollama на CPU обрабатывает один запрос за раз, параллельные
вызовы только увеличивают общее время. На GPU имеет смысл добавить параллелизм через
Send API LangGraph.

**Ограничение на длину контекста.** qwen2.5:7b имеет контекстное окно 32K токенов. При длинных
диалогах контекст может переполниться. Решение: обрезка истории через trim_messages или
суммаризация старых сообщений. В текущей версии не реализовано.

**Обработка ошибок.** Каждый узел графа не имеет собственного retry-механизма. Ошибка в
researcher приводит к остановке всего пайплайна. Решение: RetryPolicy на уровне узлов
LangGraph. В текущей версии не реализовано из-за несовместимости API.
""")

    with st.expander("Что можно улучшить в следующих версиях"):
        st.markdown("""
**Заменить web search на Tavily.** Tavily возвращает структурированные ответы с указанием
релевантности и не блокирует регионы. Бесплатный тариф — 1000 запросов в месяц.

**Добавить параллельный запуск агентов.** LangGraph поддерживает параллельное выполнение узлов
через Send API. На GPU это даёт ускорение в 2-3 раза.

**Добавить мониторинг через Langfuse.** Langfuse собирает трейсы выполнения графа, время
каждого узла, стоимость вызовов LLM. Интеграция — 10 строк кода.

**Добавить RAG для источников.** Researcher может сохранять найденные источники в векторную
базу, а writer — использовать retrieval для цитирования.

**Добавить streaming ответа.** FastAPI поддерживает Server-Sent Events. Пользователь видит
промежуточные результаты агентов в реальном времени.

**Поддержка нескольких LLM-провайдеров.** Абстракция на уровне app/llm.py позволяет
переключаться между Ollama, OpenAI, Anthropic через переменные окружения.
""")

    with st.expander("Как воспроизвести проект локально"):
        st.markdown("""
**Требования.** Python 3.9 или выше. Ollama с загруженной моделью qwen2.5:7b. 8 ГБ оперативной
памяти минимум, рекомендуется 16 ГБ.

**Шаг 1. Установить Ollama.** Скачать с ollama.com/download, установить, выполнить команду
ollama pull qwen2.5:7b в терминале. Загрузка занимает 5-10 минут в зависимости от скорости
интернета.

**Шаг 2. Клонировать репозиторий.** git clone, перейти в директорию, установить зависимости
через pip install -r requirements.txt.

**Шаг 3. Запустить API.** Выполнить python -m uvicorn app.main:app --host 0.0.0.0 --port 8000.

**Шаг 4. Запустить UI.** В отдельном терминале выполнить python -m streamlit run app.ui.

**Шаг 5. Проверить.** Открыть http://localhost:8501, ввести вопрос, нажать кнопку запуска.
Первый запрос занимает больше времени, потому что Ollama загружает модель в память.
""")

    st.markdown("---")
    st.caption(
        "Проект распространяется под лицензией MIT. "
        "Исходный код доступен на github.com/NTsundere/multi-agent-research-assistant"
    )