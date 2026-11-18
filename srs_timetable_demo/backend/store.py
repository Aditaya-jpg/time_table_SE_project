"""
In-Memory Store for Timetable Data with Persistence and CRUD operations.
Supports Sections, CourseGroups, Faculty, Rooms, Courses, and Configurations.
"""

import json
import os
from typing import Optional, List
from .models import Section, CourseGroup, Faculty, Room, Course, TimeSlotConfig, TimetableData, SolverResult
from .sample_data import get_sample_dataset

DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), "current_data.json")


class DataStore:
    def __init__(self):
        self._data: TimetableData = get_sample_dataset()
        self._load_from_disk()

    def _save_to_disk(self):
        try:
            with open(DATA_FILE_PATH, "w", encoding="utf-8") as f:
                f.write(self._data.model_dump_json(indent=2))
        except Exception as e:
            print(f"[DataStore] Warning: Could not save to disk: {e}")

    def _load_from_disk(self):
        if os.path.exists(DATA_FILE_PATH):
            try:
                with open(DATA_FILE_PATH, "r", encoding="utf-8") as f:
                    content = f.read()
                    if content.strip():
                        loaded = TimetableData.model_validate_json(content)
                        # Check if loaded data has the new 54 offerings / course groups structure
                        if loaded.course_groups and len(loaded.courses) == 54:
                            self._data = loaded
                            return
            except Exception as e:
                print(f"[DataStore] Warning: Could not load cached disk data: {e}")
        self._data = get_sample_dataset()
        self._save_to_disk()

    def get_data(self) -> TimetableData:
        return self._data

    def load_sample_dataset(self) -> TimetableData:
        self._data = get_sample_dataset()
        self._save_to_disk()
        return self._data

    def reset_data(self) -> TimetableData:
        self._data = TimetableData(
            sections=[],
            course_groups=[],
            faculty=[],
            rooms=[],
            courses=[],
            config=self._data.config,
            last_solution=None,
        )
        self._save_to_disk()
        return self._data

    # --- Course Group Management ---
    def get_course_groups(self) -> List[CourseGroup]:
        return self._data.course_groups

    def update_course_group_mapping(self, group_id: str, section_ids: List[str]) -> Optional[CourseGroup]:
        for grp in self._data.course_groups:
            if grp.id == group_id:
                grp.section_ids = section_ids
                grp.is_verified = len(section_ids) > 0
                self._data.last_solution = None
                self._save_to_disk()
                return grp
        return None

    # --- Section CRUD ---
    def add_section(self, section: Section) -> Section:
        self._data.sections = [s for s in self._data.sections if s.id != section.id]
        self._data.sections.append(section)
        self._data.last_solution = None
        self._save_to_disk()
        return section

    def update_section(self, section_id: str, section: Section) -> Optional[Section]:
        for i, s in enumerate(self._data.sections):
            if s.id == section_id:
                section.id = section_id
                self._data.sections[i] = section
                self._data.last_solution = None
                self._save_to_disk()
                return section
        return None

    def delete_section(self, section_id: str) -> bool:
        initial_len = len(self._data.sections)
        self._data.sections = [s for s in self._data.sections if s.id != section_id]
        # Remove from course references
        for course in self._data.courses:
            course.section_ids = [sid for sid in course.section_ids if sid != section_id]
        # Remove from course group references
        for grp in self._data.course_groups:
            grp.section_ids = [sid for sid in grp.section_ids if sid != section_id]
        self._data.last_solution = None
        self._save_to_disk()
        return len(self._data.sections) < initial_len

    # --- Faculty CRUD ---
    def add_faculty(self, faculty: Faculty) -> Faculty:
        num_days = len(self._data.config.days)
        num_periods = len(self._data.config.periods)
        if not faculty.availability:
            faculty.availability = [[True for _ in range(num_periods)] for _ in range(num_days)]
        self._data.faculty = [f for f in self._data.faculty if f.id != faculty.id]
        self._data.faculty.append(faculty)
        self._data.last_solution = None
        self._save_to_disk()
        return faculty

    def update_faculty(self, faculty_id: str, faculty: Faculty) -> Optional[Faculty]:
        for i, f in enumerate(self._data.faculty):
            if f.id == faculty_id:
                faculty.id = faculty_id
                self._data.faculty[i] = faculty
                self._data.last_solution = None
                self._save_to_disk()
                return faculty
        return None

    def delete_faculty(self, faculty_id: str) -> bool:
        initial_len = len(self._data.faculty)
        self._data.faculty = [f for f in self._data.faculty if f.id != faculty_id]
        self._data.last_solution = None
        self._save_to_disk()
        return len(self._data.faculty) < initial_len

    # --- Room CRUD ---
    def add_room(self, room: Room) -> Room:
        num_days = len(self._data.config.days)
        num_periods = len(self._data.config.periods)
        if not room.availability:
            room.availability = [[True for _ in range(num_periods)] for _ in range(num_days)]
        self._data.rooms = [r for r in self._data.rooms if r.id != room.id]
        self._data.rooms.append(room)
        self._data.last_solution = None
        self._save_to_disk()
        return room

    def update_room(self, room_id: str, room: Room) -> Optional[Room]:
        for i, r in enumerate(self._data.rooms):
            if r.id == room_id:
                room.id = room_id
                self._data.rooms[i] = room
                self._data.last_solution = None
                self._save_to_disk()
                return room
        return None

    def delete_room(self, room_id: str) -> bool:
        initial_len = len(self._data.rooms)
        self._data.rooms = [r for r in self._data.rooms if r.id != room_id]
        self._data.last_solution = None
        self._save_to_disk()
        return len(self._data.rooms) < initial_len

    # --- Course CRUD ---
    def add_course(self, course: Course) -> Course:
        self._data.courses = [c for c in self._data.courses if c.id != course.id]
        self._data.courses.append(course)
        self._data.last_solution = None
        self._save_to_disk()
        return course

    def update_course(self, course_id: str, course: Course) -> Optional[Course]:
        for i, c in enumerate(self._data.courses):
            if c.id == course_id:
                course.id = course_id
                self._data.courses[i] = course
                self._data.last_solution = None
                self._save_to_disk()
                return course
        return None

    def delete_course(self, course_id: str) -> bool:
        initial_len = len(self._data.courses)
        self._data.courses = [c for c in self._data.courses if c.id != course_id]
        self._data.last_solution = None
        self._save_to_disk()
        return len(self._data.courses) < initial_len

    # --- Config ---
    def update_config(self, config: TimeSlotConfig) -> TimeSlotConfig:
        self._data.config = config
        self._data.last_solution = None
        self._save_to_disk()
        return config

    # --- Solution ---
    def set_solution(self, solution: SolverResult):
        self._data.last_solution = solution
        self._save_to_disk()


store = DataStore()
