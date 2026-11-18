import re
import os
from collections import defaultdict

SOURCE_FILE = r"c:\Users\Lenovo\Downloads\timetables.md"

with open(SOURCE_FILE, "r", encoding="utf-8") as f:
    text = f.read()

tables = re.split(r"##\s+", text)[1:]
period_map = [(1, 0), (2, 1), (3, 2), (4, 3), (5, 4), (7, 5), (8, 6), (9, 7)]
day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
day_short_map = {"MON": 0, "TUES": 1, "WED": 2, "THURS": 3, "FRI": 4}

raw_merged_events = []

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
                        
                raw_merged_events.append({
                    "dept": dept,
                    "day_idx": day_idx,
                    "day_name": day_names[day_idx],
                    "start_period": p,
                    "duration": dur,
                    "raw_text": item,
                })

print(f"Total merged events: {len(raw_merged_events)}")

# Let's inspect raw text patterns
for e in raw_merged_events:
    txt = e["raw_text"]
    dept = e["dept"]
    day = e["day_name"]
    p = e["start_period"] + 1
    dur = e["duration"]
    print(f"[{dept}] {day[:3]} P{p} dur={dur} : {txt}")
