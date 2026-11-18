# Repository Audit & Architectural Analysis
## UniTime Enterprise Platform vs. Minimal SRS-Based College Scheduling Demo

**Date:** November 18, 2026  
**Project:** College Timetable Scheduling Software Engineering Demo  
**Target Repository:** `Nikhil-Verma22/time_table_SE_project` (UniTime 4.9 Fork)  
**Output Location:** `/srs_timetable_demo/`  

---

## 1. Current Repository Technology Stack

An inspection of the root codebase reveals an enterprise multi-tier monolithic architecture designed for global university campuses:

| Layer | Existing UniTime Technologies | Notes & Observations |
| :--- | :--- | :--- |
| **Backend Language** | Java (JDK 11–17) | 2,634 Java source files across 80+ packages in `JavaSource/` |
| **Web Application Framework** | Apache Struts 2 (Struts 2.5/6 Convention plugin) | Dispatches `.action` endpoints; rigid XML action mappings |
| **Client-Side Framework** | Google Web Toolkit (GWT 2.9) | Compiled Java-to-JavaScript frontend loaded via `gwt.jsp` |
| **Database & ORM** | PostgreSQL 18 / MySQL + Hibernate 5 | Complex relational schema with 100+ tables (`session`, `course_offering`, `instr_offering_subpart`, etc.) |
| **Application Server** | Apache Tomcat 10.1 (Jakarta Servlet API) | Heavyweight servlet container with multi-filter chain |
| **Build Tools** | Apache Ant (`build.xml`) + Maven (`pom.xml`) | Requires multi-gigabyte build artifacts and GWT permutation compiles |
| **Security & Auth** | Spring Security + custom role filters | Superuser, Administrator, Departmental Manager, Advisor, Student |
| **Constraint Solver** | Apereo CPSolver (Tomas Muller's custom Java engine) | Employs iterative local search, great deluge, and conflict-based statistics |

---

## 2. How the Existing Timetable Generation Process Works

In UniTime, timetable generation operates as a distributed server-side batch solver:

1. **Academic Session Initialization:** A manager configures an academic term with date patterns, time patterns, departments, and solver groups.
2. **Data Model Construction:** Course hierarchies are structured through complex abstractions:
   `CourseOffering` $\rightarrow$ `InstructionalOffering` $\rightarrow$ `InstrOfferingConfig` $\rightarrow$ `SchedulingSubpart` $\rightarrow$ `Class_`.
3. **Solver Input Extraction:** XML configuration profiles define parameters (weights, decay, maximum idle time). The server reads the relational database and constructs CPSolver domain variables (`Lecture`, `Placement`, `TimeLocation`, `RoomLocation`).
4. **Constraint Solving:** CPSolver uses Java-based Constraint Satisfaction Problem (CSP) formulation:
   - Hard constraints: Resource clash (room, instructor, student).
   - Soft constraints: Preference penalties, travel distances, time patterns.
   - Algorithms: Conflict-Based Statistics (CBS), Min-Conflicts, Random Walk, Great Deluge.
5. **Interactive Lifecycle:** Solvers run asynchronously in background daemon threads (`SolverServer`), streaming progress to GWT clients via RPC. Managers manually inspect solutions, resolve conflicts, and commit solutions back to PostgreSQL.

---

## 3. Key Scheduling Components in UniTime

- **`org.unitime.timetable.solver.CourseTimetableSolver`**: Core manager orchestrating course solver instances.
- **`org.cpsolver.coursett.model.TimetableModel`**: CSP model holding variables, constraints, and placements.
- **`org.cpsolver.coursett.constraint.InstructorConstraint`**: Tracks faculty assignments and intervals.
- **`org.cpsolver.coursett.constraint.RoomConstraint`**: Manages room availability and reservations.
- **`org.cpsolver.coursett.constraint.StudentConflict`**: Minimizes cross-enrollment clashes.

---

## 4. Why the Existing System is Infeasible for a College Mini-Project Demo

1. **Excessive Complexity for Demonstration:**
   - 2,634 Java files make it impossible for a student team to explain the architecture during an oral defense.
   - Modifying a single constraint requires navigating deep abstractions across Hibernate entities, CPSolver interfaces, and GWT UI listeners.
2. **Heavy Operational Footprint:**
   - Requires running a local PostgreSQL database instance, configuring `build.properties`, and launching an Apache Tomcat server.
   - Running GWT compilation takes 15–20 minutes and requires massive RAM.
3. **Overkill Feature Scope:**
   - Features like ERP course catalog synchronization, role permissions, automated student sectioning, exam seating charts, and XML data exchange are irrelevant to the core academic scheduling SRS.
4. **Different Solver Paradigm:**
   - UniTime relies on Apereo CPSolver (heuristic iterative repair / simulated annealing).
   - Our academic SRS specifically mandates **Constraint Programming using Google OR-Tools CP-SAT**, which guarantees mathematical feasibility and constraint propagation.

---

## 5. Architectural Strategy for `/srs_timetable_demo/`

To satisfy our Software Requirements Specification (SRS) without touching the original project:

1. **Strict Isolation:** All code lives in `/srs_timetable_demo/`. Zero original files are touched or modified.
2. **Lightweight & High-Performance Stack:**
   - **Backend:** Python 3.13 + **FastAPI** + **Uvicorn** (instantly starts in <1 second, standard REST API).
   - **Solver Engine:** **Google OR-Tools CP-SAT (`ortools.sat.python.cp_model`)**, the gold standard in modern constraint programming.
   - **Independent Validator:** Standalone Python verification script that independently validates all 10 hard constraints directly against the candidate schedule.
   - **Frontend:** Clean, responsive, modern single-page dashboard built with vanilla HTML5, CSS3, and JavaScript—zero build steps, no Node.js/Webpack compile required, projector-friendly.
3. **Domain Mapping from SRS:**
   - Simplified direct entities: `Course`, `Section`, `CourseGroup`, `Faculty`, `Room`, `TimeSlot`.
   - Multi-session course events (e.g. DBMS: 3 lectures + 1 practical).
   - Multi-room practicals (allocating 2 or 3 computer labs simultaneously for a batch).
   - Dynamic regeneration, feasibility diagnostics, and multi-view schedule grids (Section, Faculty, Room, Master).

---

## 6. Corrected Architecture & Institutional Dataset Alignment

Following the detailed scheduling accuracy audit (detailed in `DATA_CORRECTIONS.md`):
- **No-Venue Sessions Permanently Excluded:** Removed 15 self-directed project/honours sessions and 1 unsupported incomplete session, bringing the active venue-backed schedule to exactly **54 course offerings** and **91 weekly session events**.
- **CourseGroup Entity:** Separated cohort groups (`G1`, `G2`) from 13 physical student sections (`CSE1`–`CSE7`, `DS1`–`DS4`, `AI1`–`AI2`), providing an administrative mapping UI.
- **Co-Instructors:** Added multi-faculty scheduling (`faculty_ids`) ensuring zero double-booking across co-instructors (`CSN5001 TOC Tut`, `CSN5003 SE Lab`, `AIN5004 CN`).
- **Room Allocation Modes:** Distinguished `SINGLE_FROM_ELIGIBLE` from `SIMULTANEOUS_BUNDLE`.
- **Tiered Validation:** Distinguishes verified constraint proofs from unverified institutional assumptions (`VALIDATED WITH WARNINGS` vs `FULLY VALIDATED`).
