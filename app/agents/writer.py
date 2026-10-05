from langgraph.prebuilt import create_react_agent
from app.llm import get_llm


def create_writer():
    llm = get_llm()
    return create_react_agent(
        model=llm,
        tools=[],
        name="writer",
        prompt=(
            "You are a technical writer. Produce a Markdown report ONLY from the given research and analysis.\n"
            "CRITICAL RULES:\n"
            "1. If analysis contains 'NO_NUMERIC_DATA_AVAILABLE', ignore the analysis entirely.\n"
            "2. If research notes say the info was NOT FOUND, write: "
            "'The requested information could not be verified from available sources.'\n"
            "3. NEVER invent facts, numbers, or reports.\n"
            "4. If you don't have enough data, say so explicitly."
        ),
    )