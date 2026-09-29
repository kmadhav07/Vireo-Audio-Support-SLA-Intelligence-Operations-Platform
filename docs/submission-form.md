# VIREO AUDIO — SUBMISSION FORM

## 1. Candidate & Submission Details
- **Project Name:** Vireo Audio Support SLA Intelligence & Operations Platform
- **Date of Submission:** 29 September 2026
- **Operating System / Environment:** macOS / Linux / Clean Python 3.10+

---

## 2. Business Goal (Stated as a Specific Number)
> **"Cut overall support SLA breach rate from 25.0% (peaking at 26.0% post-reshuffle) to 8.5%, saving ₹157,000 per quarter (₹628,000 annually) in automated ₹350 SLA breach credits with 0 incremental headcount, while eliminating 92% of the unstaffed night backlog unfairly blamed on 24 morning-shift agents."**

### Data Grounding:
- **Pre-Reshuffle (H1 2025):** 9.3% breach rate | ₹12,308 avg monthly credits (~₹36,925/quarter).
- **Post-Reshuffle (H2 2025 – H1 2026):** 24.95% breach rate | ₹65,012 avg monthly credits (~₹195,038/quarter).
- **Root Cause:** 70.8% of post-reshuffle breaches (1,579 out of 2,229 breaches) originated between 22:00 and 06:00 IST when 0 agents were on duty.
- **Roster Optimization:** Reallocating 2 existing Chat agents to the Indore Night Shift under the current headcount freeze recovers 80%+ of night SLA compliance at ₹0 added payroll.

---

## 3. How We Know the Tool's Output is Correct
We implemented an automated test and verification suite (`verify_solution.py`) with 100% programmatic assertion coverage:
1. **Deduplication Precision:** Deduplicates 616 dual-imported migration records (11,816 raw rows down to 11,200 unique tickets), prioritizing the primary `helpdesk` record over legacy artifacts.
2. **Timezone Accuracy:** Normalizes API UTC timestamps to IST (`Asia/Kolkata`, UTC+5:30) before mapping against Policy §7 operating shift windows (Morning: 06:00–14:00, Day: 14:00–22:00, Night: 22:00–06:00).
3. **Dual-Attribution Validation:** Confirms that Morning agents achieve an 8.34% in-shift breach rate when handling tickets created during morning hours, disproving the naive helpdesk report’s 36.75% breach blame.
4. **Financial Consistency:** Matches every breach to Policy §3 standards (₹350 per breached resolved/closed ticket = ₹812,000 cumulative liability across all 18 months).
5. **CSAT Sanitization:** Automatically replaces legacy `0.0` non-response values with `NaN` in compliance with Policy §8.

---

## 4. Architectural Summary of Delivered Tool
- **Core Engine (`src/`):**
  - `data_loader.py`: Ingestion, deduplication, UTC-to-IST conversion, dynamic roster join.
  - `sla_engine.py`: Multi-channel SLA calculation, naive vs true attribution, agent scorecards, and weekly report generator.
  - `financial_engine.py`: Cost standards modeling, P&L credit impact, zero-hire scenario simulation.
  - `ai_analyzer.py`: Semantic intent classifier, broken IVR transcript detector, self-service deflection potential estimator.
  - `report_generator.py`: CSV exporter and executive summary generator.
- **Interactive UI (`app.py`):**
  - Streamlit & Plotly dark-mode interactive dashboard with 6 specialized management views for Neha, Priya, and Arjun.

---

## 5. Tools & AI Models Used
- **AI / LLM Assistants:** Anthropic Claude & Google Gemini for exploratory data analysis, rapid prototyping of Streamlit components, and scenario stress-testing.
- **Cost Incurred:** ₹0 (Standard developer API quota).
- **What Was Changed / Discarded:**
  - *Discarded Approach 1:* Naive agent ranking based solely on helpdesk breach counts. This was discarded upon discovering the June 30, 2025 Indore night shift elimination.
  - *Discarded Approach 2:* Proposing 3 new night agent hires. Discarded immediately due to Arjun Mehta’s strict Q4 headcount freeze constraint. Shifted to zero-hire roster rebalancing + AI deflection.
  - *Discarded Approach 3:* Complex external database dependencies. Discarded in favor of zero-friction single-command local execution on any clean machine.

---

## 6. Execution Instructions (Clean Machine)
```bash
# 1. Clone/navigate to directory
cd /Users/madhavkumar/Desktop/Vireo_audio

# 2. Install lightweight dependencies
pip install -r requirements.txt

# 3. Run automated verification suite
python verify_solution.py

# 4. Launch interactive dashboard
streamlit run app.py
```
