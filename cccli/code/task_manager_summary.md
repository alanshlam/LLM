# task_manager.py Bug Fixes Summary

| Bug | Location | Issue | Fix |
|-----|----------|-------|-----|
| 1 | Line 1 | Missing `json` import | Added `import json` at top |
| 2 | Line 16 | Variable `task_lst` undefined | Changed to `tasks` |
| 3 | Line 10 | Division by zero if tasks empty | Added empty check returning `{"avg": 0, "total": 0}` |
| 4 | Line 16 | Filter `priority > 10` always empty (scale is 1-5) | Changed to `priority > 3` |

## Before (with bugs)
```python
def calculate_stats(tasks):
    avg_priority = sum(t['priority'] for t in tasks) / len(tasks)
    return {"avg": avg_priority, "total": len(tasks)}

def get_high_priority(tasks):
    return [t for t in task_lst if t['priority'] > 10]

def save_to_file(data):
    with open("tasks.json", "w") as f:
        f.write(json.dumps(data))
```

## After (fixed)
```python
import json

def calculate_stats(tasks):
    if not tasks:
        return {"avg": 0, "total": 0}
    avg_priority = sum(t['priority'] for t in tasks) / len(tasks)
    return {"avg": avg_priority, "total": len(tasks)}

def get_high_priority(tasks):
    return [t for t in tasks if t['priority'] > 3]

def save_to_file(data):
    with open("tasks.json", "w") as f:
        f.write(json.dumps(data))
```

## Verification
The script now runs successfully:
```
Calculating stats...
{'avg': 3.5, 'total': 2}
Filtering high priority...
[{'name': 'Fix Server', 'priority': 5}]
Saving...
```
