import os
import subprocess
from datetime import datetime, timedelta

locations = [
    "tokyo_tower",
    "senso_ji",
    "akihabara",
    "meiji_shrine",
    "tsukiji_market",
    "odaiba",
    "shinjuku_garden"
]

stay_times = {
    "tokyo_tower": 121,
    "senso_ji": 121,
    "akihabara": 121,
    "meiji_shrine": 121,
    "tsukiji_market": 121,
    "odaiba": 121,
    "shinjuku_garden": 121
}

travel_time_matrix = [
    [0,   62,  123, 185, 240, 300, 123],
    [62,   0,   62, 123, 185, 240, 185],
    [123, 62,   0,  123, 185, 240, 185],
    [185, 123, 123,   0, 123, 185,  62],
    [240, 185, 185, 123,   0, 185, 123],
    [300, 240, 240, 185, 185,   0, 123],
    [123, 185, 185,  62, 123, 123,   0]
]

travel_times = {}
for i, loc1 in enumerate(locations):
    for j, loc2 in enumerate(locations):
        if i != j:
            travel_times[(loc1, loc2)] = travel_time_matrix[i][j]

WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

opening_hours = {
    "tokyo_tower": {
        "monday":    [(9,17)],
        "tuesday":   [(10,20)],
        "wednesday": [(8,12),(13,18)],
        "thursday":  [],
        "friday":    [(9,17)],
        "saturday":  [(10,16)],
        "sunday":    [(10,16)],
    },
    "senso_ji": {
        "monday":    [(8,18)],
        "tuesday":   [(8,18)],
        "wednesday": [(8,18)],
        "thursday":  [(8,18)],
        "friday":    [(8,18)],
        "saturday":  [(8,18)],
        "sunday":    [(8,18)],
    },
    "akihabara": {
        "monday":    [(10,22)],
        "tuesday":   [(10,22)],
        "wednesday": [(10,22)],
        "thursday":  [(10,22)],
        "friday":    [(10,22)],
        "saturday":  [(10,22)],
        "sunday":    [(10,22)],
    },
    "meiji_shrine": {
        "monday":    [(8,16)],
        "tuesday":   [(8,16)],
        "wednesday": [(8,16)],
        "thursday":  [(8,16)],
        "friday":    [(8,16)],
        "saturday":  [(8,16)],
        "sunday":    [(8,16)],
    },
    "tsukiji_market": {
        "monday":    [(6,14)],
        "tuesday":   [(6,14)],
        "wednesday": [(6,14)],
        "thursday":  [(6,14)],
        "friday":    [(6,14)],
        "saturday":  [(6,14)],
        "sunday":    [(6,14)],
    },
    "odaiba": {
        "monday":    [(10,21)],
        "tuesday":   [(10,21)],
        "wednesday": [(10,21)],
        "thursday":  [(10,21)],
        "friday":    [(10,21)],
        "saturday":  [(10,21)],
        "sunday":    [(10,21)],
    },
    "shinjuku_garden": {
        "monday":    [(9,17)],
        "tuesday":   [(9,17)],
        "wednesday": [(9,17)],
        "thursday":  [(9,17)],
        "friday":    [(9,17)],
        "saturday":  [(9,17)],
        "sunday":    [(9,17)],
    },
}

time_slots = [f"ts_{h}" for h in range(24)]

def generate_domain_pddl():
    domain_content = """(define (domain tokyo_trip)
  (:requirements :strips :typing :action-costs)
  (:types
    day location time_slot
  )
  (:predicates
    (at ?loc - location)
    (available ?loc - location)
    (visited ?loc - location)
    (day_now ?d - day)
    (next_day ?d1 ?d2 - day)
    (time_slot_now ?ts - time_slot)
    (next_slot ?ts1 ?ts2 - time_slot)
    (open ?loc - location ?d - day ?ts - time_slot)
  )
  (:functions
    (total-cost - number)
    (travel_time ?from - location ?to - location)
    (play_time ?loc - location)
  )
  (:action move
    :parameters (?from - location ?to - location ?d - day ?ts - time_slot)
    :precondition (and
      (at ?from)
      (available ?to)
      (day_now ?d)
      (time_slot_now ?ts)
      (open ?to ?d ?ts)
    )
    :effect (and
      (not (at ?from))
      (at ?to)
      (increase (total-cost) (travel_time ?from ?to))
    )
  )
  (:action visit
    :parameters (?loc - location ?d - day ?ts - time_slot)
    :precondition (and
      (at ?loc)
      (available ?loc)
      (day_now ?d)
      (time_slot_now ?ts)
      (open ?loc ?d ?ts)
    )
    :effect (and
      (visited ?loc)
      (increase (total-cost) (play_time ?loc))
    )
  )
  (:action advance_slot
    :parameters (?ts1 - time_slot ?ts2 - time_slot ?d - day)
    :precondition (and
      (time_slot_now ?ts1)
      (day_now ?d)
      (next_slot ?ts1 ?ts2)
    )
    :effect (and
      (not (time_slot_now ?ts1))
      (time_slot_now ?ts2)
      (increase (total-cost) 0)
    )
  )
)
"""
    with open("domain.pddl", "w", encoding="utf-8") as f:
        f.write(domain_content)

def generate_problem_pddl(start_day_name: str, n_days: int):
    day_names = [f"day{i}" for i in range(1, n_days+1)]
    if start_day_name.lower() not in WEEKDAYS:
        raise ValueError
    start_idx = WEEKDAYS.index(start_day_name.lower())
    def get_weekday_for_day(i):
        return WEEKDAYS[(start_idx + i) % 7]
    problem_content = f"(define (problem tokyo_trip_plan)\n  (:domain tokyo_trip)\n\n  (:objects\n    {' '.join(locations)} - location\n    {' '.join(day_names)} - day\n    {' '.join(time_slots)} - time_slot\n  )\n\n  (:init\n    (at tokyo_tower)\n"
    for loc in locations:
        problem_content += f"    (available {loc})\n"
    problem_content += "    (day_now day1)\n"
    problem_content += "    (time_slot_now ts_8)\n"
    for i in range(n_days - 1):
        problem_content += f"    (next_day {day_names[i]} {day_names[i+1]})\n"
    for h in range(23):
        problem_content += f"    (next_slot ts_{h} ts_{h+1})\n"
    problem_content += "    (= (total-cost) 0)\n\n"
    for loc, pt in stay_times.items():
        problem_content += f"    (= (play_time {loc}) {pt})\n"
    for (lf, lt), tval in travel_times.items():
        problem_content += f"    (= (travel_time {lf} {lt}) {tval})\n"
    problem_content += "\n"
    for i, dname in enumerate(day_names):
        wd = get_weekday_for_day(i)
        for loc in locations:
            intervals = opening_hours[loc].get(wd, [])
            for hour in range(24):
                for (start_h, end_h) in intervals:
                    if start_h <= hour < end_h:
                        problem_content += f"    (open {loc} {dname} ts_{hour})\n"
                        break
    problem_content += "  )\n\n  (:goal (and\n"
    for loc in locations:
        problem_content += f"    (visited {loc})\n"
    problem_content += "  ))\n  (:metric minimize (total-cost))\n)\n"
    with open("problem.pddl", "w", encoding="utf-8") as f:
        f.write(problem_content)

def run_planner():
    cmd = ["python","fast-downward.py","--alias","seq-sat-lama-2011","domain.pddl","problem.pddl"]
    subprocess.run(cmd, check=True)

def parse_sas_plan_pretty():
    plan_files = sorted([p for p in os.listdir('.') if p.startswith("sas_plan")], key=lambda x: os.path.getmtime(x))
    if not plan_files:
        print("No sas_plan found.")
        return
    latest_plan = plan_files[-1]
    print(f"Using plan: {latest_plan}\n")
    with open(latest_plan, "r", encoding="utf-8") as f:
        actions = [ln.strip().lower() for ln in f if ln.strip().startswith("(")]
    def get_time_for_slot(slot_name: str, day_num: int):
        hour = int(slot_name.replace("ts_", ""))
        base_date = datetime(2025, 1, 1) + timedelta(days=day_num - 1)
        return base_date.replace(hour=hour, minute=0, second=0)
    current_day = 1
    current_slot = "ts_8"
    current_time = get_time_for_slot(current_slot, current_day)
    for line in actions:
        tokens = line.strip("()").split()
        act = tokens[0]
        if act == "move":
            _, loc_from, loc_to, dayx, slot = tokens
            day_num = int(dayx.replace("day", ""))
            if day_num != current_day:
                current_day = day_num
                current_time = get_time_for_slot(slot, current_day)
                current_slot = slot
            elif slot != current_slot:
                new_time = get_time_for_slot(slot, current_day)
                if new_time > current_time:
                    current_time = new_time
                current_slot = slot
            tmin = travel_times.get((loc_from, loc_to), 10)
            start_t = current_time
            end_t = start_t + timedelta(minutes=tmin)
            print(f"Day {current_day}, {start_t.strftime('%H:%M')} - {end_t.strftime('%H:%M')}: MOVE {loc_from} -> {loc_to}")
            current_time = end_t
        elif act == "visit":
            _, loc, dayx, slot = tokens
            day_num = int(dayx.replace("day", ""))
            if day_num != current_day:
                current_day = day_num
                current_slot = slot
                current_time = get_time_for_slot(slot, current_day)
            elif slot != current_slot:
                new_time = get_time_for_slot(slot, current_day)
                if new_time > current_time:
                    current_time = new_time
                current_slot = slot
            pmin = stay_times.get(loc, 30)
            start_t = current_time
            end_t = start_t + timedelta(minutes=pmin)
            print(f"Day {current_day}, {start_t.strftime('%H:%M')} - {end_t.strftime('%H:%M')}: VISIT {loc}")
            current_time = end_t
        elif act == "advance_slot":
            _, slot_old, slot_new, dayx = tokens
            day_num = int(dayx.replace("day", ""))
            if day_num != current_day:
                current_day = day_num
            new_time = get_time_for_slot(slot_new, current_day)
            if new_time > current_time:
                print(f"Day {current_day}, {current_time.strftime('%H:%M')} - {new_time.strftime('%H:%M')}: [transition or idle]")
                current_time = new_time
            current_slot = slot_new
        else:
            print(f"Unknown action: {line}")
    print("\n=== End of schedule ===")

if __name__ == "__main__":
    START_DAY_NAME = "wednesday"
    N_DAYS = 5
    generate_domain_pddl()
    generate_problem_pddl(START_DAY_NAME, N_DAYS)
    run_planner()
    parse_sas_plan_pretty()
