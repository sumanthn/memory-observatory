"""
Tool Registry — Maps tool names to executable functions

Provides tool definitions in the format the agent prompt expects,
and validates + executes tool calls.
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools import financial_lookup, sec_filing, news_search, calculator


TOOLS = {
    "financial_lookup": {
        "function": financial_lookup.lookup,
        "description": (
            "Look up financial metrics for a company. "
            "Returns specific financial data points."
        ),
        "parameters": {
            "company": "string — Company name (e.g., 'TechCorp', 'HealthCo', 'RetailMax')",
            "metric": (
                "string — One of: revenue, net_income, total_debt, total_equity, "
                "operating_margin, cash, shares_outstanding, debt_to_equity, "
                "quarterly_revenue, eps, pe_ratio, r_and_d_spend, "
                "inventory_days, all_financials"
            ),
        },
    },
    "sec_filing": {
        "function": sec_filing.get_filing,
        "description": (
            "Retrieve excerpts from SEC filings (10-K, 10-Q) for a company. "
            "Contains management discussion, footnotes, and risk factors."
        ),
        "parameters": {
            "company": "string — Company name",
            "filing_type": "string — One of: 10-K, 10-Q",
        },
    },
    "news_search": {
        "function": news_search.search,
        "description": "Search recent news articles about a company.",
        "parameters": {
            "company": "string — Company name",
        },
    },
    "calculate": {
        "function": calculator.evaluate,
        "description": (
            "Evaluate a mathematical expression. "
            "Use for computing ratios, percentages, comparisons."
        ),
        "parameters": {
            "expression": "string — Math expression (e.g., '4.2 / 2.3')",
        },
    },
}


def get_tool_definitions() -> str:
    """
    Return tool definitions formatted for prompt injection.
    """
    lines = []
    for name, tool in TOOLS.items():
        lines.append(f"Tool: {name}")
        lines.append(f"  Description: {tool['description']}")
        lines.append("  Parameters:")
        for param, desc in tool["parameters"].items():
            lines.append(f"    - {param}: {desc}")
        lines.append("")
    return "\n".join(lines)


def get_tool_definitions_for_api() -> list[dict]:
    """
    Return tool definitions in Claude API tool-use format.
    """
    tools = []
    for name, tool in TOOLS.items():
        properties = {}
        required = []
        for param, desc in tool["parameters"].items():
            properties[param] = {
                "type": "string",
                "description": desc,
            }
            required.append(param)

        tools.append(
            {
                "name": name,
                "description": tool["description"],
                "input_schema": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            }
        )
    return tools


def execute_tool(tool_name: str, args: dict) -> str:
    """
    Execute a tool by name with given arguments.

    Returns the tool's output as a string.
    """
    if tool_name not in TOOLS:
        return f"Error: Unknown tool '{tool_name}'. Available: {', '.join(TOOLS.keys())}"

    tool = TOOLS[tool_name]
    func = tool["function"]

    # Validate required parameters
    for param in tool["parameters"]:
        if param not in args:
            return f"Error: Missing required parameter '{param}' for tool '{tool_name}'."

    try:
        # Call the tool function with the provided args
        result = func(**args)
        return result
    except Exception as e:
        return f"Error executing {tool_name}: {e}"
