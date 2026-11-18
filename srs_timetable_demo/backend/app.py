"""
FastAPI Server for College Timetable Scheduling Demo
Exposes REST endpoints for CRUD, CP-SAT generation, validation, and CSV export.
Mounts the frontend static application.
"""

import io
import csv
import os
from typing import List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse

from .models import (
    Section,
    Faculty,
    Room,
    Course,
    CourseGroup,
    TimeSlotConfig,
    TimetableData,
    SolverResult,
)
from .store import store
from .solver import solve_timetable
from .validator import validate_timetable

app = FastAPI(
    title="College Timetable Scheduling Demo",
    description="Minimal SRS-Based Academic Timetabling Application using Google OR-Tools CP-SAT",
    version="1.0.0",
)

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/data", response_model=TimetableData)
def get_all_data():
    """Retrieve the entire current database and active timetable solution."""
    return store.get_data()


@app.post("/api/sample-data", response_model=TimetableData)
def load_sample_data():
    """Reset and load the standard college sample dataset."""
    return store.load_sample_dataset()


@app.post("/api/reset-data", response_model=TimetableData)
def reset_data():
    """Clear all scheduling inputs and current solution."""
    return store.reset_data()


# --- SECTION CRUD ---
@app.post("/api/sections", response_model=Section)
def add_section(section: Section):
    return store.add_section(section)


@app.put("/api/sections/{section_id}", response_model=Section)
def update_section(section_id: str, section: Section):
    updated = store.update_section(section_id, section)
    if not updated:
        raise HTTPException(status_code=404, detail="Section not found")
    return updated


@app.delete("/api/sections/{section_id}")
def delete_section(section_id: str):
    if not store.delete_section(section_id):
        raise HTTPException(status_code=404, detail="Section not found")
    return {"success": True, "deleted_id": section_id}


# --- FACULTY CRUD ---
@app.post("/api/faculty", response_model=Faculty)
def add_faculty(faculty: Faculty):
    return store.add_faculty(faculty)


@app.put("/api/faculty/{faculty_id}", response_model=Faculty)
def update_faculty(faculty_id: str, faculty: Faculty):
    updated = store.update_faculty(faculty_id, faculty)
    if not updated:
        raise HTTPException(status_code=404, detail="Faculty not found")
    return updated


@app.delete("/api/faculty/{faculty_id}")
def delete_faculty(faculty_id: str):
    if not store.delete_faculty(faculty_id):
        raise HTTPException(status_code=404, detail="Faculty not found")
    return {"success": True, "deleted_id": faculty_id}


# --- ROOM CRUD ---
@app.post("/api/rooms", response_model=Room)
def add_room(room: Room):
    return store.add_room(room)


@app.put("/api/rooms/{room_id}", response_model=Room)
def update_room(room_id: str, room: Room):
    updated = store.update_room(room_id, room)
    if not updated:
        raise HTTPException(status_code=404, detail="Room not found")
    return updated


@app.delete("/api/rooms/{room_id}")
def delete_room(room_id: str):
    if not store.delete_room(room_id):
        raise HTTPException(status_code=404, detail="Room not found")
    return {"success": True, "deleted_id": room_id}


# --- COURSE CRUD ---
@app.post("/api/courses", response_model=Course)
def add_course(course: Course):
    return store.add_course(course)


@app.put("/api/courses/{course_id}", response_model=Course)
def update_course(course_id: str, course: Course):
    updated = store.update_course(course_id, course)
    if not updated:
        raise HTTPException(status_code=404, detail="Course not found")
    return updated


@app.delete("/api/courses/{course_id}")
def delete_course(course_id: str):
    if not store.delete_course(course_id):
        raise HTTPException(status_code=404, detail="Course not found")
    return {"success": True, "deleted_id": course_id}


# --- COURSE GROUP (G1 / G2) MAPPING ---
class GroupMappingRequest(BaseModel):
    section_ids: List[str]


@app.get("/api/groups", response_model=List[CourseGroup])
def get_course_groups():
    """Retrieve all CourseGroup definitions (e.g. G1, G2) and current section mappings."""
    return store.get_course_groups()


@app.put("/api/groups/{group_id}/mapping", response_model=CourseGroup)
def update_group_mapping(group_id: str, req: GroupMappingRequest):
    """Update section mapping for a CourseGroup (e.g. assigning CSE sections to G1/G2)."""
    updated = store.update_course_group_mapping(group_id, req.section_ids)
    if not updated:
        raise HTTPException(status_code=404, detail="CourseGroup not found")
    return updated


# --- CONFIG ---
@app.post("/api/config", response_model=TimeSlotConfig)
def update_config(config: TimeSlotConfig):
    return store.update_config(config)


# --- GENERATE & SOLVE ---
@app.post("/api/generate", response_model=SolverResult)
def generate_timetable():
    """
    Executes Google OR-Tools CP-SAT solver on current inputs.
    Followed by independent post-solve validation.
    """
    data = store.get_data()
    # 1. Run CP-SAT solver
    solution = solve_timetable(data)

    # 2. Run independent validator if a solution exists
    if solution.status in ("OPTIMAL", "FEASIBLE") and solution.scheduled_events:
        validation_report = validate_timetable(data, solution.scheduled_events)
        solution.validation = validation_report
        # If validator catches violations (should not happen with correct CP-SAT), mark invalid
        if not validation_report.is_valid:
            solution.diagnostics.append(
                f"Independent validation failed with {len(validation_report.details)} violation(s)."
            )

    store.set_solution(solution)
    return solution


@app.get("/api/solution", response_model=Optional[SolverResult])
def get_current_solution():
    """Returns the most recent timetable solution."""
    return store.get_data().last_solution


@app.get("/api/export-csv")
def export_csv():
    """Generates and streams a CSV of the current generated timetable."""
    data = store.get_data()
    if not data.last_solution or not data.last_solution.scheduled_events:
        raise HTTPException(status_code=400, detail="No generated timetable available to export.")

    # Create course id -> department lookup
    dept_map = {c.id: c.department for c in data.courses}

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Day",
        "Start Time",
        "End Time",
        "Course Code",
        "Course Name",
        "Department",
        "Session Type",
        "Session Index",
        "Faculty / Co-Instructors",
        "Section / Group",
        "Room Allocation Mode",
        "Room(s)",
        "Room Capacity",
        "Student Strength",
    ])

    for entry in data.last_solution.scheduled_events:
        start_t = data.config.periods[entry.start_period].start_time
        end_t = data.config.periods[entry.end_period - 1].end_time
        faculty_display = ", ".join(entry.faculty_names) if entry.faculty_names else (entry.faculty_name or "N/A")
        target_display = entry.group_name if entry.group_name else ("; ".join(entry.section_names) if entry.section_names else "N/A")
        alloc_mode = getattr(entry, "allocation_mode", "SINGLE_FROM_ELIGIBLE") or "SINGLE_FROM_ELIGIBLE"
        c_dept = dept_map.get(entry.course_id, "CSE")

        writer.writerow([
            entry.day_name,
            start_t,
            end_t,
            entry.course_code,
            entry.course_name,
            c_dept,
            entry.session_type,
            f"Session {entry.session_index}",
            faculty_display,
            target_display,
            alloc_mode,
            "; ".join(entry.room_names),
            entry.total_room_capacity,
            entry.total_student_strength,
        ])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=college_timetable.csv"},
    )


# --- FRONTEND STATIC MOUNT ---
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
if os.path.isdir(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

    @app.get("/")
    def serve_index():
        return FileResponse(os.path.join(frontend_path, "index.html"))
