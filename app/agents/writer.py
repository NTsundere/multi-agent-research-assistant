from langgraph.prebuilt import create_react_agent
from app.llm import get_llm


def create_writer():
    llm = get_llm()
    return create_react_agent(
        model=llm,
        tools=[],
        name="writer",
        prompt=(
            "You are a professional technical writer. Given research and analysis, "
            "produce a clear, well-structured report in Markdown. Include an intro, "
            "key findings, and a conclusion. Do not invent facts."
        ),
    )