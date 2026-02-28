"""
Financial Lookup Tool (Mock)

Returns financial data for fictional companies from mock_data.json.
Formats responses to look like real financial data API results.
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


def lookup(company: str, metric: str) -> str:
    """
    Look up a financial metric for a company.

    Args:
        company: Company name (e.g., 'TechCorp', 'HealthCo', 'RetailMax')
        metric: One of: revenue, net_income, total_debt, total_equity,
                operating_margin, cash, shares_outstanding, debt_to_equity,
                quarterly_revenue, eps, pe_ratio, r_and_d_spend,
                inventory_days, all_financials

    Returns:
        Formatted string with the financial data.
    """
    data = _load_data()

    # Normalize company name
    company_key = _find_company(company, data)
    if not company_key:
        available = ", ".join(data["companies"].keys())
        return f"Error: Company '{company}' not found. Available: {available}"

    company_data = data["companies"][company_key]
    financials = company_data["financials"]
    full_name = company_data["full_name"]
    fy = company_data["fiscal_year"]

    if metric == "all_financials":
        return _format_all_financials(full_name, fy, financials)

    if metric == "quarterly_revenue":
        return _format_quarterly(full_name, financials)

    if metric == "inventory_days":
        inv = financials.get("inventory_days")
        if inv is None:
            return f"{full_name}: Inventory days data not available for this company."
        return _format_inventory_days(full_name, inv)

    # Simple metric lookup
    metric_map = {
        "revenue": ("revenue_formatted", "Revenue"),
        "net_income": ("net_income_formatted", "Net Income"),
        "total_debt": ("total_debt_formatted", "Total Debt"),
        "total_equity": ("total_equity_formatted", "Total Equity"),
        "debt_to_equity": ("debt_to_equity", "Debt-to-Equity Ratio"),
        "operating_margin": ("operating_margin", "Operating Margin"),
        "cash": ("cash_formatted", "Cash & Equivalents"),
        "shares_outstanding": ("shares_outstanding_formatted", "Shares Outstanding"),
        "eps": ("eps", "Earnings Per Share"),
        "pe_ratio": ("pe_ratio", "P/E Ratio"),
        "r_and_d_spend": ("r_and_d_spend", "R&D Spend"),
    }

    if metric not in metric_map:
        return (
            f"Error: Unknown metric '{metric}'. "
            f"Available: {', '.join(metric_map.keys())}, quarterly_revenue, "
            f"inventory_days, all_financials"
        )

    key, label = metric_map[metric]
    value = financials.get(key)

    if value is None:
        return f"{full_name}: {label} data not available."

    # Format with context
    suffix = ""
    if metric == "revenue":
        yoy = financials.get("revenue_yoy_change")
        if yoy is not None:
            direction = "increase" if yoy > 0 else "decrease"
            suffix = f" Note: This represents a {abs(yoy)}% YoY {direction}."
    elif metric == "operating_margin":
        prior = financials.get("operating_margin_prior_year")
        if prior:
            suffix = f" (Prior year: {prior}%)"
        value = f"{value}%"
    elif metric == "debt_to_equity":
        suffix = " Note: Technology sector median is approximately 0.9x. Retail sector median is approximately 0.8x."
    elif metric == "r_and_d_spend":
        pct = financials.get("r_and_d_pct_revenue")
        if pct:
            value = f"${value / 1e6:.0f}M"
            suffix = f" ({pct}% of revenue)"

    return f"{full_name} {label} ({fy}): {value}.{suffix}"


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
        # Pick shortest key (most specific match)
        return min(matches, key=len)

    return None


def _format_all_financials(name: str, fy: str, fin: dict) -> str:
    lines = [f"=== {name} Financial Summary ({fy}) ==="]
    lines.append(f"Revenue: {fin['revenue_formatted']} (YoY: {fin['revenue_yoy_change']:+.1f}%)")
    lines.append(f"Net Income: {fin['net_income_formatted']}")
    lines.append(f"Operating Margin: {fin['operating_margin']}%")
    prior = fin.get("operating_margin_prior_year")
    if prior:
        lines.append(f"  (Prior Year: {prior}%)")
    lines.append(f"Total Debt: {fin['total_debt_formatted']}")
    lines.append(f"Total Equity: {fin['total_equity_formatted']}")
    lines.append(f"Debt-to-Equity: {fin['debt_to_equity']}")
    lines.append(f"Cash: {fin['cash_formatted']}")
    lines.append(f"Shares Outstanding: {fin['shares_outstanding_formatted']}")
    if fin.get("eps"):
        lines.append(f"EPS: ${fin['eps']}")
    if fin.get("pe_ratio"):
        lines.append(f"P/E Ratio: {fin['pe_ratio']}")
    if fin.get("r_and_d_spend"):
        lines.append(f"R&D Spend: ${fin['r_and_d_spend'] / 1e6:.0f}M ({fin.get('r_and_d_pct_revenue', 'N/A')}% of revenue)")
    if fin.get("new_stores_opened"):
        lines.append(f"New Stores Opened: {fin['new_stores_opened']}")
        lines.append(f"Total Store Count: {fin.get('total_store_count', 'N/A')}")
        lines.append(f"Same-Store Sales Growth: {fin.get('same_store_sales_growth', 'N/A')}%")
    return "\n".join(lines)


def _format_quarterly(name: str, fin: dict) -> str:
    quarterly = fin.get("quarterly_revenue", {})
    if not quarterly:
        return f"{name}: Quarterly revenue data not available."
    lines = [f"=== {name} Quarterly Revenue ==="]
    for quarter, data in sorted(quarterly.items()):
        status = "BEAT" if data["beat_miss"] == "beat" else "MISS"
        lines.append(
            f"  {quarter}: {data['revenue_formatted']} "
            f"(est. ${data['estimate'] / 1e6:.0f}M) — {status} by {abs(data['surprise_pct'])}%"
        )
    return "\n".join(lines)


def _format_inventory_days(name: str, inv: dict) -> str:
    lines = [f"=== {name} Inventory Days Outstanding ==="]
    for quarter, days in sorted(inv.items()):
        lines.append(f"  {quarter}: {days} days")
    lines.append(f"  Trend: {list(inv.values())[0]} → {list(inv.values())[-1]} days")
    return "\n".join(lines)
