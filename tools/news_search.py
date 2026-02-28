"""
News Search Tool (Mock)

Returns pre-written news headlines and summaries from mock_data.json.
"""

import json
import os

_DATA = None


def _load_data():
    global _DATA
    if _DATA is None:
        data_path = os.path.join(
            os.path.dirname(__file__), "..", "config", "mock_data.json"
        )
        with open(data_path) as f:
            _DATA = json.load(f)
    return _DATA


def search(company: str) -> str:
    """
    Search recent news articles about a company.

    Args:
        company: Company name (e.g., 'TechCorp', 'HealthCo', 'RetailMax')

    Returns:
        Formatted list of recent news articles.
    """
    data = _load_data()

    company_key = _find_company(company, data)
    if not company_key:
        available = ", ".join(data["companies"].keys())
        return f"Error: No news found for '{company}'. Available: {available}"

    company_data = data["companies"][company_key]
    news_items = company_data.get("news", [])
    full_name = company_data["full_name"]

    if not news_items:
        return f"No recent news found for {full_name}."

    lines = [f"=== Recent News: {full_name} ===\n"]
    for i, item in enumerate(news_items, 1):
        lines.append(f"[{i}] {item['headline']}")
        lines.append(f"    Date: {item['date']} | Source: {item['source']}")
        lines.append(f"    {item['summary']}")
        lines.append("")

    return "\n".join(lines)


def _find_company(name: str, data: dict) -> str | None:
    """Fuzzy match company name with exact-match-first priority."""
    name_lower = name.lower().strip()
    companies = data["companies"]

    # Pass 1: exact key match (case-insensitive)
    for key in companies:
        if name_lower == key.lower():
            return key

    # Pass 2: exact full_name match
    for key in companies:
        if name_lower == companies[key]["full_name"].lower():
            return key

    # Pass 3: substring match — prefer shorter keys to avoid collisions
    matches = []
    for key in companies:
        key_lower = key.lower()
        full = companies[key]["full_name"].lower()
        if name_lower in key_lower or key_lower in name_lower:
            matches.append(key)
        elif name_lower in full or full.startswith(name_lower):
            matches.append(key)
    if len(matches) == 1:
        return matches[0]
    if matches:
        return min(matches, key=len)

    return None
