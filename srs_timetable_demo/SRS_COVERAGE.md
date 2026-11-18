# Software Requirements Specification (SRS) Traceability Matrix
### Default Institutional Dataset: 5th Semester Timetables (CSE Core, AI, Data Science)

This document maps each functional requirement from the Software Requirements Specification (SRS) to its concrete implementation in `/srs_timetable_demo/`, explaining the underlying mechanism and how to demonstrate it.

---

## 1. Input Management Requirements

| Requirement ID | Requirement Description | Implementation Location | Technical Mechanism | Demonstration Method | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **REQ-IN-01** | **Course Offerings Management:** Code, name, department, faculty, section(s), type, sessions/week, duration, room allocation mode, venues. | `backend/models.py` (`Course`)<br>`backend/store.py`<br>`frontend/js/app.js` (`#courseModal`) | Pydantic schema supporting multi-session courses, co-instructors (`faculty_ids`), and allocation modes (`SINGLE_FROM_ELIGIBLE` vs `SIMULTANEOUS_BUNDLE`). | Go to *Courses* in sidebar; view 54 venue-backed offerings covering CSE, AI, and DS. | **Fully Implemented** |
| **REQ-IN-02** | **Student Sections & Course Groups Management:** Section ID, name, department, semester/year, student strength, and G1/G2 cohort mapping. | `backend/models.py` (`Section`, `CourseGroup`)<br>`backend/store.py`<br>`frontend/js/app.js` | Models 13 student sections (`CSE1`–`CSE7`, `DS1`–`DS4`, `AI1`–`AI2`) plus discrete `CourseGroup` entities (`G1`, `G2`) with admin section mapping. | Go to *Student Sections*; inspect 13 sections and use *Configure Mapping* for G1/G2. | **Fully Implemented** |
| **REQ-IN-03** | **Faculty Management & Co-Instructors:** Faculty ID, name, department, co-instructors, and custom availability matrix. | `backend/models.py` (`Faculty`)<br>`backend/store.py`<br>`frontend/js/app.js` | 2D boolean grid `[day][period]`. Supports co-instructors on TOC Tut, SE Lab, and CN. Shared faculty Dr. Ravpreet coordinated across departments. | Go to *Faculty*; view 16 faculty; inspect Dr. Ravpreet (marked *Shared (CSE/AI)*). | **Fully Implemented** |
| **REQ-IN-04** | **Classrooms & Laboratories:** Room ID, name, type (Classroom/Lab/Seminar Hall), capacity, availability. | `backend/models.py` (`Room`)<br>`backend/store.py`<br>`frontend/js/app.js` (`#roomModal`) | Models 20 distinct venues from `timetables.md`. Preserves room identities (407 vs L407). Supports unknown/unverified capacity handling without fake numbers. | Go to *Classrooms & Labs*; view 20 venues; click *Edit* on any room to customize capacity. | **Fully Implemented** |
| **REQ-IN-05** | **Time Slots & Break Schedule:** Working days, daily periods, start/end times, and lunch breaks. | `backend/models.py` (`TimeSlotConfig`)<br>`backend/sample_data.py`<br>`frontend/index.html` (`#sec-slots`) | 8 hourly periods (08:00–17:00) with non-schedulable Lunch Break (13:00–14:00) after Period 5. | Go to *Time Slots*; view 8 periods and lunch break boundary. | **Fully Implemented** |

---

## 2. Core Scheduling & Hard Constraints (Google OR-Tools CP-SAT)

| Requirement ID | Requirement Description | Implementation Location | Mathematical / Constraint Formulation | Demonstration Method | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **REQ-HC-01** | **Faculty Conflict Prevention:** No faculty can teach two sessions simultaneously (including co-instructors). | `backend/solver.py`<br>`backend/validator.py` | $\forall f \in \text{faculty\_ids}(e), d, p: \sum_{e: f \in \text{faculty\_ids}(e)} A_{e, d, p} \le 1$ | Solve timetable; verify 0 faculty clashes across all 16 instructors including co-teachers. | **Fully Implemented** |
| **REQ-HC-02** | **Student Section Conflict Prevention:** No student section can attend two classes simultaneously; group lectures reserve member sections. | `backend/solver.py`<br>`backend/validator.py` | $\forall s, d, p: \sum_{e: s \in \text{sections}(e)} A_{e, d, p} \le 1$ | Map CSE7 to G2; verify solver avoids Tuesday 15:00 clash between CSN5003 and CSN5001. | **Fully Implemented** |
| **REQ-HC-03** | **Classroom Conflict Prevention:** A classroom cannot be double-booked. | `backend/solver.py` | $\forall r, d, p: \sum_e Z_{e, r, d, p} \le 1$ where $Z = Y_{e,r} \land A_{e,d,p}$ | Open Room-wise view for Room 301 or 402; confirm only one course per period. | **Fully Implemented** |
| **REQ-HC-04** | **Laboratory Conflict Prevention:** A lab cannot be allocated to two practicals simultaneously. | `backend/solver.py` | Identical room exclusion formulation applied across `CL5`, `CL13`, `CL14`, `DS lab`. | View Room-wise timetable for Computer Lab CL14; confirm no overlap. | **Fully Implemented** |
| **REQ-HC-05** | **Faculty Availability:** Sessions cannot be placed during unavailable faculty times. | `backend/solver.py` | If $\exists f \in \text{faculty\_ids}(e): \text{avail}(f, d, p) = \text{False}$, then $X_{e, d, p} = 0$ | Toggle faculty availability in UI; solver strictly avoids unavailable slots. | **Fully Implemented** |
| **REQ-HC-06** | **Room Capacity Enforcement:** Assigned room capacity must seat enrolled students (when capacities configured). | `backend/solver.py` | $\sum_r Y_{e, r} \times \text{cap}(r) \ge \text{strength}(e)$ | If capacities entered, solver ensures joint capacity; unverified capacities flagged as notices. | **Fully Implemented** |
| **REQ-HC-07** | **Room Type Matching:** Lectures in classrooms; practicals in computer labs. | `backend/solver.py` | Restricts $Y_{e, r}$ to matching room types or explicitly designated source rooms. | Check DSN5001 practical (assigned to 301+CL14); DSN5004 practical (assigned to 305+CL13+CL14). | **Fully Implemented** |
| **REQ-HC-08** | **Session Duration & Breaks:** Consecutive periods for duration $>1$ without bridging lunch break. | `backend/solver.py` | Valid start periods strictly bounded by $p + \text{dur} \le 8$ and cannot cross lunch break. | View 2-period practicals: occupy contiguous periods (e.g. P3-P4 or P6-P7); never cross lunch. | **Fully Implemented** |
| **REQ-HC-09** | **Multi-Room Practicals & Allocation Modes:** Simultaneous bundle vs single from eligible. | `backend/solver.py` | Bundles require $\sum_r Y_{e,r} == |\text{bundle}|$; eligible requires $\sum_r Y_{e,r} == 1$. | View DSN5004: displays `Bundle: 305 + CL13 + CL14 (Simultaneous)`. | **Fully Implemented** |
| **REQ-HC-10** | **Cross-Department Coordination:** Coordinated shared courses and faculty across CSE, AI, DS. | `backend/solver.py`<br>`backend/sample_data.py` | Dr. Ravpreet teaches across both CSE Core and CSE (AI); solver coordinates both with zero clashes. | Check Dr. Ravpreet's schedule in Faculty view; observe both CSE and AI courses clash-free. | **Fully Implemented** |

---

## 3. Verification, Visualization & Export

| Requirement ID | Requirement Description | Implementation Location | Technical Mechanism | Demonstration Method | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **REQ-VAL-01** | **Independent Post-Solve Validation & Tiered Reporting:** Separate audit checking all hard constraints and unverified assumptions. | `backend/validator.py`<br>`backend/app.py` | Standalone Python module iterating over all 91 events; separates verified checks from unverified assumptions. | Displays `VALIDATED WITH WARNINGS` when G1/G2 unmapped, and `FULLY VALIDATED` when confirmed. | **Fully Implemented** |
| **REQ-UI-01** | **Section-Wise Timetable View:** Weekly grid for chosen section or course group. | `frontend/js/timetable.js`<br>`frontend/index.html` | Matrix renderer with 8 periods on X-axis, days on Y-axis, lunch break, and co-instructors. | On *View Timetable*, select *Section-Wise* $\rightarrow$ `CSE1`, `Group G1`, etc. | **Fully Implemented** |
| **REQ-UI-02** | **Faculty-Wise Timetable View:** Weekly teaching schedule per faculty. | `frontend/js/timetable.js` | Filters events by `faculty_id`. | Select *Faculty-Wise* $\rightarrow$ `Dr. Ravpreet` or `Dr. Rajesh Bhatia`. | **Fully Implemented** |
| **REQ-UI-03** | **Room-Wise Timetable View:** Weekly booking schedule per venue. | `frontend/js/timetable.js` | Filters events by `room_ids`. | Select *Room-Wise* $\rightarrow$ `Room 301` or `CL14`. | **Fully Implemented** |
| **REQ-UI-04** | **Master Timetable View:** Global schedule across all campus resources. | `frontend/js/timetable.js` | Unfiltered matrix rendering with Programme Scoping (`CSE`, `AI`, `DS`, `All`). | Select *Master View* and toggle Programme dropdown. | **Fully Implemented** |
| **REQ-EXP-01** | **CSV Export:** Downloadable timetable spreadsheet. | `backend/app.py` (`/api/export-csv`) | Generates standard UTF-8 CSV stream with days, times, courses, faculty, and rooms. | Click *Export CSV* button; open downloaded `college_timetable.csv`. | **Fully Implemented** |
| **REQ-EXP-02** | **Print Preview:** Clean, black-and-white projector & paper print format. | `frontend/css/styles.css` (`@media print`) | CSS print rules that strip UI navigation and format table cleanly for paper/PDF. | Click *Print* button or press Ctrl+P. | **Fully Implemented** |
| **REQ-DIAG-01** | **Infeasibility Diagnostics:** Explains why a schedule is impossible. | `backend/solver.py` (`generate_diagnostics`) | Structural analysis of over-demanded faculty availability and room bottlenecks. | Mark a faculty 100% unavailable; click *Generate*; read diagnostic error list. | **Fully Implemented** |
| **REQ-REGEN-01** | **On-Demand Dynamic Regeneration:** Re-solves when inputs change without restart. | `backend/app.py` (`/api/generate`)<br>`backend/store.py` | Flushes previous solution and re-executes CP-SAT on updated in-memory state in ~1.1s. | Change any course or faculty parameter; click *Generate Feasible Timetable*. | **Fully Implemented** |
