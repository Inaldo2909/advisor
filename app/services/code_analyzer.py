"""
Code Analyzer Service
Analyzes Python code and provides optimization suggestions based on best practices.
"""
import ast
import re
from typing import List
from app.models.suggestion import Suggestion


class CodeAnalyzer:
    """
    Analyzes Python code for potential improvements.

    Checks for:
    - PEP 8 style violations
    - Performance issues
    - Code smells
    - Best practices
    """

    def __init__(self):
        self.suggestions = []

    def analyze(self, code_snippet: str) -> List[Suggestion]:
        """
        Main analysis method that runs all checks.

        Args:
            code_snippet: Python code to analyze

        Returns:
            List of Suggestion objects
        """
        self.suggestions = []

        # Check if code is valid Python
        try:
            tree = ast.parse(code_snippet)
        except SyntaxError as e:
            self.suggestions.append(Suggestion(
                type="syntax",
                severity="high",
                message=f"Syntax error: {str(e)}",
                line=e.lineno if hasattr(e, 'lineno') else None
            ))
            return self.suggestions

        # Run various checks
        self._check_naming_conventions(tree, code_snippet)
        self._check_code_complexity(tree)
        self._check_best_practices(tree, code_snippet)
        self._check_performance_issues(tree, code_snippet)
        self._check_style_issues(code_snippet)

        return self.suggestions

    def _check_naming_conventions(self, tree: ast.AST, code: str):
        """Check PEP 8 naming conventions"""
        for node in ast.walk(tree):
            # Check function names
            if isinstance(node, ast.FunctionDef):
                if not re.match(r'^[a-z_][a-z0-9_]*$', node.name) and not node.name.startswith('__'):
                    # Convert to snake_case
                    snake_case_name = re.sub(r'(?<!^)(?=[A-Z])', '_', node.name).lower()
                    self.suggestions.append(Suggestion(
                        type="style",
                        severity="medium",
                        message=f"Function '{node.name}' should use snake_case naming (PEP 8)",
                        line=node.lineno,
                        suggested_fix=f"def {snake_case_name}("
                    ))

            # Check class names
            if isinstance(node, ast.ClassDef):
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                    # Convert to PascalCase
                    pascal_case_name = ''.join(word.capitalize() for word in re.split(r'[_\s]+', node.name))
                    self.suggestions.append(Suggestion(
                        type="style",
                        severity="medium",
                        message=f"Class '{node.name}' should use PascalCase naming (PEP 8)",
                        line=node.lineno,
                        suggested_fix=f"class {pascal_case_name}:"
                    ))

            # Check constant names (variables in module scope that are all caps)
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        name = target.id
                        if name.isupper() and len(name) > 1:
                            # This is likely a constant, which is fine
                            pass
                        elif '_' not in name and name.islower() and len(name) == 1:
                            # Single letter variable - suggest more descriptive name
                            self.suggestions.append(Suggestion(
                                type="readability",
                                severity="low",
                                message=f"Consider using a more descriptive name instead of '{name}'",
                                line=node.lineno,
                                suggested_fix=f"descriptive_name = ..."
                            ))

    def _check_code_complexity(self, tree: ast.AST):
        """Check for overly complex functions"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Count nested levels
                complexity = self._calculate_complexity(node)
                if complexity > 10:
                    self.suggestions.append(Suggestion(
                        type="complexity",
                        severity="high",
                        message=f"Function '{node.name}' has high complexity ({complexity}). Consider refactoring.",
                        line=node.lineno
                    ))

                # Check function length
                if hasattr(node, 'end_lineno'):
                    length = node.end_lineno - node.lineno
                    if length > 50:
                        self.suggestions.append(Suggestion(
                            type="complexity",
                            severity="medium",
                            message=f"Function '{node.name}' is too long ({length} lines). Consider breaking it down.",
                            line=node.lineno
                        ))

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    def _check_best_practices(self, tree: ast.AST, code: str):
        """Check for Python best practices"""
        for node in ast.walk(tree):
            # Check for bare except
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    self.suggestions.append(Suggestion(
                        type="best_practice",
                        severity="high",
                        message="Avoid bare 'except:' clauses. Specify exception types.",
                        line=node.lineno,
                        suggested_fix="except Exception as e:"
                    ))

            # Check for mutable default arguments
            if isinstance(node, ast.FunctionDef):
                for default in node.args.defaults:
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        self.suggestions.append(Suggestion(
                            type="best_practice",
                            severity="high",
                            message=f"Avoid mutable default arguments in function '{node.name}'. Use None instead.",
                            line=node.lineno,
                            suggested_fix="def function_name(param=None):\n    if param is None:\n        param = []"
                        ))

            # Check for global variables
            if isinstance(node, ast.Global):
                self.suggestions.append(Suggestion(
                    type="best_practice",
                    severity="medium",
                    message="Avoid using 'global'. Consider using function parameters or class attributes.",
                    line=node.lineno,
                    suggested_fix="# Pass value as parameter instead:\ndef function(parameter):\n    return parameter"
                ))

    def _check_performance_issues(self, tree: ast.AST, code: str):
        """Check for common performance issues"""
        for node in ast.walk(tree):
            # Check for string concatenation in loops
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if isinstance(child, ast.AugAssign) and isinstance(child.op, ast.Add):
                        if isinstance(child.target, ast.Name):
                            self.suggestions.append(Suggestion(
                                type="performance",
                                severity="medium",
                                message="String concatenation in loop detected. Consider using join() or list comprehension.",
                                line=node.lineno,
                                suggested_fix="# Use join instead:\nresult = ''.join(items)\n# or list comprehension:\nresult = ''.join([str(item) for item in items])"
                            ))
                            break

            # Check for inefficient list operations
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr == 'append' and isinstance(node.func.value, ast.Name):
                        # This is fine for most cases, but check if inside a loop with range
                        parent = node
                        # Simplified check - in production would need more context
                        pass

    def _check_style_issues(self, code: str):
        """Check for PEP 8 style issues"""
        lines = code.split('\n')

        for i, line in enumerate(lines, 1):
            # Check line length
            if len(line) > 120:
                self.suggestions.append(Suggestion(
                    type="style",
                    severity="low",
                    message=f"Line exceeds 120 characters (PEP 8 recommends max 79-120)",
                    line=i
                ))

            # Check for trailing whitespace
            if line.endswith(' ') or line.endswith('\t'):
                self.suggestions.append(Suggestion(
                    type="style",
                    severity="low",
                    message="Trailing whitespace detected",
                    line=i,
                    suggested_fix=line.rstrip()
                ))

            # Check for missing spaces around operators
            if '=' in line and not any(x in line for x in ['==', '!=', '<=', '>=', '+=', '-=', '*=', '/=']):
                if re.search(r'\w=[^=\s]|[^=\s]=\w', line):
                    # Add spaces around =
                    fixed_line = re.sub(r'(\w)=([^=\s])', r'\1 = \2', line)
                    fixed_line = re.sub(r'([^=\s])=(\w)', r'\1 = \2', fixed_line)
                    self.suggestions.append(Suggestion(
                        type="style",
                        severity="low",
                        message="Missing spaces around assignment operator (PEP 8)",
                        line=i,
                        suggested_fix=fixed_line.strip()
                    ))

            # Check for multiple statements on one line
            if ';' in line and not line.strip().startswith('#'):
                # Split into multiple lines
                statements = line.split(';')
                fixed = '\n'.join(s.strip() for s in statements if s.strip())
                self.suggestions.append(Suggestion(
                    type="style",
                    severity="medium",
                    message="Avoid multiple statements on one line (PEP 8)",
                    line=i,
                    suggested_fix=fixed
                ))
