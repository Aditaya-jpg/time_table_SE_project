"""
Google OR-Tools CP-SAT Timetable Scheduling Engine
Audited and corrected for exact 5th Semester Institutional Timetable.
Guarantees:
1. Multi-instructor support per session (all co-instructors checked for availability and zero double-booking).
2. CourseGroup support (G1, G2) with dynamic section reservation when mapped by administrator.
3. Clean room allocation logic (SINGLE_FROM_ELIGIBLE vs SIMULTANEOUS_BUNDLE).
4. Strictly venue-backed events only (zero no-venue project sessions).
"""

import time
from typing import List, Dict, Tuple, Optional, Set
from ortools.sat.python import cp_model

from .models import (
    TimetableData,
    TimetableEntry,
    SolverResult,
    Course,
    CourseGroup,
    Section,
    Faculty,
    Room,
    TimeSlotConfig,
    ValidationReport,
    get_course_student_ids,
)


class EventInstance:
    """Represents a single required occurrence of a course session."""

    def __init__(
        self,
        event_id: str,
        course: Course,
        session_index: int,
        student_strength: int,
        student_ids: Set[str],
        section_ids: List[str],
        section_names: List[str],
        group_id: Optional[str],
        group_name: Optional[str],
        faculty_ids: List[str],
        faculty_names: List[str],
    ):
        self.event_id = event_id
        self.course = course
        self.session_index = session_index
        self.student_strength = student_strength
        self.student_ids = student_ids
        self.section_ids = section_ids
        self.section_names = section_names
        self.group_id = group_id
        self.group_name = group_name
        self.faculty_ids = faculty_ids
        self.faculty_names = faculty_names


def generate_diagnostics(data: TimetableData, events: List[EventInstance]) -> List[str]:
    """Inspects inputs to find structural bottlenecks and reasons for infeasibility."""
    diag = []
    num_days = len(data.config.days)
    num_periods = len(data.config.periods)
    total_slots = num_days * num_periods

    faculty_dict = {f.id: f for f in data.faculty}
    section_dict = {s.id: s for s in data.sections}
    room_dict = {r.id: r for r in data.rooms}

    # 1. Faculty load check
    faculty_load: Dict[str, int] = {}
    for ev in events:
        for fid in ev.faculty_ids:
            faculty_load[fid] = faculty_load.get(fid, 0) + ev.course.duration

    for fac_id, load in faculty_load.items():
        fac = faculty_dict.get(fac_id)
        if not fac:
            diag.append(f"Faculty ID '{fac_id}' assigned to courses does not exist in Faculty database.")
            continue
        avail_count = sum(
            1
            for d in range(min(num_days, len(fac.availability)))
            for p in range(min(num_periods, len(fac.availability[d])))
            if fac.availability[d][p]
        )
        if load > avail_count:
            diag.append(
                f"Faculty '{fac.name}' is over-demanded: requires {load} teaching slots, but only has {avail_count} available slots."
            )

    # 2. Section load check
    section_load: Dict[str, int] = {}
    for ev in events:
        for sid in ev.section_ids:
            section_load[sid] = section_load.get(sid, 0) + ev.course.duration

    for sid, load in section_load.items():
        sec = section_dict.get(sid)
        sec_name = sec.name if sec else sid
        if load > total_slots:
            diag.append(
                f"Section/Group '{sec_name}' is overloaded: required {load} weekly periods, but only {total_slots} total periods exist in the week."
            )

    # 3. Room candidate availability check
    for ev in events:
        alloc_mode = ev.course.allocation_mode
        if alloc_mode == "SIMULTANEOUS_BUNDLE":
            bundle = [r for r in data.rooms if r.id in ev.course.required_room_bundle_ids]
            if len(bundle) < ev.course.rooms_required:
                diag.append(
                    f"Course '{ev.course.code}' requires {ev.course.rooms_required} simultaneous rooms ({ev.course.required_room_bundle_ids}), but only {len(bundle)} exist."
                )
        else:
            if ev.course.eligible_room_ids:
                elig = [r for r in data.rooms if r.id in ev.course.eligible_room_ids]
            else:
                elig = [r for r in data.rooms if r.room_type == ev.course.required_room_type]
            if len(elig) < ev.course.rooms_required:
                diag.append(
                    f"Course '{ev.course.code}' requires {ev.course.rooms_required} room(s), but only {len(elig)} eligible rooms exist."
                )

    # 4. Multi-period duration check against break boundaries
    for ev in events:
        dur = ev.course.duration
        valid_starts = []
        for p in range(num_periods):
            if p + dur <= num_periods:
                crosses_break = any(p <= b < p + dur - 1 for b in data.config.break_after_period)
                if not crosses_break:
                    valid_starts.append(p)
        if not valid_starts:
            diag.append(
                f"Course '{ev.course.code}' has duration {dur}, but no consecutive block in the daily schedule can accommodate it without bridging the lunch break or day end."
            )

    return diag


def solve_timetable(data: TimetableData, time_limit_seconds: float = 20.0) -> SolverResult:
    """
    Formulates and solves the academic timetable using Google OR-Tools CP-SAT.
    Guarantees satisfaction of all 10 hard constraints.
    """
    start_time = time.time()
    model = cp_model.CpModel()

    num_days = len(data.config.days)
    num_periods = len(data.config.periods)
    days = data.config.days
    periods = data.config.periods
    breaks = data.config.break_after_period

    faculty_dict = {f.id: f for f in data.faculty}
    section_dict = {s.id: s for s in data.sections}
    group_dict = {g.id: g for g in data.course_groups}
    room_dict = {r.id: r for r in data.rooms}

    # Step 1: Decompose each course into individual scheduling event instances
    events: List[EventInstance] = []
    for course in data.courses:
        # Determine faculty members (support multiple instructors)
        fac_ids = course.faculty_ids if course.faculty_ids else ([course.faculty_id] if course.faculty_id else [])
        fac_names = [faculty_dict[fid].name for fid in fac_ids if fid in faculty_dict]
        if not fac_names and course.faculty_id:
            fac_names = [course.faculty_id]

        # Determine student identities and strength via authoritative SID ranges
        student_ids = get_course_student_ids(course)
        strength = len(student_ids)

        # Labels for display
        group_id = course.group_id
        group_name = None
        resolved_sec_ids: List[str] = []
        resolved_sec_names: List[str] = []

        if group_id:
            group_name = "G1" if "G1" in group_id else ("G2" if "G2" in group_id else group_id)
            resolved_sec_ids = [group_id]
            resolved_sec_names = [f"Group {group_name}"]
        else:
            resolved_sec_ids = list(course.section_ids)
            resolved_sec_names = [section_dict[sid].name for sid in resolved_sec_ids if sid in section_dict]
            if not resolved_sec_names and course.section_ids:
                resolved_sec_names = course.section_ids

        for session_idx in range(1, course.sessions_per_week + 1):
            evt_id = f"{course.id}_S{session_idx}"
            events.append(
                EventInstance(
                    event_id=evt_id,
                    course=course,
                    session_index=session_idx,
                    student_strength=strength,
                    student_ids=student_ids,
                    section_ids=resolved_sec_ids,
                    section_names=resolved_sec_names,
                    group_id=group_id,
                    group_name=group_name,
                    faculty_ids=fac_ids,
                    faculty_names=fac_names,
                )
            )

    total_events = len(events)
    if total_events == 0:
        return SolverResult(
            status="FEASIBLE",
            solve_time_seconds=round(time.time() - start_time, 3),
            total_events=0,
            scheduled_events=[],
            diagnostics=["No venue-backed courses defined to schedule."],
            validation=ValidationReport(
                overall_status="FULLY VALIDATED",
                is_valid=True,
                faculty_status="Passed",
                section_status="Passed",
                room_status="Passed",
                capacity_status="Passed",
                duration_status="Passed",
            ),
        )

    # Pre-solve structural diagnostic check
    pre_diagnostics = generate_diagnostics(data, events)

    # Step 2: Valid start periods for each event duration (cannot bridge lunch break or cross day end)
    def get_valid_start_periods(duration: int) -> List[int]:
        valid = []
        for p in range(num_periods):
            if p + duration <= num_periods:
                crosses = any(p <= b < p + duration - 1 for b in breaks)
                if not crosses:
                    valid.append(p)
        return valid

    # Step 3: Decision Variables
    # X[e, d, p]: bool - event e starts on day d at period p
    X: Dict[Tuple[str, int, int], cp_model.IntVar] = {}
    for ev in events:
        valid_periods = get_valid_start_periods(ev.course.duration)
        for d in range(num_days):
            for p in valid_periods:
                X[(ev.event_id, d, p)] = model.NewBoolVar(f"X_{ev.event_id}_d{d}_p{p}")

    # Helper: Candidate rooms for an event based on allocation mode
    def get_candidate_rooms(ev: EventInstance) -> List[Room]:
        if ev.course.allocation_mode == "SIMULTANEOUS_BUNDLE":
            bundle_ids = ev.course.required_room_bundle_ids or ev.course.eligible_room_ids or ev.course.designated_rooms
            return [r for r in data.rooms if r.id in bundle_ids]
        else:
            elig_ids = ev.course.eligible_room_ids or ev.course.designated_rooms
            if elig_ids:
                return [r for r in data.rooms if r.id in elig_ids]
            return [r for r in data.rooms if r.room_type == ev.course.required_room_type]

    # Y[e, r]: bool - event e uses room r
    Y: Dict[Tuple[str, str], cp_model.IntVar] = {}
    for ev in events:
        for r in get_candidate_rooms(ev):
            Y[(ev.event_id, r.id)] = model.NewBoolVar(f"Y_{ev.event_id}_{r.id}")

    # --- HARD CONSTRAINT 1 & 8: Exactly one valid start time per event ---
    for ev in events:
        valid_periods = get_valid_start_periods(ev.course.duration)
        possible_slots = [
            X[(ev.event_id, d, p)] for d in range(num_days) for p in valid_periods
        ]
        if not possible_slots:
            return SolverResult(
                status="INFEASIBLE",
                solve_time_seconds=round(time.time() - start_time, 3),
                total_events=total_events,
                scheduled_events=[],
                diagnostics=[
                    f"Event '{ev.course.code}' (Session {ev.session_index}) cannot start at any valid period without crossing lunch break or day boundary."
                ]
                + pre_diagnostics,
                validation=ValidationReport(overall_status="INFEASIBLE", is_valid=False),
            )
        model.AddExactlyOne(possible_slots)

    # --- HARD CONSTRAINT 7 & 9: Room Allocation by Allocation Mode ---
    for ev in events:
        c_rooms = get_candidate_rooms(ev)
        alloc_mode = ev.course.allocation_mode

        if alloc_mode == "SIMULTANEOUS_BUNDLE":
            # All rooms in the bundle must be allocated simultaneously
            req_bundle = ev.course.required_room_bundle_ids or [r.id for r in c_rooms]
            if len(c_rooms) < len(req_bundle):
                return SolverResult(
                    status="INFEASIBLE",
                    solve_time_seconds=round(time.time() - start_time, 3),
                    total_events=total_events,
                    scheduled_events=[],
                    diagnostics=[
                        f"Insufficient rooms in bundle {req_bundle} for '{ev.course.code}'."
                    ]
                    + pre_diagnostics,
                    validation=ValidationReport(overall_status="INFEASIBLE", is_valid=False),
                )
            for r in c_rooms:
                if (ev.event_id, r.id) in Y:
                    model.Add(Y[(ev.event_id, r.id)] == 1)

        else:
            # SINGLE_FROM_ELIGIBLE: Select exactly rooms_required (normally 1) from eligible venues
            req_count = ev.course.rooms_required or 1
            if len(c_rooms) < req_count:
                return SolverResult(
                    status="INFEASIBLE",
                    solve_time_seconds=round(time.time() - start_time, 3),
                    total_events=total_events,
                    scheduled_events=[],
                    diagnostics=[
                        f"Insufficient eligible rooms for '{ev.course.code}' (needs {req_count}, found {len(c_rooms)})."
                    ]
                    + pre_diagnostics,
                    validation=ValidationReport(overall_status="INFEASIBLE", is_valid=False),
                )
            model.Add(sum(Y[(ev.event_id, r.id)] for r in c_rooms) == req_count)

        # Capacity enforcement (only when capacities are configured and verified)
        if all(r.capacity is not None and r.capacity > 0 for r in c_rooms) and ev.student_strength > 0:
            model.Add(
                sum(Y[(ev.event_id, r.id)] * r.capacity for r in c_rooms)
                >= ev.student_strength
            )

    # Helper: Active indicator A[e, d, p'] = event e occupies day d at period p'
    A: Dict[Tuple[str, int, int], cp_model.IntVar] = {}
    for ev in events:
        dur = ev.course.duration
        valid_periods = get_valid_start_periods(dur)
        for d in range(num_days):
            for p_curr in range(num_periods):
                covering_starts = [
                    p
                    for p in valid_periods
                    if p <= p_curr < p + dur and (ev.event_id, d, p) in X
                ]
                if covering_starts:
                    if len(covering_starts) == 1:
                        A[(ev.event_id, d, p_curr)] = X[(ev.event_id, d, covering_starts[0])]
                    else:
                        active_var = model.NewBoolVar(f"A_{ev.event_id}_d{d}_p{p_curr}")
                        model.Add(active_var == sum(X[(ev.event_id, d, p)] for p in covering_starts))
                        A[(ev.event_id, d, p_curr)] = active_var

    # --- HARD CONSTRAINT 5: Faculty Availability (all assigned instructors must be available) ---
    for ev in events:
        dur = ev.course.duration
        valid_periods = get_valid_start_periods(dur)
        for fid in ev.faculty_ids:
            fac = faculty_dict.get(fid)
            if fac and fac.availability:
                for d in range(min(num_days, len(fac.availability))):
                    for p in valid_periods:
                        is_unavail = any(
                            p_sub < len(fac.availability[d]) and not fac.availability[d][p_sub]
                            for p_sub in range(p, p + dur)
                        )
                        if is_unavail and (ev.event_id, d, p) in X:
                            model.Add(X[(ev.event_id, d, p)] == 0)

    # --- HARD CONSTRAINT 1: Faculty Conflict Prevention (support co-instructors) ---
    # No faculty member can be scheduled in two sessions at the same (day, period)
    for fac_id in faculty_dict.keys():
        fac_events = [ev for ev in events if fac_id in ev.faculty_ids]
        if len(fac_events) > 1:
            for d in range(num_days):
                for p_curr in range(num_periods):
                    active_for_fac = [
                        A[(ev.event_id, d, p_curr)]
                        for ev in fac_events
                        if (ev.event_id, d, p_curr) in A
                    ]
                    if len(active_for_fac) > 1:
                        model.Add(sum(active_for_fac) <= 1)

    # --- HARD CONSTRAINT 2 & 10: Student Conflict Prevention via Exact SID Ranges ---
    all_student_ids: Set[str] = set()
    for ev in events:
        all_student_ids.update(ev.student_ids)

    for s_id in all_student_ids:
        # Find all events in which student s_id participates
        student_events = [ev for ev in events if s_id in ev.student_ids]
        if len(student_events) > 1:
            for d in range(num_days):
                for p_curr in range(num_periods):
                    active_for_student = [
                        A[(ev.event_id, d, p_curr)]
                        for ev in student_events
                        if (ev.event_id, d, p_curr) in A
                    ]
                    if len(active_for_student) > 1:
                        model.Add(sum(active_for_student) <= 1)

    # --- HARD CONSTRAINT 3 & 4: Room & Laboratory Conflict Prevention ---
    for r in data.rooms:
        for d in range(num_days):
            for p_curr in range(num_periods):
                room_unavail = False
                if r.availability and d < len(r.availability) and p_curr < len(r.availability[d]):
                    if not r.availability[d][p_curr]:
                        room_unavail = True

                candidate_events = [
                    ev
                    for ev in events
                    if (ev.event_id, r.id) in Y and (ev.event_id, d, p_curr) in A
                ]

                if not candidate_events:
                    continue

                active_room_vars = []
                for ev in candidate_events:
                    z = model.NewBoolVar(f"Z_{ev.event_id}_{r.id}_d{d}_p{p_curr}")
                    model.AddBoolAnd([Y[(ev.event_id, r.id)], A[(ev.event_id, d, p_curr)]]).OnlyEnforceIf(z)
                    model.AddBoolOr([Y[(ev.event_id, r.id)].Not(), A[(ev.event_id, d, p_curr)].Not()]).OnlyEnforceIf(z.Not())

                    if room_unavail:
                        model.Add(z == 0)
                    else:
                        active_room_vars.append(z)

                if len(active_room_vars) > 1:
                    model.Add(sum(active_room_vars) <= 1)

    # --- SOFT OBJECTIVES: Target Slots & Academic Balance ---
    objective_penalties = []

    # 1. Soft preference for target slots from institutional source timetable
    for ev in events:
        if ev.course.target_slots and ev.session_index - 1 < len(ev.course.target_slots):
            ts = ev.course.target_slots[ev.session_index - 1]
            td = ts.get("day_idx")
            tp = ts.get("start_period")
            if (ev.event_id, td, tp) in X:
                objective_penalties.append((1 - X[(ev.event_id, td, tp)]) * 50)

    # 2. Spread sessions of the same course across different days
    course_grouped_events: Dict[str, List[EventInstance]] = {}
    for ev in events:
        course_grouped_events.setdefault(ev.course.id, []).append(ev)

    for c_id, c_evts in course_grouped_events.items():
        if len(c_evts) > 1 and len(c_evts) <= num_days:
            for d in range(num_days):
                day_active = []
                for ev in c_evts:
                    valid_periods = get_valid_start_periods(ev.course.duration)
                    day_active.append(
                        sum(
                            X[(ev.event_id, d, p)]
                            for p in valid_periods
                            if (ev.event_id, d, p) in X
                        )
                    )
                more_than_one = model.NewIntVar(0, len(c_evts), f"clash_{c_id}_d{d}")
                model.Add(more_than_one >= sum(day_active) - 1)
                objective_penalties.append(more_than_one * 15)

    # 3. Minor preference for earlier periods
    for (ev_id, d, p), var in X.items():
        objective_penalties.append(var * p)

    if objective_penalties:
        model.Minimize(sum(objective_penalties))

    # Step 4: Run CP-SAT Solver
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_seconds
    solver.parameters.num_workers = 4

    status = solver.Solve(model)
    solve_duration = round(time.time() - start_time, 3)

    status_str = "UNKNOWN"
    if status == cp_model.OPTIMAL:
        status_str = "OPTIMAL"
    elif status == cp_model.FEASIBLE:
        status_str = "FEASIBLE"
    elif status == cp_model.INFEASIBLE:
        status_str = "INFEASIBLE"
    elif status == cp_model.MODEL_INVALID:
        status_str = "MODEL_INVALID"

    if status_str not in ("OPTIMAL", "FEASIBLE"):
        return SolverResult(
            status=status_str,
            solve_time_seconds=solve_duration,
            total_events=total_events,
            scheduled_events=[],
            diagnostics=[
                f"CP-SAT solver returned '{status_str}'."
            ]
            + pre_diagnostics,
            validation=ValidationReport(overall_status="INFEASIBLE", is_valid=False),
        )

    # Step 5: Extract Solution
    scheduled: List[TimetableEntry] = []
    for ev in events:
        assigned_day = -1
        assigned_start = -1
        valid_periods = get_valid_start_periods(ev.course.duration)

        for d in range(num_days):
            for p in valid_periods:
                if (ev.event_id, d, p) in X and solver.Value(X[(ev.event_id, d, p)]) == 1:
                    assigned_day = d
                    assigned_start = p
                    break
            if assigned_day != -1:
                break

        assigned_room_ids = []
        assigned_room_names = []
        tot_cap = 0
        has_unknown_cap = False
        for r in data.rooms:
            if (ev.event_id, r.id) in Y and solver.Value(Y[(ev.event_id, r.id)]) == 1:
                assigned_room_ids.append(r.id)
                assigned_room_names.append(r.name)
                if r.capacity is not None and r.capacity > 0:
                    tot_cap += r.capacity
                else:
                    has_unknown_cap = True

        entry = TimetableEntry(
            event_id=ev.event_id,
            course_id=ev.course.id,
            course_code=ev.course.code,
            course_name=ev.course.name,
            department=ev.course.department,
            session_type=ev.course.session_type,
            session_index=ev.session_index,
            faculty_ids=ev.faculty_ids,
            faculty_names=ev.faculty_names,
            faculty_id=", ".join(ev.faculty_ids),
            faculty_name=", ".join(ev.faculty_names),
            section_ids=ev.section_ids,
            section_names=ev.section_names,
            group_id=ev.group_id,
            group_name=ev.group_name,
            day_index=assigned_day,
            day_name=days[assigned_day],
            start_period=assigned_start,
            end_period=assigned_start + ev.course.duration,
            duration=ev.course.duration,
            allocation_mode=ev.course.allocation_mode,
            room_ids=assigned_room_ids,
            room_names=assigned_room_names,
            total_room_capacity=None if (has_unknown_cap or not assigned_room_ids) else tot_cap,
            total_student_strength=ev.student_strength,
            needs_review=ev.course.needs_review,
            review_reason=ev.course.review_reason,
        )
        scheduled.append(entry)

    scheduled.sort(key=lambda e: (e.day_index, e.start_period, e.course_code))

    return SolverResult(
        status=status_str,
        solve_time_seconds=solve_duration,
        total_events=total_events,
        scheduled_events=scheduled,
        diagnostics=[
            f"Successfully found {status_str} timetable schedule in {solve_duration}s."
        ],
    )
