#!/bin/bash
# Hook: Set continuation flag after current task completes
# Triggered by: Stop event
#
# This hook solves the root cause: "Stop event timing is too late"
# Solution: Instead of trying to execute (which doesn't work), we set a flag
# that will be read by the UserPromptSubmit hook on the next user interaction.

QUEUE_DIR="$HOME/.claude/queue"
QUEUE_MANAGER="$HOME/.claude/scripts/queue_manager.py"
AUTO_CONTINUE_SCRIPT="$HOME/.claude/scripts/auto_continue.py"
FLAG_FILE="$QUEUE_DIR/.auto_continue"

# Ensure queue directory exists
mkdir -p "$QUEUE_DIR"

# Check if there are queued tasks
QUEUE_STATUS=$(python3 "$QUEUE_MANAGER" status 2>/dev/null)
QUEUED=$(echo "$QUEUE_STATUS" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('queued', 0))" 2>/dev/null)

if [ "$QUEUED" -gt 0 ]; then
    # Get next task info
    NEXT_TASK=$(python3 "$QUEUE_MANAGER" next 2>/dev/null)
    HAS_NEXT=$(echo "$NEXT_TASK" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('has_next', False))" 2>/dev/null)

    if [ "$HAS_NEXT" = "True" ]; then
        TASK_ID=$(echo "$NEXT_TASK" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('task', {}).get('id', ''))" 2>/dev/null)
        TASK_CMD=$(echo "$NEXT_TASK" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('task', {}).get('command', ''))" 2>/dev/null)
        TASK_PRIORITY=$(echo "$NEXT_TASK" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('task', {}).get('priority', 'normal'))" 2>/dev/null)
        REMAINING=$(echo "$NEXT_TASK" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('remaining', 0))" 2>/dev/null)

        # Option 1: Use Python script if available
        if [ -f "$AUTO_CONTINUE_SCRIPT" ]; then
            python3 "$AUTO_CONTINUE_SCRIPT" stop
        else
            # Option 2: Fallback to direct JSON write
            cat > "$FLAG_FILE" << EOF
{
  "task_id": "$TASK_ID",
  "command": "$TASK_CMD",
  "priority": "$TASK_PRIORITY",
  "remaining": $REMAINING,
  "created_at": "$(date -u +"%Y-%m-%dT%H:%M:%S.000000")"
}
EOF
        fi

        # Display notification (informational only)
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📋 TASK QUEUE: Continuation flag set"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "   Next task: $TASK_ID"
        echo "   Command:   $TASK_CMD"
        echo "   Remaining: $REMAINING more task(s)"
        echo ""
        echo "   Queue will auto-continue on next prompt."
        echo ""
    fi
fi
