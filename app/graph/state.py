from typing import TypedDict, List, Dict, Any, Annotated
from langgraph.graph.message import add_messages


class ResearchState(TypedDict, total=False):
    messages: Annotated[List[Dict[str, Any]], add_messages]
    research_notes: str
    analysis: str
    final_report: str
    next_agent: str