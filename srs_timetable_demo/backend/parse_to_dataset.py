"""
Parse timetables.md into exact Course Offerings, Sections, Faculty, and Rooms.
Generates the comprehensive 5th semester dataset.
"""

import re
import json
from collections import defaultdict

SOURCE_FILE = r"c:\Users\Lenovo\Downloads\timetables.md"

with open(SOURCE_FILE, "r", encoding="utf-8") as f:
    text = f.read()

tables = re.split(r"##\s+", text)[1:]
period_map = [(1, 0), (2, 1), (3, 2), (4, 3), (5, 4), (7, 5), (8, 6), (9, 7)]
day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
day_short_map = {"MON": 0, "TUES": 1, "WED": 2, "THURS": 3, "FRI": 4}

raw_events = []

for t in tables:
    lines = t.strip().split("\n")
    prog_title = lines[0].strip()
    dept = "DS" if "Data Science" in prog_title else ("AI" if "(AI)" in prog_title else "CSE")
    
    for l in lines[4:]:
        if not l.strip() or not l.startswith("|"):
            continue
        cells = [c.strip() for c in l.split("|")[1:-1]]
        day_raw = cells[0].replace("*", "").strip()
        day_idx = day_short_map.get(day_raw, 0)
        
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
                while curr_p < 7 and curr_p != 4:
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
                        
                raw_events.append({
                    "dept": dept,
                    "day_idx": day_idx,
                    "day_name": day_names[day_idx],
                    "start_period": p,
                    "duration": dur,
                    "raw_text": item,
                })

print(f"Total raw merged events: {len(raw_events)}")

# Course codes known:
# DSN5001, DSN5002, DSN5003, DSN5004, DSP5101, DSH1001, DSM1003
# CSN5001, CSN5002, CSN5003, CSN5004, CSP5101, CSM1003
# AIN5001, AIN5002, AIN5003, AIN5004, AIP5101, AIH1001, AIM1003

# Venues:
# 301, 303, 304, 305, 306, 402, 405, 407, L19, L21, L22, L26, L30, L405, L406, L407, CL5, CL13, CL14, DS lab

# Let's inspect parsing of each raw_event
parsed_events = []
for ev in raw_events:
    raw = ev["raw_text"]
    dept = ev["dept"]
    
    # Check incomplete records
    if raw == "– Dr. Rajesh Bhatia":
        parsed_events.append({
            "code": "DSN_INCOMPLETE",
            "name": "Unspecified Course",
            "session_type": "Lecture",
            "faculty": "Dr. Rajesh Bhatia",
            "faculty_id": "FAC_RAJESH_BHATIA",
            "sections": ["DS_ALL"],
            "section_ids": ["SEC_DS1", "SEC_DS2", "SEC_DS3", "SEC_DS4"],
            "rooms": [],
            "rooms_required": 1,
            "room_type": "Classroom",
            "duration": ev["duration"],
            "dept": dept,
            "needs_review": True,
            "review_reason": "Friday 12:00-13:00 incomplete entry in source timetable: course code and room missing.",
            "target": {"day_idx": ev["day_idx"], "start_period": ev["start_period"], "duration": ev["duration"]}
        })
        continue

    # AI Friday 12:00-13:00: AIN5004 CN – Dr. Divya Bansal + Pooja #305
    if "AIN5004 CN – Dr. Divya Bansal + Pooja #305" in raw:
        parsed_events.append({
            "code": "AIN5004",
            "name": "AIN5004 CN",
            "session_type": "Lecture",
            "faculty": "Dr. Divya Bansal + Pooja",
            "faculty_id": "FAC_DIVYA_POOJA",
            "sections": ["AI_ALL"],
            "section_ids": ["SEC_AI1", "SEC_AI2"],
            "rooms": ["305"],
            "rooms_required": 1,
            "room_type": "Classroom",
            "duration": ev["duration"],
            "dept": dept,
            "needs_review": True,
            "review_reason": "Friday 12:00-13:00 entry has '#305' room designation and unstated student section.",
            "target": {"day_idx": ev["day_idx"], "start_period": ev["start_period"], "duration": ev["duration"]}
        })
        continue

    # Projects / Honours
    # DSP5101 - Minor Project
    # CSP5101 - Minor Project
    # AIP5101 - Minor Project
    # DSH1001 - Honours Project-I
    # AIH1001 - Honours Project-I
    if "Minor Project" in raw or "Honours Project" in raw:
        code_match = re.search(r"(DSP5101|CSP5101|AIP5101|DSH1001|AIH1001)", raw)
        code = code_match.group(1) if code_match else "PROJECT"
        name = raw.strip()
        stype = "Project"
        
        # Sections
        if dept == "DS":
            sec_ids = ["SEC_DS1", "SEC_DS2", "SEC_DS3", "SEC_DS4"]
        elif dept == "AI":
            sec_ids = ["SEC_AI1", "SEC_AI2"]
        else:
            sec_ids = [f"SEC_CSE{i}" for i in range(1, 8)]
            
        parsed_events.append({
            "code": code,
            "name": name,
            "session_type": stype,
            "faculty": "TBA / Self-Directed",
            "faculty_id": "FAC_TBA",
            "sections": [s.replace("SEC_", "") for s in sec_ids],
            "section_ids": sec_ids,
            "rooms": [],
            "rooms_required": 0,
            "room_type": "Classroom",
            "duration": ev["duration"],
            "dept": dept,
            "needs_review": True,
            "review_reason": "Self-directed project / honours session without assigned room or faculty in source timetable.",
            "target": {"day_idx": ev["day_idx"], "start_period": ev["start_period"], "duration": ev["duration"]}
        })
        continue

    # Regular course entries
    # Examples:
    # DSN5001 DAIR Lab (DS2+DS3) 301+CL14 – Dr. Suraj Srivastava
    # MSC L (DSM1003 ATDS – Dr. Manish Kumar) L407
    # CSN5001 TOC Tut (CSE3,CSE4) 304+306 – Dr. Sandeep Harit + Dr. Ravpreet
    # CSN5003 SE Lab (CSE5,CSE6) CL13+CL5 – Dr. Shivani/Dr. Tejinder
    # AIN5001 TOC (L) L407 backlog – Dr. Ravpreet
    # AIN5001 TOC Tut AI1+AI2, 402 – Dr. Ravpreet
    
    # Extract code
    code_match = re.search(r"(DSN\d+|DSP\d+|DSH\d+|DSM\d+|CSN\d+|CSP\d+|CSH\d+|CSM\d+|AIN\d+|AIP\d+|AIH\d+|AIM\d+)", raw)
    code = code_match.group(1) if code_match else "UNKNOWN"
    
    # Extract faculty (after dash / en-dash / em-dash)
    parts = re.split(r"–|—|-", raw)
    faculty = ""
    # In some strings like "MSC L (DSM1003 ATDS – Dr. Manish Kumar) L407", dash is inside brackets
    if "Dr." in raw or "Ms." in raw or "Sanehi" in raw or "Pooja" in raw or "Shivani" in raw:
        fac_match = re.search(r"(Dr\.\s*[^–—\)\n#]+|Ms\.\s*[^–—\)\n#]+|Sanehi|Pooja|Shivani[^–—\)\n#]*)", raw)
        # Better extraction from right side or regex:
        # Let's see: usually after "–"
        dash_parts = re.split(r"[–—]", raw)
        if len(dash_parts) > 1:
            # take right part before any closing paren or trailing room
            right = dash_parts[-1].strip()
            # If trailing room exists like ") L407"
            right = re.sub(r"\)\s*[A-Z0-9]+.*", "", right).strip()
            faculty = right
        else:
            faculty = fac_match.group(1).strip() if fac_match else "Faculty TBA"
    else:
        faculty = "Faculty TBA"

    # Clean faculty string
    faculty = faculty.strip()

    # Determine Session Type
    if "Lab" in raw:
        session_type = "Practical"
    elif "Tut" in raw:
        session_type = "Tutorial"
    elif "MSC L" in raw or "(L)" in raw or "L " in raw or " L" in raw:
        session_type = "Lecture"
    else:
        session_type = "Lecture"

    # Extract sections / groups
    # Look for (DS2+DS3), (DS1), (G1), (G2), (CSE3,CSE4), AI1+AI2
    sec_matches = re.findall(r"(?:CSE[1-7]|DS[1-4]|AI[1-2]|G[1-2])", raw)
    sec_matches = list(dict.fromkeys(sec_matches))  # deduplicate preserving order
    if not sec_matches:
        # Default all department sections
        if dept == "DS":
            sec_matches = ["DS1", "DS2", "DS3", "DS4"]
        elif dept == "AI":
            sec_matches = ["AI1", "AI2"]
        elif dept == "CSE":
            # If not specified, is it for entire CSE or G1/G2?
            # E.g. CSP5101 handled above
            sec_matches = ["CSE1", "CSE2", "CSE3", "CSE4", "CSE5", "CSE6", "CSE7"]

    # Extract rooms:
    # 301, 303, 304, 305, 306, 402, 405, 407, L19, L21, L22, L26, L30, L405, L406, L407, CL5, CL13, CL14, DS lab
    venue_candidates = [
        "301", "303", "304", "305", "306", "402", "405", "407",
        "L19", "L21", "L22", "L26", "L30", "L405", "L406", "L407",
        "CL5", "CL13", "CL14", "DS lab"
    ]
    found_rooms = []
    # Match plus combinations e.g. 301+CL14, 305+CL13+CL14, 301+306
    for vc in venue_candidates:
        # check whole word match
        pattern = r"(?<![A-Za-z0-9])" + re.escape(vc) + r"(?![A-Za-z0-9])"
        if re.search(pattern, raw, re.IGNORECASE):
            found_rooms.append(vc)

    # Sort rooms by appearance in raw text
    found_rooms.sort(key=lambda r: raw.find(r) if raw.find(r) != -1 else 999)
    # Deduplicate
    found_rooms = list(dict.fromkeys(found_rooms))

    # Room type
    if session_type == "Practical" or any("CL" in r or "lab" in r.lower() for r in found_rooms):
        room_type = "Computer Lab"
    else:
        room_type = "Classroom"

    rooms_required = len(found_rooms) if found_rooms else 1

    # Map faculty ID
    # Clean faculty string
    fac_name = faculty
    if "Shivani" in fac_name:
        fac_name = "Shivani"  # Unify base name, flag note
    elif "Dr. Ravpreet" in fac_name:
        fac_name = "Dr. Ravpreet"
    elif "Sandeep Harit" in fac_name:
        fac_name = "Dr. Sandeep Harit"
    elif "Dr. Rajesh Bhatia" in fac_name:
        fac_name = "Dr. Rajesh Bhatia"
    elif "Dr. Suraj Srivastava" in fac_name:
        fac_name = "Dr. Suraj Srivastava"
    elif "Dr. Manish Kumar" in fac_name:
        fac_name = "Dr. Manish Kumar"
    elif "Ms. Ishita" in fac_name:
        fac_name = "Ms. Ishita"
    elif "Sanehi" in fac_name:
        fac_name = "Sanehi"
    elif "Dr. Tejinder" in fac_name:
        fac_name = "Dr. Tejinder"
    elif "Dr. Dipika" in fac_name:
        fac_name = "Dr. Dipika"
    elif "Dr. Shilpa" in fac_name:
        fac_name = "Dr. Shilpa"
    elif "Dr. Pravneet Kaur" in fac_name:
        fac_name = "Dr. Pravneet Kaur"
    elif "Dr. Padmavati" in fac_name:
        fac_name = "Dr. Padmavati"
    elif "Dr. Alka Jindal" in fac_name:
        fac_name = "Dr. Alka Jindal"
    elif "Dr. Divya Bansal" in fac_name or "Pooja" in fac_name:
        fac_name = "Dr. Divya Bansal"

    # Map section IDs
    sec_ids = []
    for s in sec_matches:
        if s.startswith("G"):
            sec_ids.append(f"GRP_{s}")
        else:
            sec_ids.append(f"SEC_{s}")

    # Course name from raw text
    # Extract clean title e.g. "DSN5001 DAIR", "CSN5004 DBMS"
    title_match = re.search(r"((?:DSN|DSP|DSH|DSM|CSN|CSP|CSH|CSM|AIN|AIP|AIH|AIM)\d+\s+[A-Za-z0-9\-]+)", raw)
    cname = title_match.group(1).strip() if title_match else f"{code} Course"

    parsed_events.append({
        "code": code,
        "name": cname,
        "session_type": session_type,
        "faculty": fac_name,
        "raw_faculty": faculty,
        "sections": sec_matches,
        "section_ids": sec_ids,
        "rooms": found_rooms,
        "rooms_required": rooms_required,
        "room_type": room_type,
        "duration": ev["duration"],
        "dept": dept,
        "needs_review": False,
        "review_reason": None,
        "target": {"day_idx": ev["day_idx"], "start_period": ev["start_period"], "duration": ev["duration"]}
    })

print(f"Total parsed events: {len(parsed_events)}")

# Group into offerings
groups = defaultdict(list)
for e in parsed_events:
    # Offerings grouped by code, session_type, sections, duration, rooms_required, faculty
    key = (e['code'], e['session_type'], tuple(sorted(e['section_ids'])), e['duration'], e['rooms_required'], e['faculty'])
    groups[key].append(e)

print(f"Total distinct course offerings: {len(groups)}")
total_sessions = sum(len(evs) for evs in groups.values())
print(f"Total weekly sessions across all offerings: {total_sessions}")

# Inspect some offerings
for k, evs in list(groups.items())[:20]:
    targets = [f"{e['target']['day_idx']}:P{e['target']['start_period']+1}" for e in evs]
    rooms = list(dict.fromkeys(r for e in evs for r in e['rooms']))
    print(f"[{k[0]}] {k[1]} | Secs: {len(k[2])} | Dur: {k[3]} | RoomsReq: {k[4]} (Rooms: {rooms}) | Fac: {k[5]} -> Sessions/week: {len(evs)} @ {targets}")

