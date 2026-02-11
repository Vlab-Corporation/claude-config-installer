---
name: task-queue
description: Manage task queue for sequential execution with conflict detection, dependency resolution, and auto-execution. Use when user wants to queue tasks, check queue status, or manage task execution order.
allowed-tools: Bash, Read, Write
user-invocable: false
---

# Task Queue Management Skill

This skill enables intelligent task queue management for Claude Code sessions.

## When to Activate
- User mentions "queue", "다음 작업", "나중에", "after this"
- User wants to schedule multiple tasks
- User is working on something and mentions another task to do later
- Commands like /queue, /queue:list, /queue:cancel, /queue:next

## Core Capabilities

### 1. Add Task to Queue
```bash
python3 ~/.claude/scripts/queue_manager.py add "command" [priority]
```

### 2. Check for Conflicts
When adding a task, always analyze the result for conflicts:
```json
{
  "conflicts": [...],
  "action_required": true,
  "options": ["parallel", "depend", "cancel"]
}
```

If conflicts detected, ask user:
- **Parallel**: Run independently (risk of conflicts)
- **Depend**: Add as dependency (safe, sequential)
- **Cancel**: Don't add

### 3. Resolve Conflicts
```bash
python3 ~/.claude/scripts/queue_manager.py add-resolved "command" "depend" "conflict-task-id"
```

### 4. Execute Next Task
```bash
# Get next executable task
python3 ~/.claude/scripts/queue_manager.py next

# Mark as started
python3 ~/.claude/scripts/queue_manager.py start task-id

# After execution, mark complete
python3 ~/.claude/scripts/queue_manager.py complete task-id true  # success
python3 ~/.claude/scripts/queue_manager.py complete task-id false "error"  # failure
```

### 5. Auto-Continuation
After completing a task, always check for next:
- If successful: Execute `on_success` chain or next in queue
- If failed: Skip dependent tasks, execute independent tasks

## Conflict Detection Logic

The system analyzes commands to extract scope:
- **Files**: Direct file references in command
- **Modules**: Module/component names mentioned
- **Directories**: Directory paths referenced

Conflicts occur when:
- Same files targeted by multiple tasks
- Same modules modified by multiple tasks
- Overlapping directory scopes

## Priority System

Execution order: `critical > high > normal > low`

Within same priority:
1. Dependency order (topological sort)
2. FIFO (creation time)

## Commands Reference

| Command | Action |
|---------|--------|
| `add "cmd" [priority]` | Add new task |
| `add-resolved "cmd" "resolution" "deps"` | Add with conflict resolution |
| `list [status]` | Show queue |
| `cancel task-id` | Cancel specific task |
| `cancel --all` | Clear queue |
| `next` | Get next executable |
| `start task-id` | Mark as running |
| `complete task-id success [error]` | Mark completion |
| `move task-id position` | Change priority |
| `status` | Queue summary |

## Integration Pattern

When user mentions a future task while working:

1. **Detect Intent**: "다음에", "나중에", "그 다음", "after this"
2. **Extract Command**: Parse the intended task
3. **Add to Queue**: Run add command with scope analysis
4. **Handle Conflicts**: If any, present options to user
5. **Confirm**: Show task position in queue
6. **Continue Current Work**: Don't interrupt current task

## Example Interaction

User: "이거 끝나면 테스트도 돌려줘"

Claude:
```bash
python3 ~/.claude/scripts/queue_manager.py add "/sc:test integration"
```

Result analysis → No conflicts → Task added

Response:
```
✅ Task queued: /sc:test integration
   Position: #1 in queue
   Will auto-execute after current task
```
