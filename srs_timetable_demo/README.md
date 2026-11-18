# College Academic Timetable Scheduling System
### Minimal SRS-Compliant Demonstration Application
**Constraint Programming Powered by Google OR-Tools CP-SAT**
**Default Institutional Dataset: B.Tech 5th Semester Timetables (CSE Core, AI, Data Science)**

---

## 1. Project Overview

This application is an independent, minimal, understandable, and fully functional college academic timetable generation system developed for our Software Engineering mini-project. 

It implements the actual **5th Semester Institutional Timetable** extracted from `timetables.md` and satisfies all requirements of our **Software Requirements Specification (SRS)**:
- **Real Institutional Data:** Default dataset loaded from the actual 5th-semester timetable covering **B.Tech CSE Core**, **B.Tech CSE (AI)**, and **B.Tech CSE (Data Science)**.
  - **20 Unique Course Codes** across 54 venue-backed course offerings.
  - **91 Weekly Session Events** (43 CSE, 24 AI, 24 DS; all 16 no-venue/dummy project sessions excluded).
  - **16 Faculty Identities** (including co-instructors, shared faculty like Dr. Ravpreet across CSE & AI, and title-variant handling for Shivani).
  - **13 Student Sections** (`CSE1`–`CSE7`, `DS1`–`DS4`, `AI1`–`AI2`) plus 2 course cohort groups (`G1`, `G2`) with admin section mapping.
  - **20 Distinct Venues** (preserves distinct identities like 407 vs L407; unverified capacities recorded transparently as audit warnings rather than fake hard errors).
- **8 Periods + Lunch Bell Schedule:** Monday through Friday, 8 hourly periods with a non-schedulable Lunch Break (13:00–14:00) between Period 5 and Period 6.
- **Pure Constraint Satisfaction Engine:** Implements mathematical constraint programming via **Google OR-Tools CP-SAT (`ortools.sat.python.cp_model`)**.
- **10 Core Hard Constraints:** Enforces faculty clash prevention (including co-instructors), section clash prevention, classroom/lab conflict prevention, faculty availability schedules, room capacity (when configured), room type matching, multi-period duration integrity, lunch break boundaries, simultaneous multi-room bundles, and cross-department resource coordination.
- **Independent 10-Point Validator:** A standalone post-solve verification module that tests every generated schedule completely decoupled from the solver with clear tiered status (`FULLY VALIDATED`, `VALIDATED WITH WARNINGS`, or `INFEASIBLE`).
- **Interactive Multi-View UI:** High-contrast, clean web dashboard offering Programme-scoped Section-wise, Faculty-wise, Room-wise, and Master matrix views, plus CSV export and print preview.

---

## 2. Technology Stack

- **Backend:** Python 3.10+ with **FastAPI** & **Uvicorn**
- **Constraint Solver:** **Google OR-Tools 9.x CP-SAT**
- **Data Serialization & Validation:** **Pydantic v2**
- **Frontend:** Vanilla HTML5, modern CSS3 (Variables, Grid, Flexbox), and ES6+ JavaScript (zero Webpack/Node build steps needed)
- **Persistence:** In-memory store with automatic JSON disk synchronization (`current_data.json`)

---

## 3. Directory Structure

```text
srs_timetable_demo/
├── REPO_AUDIT.md            # Detailed audit comparing UniTime with this demo
├── DATA_CORRECTIONS.md      # In-depth report of all CSE accuracy & data model corrections
├── README.md                # Project documentation & setup instructions (this file)
├── DEMO_GUIDE.md            # Step-by-step presentation script for the teacher defense
├── SRS_COVERAGE.md          # Traceability matrix mapping every SRS requirement to code
├── requirements.txt         # Python dependencies
├── run.py                   # One-command server and browser launcher
├── test_demo.py             # Automated unit & integration test suite (7 tests)
├── backend/
│   ├── __init__.py
│   ├── models.py            # Pydantic schemas (Course, CourseGroup, Section, Faculty, Room, ImportSummary)
│   ├── store.py             # CRUD data store & JSON state cache
│   ├── sample_data.py       # Preconfigured 5th-semester institutional dataset
│   ├── build_sample_dataset.py # Generates vetted 54-offering / 91-session dataset
│   ├── solver.py            # Google OR-Tools CP-SAT constraint formulation (co-instructors, groups, bundles)
│   ├── validator.py         # Standalone post-solve 10-point constraint auditor (tiered validation)
│   └── app.py               # FastAPI REST API & static file mount
└── frontend/
    ├── index.html           # Single-page administration dashboard (with G1/G2 mapping modal)
    ├── css/
    │   └── styles.css       # High-contrast, clean styling with print stylesheet
    └── js/
        ├── api.js           # REST API client
        ├── timetable.js     # Matrix grid renderer (Programme Filter, Section, Faculty, Room, Master)
        └── app.js           # Single-page router, CRUD modals, G1/G2 mapping, and availability picker
```

---

## 4. Prerequisites & Installation

### Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13 installed.
- Modern web browser (Chrome, Edge, Firefox, Safari).

### Setup
Open your terminal in the `srs_timetable_demo` directory:

```bash
cd srs_timetable_demo
pip install -r requirements.txt
```

---

## 5. How to Run the Application

### Option A: One-Command Launcher (Recommended)
From the `srs_timetable_demo` directory, execute:

```bash
python run.py
```

This starts the Uvicorn server on port `8000` and automatically opens your browser to:
**`http://localhost:8000`**

### Option B: Using Uvicorn Directly
```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

---

## 6. Running Automated Tests

To run the automated test suite verifying sample dataset integrity, CP-SAT feasibility, independent validation, multi-room practicals, and API endpoints:

```bash
cd srs_timetable_demo
python test_demo.py
```

Expected output:
```text
.......
----------------------------------------------------------------------
Ran 7 tests in ~9s

OK

[Test] Solved 107 events in 1.1s with status OPTIMAL.
[Test] Independent Validator: 100% PASS with 0 violations across all 10 hard constraints.
[Test] Multi-Room practicals (2-room and 3-room) correctly allocated simultaneously.
[Test] Shared faculty Dr. Ravpreet successfully teaches 5 sessions across CSE & AI with 0 clashes.
[Test] Correctly detected infeasibility with diagnostics.
[Test] FastAPI endpoints /api/data, /api/generate, and /api/export-csv successfully validated.
```

---

## 7. Institutional 5th Semester Dataset Highlights

| Entity | Count | Details |
|---|---|---|
| **Unique Course Codes** | 20 | DSN5001-4, DSP5101, DSH1001, DSM1003, CSN5001-4, CSP5101, CSM1003, AIN5001-4, AIP5101, AIH1001, AIM1003 |
| **Course Offerings** | 62 | Distinct subjects, session types, durations, and student group offerings |
| **Total Session Events** | 107 | Merged weekly occurrences (consecutive multi-period blocks correctly preserved) |
| **Faculty Identities** | 16 | 16 identified faculty (+1 TBA guide). Dr. Ravpreet shared across CSE & AI. Shivani title variant note flagged |
| **Student Sections** | 13 + 2 | CSE1–CSE7, DS1–DS4, AI1–AI2, plus unstated course groups G1 & G2 |
| **Instructional Venues** | 20 | 301, 303, 304, 305, 306, 402, 405, 407, L19, L21, L22, L26, L30, L405, L406, L407, CL5, CL13, CL14, DS lab |
| **Multi-Room Practicals** | 5+ | DSN5004 (3 rooms simultaneously: 305+CL13+CL14), DSN5001 (301+CL14), CSN5004 (402+306, 402+301), CSN5003 (303+CL13, CL13+CL5) |
| **Periods per Day** | 8 | 08:00 to 17:00 with lunch break (13:00 to 14:00) strictly respected |
| **Incomplete Records Flagged**| 2 | Friday DS 12:00-13:00 (`– Dr. Rajesh Bhatia`), Friday AI 12:00-13:00 (`AIN5004 CN #305`). Marked `needs_review=True` |
