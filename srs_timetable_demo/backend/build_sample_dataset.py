"""
Builds backend/sample_data.py with exact, audited 5th semester dataset.
Removes all no-venue project/honours sessions.
Supports CourseGroup (G1, G2), multiple faculty members, and clean room allocation modes.
"""

import json

def generate_sample_data_py():
    sections = [
        ("SEC_CSE1", "CSE1", "CSE", "5th Semester", "Practical Batch", 1, 20, 20, "Practical batch (SID 1–20)"),
        ("SEC_CSE2", "CSE2", "CSE", "5th Semester", "Practical Batch", 21, 40, 20, "Practical batch (SID 21–40)"),
        ("SEC_CSE3", "CSE3", "CSE", "5th Semester", "Practical Batch", 41, 60, 20, "Practical batch (SID 41–60)"),
        ("SEC_CSE4", "CSE4", "CSE", "5th Semester", "Practical Batch", 61, 80, 20, "Practical batch (SID 61–80: 9 in G1, 11 in G2)"),
        ("SEC_CSE5", "CSE5", "CSE", "5th Semester", "Practical Batch", 81, 100, 20, "Practical batch (SID 81–100)"),
        ("SEC_CSE6", "CSE6", "CSE", "5th Semester", "Practical Batch", 101, 120, 20, "Practical batch (SID 101–120)"),
        ("SEC_CSE7", "CSE7", "CSE", "5th Semester", "Practical Batch", 121, 138, 18, "Practical batch (SID 121–138)"),
        ("SEC_DS1", "DS1", "DS", "5th Semester", "Practical Batch", 1, 15, 15, "Practical batch (SID 1–15)"),
        ("SEC_DS2", "DS2", "DS", "5th Semester", "Practical Batch", 16, 30, 15, "Practical batch (SID 16–30)"),
        ("SEC_DS3", "DS3", "DS", "5th Semester", "Practical Batch", 31, 45, 15, "Practical batch (SID 31–45)"),
        ("SEC_DS4", "DS4", "DS", "5th Semester", "Practical Batch", 46, 60, 15, "Practical batch (SID 46–60)"),
        ("SEC_AI1", "AI1", "AI", "5th Semester", "Practical Batch", 1, 15, 15, "Practical batch (SID 1–15)"),
        ("SEC_AI2", "AI2", "AI", "5th Semester", "Practical Batch", 16, 30, 15, "Practical batch (SID 16–30)"),
    ]

    course_groups = [
        ("GRP_G1", "G1", "CSE", "Lecture Division", 1, 69, 69, "Lecture division G1 (SID 1–69, 69 students)"),
        ("GRP_G2", "G2", "CSE", "Lecture Division", 70, 138, 69, "Lecture division G2 (SID 70–138, 69 students)"),
    ]

    faculty = [
        ("FAC_SURAJ_SRIVASTAVA", "Dr. Suraj Srivastava", "DS", "Professor", False, None),
        ("FAC_MANISH_KUMAR", "Dr. Manish Kumar", "DS", "Associate Professor", False, None),
        ("FAC_ISHITA", "Ms. Ishita", "DS", "Assistant Professor", False, None),
        ("FAC_RAJESH_BHATIA", "Dr. Rajesh Bhatia", "DS", "Professor", False, None),
        ("FAC_SANEHI", "Sanehi", "DS", "Assistant Professor", False, None),
        ("FAC_SANDEEP_HARIT", "Dr. Sandeep Harit", "CSE", "Professor", False, None),
        ("FAC_RAVPREET", "Dr. Ravpreet", "CSE/AI - Shared", "Associate Professor", True, "Shared faculty across B.Tech CSE and B.Tech CSE (AI)."),
        ("FAC_TEJINDER", "Dr. Tejinder", "CSE", "Associate Professor", False, None),
        ("FAC_DIPIKA", "Dr. Dipika", "CSE", "Assistant Professor", False, None),
        ("FAC_SHILPA", "Dr. Shilpa", "CSE", "Assistant Professor", False, None),
        ("FAC_PRAVNEET_KAUR", "Dr. Pravneet Kaur", "CSE", "Associate Professor", False, None),
        ("FAC_PADMAVATI", "Dr. Padmavati", "AI", "Professor", False, None),
        ("FAC_ALKA_JINDAL", "Dr. Alka Jindal", "AI", "Professor", False, None),
        ("FAC_DIVYA_BANSAL", "Dr. Divya Bansal", "AI", "Professor", False, None),
        ("FAC_POOJA", "Pooja", "AI", "Assistant Professor", False, None),
        ("FAC_SHIVANI", "Shivani", "CSE", "Assistant Professor", False, "Title and spelling variant in source timetable: Dr. Shivani / Ms. Shivani / Shivani. Unification preserved for scheduling; flagged for verification."),
    ]

    venues = [
        ("301", "Room 301", "Classroom"),
        ("303", "Room 303", "Classroom"),
        ("304", "Room 304", "Classroom"),
        ("305", "Room 305", "Classroom"),
        ("306", "Room 306", "Classroom"),
        ("402", "Room 402", "Classroom"),
        ("405", "Room 405", "Classroom"),
        ("407", "Room 407", "Classroom"),
        ("L19", "Lecture Hall L19", "Lecture Hall"),
        ("L21", "Lecture Hall L21", "Lecture Hall"),
        ("L22", "Lecture Hall L22", "Lecture Hall"),
        ("L26", "Lecture Hall L26", "Lecture Hall"),
        ("L30", "Lecture Hall L30", "Lecture Hall"),
        ("L405", "Lecture Hall L405", "Lecture Hall"),
        ("L406", "Lecture Hall L406", "Lecture Hall"),
        ("L407", "Lecture Hall L407", "Lecture Hall"),
        ("CL5", "Computer Lab CL5", "Computer Lab"),
        ("CL13", "Computer Lab CL13", "Computer Lab"),
        ("CL14", "Computer Lab CL14", "Computer Lab"),
        ("DS lab", "Data Science Lab", "Computer Lab"),
    ]

    # Courses definition: exactly 54 offerings covering 91 weekly sessions
    # Each entry:
    # (id, code, name, dept, faculty_ids, section_ids, group_id, session_type, spw, dur, rtype, rooms_req, alloc_mode, eligible_rooms, bundle_rooms, needs_review, review_reason, target_slots)
    courses = [
        # --- CSE: CSN5001 ---
        (
            "CRS_CSE_CSN5001_G1", "CSN5001", "CSN5001 TOC (G1)", "CSE",
            ["FAC_SANDEEP_HARIT"], [], "GRP_G1", "Lecture", 3, 1, "Lecture Hall", 1,
            "SINGLE_FROM_ELIGIBLE", ["L21"], [], False, None,
            [{"day_idx": 0, "start_period": 2, "duration": 1}, {"day_idx": 2, "start_period": 5, "duration": 1}, {"day_idx": 3, "start_period": 7, "duration": 1}]
        ),
        (
            "CRS_CSE_CSN5001_G2", "CSN5001", "CSN5001 TOC (G2)", "CSE",
            ["FAC_SANDEEP_HARIT"], [], "GRP_G2", "Lecture", 3, 1, "Lecture Hall", 1,
            "SINGLE_FROM_ELIGIBLE", ["L21", "L407", "L26"], [], False, None,
            [{"day_idx": 0, "start_period": 5, "duration": 1}, {"day_idx": 1, "start_period": 3, "duration": 1}, {"day_idx": 2, "start_period": 6, "duration": 1}]
        ),
        (
            "CRS_CSE_CSN5001_TUT_1", "CSN5001", "CSN5001 TOC Tut (CSE1,CSE2)", "CSE",
            ["FAC_SANDEEP_HARIT", "FAC_RAVPREET"], ["SEC_CSE1", "SEC_CSE2"], None, "Tutorial", 1, 1, "Classroom", 2,
            "SIMULTANEOUS_BUNDLE", ["304", "306"], ["304", "306"], False, None,
            [{"day_idx": 0, "start_period": 4, "duration": 1}]
        ),
        (
            "CRS_CSE_CSN5001_TUT_2", "CSN5001", "CSN5001 TOC Tut (CSE3,CSE4)", "CSE",
            ["FAC_SANDEEP_HARIT", "FAC_RAVPREET"], ["SEC_CSE3", "SEC_CSE4"], None, "Tutorial", 1, 1, "Classroom", 2,
            "SIMULTANEOUS_BUNDLE", ["304", "306"], ["304", "306"], False, None,
            [{"day_idx": 0, "start_period": 3, "duration": 1}]
        ),
        (
            "CRS_CSE_CSN5001_TUT_3", "CSN5001", "CSN5001 TOC Tut (CSE5,CSE6)", "CSE",
            ["FAC_SANDEEP_HARIT", "FAC_RAVPREET"], ["SEC_CSE5", "SEC_CSE6"], None, "Tutorial", 1, 1, "Classroom", 2,
            "SIMULTANEOUS_BUNDLE", ["301", "306"], ["301", "306"], False, None,
            [{"day_idx": 1, "start_period": 5, "duration": 1}]
        ),
        (
            "CRS_CSE_CSN5001_TUT_4", "CSN5001", "CSN5001 TOC Tut (CSE7)", "CSE",
            ["FAC_SANDEEP_HARIT", "FAC_RAVPREET"], ["SEC_CSE7"], None, "Tutorial", 1, 1, "Classroom", 1,
            "SINGLE_FROM_ELIGIBLE", ["304"], [], False, None,
            [{"day_idx": 1, "start_period": 6, "duration": 1}]
        ),

        # --- CSE: CSN5002 ---
        (
            "CRS_CSE_CSN5002_G1", "CSN5002", "CSN5002 SC (G1)", "CSE",
            ["FAC_DIPIKA"], [], "GRP_G1", "Lecture", 3, 1, "Lecture Hall", 1,
            "SINGLE_FROM_ELIGIBLE", ["L21", "L407"], [], False, None,
            [{"day_idx": 0, "start_period": 6, "duration": 1}, {"day_idx": 1, "start_period": 4, "duration": 1}, {"day_idx": 4, "start_period": 1, "duration": 1}]
        ),
        (
            "CRS_CSE_CSN5002_G2", "CSN5002", "CSN5002 SC (G2)", "CSE",
            ["FAC_DIPIKA"], [], "GRP_G2", "Lecture", 3, 1, "Lecture Hall", 1,
            "SINGLE_FROM_ELIGIBLE", ["405", "L406", "L22"], [], False, None,
            [{"day_idx": 2, "start_period": 5, "duration": 1}, {"day_idx": 3, "start_period": 3, "duration": 1}, {"day_idx": 3, "start_period": 7, "duration": 1}]
        ),
        (
            "CRS_CSE_CSN5002_LAB_1", "CSN5002", "CSN5002 SC Lab (CSE5,CSE6)", "CSE",
            ["FAC_DIPIKA"], ["SEC_CSE5", "SEC_CSE6"], None, "Practical", 1, 2, "Classroom", 1,
            "SINGLE_FROM_ELIGIBLE", ["305"], [], False, None,
            [{"day_idx": 1, "start_period": 1, "duration": 2}]
        ),
        (
            "CRS_CSE_CSN5002_LAB_2", "CSN5002", "CSN5002 SC Lab (CSE1,CSE2,CSE3,CSE4)", "CSE",
            ["FAC_DIPIKA"], ["SEC_CSE1", "SEC_CSE2", "SEC_CSE3", "SEC_CSE4"], None, "Practical", 1, 2, "Computer Lab", 1,
            "SINGLE_FROM_ELIGIBLE", ["DS lab"], [], False, None,
            [{"day_idx": 2, "start_period": 3, "duration": 2}]
        ),
        (
            "CRS_CSE_CSN5002_LAB_3", "CSN5002", "CSN5002 SC Lab (CSE7)", "CSE",
            ["FAC_DIPIKA"], ["SEC_CSE7"], None, "Practical", 1, 2, "Classroom", 1,
            "SINGLE_FROM_ELIGIBLE", ["301"], [], False, None,
            [{"day_idx": 4, "start_period": 2, "duration": 2}]
        ),

        # --- CSE: CSN5003 ---
        (
            "CRS_CSE_CSN5003_G1", "CSN5003", "CSN5003 SE (G1)", "CSE",
            ["FAC_TEJINDER"], [], "GRP_G1", "Lecture", 3, 1, "Lecture Hall", 1,
            "SINGLE_FROM_ELIGIBLE", ["L21", "L407"], [], False, None,
            [{"day_idx": 0, "start_period": 1, "duration": 1}, {"day_idx": 3, "start_period": 3, "duration": 1}, {"day_idx": 4, "start_period": 5, "duration": 1}]
        ),
        (
            "CRS_CSE_CSN5003_G2", "CSN5003", "CSN5003 SE (G2)", "CSE",
            ["FAC_TEJINDER"], [], "GRP_G2", "Lecture", 3, 1, "Lecture Hall", 1,
            "SINGLE_FROM_ELIGIBLE", ["L22", "L21", "L30"], [], False, None,
            [{"day_idx": 0, "start_period": 2, "duration": 1}, {"day_idx": 1, "start_period": 6, "duration": 1}, {"day_idx": 3, "start_period": 4, "duration": 1}]
        ),
        (
            "CRS_CSE_CSN5003_LAB_1", "CSN5003", "CSN5003 SE Lab (CSE5,CSE6)", "CSE",
            ["FAC_TEJINDER", "FAC_SHIVANI"], ["SEC_CSE5", "SEC_CSE6"], None, "Practical", 1, 2, "Computer Lab", 2,
            "SIMULTANEOUS_BUNDLE", ["CL13", "CL5"], ["CL13", "CL5"], False, None,
            [{"day_idx": 2, "start_period": 2, "duration": 2}]
        ),
        (
            "CRS_CSE_CSN5003_LAB_2", "CSN5003", "CSN5003 SE Lab (CSE3,CSE4)", "CSE",
            ["FAC_TEJINDER", "FAC_SHIVANI"], ["SEC_CSE3", "SEC_CSE4"], None, "Practical", 1, 2, "Classroom", 1,
            "SINGLE_FROM_ELIGIBLE", ["301"], [], False, None,
            [{"day_idx": 3, "start_period": 1, "duration": 2}]
        ),
        (
            "CRS_CSE_CSN5003_LAB_3", "CSN5003", "CSN5003 SE Lab (CSE7)", "CSE",
            ["FAC_TEJINDER", "FAC_SHIVANI"], ["SEC_CSE7"], None, "Practical", 1, 2, "Classroom", 1,
            "SINGLE_FROM_ELIGIBLE", ["306"], [], False, None,
            [{"day_idx": 3, "start_period": 5, "duration": 2}]
        ),
        (
            "CRS_CSE_CSN5003_LAB_4", "CSN5003", "CSN5003 SE Lab (CSE1,CSE2)", "CSE",
            ["FAC_TEJINDER", "FAC_SHIVANI"], ["SEC_CSE1", "SEC_CSE2"], None, "Practical", 1, 2, "Computer Lab", 2,
            "SIMULTANEOUS_BUNDLE", ["303", "CL13"], ["303", "CL13"], False, None,
            [{"day_idx": 4, "start_period": 2, "duration": 2}]
        ),

        # --- CSE: CSN5004 ---
        (
            "CRS_CSE_CSN5004_G1", "CSN5004", "CSN5004 DBMS (G1)", "CSE",
            ["FAC_SHILPA"], [], "GRP_G1", "Lecture", 3, 1, "Lecture Hall", 1,
            "SINGLE_FROM_ELIGIBLE", ["L22", "L407", "407"], [], False, None,
            [{"day_idx": 1, "start_period": 3, "duration": 1}, {"day_idx": 3, "start_period": 4, "duration": 1}, {"day_idx": 4, "start_period": 4, "duration": 1}]
        ),
        (
            "CRS_CSE_CSN5004_G2", "CSN5004", "CSN5004 DBMS (G2)", "CSE",
            ["FAC_SHILPA"], [], "GRP_G2", "Lecture", 3, 1, "Lecture Hall", 1,
            "SINGLE_FROM_ELIGIBLE", ["L22", "L406"], [], False, None,
            [{"day_idx": 0, "start_period": 6, "duration": 1}, {"day_idx": 1, "start_period": 4, "duration": 1}, {"day_idx": 4, "start_period": 1, "duration": 1}]
        ),
        (
            "CRS_CSE_CSN5004_LAB_1", "CSN5004", "CSN5004 DBMS Lab (CSE1,CSE2)", "CSE",
            ["FAC_SHILPA"], ["SEC_CSE1", "SEC_CSE2"], None, "Practical", 1, 2, "Classroom", 2,
            "SIMULTANEOUS_BUNDLE", ["402", "306"], ["402", "306"], False, None,
            [{"day_idx": 2, "start_period": 0, "duration": 2}]
        ),
        (
            "CRS_CSE_CSN5004_LAB_2", "CSN5004", "CSN5004 DBMS Lab (CSE7)", "CSE",
            ["FAC_SHILPA"], ["SEC_CSE7"], None, "Practical", 1, 2, "Computer Lab", 1,
            "SINGLE_FROM_ELIGIBLE", ["CL14"], [], False, None,
            [{"day_idx": 2, "start_period": 2, "duration": 2}]
        ),
        (
            "CRS_CSE_CSN5004_LAB_3", "CSN5004", "CSN5004 DBMS Lab (CSE5,CSE6)", "CSE",
            ["FAC_SHILPA"], ["SEC_CSE5", "SEC_CSE6"], None, "Practical", 1, 2, "Classroom", 2,
            "SIMULTANEOUS_BUNDLE", ["402", "301"], ["402", "301"], False, None,
            [{"day_idx": 3, "start_period": 5, "duration": 2}]
        ),
        (
            "CRS_CSE_CSN5004_LAB_4", "CSN5004", "CSN5004 DBMS Lab (CSE3,CSE4)", "CSE",
            ["FAC_SHILPA"], ["SEC_CSE3", "SEC_CSE4"], None, "Practical", 1, 2, "Classroom", 2,
            "SIMULTANEOUS_BUNDLE", ["402", "L407"], ["402", "L407"], False, None,
            [{"day_idx": 4, "start_period": 2, "duration": 2}]
        ),

        # --- CSE: CSM1003 ---
        (
            "CRS_CSE_CSM1003_LEC", "CSM1003", "MSC L (CSM1003 DBMS)", "CSE",
            ["FAC_PRAVNEET_KAUR"], ["SEC_CSE1", "SEC_CSE2", "SEC_CSE3", "SEC_CSE4", "SEC_CSE5", "SEC_CSE6", "SEC_CSE7"], None, "Lecture", 3, 1, "Lecture Hall", 1,
            "SINGLE_FROM_ELIGIBLE", ["L19", "L22"], [], False, None,
            [{"day_idx": 0, "start_period": 7, "duration": 1}, {"day_idx": 1, "start_period": 7, "duration": 1}, {"day_idx": 2, "start_period": 7, "duration": 1}]
        ),
        (
            "CRS_CSE_CSM1003_LAB", "CSM1003", "MSC Lab (CSM1003 DBMS)", "CSE",
            ["FAC_PRAVNEET_KAUR"], ["SEC_CSE1", "SEC_CSE2", "SEC_CSE3", "SEC_CSE4", "SEC_CSE5", "SEC_CSE6", "SEC_CSE7"], None, "Practical", 1, 2, "Lecture Hall", 1,
            "SINGLE_FROM_ELIGIBLE", ["L22"], [], False, None,
            [{"day_idx": 4, "start_period": 6, "duration": 2}]
        ),

        # --- AI: AIN5001 ---
        (
            "CRS_AI_AIN5001_BACKLOG", "AIN5001", "AIN5001 TOC (L) Backlog", "AI",
            ["FAC_RAVPREET"], ["SEC_AI1", "SEC_AI2"], None, "Lecture", 1, 1, "Lecture Hall", 1,
            "SINGLE_FROM_ELIGIBLE", ["L407"], [], False, "Backlog lecture scheduled in L407.",
            [{"day_idx": 3, "start_period": 0, "duration": 1}]
        ),
        (
            "CRS_AI_AIN5001_LEC", "AIN5001", "AIN5001 TOC (L)", "AI",
            ["FAC_RAVPREET"], ["SEC_AI1", "SEC_AI2"], None, "Lecture", 3, 1, "Lecture Hall", 1,
            "SINGLE_FROM_ELIGIBLE", ["L406", "L21", "L407"], [], False, None,
            [{"day_idx": 0, "start_period": 5, "duration": 1}, {"day_idx": 2, "start_period": 1, "duration": 1}, {"day_idx": 3, "start_period": 1, "duration": 1}]
        ),
        (
            "CRS_AI_AIN5001_TUT", "AIN5001", "AIN5001 TOC Tut (AI1+AI2)", "AI",
            ["FAC_RAVPREET"], ["SEC_AI1", "SEC_AI2"], None, "Tutorial", 1, 1, "Classroom", 1,
            "SINGLE_FROM_ELIGIBLE", ["402"], [], False, None,
            [{"day_idx": 3, "start_period": 3, "duration": 1}]
        ),

        # --- AI: AIN5002 ---
        (
            "CRS_AI_AIN5002_LEC", "AIN5002", "AIN5002 DL", "AI",
            ["FAC_PADMAVATI"], ["SEC_AI1", "SEC_AI2"], None, "Lecture", 3, 1, "Lecture Hall", 1,
            "SINGLE_FROM_ELIGIBLE", ["L406", "L19", "305"], [], False, None,
            [{"day_idx": 0, "start_period": 6, "duration": 1}, {"day_idx": 2, "start_period": 2, "duration": 1}, {"day_idx": 3, "start_period": 4, "duration": 1}]
        ),
        (
            "CRS_AI_AIN5002_LAB_AI2", "AIN5002", "AIN5002 DL Lab (AI2)", "AI",
            ["FAC_PADMAVATI"], ["SEC_AI2"], None, "Practical", 1, 2, "Computer Lab", 1,
            "SINGLE_FROM_ELIGIBLE", ["CL5"], [], False, None,
            [{"day_idx": 0, "start_period": 3, "duration": 2}]
        ),
        (
            "CRS_AI_AIN5002_LAB_AI1", "AIN5002", "AIN5002 DL Lab (AI1)", "AI",
            ["FAC_PADMAVATI"], ["SEC_AI1"], None, "Practical", 1, 2, "Computer Lab", 1,
            "SINGLE_FROM_ELIGIBLE", ["CL13"], [], False, None,
            [{"day_idx": 1, "start_period": 3, "duration": 2}]
        ),

        # --- AI: AIN5003 ---
        (
            "CRS_AI_AIN5003_LEC", "AIN5003", "AIN5003 HMI", "AI",
            ["FAC_ALKA_JINDAL"], ["SEC_AI1", "SEC_AI2"], None, "Lecture", 3, 1, "Lecture Hall", 1,
            "SINGLE_FROM_ELIGIBLE", ["L406", "L407"], [], False, None,
            [{"day_idx": 1, "start_period": 1, "duration": 1}, {"day_idx": 2, "start_period": 3, "duration": 1}, {"day_idx": 4, "start_period": 1, "duration": 1}]
        ),
        (
            "CRS_AI_AIN5003_LAB_AI2", "AIN5003", "AIN5003 HMI Lab (AI2)", "AI",
            ["FAC_ALKA_JINDAL"], ["SEC_AI2"], None, "Practical", 1, 2, "Computer Lab", 1,
            "SINGLE_FROM_ELIGIBLE", ["CL14"], [], False, None,
            [{"day_idx": 1, "start_period": 3, "duration": 2}]
        ),
        (
            "CRS_AI_AIN5003_LAB_AI1", "AIN5003", "AIN5003 HMI Lab (AI1)", "AI",
            ["FAC_ALKA_JINDAL"], ["SEC_AI1"], None, "Practical", 1, 2, "Computer Lab", 1,
            "SINGLE_FROM_ELIGIBLE", ["CL5"], [], False, None,
            [{"day_idx": 4, "start_period": 2, "duration": 2}]
        ),

        # --- AI: AIN5004 ---
        (
            "CRS_AI_AIN5004_LEC", "AIN5004", "AIN5004 CN", "AI",
            ["FAC_DIVYA_BANSAL", "FAC_POOJA"], ["SEC_AI1", "SEC_AI2"], None, "Lecture", 3, 1, "Lecture Hall", 1,
            "SINGLE_FROM_ELIGIBLE", ["L406", "305"], [], False, "Friday lecture designated in Room 305.",
            [{"day_idx": 1, "start_period": 2, "duration": 1}, {"day_idx": 2, "start_period": 4, "duration": 1}, {"day_idx": 4, "start_period": 4, "duration": 1}]
        ),
        (
            "CRS_AI_AIN5004_LAB_AI1", "AIN5004", "AIN5004 CN Lab (AI1)", "AI",
            ["FAC_DIVYA_BANSAL", "FAC_POOJA"], ["SEC_AI1"], None, "Practical", 1, 2, "Computer Lab", 1,
            "SINGLE_FROM_ELIGIBLE", ["CL13"], [], False, None,
            [{"day_idx": 0, "start_period": 3, "duration": 2}]
        ),
        (
            "CRS_AI_AIN5004_LAB_AI2", "AIN5004", "AIN5004 CN Lab (AI2)", "AI",
            ["FAC_DIVYA_BANSAL", "FAC_POOJA"], ["SEC_AI2"], None, "Practical", 1, 2, "Classroom", 1,
            "SINGLE_FROM_ELIGIBLE", ["304"], [], False, None,
            [{"day_idx": 4, "start_period": 2, "duration": 2}]
        ),

        # --- AI: AIM1003 ---
        (
            "CRS_AI_AIM1003_LEC", "AIM1003", "MSC L (AIM1003 HMI)", "AI",
            ["FAC_ALKA_JINDAL"], ["SEC_AI1", "SEC_AI2"], None, "Lecture", 3, 1, "Lecture Hall", 1,
            "SINGLE_FROM_ELIGIBLE", ["L406"], [], False, None,
            [{"day_idx": 0, "start_period": 7, "duration": 1}, {"day_idx": 1, "start_period": 7, "duration": 1}, {"day_idx": 2, "start_period": 7, "duration": 1}]
        ),
        (
            "CRS_AI_AIM1003_LAB", "AIM1003", "MSC Lab (AIM1003 HMI)", "AI",
            ["FAC_ALKA_JINDAL"], ["SEC_AI1", "SEC_AI2"], None, "Practical", 1, 2, "Lecture Hall", 1,
            "SINGLE_FROM_ELIGIBLE", ["L406"], [], False, None,
            [{"day_idx": 4, "start_period": 6, "duration": 2}]
        ),

        # --- DS: DSN5001 ---
        (
            "CRS_DS_DSN5001_LEC", "DSN5001", "DSN5001 DAIR", "DS",
            ["FAC_SURAJ_SRIVASTAVA"], ["SEC_DS1", "SEC_DS2", "SEC_DS3", "SEC_DS4"], None, "Lecture", 3, 1, "Lecture Hall", 1,
            "SINGLE_FROM_ELIGIBLE", ["L405", "407"], [], False, None,
            [{"day_idx": 1, "start_period": 1, "duration": 1}, {"day_idx": 2, "start_period": 2, "duration": 1}, {"day_idx": 3, "start_period": 1, "duration": 1}]
        ),
        (
            "CRS_DS_DSN5001_LAB_DS23", "DSN5001", "DSN5001 DAIR Lab (DS2+DS3)", "DS",
            ["FAC_SURAJ_SRIVASTAVA"], ["SEC_DS2", "SEC_DS3"], None, "Practical", 1, 2, "Computer Lab", 2,
            "SIMULTANEOUS_BUNDLE", ["301", "CL14"], ["301", "CL14"], False, None,
            [{"day_idx": 0, "start_period": 2, "duration": 2}]
        ),
        (
            "CRS_DS_DSN5001_LAB_DS4", "DSN5001", "DSN5001 DAIR Lab (DS4)", "DS",
            ["FAC_SURAJ_SRIVASTAVA"], ["SEC_DS4"], None, "Practical", 1, 2, "Classroom", 1,
            "SINGLE_FROM_ELIGIBLE", ["402"], [], False, None,
            [{"day_idx": 1, "start_period": 3, "duration": 2}]
        ),
        (
            "CRS_DS_DSN5001_LAB_DS1", "DSN5001", "DSN5001 DAIR Lab (DS1)", "DS",
            ["FAC_SURAJ_SRIVASTAVA"], ["SEC_DS1"], None, "Practical", 1, 2, "Classroom", 1,
            "SINGLE_FROM_ELIGIBLE", ["402"], [], False, None,
            [{"day_idx": 2, "start_period": 5, "duration": 2}]
        ),

        # --- DS: DSN5002 ---
        (
            "CRS_DS_DSN5002_LEC", "DSN5002", "DSN5002 ATDS", "DS",
            ["FAC_MANISH_KUMAR"], ["SEC_DS1", "SEC_DS2", "SEC_DS3", "SEC_DS4"], None, "Lecture", 3, 1, "Lecture Hall", 1,
            "SINGLE_FROM_ELIGIBLE", ["L407", "L405"], [], False, None,
            [{"day_idx": 0, "start_period": 6, "duration": 1}, {"day_idx": 3, "start_period": 4, "duration": 1}, {"day_idx": 4, "start_period": 2, "duration": 1}]
        ),
        (
            "CRS_DS_DSN5002_LAB_DS1", "DSN5002", "DSN5002 ATDS Lab (DS1)", "DS",
            ["FAC_MANISH_KUMAR"], ["SEC_DS1"], None, "Practical", 1, 2, "Classroom", 1,
            "SINGLE_FROM_ELIGIBLE", ["402"], [], False, None,
            [{"day_idx": 0, "start_period": 2, "duration": 2}]
        ),
        (
            "CRS_DS_DSN5002_LAB_DS2", "DSN5002", "DSN5002 ATDS Lab (DS2)", "DS",
            ["FAC_MANISH_KUMAR"], ["SEC_DS2"], None, "Practical", 1, 2, "Classroom", 1,
            "SINGLE_FROM_ELIGIBLE", ["301"], [], False, None,
            [{"day_idx": 1, "start_period": 3, "duration": 2}]
        ),
        (
            "CRS_DS_DSN5002_LAB_DS34", "DSN5002", "DSN5002 ATDS Lab (DS3+DS4)", "DS",
            ["FAC_MANISH_KUMAR"], ["SEC_DS3", "SEC_DS4"], None, "Practical", 1, 2, "Classroom", 1,
            "SINGLE_FROM_ELIGIBLE", ["305"], [], False, None,
            [{"day_idx": 2, "start_period": 3, "duration": 2}]
        ),

        # --- DS: DSN5003 ---
        (
            "CRS_DS_DSN5003_LEC", "DSN5003", "DSN5003 SE", "DS",
            ["FAC_RAJESH_BHATIA"], ["SEC_DS1", "SEC_DS2", "SEC_DS3", "SEC_DS4"], None, "Lecture", 2, 1, "Lecture Hall", 1,
            "SINGLE_FROM_ELIGIBLE", ["L405", "L407"], [], False, None,
            [{"day_idx": 1, "start_period": 2, "duration": 1}, {"day_idx": 3, "start_period": 2, "duration": 1}]
        ),
        (
            "CRS_DS_DSN5003_LAB_DS12", "DSN5003", "DSN5003 SE Lab (DS1+DS2)", "DS",
            ["FAC_RAJESH_BHATIA"], ["SEC_DS1", "SEC_DS2"], None, "Practical", 1, 2, "Classroom", 2,
            "SIMULTANEOUS_BUNDLE", ["301", "306"], ["301", "306"], False, None,
            [{"day_idx": 2, "start_period": 3, "duration": 2}]
        ),
        (
            "CRS_DS_DSN5003_LAB_DS34", "DSN5003", "DSN5003 SE Lab (DS3+DS4)", "DS",
            ["FAC_RAJESH_BHATIA"], ["SEC_DS3", "SEC_DS4"], None, "Practical", 1, 2, "Classroom", 2,
            "SIMULTANEOUS_BUNDLE", ["303", "306"], ["303", "306"], False, None,
            [{"day_idx": 2, "start_period": 5, "duration": 2}]
        ),

        # --- DS: DSN5004 ---
        (
            "CRS_DS_DSN5004_LEC", "DSN5004", "DSN5004 IoT", "DS",
            ["FAC_ISHITA"], ["SEC_DS1", "SEC_DS2", "SEC_DS3", "SEC_DS4"], None, "Lecture", 3, 1, "Lecture Hall", 1,
            "SINGLE_FROM_ELIGIBLE", ["L407", "L406"], [], False, None,
            [{"day_idx": 0, "start_period": 4, "duration": 1}, {"day_idx": 1, "start_period": 6, "duration": 1}, {"day_idx": 4, "start_period": 3, "duration": 1}]
        ),
        (
            "CRS_DS_DSN5004_LAB", "DSN5004", "DSN5004 IoT Lab (DS1+DS2+DS3+DS4)", "DS",
            ["FAC_SANEHI"], ["SEC_DS1", "SEC_DS2", "SEC_DS3", "SEC_DS4"], None, "Practical", 1, 2, "Computer Lab", 3,
            "SIMULTANEOUS_BUNDLE", ["305", "CL13", "CL14"], ["305", "CL13", "CL14"], False, None,
            [{"day_idx": 3, "start_period": 5, "duration": 2}]
        ),

        # --- DS: DSM1003 ---
        (
            "CRS_DS_DSM1003_LEC", "DSM1003", "MSC L (DSM1003 ATDS)", "DS",
            ["FAC_MANISH_KUMAR"], ["SEC_DS1", "SEC_DS2", "SEC_DS3", "SEC_DS4"], None, "Lecture", 3, 1, "Lecture Hall", 1,
            "SINGLE_FROM_ELIGIBLE", ["L407"], [], False, None,
            [{"day_idx": 0, "start_period": 7, "duration": 1}, {"day_idx": 1, "start_period": 7, "duration": 1}, {"day_idx": 2, "start_period": 7, "duration": 1}]
        ),
        (
            "CRS_DS_DSM1003_LAB", "DSM1003", "MSC Lab (DSM1003 ATDS)", "DS",
            ["FAC_MANISH_KUMAR"], ["SEC_DS1", "SEC_DS2", "SEC_DS3", "SEC_DS4"], None, "Practical", 1, 2, "Lecture Hall", 1,
            "SINGLE_FROM_ELIGIBLE", ["L407"], [], False, None,
            [{"day_idx": 4, "start_period": 6, "duration": 2}]
        ),
    ]

    total_sessions = sum(c[8] for c in courses)
    print(f"Generated {len(courses)} course offerings with total {total_sessions} weekly session events.")

    py_lines = [
        '"""',
        'Preconfigured 5th Semester Institutional Dataset for UniScheduler Demo.',
        'Audited and corrected against timetables.md (CSE Core, CSE AI, CSE Data Science).',
        'Excluded all no-venue project/honours sessions.',
        'Supports CourseGroup (G1, G2), multiple co-instructors, and distinct room allocation modes.',
        '"""',
        '',
        'from typing import List',
        'from .models import Section, CourseGroup, Faculty, Room, Course, TimeSlotConfig, TimetableData, Period, ImportSummary',
        '',
        '',
        'def build_default_availability(num_days: int = 5, num_periods: int = 8, unavail_slots=None) -> List[List[bool]]:',
        '    """Returns a 2D boolean grid (days x periods). True = Available, False = Unavailable."""',
        '    grid = [[True for _ in range(num_periods)] for _ in range(num_days)]',
        '    if unavail_slots:',
        '        for day, period in unavail_slots:',
        '            if 0 <= day < num_days and 0 <= period < num_periods:',
        '                grid[day][period] = False',
        '    return grid',
        '',
        '',
        'def get_sample_dataset() -> TimetableData:',
        '    num_days = 5',
        '    num_periods = 8',
        '',
        '    # 1. Actual Student Sections (13 distinct practical batches)',
        '    sections = ['
    ]

    for sid, sname, dept, sem, div_type, start, end, strength, notes in sections:
        py_lines.append(f'        Section(id="{sid}", name="{sname}", department="{dept}", semester_year="{sem}", division_type="{div_type}", sid_start={start}, sid_end={end}, strength={strength}, is_group=False, notes="{notes}"),')

    py_lines.extend([
        '    ]',
        '',
        '    # 2. Course Groups (Separate CourseGroup entities for lecture divisions defined by SID ranges)',
        '    course_groups = ['
    ])

    for gid, gname, dept, div_type, start, end, strength, notes in course_groups:
        py_lines.append(f'        CourseGroup(id="{gid}", name="{gname}", department="{dept}", division_type="{div_type}", sid_start={start}, sid_end={end}, strength={strength}, is_verified=True, notes="{notes}"),')

    py_lines.extend([
        '    ]',
        '',
        '    # 3. Faculty Members (16 actual identities, zero unused TBA guides)',
        '    faculty = ['
    ])

    for fid, fname, dept, desig, is_shared, notes in faculty:
        notes_repr = f'"{notes}"' if notes else 'None'
        py_lines.append(f'        Faculty(id="{fid}", name="{fname}", department="{dept}", designation="{desig}", availability=build_default_availability(num_days, num_periods), is_shared={is_shared}, notes={notes_repr}),')

    py_lines.extend([
        '    ]',
        '',
        '    # 4. Instructional Venues (20 distinct venues, unknown capacity marked unverified)',
        '    rooms = ['
    ])

    for rid, rname, rtype in venues:
        py_lines.append(f'        Room(id="{rid}", name="{rname}", room_type="{rtype}", capacity=None, availability=build_default_availability(num_days, num_periods), notes="Capacity unverified in source timetable."),')

    py_lines.extend([
        '    ]',
        '',
        '    # 5. Course Offerings (54 venue-backed offerings, exactly 91 weekly sessions)',
        '    courses = ['
    ])

    for (cid, code, name, dept, fac_ids, sec_ids, grp_id, stype, spw, dur, rtype, rooms_req, alloc_mode, elig_rooms, bundle_rooms, needs_review, rev_reason, targets) in courses:
        grp_repr = f'"{grp_id}"' if grp_id else 'None'
        rev_repr = f'"{rev_reason}"' if rev_reason else 'None'
        primary_fac = fac_ids[0] if fac_ids else ""
        all_rooms = bundle_rooms if alloc_mode == "SIMULTANEOUS_BUNDLE" else elig_rooms

        py_lines.append(f'        Course(')
        py_lines.append(f'            id="{cid}",')
        py_lines.append(f'            code="{code}",')
        py_lines.append(f'            name="{name}",')
        py_lines.append(f'            department="{dept}",')
        py_lines.append(f'            faculty_ids={json.dumps(fac_ids)},')
        py_lines.append(f'            faculty_id="{primary_fac}",')
        py_lines.append(f'            section_ids={json.dumps(sec_ids)},')
        py_lines.append(f'            group_id={grp_repr},')
        py_lines.append(f'            session_type="{stype}",')
        py_lines.append(f'            sessions_per_week={spw},')
        py_lines.append(f'            duration={dur},')
        py_lines.append(f'            required_room_type="{rtype}",')
        py_lines.append(f'            rooms_required={rooms_req},')
        py_lines.append(f'            allocation_mode="{alloc_mode}",')
        py_lines.append(f'            eligible_room_ids={json.dumps(elig_rooms)},')
        py_lines.append(f'            required_room_bundle_ids={json.dumps(bundle_rooms)},')
        py_lines.append(f'            designated_rooms={json.dumps(all_rooms)},')
        py_lines.append(f'            needs_review={needs_review},')
        py_lines.append(f'            review_reason={rev_repr},')
        py_lines.append(f'            target_slots={json.dumps(targets)},')
        py_lines.append(f'        ),')

    py_lines.extend([
        '    ]',
        '',
        '    # 6. Time Slot Configuration (8 periods + Lunch Break)',
        '    config = TimeSlotConfig(',
        '        days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],',
        '        periods=[',
        '            Period(index=0, name="Period 1", start_time="08:00", end_time="09:00"),',
        '            Period(index=1, name="Period 2", start_time="09:00", end_time="10:00"),',
        '            Period(index=2, name="Period 3", start_time="10:00", end_time="11:00"),',
        '            Period(index=3, name="Period 4", start_time="11:00", end_time="12:00"),',
        '            Period(index=4, name="Period 5", start_time="12:00", end_time="13:00"),',
        '            Period(index=5, name="Period 6", start_time="14:00", end_time="15:00"),',
        '            Period(index=6, name="Period 7", start_time="15:00", end_time="16:00"),',
        '            Period(index=7, name="Period 8", start_time="16:00", end_time="17:00"),',
        '        ],',
        '        break_after_period=[4],  # Lunch 13:00 - 14:00',
        '    )',
        '',
        '    # 7. Data Import Summary',
        '    import_summary = ImportSummary(',
        '        source_name="5th Semester Timetables (CSE, AI, DS)",',
        '        unique_course_codes=18,',
        f'        total_offerings={len(courses)},',
        f'        total_session_events={total_sessions},',
        '        total_faculty=16,',
        '        total_sections=13,',
        '        total_course_groups=2,',
        '        total_venues=20,',
        '        removed_no_venue_offerings=[',
        '            "CSP5101 — Minor Project (2 sessions)",',
        '            "DSP5101 — Minor Project (4 sessions)",',
        '            "DSH1001 — Honours Project-I (3 sessions)",',
        '            "AIP5101 — Minor Project (4 sessions)",',
        '            "AIH1001 — Honours Project-I (2 sessions)",',
        '            "DSN_INCOMPLETE — Unspecified Course (1 session)"',
        '        ],',
        '        unverified_notes=[',
        '            "CSE: 138 distinct students (G1: SID 1–69, G2: SID 70–138; Practical batches CSE1–CSE7)",',
        '            "AI: 30 distinct students (AI Shared: SID 1–30; Practical batches AI1–AI2)",',
        '            "DS: 60 distinct students (DS Shared: SID 1–60; Practical batches DS1–DS4)",',
        '            "Room capacities not specified in institutional source timetable (all marked unverified)",',
        '            "Shivani faculty identity has title/spelling variants in source (Dr. / Ms. / Shivani)"',
        '        ],',
        '    )',
        '',
        '    return TimetableData(',
        '        sections=sections,',
        '        course_groups=course_groups,',
        '        faculty=faculty,',
        '        rooms=rooms,',
        '        courses=courses,',
        '        config=config,',
        '        import_summary=import_summary,',
        '    )',
        ''
    ])

    import os
    output_path = os.path.join(os.path.dirname(__file__), "sample_data.py")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(py_lines))

    print(f"Successfully generated {output_path} with {len(courses)} offerings and {total_sessions} weekly sessions.")

if __name__ == "__main__":
    generate_sample_data_py()
