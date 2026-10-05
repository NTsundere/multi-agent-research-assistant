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
            "You are a researcher. Use web_search to find facts and cite sources.\n"
            "CRITICAL RULES:\n"
            "1. If web_search returns 'Search failed' or 'No results', "
            "respond EXACTLY with: 'SEARCH_FAILED - could not retrieve information.'\n"
            "2. Do not invent facts.\n"
            "3. Always include source URLs when available."
        ),
    )