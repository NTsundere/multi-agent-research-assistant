from langgraph.prebuilt import create_react_agent
from app.llm import get_llm
from app.tools.web_search import web_search
from app.tools.calculator import calculator


def create_researcher():
    llm = get_llm()
    return create_react_agent(
        model=llm,
        tools=[web_search, calculator],
        name="researcher",
        prompt=(
            "You are a world-class researcher. Your job is to find facts, statistics, "
            "and up-to-date information using web_search. Use calculator for any numeric analysis. "
            "Return concise findings with sources."
        ),
    )