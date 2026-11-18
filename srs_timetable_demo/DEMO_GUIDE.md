# College Timetable Scheduling Demo • Teacher Presentation Guide
### Presentation Walkthrough for 5th Semester Institutional Timetable Demo
**Constraint Programming Powered by Google OR-Tools CP-SAT**

---

## 🎯 Presentation Objectives
1. Prove that the application is **fully functional**, not a mock UI or random simulation.
2. Demonstrate how the **Google OR-Tools CP-SAT Constraint Programming engine** generates mathematically optimal academic schedules in ~1 second.
3. Show how the **5th Semester Institutional Timetable** (`timetables.md`) for B.Tech CSE Core, CSE (AI), and CSE (Data Science) is modeled accurately with 107 weekly session events.
4. Show how **10 hard constraints** from the SRS are modeled, satisfied, and independently validated.
5. Demonstrate multi-perspective visualization (Programme Scoping, Section-wise, Faculty-wise, Room-wise, Master Grid), print preview, and CSV export.

---

## 📋 Recommended Demonstration Script

### Step 1: Launch the Application
- Open terminal in `srs_timetable_demo/`.
- Run:
  ```bash
  python run.py
  ```
- The browser opens automatically at `http://localhost:8000`.
- **Talking Point:** *"Our application is an independent, lightweight web application built with FastAPI and Google OR-Tools CP-SAT in Python, paired with a modern responsive frontend. It contains zero legacy Java or enterprise container overhead."*

---

### Step 2: Show Dashboard & Institutional Dataset Summary
- Point out the KPI summary cards on the Dashboard:
  - **54 Course Offerings** (representing 20 unique course codes across CSE, AI, and Data Science).
  - **16 Faculty Members** (strictly verified instructors; artificial TBA removed).
  - **13 Student Sections** (`CSE1`–`CSE7`, `DS1`–`DS4`, `AI1`–`AI2`).
  - **2 Course Cohort Groups** (`G1`, `G2`).
  - **20 Classrooms & Laboratories**.
  - **91 Total Required Weekly Session Events** (43 CSE, 24 AI, 24 DS).
- Point to the **Institutional Dataset Summary Box**:
  - Explain that all 15 no-venue project/honours milestones and 1 incomplete entry were permanently excluded so the demo schedules only real venue-backed teaching sessions.
  - Highlight the transparent data quality notices regarding G1/G2 mapping and unmeasured room capacities.

---

### Step 3: Explain Course Offerings, Co-Instructors & Room Modes
- Click **"Courses"** in the sidebar.
- Point out:
  1. **Co-Instructors (Multi-Faculty Assignments):**
     - `CSN5001 TOC Tut`: Co-taught by **Dr. Sandeep Harit + Dr. Ravpreet**.
     - `CSN5003 SE Practical`: Co-supervised by **Dr. Tejinder + Shivani**.
     - `AIN5004 CN`: Co-taught by **Dr. Divya Bansal + Pooja**.
     - **Talking Point:** *"Instead of a single faculty ID, our model natively supports co-instructors. The solver guarantees zero simultaneous double-booking for any instructor in the team."*
  2. **Room Allocation Modes:**
     - **Simultaneous Bundles:** Practical sessions requiring multiple labs concurrently:
       - `DSN5004 IoT Lab`: Requires **3 rooms simultaneously** (`305 + CL13 + CL14`).
       - `CSN5004 DBMS Lab`: Requires **2 rooms simultaneously** (`402 + 306`).
       - `CSN5003 SE Lab`: Requires **2 rooms simultaneously** (`CL13 + CL5` or `303 + CL13`).
       - `DSN5001 DAIR Lab`: Requires **2 rooms simultaneously** (`301 + CL14`).
     - **Single from Eligible:** Lectures with multiple valid candidate rooms (e.g. `CSN5001 G2` in `L21`, `L407`, or `L26`). The solver picks exactly one room from the eligible pool.
  3. **Cohort Targets:** Clear distinction between individual student sections (`CSE1`, `AI1`) and cohort groups (`Group G1`, `Group G2`).

---

### Step 4: Demonstrate G1/G2 Section Mapping & Conflict Prevention
- Click **"Student Sections"** in the sidebar.
- Point out the 13 physical student sections (`CSE1`–`CSE7`, `DS1`–`DS4`, `AI1`–`AI2`).
- Scroll down to the **Course Cohort Groups (G1 & G2) Section Mapping** card:
  - Explain that G1 and G2 are lecture groups, not individual student classes.
  - Notice the badge: `Mapping Pending / Unverified`.
  - Click **"Configure Mapping"** for `Group G2`:
    - Select checkboxes for `CSE5`, `CSE6`, and `CSE7`.
    - Click **"Save Group Mapping"**.
  - Click **"Configure Mapping"** for `Group G1`:
    - Select checkboxes for `CSE1`, `CSE2`, `CSE3`, and `CSE4`.
    - Click **"Save Group Mapping"**.
  - Notice the badge immediately changes to `All Groups Verified`.
  - **Talking Point (Known Conflict Proof):** *"In the original timetable, Tuesday 15:00 has both CSN5003 SE (G2) and CSN5001 TOC Tut (CSE7). Now that CSE7 is mapped to G2, our CP-SAT solver automatically detects the student section clash and shifts one of them so that CSE7 students are never double-booked!"*

---

### Step 5: Show Faculty Directory & Cross-Department Sharing
- Click **"Faculty"** in the sidebar.
- Highlight **Dr. Ravpreet**:
  - Notice the badge: `Shared (CSE/AI)`.
  - **Talking Point:** *"Dr. Ravpreet teaches Theory of Computation across both B.Tech CSE Core and B.Tech CSE (AI). The CP-SAT solver coordinates her schedule across both departments with zero clashes."*
- Highlight **Shivani**:
  - Note the data quality annotation: *"Title and spelling variant in source timetable: Dr. Shivani / Ms. Shivani / Shivani. Unified for scheduling with review note."*

---

### Step 6: Show Classrooms, Laboratories & Venue Identities
- Click **"Classrooms & Labs"** in the sidebar.
- Point out the 20 distinct venues:
  - Classrooms: `301`, `303`, `304`, `305`, `306`, `402`, `405`, `407`.
  - Lecture Halls: `L19`, `L21`, `L22`, `L26`, `L30`, `L405`, `L406`, `L407`.
  - Computer Laboratories: `CL5`, `CL13`, `CL14`, `DS lab`.
- **Talking Point:** *"Distinct venue identities are preserved without merging (`407` vs `L407`, `305` vs `L405`). Room capacities were not specified in the college source timetable and are marked as 'Unverified' instead of inventing fake numbers."*

---

### Step 7: Show Daily Bell Schedule & Lunch Break
- Click **"Time Slots"** in the sidebar.
- Point out the 8 hourly periods:
  - Period 1 to Period 5: 08:00 to 13:00.
  - **Lunch Break: 13:00 to 14:00 (Break boundary after Period 5).**
  - Period 6 to Period 8: 14:00 to 17:00.
- **Talking Point:** *"The CP-SAT model strictly prevents any 2-period practical or long lecture from bridging across the 13:00–14:00 lunch break."*

---

### Step 8: Generate Timetable with Google OR-Tools CP-SAT
- Click **"Generate Timetable"** in the sidebar.
- Click **"Solve With Google OR-Tools"**.
- Watch the solver run:
  - Solves the discrete model in **~0.93 seconds**.
  - Status: **`OPTIMAL`**.
  - All **91 venue-backed weekly session events** successfully placed.
- **Talking Point:** *"This uses mathematical constraint satisfaction: boolean decision variables $X_{e, d, p}$ for time placement and $Y_{e, r}$ for room assignment. Google OR-Tools CP-SAT searches the combinatorial space using propagation, SAT clause learning, and multi-threading."*

---

### Step 9: Demonstrate Independent Validator & Tiered Reporting
- Point to the **Validation Summary Banner**:
  - If G1/G2 mappings or capacities are pending: shows `VALIDATED WITH WARNINGS` with explicit notices explaining that provisional scheduling succeeded without resource clashes.
  - If mappings are configured: shows `FULLY VALIDATED (100% FEASIBLE)`:
    - Faculty Clashes: `0` (across all co-instructors)
    - Section Clashes: `Passed (G1/G2 Mapped)`
    - Room Clashes: `0`
    - Duration Violations: `0`
    - Multi-Room Bundle Violations: `0`
- **Talking Point:** *"We implemented a decoupled verification module in `backend/validator.py`. It inspects the raw output timetable independently from the CP-SAT engine to mathematically prove zero clashes occur and clearly separates proven checks from unverified assumptions."*

---

### Step 9: Multi-Perspective Timetable Visualization
- Click **"View Timetable"** in the sidebar.
- **Programme Filter:**
  - Select **`B.Tech CSE Core`**: The schedule isolates CSE offerings (`CSN5001`, `CSN5002`, `CSN5003`, `CSN5004`, `CSP5101`, `CSM1003`).
  - Select **`B.Tech CSE (AI)`**: Isolates AI offerings (`AIN5001`, `AIN5002`, `AIN5003`, `AIN5004`, `AIP5101`, `AIH1001`, `AIM1003`).
  - Select **`B.Tech CSE (Data Science)`**: Isolates DS offerings (`DSN5001`, `DSN5002`, `DSN5003`, `DSN5004`, `DSP5101`, `DSH1001`, `DSM1003`).
- **Section-Wise View:**
  - Select **`CSE1`**, **`AI1`**, or **`DS1`** to see the student's weekly timetable.
  - Notice that 2-period practicals span two full columns.
  - Notice the **Lunch Break** column clearly separating Period 5 and Period 6.
- **Faculty-Wise View:**
  - Select **`Dr. Ravpreet`**: Show that her CSE and AI sessions are scheduled without conflict.
- **Room-Wise View:**
  - Select **`Room 301`** or **`CL14`**: Show that no two classes are ever double-booked into the room.
- **Master View:**
  - View all simultaneous campus activities across the institutional schedule.

---

### Step 10: Print & CSV Export
- Click **"Export CSV"**: Demonstrates generating an institutional CSV schedule file ready for download.
- Click **"Print"**: Shows the clean, printer-friendly CSS layout.

---

### Step 11: Run Automated Tests
- In terminal, execute:
  ```bash
  python test_demo.py
  ```
- Show all 7 unit and integration tests passing (`OK`), proving programmatic correctness to the evaluation committee.
