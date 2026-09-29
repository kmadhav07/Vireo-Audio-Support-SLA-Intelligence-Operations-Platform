"""
Data Loader and Preprocessing Module for Vireo Audio Support Intelligence.
Handles data ingestion, deduplication, UTC to IST timestamp conversion,
and dynamic agent roster mapping across historical date windows.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, Any, Optional

def load_and_preprocess_data(base_path: str = ".") -> Dict[str, pd.DataFrame]:
    """
    Loads all datasets from the workspace, cleans duplicates,
    normalizes timezones to IST, maps roster assignments dynamically,
    and returns a clean dictionary of DataFrames.
    """
    base_dir = Path(base_path)
    if (base_dir / "data").exists() and (base_dir / "data" / "tickets.csv").exists():
        data_dir = base_dir / "data"
    else:
        data_dir = base_dir
    
    # 1. Load CSVs
    tickets_raw = pd.read_csv(data_dir / "tickets.csv")
    agents_raw = pd.read_csv(data_dir / "agents.csv")
    orders_raw = pd.read_csv(data_dir / "orders.csv")
    customers_raw = pd.read_csv(data_dir / "customers.csv")
    products_raw = pd.read_csv(data_dir / "products.csv")
    
    # 2. Deduplicate tickets (Favor 'helpdesk' source over 'legacy_fd')
    # Legacy migration created 616 duplicate tickets in export
    tickets_sorted = tickets_raw.sort_values(by=["ticket_id", "source_system"], ascending=[True, True])
    tickets_dedup = tickets_sorted.drop_duplicates(subset=["ticket_id"], keep="first").reset_index(drop=True)
    
    # 3. Clean CSAT: Policy §8 states blank means no response and must be excluded, not treated as 0.
    # In legacy_fd rows, non-responses were exported as 0.0 -> map 0.0 to NaN.
    tickets_dedup["csat_score_cleaned"] = tickets_dedup["csat_score"].replace(0.0, np.nan)
    
    # 4. Convert timestamps from UTC (API export) to IST (Operating hours)
    for col in ["created_at", "first_response_at", "resolved_at"]:
        tickets_dedup[col + "_utc"] = pd.to_datetime(tickets_dedup[col], errors="coerce", utc=True)
        tickets_dedup[col + "_ist"] = tickets_dedup[col + "_utc"].dt.tz_convert("Asia/Kolkata")
    
    # 5. Calculate First Response Time (FRT) and Handle Time (HT) in minutes
    tickets_dedup["frt_minutes"] = (
        tickets_dedup["first_response_at_utc"] - tickets_dedup["created_at_utc"]
    ).dt.total_seconds() / 60.0
    
    tickets_dedup["handle_time_minutes"] = (
        tickets_dedup["resolved_at_utc"] - tickets_dedup["first_response_at_utc"]
    ).dt.total_seconds() / 60.0
    
    # 6. Shift Definitions (IST):
    # Morning: 06:00 - 14:00 IST
    # Day:     14:00 - 22:00 IST
    # Night:   22:00 - 06:00 IST
    def get_ist_shift(dt):
        if pd.isna(dt):
            return np.nan
        h = dt.hour
        if 6 <= h < 14:
            return "Morning"
        elif 14 <= h < 22:
            return "Day"
        else:
            return "Night"
            
    tickets_dedup["created_shift"] = tickets_dedup["created_at_ist"].apply(get_ist_shift)
    tickets_dedup["response_shift"] = tickets_dedup["first_response_at_ist"].apply(get_ist_shift)
    tickets_dedup["resolved_shift"] = tickets_dedup["resolved_at_ist"].apply(get_ist_shift)
    
    # 7. Dynamic Agent Roster Matching
    # Agents have historical date windows (from_date to to_date)
    agents_clean = agents_raw.copy()
    agents_clean["from_date_dt"] = pd.to_datetime(agents_clean["from_date"])
    agents_clean["to_date_dt"] = pd.to_datetime(agents_clean["to_date"]).fillna(pd.to_datetime("2099-12-31"))
    
    # Map each ticket to agent roster assignment at time of first response / creation
    tickets_dedup["response_date"] = pd.to_datetime(tickets_dedup["first_response_at_ist"].dt.date)
    
    agent_records = []
    for idx, row in tickets_dedup.iterrows():
        aid = row["agent_id"]
        r_date = row["response_date"]
        
        # Match agent on response date window
        match = agents_clean[
            (agents_clean["agent_id"] == aid) &
            (agents_clean["from_date_dt"] <= r_date) &
            (agents_clean["to_date_dt"] >= r_date)
        ]
        
        # Fallback if unassigned date window
        if len(match) == 0:
            match = agents_clean[agents_clean["agent_id"] == aid]
            
        if len(match) > 0:
            m = match.iloc[0]
            agent_records.append({
                "agent_name": m["name"],
                "agent_site": m["site"],
                "agent_team": m["team"],
                "agent_shift": m["shift"],
                "agent_tier": m["tier"]
            })
        else:
            agent_records.append({
                "agent_name": "Unassigned",
                "agent_site": "Unknown",
                "agent_team": "Unknown",
                "agent_shift": "Unknown",
                "agent_tier": np.nan
            })
            
    agent_df = pd.DataFrame(agent_records)
    tickets_final = pd.concat([tickets_dedup, agent_df], axis=1)
    
    # 8. Add Week, Month, and Quarter helpers (in IST without timezone warning)
    created_naive = tickets_final["created_at_ist"].dt.tz_localize(None)
    tickets_final["created_week"] = created_naive.dt.to_period("W-SUN").astype(str)
    tickets_final["created_month"] = created_naive.dt.to_period("M").astype(str)
    tickets_final["created_quarter"] = created_naive.dt.to_period("Q").astype(str)
    
    return {
        "tickets": tickets_final,
        "agents": agents_clean,
        "orders": orders_raw,
        "customers": customers_raw,
        "products": products_raw
    }

if __name__ == "__main__":
    data = load_and_preprocess_data(".")
    print(f"Data successfully loaded. Clean tickets count: {len(data['tickets'])}")
