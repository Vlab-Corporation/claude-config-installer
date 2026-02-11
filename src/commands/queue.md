# /queue - Add Task to Queue

Add a task to the execution queue with conflict detection and scope analysis.

## Usage
```
/queue "command to execute"
/queue "command" --priority high
/queue "command" --after task-001
/queue "command" --on-success "next command" --on-fail "fallback command"
```

## Behavior

When this command is invoked:

1. **Parse the command** - Extract the task command from arguments
2. **Analyze scope** - Determine which files/modules will be modified
3. **Detect conflicts** - Check against existing queued tasks
4. **Handle conflicts** - If conflicts found, present options to user

## Execution Steps

### Step 1: Add Task
```bash
python3 ~/.claude/scripts/queue_manager.py add "$ARGUMENTS"
```

### Step 2: If CONFLICT_DETECTED
Present to user:
```
⚠️ CONFLICT DETECTED

Your task: $NEW_COMMAND
Conflicts with: $EXISTING_TASK

Overlapping scope:
- $CONFLICT_REASONS

Options:
1. [P]arallel - Run independently (risk: potential conflicts)
2. [D]epend - Add as dependency (runs after conflicting task)
3. [C]ancel - Don't add this task

Choose [P/D/C]:
```

### Step 3: Apply Resolution
Based on user choice:
- **P**: `python3 ~/.claude/scripts/queue_manager.py add-resolved "$COMMAND" parallel`
- **D**: `python3 ~/.claude/scripts/queue_manager.py add-resolved "$COMMAND" depend "$CONFLICT_TASK_IDS"`
- **C**: Do nothing, inform user

### Step 4: Confirm Addition
```
✅ Task added to queue
   ID: task-xxxxxxxx
   Command: $COMMAND
   Priority: $PRIORITY
   Position: #$POSITION in queue

Scope analysis:
   Files: $FILES
   Modules: $MODULES
   Estimated impact: $SCOPE
```

## Priority Levels
- `critical` - Execute first, urgent
- `high` - Execute before normal tasks
- `normal` - Default priority (FIFO among same priority)
- `low` - Execute when nothing else queued

## Dependency Syntax
- `--after task-001` - Run after specific task completes
- `--after task-001,task-002` - Run after multiple tasks complete

## Chaining Syntax
- `--on-success "command"` - Execute this command if task succeeds
- `--on-fail "command"` - Execute this command if task fails

## Examples

```bash
# Simple task (bash command)
/queue "!npm run build"

# High priority task (skill command)
/queue "/sc:test integration" --priority high

# Task with dependency
/queue "/sc:deploy staging" --after task-001

# Task with chaining
/queue "/sc:build" --on-success "/sc:deploy" --on-fail "/sc:notify-failure"
```
