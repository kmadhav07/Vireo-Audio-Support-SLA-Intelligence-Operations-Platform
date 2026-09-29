"""
Verification Suite for Vireo Audio Support Intelligence.
Tests end-to-end data pipeline, deduplication, SLA breach accuracy,
dual attribution model, and financial consistency.
"""

import sys
import pandas as pd
import numpy as np

from src.data_loader import load_and_preprocess_data
from src.sla_engine import evaluate_sla, generate_shift_summary, generate_agent_scorecard, generate_weekly_breach_report
from src.financial_engine import compute_financial_breakdown, simulate_roster_scenarios
from src.ai_analyzer import analyze_deflection_potential

def run_tests():
    print("========================================")
    print("RUNNING VIREO INTELLIGENCE VERIFICATION")
    print("========================================")
    
    # 1. Test Data Ingestion & Deduplication
    print("\n[Test 1] Testing Data Loading & Deduplication...")
    raw_data = load_and_preprocess_data(".")
    tickets = raw_data["tickets"]
    assert len(tickets) == 11200, f"Expected 11,200 deduplicated tickets, got {len(tickets)}"
    assert tickets["ticket_id"].nunique() == 11200, "Found duplicate ticket_ids after deduplication!"
    print("  -> Passed: Exactly 11,200 clean unique tickets loaded.")
    
    # 2. Test Timezone & Shift Assignment
    print("\n[Test 2] Testing UTC to IST Timezone & Shift Windows...")
    assert "created_at_ist" in tickets.columns, "Missing created_at_ist column"
    assert "created_shift" in tickets.columns, "Missing created_shift column"
    shifts = set(tickets["created_shift"].dropna().unique())
    assert shifts == {"Morning", "Day", "Night"}, f"Unexpected shifts: {shifts}"
    print(f"  -> Passed: IST shifts successfully assigned ({shifts}).")
    
    # 3. Test SLA Target Mapping & Breach Logic
    print("\n[Test 3] Testing SLA Targets and Breach Calculations...")
    evaluated = evaluate_sla(tickets)
    assert evaluated["is_breach"].sum() == 2440, f"Expected 2,440 breaches, got {evaluated['is_breach'].sum()}"
    
    # Check channel targets
    chat_tickets = evaluated[evaluated["channel"] == "chat"]
    assert (chat_tickets["sla_target_min"] == 15).all(), "Chat SLA target mismatch (expected 15 min)"
    
    voice_tickets = evaluated[evaluated["channel"] == "voice"]
    assert (voice_tickets["sla_target_min"] == 120).all(), "Voice SLA target mismatch (expected 120 min)"
    print("  -> Passed: SLA targets and 2,440 breaches verified.")
    
    # 4. Test Dual Attribution Logic
    print("\n[Test 4] Testing Dual Attribution (Naive vs True In-Shift)...")
    night_breaches = evaluated[evaluated["created_shift"] == "Night"]["is_breach"].sum()
    assert night_breaches == 1631, f"Expected 1,631 night breaches, got {night_breaches}"
    
    post = evaluated[evaluated["created_at_ist"] >= "2025-07-01"]
    morn_on_morn = post[(post["agent_shift"] == "Morning") & (post["created_shift"] == "Morning")]
    morn_in_shift_rate = (morn_on_morn["is_breach"].mean() * 100)
    assert round(morn_in_shift_rate, 1) == 8.3, f"Expected 8.3% true morning breach rate, got {morn_in_shift_rate:.2f}%"
    print(f"  -> Passed: True Morning In-Shift breach rate confirmed at {morn_in_shift_rate:.1f}%.")
    
    # 5. Test Financial Calculations
    print("\n[Test 5] Testing P&L Financial Calculations & Scenarios...")
    fin = compute_financial_breakdown(evaluated, raw_data["products"])
    assert fin["total_sla_credits"] == 812000.0, f"Expected ₹812,000 credits, got {fin['total_sla_credits']}"
    assert fin["double_dip_count"] == 6, f"Expected 6 double dips, got {fin['double_dip_count']}"
    
    scenarios = simulate_roster_scenarios(evaluated)
    assert len(scenarios) == 4, f"Expected 4 scenarios, got {len(scenarios)}"
    print(f"  -> Passed: Total SLA credits (₹{fin['total_sla_credits']:,.0f}) and scenario models verified.")
    
    # 6. Test Weekly Report Generation
    print("\n[Test 6] Testing Weekly Breach Report Generation...")
    weekly = generate_weekly_breach_report(evaluated)
    assert len(weekly) > 0, "Weekly report empty!"
    print(f"  -> Passed: Weekly report generated ({len(weekly)} agent-week rows).")
    
    # 7. Test AI Deflection Engine
    print("\n[Test 7] Testing AI Intent Categorization & Deflection Engine...")
    ai_res = analyze_deflection_potential(evaluated)
    assert ai_res["failed_ivr_count"] > 0, "No failed IVRs detected"
    print(f"  -> Passed: AI Deflection engine classified {len(ai_res['intent_breakdown'])} intent categories.")
    
    print("\n========================================")
    print("ALL VERIFICATION TESTS PASSED SUCCESSFULLY! (100% ACCURACY)")
    print("========================================")

if __name__ == "__main__":
    run_tests()
