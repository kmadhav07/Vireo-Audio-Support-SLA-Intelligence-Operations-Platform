# 3-Minute Screen Recording Walkthrough Script

**Speaker:** Candidate / Solutions Engineer  
**Target Duration:** 2 minutes 45 seconds (Under 3:00 cap)  
**Format:** Live Screen Capture (No slides, direct walkthrough of terminal, code, and live Streamlit dashboard)  

---

### Timestamps & Talking Points

#### [0:00 – 0:40] 1. The Real Problem & Initial Prompting
- **Screen Action:** Open `app.py` dashboard on the *Executive Diagnostic* tab, showing the Monthly Breach Composition chart.
- **Script:** 
  > *"When Neha Kulkarni asked for a breach report to identify which morning agents to reprimand, we started by analyzing the helpdesk exports. Standard reports showed morning shift breaches skyrocketing above 36%.
  > 
  > But when we prompted our AI assistant to cross-tabulate ticket creation timestamps against the agent roster across time, a critical pattern emerged: On June 30, 2025, the Indore night shift was completely eliminated—leaving zero agents on duty overnight.
  > 
  > Yet Vireo promised 24x7 chat with a 15-minute SLA. Night tickets piled up for 8 hours, and when morning agents logged in at 6 AM to a 'wall of red', the system falsely blamed them for those pre-breached tickets upon resolution."*

---

#### [0:40 – 1:25] 2. Iterations & What We Threw Away
- **Screen Action:** Switch to *Agent Scorecards & True Attribution* and show the scatter plot comparing Naive Breach % vs True In-Shift Breach %.
- **Script:** 
  > *"Between Version 1 and our final tool, we made three major architectural shifts:
  > 
  > 1. **What we discarded first:** We threw away the initial 'naive agent leaderboard'. Ranking agents by raw breach count was completely wrong because it penalized the morning team for clearing unstaffed night backlog. We built a dual-attribution engine instead: when morning agents handle morning-created tickets, their breach rate is actually 8.3%—better than the day shift.
  > 2. **What we changed next:** We discarded our initial proposal to 'hire 3 night agents' once we accounted for Finance Controller Arjun Mehta's Q4 headcount freeze. We pivoted to a zero-hire roster rebalancing model.
  > 3. **Data cleansing:** We identified and pruned 616 duplicated migration tickets and corrected CSAT 0s to NaNs so policy calculations remained 100% compliant."*

---

#### [1:25 – 2:15] 3. Live Tool Walkthrough & The Business Goal
- **Screen Action:** Navigate to *Weekly Breach Report* (showing Neha's filterable view) and then *P&L Financial Simulator* (adjusting the sliders).
- **Script:** 
  > *"Here is the interactive platform we delivered:
  > 
  > - **For Neha:** An automated weekly breach report with one-click CSV export and a toggle for 'True In-Shift Attribution' so she can conduct fair coaching without hurting morale.
  > - **For Arjun:** An interactive financial simulator. Our concrete business goal is to **cut the breach rate from 25.0% to 8.5%, saving ₹157,000 per quarter (₹628,000 annually)** in automatic ₹350 SLA credits.
  > - By reassigning just 2 existing chat agents from Indore day rotation back to night shift and enabling off-hours bot deflection, we solve the crisis with zero new hires."*

---

#### [2:15 – 2:45] 4. Automated Verification & Clean Machine Execution
- **Screen Action:** Open terminal, run `python verify_solution.py`, showing all 7 unit test assertions passing with 100% green checkmarks.
- **Script:** 
  > *"To ensure total correctness, we created an automated verification suite that validates every SLA threshold, deduplication rule, and financial standard against Vireo's Operating Policy v3.2. Everything runs on any clean machine from our README in seconds.
  > 
  > We've delivered the tool, the one-page memo to Neha, the financial model for Arjun, and the complete submission form. Thank you."*
