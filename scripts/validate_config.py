#!/usr/bin/env python3
"""
Pre-flight validation for Memory Observatory config files.

Checks:
1. All session IDs are unique and sequential (1-N)
2. All companies referenced in sessions exist in mock_data.json
3. All scoring criteria have non-empty keywords
4. Tool fuzzy matcher resolves every company without ambiguity
5. Each session has at least 4 scoring criteria
"""

import json
import os
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)


def load_json(path):
    with open(os.path.join(ROOT, path)) as f:
        return json.load(f)


def validate():
    errors = []
    warnings = []

    # Load config files
    try:
        mock_data = load_json("config/mock_data.json")
    except Exception as e:
        print(f"FATAL: Cannot load mock_data.json: {e}")
        return False

    try:
        scenarios = load_json("config/scenarios.json")
    except Exception as e:
        print(f"FATAL: Cannot load scenarios.json: {e}")
        return False

    companies = mock_data["companies"]
    sessions = scenarios["sessions"]
    company_keys = set(companies.keys())

    print(f"Companies: {len(company_keys)} ({', '.join(sorted(company_keys))})")
    print(f"Sessions: {len(sessions)}")
    print()

    # 1. Check session IDs are unique and sequential
    print("1. Checking session IDs...")
    ids = [s["id"] for s in sessions]
    if len(ids) != len(set(ids)):
        dupes = [i for i in ids if ids.count(i) > 1]
        errors.append(f"Duplicate session IDs: {set(dupes)}")
    expected = list(range(1, len(ids) + 1))
    if sorted(ids) != expected:
        missing = set(expected) - set(ids)
        extra = set(ids) - set(expected)
        if missing:
            errors.append(f"Missing session IDs: {sorted(missing)}")
        if extra:
            errors.append(f"Unexpected session IDs: {sorted(extra)}")
    if not errors:
        print(f"   OK — {len(ids)} sessions, IDs 1-{max(ids)}")

    # 2. Check all companies referenced in sessions exist
    print("2. Checking company references...")
    meta_types = {"comparison", "follow_up", "synthesis"}
    session_companies = set()
    for s in sessions:
        comp = s.get("company", "")
        if comp not in meta_types:
            session_companies.add(comp)
    missing_companies = session_companies - company_keys
    if missing_companies:
        errors.append(f"Companies in sessions but not in mock_data: {missing_companies}")
    else:
        print(f"   OK — all referenced companies exist in mock_data.json")

    # 3. Check scoring criteria keywords are non-empty
    print("3. Checking scoring criteria...")
    empty_keywords = []
    for s in sessions:
        criteria = s.get("ground_truth_score_criteria", {})
        for crit_name, crit in criteria.items():
            kw = crit.get("keywords", [])
            if not kw:
                empty_keywords.append(f"S{s['id']}.{crit_name}")
    if empty_keywords:
        errors.append(f"Empty keywords in criteria: {empty_keywords[:10]}{'...' if len(empty_keywords) > 10 else ''}")
    else:
        total_criteria = sum(len(s.get("ground_truth_score_criteria", {})) for s in sessions)
        print(f"   OK — {total_criteria} criteria, all have keywords")

    # 4. Check fuzzy matcher resolves every company
    print("4. Checking tool fuzzy matching...")
    from tools.financial_lookup import _find_company, _load_data
    data = _load_data()

    # Test each company key resolves to itself
    for key in company_keys:
        result = _find_company(key, data)
        if result != key:
            errors.append(f"Fuzzy match '{key}' resolved to '{result}' instead of itself")

    # Test common variations
    test_names = {
        "TechCorp": "TechCorp",
        "techcorp": "TechCorp",
        "TechCorp Inc.": "TechCorp",
        "HealthCo": "HealthCo",
        "HealthCo Ltd.": "HealthCo",
        "RetailMax": "RetailMax",
        "EnergyX": "EnergyX",
        "BankFirst": "BankFirst",
        "PropCore": "PropCore",
        "ManufactCo": "ManufactCo",
        "MedDevice": "MedDevice",
        "FinTechPay": "FinTechPay",
        "LogiFlow": "LogiFlow",
    }
    for test_name, expected_key in test_names.items():
        if expected_key not in company_keys:
            continue
        result = _find_company(test_name, data)
        if result != expected_key:
            errors.append(f"Fuzzy match '{test_name}' → '{result}' (expected '{expected_key}')")

    # Test potential collision: "Tech" should not match FinTechPay
    if "TechCorp" in company_keys and "FinTechPay" in company_keys:
        result = _find_company("Tech", data)
        if result not in ("TechCorp", None):
            warnings.append(f"Fuzzy match 'Tech' resolved to '{result}' — may cause ambiguity")

    if not any("Fuzzy match" in e for e in errors):
        print(f"   OK — all {len(company_keys)} companies resolve correctly")

    # 5. Check minimum criteria per session
    print("5. Checking minimum criteria count...")
    too_few = []
    for s in sessions:
        count = len(s.get("ground_truth_score_criteria", {}))
        if count < 4:
            too_few.append(f"S{s['id']}: {count} criteria")
    if too_few:
        errors.append(f"Sessions with <4 criteria: {too_few[:10]}{'...' if len(too_few) > 10 else ''}")
    else:
        min_c = min(len(s.get("ground_truth_score_criteria", {})) for s in sessions)
        max_c = max(len(s.get("ground_truth_score_criteria", {})) for s in sessions)
        print(f"   OK — criteria per session: min={min_c}, max={max_c}")

    # 6. Check required fields exist on all sessions
    print("6. Checking required fields...")
    required = ["id", "title", "task", "company", "expected_entities", "ground_truth_score_criteria"]
    missing_fields = []
    for s in sessions:
        for field in required:
            if field not in s:
                missing_fields.append(f"S{s.get('id', '?')}: missing '{field}'")
    if missing_fields:
        errors.append(f"Missing required fields: {missing_fields[:10]}{'...' if len(missing_fields) > 10 else ''}")
    else:
        print(f"   OK — all sessions have required fields")

    # Summary
    print()
    if warnings:
        print(f"WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  ⚠ {w}")
        print()

    if errors:
        print(f"ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  ✗ {e}")
        print(f"\nValidation FAILED — fix {len(errors)} error(s) before running experiments")
        return False
    else:
        print("✓ All checks passed — config is ready for experiments")

        # Print summary stats
        weight_3 = sum(
            1 for s in sessions
            for c in s.get("ground_truth_score_criteria", {}).values()
            if c.get("weight") == 3
        )
        total_criteria = sum(len(s.get("ground_truth_score_criteria", {})) for s in sessions)
        categories = {}
        for s in sessions:
            sid = s["id"]
            if sid <= 10:
                cat = "A"
            elif sid <= 20:
                cat = "B"
            elif sid <= 30:
                cat = "C"
            elif sid <= 50:
                cat = "D"
            elif sid <= 75:
                cat = "E"
            elif sid <= 88:
                cat = "F"
            else:
                cat = "G"
            categories[cat] = categories.get(cat, 0) + 1

        print(f"\n  Sessions: {len(sessions)}")
        print(f"  Companies: {len(company_keys)}")
        print(f"  Total scoring criteria: {total_criteria}")
        print(f"  Weight-3 (deep research) criteria: {weight_3}")
        print(f"  Categories: {dict(sorted(categories.items()))}")
        est_cost = len(sessions) * 3 * 0.017
        print(f"  Estimated cost (3 experiments): ~${est_cost:.2f}")
        return True


if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)
