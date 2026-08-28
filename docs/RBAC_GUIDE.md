# 🔐 Role-Based Access Control (RBAC) & Governance Matrix

The platform enforces Role-Based Access Control (RBAC) across seven operational personas. Access controls dictate visibility of student telemetry, offer modification rights, drive broadcast permissions, and accreditation report generation.

---

## 1. Stakeholder Access Matrix

| Capability / Operational Route | Student | Placement Head | Placement Team | Hiring Partner | HOD / Management | PragyanAI Engine | Public / Wall of Fame |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Profile & Skill Passport Editing** | 🟢 (Self) | 🔴 | 🟡 (Assisted) | 🔴 | 🔴 | 🟢 (Scoring) | 🔴 |
| **RAG Resume vs. JD Analyzer** | 🟢 | 🔴 | 🔴 | 🔴 | 🔴 | 🟢 | 🔴 |
| **Multimedia Voice Debrief Logging** | 🟢 (Self) | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 |
| **Download Student Offer Certificate**| 🟢 (Self) | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🟢 (Public Card) |
| **Broadcast Campus Drive & JDs** | 🔴 | 🟢 | 🔴 | 🟡 (Draft) | 🔴 | 🔴 | 🔴 |
| **Approve / Reject Corporate Partners**| 🔴 | 🟢 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 |
| **Schedule Bootcamps & Workshops** | 🔴 | 🟢 | 🔴 | 🔴 | 🔴 | 🟢 | 🔴 |
| **Post-Drive Reconciliation & Offers** | 🔴 | 🔴 | 🟢 | 🔴 | 🔴 | 🔴 | 🔴 |
| **Stage Progression Updates** | 🔴 | 🔴 | 🟢 | 🔴 | 🔴 | 🔴 | 🔴 |
| **Unredacted Candidate Discovery** | 🔴 | 🔴 | 🔴 | 🟢 | 🔴 | 🔴 | 🔴 |
| **Submit Recruiter Feedback on Gaps** | 🔴 | 🔴 | 🔴 | 🟢 | 🔴 | 🔴 | 🔴 |
| **Multidimensional Pivots & Sunburst**| 🔴 | 🟢 | 🔴 | 🔴 | 🟢 | 🟢 | 🔴 |
| **NIRF / NAAC Compliance PDF Export** | 🔴 | 🔴 | 🔴 | 🔴 | 🟢 | 🔴 | 🔴 |
| **Competency Radar & Badge Telemetry**| 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🟢 | 🔴 |
| **Wall of Fame Honors Showcase** | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 |

---

## 2. Navigation Routing Table (`app.py`)

```python
# RBAC Navigation Mapping Rule
if active_role == "Student":
    nav = st.navigation([student_page, wall_of_fame_page])
elif active_role == "Placement Head":
    nav = st.navigation([head_page, team_page, exec_page, wall_of_fame_page, pragyan_page])
elif active_role == "Placement Team":
    nav = st.navigation([team_page, student_page, wall_of_fame_page, exec_page])
elif active_role == "Hiring Partner":
    nav = st.navigation([company_page, wall_of_fame_page])
elif active_role == "HOD / Principal / Management":
    nav = st.navigation([exec_page, wall_of_fame_page])
elif active_role == "PragyanAI Engine":
    nav = st.navigation([pragyan_page, exec_page, wall_of_fame_page])
else:  # Public / Wall of Fame
    nav = st.navigation([wall_of_fame_page, exec_page])
