#!/usr/bin/python3

# task_manager.py
# Fixed version with 4 bugs corrected:
# 1. Added missing import (json)
# 2. Fixed variable name typo (task_lst -> tasks)
# 3. Added division by zero protection
# 4. Fixed logic error in filter (> 10 -> >= 4 for 1-5 scale)

import json

def calculate_stats(tasks):
    # FIX 3: Handle empty tasks list
    if not tasks:
        return {"avg": 0, "total": 0}
    avg_priority = sum(t['priority'] for t in tasks) / len(tasks)
    return {"avg": avg_priority, "total": len(tasks)}

def get_high_priority(tasks):
    # FIX 2: Corrected variable name from 'task_lst' to 'tasks'
    # FIX 4: Changed > 10 to >= 4 (high priority on 1-5 scale)
    return [t for t in tasks if t['priority'] >= 4]

def save_to_file(data):
    # FIX 1: json is now imported
    with open("tasks.json", "w") as f:
        f.write(json.dumps(data))

if __name__ == "__main__":
    my_tasks = [
        {"name": "Fix Server", "priority": 5},
        {"name": "Email Client", "priority": 2}
    ]

    print("Calculating stats...")
    print(calculate_stats(my_tasks))

    print("Filtering high priority...")
    print(get_high_priority(my_tasks))

    print("Saving...")
    save_to_file(my_tasks)
