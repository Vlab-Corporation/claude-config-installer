# /queue:next - Execute Next Task

Manually trigger execution of the next task in the queue.

## Usage
```
/queue:next
/queue:next --dry-run
```

## CRITICAL: Execution Logic

**Claude MUST execute the queued command using the appropriate tool:**

### Step 1: Get Next Task
```bash
python3 ~/.claude/scripts/queue_manager.py next
```

Parse the JSON result to extract `task.id` and `task.command`.

### Step 2: Mark Task as Started
```bash
python3 ~/.claude/scripts/queue_manager.py start {task_id}
```

### Step 3: Execute Based on Command Type

**IMPORTANT**: Detect command type and execute accordingly:

| Command Pattern | Execution Method |
|-----------------|------------------|
| `/sc:xxx args` | Use **Skill tool**: `skill="sc:xxx"`, `args="args"` |
| `/xxx args` | Use **Skill tool**: `skill="xxx"`, `args="args"` |
| `!cmd` | Use **Bash tool**: `command="cmd"` |
| Natural language | Claude interprets and executes directly |

#### Example Executions:

**For `/sc:implement user-auth`:**
```
Use Skill tool with:
  skill: "sc:implement"
  args: "user-auth"
```

**For `/commit`:**
```
Use Skill tool with:
  skill: "commit"
```

**For `!npm test`:**
```
Use Bash tool with:
  command: "npm test"
```

**For `Fix the type errors in auth module`:**
```
Claude directly executes this as an instruction
```

### Step 4: Mark Task Complete

After execution completes:

**On Success:**
```bash
python3 ~/.claude/scripts/queue_manager.py complete {task_id} true
```

**On Failure:**
```bash
python3 ~/.claude/scripts/queue_manager.py complete {task_id} false "Error description"
```

### Step 5: Auto-Continue

Check the `complete` response:
- If `auto_execute: true` and `next_task` exists → Execute next task immediately
- If `chain_task` exists → Queue and execute the chain task
- Otherwise → Report queue status

## Output Format

```
🚀 EXECUTING TASK

ID: task-a1b2
Command: !npm run build
Priority: high
Scope: modules=[build]

[Execution output here...]

✅ Task completed successfully

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 NEXT TASK (auto-executing...)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Dry Run Mode
```
/queue:next --dry-run
```

Shows what would be executed without actually running:
```
🔍 DRY RUN - Next task preview

Would execute:
   ID: task-a1b2
   Command: /sc:implement user-auth
   Execution: Skill tool (skill="sc:implement", args="user-auth")

Followed by (if successful):
   ID: task-c3d4
   Command: /sc:test integration
```

## Error Handling

If execution fails:
1. Mark task as failed with error message
2. Check for `on_fail` chain task
3. Skip dependent tasks
4. Continue with independent tasks

## No Task Available

```
📭 No executable tasks

Queue status:
- Queued: 2 tasks (blocked by dependencies)
- Waiting for: task-001 to complete

Use /queue:list to see full queue status.
```
