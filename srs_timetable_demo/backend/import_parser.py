"""
Parser for timetables.md
Extracts courses, sections, faculty, venues, session frequencies, durations, and flags incomplete records.
"""

import re
import os
from typing import Dict, List, Any, Optional

SOURCE_FILE = r"c:\Users\Lenovo\Downloads\timetables.md"


def parse_timetables_md(file_path: str = SOURCE_FILE):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Source file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    tables = re.split(r"##\s+", text)[1:]
    days_order = ["MON", "TUES", "WED", "THURS", "FRI"]
    period_map = [(1, 0), (2, 1), (3, 2), (4, 3), (5, 4), (7, 5), (8, 6), (9, 7)]

    raw_merged_events = []

    for t in tables:
        lines = t.strip().split("\n")
        prog_title = lines[0].strip()
        dept = "DS" if "Data Science" in prog_title else ("AI" if "(AI)" in prog_title else "CSE")

        for l in lines[4:]:
            if not l.strip() or not l.startswith("|"):
                continue
            cells = [c.strip() for c in l.split("|")[1:-1]]
            day = cells[0].replace("*", "").strip()

            period_items = {}
            for col_idx, p_idx in period_map:
                cell = cells[col_idx]
                if cell in ("—", "–", "-", "LUNCH", ""):
                    period_items[p_idx] = []
                else:
                    period_items[p_idx] = [s.strip() for s in cell.split("<br>") if s.strip()]

            visited = {p: [False] * len(period_items[p]) for p in range(8)}

            for p in range(8):
                for idx, item in enumerate(period_items[p]):
                    if visited[p][idx]:
                        continue
                    visited[p][idx] = True

                    dur = 1
                    curr_p = p
                    while curr_p < 7 and curr_p != 4:  # Cannot cross lunch break (p=4 is 12:00-13:00, p=5 is 14:00-15:00)
                        next_p = curr_p + 1
                        found_next = False
                        for next_idx, next_item in enumerate(period_items[next_p]):
                            if not visited[next_p][next_idx] and next_item == item:
                                visited[next_p][next_idx] = True
                                found_next = True
                                break
                        if found_next:
                            dur += 1
                            curr_p = next_p
                        else:
                            break

                    raw_merged_events.append({
                        "dept": dept,
                        "day": day,
                        "start_period": p,
                        "duration": dur,
                        "raw_text": item,
                    })

    return raw_merged_events


if __name__ == "__main__":
    events = parse_timetables_md()
    print(f"Total merged occurrences: {len(events)}")
    for i, e in enumerate(events[:25]):
        print(f"[{i+1}] {e['dept']} | {e['day']} Period {e['start_period']+1} (Duration: {e['duration']}): {e['raw_text']}")
