# /queue:move - Change Task Priority

Move a task to a different priority position in the queue.

## Usage
```
/queue:move task-001 --first
/queue:move task-001 --last
/queue:move task-001 --priority high
```

## Behavior

```bash
python3 ~/.claude/scripts/queue_manager.py move task-001 first
```

## Priority Mappings
- `--first` → Sets priority to `critical`
- `--last` → Sets priority to `low`
- `--priority critical|high|normal|low` → Sets specific priority

## Output Format

```
✅ Task moved: task-001

Before: Priority normal, Position #3
After:  Priority critical, Position #1

New execution order:
1. task-001 (critical) ← moved
2. task-002 (high)
3. task-003 (normal)
```

## Notes
- Moving a task doesn't change its dependencies
- A task with unmet dependencies won't execute even with critical priority
- Use this for urgent tasks that have all dependencies satisfied
