#! /usr/bin/python3

# task_manager.py
# This script has 4 intentional bugs:
# 1. Missing import (json)
# 2. Variable name typo (task_lst vs tasks)
# 3. Division by Zero error
# 4. Logic error in the filter (returns empty list)

def calculate_stats(tasks):
    # BUG 3: Division by zero if tasks is empty
    avg_priority = sum(t['priority'] for t in tasks) / len(tasks)
    return {"avg": avg_priority, "total": len(tasks)}

def get_high_priority(tasks):
    # BUG 2: Typo 'task_lst' instead of 'tasks'
    # BUG 4: Logic error (> 10 is impossible if scale is 1-5)
    return [t for t in task_lst if t['priority'] > 10]

def save_to_file(data):
    # BUG 1: 'json' is not imported
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

