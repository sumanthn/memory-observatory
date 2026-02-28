#!/usr/bin/env python3
"""
Backfill semantic memory from existing experiment results.

Since the fact extraction LLM call silently failed during the original run
(JSON parsing bug — now fixed), this script manually extracts facts from
the known mock data and populates the semantic store.

This lets us test what the full memory pipeline looks like with semantic
memory actually populated, without re-running the expensive LLM experiments.

Usage:
    python scripts/backfill_semantic.py                    # backfill into full_memory.db
    python scripts/backfill_semantic.py --db path/to.db    # backfill into specific DB
    python scripts/backfill_semantic.py --dry-run           # show what would be stored
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from memory.semantic_store import SemanticStore


# Facts extracted from mock_data.json — what the LLM _should_ have produced
# Organized by session (which company was researched when)
FACTS_BY_SESSION = {
    1: {  # Session 1: TechCorp research
        "company": "TechCorp Inc.",
        "facts": [
            ("revenue", "$4.2B", "FY2025, +3.1% YoY"),
            ("net_income", "$380M", "FY2025"),
            ("operating_margin", "18.2%", "FY2025, prior year 19.8%"),
            ("total_debt", "$2.8B", "FY2025"),
            ("total_equity", "$1.55B", "FY2025"),
            ("debt_to_equity", "1.81x", "Significantly exceeds tech sector median ~0.9x"),
            ("cash", "$900M", "FY2025"),
            ("EPS", "$1.55", "FY2025"),
            ("PE_ratio", "22.4x", "FY2025"),
            ("R&D_spend", "$520M (12.4% of revenue)", "FY2025"),
            ("shares_outstanding", "245M", "FY2025"),
            ("Q1_revenue", "$980M", "Q1 2025, beat estimate by 0.5%"),
            ("Q2_revenue", "$1.05B", "Q2 2025, beat estimate by 2.9%"),
            ("Q3_revenue", "$1.02B", "Q3 2025, MISSED by 8.1%"),
            ("Q4_revenue", "$1.15B", "Q4 2025, beat estimate by 1.8%"),
            ("CEO", "Sarah Chen", "Appointed July 2025, replacing Robert Martinez (12-year tenure)"),
            ("leverage_ratio", "1.83x EBITDA", "vs 1.5x covenant max — TECHNICAL BREACH"),
            ("covenant_waiver", "Through March 31, 2026", "Temporary waiver, permanent amendment pending"),
            ("transition_costs", "$18M", "Q3 2025, executive severance and consulting"),
            ("cloud_growth", "+12% YoY", "Offsetting 6% decline in legacy hardware"),
            ("gross_margin", "62.3%", "FY2025, expanded 40bps"),
            ("AI_partnership", "$200M committed minimum over 3 years", "Dec 2025, Nova AI platform distribution"),
            ("analyst_rating", "Downgraded to Equal Weight", "Morgan Stanley, Nov 2025, leverage concerns"),
        ],
    },
    2: {  # Session 2: HealthCo research
        "company": "HealthCo Ltd.",
        "facts": [
            ("revenue", "$2.1B", "FY2025, -5.2% YoY"),
            ("net_income", "$95M", "FY2025"),
            ("operating_margin", "11.8%", "FY2025, declining to 8.9% in Q4"),
            ("total_debt", "$800M", "FY2025"),
            ("total_equity", "$1.2B", "FY2025"),
            ("debt_to_equity", "0.67x", "Conservative, below sector median"),
            ("cash", "$450M", "FY2025"),
            ("EPS", "$0.53", "FY2025"),
            ("PE_ratio", "34.2x", "FY2025, elevated amid declining earnings"),
            ("R&D_spend", "$340M (16.2% of revenue)", "FY2025, focused on Nexaviron"),
            ("Q1_revenue", "$560M", "Q1 2025"),
            ("Q2_revenue", "$540M", "Q2 2025, declining"),
            ("Q3_revenue", "$520M", "Q3 2025, declining"),
            ("Q4_revenue", "$480M", "Q4 2025, -9.4% sequential decline"),
            ("revenue_trend", "4 consecutive quarters of decline", "Accelerating erosion"),
            ("lead_drug", "Nexaviron", "Phase III, FDA requested additional hepatotoxicity data"),
            ("FDA_status", "Pending, 3-6 month potential delay", "Additional safety data requested"),
            ("legacy_drug", "Cardiovex", "Franchise down 22% YoY, generic competition"),
            ("related_party_transaction", "$42M consulting deal with Meridian Strategic Partners", "Firm managed by board director James Whitfield"),
            ("activist_investor", "ValueAct Partners", "Accumulated 6.2% stake, questioning governance"),
            ("cash_burn_concern", "$450M cash vs $340M annual R&D", "~1.3 years runway at current burn"),
        ],
    },
    5: {  # Session 5: RetailMax research
        "company": "RetailMax Corp.",
        "facts": [
            ("revenue", "$6.8B", "FY2025, +8% YoY"),
            ("net_income", "$210M", "FY2025"),
            ("operating_margin", "5.1%", "FY2025, compressed from 7.2% prior year"),
            ("total_debt", "$3.2B", "FY2025"),
            ("total_equity", "$2.1B", "FY2025"),
            ("debt_to_equity", "1.52x", "Above retail sector median ~0.8x"),
            ("cash", "$380M", "FY2025"),
            ("new_stores_opened", "40", "FY2025, funded by debt"),
            ("total_store_count", "892", "FY2025"),
            ("same_store_sales_growth", "1.2%", "FY2025, weak"),
            ("inventory_days_Q1", "60 days", "Q1 2025"),
            ("inventory_days_Q2", "75 days", "Q2 2025, building"),
            ("inventory_days_Q3", "85 days", "Q3 2025, building"),
            ("inventory_days_Q4", "95 days", "Q4 2025, alarming buildup"),
            ("margin_compression", "5.1% from 7.2%", "210bps compression YoY, aggressive expansion costs"),
        ],
    },
}


def backfill(db_path: str, dry_run: bool = False):
    """Populate semantic store with known facts from each research session."""
    if not dry_run:
        store = SemanticStore(db_path)

    total = 0
    for session_id, session_data in sorted(FACTS_BY_SESSION.items()):
        company = session_data["company"]
        facts = session_data["facts"]
        print(f"\nSession {session_id}: {company} ({len(facts)} facts)")

        for attribute, value, context in facts:
            total += 1
            if dry_run:
                print(f"  [{total:3d}] {company} — {attribute}: {value} ({context})")
            else:
                fact_id = store.add(
                    entity=company,
                    attribute=attribute,
                    value=value,
                    context=context,
                    source_session=session_id,
                    confidence=1.0,
                )
                print(f"  [{total:3d}] Stored id={fact_id}: {attribute} = {value}")

    print(f"\n{'Would store' if dry_run else 'Stored'} {total} facts total")

    if not dry_run:
        stats = store.get_stats()
        print(f"Semantic store: {stats['count']} facts, {stats['unique_entities']} entities")


def main():
    parser = argparse.ArgumentParser(description="Backfill semantic memory from known data")
    parser.add_argument(
        "--db",
        default="output/memories/full_memory.db",
        help="Path to memory database (default: output/memories/full_memory.db)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show what would be stored without writing")
    args = parser.parse_args()

    if not os.path.exists(args.db) and not args.dry_run:
        print(f"Error: Database not found: {args.db}")
        sys.exit(1)

    backfill(args.db, args.dry_run)


if __name__ == "__main__":
    main()
