# /queue:list - View Queue Status

Display all tasks in the queue with their status, priority, and execution order.

## Usage
```
/queue:list
/queue:list --status queued
/queue:list --verbose
```

## Behavior

Execute:
```bash
python3 ~/.claude/scripts/queue_manager.py list
```

## Output Format

```
📋 TASK QUEUE STATUS

Queued: $QUEUED_COUNT | Running: $RUNNING_COUNT | Today: ✅$COMPLETED ❌$FAILED

EXECUTION ORDER:
┌────┬─────────────┬──────────────────────────────────────┬──────────┬─────────────┐
│ #  │ ID          │ Command                              │ Priority │ Depends On  │
├────┼─────────────┼──────────────────────────────────────┼──────────┼─────────────┤
│ 1  │ task-a1b2   │ !npm run build                       │ high     │ -           │
│ 2  │ task-c3d4   │ /sc:test integration                 │ normal   │ task-a1b2   │
│ 3  │ task-e5f6   │ /sc:deploy staging                   │ normal   │ task-c3d4   │
└────┴─────────────┴──────────────────────────────────────┴──────────┴─────────────┘

SCOPE ANALYSIS (--verbose):
task-a1b2: modules=[profile], files=[profile.ts, profile.test.ts]
task-c3d4: scope=[integration tests]
task-e5f6: scope=[deployment]

NEXT EXECUTABLE: task-a1b2
```

## Status Filters
- `--status queued` - Show only queued tasks
- `--status running` - Show only running tasks
- `--status all` - Show all including completed (from history)

## Verbose Mode
Shows additional information:
- Scope analysis for each task
- Conflict potential between tasks
- Estimated execution time
- Chain relationships
