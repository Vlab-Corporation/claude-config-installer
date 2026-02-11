#!/bin/bash
# Hook: Check for queue auto-continuation on user prompt
# Triggered by: UserPromptSubmit event
#
# This hook solves the root cause: "Hook cannot trigger Claude actions"
# Solution: Output <system-reminder> that Claude will interpret and act upon

QUEUE_DIR="$HOME/.claude/queue"
AUTO_CONTINUE_SCRIPT="$HOME/.claude/scripts/auto_continue.py"
FLAG_FILE="$QUEUE_DIR/.auto_continue"

# Check if continuation flag exists
if [ -f "$FLAG_FILE" ]; then
    # Use Python script to generate proper system reminder
    if [ -f "$AUTO_CONTINUE_SCRIPT" ]; then
        python3 "$AUTO_CONTINUE_SCRIPT" user-prompt
    else
        # Fallback: basic reminder without Python
        TASK_ID=$(python3 -c "import json; print(json.load(open('$FLAG_FILE')).get('task_id', 'unknown'))" 2>/dev/null)
        COMMAND=$(python3 -c "import json; print(json.load(open('$FLAG_FILE')).get('command', 'next task'))" 2>/dev/null)
        REMAINING=$(python3 -c "import json; print(json.load(open('$FLAG_FILE')).get('remaining', 0))" 2>/dev/null)

        if [ -n "$TASK_ID" ] && [ "$TASK_ID" != "unknown" ]; then
            echo ""
            echo "<system-reminder>"
            echo "QUEUE AUTO-CONTINUATION: A queued task is ready for execution."
            echo ""
            echo "Next Task:"
            echo "  ID: $TASK_ID"
            echo "  Command: $COMMAND"
            echo "  Remaining: $REMAINING more task(s) in queue"
            echo ""
            echo "ACTION REQUIRED: Execute /queue:next immediately to continue the queue."
            echo "</system-reminder>"

            # Clear the flag after outputting
            rm -f "$FLAG_FILE"
        fi
    fi
fi
