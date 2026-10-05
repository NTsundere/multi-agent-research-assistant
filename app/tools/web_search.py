from langchain_core.tools import tool
from duckduckgo_search import DDGS


@tool
def web_search(query: str) -> str:
    """Search the web for current information. Use for facts, news, statistics, and research."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        if not results:
            return f"No results found for: {query}"
        lines = [f"- {r['title']}: {r['body'][:200]}... ({r['href']})" for r in results]
        return "\n".join(lines)
    except Exception as e:
        return f"Search failed: {e}"