#!/usr/bin/env python3
"""Generate the 100-session scenarios.json file."""
import json
import os

# Keep sessions 1-5 from the existing file
existing_path = os.path.join(os.path.dirname(__file__), "..", "config", "scenarios.json")
with open(existing_path) as f:
    existing = json.load(f)
existing_sessions = existing["sessions"]  # Sessions 1-5

# Helper to build a session dict
def s(id, title, task, company, entities, criteria):
    return {
        "id": id,
        "title": title,
        "task": task,
        "company": company,
        "expected_entities": entities,
        "ground_truth_score_criteria": criteria,
    }

def c(desc, keywords, weight):
    return {"description": desc, "keywords": keywords, "weight": weight}

sessions = list(existing_sessions)  # 1-5

# ============================================================
# Category A: Initial Analysis (Sessions 6-10)
# ============================================================
sessions.append(s(6, "Research EnergyX Corp",
    "Conduct a thorough financial analysis of EnergyX Corp. Identify key strengths, risks, and any red flags. Provide a summary suitable for an investment committee.",
    "EnergyX",
    ["revenue", "reserve_depletion", "oil_price_risk", "debt_covenant", "margin_compression"],
    {
        "identified_revenue": c("Identified revenue of ~$8.9B with decline", ["8.9", "revenue", "decline", "12"], 1),
        "identified_margin_compression": c("Identified operating margin drop from 22.1% to 14.2%", ["22.1", "14.2", "margin", "compress", "decline"], 2),
        "identified_reserve_depletion": c("Flagged reserve replacement ratio of 0.68x", ["0.68", "reserve", "replacement", "depletion"], 2),
        "found_covenant_near_breach": c("Found covenant near-breach in 10-K — 3.2x vs 3.0x minimum, $45M cushion", ["3.2", "3.0", "covenant", "cushion", "45"], 3),
        "identified_oil_price_risk": c("Connected revenue decline to oil price drop", ["oil", "price", "$68", "$82", "commodity"], 1),
        "provided_recommendation": c("Provided investment recommendation with risk assessment", ["recommend", "risk", "caution", "outlook", "assessment"], 1),
    }
))

sessions.append(s(7, "Research BankFirst Financial",
    "Conduct a thorough financial analysis of BankFirst Financial Group. Identify key strengths, risks, and any red flags. Provide a summary suitable for an investment committee.",
    "BankFirst",
    ["npl_ratio", "cre_exposure", "provision_increase", "nim_compression", "credit_quality"],
    {
        "identified_revenue": c("Identified net interest income of ~$1.8B", ["1.8", "revenue", "interest income", "decline"], 1),
        "identified_npl_surge": c("Flagged NPL ratio surge from 1.9% to 3.8%", ["3.8", "1.9", "NPL", "non-performing", "doubled"], 2),
        "identified_cre_exposure": c("Identified CRE exposure at 34.2% of loan book", ["34.2", "CRE", "commercial real estate", "office", "exposure"], 2),
        "found_provision_detail": c("Found provision increase of 156% to $285M in filings", ["285", "156", "provision", "credit loss", "Harmon"], 3),
        "identified_nim_compression": c("Noted NIM compression of 45bps", ["NIM", "net interest margin", "45", "compress", "basis point"], 2),
        "provided_recommendation": c("Provided investment recommendation", ["recommend", "risk", "caution", "outlook", "assessment"], 1),
    }
))

sessions.append(s(8, "Research PropCore REIT",
    "Conduct a thorough financial analysis of PropCore REIT Inc. Identify key strengths, risks, and any red flags. Provide a summary suitable for an investment committee.",
    "PropCore",
    ["floating_rate_debt", "occupancy_decline", "deferred_maintenance", "leverage", "dividend_risk"],
    {
        "identified_revenue": c("Identified rental income of ~$1.35B", ["1.35", "revenue", "rental", "income"], 1),
        "identified_floating_rate": c("Flagged 62% floating-rate debt exposure", ["62", "floating", "rate", "variable", "$30M"], 2),
        "identified_occupancy_decline": c("Identified occupancy drop from 93.1% to 87.3%", ["93.1", "87.3", "occupancy", "decline", "580"], 2),
        "found_deferred_maintenance": c("Found $340M deferred maintenance backlog in 10-K", ["340", "deferred", "maintenance", "backlog", "capex"], 3),
        "identified_high_leverage": c("Noted D/E of 2.29, elevated for REITs", ["2.29", "debt-to-equity", "leverage", "peer", "1.4"], 2),
        "provided_recommendation": c("Provided investment recommendation", ["recommend", "risk", "caution", "outlook", "dividend"], 1),
    }
))

sessions.append(s(9, "Research ManufactCo Industries",
    "Conduct a thorough financial analysis of ManufactCo Industries Inc. Identify key strengths, risks, and any red flags. Provide a summary suitable for an investment committee.",
    "ManufactCo",
    ["pension_underfunding", "customer_concentration", "contract_renewal", "margins", "defense_exposure"],
    {
        "identified_revenue": c("Identified revenue of ~$3.6B", ["3.6", "revenue", "1.8", "growth"], 1),
        "identified_pension_underfunding": c("Flagged pension underfunding of $420M (72% funded)", ["420", "pension", "underfund", "72%", "1.5", "1.08"], 3),
        "identified_customer_concentration": c("Identified 67% revenue from single customer", ["67%", "Northrop", "concentration", "customer", "single"], 2),
        "identified_contract_risk": c("Flagged $2.4B defense contract renewal due Q2 2026", ["2.4", "contract", "renewal", "Q2 2026", "defense"], 2),
        "identified_margin_weakness": c("Noted operating margin of 9.4% below peers", ["9.4", "margin", "peer", "12.1", "below"], 1),
        "provided_recommendation": c("Provided investment recommendation", ["recommend", "risk", "caution", "outlook", "assessment"], 1),
    }
))

sessions.append(s(10, "Research MedDevice Systems",
    "Conduct a thorough financial analysis of MedDevice Systems Corp. Identify key strengths, risks, and any red flags. Provide a summary suitable for an investment committee.",
    "MedDevice",
    ["fda_483", "goodwill_impairment", "product_liability", "revenue_growth", "field_correction"],
    {
        "identified_revenue": c("Identified revenue of ~$2.8B with 6.2% growth", ["2.8", "revenue", "6.2", "growth"], 1),
        "identified_fda_483": c("Flagged FDA Form 483 for Cardiofix facility", ["483", "FDA", "Cardiofix", "quality", "observation"], 2),
        "found_goodwill_impairment": c("Found $210M goodwill write-down from PulseTech in 10-K", ["210", "goodwill", "impairment", "PulseTech", "write-down", "1.2"], 3),
        "identified_field_correction": c("Identified Cardiofix voluntary field correction affecting 12,000 units", ["field correction", "Cardiofix", "12,000", "voluntary", "40"], 2),
        "identified_litigation": c("Noted 340 pending OrthoFlex lawsuits", ["340", "lawsuit", "litigation", "OrthoFlex", "liability", "85"], 2),
        "provided_recommendation": c("Provided investment recommendation", ["recommend", "risk", "caution", "outlook", "assessment"], 1),
    }
))

# ============================================================
# Category B: Risk Deep-Dives (Sessions 11-20)
# ============================================================
sessions.append(s(11, "EnergyX Debt Covenant Risk",
    "Deep-dive into EnergyX's debt covenant situation. What is their current covenant status, how close are they to breach, and what scenarios could trigger a violation?",
    "EnergyX",
    ["covenant_ratio", "ebitda_cushion", "oil_price_sensitivity", "waiver_risk", "refinancing"],
    {
        "identified_covenant_ratio": c("Identified current ratio of 3.2x vs 3.0x minimum", ["3.2", "3.0", "coverage", "interest", "covenant"], 2),
        "identified_cushion": c("Quantified the $45M EBITDA cushion", ["45", "cushion", "EBITDA", "slim", "thin"], 3),
        "modeled_oil_sensitivity": c("Connected oil price to covenant risk", ["oil", "$70", "price", "breach", "scenario"], 2),
        "discussed_consequences": c("Discussed consequences of covenant breach", ["acceleration", "waiver", "lender", "default", "refinanc"], 2),
        "provided_outlook": c("Provided forward-looking risk assessment", ["Q1 2026", "outlook", "risk", "monitor", "watch"], 1),
    }
))

sessions.append(s(12, "BankFirst Credit Quality Deep-Dive",
    "Analyze BankFirst's credit quality deterioration in detail. What is driving the NPL increase, how exposed are they to CRE, and what is the outlook for provisions?",
    "BankFirst",
    ["npl_trajectory", "cre_detail", "office_exposure", "provision_outlook", "harmon_plaza"],
    {
        "identified_npl_trend": c("Traced NPL ratio from 1.9% to 3.8%", ["1.9", "3.8", "NPL", "doubled", "trend"], 2),
        "identified_cre_breakdown": c("Broke down CRE into office/retail segments", ["34.2", "office", "retail", "$6.2", "CRE"], 2),
        "found_harmon_detail": c("Found Harmon Plaza $180M loan detail", ["Harmon", "180", "Portland", "anchor tenant", "vacancy"], 3),
        "provision_analysis": c("Analyzed provision trajectory and adequacy", ["285", "156%", "provision", "adequa", "reserve"], 2),
        "risk_assessment": c("Assessed forward credit risk", ["stress", "deteriorat", "outlook", "recession", "concern"], 1),
    }
))

sessions.append(s(13, "PropCore Rate Sensitivity Analysis",
    "Analyze PropCore's floating-rate debt exposure in detail. Model the impact of different rate scenarios on their financials and dividend sustainability.",
    "PropCore",
    ["floating_rate_pct", "rate_impact", "refinancing_risk", "dividend_coverage", "hedging"],
    {
        "identified_floating_pct": c("Identified 62% floating-rate debt ($2.98B)", ["62", "2.98", "floating", "rate"], 2),
        "modeled_rate_impact": c("Modeled $30M impact per 25bps", ["30", "25bp", "impact", "annual", "cost"], 3),
        "dividend_sustainability": c("Assessed dividend sustainability at 6.8% yield", ["6.8", "dividend", "sustain", "FFO", "coverage"], 2),
        "refinancing_risk": c("Discussed refinancing challenges", ["refinanc", "maturity", "swap", "fixed", "hedg"], 2),
        "scenario_analysis": c("Provided rate scenario analysis", ["scenario", "rate cut", "rate hike", "100bp", "sensitivity"], 1),
    }
))

sessions.append(s(14, "ManufactCo Pension Risk Assessment",
    "Deep-dive into ManufactCo's $420M pension underfunding. What are the risks, required contributions, and potential impact on cash flow and earnings?",
    "ManufactCo",
    ["pension_gap", "funded_status", "contribution_requirements", "cash_flow_impact", "accounting_risk"],
    {
        "identified_pension_gap": c("Quantified $420M underfunding (72% funded)", ["420", "72", "underfund", "pension", "1.5", "1.08"], 3),
        "contribution_analysis": c("Analyzed required pension contributions", ["contribution", "cash flow", "$45M", "annual", "required"], 2),
        "earnings_impact": c("Assessed impact on reported earnings", ["earnings", "expense", "actuarial", "discount rate", "GAAP"], 2),
        "de_risking_options": c("Discussed de-risking strategies", ["de-risk", "annuity", "buyout", "freeze", "close"], 1),
        "comparison_to_peers": c("Compared pension burden to manufacturing peers", ["peer", "sector", "compare", "relative", "burden"], 1),
    }
))

sessions.append(s(15, "MedDevice Regulatory Risk",
    "Deep-dive into MedDevice's FDA regulatory challenges. Analyze the Form 483 findings, Cardiofix field correction, and implications for future product approvals.",
    "MedDevice",
    ["fda_483_detail", "field_correction_scope", "remediation_timeline", "revenue_impact", "approval_risk"],
    {
        "identified_483_findings": c("Detailed the 3 quality system observations", ["483", "three", "3", "quality system", "finding", "observation"], 2),
        "field_correction_scope": c("Quantified 12,000-unit field correction and $40M revenue impact", ["12,000", "40", "field correction", "Cardiofix", "defer"], 3),
        "remediation_plan": c("Discussed remediation requirements and timeline", ["remediat", "corrective", "timeline", "consent", "warning"], 2),
        "pipeline_impact": c("Assessed impact on future product approvals", ["approv", "pipeline", "submission", "delay", "scrutiny"], 1),
        "financial_impact": c("Estimated total financial impact", ["revenue", "cost", "margin", "impact", "guidance"], 1),
    }
))

sessions.append(s(16, "FinTechPay SEC Inquiry Impact",
    "Analyze the SEC's informal inquiry into FinTechPay's revenue recognition practices. What are they investigating, what's the potential impact, and what's the timeline?",
    "FinTechPay",
    ["sec_inquiry_scope", "revenue_recognition", "sign_up_bonuses", "restatement_risk", "timeline"],
    {
        "identified_inquiry_scope": c("Identified SEC inquiry into $48M sign-up bonus timing", ["SEC", "inquiry", "48", "sign-up", "bonus", "revenue recognition"], 3),
        "accounting_issue": c("Explained the amortize vs upfront recognition issue", ["amortiz", "upfront", "recogni", "ASC", "timing"], 2),
        "restatement_risk": c("Assessed potential restatement risk", ["restat", "material", "weak", "control", "audit"], 2),
        "timeline_assessment": c("Estimated investigation timeline", ["timeline", "months", "cooperat", "resol", "settl"], 1),
        "stock_impact": c("Assessed market/stock impact", ["stock", "market", "investor", "confidence", "impact"], 1),
    }
))

sessions.append(s(17, "LogiFlow Contract Renewal Analysis",
    "Analyze LogiFlow's top 3 contract renewals due in 2026. What are the risks if any don't renew, and what's the likely outcome?",
    "LogiFlow",
    ["amazon_contract", "walmart_contract", "target_contract", "renewal_risk", "alternatives"],
    {
        "identified_concentration": c("Identified 38% of revenue in top 3 contracts", ["38%", "top 3", "concentration", "1.98", "revenue"], 2),
        "amazon_detail": c("Detailed Amazon contract: $1.1B, renews June 2026", ["Amazon", "1.1", "June 2026", "largest", "contract"], 3),
        "walmart_target": c("Covered Walmart ($520M) and Target ($360M)", ["Walmart", "520", "Target", "360", "Sept", "Nov"], 2),
        "renewal_risk": c("Assessed likelihood and risk of non-renewal", ["renewal", "negotiat", "competition", "pricing", "risk"], 2),
        "mitigation": c("Suggested diversification or mitigation strategies", ["diversif", "mitigat", "new client", "alternative", "strategy"], 1),
    }
))

sessions.append(s(18, "TechCorp Leadership Transition Impact",
    "Analyze how TechCorp's CEO transition from Martinez to Chen has affected operations, strategy, and financial performance. Reference prior research if available.",
    "TechCorp",
    ["ceo_transition", "strategy_shift", "q3_miss_link", "nova_ai", "execution_risk"],
    {
        "identified_transition": c("Detailed the Martinez→Chen transition", ["Martinez", "Chen", "CEO", "transition", "July"], 2),
        "linked_to_q3_miss": c("Connected Q3 miss to customer uncertainty during transition", ["Q3", "miss", "customer", "uncertainty", "renewal", "delay"], 2),
        "strategy_analysis": c("Analyzed the cloud/AI strategic pivot", ["Nova AI", "cloud", "strategy", "pivot", "transform"], 2),
        "transition_costs": c("Identified $18M transition costs", ["18", "transition cost", "severance", "consulting"], 3),
        "forward_assessment": c("Assessed execution risk under new leadership", ["execution", "risk", "new leadership", "confidence", "outlook"], 1),
    }
))

sessions.append(s(19, "RetailMax Inventory Deterioration",
    "Deep-dive into RetailMax's inventory buildup trend (60→95 days). What's driving it, what are the implications, and how does it compare to retail peers?",
    "RetailMax",
    ["inventory_trend", "demand_signal", "clearance_risk", "seasonal_exposure", "peer_comparison"],
    {
        "identified_trend": c("Traced inventory days: 60→75→85→95", ["60", "75", "85", "95", "inventory days", "trend"], 2),
        "demand_analysis": c("Analyzed whether demand weakness or over-ordering", ["demand", "weak", "over-order", "pre-stock", "sell-through"], 2),
        "found_seasonal_risk": c("Found $280M seasonal merchandise liquidation risk in 10-K", ["280", "seasonal", "liquidat", "clearance", "reduced margin"], 3),
        "margin_impact": c("Assessed margin impact of potential markdowns", ["margin", "markdown", "clear", "write-down", "compress"], 2),
        "peer_comparison": c("Compared to retail peer inventory levels", ["peer", "sector", "median", "compare", "normal"], 1),
    }
))

sessions.append(s(20, "HealthCo Pipeline Dependency",
    "Analyze HealthCo's extreme dependency on the Nexaviron pipeline. What happens in the approve vs reject scenarios, and how sustainable is the business without it?",
    "HealthCo",
    ["nexaviron_probability", "approve_scenario", "reject_scenario", "cardiovex_erosion", "cash_runway"],
    {
        "approval_scenario": c("Modeled bull case: $4.8B market, $1.5-2B peak sales", ["4.8", "1.5", "2.0", "peak", "approve", "bull"], 2),
        "rejection_scenario": c("Modeled bear case: continued erosion, cash depletion", ["reject", "fail", "bear", "erosion", "cash", "survival"], 2),
        "hepatotoxicity_risk": c("Detailed the 2.3% hepatotoxicity signal", ["2.3", "hepatotox", "safety", "liver", "FDA"], 3),
        "cardiovex_erosion": c("Quantified Cardiovex decline (22% YoY to $340M)", ["Cardiovex", "22%", "340", "generic", "erosion"], 2),
        "sustainability": c("Assessed business sustainability without Nexaviron", ["sustain", "burn", "runway", "restructur", "viable"], 1),
    }
))

# ============================================================
# Category C: Growth/Upside (Sessions 21-30)
# ============================================================
sessions.append(s(21, "TechCorp Growth Catalysts",
    "What are TechCorp's key growth catalysts? Analyze the Nova AI platform potential, the cloud partnership, and the path to revenue reacceleration.",
    "TechCorp",
    ["nova_ai_potential", "cloud_partnership", "revenue_reacceleration", "competitive_position", "upside_scenario"],
    {
        "nova_ai_analysis": c("Analyzed Nova AI platform market opportunity", ["Nova AI", "platform", "enterprise", "AI", "opportunity"], 2),
        "partnership_value": c("Quantified cloud partnership: $200M committed minimum", ["200", "partnership", "cloud", "committed", "minimum"], 2),
        "revenue_model": c("Modeled revenue reacceleration path", ["accelerat", "growth", "cloud", "transition", "revenue", "model"], 2),
        "competitive_assessment": c("Assessed competitive positioning", ["competi", "market share", "advantage", "differentiat", "peer"], 1),
        "upside_case": c("Provided bull-case scenario with estimates", ["bull", "upside", "target", "potential", "scenario"], 1),
    }
))

sessions.append(s(22, "HealthCo Nexaviron Upside Scenario",
    "If the FDA approves Nexaviron, model the bull case for HealthCo. What's the revenue trajectory, market share capture, and impact on valuation?",
    "HealthCo",
    ["approval_probability", "peak_sales", "launch_timeline", "market_share", "valuation_impact"],
    {
        "market_sizing": c("Sized the $4.8B autoimmune market opportunity", ["4.8", "autoimmune", "market", "opportunity", "TAM"], 2),
        "peak_sales": c("Estimated peak sales of $1.5-2.0B", ["1.5", "2.0", "peak", "sales", "revenue"], 2),
        "launch_timeline": c("Modeled launch ramp and market penetration", ["launch", "ramp", "penetrat", "year 1", "year 3"], 2),
        "valuation_impact": c("Quantified impact on HealthCo valuation", ["valuation", "P/E", "multiple", "price target", "EPS"], 1),
        "risk_factors": c("Acknowledged remaining risks (hepatotoxicity, competition)", ["risk", "hepatotox", "competition", "launch risk", "execut"], 1),
    }
))

sessions.append(s(23, "RetailMax Expansion Potential",
    "Analyze RetailMax's plan for 50 new stores in FY2026. Can execution improve? Model the upside if same-store sales recover and margins stabilize.",
    "RetailMax",
    ["store_growth", "margin_recovery", "same_store_improvement", "market_opportunity", "execution_risk"],
    {
        "expansion_plan": c("Analyzed the 50-store expansion plan", ["50", "new store", "expansion", "FY2026", "plan"], 2),
        "margin_recovery": c("Modeled margin recovery to 6.0-6.5% target", ["6.0", "6.5", "margin", "recover", "stabiliz"], 2),
        "same_store_thesis": c("Analyzed same-store improvement potential", ["same-store", "1.2", "organic", "improv", "traffic"], 2),
        "funding_sustainability": c("Assessed whether debt-funded growth is sustainable", ["debt", "fund", "sustain", "capital", "6.75"], 1),
        "upside_scenario": c("Provided upside scenario with key assumptions", ["upside", "bull", "scenario", "assum", "target"], 1),
    }
))

sessions.append(s(24, "EnergyX Commodity Upside",
    "If oil prices recover to $85/bbl, remodel EnergyX's financials. What would revenue, margins, and covenant compliance look like?",
    "EnergyX",
    ["oil_price_sensitivity", "revenue_recovery", "margin_expansion", "covenant_cure", "reserve_value"],
    {
        "oil_sensitivity": c("Modeled revenue at $85/bbl vs current $68/bbl", ["85", "68", "oil", "revenue", "model"], 2),
        "margin_recovery": c("Projected margin recovery from 14.2% toward 22%", ["margin", "14.2", "22", "recover", "expand"], 2),
        "covenant_cure": c("Showed covenant compliance restored at higher oil", ["covenant", "3.0", "cure", "compli", "comfortable"], 2),
        "reserve_valuation": c("Discussed reserve value uplift at higher prices", ["reserve", "1.2", "BOE", "value", "asset"], 1),
        "probability_assessment": c("Assessed likelihood of oil recovery scenario", ["probab", "likel", "supply", "demand", "OPEC"], 1),
    }
))

sessions.append(s(25, "BankFirst Recovery Scenario",
    "Model a recovery scenario for BankFirst: if CRE stabilizes and rates drop 100bps, how do financials improve? What's the path to normalization?",
    "BankFirst",
    ["cre_stabilization", "rate_cut_impact", "nim_recovery", "npl_normalization", "dividend_restoration"],
    {
        "rate_impact": c("Modeled NIM expansion from rate cuts", ["NIM", "rate cut", "100bp", "expand", "income"], 2),
        "cre_stabilization": c("Analyzed CRE recovery scenario", ["CRE", "stabiliz", "occupancy", "office", "recover"], 2),
        "npl_normalization": c("Modeled NPL ratio normalization path", ["NPL", "3.8", "normaliz", "peak", "decline"], 2),
        "provision_release": c("Assessed potential provision release", ["provision", "release", "reverse", "reserve", "earnings"], 1),
        "dividend_outlook": c("Discussed dividend restoration potential", ["dividend", "restor", "payout", "sustain", "yield"], 1),
    }
))

sessions.append(s(26, "PropCore Value Play Thesis",
    "Make the bull case for PropCore as a value play: 6.8% yield, below-NAV pricing, occupancy recovery potential. What's the upside if execution improves?",
    "PropCore",
    ["yield_attraction", "nav_discount", "occupancy_recovery", "rate_sensitivity_upside", "management_execution"],
    {
        "yield_analysis": c("Analyzed 6.8% yield attractiveness vs peers", ["6.8", "yield", "attractive", "peer", "income"], 2),
        "nav_assessment": c("Assessed discount to net asset value", ["NAV", "discount", "asset value", "book", "property"], 2),
        "occupancy_recovery": c("Modeled occupancy recovery from 87.3% toward 93%", ["87.3", "93", "occupancy", "recover", "lease"], 2),
        "rate_upside": c("Showed benefits of rate cuts on floating debt", ["rate cut", "floating", "benefit", "savings", "refi"], 1),
        "execution_requirements": c("Identified execution requirements for recovery", ["execut", "management", "maintenance", "340", "capex"], 1),
    }
))

sessions.append(s(27, "ManufactCo Contract Win Scenario",
    "Model the upside for ManufactCo if the defense contract renews and they win additional contracts. What's the revenue and margin trajectory?",
    "ManufactCo",
    ["contract_renewal", "new_wins", "revenue_growth", "margin_expansion", "backlog_growth"],
    {
        "renewal_scenario": c("Modeled $2.4B contract renewal and terms", ["2.4", "renew", "Northrop", "defense", "contract"], 2),
        "new_wins": c("Assessed potential for additional contract wins", ["new", "win", "bid", "additional", "diversif"], 2),
        "margin_improvement": c("Projected margin expansion from scale", ["margin", "9.4", "improv", "scale", "operating leverage"], 2),
        "pension_funding": c("Showed pension funding improvement with higher cash flow", ["pension", "fund", "cash flow", "contribution", "improv"], 1),
        "valuation_upside": c("Quantified valuation upside", ["valuation", "P/E", "14.5", "multiple", "upside"], 1),
    }
))

sessions.append(s(28, "MedDevice Cardiac Division Potential",
    "Analyze MedDevice's strong cardiac division growth. What's the organic growth potential ex-Cardiofix issues and PulseTech goodwill?",
    "MedDevice",
    ["cardiac_growth", "organic_revenue", "pipeline_strength", "ex_cardiofix_margins", "innovation"],
    {
        "cardiac_growth": c("Analyzed cardiac division organic growth rate", ["cardiac", "organic", "growth", "strong", "division"], 2),
        "ex_issues_model": c("Modeled financials excluding Cardiofix and PulseTech", ["ex-Cardiofix", "exclud", "organic", "core", "adjust"], 2),
        "pipeline_value": c("Assessed innovation pipeline value", ["pipeline", "innovation", "R&D", "new product", "approval"], 2),
        "margin_potential": c("Showed margin expansion potential post-remediation", ["margin", "18.6", "expand", "remediat", "normaliz"], 1),
        "growth_thesis": c("Articulated long-term growth thesis", ["long-term", "thesis", "growth", "market leader", "secular"], 1),
    }
))

sessions.append(s(29, "FinTechPay Payments Platform Scale",
    "Analyze FinTechPay's $142B payment volume and growth trajectory. At what scale does the platform become profitable, and what's the market share opportunity?",
    "FinTechPay",
    ["tpv_growth", "unit_economics", "profitability_path", "market_share", "competitive_moat"],
    {
        "tpv_analysis": c("Analyzed $142B total payment volume", ["142", "TPV", "payment volume", "growth", "transaction"], 2),
        "unit_economics": c("Broke down unit economics and take rate", ["unit economics", "take rate", "gross margin", "42.5", "merchant"], 2),
        "profitability_model": c("Modeled path to profitability", ["profitab", "breakeven", "loss", "-85", "scale"], 2),
        "market_share": c("Assessed market share and expansion opportunity", ["market share", "380K", "merchant", "TAM", "penetrat"], 1),
        "competitive_position": c("Evaluated competitive position vs Stripe etc.", ["competit", "Stripe", "moat", "differentiat", "advantage"], 1),
    }
))

sessions.append(s(30, "LogiFlow Fleet Modernization Upside",
    "Analyze LogiFlow's fleet electrification and automation investments. What's the margin improvement potential and competitive advantage?",
    "LogiFlow",
    ["electrification", "automation", "fuel_savings", "margin_expansion", "competitive_advantage"],
    {
        "electrification_plan": c("Analyzed fleet electrification program", ["electric", "fleet", "18,500", "EV", "transition"], 2),
        "fuel_savings": c("Modeled fuel cost reduction from 28.4% of revenue", ["fuel", "28.4", "savings", "diesel", "cost"], 2),
        "automation_impact": c("Assessed automation/technology impact on margins", ["automat", "technology", "efficien", "margin", "labor"], 2),
        "margin_trajectory": c("Projected margin improvement toward peer levels", ["margin", "7.8", "9.5", "peer", "expand", "improv"], 1),
        "investment_case": c("Made the case for fleet modernization ROI", ["ROI", "investment", "return", "payback", "capital"], 1),
    }
))

# ============================================================
# Category D: Comparisons (Sessions 31-50)
# ============================================================
comparison_sessions = [
    (31, "Compare EnergyX vs PropCore — Debt Risk",
     "Compare the debt risk profiles of EnergyX and PropCore. Both have leverage concerns but in different ways. Which is more concerning?",
     ["energyx_debt", "propcore_debt", "covenant_risk", "floating_rate_risk", "comparison"],
     {
         "energyx_debt": c("Detailed EnergyX debt profile (D/E 1.34, covenant)", ["1.34", "EnergyX", "covenant", "3.2", "5.1"], 2),
         "propcore_debt": c("Detailed PropCore debt profile (D/E 2.29, floating)", ["2.29", "PropCore", "floating", "62", "4.8"], 2),
         "risk_comparison": c("Compared which has more acute debt risk", ["more", "acute", "concern", "compare", "worse"], 2),
         "different_risks": c("Distinguished covenant risk vs rate risk", ["covenant", "floating", "different", "type", "nature"], 1),
         "recommendation": c("Recommended which is more investable", ["recommend", "prefer", "better", "investab", "favor"], 1),
     }),
    (32, "Compare BankFirst vs FinTechPay — Financial Services",
     "Compare BankFirst (traditional banking) vs FinTechPay (fintech). Different business models, different risks. Which is better positioned for the next 3 years?",
     ["bankfirst_model", "fintechpay_model", "growth_vs_value", "risk_profiles", "positioning"],
     {
         "bankfirst_analysis": c("Summarized BankFirst's challenges (NPL, CRE)", ["BankFirst", "NPL", "3.8", "CRE", "tradition"], 2),
         "fintechpay_analysis": c("Summarized FinTechPay's challenges (SEC, churn)", ["FinTechPay", "SEC", "churn", "3.8", "profitab"], 2),
         "model_comparison": c("Compared business model strengths/weaknesses", ["model", "fintech", "bank", "disrupt", "advantage"], 2),
         "growth_trajectory": c("Compared growth trajectories", ["growth", "24.8", "-3.8", "trajectory", "revenue"], 1),
         "recommendation": c("Clear recommendation between the two", ["recommend", "prefer", "better", "positioned", "favor"], 1),
     }),
    (33, "Compare TechCorp vs MedDevice — Growth Profiles",
     "Compare TechCorp and MedDevice as growth investments. Both are in innovation-driven sectors. Which offers better risk-adjusted growth?",
     ["techcorp_growth", "meddevice_growth", "risk_profiles", "innovation_comparison", "recommendation"],
     {
         "techcorp_growth": c("Analyzed TechCorp's growth profile (3.1%, Nova AI)", ["TechCorp", "3.1", "Nova AI", "cloud", "growth"], 2),
         "meddevice_growth": c("Analyzed MedDevice's growth profile (6.2%, cardiac)", ["MedDevice", "6.2", "cardiac", "organic", "growth"], 2),
         "risk_comparison": c("Compared risk profiles (covenant vs FDA)", ["covenant", "FDA", "483", "risk", "compare"], 2),
         "valuation": c("Compared valuations (P/E 22.4 vs 28.4)", ["P/E", "22.4", "28.4", "valuation", "multiple"], 1),
         "recommendation": c("Clear investment recommendation", ["recommend", "prefer", "risk-adjust", "better", "favor"], 1),
     }),
    (34, "Compare RetailMax vs LogiFlow — Operations",
     "Compare RetailMax and LogiFlow from an operational execution perspective. Both have execution challenges. Which management team is handling them better?",
     ["retailmax_ops", "logiflow_ops", "management_quality", "execution_risk", "comparison"],
     {
         "retailmax_ops": c("Assessed RetailMax operations (inventory, expansion)", ["RetailMax", "inventory", "95", "expansion", "40 store"], 2),
         "logiflow_ops": c("Assessed LogiFlow operations (fleet, contracts)", ["LogiFlow", "fleet", "contract", "18,500", "on-time"], 2),
         "management_comparison": c("Compared management execution quality", ["management", "execution", "leadership", "quality", "track record"], 2),
         "operational_risk": c("Identified key operational risks for each", ["risk", "concentration", "union", "inventory", "margin"], 1),
         "recommendation": c("Recommended which is better operationally", ["recommend", "better", "prefer", "stronger", "operationally"], 1),
     }),
    (35, "Compare ManufactCo vs EnergyX — Industrial Risk",
     "Compare ManufactCo and EnergyX as industrial investments. Both have major hidden liabilities. Which has the more manageable risk profile?",
     ["manufactco_risks", "energyx_risks", "pension_vs_reserves", "hidden_liabilities", "comparison"],
     {
         "manufactco_risks": c("Summarized ManufactCo risks (pension, concentration)", ["ManufactCo", "pension", "420", "67%", "Northrop"], 2),
         "energyx_risks": c("Summarized EnergyX risks (reserves, covenant)", ["EnergyX", "reserve", "0.68", "covenant", "oil"], 2),
         "liability_comparison": c("Compared hidden liabilities: pension vs reserves", ["pension", "reserve", "off-balance", "hidden", "liability"], 2),
         "manageability": c("Assessed which risk is more manageable", ["manag", "control", "mitigat", "option", "lever"], 1),
         "recommendation": c("Clear investment recommendation", ["recommend", "prefer", "better", "favor", "industrial"], 1),
     }),
    (36, "Compare HealthCo vs MedDevice — Healthcare Sector",
     "Compare HealthCo and MedDevice as healthcare investments. Pharma vs devices, different risk profiles. Which is the better healthcare play?",
     ["healthco_profile", "meddevice_profile", "pipeline_vs_devices", "regulatory_risk", "comparison"],
     {
         "healthco_analysis": c("Summarized HealthCo (Nexaviron, revenue decline)", ["HealthCo", "Nexaviron", "decline", "5.2", "pipeline"], 2),
         "meddevice_analysis": c("Summarized MedDevice (cardiac, FDA 483)", ["MedDevice", "cardiac", "483", "6.2", "growth"], 2),
         "risk_comparison": c("Compared binary (FDA) vs operational (quality) risk", ["binary", "FDA", "quality", "operational", "risk"], 2),
         "growth_comparison": c("Compared growth potential", ["growth", "-5.2", "6.2", "trajectory", "potential"], 1),
         "recommendation": c("Clear healthcare sector recommendation", ["recommend", "prefer", "healthcare", "better", "favor"], 1),
     }),
    (37, "Best Risk-Adjusted Return — Top 3 Portfolio",
     "Across all 10 companies we've analyzed, rank them by risk-adjusted return potential. Select the top 3 for a concentrated portfolio and justify your choices.",
     ["ranking_methodology", "top_3_picks", "risk_adjusted_analysis", "portfolio_construction", "justification"],
     {
         "ranked_all_10": c("Considered all 10 companies in ranking", ["TechCorp", "HealthCo", "RetailMax", "EnergyX", "BankFirst", "PropCore", "ManufactCo", "MedDevice", "FinTechPay", "LogiFlow"], 2),
         "methodology": c("Explained ranking methodology", ["risk-adjust", "Sharpe", "method", "criteria", "framework"], 1),
         "top_3": c("Selected and justified top 3 picks", ["top 3", "select", "pick", "portfolio", "concentrat"], 2),
         "risk_analysis": c("Analyzed correlation and diversification of picks", ["correlat", "diversif", "sector", "overlap", "portfolio"], 2),
         "clear_thesis": c("Provided clear investment thesis for each pick", ["thesis", "why", "catalyst", "upside", "conviction"], 1),
     }),
    (38, "Worst Risk-Adjusted — Bottom 3",
     "Which 3 of our 10 companies have the worst risk-adjusted outlook? Identify the most dangerous positions and explain why.",
     ["ranking_worst", "bottom_3", "specific_risks", "avoidance_thesis", "catalysts_to_watch"],
     {
         "bottom_3": c("Selected and justified bottom 3 picks", ["bottom", "worst", "avoid", "dangerous", "sell"], 2),
         "specific_risks": c("Detailed specific risks for each", ["covenant", "FDA", "NPL", "pension", "SEC"], 2),
         "downside_quantification": c("Quantified downside potential", ["downside", "%", "loss", "scenario", "worst case"], 2),
         "catalyst_timeline": c("Identified near-term negative catalysts", ["catalyst", "timeline", "trigger", "Q1", "Q2", "2026"], 1),
         "comparison_to_top": c("Contrasted with top picks", ["vs", "contrast", "better", "top", "alternative"], 1),
     }),
    (39, "Compare TechCorp vs FinTechPay — Tech Sector",
     "Compare TechCorp (established tech) vs FinTechPay (growth fintech). Different stages, different risks. Which is the better tech investment?",
     ["techcorp_established", "fintechpay_growth", "stage_comparison", "valuation", "recommendation"],
     {
         "techcorp_profile": c("Analyzed TechCorp as established tech play", ["TechCorp", "established", "4.2", "mature", "transition"], 2),
         "fintechpay_profile": c("Analyzed FinTechPay as growth play", ["FinTechPay", "growth", "24.8", "1.6", "loss"], 2),
         "stage_analysis": c("Compared investment stage and risk/reward", ["stage", "mature", "growth", "risk-reward", "profile"], 2),
         "valuation_comparison": c("Compared valuations", ["P/E", "22.4", "valuation", "growth premium", "multiple"], 1),
         "recommendation": c("Clear recommendation between the two", ["recommend", "prefer", "better", "tech", "favor"], 1),
     }),
    (40, "Compare BankFirst vs PropCore — Rate Sensitivity",
     "Both BankFirst and PropCore are significantly affected by interest rates. Compare their rate sensitivity profiles. Who benefits more from rate cuts?",
     ["bankfirst_rate", "propcore_rate", "nim_vs_floating", "cut_scenario", "positioning"],
     {
         "bankfirst_rate": c("Analyzed BankFirst rate sensitivity (NIM)", ["BankFirst", "NIM", "net interest", "rate", "45bp"], 2),
         "propcore_rate": c("Analyzed PropCore rate sensitivity (floating debt)", ["PropCore", "floating", "62%", "30M", "25bp"], 2),
         "comparison": c("Compared who benefits more from rate cuts", ["benefit", "rate cut", "more", "sensitivity", "compare"], 2),
         "scenario_modeling": c("Modeled 100bp cut scenario for both", ["100bp", "scenario", "model", "impact", "improvement"], 1),
         "recommendation": c("Recommended best rate-cut play", ["recommend", "play", "position", "better", "cut"], 1),
     }),
    (41, "Defensive Portfolio — Lowest Downside Risk",
     "From our 10-company universe, construct a 3-4 company defensive portfolio optimized for minimum downside risk. Justify each inclusion.",
     ["defensive_criteria", "selected_companies", "risk_mitigation", "portfolio_characteristics", "stress_test"],
     {
         "criteria": c("Defined defensive criteria (balance sheet, margins, stability)", ["defensive", "criteria", "balance sheet", "stable", "quality"], 1),
         "selections": c("Selected 3-4 companies with justification", ["select", "portfolio", "include", "3", "4", "defensive"], 2),
         "risk_metrics": c("Analyzed portfolio risk metrics", ["D/E", "beta", "downside", "risk", "volatil"], 2),
         "exclusion_reasons": c("Explained why certain companies were excluded", ["exclud", "avoid", "too risky", "concern", "not defensive"], 2),
         "stress_test": c("Stress-tested the portfolio", ["stress", "recession", "scenario", "drawdown", "protecti"], 1),
     }),
    (42, "Growth Portfolio — Maximum Upside",
     "From our 10-company universe, construct a 3-4 company growth portfolio optimized for maximum upside. Accept higher risk for higher reward.",
     ["growth_criteria", "selected_companies", "upside_quantification", "risk_acceptance", "catalyst_timeline"],
     {
         "criteria": c("Defined growth criteria", ["growth", "criteria", "revenue", "catalyst", "upside"], 1),
         "selections": c("Selected 3-4 high-growth companies", ["select", "portfolio", "include", "growth", "catalyst"], 2),
         "upside_targets": c("Quantified upside targets for each", ["upside", "target", "return", "%", "potential"], 2),
         "risk_awareness": c("Acknowledged portfolio risks", ["risk", "volatil", "downside", "loss", "aware"], 2),
         "catalysts": c("Identified growth catalysts and timelines", ["catalyst", "timeline", "trigger", "2026", "when"], 1),
     }),
    (43, "Compare ManufactCo vs LogiFlow — Concentration Risk",
     "Both ManufactCo (67% customer concentration) and LogiFlow (38% contract concentration) face concentration risk. Compare and assess which is more diversified.",
     ["manufactco_concentration", "logiflow_concentration", "diversification", "mitigation_options", "recommendation"],
     {
         "manufactco_concentration": c("Detailed ManufactCo's 67% single-customer exposure", ["67", "Northrop", "single customer", "ManufactCo", "concentrat"], 2),
         "logiflow_concentration": c("Detailed LogiFlow's 38% top-3 contract exposure", ["38", "top 3", "Amazon", "LogiFlow", "concentrat"], 2),
         "comparison": c("Compared concentration types and severity", ["compare", "worse", "more", "diversif", "concentrated"], 2),
         "mitigation": c("Assessed diversification options for each", ["diversif", "mitigat", "new client", "alternative", "option"], 1),
         "recommendation": c("Recommended which has more manageable concentration", ["recommend", "manageable", "better", "prefer", "position"], 1),
     }),
    (44, "Governance Scorecard — All Companies",
     "Create a governance scorecard ranking all 10 companies. Assess board quality, management alignment, transparency, and red flags.",
     ["governance_framework", "ranking", "board_quality", "transparency", "red_flags"],
     {
         "framework": c("Defined governance scoring framework", ["governance", "framework", "criteria", "score", "assess"], 1),
         "all_10_ranked": c("Ranked all 10 companies on governance", ["rank", "all", "10", "score", "governance"], 2),
         "worst_governance": c("Identified worst governance (Meridian $42M, SEC inquiry)", ["Meridian", "42", "SEC", "worst", "concern", "Whitfield"], 3),
         "best_governance": c("Identified best governance practices", ["best", "strong", "transparent", "align", "board"], 1),
         "recommendations": c("Made governance-based investment recommendations", ["recommend", "avoid", "prefer", "governance", "factor"], 1),
     }),
    (45, "Compare EnergyX vs LogiFlow — Commodity Exposure",
     "Both EnergyX and LogiFlow have significant commodity exposure (oil). Compare how oil price movements affect each differently.",
     ["energyx_oil_direct", "logiflow_fuel_cost", "sensitivity_comparison", "hedging", "positioning"],
     {
         "energyx_exposure": c("Analyzed EnergyX direct oil revenue exposure", ["EnergyX", "oil", "revenue", "direct", "$82", "$68"], 2),
         "logiflow_exposure": c("Analyzed LogiFlow fuel cost exposure (28.4%)", ["LogiFlow", "fuel", "28.4", "cost", "$65M", "per $10"], 2),
         "opposite_impacts": c("Noted opposing impacts: EnergyX benefits, LogiFlow hurt by high oil", ["opposite", "benefit", "hurt", "inverse", "hedge"], 2),
         "hedging_analysis": c("Assessed hedging strategies", ["hedge", "unhedge", "protect", "strategy", "exposure"], 1),
         "portfolio_implication": c("Discussed portfolio diversification benefit", ["portfolio", "diversif", "natural hedge", "pair", "offset"], 1),
     }),
    (46, "Income Portfolio — Best Dividend/Yield Plays",
     "Which companies in our universe offer the best income/yield opportunity? Consider PropCore's 6.8% yield, BankFirst's dividend, and others.",
     ["yield_comparison", "dividend_sustainability", "payout_ratios", "income_portfolio", "risk_assessment"],
     {
         "yield_comparison": c("Compared yields across all companies", ["yield", "dividend", "compare", "PropCore", "6.8"], 2),
         "sustainability": c("Assessed dividend sustainability for each", ["sustain", "payout", "coverage", "cash flow", "safe"], 2),
         "propcore_yield": c("Analyzed PropCore 6.8% yield risk/reward", ["PropCore", "6.8", "yield", "REIT", "risk"], 2),
         "portfolio_construction": c("Constructed income portfolio", ["portfolio", "income", "select", "diversif", "allocation"], 1),
         "total_return": c("Considered total return (yield + price appreciation)", ["total return", "price", "appreciation", "capital", "combined"], 1),
     }),
    (47, "Compare HealthCo vs FinTechPay — Binary Risk Events",
     "Both HealthCo (FDA decision) and FinTechPay (SEC inquiry) face binary risk events. Compare the probability, impact, and timeline of each.",
     ["healthco_binary", "fintechpay_binary", "probability_comparison", "impact_comparison", "positioning"],
     {
         "healthco_event": c("Analyzed Nexaviron FDA decision as binary event", ["HealthCo", "Nexaviron", "FDA", "binary", "approve", "reject"], 2),
         "fintechpay_event": c("Analyzed SEC inquiry as binary risk", ["FinTechPay", "SEC", "inquiry", "restat", "binary"], 2),
         "probability": c("Compared probability of negative outcomes", ["probab", "likelihood", "odds", "percent", "expect"], 2),
         "impact_sizing": c("Compared potential financial impact", ["impact", "downside", "revenue", "valuation", "stock"], 1),
         "recommendation": c("Recommended positioning for each", ["recommend", "position", "hedge", "avoid", "wait"], 1),
     }),
    (48, "Sector Rotation Strategy",
     "Based on our analysis of all 10 companies across 6 sectors, which sectors are best and worst positioned for the next 12 months? Recommend sector allocation.",
     ["sector_analysis", "macro_outlook", "best_sectors", "worst_sectors", "allocation"],
     {
         "all_sectors": c("Analyzed all sectors represented", ["tech", "healthcare", "retail", "energy", "bank", "REIT", "manufact", "fintech", "logistics"], 2),
         "macro_context": c("Connected to macro environment (rates, economy)", ["macro", "rate", "economy", "GDP", "inflation", "recession"], 2),
         "best_positioned": c("Identified best-positioned sectors", ["best", "overweight", "favor", "positioned", "sector"], 2),
         "worst_positioned": c("Identified worst-positioned sectors", ["worst", "underweight", "avoid", "concern", "sector"], 1),
         "allocation": c("Provided specific allocation recommendations", ["allocat", "weight", "%", "portfolio", "recommend"], 1),
     }),
    (49, "Compare MedDevice vs ManufactCo — Hidden Liabilities",
     "Both MedDevice ($1.2B goodwill, $85M litigation) and ManufactCo ($420M pension) carry significant hidden liabilities. Compare and assess.",
     ["meddevice_liabilities", "manufactco_liabilities", "off_balance_sheet", "impact_comparison", "recommendation"],
     {
         "meddevice_liabilities": c("Detailed MedDevice hidden liabilities ($1.2B goodwill, $85M accrued)", ["MedDevice", "1.2", "goodwill", "85", "litigation", "OrthoFlex"], 2),
         "manufactco_liabilities": c("Detailed ManufactCo hidden liability ($420M pension)", ["ManufactCo", "420", "pension", "underfund", "off-balance"], 2),
         "comparison": c("Compared magnitude and controllability", ["compare", "larger", "control", "manage", "worse"], 2),
         "earnings_impact": c("Assessed earnings impact for each", ["earnings", "impairment", "210", "write-down", "expense"], 2),
         "recommendation": c("Recommended which is more concerning", ["recommend", "concern", "prefer", "avoid", "manageable"], 1),
     }),
    (50, "Full Portfolio Risk Matrix",
     "Create a comprehensive risk matrix for all 10 companies. Map key risks (debt, regulatory, concentration, macro) and identify correlations and portfolio-level vulnerabilities.",
     ["risk_taxonomy", "all_10_mapped", "correlations", "portfolio_vulnerabilities", "diversification"],
     {
         "all_risks_mapped": c("Mapped key risks for all 10 companies", ["TechCorp", "HealthCo", "RetailMax", "EnergyX", "BankFirst", "PropCore", "ManufactCo", "MedDevice", "FinTechPay", "LogiFlow"], 2),
         "risk_categories": c("Organized into risk categories", ["debt", "regulat", "concentrat", "macro", "governance", "operational"], 2),
         "correlations": c("Identified correlated risks across portfolio", ["correlat", "cluster", "systemic", "common", "overlap"], 2),
         "vulnerabilities": c("Identified portfolio-level vulnerabilities", ["portfolio", "vulnerab", "exposure", "concentrated", "gap"], 2),
         "mitigation": c("Recommended risk mitigation strategies", ["mitigat", "diversif", "hedge", "reduce", "strategy"], 1),
     }),
]

for args in comparison_sessions:
    sessions.append(s(args[0], args[1], args[2], "comparison", args[3], args[4]))

# ============================================================
# Category E: Follow-ups (Sessions 51-75)
# ============================================================
followup_sessions = [
    (51, "Follow-up: Update on EnergyX Covenant",
     "Recall our earlier analysis of EnergyX. Summarize the covenant situation — what's the current ratio, what's the cushion, and what oil price triggers a breach?",
     ["covenant_recall", "cushion_detail", "oil_trigger", "timeline", "recommendation"],
     {
         "recalled_covenant": c("Recalled covenant ratio of 3.2x vs 3.0x minimum", ["3.2", "3.0", "covenant", "interest coverage", "ratio"], 3),
         "recalled_cushion": c("Recalled $45M EBITDA cushion", ["45", "cushion", "EBITDA", "slim", "breach"], 2),
         "oil_trigger": c("Recalled oil price trigger level ($70/bbl)", ["$70", "oil", "trigger", "below", "breach"], 2),
         "timeline": c("Discussed Q1 2026 timeline", ["Q1 2026", "timeline", "near-term", "months", "imminent"], 1),
         "action": c("Recommended monitoring action", ["monitor", "watch", "action", "hedge", "recommend"], 1),
     }),
    (52, "Follow-up: BankFirst NPL Trend",
     "Based on our prior analysis of BankFirst, what's the trajectory of their NPL ratio? Is it stabilizing or worsening? What's your current assessment?",
     ["npl_trajectory", "stabilization_view", "provision_adequacy", "cre_outlook", "assessment"],
     {
         "recalled_npl": c("Recalled NPL ratio increase from 1.9% to 3.8%", ["1.9", "3.8", "NPL", "doubled", "trajectory"], 3),
         "recalled_cre": c("Recalled CRE exposure details", ["CRE", "34.2", "office", "Harmon", "exposure"], 2),
         "trend_assessment": c("Assessed whether trend is stabilizing or worsening", ["trend", "stabiliz", "worsen", "peak", "trajectory"], 2),
         "provision_view": c("Assessed provision adequacy", ["provision", "285", "adequa", "reserve", "sufficient"], 1),
         "outlook": c("Provided updated outlook", ["outlook", "assess", "monitor", "expect", "forecast"], 1),
     }),
    (53, "Client: PropCore Dividend Safety",
     "A client asks: 'Is PropCore's 6.8% dividend sustainable given what we found about their finances? Should I rely on this for income?'",
     ["dividend_yield", "coverage_ratio", "floating_rate_impact", "occupancy_impact", "recommendation"],
     {
         "recalled_yield": c("Recalled 6.8% dividend yield and FFO", ["6.8", "dividend", "yield", "FFO", "2.85"], 2),
         "rate_impact": c("Connected floating-rate debt to dividend risk", ["floating", "62%", "rate", "cost", "dividend", "30M"], 3),
         "occupancy_threat": c("Connected occupancy decline to revenue risk", ["87.3", "occupancy", "decline", "revenue", "rental"], 2),
         "coverage_analysis": c("Analyzed dividend coverage ratio", ["coverage", "payout", "ratio", "sustain", "FFO"], 2),
         "recommendation": c("Clear recommendation on dividend safety", ["recommend", "safe", "cut", "risk", "income", "rely"], 1),
     }),
    (54, "Follow-up: ManufactCo Contract Status",
     "Recall our research on ManufactCo. What's the status of the $2.4B defense contract renewal? When is it due and what's at risk?",
     ["contract_value", "renewal_date", "customer_dependency", "alternatives", "risk_assessment"],
     {
         "recalled_contract": c("Recalled $2.4B contract with Northrop Grumman", ["2.4", "Northrop", "contract", "defense", "renewal"], 3),
         "recalled_timing": c("Recalled Q2 2026 renewal date", ["Q2 2026", "renewal", "due", "timeline", "expires"], 2),
         "concentration_context": c("Contextualized 67% revenue dependency", ["67", "concentrat", "dependency", "single customer", "revenue"], 2),
         "risk_scenario": c("Assessed non-renewal scenario", ["non-renewal", "lose", "risk", "alternative", "impact"], 1),
         "recommendation": c("Provided action recommendation", ["recommend", "monitor", "hedge", "diversif", "action"], 1),
     }),
    (55, "Client: MedDevice Litigation Exposure",
     "A client asks about MedDevice litigation. Summarize the legal risks we identified, the potential financial exposure, and whether it's priced into the stock.",
     ["orthoFlex_lawsuits", "accrued_liability", "settlement_potential", "stock_impact", "recommendation"],
     {
         "recalled_lawsuits": c("Recalled 340 pending OrthoFlex lawsuits", ["340", "OrthoFlex", "lawsuit", "litigation", "pending"], 3),
         "recalled_accrual": c("Recalled $85M accrued liability", ["85", "accrued", "liability", "provision", "legal"], 2),
         "settlement_analysis": c("Assessed potential settlement range", ["settlement", "range", "cost", "exposure", "estimate"], 2),
         "stock_pricing": c("Assessed whether priced into stock", ["priced in", "stock", "market", "discount", "reflect"], 1),
         "recommendation": c("Client recommendation on litigation risk", ["recommend", "concern", "manageable", "material", "watch"], 1),
     }),
    (56, "Follow-up: FinTechPay SEC Timeline",
     "What did we find about the SEC inquiry into FinTechPay? What's the likely timeline and potential impact on the company?",
     ["inquiry_scope", "revenue_impact", "timeline", "restatement_risk", "outlook"],
     {
         "recalled_inquiry": c("Recalled SEC inquiry into $48M sign-up bonus timing", ["SEC", "48", "sign-up", "bonus", "inquiry", "revenue recognition"], 3),
         "timeline_estimate": c("Estimated investigation timeline", ["timeline", "months", "resolution", "cooperat", "settle"], 2),
         "restatement_assessment": c("Assessed restatement probability", ["restat", "material", "probab", "adjustment", "impact"], 2),
         "stock_impact": c("Assessed impact on stock and fundraising", ["stock", "market", "investor", "confidence", "fundrais"], 1),
         "recommendation": c("Provided recommendation", ["recommend", "monitor", "risk", "wait", "resolution"], 1),
     }),
    (57, "Follow-up: LogiFlow Union Risk",
     "Recall our analysis of LogiFlow. Summarize the union negotiation risk and potential impact of a work stoppage.",
     ["teamsters_cba", "expiry_date", "strike_history", "financial_impact", "mitigation"],
     {
         "recalled_union": c("Recalled Teamsters CBA expiring March 2026", ["Teamsters", "March 2026", "CBA", "union", "8,400"], 3),
         "recalled_strike": c("Recalled 2022 strike history (14 days, $45M)", ["2022", "strike", "14 day", "45M", "work stoppage"], 2),
         "financial_impact": c("Estimated potential financial impact of new stoppage", ["impact", "revenue", "cost", "disrupt", "loss"], 2),
         "negotiation_outlook": c("Assessed negotiation outlook", ["negotiat", "demand", "wage", "outlook", "resolution"], 1),
         "mitigation": c("Discussed contingency planning", ["contingency", "mitigat", "plan", "alternative", "prepare"], 1),
     }),
    (58, "Client: TechCorp Debt Covenant Update",
     "A client asks about TechCorp's covenant waiver. When does it expire and what happens if the waiver is not renewed? Is TechCorp at risk of default?",
     ["waiver_expiry", "renewal_probability", "default_risk", "remediation_options", "recommendation"],
     {
         "recalled_waiver": c("Recalled waiver expiring March 2026", ["March 2026", "waiver", "expire", "temporary", "lender"], 3),
         "recalled_breach": c("Recalled 1.83x ratio vs 1.5x covenant", ["1.83", "1.5", "breach", "leverage ratio", "covenant"], 2),
         "default_scenario": c("Assessed default risk if waiver lapses", ["default", "acceleration", "credit facility", "3.5 billion", "risk"], 2),
         "remediation": c("Discussed remediation options", ["amend", "remediat", "pay down", "asset sale", "option"], 1),
         "recommendation": c("Clear client recommendation", ["recommend", "concern", "monitor", "position", "action"], 1),
     }),
    (59, "Follow-up: HealthCo Cash Runway",
     "Based on our analysis, how long can HealthCo sustain operations if Nexaviron is rejected? What's the cash burn rate and survival timeline?",
     ["cash_position", "burn_rate", "runway_months", "cost_cuts", "survival_options"],
     {
         "recalled_cash": c("Recalled $450M cash, down from $580M", ["450", "580", "cash", "declining", "burn"], 3),
         "burn_analysis": c("Calculated quarterly cash burn rate", ["burn", "quarter", "rate", "130M", "operating"], 2),
         "runway_estimate": c("Estimated survival runway in quarters/years", ["runway", "quarter", "year", "surviv", "sustain"], 2),
         "cost_cut_impact": c("Connected $150M cost reduction program", ["150", "cost", "reduction", "restructur", "800 job"], 1),
         "survival_options": c("Discussed survival options without Nexaviron", ["option", "asset sale", "partner", "acquir", "merge"], 1),
     }),
    (60, "Client: RetailMax vs Peers",
     "A client asks: how does RetailMax's inventory problem compare to what we've seen at other companies in our portfolio? Is this unique to RetailMax?",
     ["inventory_comparison", "peer_context", "sector_assessment", "unique_vs_systemic", "recommendation"],
     {
         "recalled_inventory": c("Recalled RetailMax inventory days: 60→95", ["60", "95", "inventory", "RetailMax", "days"], 3),
         "peer_comparison": c("Compared to other portfolio companies' inventory/working capital", ["peer", "compare", "other", "portfolio", "sector"], 2),
         "systemic_assessment": c("Assessed whether systemic vs company-specific", ["systemic", "specific", "unique", "company", "sector-wide"], 2),
         "retail_context": c("Provided retail sector context", ["retail", "consumer", "demand", "spending", "slowdown"], 1),
         "recommendation": c("Client recommendation", ["recommend", "concern", "monitor", "position", "action"], 1),
     }),
    (61, "Follow-up: EnergyX Reserve Life",
     "How many years of reserves does EnergyX have at current production and replacement rates? Is depletion accelerating?",
     ["reserve_volume", "replacement_ratio", "depletion_rate", "reserve_life", "strategic_options"],
     {
         "recalled_reserves": c("Recalled 1.2B BOE proven reserves", ["1.2", "BOE", "reserve", "proven", "billion"], 2),
         "recalled_replacement": c("Recalled 0.68x replacement ratio", ["0.68", "replacement", "ratio", "depleting", "faster"], 3),
         "reserve_life": c("Calculated reserve life in years", ["year", "life", "production", "rate", "deplet"], 2),
         "acceleration": c("Assessed whether depletion is accelerating", ["accelerat", "trend", "worsen", "invest", "capex"], 1),
         "strategic_options": c("Discussed strategic options (acquisition, exploration)", ["acqui", "explor", "strategic", "option", "replace"], 1),
     }),
    (62, "Client: BankFirst Dividend Risk",
     "Based on our analysis, should BankFirst cut its dividend? What's the payout ratio, and can they sustain it given NPL and provision trends?",
     ["payout_ratio", "earnings_pressure", "npl_impact", "regulatory_pressure", "recommendation"],
     {
         "recalled_earnings": c("Recalled net income of $245M and EPS $1.48", ["245", "1.48", "earnings", "net income", "EPS"], 2),
         "provision_pressure": c("Connected $285M provisions to earnings pressure", ["285", "provision", "pressure", "earnings", "squeeze"], 3),
         "payout_analysis": c("Analyzed dividend payout ratio sustainability", ["payout", "ratio", "sustain", "coverage", "dividend"], 2),
         "regulatory_context": c("Discussed regulatory pressure on dividends", ["regulat", "stress test", "Fed", "capital", "buffer"], 1),
         "recommendation": c("Clear recommendation on dividend action", ["cut", "maintain", "reduce", "recommend", "dividend"], 1),
     }),
    (63, "Follow-up: PropCore Refinancing Risk",
     "Recall PropCore's floating-rate debt situation. If rates stay elevated through 2026, what's the refinancing risk and cost impact?",
     ["floating_debt_detail", "rate_scenario", "refinancing_wall", "cost_escalation", "options"],
     {
         "recalled_floating": c("Recalled $2.98B floating-rate debt (62%)", ["2.98", "62", "floating", "rate", "debt"], 3),
         "rate_scenario": c("Modeled elevated rate scenario through 2026", ["elevated", "rate", "2026", "scenario", "persist"], 2),
         "refinancing_timeline": c("Identified debt maturity/refinancing timeline", ["matur", "refinanc", "timeline", "wall", "due"], 2),
         "cost_impact": c("Quantified additional interest cost", ["cost", "interest", "30M", "million", "additional"], 1),
         "strategic_options": c("Discussed hedging/swap options", ["hedge", "swap", "fixed", "convert", "option"], 1),
     }),
    (64, "Client: ManufactCo Alternative Revenue",
     "If ManufactCo loses the Northrop contract, what's the revenue impact and do they have alternatives? Can they survive losing 67% of revenue?",
     ["revenue_impact", "alternative_customers", "restructuring_needs", "survival_analysis", "recommendation"],
     {
         "recalled_dependency": c("Recalled 67% revenue from Northrop ($2.4B)", ["67", "2.4", "Northrop", "revenue", "dependency"], 3),
         "revenue_scenario": c("Modeled revenue impact of contract loss", ["loss", "impact", "decline", "revenue", "$1.2B remaining"], 2),
         "alternatives": c("Assessed alternative customer pipeline", ["alternative", "customer", "bid", "diversif", "pipeline"], 2),
         "restructuring": c("Discussed restructuring requirements", ["restructur", "cost cut", "downsize", "right-size", "surviv"], 1),
         "recommendation": c("Survival assessment and recommendation", ["surviv", "viable", "recommend", "diversif", "urgent"], 1),
     }),
    (65, "Follow-up: MedDevice Goodwill Write-down",
     "How much goodwill impairment is expected for MedDevice's PulseTech acquisition, and what's the impact on reported earnings?",
     ["goodwill_amount", "impairment_size", "earnings_impact", "acquisition_performance", "outlook"],
     {
         "recalled_goodwill": c("Recalled $1.2B goodwill from PulseTech acquisition", ["1.2", "goodwill", "PulseTech", "acquisition", "billion"], 2),
         "recalled_impairment": c("Recalled $210M expected write-down", ["210", "impairment", "write-down", "35% below", "projection"], 3),
         "earnings_impact": c("Calculated earnings impact of write-down", ["earnings", "EPS", "impact", "charge", "non-cash"], 2),
         "acquisition_review": c("Assessed PulseTech acquisition performance", ["PulseTech", "acquisition", "performance", "below", "overpaid"], 1),
         "forward_risk": c("Assessed risk of additional impairment", ["additional", "further", "risk", "future", "remaining"], 1),
     }),
    (66, "Client: FinTechPay Churn Fix",
     "What's driving FinTechPay's merchant churn increase (2.1% to 3.8%) and can management fix it? Is this a temporary or structural issue?",
     ["churn_drivers", "churn_trend", "management_response", "structural_vs_temporary", "recommendation"],
     {
         "recalled_churn": c("Recalled churn increase from 2.1% to 3.8% monthly", ["2.1", "3.8", "churn", "merchant", "doubled"], 3),
         "driver_analysis": c("Analyzed drivers of churn increase", ["driver", "competi", "pricing", "service", "Stripe"], 2),
         "management_response": c("Assessed management's ability to address churn", ["management", "fix", "address", "strateg", "retention"], 2),
         "structural_view": c("Assessed whether temporary or structural", ["structural", "temporary", "cyclical", "permanent", "trend"], 1),
         "recommendation": c("Recommendation on churn outlook", ["recommend", "outlook", "improv", "concern", "monitor"], 1),
     }),
    (67, "Follow-up: LogiFlow Amazon Dependency",
     "How dependent is LogiFlow on the Amazon contract? If Amazon doesn't renew the $1.1B contract, what's the financial impact and can LogiFlow survive?",
     ["amazon_contract_size", "revenue_dependency", "replacement_feasibility", "financial_impact", "survival"],
     {
         "recalled_amazon": c("Recalled $1.1B Amazon contract (21% of revenue)", ["1.1", "Amazon", "21%", "largest", "contract"], 3),
         "recalled_timing": c("Recalled June 2026 renewal date", ["June 2026", "renewal", "expires", "timeline"], 2),
         "replacement_analysis": c("Assessed ability to replace Amazon revenue", ["replace", "new client", "alternative", "pipeline", "capacity"], 2),
         "financial_modeling": c("Modeled financial impact of non-renewal", ["impact", "revenue", "margin", "loss", "decline"], 1),
         "recommendation": c("Survival assessment and action items", ["surviv", "action", "recommend", "contingency", "diversif"], 1),
     }),
    (68, "Client: Portfolio Debt Summary",
     "A client asks: give me a comprehensive debt risk summary across all companies we've analyzed. Which have the most and least concerning debt profiles?",
     ["all_company_debt", "ranking", "covenant_risks", "most_concerning", "least_concerning"],
     {
         "all_10_covered": c("Covered debt profiles for all 10 companies", ["TechCorp", "HealthCo", "RetailMax", "EnergyX", "BankFirst", "PropCore", "ManufactCo", "MedDevice", "FinTechPay", "LogiFlow"], 2),
         "d_e_comparison": c("Compared D/E ratios across portfolio", ["D/E", "debt-to-equity", "ratio", "compare", "range"], 2),
         "most_concerning": c("Identified most concerning (PropCore 2.29, TechCorp 1.81)", ["PropCore", "2.29", "TechCorp", "1.81", "most", "concern"], 3),
         "covenant_risks": c("Flagged covenant risk companies", ["covenant", "breach", "waiver", "EnergyX", "TechCorp"], 2),
         "recommendation": c("Ranked debt risk and recommended actions", ["rank", "recommend", "action", "monitor", "reduce"], 1),
     }),
    (69, "Follow-up: Healthcare Portfolio View",
     "Summarize the key risks across our healthcare holdings (HealthCo and MedDevice). What's the overall healthcare portfolio risk?",
     ["healthco_risks", "meddevice_risks", "correlation", "portfolio_risk", "recommendation"],
     {
         "healthco_summary": c("Recalled key HealthCo risks (Nexaviron, decline, $42M)", ["HealthCo", "Nexaviron", "decline", "42", "Meridian"], 2),
         "meddevice_summary": c("Recalled key MedDevice risks (FDA 483, goodwill, litigation)", ["MedDevice", "483", "goodwill", "210", "OrthoFlex"], 2),
         "correlation": c("Assessed correlation of healthcare risks", ["correlat", "FDA", "regulat", "healthcare", "sector"], 2),
         "combined_exposure": c("Quantified combined healthcare exposure", ["combined", "portfolio", "weight", "exposure", "healthcare"], 1),
         "recommendation": c("Portfolio-level healthcare recommendation", ["recommend", "reduce", "maintain", "rebalance", "diversif"], 1),
     }),
    (70, "Client: Worst-Case Scenarios",
     "For each company in our portfolio, what's the single biggest risk that could cause >20% downside? Rank them by probability of occurrence.",
     ["all_10_worst_case", "downside_quantification", "probability_ranking", "catalysts", "hedging"],
     {
         "all_10_risks": c("Identified worst-case risk for each company", ["TechCorp", "HealthCo", "RetailMax", "EnergyX", "BankFirst", "PropCore", "ManufactCo", "MedDevice", "FinTechPay", "LogiFlow"], 2),
         "downside_sizing": c("Quantified >20% downside scenarios", ["20%", "downside", "loss", "decline", "worst case"], 2),
         "probability_ranking": c("Ranked by probability of occurrence", ["probab", "rank", "likelihood", "most likely", "imminent"], 2),
         "specific_catalysts": c("Named specific trigger catalysts", ["catalyst", "trigger", "covenant", "FDA", "contract", "SEC"], 2),
         "hedging_strategies": c("Suggested portfolio-level hedging", ["hedge", "protect", "put", "reduce", "mitigat"], 1),
     }),
    (71, "Follow-up: Rate Sensitivity Across Portfolio",
     "Which of our companies are most hurt by rising rates? Recall our analysis and rank rate sensitivity across the portfolio.",
     ["rate_sensitive_companies", "ranking", "magnitude", "hedging_status", "positioning"],
     {
         "propcore_sensitivity": c("Recalled PropCore's 62% floating-rate exposure", ["PropCore", "62%", "floating", "$30M", "per 25bp"], 3),
         "bankfirst_sensitivity": c("Recalled BankFirst NIM compression", ["BankFirst", "NIM", "45bp", "compress", "rate"], 2),
         "all_ranked": c("Ranked all companies by rate sensitivity", ["rank", "most", "least", "sensitive", "rate"], 2),
         "hedging_status": c("Assessed hedging positions", ["hedge", "unhedge", "protect", "exposure", "natural"], 1),
         "positioning": c("Recommended portfolio positioning for rates", ["position", "recommend", "overweight", "underweight", "tilt"], 1),
     }),
    (72, "Client: ESG Risk Assessment",
     "Based on everything we've analyzed, which companies have the most concerning governance or ESG-related issues? Rank them.",
     ["governance_issues", "environmental_risks", "social_risks", "esg_ranking", "recommendation"],
     {
         "governance_flags": c("Recalled governance red flags (HealthCo $42M, TechCorp CEO, FinTechPay SEC)", ["Meridian", "42M", "Whitfield", "SEC", "governance"], 3),
         "environmental": c("Assessed environmental risks (EnergyX, LogiFlow)", ["EnergyX", "LogiFlow", "environment", "emission", "climate"], 2),
         "social_risks": c("Assessed social risks (layoffs, union, pensions)", ["layoff", "union", "pension", "employee", "social"], 2),
         "ranking": c("Ranked companies by ESG risk", ["rank", "ESG", "worst", "best", "score"], 1),
         "recommendation": c("ESG-informed investment recommendations", ["recommend", "ESG", "screen", "exclude", "improve"], 1),
     }),
    (73, "Follow-up: Industrial Sector Outlook",
     "Summarize our findings on ManufactCo, LogiFlow, and EnergyX. What's the overall industrial/cyclical sector outlook based on our research?",
     ["manufactco_summary", "logiflow_summary", "energyx_summary", "sector_outlook", "recommendation"],
     {
         "manufactco_recall": c("Recalled ManufactCo key findings (pension, concentration)", ["ManufactCo", "pension", "420", "67%", "Northrop"], 2),
         "logiflow_recall": c("Recalled LogiFlow key findings (contracts, union)", ["LogiFlow", "contract", "38%", "Teamsters", "Amazon"], 2),
         "energyx_recall": c("Recalled EnergyX key findings (reserves, covenant)", ["EnergyX", "reserve", "0.68", "covenant", "3.2"], 2),
         "sector_synthesis": c("Synthesized industrial sector outlook", ["industrial", "cyclical", "sector", "outlook", "macro"], 2),
         "recommendation": c("Sector allocation recommendation", ["recommend", "allocat", "weight", "industrial", "exposure"], 1),
     }),
    (74, "Client: Near-Term Catalysts",
     "Which companies in our portfolio have the most significant near-term catalysts in the next 6 months? List them with expected dates.",
     ["catalyst_list", "dates", "impact_assessment", "probability", "positioning"],
     {
         "all_catalysts": c("Listed catalysts for multiple companies", ["catalyst", "event", "trigger", "date", "timeline"], 2),
         "healthco_fda": c("Recalled HealthCo Nexaviron FDA decision Q2 2026", ["Nexaviron", "FDA", "Q2 2026", "decision", "PDUFA"], 2),
         "contract_renewals": c("Recalled ManufactCo and LogiFlow contract timelines", ["ManufactCo", "Q2 2026", "LogiFlow", "June 2026", "Amazon", "Northrop"], 3),
         "covenant_dates": c("Recalled TechCorp waiver March 2026, EnergyX Q1 risk", ["March 2026", "waiver", "TechCorp", "EnergyX", "Q1"], 2),
         "positioning": c("Recommended positioning ahead of catalysts", ["position", "ahead", "before", "prepare", "recommend"], 1),
     }),
    (75, "Follow-up: Regulatory Risk Summary",
     "Across all companies, summarize the regulatory risks we've identified. Which companies face the most regulatory exposure?",
     ["regulatory_risks", "fda", "sec", "covenant_compliance", "ranking"],
     {
         "fda_risks": c("Recalled FDA risks (HealthCo Nexaviron, MedDevice 483)", ["FDA", "Nexaviron", "483", "HealthCo", "MedDevice"], 3),
         "sec_risk": c("Recalled SEC inquiry into FinTechPay", ["SEC", "FinTechPay", "inquiry", "revenue recognition"], 2),
         "financial_regulation": c("Recalled BankFirst regulatory risks (stress tests, capital)", ["BankFirst", "stress test", "Fed", "regulat", "capital"], 2),
         "covenant_compliance": c("Recalled covenant compliance issues (TechCorp, EnergyX)", ["covenant", "TechCorp", "EnergyX", "breach", "waiver"], 2),
         "ranking": c("Ranked by regulatory exposure", ["rank", "most", "exposure", "regulat", "risk"], 1),
     }),
]

for args in followup_sessions:
    sessions.append(s(args[0], args[1], args[2], "follow_up", args[3], args[4]))

# ============================================================
# Category F: Thematic Synthesis (Sessions 76-88)
# ============================================================
synthesis_sessions = [
    (76, "Thematic: Companies Most Likely to Violate Covenants in 2026",
     "Analyze across all companies in our portfolio: which are most likely to violate debt covenants in 2026? Rank by probability and impact.",
     ["covenant_screening", "probability_ranking", "impact_assessment", "monitoring_plan", "portfolio_impact"],
     {
         "techcorp_covenant": c("Recalled TechCorp covenant breach and waiver", ["TechCorp", "1.83", "1.5x", "waiver", "March 2026"], 3),
         "energyx_covenant": c("Recalled EnergyX near-breach (3.2x vs 3.0x)", ["EnergyX", "3.2", "3.0", "45M", "cushion"], 3),
         "ranking": c("Ranked all companies by covenant violation probability", ["rank", "probab", "most likely", "least likely", "violat"], 2),
         "impact_analysis": c("Assessed impact of each potential violation", ["impact", "acceleration", "default", "refinanc", "consequence"], 2),
         "monitoring": c("Proposed monitoring framework", ["monitor", "watch", "trigger", "alert", "framework"], 1),
     }),
    (77, "Thematic: Hidden Liabilities Across the Portfolio",
     "Map all hidden or off-balance-sheet liabilities across our 10-company portfolio. Which companies have the most concerning undisclosed risks?",
     ["pension_liabilities", "goodwill_risk", "litigation", "deferred_maintenance", "off_balance_sheet"],
     {
         "pension": c("Identified ManufactCo $420M pension underfunding", ["ManufactCo", "420", "pension", "underfund"], 2),
         "goodwill": c("Identified MedDevice $1.2B goodwill, $210M impairment", ["MedDevice", "1.2", "210", "goodwill", "impairment"], 2),
         "litigation": c("Identified MedDevice 340 lawsuits, $85M accrued", ["340", "85", "lawsuit", "OrthoFlex", "litigation"], 2),
         "deferred": c("Identified PropCore $340M deferred maintenance", ["PropCore", "340", "deferred", "maintenance", "backlog"], 2),
         "total_quantification": c("Quantified total hidden liabilities across portfolio", ["total", "combined", "portfolio", "hidden", "quantif"], 1),
     }),
    (78, "Thematic: Management Quality Ranking",
     "Rank all 10 management teams by quality, execution ability, and alignment with shareholders. Who is best and worst positioned to navigate challenges?",
     ["management_assessment", "execution_track_record", "shareholder_alignment", "ranking", "recommendation"],
     {
         "all_10_assessed": c("Assessed all 10 management teams", ["TechCorp", "HealthCo", "RetailMax", "EnergyX", "BankFirst", "PropCore", "ManufactCo", "MedDevice", "FinTechPay", "LogiFlow"], 2),
         "execution_evidence": c("Used evidence from our research for rankings", ["execut", "track record", "delivered", "miss", "perform"], 2),
         "governance_concerns": c("Flagged governance concerns in rankings", ["governance", "Whitfield", "42M", "CEO change", "SEC"], 2),
         "best_management": c("Identified strongest management team(s)", ["best", "strong", "top", "confident", "capable"], 1),
         "worst_management": c("Identified weakest management team(s)", ["worst", "weak", "concern", "poor", "questionable"], 1),
     }),
    (79, "Thematic: Macro Scenario — Recession Impact",
     "Model a recession scenario across all 10 companies. Who is most and least resilient? Estimate earnings and stock price impact.",
     ["recession_modeling", "most_resilient", "least_resilient", "earnings_impact", "portfolio_drawdown"],
     {
         "all_10_modeled": c("Modeled recession impact on all 10 companies", ["recession", "all 10", "model", "impact", "scenario"], 2),
         "most_resilient": c("Identified most recession-resilient companies", ["resilient", "defensive", "least affected", "strong", "survive"], 2),
         "most_vulnerable": c("Identified most vulnerable companies", ["vulnerab", "cyclical", "most affected", "risk", "fragile"], 2),
         "earnings_estimates": c("Estimated earnings declines", ["earnings", "decline", "EPS", "%, revenue", "margin"], 2),
         "portfolio_strategy": c("Recommended recession-proofing strategy", ["strategy", "protect", "rebalance", "defensive", "hedge"], 1),
     }),
    (80, "Thematic: Macro Scenario — Rate Cuts",
     "If the Fed cuts rates by 100bps over the next year, which of our 10 companies benefit most? Model the impact and recommend positioning.",
     ["rate_sensitivity_all", "biggest_beneficiaries", "least_benefit", "portfolio_positioning", "timing"],
     {
         "propcore_benefit": c("Identified PropCore as major rate-cut beneficiary", ["PropCore", "floating", "62%", "save", "benefit", "30M"], 3),
         "bankfirst_benefit": c("Identified BankFirst NIM benefit", ["BankFirst", "NIM", "expand", "rate cut", "income"], 2),
         "all_ranked": c("Ranked all 10 by rate-cut sensitivity", ["rank", "all 10", "rate cut", "benefit", "sensitivity"], 2),
         "portfolio_positioning": c("Recommended portfolio positioning", ["position", "overweight", "underweight", "tilt", "allocat"], 1),
         "timing_consideration": c("Discussed timing and probability of cuts", ["timing", "Fed", "probab", "when", "pace"], 1),
     }),
    (81, "Thematic: Concentration Risk Report",
     "Map concentration risks across all 10 companies: customer, product, geographic, and supplier concentration. Which companies are most dangerously concentrated?",
     ["customer_concentration", "product_concentration", "geographic_risk", "supplier_risk", "ranking"],
     {
         "customer_concentration": c("Mapped customer concentration (ManufactCo 67%, LogiFlow 38%)", ["ManufactCo", "67", "LogiFlow", "38", "customer", "concentrat"], 3),
         "product_risk": c("Identified product concentration risks", ["product", "Nexaviron", "Cardiovex", "Cardiofix", "single"], 2),
         "all_mapped": c("Mapped concentration for all 10 companies", ["all 10", "map", "concentrat", "portfolio", "risk"], 2),
         "ranking": c("Ranked by overall concentration risk", ["rank", "worst", "most concentrated", "dangerous", "diversif"], 1),
         "mitigation": c("Suggested portfolio-level mitigation", ["mitigat", "diversif", "portfolio", "reduce", "strategy"], 1),
     }),
    (82, "Thematic: 2026 Earnings Risk",
     "Which companies in our portfolio are most likely to miss earnings estimates in 2026? Rank by probability and identify the key risk factors.",
     ["earnings_risk_ranking", "specific_risks", "guidance_credibility", "consensus_gaps", "positioning"],
     {
         "all_ranked": c("Ranked all companies by earnings miss probability", ["rank", "miss", "earnings", "probab", "likely"], 2),
         "specific_risks": c("Identified specific earnings risk for each", ["covenant", "FDA", "contract", "NPL", "churn", "inventory"], 2),
         "highest_risk": c("Identified highest-risk companies for misses", ["highest", "most likely", "miss", "disappoint", "risk"], 2),
         "guidance_analysis": c("Assessed management guidance credibility", ["guidance", "credib", "track record", "conservat", "optimis"], 1),
         "positioning": c("Recommended positioning ahead of earnings", ["position", "ahead", "reduce", "hedge", "protect"], 1),
     }),
    (83, "Thematic: Cash Flow Quality",
     "Rank all 10 companies by earnings-to-cash-flow quality. Which companies have the most and least reliable reported earnings?",
     ["cash_flow_analysis", "quality_ranking", "accruals", "working_capital", "red_flags"],
     {
         "all_analyzed": c("Analyzed cash flow quality for all 10", ["cash flow", "quality", "all 10", "operating", "free"], 2),
         "best_quality": c("Identified highest quality earnings", ["best", "highest quality", "reliable", "strong", "convert"], 2),
         "worst_quality": c("Identified lowest quality or most suspect earnings", ["worst", "lowest", "suspect", "accrual", "concern"], 2),
         "specific_flags": c("Flagged specific concerns (FinTechPay recognition, RetailMax inventory)", ["FinTechPay", "recognition", "RetailMax", "inventory", "channel stuff"], 2),
         "ranking": c("Complete quality ranking", ["rank", "1", "10", "order", "quality"], 1),
     }),
    (84, "Thematic: Activist Investor Targets",
     "Which companies in our portfolio are most vulnerable to activist investor campaigns? Consider governance, underperformance, and breakup value.",
     ["activist_criteria", "vulnerable_companies", "potential_demands", "catalyst_assessment", "positioning"],
     {
         "criteria": c("Defined activist targeting criteria", ["activist", "criteria", "governance", "underperform", "value"], 1),
         "healthco_target": c("Identified HealthCo as activist target (Prescott already active)", ["HealthCo", "Prescott", "activist", "4.2%", "board"], 2),
         "other_targets": c("Identified other vulnerable companies", ["vulnerab", "target", "undervalue", "breakup", "change"], 2),
         "potential_demands": c("Listed potential activist demands", ["demand", "board seat", "sale", "cost cut", "dividend", "split"], 2),
         "investment_implication": c("Assessed activist involvement as investment catalyst", ["catalyst", "unlock", "value", "upside", "change"], 1),
     }),
    (85, "Thematic: M&A Candidates",
     "Based on our analysis, which companies are likely M&A targets or acquirers? Consider strategic fit, valuation, and vulnerability.",
     ["target_candidates", "acquirer_candidates", "strategic_rationale", "valuation_gap", "probability"],
     {
         "targets_identified": c("Identified likely acquisition targets", ["target", "acquisition", "buy", "takeover", "vulnerab"], 2),
         "acquirers_identified": c("Identified potential acquirers", ["acquirer", "buyer", "strategic", "consolidat", "merger"], 2),
         "rationale": c("Explained strategic rationale for deals", ["strategic", "synergy", "rationale", "fit", "value"], 2),
         "valuation_analysis": c("Assessed valuation attractiveness for M&A", ["valuation", "premium", "cheap", "discount", "P/E"], 1),
         "probability": c("Estimated M&A probability", ["probab", "likely", "timeline", "rumor", "approach"], 1),
     }),
    (86, "Thematic: Credit Rating Downgrade Risk",
     "Rank our 10 companies by likelihood of credit rating downgrade. Consider leverage trends, coverage ratios, and negative outlook indicators.",
     ["downgrade_ranking", "leverage_analysis", "coverage_ratios", "agency_signals", "portfolio_impact"],
     {
         "all_ranked": c("Ranked all 10 by downgrade probability", ["rank", "downgrade", "rating", "probab", "credit"], 2),
         "highest_risk": c("Identified highest downgrade risk companies", ["highest", "most likely", "downgrade", "junk", "speculative"], 2),
         "coverage_analysis": c("Analyzed coverage ratios for each", ["coverage", "ratio", "EBITDA", "interest", "debt service"], 2),
         "techcorp_energyx": c("Highlighted TechCorp and EnergyX covenant issues", ["TechCorp", "EnergyX", "covenant", "breach", "waiver"], 2),
         "portfolio_impact": c("Assessed portfolio impact of downgrades", ["portfolio", "impact", "cost", "access", "refinanc"], 1),
     }),
    (87, "Thematic: Portfolio Rebalancing Memo",
     "Write a portfolio rebalancing memo: for all 10 companies, recommend buy, hold, or sell. Use all our research to justify each rating.",
     ["all_10_rated", "buy_list", "sell_list", "hold_list", "rationale"],
     {
         "all_10_rated": c("Rated all 10 companies (buy/hold/sell)", ["buy", "hold", "sell", "all 10", "rating", "recommend"], 2),
         "buy_justification": c("Justified buy recommendations", ["buy", "upside", "undervalue", "catalyst", "attractive"], 2),
         "sell_justification": c("Justified sell recommendations with specific risks", ["sell", "risk", "downside", "avoid", "concern", "covenant", "FDA", "NPL"], 2),
         "portfolio_construction": c("Considered portfolio-level balance", ["portfolio", "balance", "diversif", "allocat", "weight"], 2),
         "action_items": c("Provided clear action items", ["action", "next step", "timeline", "execute", "implement"], 1),
     }),
    (88, "Thematic: Key Monitoring Dashboard",
     "For each company in our portfolio, identify the single most important metric to monitor in Q1 2026. Create a monitoring checklist.",
     ["all_10_metrics", "monitoring_frequency", "trigger_levels", "escalation_criteria", "checklist"],
     {
         "all_10_metrics": c("Identified key metric for each company", ["TechCorp", "HealthCo", "RetailMax", "EnergyX", "BankFirst", "PropCore", "ManufactCo", "MedDevice", "FinTechPay", "LogiFlow"], 2),
         "specific_metrics": c("Named specific metrics (e.g., TechCorp leverage ratio, HealthCo FDA date)", ["leverage ratio", "FDA", "NPL", "occupancy", "covenant", "contract", "churn", "inventory"], 2),
         "trigger_levels": c("Defined trigger/alert levels for each", ["trigger", "threshold", "alert", "if", "below", "above"], 2),
         "monitoring_plan": c("Proposed monitoring frequency", ["monitor", "weekly", "monthly", "quarterly", "frequency"], 1),
         "escalation": c("Defined escalation criteria", ["escalat", "action", "if triggered", "sell", "reduce"], 1),
     }),
]

for args in synthesis_sessions:
    sessions.append(s(args[0], args[1], args[2], "synthesis", args[3], args[4]))

# ============================================================
# Category G: Deep Dives (Sessions 89-100)
# ============================================================
deep_dive_sessions = [
    (89, "Deep Dive: EnergyX Restructuring Plan",
     "Using all our prior research on EnergyX, design a comprehensive turnaround plan. Address the covenant risk, reserve depletion, and margin compression.",
     "EnergyX",
     ["turnaround_strategy", "covenant_fix", "reserve_strategy", "cost_restructuring", "timeline"],
     {
         "covenant_solution": c("Proposed covenant amendment or cure strategy", ["covenant", "amend", "cure", "waiver", "negotiate", "3.0"], 3),
         "reserve_strategy": c("Proposed reserve replacement strategy", ["reserve", "0.68", "replace", "acquisition", "exploration", "capex"], 2),
         "cost_restructuring": c("Designed cost restructuring plan", ["cost", "cut", "restructur", "margin", "14.2", "improve"], 2),
         "asset_optimization": c("Considered asset sales or divestitures", ["asset", "divest", "sell", "non-core", "proceeds"], 1),
         "timeline": c("Proposed implementation timeline", ["timeline", "phase", "Q1", "Q2", "month", "year"], 1),
     }),
    (90, "Deep Dive: BankFirst Stress Test",
     "Using all our prior research, model a stress test for BankFirst. If NPL ratio increases another 2% (to 5.8%), what happens to capital, earnings, and dividends?",
     "BankFirst",
     ["stress_scenario", "capital_impact", "earnings_impact", "dividend_decision", "survival"],
     {
         "npl_scenario": c("Modeled NPL increase from 3.8% to 5.8%", ["3.8", "5.8", "NPL", "increase", "stress"], 2),
         "provision_estimate": c("Estimated additional provisions required", ["provision", "additional", "credit loss", "reserve", "billion"], 2),
         "capital_impact": c("Calculated capital ratio impact (Tier 1 10.8%)", ["capital", "Tier 1", "10.8", "ratio", "buffer"], 3),
         "earnings_wipeout": c("Showed potential earnings wipeout", ["earnings", "loss", "wipeout", "negative", "EPS"], 2),
         "action_plan": c("Recommended action plan", ["action", "plan", "dividend cut", "raise capital", "de-risk"], 1),
     }),
    (91, "Deep Dive: PropCore Debt Restructuring",
     "Using all our research, design a debt restructuring plan for PropCore. Propose converting floating to fixed rate, estimate costs, and model the impact.",
     "PropCore",
     ["restructuring_plan", "swap_analysis", "cost_estimate", "noi_impact", "timeline"],
     {
         "swap_proposal": c("Proposed floating-to-fixed swap for $2.98B", ["swap", "2.98", "floating", "fixed", "convert"], 3),
         "cost_analysis": c("Estimated swap/refinancing costs", ["cost", "premium", "swap rate", "spread", "basis point"], 2),
         "cash_flow_impact": c("Modeled impact on FFO and dividend coverage", ["FFO", "dividend", "coverage", "cash flow", "impact"], 2),
         "maintenance_plan": c("Addressed $340M deferred maintenance", ["340", "deferred", "maintenance", "capex", "address"], 1),
         "timeline": c("Proposed execution timeline", ["timeline", "phase", "quarter", "month", "execute"], 1),
     }),
    (92, "Deep Dive: ManufactCo Pension De-risking",
     "Using all our research, propose strategies to address ManufactCo's $420M pension underfunding. Analyze options and recommend a plan.",
     "ManufactCo",
     ["de_risking_options", "contribution_plan", "liability_reduction", "cost_analysis", "timeline"],
     {
         "options_analyzed": c("Analyzed pension de-risking options (annuity buyout, LDI, contributions)", ["annuity", "buyout", "LDI", "contribution", "de-risk", "option"], 2),
         "gap_analysis": c("Detailed the $420M gap (PBO $1.5B, assets $1.08B)", ["420", "1.5", "1.08", "gap", "underfund"], 3),
         "recommended_plan": c("Recommended specific de-risking plan", ["recommend", "plan", "strategy", "phase", "approach"], 2),
         "cost_impact": c("Estimated cost and earnings impact", ["cost", "earnings", "cash flow", "contribution", "expense"], 1),
         "risk_reduction": c("Quantified risk reduction achieved", ["risk", "reduction", "funded", "improve", "progress"], 1),
     }),
    (93, "Deep Dive: MedDevice FDA Response Plan",
     "Using all our research, design MedDevice's response strategy for the FDA Form 483 findings. Include remediation, communication, and financial planning.",
     "MedDevice",
     ["remediation_plan", "fda_response", "communication_strategy", "financial_impact", "timeline"],
     {
         "remediation_detail": c("Proposed detailed remediation for 3 quality system findings", ["remediat", "quality system", "3 finding", "corrective", "CAPA"], 3),
         "field_correction_plan": c("Addressed 12,000-unit field correction", ["12,000", "field correction", "recall", "Cardiofix", "unit"], 2),
         "fda_communication": c("Planned FDA communication strategy", ["FDA", "communicat", "response", "timeline", "submit"], 2),
         "financial_planning": c("Estimated remediation costs and revenue impact", ["cost", "revenue", "impact", "$40M", "defer", "remediat"], 1),
         "pipeline_protection": c("Protected future pipeline approvals", ["pipeline", "future", "approval", "protect", "submission"], 1),
     }),
    (94, "Deep Dive: FinTechPay Path to Profitability",
     "Using all our research, model when FinTechPay becomes profitable. What revenue scale, margin improvement, and churn reduction is needed?",
     "FinTechPay",
     ["profitability_model", "breakeven_analysis", "churn_reduction", "margin_expansion", "timeline"],
     {
         "current_losses": c("Detailed current -$85M net loss and cost structure", ["-85", "loss", "net income", "negative", "unprofitable"], 2),
         "breakeven_model": c("Modeled breakeven revenue and margin requirements", ["breakeven", "break even", "profitab", "scale", "gross margin", "42.5"], 3),
         "churn_impact": c("Modeled impact of churn reduction (3.8%→2.0%)", ["churn", "3.8", "2.0", "reduction", "retention"], 2),
         "revenue_growth_needed": c("Estimated revenue growth needed for profitability", ["revenue", "growth", "$2B", "scale", "volume", "142B"], 2),
         "timeline_estimate": c("Estimated profitability timeline", ["timeline", "year", "quarter", "2027", "2028", "when"], 1),
     }),
    (95, "Deep Dive: LogiFlow Labor Strategy",
     "Using all our research, design LogiFlow's strategy for the Teamsters CBA negotiation expiring March 2026. Include risk mitigation and contingency planning.",
     "LogiFlow",
     ["negotiation_strategy", "wage_proposal", "strike_contingency", "cost_modeling", "timeline"],
     {
         "negotiation_approach": c("Proposed negotiation strategy with Teamsters", ["negotiat", "Teamsters", "CBA", "strategy", "approach", "Local 952"], 2),
         "wage_modeling": c("Modeled wage increase scenarios and cost impact", ["wage", "increase", "cost", "per driver", "8,400", "total"], 2),
         "strike_contingency": c("Designed strike contingency plan", ["strike", "contingency", "backup", "contractor", "disruption", "14 day"], 3),
         "financial_impact": c("Estimated financial impact of scenarios", ["financial", "impact", "$45M", "revenue", "cost", "scenario"], 2),
         "timeline": c("Mapped negotiation timeline", ["timeline", "March 2026", "deadline", "phase", "milestone"], 1),
     }),
    (96, "Deep Dive: TechCorp 3-Year Model",
     "Using all our research, build a 3-year financial model for TechCorp under both Nova AI success and failure scenarios.",
     "TechCorp",
     ["success_scenario", "failure_scenario", "revenue_projections", "margin_trajectory", "debt_paydown"],
     {
         "success_model": c("Modeled Nova AI success scenario (revenue acceleration)", ["Nova AI", "success", "accelerat", "cloud", "growth", "revenue"], 2),
         "failure_model": c("Modeled failure scenario (continued decline)", ["fail", "decline", "legacy", "hardware", "deteriorat"], 2),
         "covenant_resolution": c("Modeled covenant resolution path", ["covenant", "1.83", "1.5", "resolve", "amend", "pay down"], 3),
         "margin_projection": c("Projected margins under each scenario", ["margin", "18.2", "project", "expand", "contract"], 2),
         "valuation_range": c("Estimated valuation range", ["valuation", "target", "range", "P/E", "DCF", "upside", "downside"], 1),
     }),
    (97, "Deep Dive: HealthCo Survival Analysis",
     "Using all our research, model HealthCo's financial trajectory under Nexaviron approve vs reject scenarios. Include cash runway and strategic options.",
     "HealthCo",
     ["approve_model", "reject_model", "cash_runway", "strategic_options", "probability_weighted"],
     {
         "approve_scenario": c("Detailed approve scenario with revenue ramp", ["approve", "Nexaviron", "launch", "revenue", "ramp", "4.8B market"], 2),
         "reject_scenario": c("Detailed reject scenario with cash depletion", ["reject", "fail", "cash", "burn", "deplet", "survival"], 2),
         "cash_runway": c("Calculated cash runway: $450M, $130M quarterly burn", ["450", "130", "runway", "quarter", "burn", "cash"], 3),
         "strategic_options": c("Listed survival options (M&A, partnership, asset sale)", ["M&A", "partner", "asset sale", "licens", "option", "strategic"], 2),
         "probability_weighted": c("Provided probability-weighted valuation", ["probability", "weight", "expected value", "scenario", "blended"], 1),
     }),
    (98, "Deep Dive: RetailMax Working Capital",
     "Using all our research, design an inventory liquidation and working capital improvement plan for RetailMax. Model the margin recovery timeline.",
     "RetailMax",
     ["liquidation_plan", "inventory_reduction", "margin_recovery", "cash_generation", "timeline"],
     {
         "liquidation_strategy": c("Proposed strategy for $280M seasonal inventory", ["280", "seasonal", "liquidat", "clearance", "markdown"], 3),
         "inventory_target": c("Set inventory days target (95→70)", ["95", "70", "inventory days", "target", "reduce"], 2),
         "margin_recovery": c("Modeled margin recovery from 5.1% to 6.0-6.5%", ["5.1", "6.0", "6.5", "margin", "recover"], 2),
         "cash_generation": c("Estimated cash generated from inventory reduction", ["cash", "generat", "working capital", "free cash", "release"], 1),
         "expansion_pace": c("Recommended adjusted expansion pace", ["expansion", "50 store", "slow", "pace", "fund", "sustain"], 1),
     }),
    (99, "Deep Dive: Full Portfolio DCF Rankings",
     "Using all our research, perform a simplified DCF analysis for all 10 companies. Rank by upside/downside to current valuation.",
     "synthesis",
     ["dcf_methodology", "all_10_valued", "upside_ranking", "key_assumptions", "conviction_picks"],
     {
         "methodology": c("Explained DCF methodology and assumptions", ["DCF", "discount", "WACC", "terminal", "method", "free cash"], 2),
         "all_10_valued": c("Valued all 10 companies", ["TechCorp", "HealthCo", "RetailMax", "EnergyX", "BankFirst", "PropCore", "ManufactCo", "MedDevice", "FinTechPay", "LogiFlow"], 2),
         "upside_ranking": c("Ranked by upside/downside to fair value", ["rank", "upside", "downside", "fair value", "over", "under"], 2),
         "key_assumptions": c("Stated key assumptions for each model", ["assum", "growth rate", "margin", "discount", "terminal"], 2),
         "conviction": c("Identified highest-conviction picks", ["conviction", "highest", "best", "strong", "recommend"], 1),
     }),
    (100, "Deep Dive: Final Investment Memo",
     "Write a comprehensive final investment memo covering all 10 companies. Synthesize everything from our 99 prior sessions into definitive buy/hold/sell recommendations with specific price targets and risk factors.",
     "synthesis",
     ["all_10_recommendations", "synthesis_quality", "specific_targets", "risk_factors", "actionable_conclusions"],
     {
         "all_10_covered": c("Covered all 10 companies with specific recommendations", ["TechCorp", "HealthCo", "RetailMax", "EnergyX", "BankFirst", "PropCore", "ManufactCo", "MedDevice", "FinTechPay", "LogiFlow"], 2),
         "buy_sell_hold": c("Clear buy/hold/sell for each", ["buy", "sell", "hold", "recommend", "rating"], 2),
         "specific_details": c("Referenced specific findings from prior research", ["covenant", "1.83", "Nexaviron", "FDA", "NPL", "3.8", "pension", "420", "483", "SEC"], 3),
         "risk_reward": c("Quantified risk/reward for each position", ["risk", "reward", "upside", "downside", "target", "return"], 2),
         "actionable": c("Provided actionable conclusions and next steps", ["action", "next step", "implement", "timeline", "execute", "monitor"], 1),
     }),
]

for args in deep_dive_sessions:
    if isinstance(args[3], str):
        sessions.append(s(args[0], args[1], args[2], args[3], args[4], args[5]))
    else:
        sessions.append(s(args[0], args[1], args[2], "deep_dive", args[3], args[4]))

# Sort by id to be safe
sessions.sort(key=lambda x: x["id"])

# Validate
assert len(sessions) == 100, f"Expected 100 sessions, got {len(sessions)}"
ids = [s["id"] for s in sessions]
assert ids == list(range(1, 101)), f"Session IDs are not sequential 1-100: {sorted(set(range(1,101)) - set(ids))}"

output = {"sessions": sessions}
output_path = os.path.join(os.path.dirname(__file__), "..", "config", "scenarios.json")
with open(output_path, "w") as f:
    json.dump(output, f, indent=2)

print(f"Generated {len(sessions)} sessions")
print(f"Written to {output_path}")

# Stats
categories = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0, "G": 0}
for sess in sessions:
    sid = sess["id"]
    if sid <= 10: categories["A"] += 1
    elif sid <= 20: categories["B"] += 1
    elif sid <= 30: categories["C"] += 1
    elif sid <= 50: categories["D"] += 1
    elif sid <= 75: categories["E"] += 1
    elif sid <= 88: categories["F"] += 1
    else: categories["G"] += 1
print(f"Categories: {categories}")
total_criteria = sum(len(s["ground_truth_score_criteria"]) for s in sessions)
weight_3 = sum(1 for s in sessions for c in s["ground_truth_score_criteria"].values() if c["weight"] == 3)
print(f"Total criteria: {total_criteria}, Weight-3: {weight_3}")
