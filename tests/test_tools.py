from app.tools.calculator import calculator
from app.tools.web_search import web_search


def test_calculator():
    result = calculator.invoke("2 + 2")
    assert "4" in result


def test_web_search():
    result = web_search.invoke("Python programming language")
    assert isinstance(result, str)
    assert len(result) > 0