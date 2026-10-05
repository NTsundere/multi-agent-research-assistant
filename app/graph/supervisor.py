from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.llm import get_llm
import re


SUPERVISOR_PROMPT = """You are a team supervisor managing three agents:
- researcher: finds facts, statistics, and current information via web search
- analyst: analyzes numbers, computes metrics, and extracts insights
- writer: produces the final Markdown report

Given the conversation, decide which agent should act next.

Reply with EXACTLY ONE WORD from this list: researcher, analyst, writer, or FINISH.

Rules:
- If no research yet -> researcher
- If research exists but no analysis -> analyst
- If analysis exists but no report -> writer
- If final report is written -> FINISH

Your answer:"""


def _parse_decision(text: str) -> str:
    """Ищем одно из ключевых слов в ответе модели."""
    text_lower = text.lower()
    for word in ["researcher", "analyst", "writer", "finish"]:
        if word in text_lower:
            return word.capitalize() if word == "finish" else word
    return "FINISH"


def supervisor_node(state):
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", SUPERVISOR_PROMPT),
        MessagesPlaceholder(variable_name="messages"),
    ])
    chain = prompt | llm
    result = chain.invoke({"messages": state["messages"]})
    decision = _parse_decision(result.content)
    return {"next_agent": decision}