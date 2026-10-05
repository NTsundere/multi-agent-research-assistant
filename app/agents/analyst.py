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
            "You are a data analyst. Given raw findings, extract insights, "
            "compute comparisons, growth rates, and percentages using the calculator. "
            "Return structured analysis with numbers."
        ),
    )