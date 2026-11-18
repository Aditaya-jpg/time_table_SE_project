"""
Independent Timetable Validator
Post-solve validator completely decoupled from CP-SAT.
Scans the generated schedule and raw input database to independently verify all hard constraints.
Distinguishes passed, violated, and unverified constraints.
"""

from typing import List, Dict, Set, Tuple
from .models import (
    TimetableData,
    TimetableEntry,
    ValidationReport,
    Course,
    CourseGroup,
    Faculty,
    Room,
    Section,
)


def validate_timetable(data: TimetableData, scheduled: List[TimetableEntry]) -> ValidationReport:
    """
    Independently inspects every scheduled event and pair of events against raw constraints.
    Returns an exhaustive ValidationReport separating verified checks from unverified assumptions.
    """
    report = ValidationReport()
    details: List[str] = []
    unverified: List[str] = []

    faculty_dict = {f.id: f for f in data.faculty}
    room_dict = {r.id: r for r in data.rooms}
    section_dict = {s.id: s for s in data.sections}
    group_dict = {g.id: g for g in data.course_groups}
    course_dict = {c.id: c for c in data.courses}
    breaks = data.config.break_after_period

    # Helper: Check time overlap between two events
    def events_overlap(e1: TimetableEntry, e2: TimetableEntry) -> bool:
        if e1.day_index != e2.day_index:
            return False
        # Overlap if max(start1, start2) < min(end1, end2)
        return max(e1.start_period, e2.start_period) < min(e1.end_period, e2.end_period)

    # 1. Pairwise Resource Clashes
    num_events = len(scheduled)
    for i in range(num_events):
        e1 = scheduled[i]
        for j in range(i + 1, num_events):
            e2 = scheduled[j]

            if not events_overlap(e1, e2):
                continue

            # A. Faculty Conflict: Support co-instructors
            e1_facs = set(e1.faculty_ids) if e1.faculty_ids else ({e1.faculty_id} if e1.faculty_id else set())
            e2_facs = set(e2.faculty_ids) if e2.faculty_ids else ({e2.faculty_id} if e2.faculty_id else set())
            shared_faculty = e1_facs.intersection(e2_facs)
            shared_faculty = {fid for fid in shared_faculty if fid not in ("FAC_TBA", "TBA", "")}

            if shared_faculty:
                report.faculty_conflicts += 1
                fac_names = [faculty_dict[fid].name for fid in shared_faculty if fid in faculty_dict]
                details.append(
                    f"Faculty Conflict: Instructor(s) {', '.join(fac_names)} double-booked on {e1.day_name} between {e1.course_code} ({e1.start_period}-{e1.end_period}) and {e2.course_code} ({e2.start_period}-{e2.end_period})."
                )

            # B. Section Conflict: Shared student sections / groups
            shared_sections = set(e1.section_ids).intersection(set(e2.section_ids))
            if shared_sections:
                shared_names = [
                    section_dict[s].name if s in section_dict else (group_dict[s].name if s in group_dict else s)
                    for s in shared_sections
                ]
                report.section_conflicts += 1
                details.append(
                    f"Section Conflict: Cohort(s) {', '.join(shared_names)} double-booked on {e1.day_name} between {e1.course_code} and {e2.course_code}."
                )

            # C. Room / Laboratory Conflict: Shared venue in overlapping periods
            shared_rooms = set(e1.room_ids).intersection(set(e2.room_ids))
            if shared_rooms:
                room_names = [room_dict[r].name for r in shared_rooms if r in room_dict]
                report.room_conflicts += 1
                details.append(
                    f"Room Conflict: Venue(s) {', '.join(room_names)} double-booked on {e1.day_name} between {e1.course_code} and {e2.course_code}."
                )

    # 2. Check G1/G2 CourseGroup mapping verification
    unmapped_groups = [g.name for g in data.course_groups if not g.is_verified or not g.section_ids]
    if unmapped_groups:
        unverified.append(
            f"Student Section Conflicts: Unverified — Course group(s) {', '.join(unmapped_groups)} have pending section mapping."
        )
        report.section_status = "Unverified — G1/G2 mapping pending"
    else:
        report.section_status = "Passed (G1/G2 Mapped)"

    # 3. Individual Event Constraint Checks
    for e in scheduled:
        course = course_dict.get(e.course_id)

        # Duration & Break Integrity
        if e.end_period - e.start_period != e.duration:
            report.duration_violations += 1
            details.append(
                f"Duration Violation: {e.course_code} Session {e.session_index} allocated {e.end_period - e.start_period} periods instead of required {e.duration}."
            )

        crosses_break = any(e.start_period <= b < e.end_period - 1 for b in breaks)
        if crosses_break:
            report.duration_violations += 1
            details.append(
                f"Break Violation: {e.course_code} on {e.day_name} crosses lunch break between periods {e.start_period} and {e.end_period}."
            )

        # Faculty Availability Check (all assigned instructors)
        fac_ids = e.faculty_ids if e.faculty_ids else ([e.faculty_id] if e.faculty_id else [])
        for fid in fac_ids:
            fac = faculty_dict.get(fid)
            if fac and fac.availability:
                for p in range(e.start_period, e.end_period):
                    if e.day_index < len(fac.availability) and p < len(fac.availability[e.day_index]):
                        if not fac.availability[e.day_index][p]:
                            report.availability_violations += 1
                            details.append(
                                f"Faculty Availability Violation: {fac.name} is unavailable on {e.day_name} Period {p + 1}, but scheduled for {e.course_code}."
                            )

        # Room Allocation Verification
        if course:
            if course.allocation_mode == "SIMULTANEOUS_BUNDLE":
                expected_bundle = set(course.required_room_bundle_ids or course.eligible_room_ids)
                if set(e.room_ids) != expected_bundle:
                    report.multi_room_violations += 1
                    details.append(
                        f"Multi-Room Allocation Violation: {e.course_code} requires simultaneous bundle {expected_bundle}, but received {set(e.room_ids)}."
                    )
            else:
                expected_count = course.rooms_required or 1
                if len(e.room_ids) != expected_count:
                    report.multi_room_violations += 1
                    details.append(
                        f"Room Count Violation: {e.course_code} requires {expected_count} room(s), but received {len(e.room_ids)}."
                    )
                if course.eligible_room_ids and not set(e.room_ids).issubset(set(course.eligible_room_ids)):
                    report.room_type_violations += 1
                    details.append(
                        f"Eligible Room Violation: {e.course_code} allocated room {e.room_ids} outside eligible set {course.eligible_room_ids}."
                    )

        # Room Capacity Check (Check for unverified vs violated)
        has_unknown_cap = False
        tot_cap = 0
        for rid in e.room_ids:
            rm = room_dict.get(rid)
            if rm:
                if rm.capacity is None or rm.capacity <= 0:
                    has_unknown_cap = True
                else:
                    tot_cap += rm.capacity

        if has_unknown_cap:
            note = f"Room Capacities: Unverified — venue(s) {', '.join(e.room_ids)} for {e.course_code} have unknown seating capacities in source data."
            if note not in unverified:
                unverified.append(note)
        elif e.total_student_strength > 0 and tot_cap < e.total_student_strength:
            report.capacity_violations += 1
            details.append(
                f"Capacity Violation: {e.course_code} has {e.total_student_strength} students, but assigned room(s) seat {tot_cap}."
            )

    # 4. Status Consolidation
    report.faculty_status = "Passed" if (report.faculty_conflicts == 0 and report.availability_violations == 0) else "Violated"
    report.room_status = "Passed" if (report.room_conflicts == 0 and report.room_type_violations == 0 and report.multi_room_violations == 0) else "Violated"
    report.duration_status = "Passed" if report.duration_violations == 0 else "Violated"

    any_capacity_unverified = any("Room Capacities: Unverified" in u for u in unverified)
    if any_capacity_unverified:
        report.capacity_status = "Unverified — capacities not defined in source"
    else:
        report.capacity_status = "Passed" if report.capacity_violations == 0 else "Violated"

    total_violations = (
        report.faculty_conflicts
        + report.section_conflicts
        + report.room_conflicts
        + report.availability_violations
        + report.capacity_violations
        + report.room_type_violations
        + report.duration_violations
        + report.multi_room_violations
    )

    report.is_valid = (total_violations == 0)
    report.details = details
    report.unverified_constraints = unverified

    if total_violations > 0:
        report.overall_status = "INFEASIBLE"
    elif unverified:
        report.overall_status = "VALIDATED WITH WARNINGS"
    else:
        report.overall_status = "FULLY VALIDATED"

    return report
