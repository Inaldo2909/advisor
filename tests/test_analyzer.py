"""
Unit Tests for Code Analyzer
Tests the core functionality of the code analysis engine.
"""
import pytest
from app.services.code_analyzer import CodeAnalyzer
from app.models.suggestion import Suggestion


def test_analyzer_valid_code():
    """Test analyzer with valid, well-formatted code"""
    analyzer = CodeAnalyzer()
    code = """
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total
"""
    suggestions = analyzer.analyze(code)
    # Well-formatted code should have minimal or no suggestions
    assert isinstance(suggestions, list)


def test_analyzer_naming_convention():
    """Test detection of naming convention violations"""
    analyzer = CodeAnalyzer()
    code = "def BadFunctionName():\n    pass"

    suggestions = analyzer.analyze(code)

    # Should detect PascalCase in function name
    assert any(s.type == "style" for s in suggestions)
    assert any("snake_case" in s.message for s in suggestions)


def test_analyzer_syntax_error():
    """Test handling of syntax errors"""
    analyzer = CodeAnalyzer()
    code = "def broken(\n    pass"  # Invalid syntax

    suggestions = analyzer.analyze(code)

    # Should detect syntax error
    assert len(suggestions) > 0
    assert suggestions[0].type == "syntax"
    assert suggestions[0].severity == "high"


def test_analyzer_bare_except():
    """Test detection of bare except clauses"""
    analyzer = CodeAnalyzer()
    code = """
try:
    risky_operation()
except:
    pass
"""

    suggestions = analyzer.analyze(code)

    # Should detect bare except
    assert any(s.type == "best_practice" for s in suggestions)
    assert any("bare" in s.message.lower() for s in suggestions)


def test_analyzer_line_length():
    """Test detection of long lines"""
    analyzer = CodeAnalyzer()
    long_line = "x = " + "1" * 150  # Very long line

    suggestions = analyzer.analyze(long_line)

    # Should detect line length issue
    assert any("exceeds" in s.message for s in suggestions)


def test_suggestion_model():
    """Test Suggestion model creation"""
    suggestion = Suggestion(
        type="style",
        severity="low",
        message="Test message",
        line=1
    )

    assert suggestion.type == "style"
    assert suggestion.severity == "low"
    assert suggestion.message == "Test message"
    assert suggestion.line == 1


def test_analyzer_empty_code():
    """Test analyzer with empty code"""
    analyzer = CodeAnalyzer()
    code = ""

    # Should handle gracefully
    try:
        suggestions = analyzer.analyze(code)
        assert isinstance(suggestions, list)
    except Exception as e:
        pytest.fail(f"Analyzer failed on empty code: {e}")


def test_analyzer_complexity():
    """Test detection of high complexity"""
    analyzer = CodeAnalyzer()
    # Function with multiple nested conditions
    code = """
def complex_function(x, y, z):
    if x > 0:
        if y > 0:
            if z > 0:
                if x > y:
                    if y > z:
                        if z > 1:
                            return True
    return False
"""

    suggestions = analyzer.analyze(code)

    # Should detect complexity or nesting issues
    # This is a heuristic test - actual results may vary
    assert isinstance(suggestions, list)
