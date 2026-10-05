from langgraph.prebuilt import create_react_agent
from app.llm import get_llm
from app.tools.calculator import calculator


def create_analyst():
    llm = get_llm()
    return create_react_agent(
        model=llm,
        tools=[calculator],
        name="analyst",
        prompt=(
            "You are a data analyst. You receive research notes and must extract numeric insights.\n"
            "CRITICAL RULES:\n"
            "1. If research notes contain NO numeric data, respond EXACTLY with: "
            "'NO_NUMERIC_DATA_AVAILABLE - cannot perform analysis.'\n"
            "2. NEVER invent, fabricate, or assume numbers.\n"
            "3. Only analyze numbers that are literally present in the input.\n"
            "4. Use the calculator tool for all arithmetic."
        ),
    )