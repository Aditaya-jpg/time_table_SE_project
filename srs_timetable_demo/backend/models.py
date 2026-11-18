"""
Data Models for the College Timetable Scheduling Demo
Uses Pydantic for validation and serialization.
Audited and corrected for exact 5th Semester Institutional Timetable Data.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Section(BaseModel):
    """Represents an actual student cohort (e.g. CSE1-CSE7, DS1-DS4, AI1-AI2)."""
    id: str
    name: str  # e.g., "CSE1", "DS1", "AI1"
    department: str  # "CSE", "AI", "DS"
    semester_year: str = "5th Semester"
    strength: int = 60  # Number of students
    is_group: bool = False
    notes: Optional[str] = None


class CourseGroup(BaseModel):
    """
    Represents an unstated curriculum course group (e.g. G1, G2 in CSE).
    Memberships can be configured by an administrator; marked unverified until configured.
    """
    id: str  # e.g., "GRP_G1", "GRP_G2"
    name: str  # "G1", "G2"
    department: str = "CSE"
    section_ids: List[str] = Field(default_factory=list)  # Mapped section IDs e.g. ["SEC_CSE1", ...]
    is_verified: bool = False  # True once mapped by administrator
    notes: Optional[str] = None


class Faculty(BaseModel):
    id: str
    name: str  # e.g., "Dr. Ravpreet", "Dr. Rajesh Bhatia"
    department: str  # "CSE", "AI", "DS", "CSE/AI - Shared", "COMMON"
    designation: str = "Professor"
    # availability[day_idx][slot_idx] = True if available, False if unavailable
    availability: List[List[bool]] = Field(default_factory=list)
    is_shared: bool = False  # e.g., Dr. Ravpreet shared across CSE & AI
    notes: Optional[str] = None  # e.g., Title/spelling verification note for Shivani


class Room(BaseModel):
    id: str  # e.g., "301", "L407", "CL13", "DS lab"
    name: str  # e.g., "Room 301", "Lecture Hall L407", "Computer Lab CL13"
    room_type: str = "Classroom"  # "Classroom", "Computer Lab", "Lecture Hall"
    capacity: Optional[int] = None  # Unknown/Unverified if None or <= 0
    # availability[day_idx][slot_idx] = True if available, False if unavailable
    availability: List[List[bool]] = Field(default_factory=list)
    notes: Optional[str] = None


class Course(BaseModel):
    id: str
    code: str  # e.g., "DSN5001", "CSN5004", "AIN5001"
    name: str  # e.g., "DSN5001 DAIR", "CSN5004 DBMS"
    department: str  # "CSE", "AI", "DS"
    faculty_ids: List[str] = Field(default_factory=list)  # Primary multi-instructor list
    faculty_id: Optional[str] = None  # Backward-compatibility convenience
    section_ids: List[str] = Field(default_factory=list)  # Direct section references
    group_id: Optional[str] = None  # CourseGroup reference (e.g. "GRP_G1", "GRP_G2")
    session_type: str = "Lecture"  # "Lecture", "Tutorial", "Practical"
    sessions_per_week: int = 1  # Occurrence count per week
    duration: int = 1  # Number of consecutive time slots (e.g. 1 or 2)
    required_room_type: str = "Classroom"
    rooms_required: int = 1  # Number of rooms required
    allocation_mode: str = "SINGLE_FROM_ELIGIBLE"  # "SINGLE_FROM_ELIGIBLE" or "SIMULTANEOUS_BUNDLE"
    eligible_room_ids: List[str] = Field(default_factory=list)  # Alternative venue choices (pick exactly 1)
    required_room_bundle_ids: List[str] = Field(default_factory=list)  # Fixed multi-room bundle for simultaneous allocation
    designated_rooms: List[str] = Field(default_factory=list)  # Backward compat alias
    needs_review: bool = False  # Incomplete or unverified offering
    review_reason: Optional[str] = None  # Reason why it needs review
    target_slots: List[Dict[str, Any]] = Field(default_factory=list)  # Source day/period references


class Period(BaseModel):
    index: int
    name: str  # e.g., "Period 1"
    start_time: str  # e.g., "08:00"
    end_time: str  # e.g., "09:00"
    is_break: bool = False


class TimeSlotConfig(BaseModel):
    days: List[str] = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    periods: List[Period] = [
        Period(index=0, name="Period 1", start_time="08:00", end_time="09:00"),
        Period(index=1, name="Period 2", start_time="09:00", end_time="10:00"),
        Period(index=2, name="Period 3", start_time="10:00", end_time="11:00"),
        Period(index=3, name="Period 4", start_time="11:00", end_time="12:00"),
        Period(index=4, name="Period 5", start_time="12:00", end_time="13:00"),
        Period(index=5, name="Period 6", start_time="14:00", end_time="15:00"),
        Period(index=6, name="Period 7", start_time="15:00", end_time="16:00"),
        Period(index=7, name="Period 8", start_time="16:00", end_time="17:00"),
    ]
    # Lunch break is 13:00 - 14:00, between Period 5 (index 4) and Period 6 (index 5)
    break_after_period: List[int] = [4]


class TimetableEntry(BaseModel):
    event_id: str
    course_id: str
    course_code: str
    course_name: str
    department: str
    session_type: str
    session_index: int
    faculty_ids: List[str] = Field(default_factory=list)
    faculty_names: List[str] = Field(default_factory=list)
    faculty_id: str = ""  # Display string / primary
    faculty_name: str = ""  # Display string / primary
    section_ids: List[str] = Field(default_factory=list)
    section_names: List[str] = Field(default_factory=list)
    group_id: Optional[str] = None
    group_name: Optional[str] = None
    day_index: int
    day_name: str
    start_period: int
    end_period: int  # exclusive
    duration: int
    allocation_mode: str = "SINGLE_FROM_ELIGIBLE"
    room_ids: List[str] = Field(default_factory=list)
    room_names: List[str] = Field(default_factory=list)
    total_room_capacity: Optional[int] = None
    total_student_strength: int = 0
    needs_review: bool = False
    review_reason: Optional[str] = None


class ValidationReport(BaseModel):
    overall_status: str = "VALIDATED WITH WARNINGS"  # "FULLY VALIDATED", "VALIDATED WITH WARNINGS", "INFEASIBLE"
    is_valid: bool = True
    faculty_conflicts: int = 0
    section_conflicts: int = 0
    room_conflicts: int = 0
    availability_violations: int = 0
    capacity_violations: int = 0
    room_type_violations: int = 0
    duration_violations: int = 0
    multi_room_violations: int = 0
    faculty_status: str = "Passed"
    section_status: str = "Unverified — G1/G2 mapping pending"
    room_status: str = "Passed"
    capacity_status: str = "Unverified — capacities not defined in source"
    duration_status: str = "Passed"
    unverified_constraints: List[str] = Field(default_factory=list)
    details: List[str] = Field(default_factory=list)


class SolverResult(BaseModel):
    status: str  # "OPTIMAL", "FEASIBLE", "INFEASIBLE", "UNKNOWN"
    solve_time_seconds: float = 0.0
    total_events: int = 0
    scheduled_events: List[TimetableEntry] = Field(default_factory=list)
    diagnostics: List[str] = Field(default_factory=list)
    validation: ValidationReport = Field(default_factory=ValidationReport)


class ImportSummary(BaseModel):
    source_name: str = "5th Semester Timetables (CSE, AI, DS)"
    unique_course_codes: int = 18
    total_offerings: int = 54
    total_session_events: int = 91
    total_faculty: int = 16
    total_sections: int = 13
    total_course_groups: int = 2
    total_venues: int = 20
    removed_no_venue_offerings: List[str] = Field(default_factory=list)
    unverified_notes: List[str] = Field(default_factory=list)


class TimetableData(BaseModel):
    sections: List[Section] = Field(default_factory=list)
    course_groups: List[CourseGroup] = Field(default_factory=list)
    faculty: List[Faculty] = Field(default_factory=list)
    rooms: List[Room] = Field(default_factory=list)
    courses: List[Course] = Field(default_factory=list)
    config: TimeSlotConfig = Field(default_factory=TimeSlotConfig)
    last_solution: Optional[SolverResult] = None
    import_summary: Optional[ImportSummary] = None
