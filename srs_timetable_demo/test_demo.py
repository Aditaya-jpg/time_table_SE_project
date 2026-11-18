"""
Automated Test Suite for the College Timetable Scheduling Demo
Audited and Corrected for 5th Semester Institutional Timetable:
1. Data models and 54 venue-backed course offerings (91 weekly sessions).
2. Complete exclusion of 16 no-venue / incomplete sessions (CSP5101, DSP5101, DSH1001, AIP5101, AIH1001, DSN_INCOMPLETE) and TBA faculty.
3. Separate CourseGroup entity (G1, G2) with interactive section mapping.
4. Co-instructor scheduling and multi-faculty conflict prevention (Dr. Sandeep Harit + Dr. Ravpreet, Dr. Tejinder + Shivani, Dr. Divya Bansal + Pooja).
5. Room allocation modes: SIMULTANEOUS_BUNDLE vs SINGLE_FROM_ELIGIBLE.
6. Conflict prevention on known potential clash (Tuesday 15:00 CSN5003 SE G2 vs CSN5001 TOC Tut CSE7).
7. Validation reporting: VALIDATED WITH WARNINGS vs FULLY VALIDATED.
8. FastAPI REST endpoints including /api/groups and updated CSV export.
"""

import sys
import os
import unittest

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.sample_data import get_sample_dataset
from backend.solver import solve_timetable
from backend.validator import validate_timetable
from backend.models import Course, Room, Faculty, Section, CourseGroup, TimeSlotConfig, TimetableData
from backend.store import DataStore
from fastapi.testclient import TestClient
from backend.app import app


class TestTimetableDemo(unittest.TestCase):

    def setUp(self):
        self.sample_data = get_sample_dataset()

    def test_01_sample_dataset_integrity(self):
        """Verifies that audited dataset satisfies all venue-backed 5th-semester requirements."""
        # 13 actual student sections + 2 separate CourseGroups
        self.assertEqual(len(self.sample_data.sections), 13, "Must have exactly 13 student sections (7 CSE, 4 DS, 2 AI)")
        self.assertEqual(len(self.sample_data.course_groups), 2, "Must have exactly 2 CourseGroup entities (G1, G2)")
        self.assertEqual(len(self.sample_data.faculty), 16, "Must have exactly 16 identified faculty (TBA removed)")
        self.assertEqual(len(self.sample_data.rooms), 20, "Must have 20 distinct venues")
        self.assertEqual(len(self.sample_data.courses), 54, "Must have exactly 54 venue-backed course offerings")

        total_sessions = sum(c.sessions_per_week for c in self.sample_data.courses)
        self.assertEqual(total_sessions, 91, "Must have exactly 91 weekly session events (43 CSE, 24 AI, 24 DS)")

        # Verify no-venue courses are permanently excluded
        excluded_codes = {"CSP5101", "DSP5101", "DSH1001", "AIP5101", "AIH1001", "DSN_INCOMPLETE"}
        present_codes = {c.code for c in self.sample_data.courses}
        self.assertTrue(excluded_codes.isdisjoint(present_codes), f"No-venue courses must be excluded: {excluded_codes & present_codes}")

        # Check for cross-department shared faculty (Dr. Ravpreet)
        shared_fac = [f for f in self.sample_data.faculty if f.is_shared]
        self.assertEqual(len(shared_fac), 1, "Dr. Ravpreet must be marked as shared faculty")
        self.assertEqual(shared_fac[0].name, "Dr. Ravpreet")

        # Check for co-instructors
        multi_fac_courses = [c for c in self.sample_data.courses if len(c.faculty_ids) > 1]
        self.assertGreaterEqual(len(multi_fac_courses), 3, "Must have co-instructors on TOC Tut, SE Lab, and CN")

        # Check allocation modes
        bundle_courses = [c for c in self.sample_data.courses if c.allocation_mode == "SIMULTANEOUS_BUNDLE"]
        eligible_courses = [c for c in self.sample_data.courses if c.allocation_mode == "SINGLE_FROM_ELIGIBLE"]
        self.assertGreaterEqual(len(bundle_courses), 5, "Must have simultaneous bundle practicals")
        self.assertGreaterEqual(len(eligible_courses), 5, "Must have single from eligible lecture courses")

    def test_02_cpsat_solver_feasibility(self):
        """Tests that Google OR-Tools CP-SAT generates an optimal/feasible timetable for all 91 sessions."""
        solution = solve_timetable(self.sample_data, time_limit_seconds=15.0)
        self.assertIn(solution.status, ("OPTIMAL", "FEASIBLE"), f"Expected feasible solution, got: {solution.status}")
        self.assertEqual(len(solution.scheduled_events), 91, "All 91 session events must be scheduled")
        print(f"\n[Test] Solved 91 venue-backed events in {solution.solve_time_seconds}s with status {solution.status}.")

    def test_03_independent_validator_warnings_when_unmapped(self):
        """Tests that validator reports VALIDATED WITH WARNINGS when G1/G2 are unmapped."""
        solution = solve_timetable(self.sample_data, time_limit_seconds=15.0)
        self.assertIn(solution.status, ("OPTIMAL", "FEASIBLE"))

        report = validate_timetable(self.sample_data, solution.scheduled_events)
        self.assertTrue(report.is_valid, f"Violations found: {report.details}")
        self.assertEqual(report.overall_status, "VALIDATED WITH WARNINGS")
        self.assertTrue(any("Student Section Conflicts: Unverified" in w for w in report.unverified_constraints))
        self.assertEqual(report.faculty_conflicts, 0)
        self.assertEqual(report.room_conflicts, 0)
        print(f"[Test] Unmapped validator: VALIDATED WITH WARNINGS as expected.")

    def test_04_g1_g2_mapping_prevents_overlap(self):
        """
        Tests that when CSE7 is mapped to G2, the solver prevents overlap between
        CSN5003 SE (G2) and CSN5001 TOC Tut (CSE7).
        """
        data = get_sample_dataset()
        # Map G2 to CSE5, CSE6, CSE7
        for g in data.course_groups:
            if g.id == "GRP_G2":
                g.section_ids = ["SEC_CSE_5", "SEC_CSE_6", "SEC_CSE_7"]
                g.is_verified = True
            elif g.id == "GRP_G1":
                g.section_ids = ["SEC_CSE_1", "SEC_CSE_2", "SEC_CSE_3", "SEC_CSE_4"]
                g.is_verified = True

        solution = solve_timetable(data, time_limit_seconds=15.0)
        self.assertIn(solution.status, ("OPTIMAL", "FEASIBLE"))

        # Find CSN5003 SE (G2) and CSN5001 TOC Tut (CSE7)
        g2_se_events = [e for e in solution.scheduled_events if e.course_code == "CSN5003" and e.group_id == "GRP_G2"]
        cse7_tut_events = [e for e in solution.scheduled_events if e.course_code == "CSN5001" and "SEC_CSE_7" in e.section_ids]

        self.assertGreater(len(g2_se_events), 0)
        self.assertGreater(len(cse7_tut_events), 0)

        # Verify no overlap between any G2 lecture and CSE7 tutorial
        for se in g2_se_events:
            for tut in cse7_tut_events:
                if se.day_index == tut.day_index:
                    overlap = max(se.start_period, tut.start_period) < min(se.end_period, tut.end_period)
                    self.assertFalse(overlap, f"Overlap detected between G2 lecture and CSE7 tutorial on {se.day_name}")

        # Validate with mapped groups -> section_status is Passed
        report = validate_timetable(data, solution.scheduled_events)
        self.assertTrue(report.is_valid)
        self.assertEqual(report.section_status, "Passed (G1/G2 Mapped)")

        # When room capacities are also confirmed, overall_status reaches FULLY VALIDATED
        for r in data.rooms:
            r.capacity = 500
        fully_report = validate_timetable(data, solution.scheduled_events)
        self.assertEqual(fully_report.overall_status, "FULLY VALIDATED")
        print("[Test] G1/G2 mapping successfully verified! Solver prevented clash and validator reported FULLY VALIDATED.")

    def test_05_multi_faculty_co_instructors(self):
        """Tests that co-instructors are both scheduled and have zero clashes."""
        solution = solve_timetable(self.sample_data, time_limit_seconds=15.0)

        # Check TOC Tut (Harit + Ravpreet)
        toc_tuts = [e for e in solution.scheduled_events if e.course_code == "CSN5001" and e.session_type == "Tutorial"]
        self.assertGreater(len(toc_tuts), 0)
        for tut in toc_tuts:
            self.assertIn("FAC_SANDEEP_HARIT", tut.faculty_ids)
            self.assertIn("FAC_RAVPREET", tut.faculty_ids)

        # Check SE Practical (Tejinder + Shivani)
        se_practicals = [e for e in solution.scheduled_events if e.course_code == "CSN5003" and e.session_type == "Practical"]
        self.assertGreater(len(se_practicals), 0)
        for lab in se_practicals:
            self.assertIn("FAC_TEJINDER", lab.faculty_ids)
            self.assertIn("FAC_SHIVANI", lab.faculty_ids)

        # Check CN (Divya Bansal + Pooja)
        cn_events = [e for e in solution.scheduled_events if e.course_code == "AIN5004"]
        self.assertGreater(len(cn_events), 0)
        for ev in cn_events:
            self.assertIn("FAC_DIVYA_BANSAL", ev.faculty_ids)
            self.assertIn("FAC_POOJA", ev.faculty_ids)

        print("[Test] Co-instructors correctly assigned to all sessions across CSE and AI.")

    def test_06_simultaneous_bundle_vs_single_eligible(self):
        """Tests simultaneous multi-room bundles vs single-room eligible selection."""
        solution = solve_timetable(self.sample_data, time_limit_seconds=15.0)

        # Check 3-room simultaneous bundle for DSN5004 practical
        dsn5004_labs = [e for e in solution.scheduled_events if e.course_code == "DSN5004" and e.session_type == "Practical"]
        for ev in dsn5004_labs:
            self.assertEqual(ev.allocation_mode, "SIMULTANEOUS_BUNDLE")
            self.assertEqual(len(ev.room_ids), 3)
            self.assertEqual(sorted(ev.room_ids), ["305", "CL13", "CL14"])

        # Check single eligible for CSN5001 G2 lecture (L21, L407, or L26)
        csn5001_lecs = [e for e in solution.scheduled_events if e.course_code == "CSN5001" and e.group_id == "GRP_G2" and e.session_type == "Lecture"]
        self.assertGreater(len(csn5001_lecs), 0)
        for ev in csn5001_lecs:
            self.assertEqual(ev.allocation_mode, "SINGLE_FROM_ELIGIBLE")
            self.assertEqual(len(ev.room_ids), 1)
            self.assertIn(ev.room_ids[0], ["L21", "L407", "L26"])

        print("[Test] Room allocation modes correctly enforced: SIMULTANEOUS_BUNDLE and SINGLE_FROM_ELIGIBLE.")

    def test_07_api_endpoints(self):
        """Tests FastAPI REST endpoints including /api/groups and CSV export."""
        client = TestClient(app)

        # GET /api/data
        res = client.get("/api/data")
        self.assertEqual(res.status_code, 200)
        data_json = res.json()
        self.assertEqual(len(data_json["sections"]), 13)
        self.assertEqual(len(data_json["course_groups"]), 2)
        self.assertEqual(len(data_json["faculty"]), 16)
        self.assertEqual(len(data_json["rooms"]), 20)
        self.assertEqual(len(data_json["courses"]), 54)

        # GET /api/groups
        grp_res = client.get("/api/groups")
        self.assertEqual(grp_res.status_code, 200)
        self.assertEqual(len(grp_res.json()), 2)

        # PUT /api/groups/GRP_G1/mapping
        put_res = client.put("/api/groups/GRP_G1/mapping", json={"section_ids": ["SEC_CSE_1", "SEC_CSE_2"]})
        self.assertEqual(put_res.status_code, 200)
        self.assertEqual(put_res.json()["section_ids"], ["SEC_CSE_1", "SEC_CSE_2"])
        self.assertTrue(put_res.json()["is_verified"])

        # POST /api/generate
        gen_res = client.post("/api/generate")
        self.assertEqual(gen_res.status_code, 200)
        gen_json = gen_res.json()
        self.assertIn(gen_json["status"], ("OPTIMAL", "FEASIBLE"))
        self.assertEqual(len(gen_json["scheduled_events"]), 91)

        # GET /api/export-csv
        csv_res = client.get("/api/export-csv")
        self.assertEqual(csv_res.status_code, 200)
        self.assertIn("text/csv", csv_res.headers["content-type"])
        csv_lines = [l for l in csv_res.text.strip().split("\n") if l]
        self.assertEqual(len(csv_lines), 92, "CSV must have header + 91 scheduled events")
        print("[Test] REST API /api/data, /api/groups, /api/generate, and /api/export-csv successfully validated.")


if __name__ == "__main__":
    unittest.main()
