"""
AI-Assisted Ticket Analyzer & Intent Intelligence Engine.
Performs semantic categorization, automated IVR failure detection,
deflection opportunity scoring, and quality/compliance auditing.
"""

import re
import pandas as pd
import numpy as np
from typing import Dict, List, Any

# Common keywords for customer intent detection
INTENT_PATTERNS = {
    "Order & Delivery Tracking": [
        r"delivery", r"where is my order", r"tracking", r"dispatch", r"courier",
        r"not delivered", r"delayed", r"shipment", r"parcel"
    ],
    "Hardware Defect / DOA": [
        r"crackling", r"won't turn on", r"not working", r"buzzing", r"damaged",
        r"broken", r"battery drain", r"left ear", r"right ear", r"mic", r"distortion",
        r"charging", r"dead on arrival", r"doa"
    ],
    "Returns & Refunds": [
        r"refund", r"return", r"pickup", r"cancel", r"money back", r"wrong product",
        r"wrong item", r"exchange"
    ],
    "Pairing & Connectivity": [
        r"pair", r"bluetooth", r"connect", r"disconnect", r"app", r"firmware",
        r"sync", r"iphone", r"android"
    ],
    "Billing & Payments": [
        r"double charge", r"deducted", r"invoice", r"coupon", r"discount",
        r"payment failed", r"price adjustment"
    ]
}

def detect_failed_ivr_transcripts(text: str) -> bool:
    """
    Identifies broken or garbled IVR transcripts (as noted by Sameer Qureshi).
    """
    if not isinstance(text, str) or not text.strip():
        return True
    
    clean_text = text.lower()
    
    # Specific IVR artifacts and garbled indicators
    if "[ivr transcript]" in clean_text:
        # Check if transcript is truncated, empty or contains failure tokens
        remaining = clean_text.replace("[ivr transcript]", "").strip()
        if len(remaining) < 10:
            return True
        if re.search(r"(unintelligible|incomprehensible|garbled|silence|audio cut off|\.\.\.$)", remaining):
            return True
            
    # Very short noise messages
    if len(clean_text) < 6 and not any(w in clean_text for w in ["hi", "help", "hello"]):
        return True
        
    return False

def classify_ticket_intent(message: str) -> str:
    """
    Classifies a customer message into an operational intent category.
    """
    if not isinstance(message, str):
        return "General / Unspecified"
        
    clean_msg = message.lower()
    
    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, clean_msg):
                return intent
                
    return "General / Inquiries"

def analyze_deflection_potential(tickets: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyzes which repetitive intents could be deflected by an overnight AI bot
    to eliminate night shift queue accumulation.
    """
    df = tickets.copy()
    
    # Classify intents
    df["ai_predicted_intent"] = df["customer_message"].apply(classify_ticket_intent)
    df["is_failed_ivr"] = df["customer_message"].apply(detect_failed_ivr_transcripts)
    
    # Highly deflectable categories (Order tracking, simple pairing guides, invoice requests)
    deflectable_intents = ["Order & Delivery Tracking", "Pairing & Connectivity", "Billing & Payments"]
    df["is_bot_deflectable"] = (
        df["ai_predicted_intent"].isin(deflectable_intents) & 
        (df["transfers"] == 0) & 
        (~df["is_failed_ivr"])
    )
    
    night_tickets = df[df["created_shift"] == "Night"]
    night_deflectable_count = night_tickets["is_bot_deflectable"].sum()
    night_deflectable_pct = (night_deflectable_count / len(night_tickets) * 100) if len(night_tickets) > 0 else 0
    
    intent_breakdown = df.groupby("ai_predicted_intent").agg(
        total_tickets=("ticket_id", "count"),
        breaches=("is_breach", "sum"),
        breach_rate_pct=("is_breach", lambda x: round(x.mean() * 100, 2)),
        avg_handle_time_min=("handle_time_minutes", "median")
    ).reset_index().sort_values(by="total_tickets", ascending=False)
    
    failed_ivr_count = df["is_failed_ivr"].sum()
    
    return {
        "intent_breakdown": intent_breakdown,
        "failed_ivr_count": failed_ivr_count,
        "night_deflectable_count": night_deflectable_count,
        "night_deflectable_pct": round(night_deflectable_pct, 1),
        "analyzed_dataframe": df
    }
