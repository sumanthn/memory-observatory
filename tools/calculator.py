"""
Calculator Tool (Actual)

Evaluates mathematical expressions using a restricted Python eval.
Only allows mathematical operations — no imports, no builtins.
"""

import math


# Restricted namespace for safe evaluation
_SAFE_NAMESPACE = {
    "__builtins__": {},
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "sum": sum,
    "pow": pow,
    "sqrt": math.sqrt,
    "log": math.log,
    "log10": math.log10,
    "ceil": math.ceil,
    "floor": math.floor,
    "pi": math.pi,
    "e": math.e,
}


def evaluate(expression: str) -> str:
    """
    Evaluate a mathematical expression.

    Args:
        expression: Math expression (e.g., '4.2 / 2.3', '(1.8 - 0.67) / 0.67 * 100')

    Returns:
        The computed result as a formatted string.
    """
    try:
        # Clean up the expression
        expr = expression.strip()

        # Safety check: reject anything that looks like code injection
        forbidden = ["import", "exec", "eval", "open", "file", "__", "os", "sys"]
        for word in forbidden:
            if word in expr.lower():
                return f"Error: Expression contains forbidden term '{word}'."

        result = eval(expr, _SAFE_NAMESPACE)

        # Format nicely
        if isinstance(result, float):
            if result == int(result):
                return f"Result: {int(result)}"
            elif abs(result) >= 1000:
                return f"Result: {result:,.2f}"
            else:
                return f"Result: {result:.4f}"
        return f"Result: {result}"

    except ZeroDivisionError:
        return "Error: Division by zero."
    except SyntaxError:
        return f"Error: Invalid expression syntax: '{expression}'"
    except Exception as e:
        return f"Error evaluating expression: {e}"
