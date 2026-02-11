# /queue:cancel - Cancel Queued Task(s)

Remove task(s) from the queue without executing.

## Usage
```
/queue:cancel task-001
/queue:cancel --all
```

## Behavior

### Cancel Specific Task
```bash
python3 ~/.claude/scripts/queue_manager.py cancel task-001
```

### Cancel All Tasks
```bash
python3 ~/.claude/scripts/queue_manager.py cancel --all
```

## Output Format

### Single Cancel
```
✅ Task cancelled: task-001
   Command: !npm run build

Remaining in queue: $COUNT tasks

⚠️ Dependent tasks affected:
   - task-002 (was depending on task-001)
   - task-003 (was depending on task-001)

These tasks are now blocked. Options:
1. Cancel dependent tasks too
2. Remove their dependencies (make them executable)
```

### Cancel All
```
✅ Queue cleared
   Cancelled: $COUNT tasks

Tasks moved to history:
   - task-001: !npm run build
   - task-002: /sc:test integration
```

## Safety Checks
- Cannot cancel a running task (must wait or interrupt)
- Warns about dependent tasks that will be blocked
- Confirms before cancelling multiple tasks
