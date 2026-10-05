import os
import sqlite3
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from app.graph.state import ResearchState
from app.graph.supervisor import supervisor_node
from app.agents.researcher import create_researcher
from app.agents.analyst import create_analyst
from app.agents.writer import create_writer
from app.config import settings


def build_graph():
    os.makedirs(os.path.dirname(settings.sqlite_db_path), exist_ok=True)

    # Создаём постоянное подключение к SQLite (живёт всё время работы приложения)
    conn = sqlite3.connect(settings.sqlite_db_path, check_same_thread=False)
    checkpointer = SqliteSaver(conn)

    researcher = create_researcher()
    analyst = create_analyst()
    writer = create_writer()

    def research_node(state):
        result = researcher.invoke({"messages": state["messages"]})
        return {
            "messages": result["messages"],
            "research_notes": result["messages"][-1].content,
        }

    def analyst_node(state):
        prompt = f"Analyze these findings:\n{state.get('research_notes', '')}"
        result = analyst.invoke({"messages": [{"role": "user", "content": prompt}]})
        return {
            "messages": result["messages"],
            "analysis": result["messages"][-1].content,
        }

    def writer_node(state):
        prompt = (
            f"Research:\n{state.get('research_notes', '')}\n\n"
            f"Analysis:\n{state.get('analysis', '')}\n\n"
            "Write the final report."
        )
        result = writer.invoke({"messages": [{"role": "user", "content": prompt}]})
        return {
            "messages": result["messages"],
            "final_report": result["messages"][-1].content,
        }
    workflow = StateGraph(ResearchState)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("researcher", research_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("writer", writer_node)

    workflow.add_edge(START, "supervisor")
    workflow.add_conditional_edges(
        "supervisor",
        lambda s: s.get("next_agent", "FINISH"),
        {
            "researcher": "researcher",
            "analyst": "analyst",
            "writer": "writer",
            "FINISH": END,
        },
    )
    workflow.add_edge("researcher", "supervisor")
    workflow.add_edge("analyst", "supervisor")
    workflow.add_edge("writer", "supervisor")

    return workflow.compile(checkpointer=checkpointer)


graph = build_graph()