# Task Queue Mode

**Purpose**: Sequential task execution with intelligent conflict detection, dependency resolution, and auto-execution.

## Activation Triggers
- `/queue`, `/queue:list`, `/queue:cancel`, `/queue:next`, `/queue:move` commands
- Keywords: "큐", "다음 작업", "나중에", "그 다음", "after this", "queue"
- User mentions another task while Claude is working
- Manual flag: `--queue`

## Core Features

### 1. Conflict Detection
When adding tasks, the system analyzes command scope:
- **Files**: Direct file references
- **Modules**: Module/component names
- **Directories**: Directory paths

Conflicts are detected when multiple tasks target the same scope.

### 2. Dependency Resolution
- **Topological Sort**: Tasks with dependencies execute in correct order
- **Priority Levels**: critical > high > normal > low
- **FIFO**: Within same priority and no dependencies

### 3. Failure Handling
- Failed tasks are logged to history
- Dependent tasks are blocked
- Independent tasks continue execution

### 4. Auto-Execution
After task completion, next executable task runs automatically.

## Commands

| Command | Description |
|---------|-------------|
| `/queue "cmd"` | Add task to queue |
| `/queue "cmd" --priority high` | Add with priority |
| `/queue "cmd" --after task-id` | Add with dependency |
| `/queue:list` | View queue status |
| `/queue:cancel task-id` | Cancel specific task |
| `/queue:cancel --all` | Clear entire queue |
| `/queue:next` | Execute next task |
| `/queue:move task-id --first` | Move to top priority |

## Conflict Resolution Options

When conflict detected:
```
⚠️ CONFLICT DETECTED

Your task: /sc:implement update-profile
Conflicts with: !npm run migrate:profile

Reason: modules: profile

Options:
1. [P]arallel - Run independently (risk)
2. [D]epend - Run after conflicting task (safe)
3. [C]ancel - Don't add
```

## Integration

### With Shell Commands
```bash
# Queue bash commands
/queue "!npm run build"
/queue "!pytest tests/"
# Will auto-execute after current task
```

### With Skill Commands
```bash
/queue "/sc:test integration" --after task-001
/queue "/sc:deploy staging" --priority high
```

### Chaining
```bash
/queue "/sc:build" --on-success "/sc:deploy" --on-fail "/sc:notify"
```

## File Locations

```
~/.claude/
├── queue/
│   ├── tasks.json       # Active queue
│   └── history.json     # Completed/failed tasks
├── scripts/
│   └── queue_manager.py # Core logic
├── commands/
│   ├── queue.md         # /queue
│   └── queue/           # Subcommands
│       ├── list.md      # /queue:list
│       ├── cancel.md    # /queue:cancel
│       ├── next.md      # /queue:next
│       └── move.md      # /queue:move
├── hooks/
│   ├── queue-auto-execute.sh
│   └── queue-session-start.sh
└── skills/
    └── task-queue/
        └── SKILL.md
```

## Behavioral Notes

- **Scope Analysis**: Commands are parsed to extract target files/modules
- **Conflict Warning**: Always warn before parallel execution of conflicting tasks
- **History Tracking**: All completed/failed/cancelled tasks logged
- **Session Persistence**: Queue survives session restarts
- **Auto-Continue**: After completion, automatically proceeds to next task

## Examples

### Basic Queue Usage
```
User: "이거 끝나면 테스트도 돌려줘"

Claude:
✅ Task queued: /sc:test
   Position: #1
   Will auto-execute after current task
```

### Conflict Handling
```
User: /queue "/sc:implement update-auth"

Claude:
⚠️ Conflict detected with existing task targeting 'auth' module

   Options:
   - Depend: Run after task-001 completes (recommended)
   - Parallel: Run independently (risk of conflicts)
   - Cancel: Don't add this task

User: depend

Claude:
✅ Task added with dependency on task-001
   Will execute after !npm run migrate:auth completes
```

### Failure Recovery
```
Task task-001 failed: Type error in auth module

Skipping dependent tasks:
- task-002: /sc:test auth (blocked)

Continuing with independent tasks:
- task-003: /sc:build docs
```
