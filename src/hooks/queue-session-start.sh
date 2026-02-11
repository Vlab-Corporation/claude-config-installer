#!/bin/bash
# Hook: Notify about pending queue on session start
# Triggered by: SessionStart event

QUEUE_MANAGER="$HOME/.claude/scripts/queue_manager.py"

# Check if queue manager exists
if [ ! -f "$QUEUE_MANAGER" ]; then
    exit 0
fi

# Get queue status
QUEUE_STATUS=$(python3 "$QUEUE_MANAGER" status 2>/dev/null)

if [ -z "$QUEUE_STATUS" ]; then
    exit 0
fi

# Parse status
QUEUED=$(echo "$QUEUE_STATUS" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('queued', 0))" 2>/dev/null)
RUNNING=$(echo "$QUEUE_STATUS" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('running', 0))" 2>/dev/null)

if [ "$QUEUED" -gt 0 ] || [ "$RUNNING" -gt 0 ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📋 TASK QUEUE STATUS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "   Queued:  $QUEUED task(s)"
    echo "   Running: $RUNNING task(s)"
    echo ""

    if [ "$QUEUED" -gt 0 ]; then
        # Show first few tasks
        TASK_LIST=$(python3 "$QUEUE_MANAGER" list 2>/dev/null)
        echo "   Next tasks:"
        echo "$TASK_LIST" | python3 -c "
import sys, json
d = json.load(sys.stdin)
tasks = d.get('tasks', [])[:3]
for i, t in enumerate(tasks, 1):
    cmd = t.get('command', '')[:40]
    if len(t.get('command', '')) > 40:
        cmd += '...'
    print(f'   {i}. {cmd}')
" 2>/dev/null
        echo ""
        echo "   Use /queue:list to see full queue"
        echo "   Use /queue:next to execute next task"
    fi
    echo ""
fi
