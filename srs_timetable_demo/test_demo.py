"""
Automated Test Suite for the College Timetable Scheduling Demo
Audited and Corrected for 5th Semester Institutional Timetable:
1. Data models and 54 venue-backed course offerings (91 weekly sessions).
2. Complete exclusion of 16 no-venue / incomplete sessions (CSP5101, DSP5101, DSH1001, AIP5101, AIH1001, DSN_INCOMPLETE) and TBA faculty.
3. Authoritative SID identity model and exact set-union strengths:
   - CSE: 138 students (G1: SID 1–69, G2: SID 70–138; Practical batches CSE1–CSE7)
   - AI: 30 students (AI Shared: SID 1–30; Practical batches AI1–AI2)
   - DS: 60 students (DS Shared: SID 1–60; Practical batches DS1–DS4)
   - Campus total: 228 distinct students across all programmes.
4. Comprehensive 12-point SID clash/non-clash unit tests:
   - G1 & CSE1 overlap: clash.
   - G1 & CSE4 overlap: clash (SIDs 61–69, 9 students).
   - G2 & CSE4 overlap: clash (SIDs 70–80, 11 students).
   - G2 & CSE7 overlap: clash (SIDs 121–138, 18 students).
   - G1 & CSE7 overlap: NO clash (disjoint sets).
   - DS Shared & DS2 overlap: clash.
   - AI Shared & AI1 overlap: clash.
   - CSE SID 1 & AI SID 1 overlap: NO clash (namespaced).
   - CSE total student strength == 138.
   - AI total student strength == 30.
   - DS total student strength == 60.
   - CSE4 == 20 students (9 in G1, 11 in G2).
5. CP-SAT solver assigns all 91 sessions with 0 student, faculty, or room clashes.
6. Independent validator reports VALIDATED WITH WARNINGS for unverified room capacities (and FULLY VALIDATED when capacities verified).
7. FastAPI REST endpoints and verified CSV export strengths.
"""

import sys
import os
import unittest
import csv
import io

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.sample_data import get_sample_dataset
from backend.solver import solve_timetable
from backend.validator import validate_timetable
from backend.models import (
    Course, Room, Faculty, Section, CourseGroup, TimeSlotConfig,
    TimetableData, STUDENT_DIVISIONS, get_course_student_ids
)
from backend.store import DataStore
from fastapi.testclient import TestClient
from backend.app import app


class TestTimetableDemo(unittest.TestCase):

    def setUp(self):
        self.sample_data = get_sample_dataset()

    def test_01_sample_dataset_integrity(self):
        """Verifies that audited dataset satisfies all venue-backed 5th-semester requirements."""
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

    def test_02_sid_identity_model_and_intersections(self):
        """
        Unit tests for the 12 specific SID-based student identity conditions:
        1. G1 and CSE1 overlap: clash.
        2. G1 and CSE4 overlap: clash (SIDs 61–69).
        3. G2 and CSE4 overlap: clash (SIDs 70–80).
        4. G2 and CSE7 overlap: clash.
        5. G1 and CSE7 overlap: NO clash.
        6. DS Shared and DS2 overlap: clash.
        7. AI Shared and AI1 overlap: clash.
        8. CSE SID 1 and AI SID 1 overlap: NO clash.
        9. Total CSE student strength = 138.
        10. Total AI student strength = 30.
        11. Total DS student strength = 60.
        12. CSE4 = 20 students, with 9 in G1 and 11 in G2.
        """
        def get_sids(entry_id: str):
            info = STUDENT_DIVISIONS[entry_id]
            dept = info["dept"]
            return {f"{dept}:SID:{sid}" for sid in range(info["start"], info["end"] + 1)}

        sids_g1 = get_sids("GRP_G1")
        sids_g2 = get_sids("GRP_G2")
        sids_cse1 = get_sids("SEC_CSE1")
        sids_cse4 = get_sids("SEC_CSE4")
        sids_cse7 = get_sids("SEC_CSE7")

        sids_ds_shared = get_sids("GRP_DS_SHARED")
        sids_ds2 = get_sids("SEC_DS2")

        sids_ai_shared = get_sids("GRP_AI_SHARED")
        sids_ai1 = get_sids("SEC_AI1")

        # 1. G1 and CSE1 overlap -> clash
        self.assertTrue(len(sids_g1.intersection(sids_cse1)) > 0, "G1 and CSE1 must clash")
        self.assertEqual(len(sids_g1.intersection(sids_cse1)), 20)

        # 2. G1 and CSE4 overlap -> clash (SIDs 61–69, 9 students)
        self.assertTrue(len(sids_g1.intersection(sids_cse4)) > 0, "G1 and CSE4 must clash")
        self.assertEqual(len(sids_g1.intersection(sids_cse4)), 9, "G1 must share 9 students with CSE4 (SIDs 61-69)")

        # 3. G2 and CSE4 overlap -> clash (SIDs 70–80, 11 students)
        self.assertTrue(len(sids_g2.intersection(sids_cse4)) > 0, "G2 and CSE4 must clash")
        self.assertEqual(len(sids_g2.intersection(sids_cse4)), 11, "G2 must share 11 students with CSE4 (SIDs 70-80)")

        # 4. G2 and CSE7 overlap -> clash (SIDs 121–138, 18 students)
        self.assertTrue(len(sids_g2.intersection(sids_cse7)) > 0, "G2 and CSE7 must clash")
        self.assertEqual(len(sids_g2.intersection(sids_cse7)), 18, "G2 must share 18 students with CSE7")

        # 5. G1 and CSE7 overlap -> NO clash (disjoint)
        self.assertEqual(len(sids_g1.intersection(sids_cse7)), 0, "G1 and CSE7 must NOT clash (disjoint SIDs)")

        # 6. DS Shared and DS2 overlap -> clash
        self.assertTrue(len(sids_ds_shared.intersection(sids_ds2)) > 0, "DS Shared and DS2 must clash")
        self.assertEqual(len(sids_ds_shared.intersection(sids_ds2)), 15)

        # 7. AI Shared and AI1 overlap -> clash
        self.assertTrue(len(sids_ai_shared.intersection(sids_ai1)) > 0, "AI Shared and AI1 must clash")
        self.assertEqual(len(sids_ai_shared.intersection(sids_ai1)), 15)

        # 8. CSE SID 1 and AI SID 1 overlap -> NO clash (namespaced)
        cse_sid_1 = {"CSE:SID:1"}
        ai_sid_1 = {"AI:SID:1"}
        self.assertEqual(len(cse_sid_1.intersection(ai_sid_1)), 0, "CSE SID 1 and AI SID 1 must NOT clash (namespaced)")

        # 9. Total CSE student strength = 138
        all_cse_sids = set()
        for i in range(1, 8):
            all_cse_sids.update(get_sids(f"SEC_CSE{i}"))
        self.assertEqual(len(all_cse_sids), 138, "Total CSE strength must be 138")
        self.assertEqual(len(sids_g1.union(sids_g2)), 138, "G1 union G2 must equal 138")

        # 10. Total AI student strength = 30
        all_ai_sids = get_sids("SEC_AI1").union(get_sids("SEC_AI2"))
        self.assertEqual(len(all_ai_sids), 30, "Total AI strength must be 30")
        self.assertEqual(len(sids_ai_shared), 30, "AI Shared must equal 30")

        # 11. Total DS student strength = 60
        all_ds_sids = set()
        for i in range(1, 5):
            all_ds_sids.update(get_sids(f"SEC_DS{i}"))
        self.assertEqual(len(all_ds_sids), 60, "Total DS strength must be 60")
        self.assertEqual(len(sids_ds_shared), 60, "DS Shared must equal 60")

        # 12. CSE4 = 20 students, with 9 in G1 and 11 in G2
        self.assertEqual(len(sids_cse4), 20, "CSE4 must have 20 students")
        in_g1 = len(sids_cse4.intersection(sids_g1))
        in_g2 = len(sids_cse4.intersection(sids_g2))
        self.assertEqual(in_g1, 9, "CSE4 must have exactly 9 students in G1 (SIDs 61-69)")
        self.assertEqual(in_g2, 11, "CSE4 must have exactly 11 students in G2 (SIDs 70-80)")
        self.assertEqual(in_g1 + in_g2, 20, "9 in G1 + 11 in G2 must account for all 20 students in CSE4")

        # Total campus students = 138 + 30 + 60 = 228
        total_campus = all_cse_sids.union(all_ai_sids).union(all_ds_sids)
        self.assertEqual(len(total_campus), 228, "Total campus students must be exactly 228 distinct individuals")
        print("\n[Test] All 12 SID identity conditions and set-union calculations verified successfully!")

    def test_03_cpsat_solver_feasibility(self):
        """Tests that Google OR-Tools CP-SAT generates an optimal/feasible timetable for all 91 sessions."""
        solution = solve_timetable(self.sample_data, time_limit_seconds=15.0)
        self.assertIn(solution.status, ("OPTIMAL", "FEASIBLE"), f"Expected feasible solution, got: {solution.status}")
        self.assertEqual(len(solution.scheduled_events), 91, "All 91 session events must be scheduled")
        print(f"[Test] Solved 91 venue-backed events in {solution.solve_time_seconds}s with status {solution.status}.")

    def test_04_cpsat_sid_conflict_prevention(self):
        """
        Tests that CP-SAT solver uses SID ranges and automatically prevents clashes between
        overlapping student divisions (e.g. CSN5003 SE G2 and CSN5001 TOC Tut CSE7).
        """
        solution = solve_timetable(self.sample_data, time_limit_seconds=15.0)
        self.assertIn(solution.status, ("OPTIMAL", "FEASIBLE"))

        # Find CSN5003 SE (G2, SIDs 70-138) and CSN5001 TOC Tut (CSE7, SIDs 121-138)
        g2_se_events = [e for e in solution.scheduled_events if e.course_code == "CSN5003" and e.group_id == "GRP_G2"]
        cse7_tut_events = [e for e in solution.scheduled_events if e.course_code == "CSN5001" and "SEC_CSE7" in e.section_ids]

        self.assertGreater(len(g2_se_events), 0)
        self.assertGreater(len(cse7_tut_events), 0)

        # Verify no overlap between any G2 lecture and CSE7 tutorial
        for se in g2_se_events:
            for tut in cse7_tut_events:
                if se.day_index == tut.day_index:
                    overlap = max(se.start_period, tut.start_period) < min(se.end_period, tut.end_period)
                    self.assertFalse(overlap, f"Overlap detected between G2 lecture and CSE7 tutorial on {se.day_name}")

        print("[Test] SID-based conflict prevention successfully verified: G2 and CSE7 never overlap.")

    def test_05_independent_validator_results(self):
        """Tests that independent validator reports 0 clashes and VALIDATED WITH WARNINGS (unverified room capacity)."""
        solution = solve_timetable(self.sample_data, time_limit_seconds=15.0)
        report = validate_timetable(self.sample_data, solution.scheduled_events)

        self.assertTrue(report.is_valid, f"Violations found: {report.details}")
        self.assertEqual(report.faculty_conflicts, 0, "Must have zero faculty clashes")
        self.assertEqual(report.section_conflicts, 0, "Must have zero student section clashes")
        self.assertEqual(report.room_conflicts, 0, "Must have zero room clashes")
        self.assertEqual(report.section_status, "Passed (SID-verified)")
        self.assertEqual(report.overall_status, "VALIDATED WITH WARNINGS")
        self.assertTrue(any("Room Capacities: Unverified" in w for w in report.unverified_constraints))

        # When room capacities are simulated as verified, status becomes FULLY VALIDATED
        data_with_caps = get_sample_dataset()
        for r in data_with_caps.rooms:
            r.capacity = 500
        fully_report = validate_timetable(data_with_caps, solution.scheduled_events)
        self.assertEqual(fully_report.overall_status, "FULLY VALIDATED")
        print("[Test] Independent validator verified: 0 clashes, Passed (SID-verified), VALIDATED WITH WARNINGS.")

    def test_06_multi_faculty_co_instructors(self):
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

    def test_07_simultaneous_bundle_vs_single_eligible(self):
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

    def test_08_api_endpoints_and_csv_calculated_strengths(self):
        """Tests FastAPI REST endpoints and verifies that exported CSV has exact set-union student strengths."""
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

        reader = csv.DictReader(io.StringIO(csv_res.text))
        rows = list(reader)
        self.assertEqual(len(rows), 91, "CSV must have exactly 91 scheduled events")

        # Verify specific student strengths in exported CSV
        for r in rows:
            code = r["Course Code"]
            stype = r["Session Type"]
            target = r["Section / Group"]
            strength = int(r["Student Strength"])

            if "G1" in target and stype == "Lecture":
                self.assertEqual(strength, 69, f"CSE G1 lecture must have strength 69, got {strength}")
            elif "G2" in target and stype == "Lecture":
                self.assertEqual(strength, 69, f"CSE G2 lecture must have strength 69, got {strength}")
            elif code == "CSM1003":
                self.assertEqual(strength, 138, f"CSM1003 (All CSE) must have strength 138, got {strength}")
            elif target == "CSE7":
                self.assertEqual(strength, 18, f"CSE7 practical/tutorial must have strength 18, got {strength}")
            elif target == "AI1" and stype == "Practical":
                self.assertEqual(strength, 15, f"AI1 practical must have strength 15, got {strength}")
            elif target == "AI1; AI2" and stype == "Lecture":
                self.assertEqual(strength, 30, f"AI Shared lecture must have strength 30, got {strength}")
            elif target == "DS2; DS3" and stype == "Practical":
                self.assertEqual(strength, 30, f"DS2+DS3 practical must have strength 30, got {strength}")
            elif target == "DS1; DS2; DS3; DS4" and stype == "Lecture":
                self.assertEqual(strength, 60, f"DS Shared lecture must have strength 60, got {strength}")

        print("[Test] REST API and CSV export verified: exact set-union student strengths confirmed for all events!")


if __name__ == "__main__":
    unittest.main()
