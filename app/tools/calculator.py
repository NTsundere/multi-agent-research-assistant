from langchain_core.tools import tool
import numexpr


@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression. Use for arithmetic, percentages, and numeric analysis.
    Example input: '2 + 2 * 10' or '(100 * 1.15)'."""
    try:
        result = numexpr.evaluate(expression).item()
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error evaluating '{expression}': {e}"