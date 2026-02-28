"""
SEC Filing Tool (Mock)

Returns pre-written SEC filing excerpts from mock_data.json.
The filing text has red flags deliberately buried in the prose,
just like real SEC filings.
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


def get_filing(company: str, filing_type: str) -> str:
    """
    Retrieve excerpts from SEC filings for a company.

    Args:
        company: Company name (e.g., 'TechCorp', 'HealthCo', 'RetailMax')
        filing_type: One of: '10-K', '10-Q'

    Returns:
        Filing excerpt text (2-3 paragraphs with embedded red flags).
    """
    data = _load_data()

    # Normalize company name
    company_key = _find_company(company, data)
    if not company_key:
        return f"Error: Company '{company}' not found in SEC filing database."

    company_data = data["companies"][company_key]
    filings = company_data.get("sec_filings", {})
    full_name = company_data["full_name"]

    # Normalize filing type
    filing_type = filing_type.upper().replace(" ", "")
    if filing_type not in filings:
        available = ", ".join(filings.keys())
        return (
            f"Error: Filing type '{filing_type}' not available for {full_name}. "
            f"Available filings: {available}"
        )

    filing_text = filings[filing_type]

    # Wrap in realistic header
    header = (
        f"=== SEC Filing: {full_name} — Form {filing_type} ===\n"
        f"Filed with the Securities and Exchange Commission\n"
        f"Fiscal Year: {company_data['fiscal_year']}\n"
        f"{'=' * 50}\n\n"
    )

    return header + filing_text


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
