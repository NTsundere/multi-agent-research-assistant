from app.logger import setup_logger

logger = setup_logger(__name__)


def supervisor_node(state):
    """
    Детерминированный supervisor.
    Запускает агентов в фиксированном порядке: researcher -> analyst -> writer -> FINISH.
    Это надёжнее, чем LLM-решение, потому что Qwen 2.5:7b часто выдаёт неверные ответы.
    """
    has_research = bool(state.get("research_notes", "").strip())
    has_analysis = bool(state.get("analysis", "").strip())
    has_report = bool(state.get("final_report", "").strip())

    if not has_research:
        logger.info("Supervisor decision: -> researcher")
        return {"next_agent": "researcher"}

    if not has_analysis:
        logger.info("Supervisor decision: -> analyst")
        return {"next_agent": "analyst"}

    if not has_report:
        logger.info("Supervisor decision: -> writer")
        return {"next_agent": "writer"}

    logger.info("Supervisor decision: -> FINISH")
    return {"next_agent": "FINISH"}