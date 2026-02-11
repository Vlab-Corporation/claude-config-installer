# Integration Test Scenarios

This document defines test scenarios for validating the `/planning` skill integration with existing systems.

---

## Test Categories

```
┌─────────────────────────────────────────────────────────────────────┐
│                      TEST CATEGORIES                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. /sc:brainstorm Integration                                      │
│  2. Queue System Integration                                        │
│  3. Domain Expert Integration                                       │
│  4. TodoWrite Integration                                           │
│  5. Error Recovery Scenarios                                        │
│  6. User Approval Workflow                                          │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 1. /sc:brainstorm Integration Tests

### Test 1.1: Basic Brainstorm Execution

```yaml
test_id: PLAN-BS-001
name: "Basic brainstorm execution via planning"
description: "Verify /planning correctly triggers /sc:brainstorm"

setup:
  - Clear existing todos
  - No context files

input: |
  /planning "로그인 기능 구현"

expected:
  phase_1:
    - Goal parsed: "로그인 기능 구현"
    - Domain detected: "security" or "general"

  phase_2:
    - /sc:brainstorm queued
    - Brainstorm executed with optimized prompt
    - Tasks generated (N > 0)
    - Tasks added to TodoWrite

  validation:
    - TodoWrite contains generated tasks
    - Each task has valid format (content, status, activeForm)

pass_criteria:
  - Phase 2 completes without error
  - At least 5 tasks generated
  - All tasks in TodoWrite
```

### Test 1.2: Brainstorm with Context Files

```yaml
test_id: PLAN-BS-002
name: "Brainstorm with context file analysis"
description: "Verify context files are incorporated into brainstorm"

setup:
  - Create test file: /tmp/test-auth.ts
  - File content: "export function login() { /* existing code */ }"

input: |
  /planning "인증 시스템 개선" @/tmp/test-auth.ts

expected:
  phase_1:
    - Context file loaded
    - Existing patterns detected
    - Context summary generated

  phase_2:
    - Brainstorm prompt includes context
    - Generated tasks reference existing patterns
    - No duplicate functionality suggested

validation:
  - Context file content reflected in analysis
  - Tasks are context-aware

pass_criteria:
  - Context file successfully loaded
  - Generated tasks mention existing code/patterns
```

### Test 1.3: Brainstorm Failure Recovery

```yaml
test_id: PLAN-BS-003
name: "Brainstorm failure recovery"
description: "Verify recovery when brainstorm fails"

setup:
  - Simulate brainstorm timeout
  - Or use extremely vague goal

input: |
  /planning "것"  # Intentionally vague

expected:
  phase_2:
    - Brainstorm fails or returns empty
    - Recovery prompt shown
    - Options presented: Retry / Manual / Cancel

recovery_flow:
  option_1_retry:
    - User selects retry
    - Simplified prompt used
    - Re-execution attempted

  option_2_manual:
    - User selects manual
    - Manual task entry interface shown
    - User can add tasks directly

pass_criteria:
  - Error gracefully handled
  - User given recovery options
  - System does not crash
```

---

## 2. Queue System Integration Tests

### Test 2.1: Auto-Queue Execution

```yaml
test_id: PLAN-Q-001
name: "Auto-queue planning phases"
description: "Verify planning phases are queued and executed in order"

input: |
  /planning "API 리팩토링"

expected:
  queue_sequence:
    1. "/sc:brainstorm {goal}" - queued
    2. Wait for completion
    3. "INTERNAL:review" - queued
    4. Wait for completion
    5. "INTERNAL:approval" - queued

validation:
  - Queue shows planning tasks
  - Tasks execute in correct order
  - No task skipped

pass_criteria:
  - Queue integration working
  - Sequential execution maintained
```

### Test 2.2: Queue Conflict Detection

```yaml
test_id: PLAN-Q-002
name: "Conflict with existing queue tasks"
description: "Verify conflict detection when planning targets same scope"

setup:
  - Add task to queue: "/sc:implement auth-module"

input: |
  /planning "인증 시스템 구현"

expected:
  - Conflict detected: "auth" module
  - Warning shown to user
  - Options: Depend / Parallel / Cancel

user_selects: "Depend"

result:
  - Planning tasks added with dependency
  - Will execute after existing auth task

pass_criteria:
  - Conflict correctly detected
  - Dependency correctly established
```

### Test 2.3: Queue Failure Handling

```yaml
test_id: PLAN-Q-003
name: "Queue failure during planning"
description: "Verify graceful handling when queue fails"

setup:
  - Simulate queue system failure

input: |
  /planning "기능 구현"

expected:
  - Queue failure detected
  - Fallback to direct execution
  - Warning shown but planning continues

pass_criteria:
  - Planning completes despite queue failure
  - User informed of fallback mode
```

---

## 3. Domain Expert Integration Tests

### Test 3.1: Auto Domain Detection

```yaml
test_id: PLAN-DE-001
name: "Automatic domain expert selection"
description: "Verify correct domain expert is auto-selected"

test_cases:
  security_domain:
    input: /planning "OAuth 2.0 로그인 구현"
    expected_domain: "security"
    expected_expert: "🔐 Security Expert"

  fintech_domain:
    input: /planning "결제 API 구현"
    expected_domain: "fintech"
    expected_expert: "💰 Fintech Expert"

  healthcare_domain:
    input: /planning "환자 데이터 관리"
    expected_domain: "healthcare"
    expected_expert: "🏥 Healthcare Expert"

  general_domain:
    input: /planning "버튼 컴포넌트 구현"
    expected_domain: "general"
    expected_expert: "General Expert"

pass_criteria:
  - Correct domain detected for each case
  - Domain-specific review criteria applied
```

### Test 3.2: Manual Domain Override

```yaml
test_id: PLAN-DE-002
name: "Manual domain specification"
description: "Verify --domain flag overrides auto-detection"

input: |
  /planning "데이터 처리 기능" --domain healthcare

expected:
  - Auto-detection skipped
  - Healthcare domain used
  - HIPAA checks included in review

pass_criteria:
  - Manual domain respected
  - Correct expert loaded
```

### Test 3.3: Domain Expert Handoff

```yaml
test_id: PLAN-DE-003
name: "Domain expert project handoff"
description: "Verify project-specific customization loaded"

setup:
  - Create .claude/planning.config.yaml with custom checklist

input: |
  /planning "결제 기능 추가"

expected:
  - Config file detected
  - Custom checklist items added
  - Expert handoff complete message shown

pass_criteria:
  - Project config loaded
  - Custom items in review
```

---

## 4. TodoWrite Integration Tests

### Test 4.1: Initial Task Creation

```yaml
test_id: PLAN-TW-001
name: "Create tasks in TodoWrite"
description: "Verify tasks correctly added to TodoWrite"

input: |
  /planning "CRUD API 구현"

expected:
  - TodoWrite updated after Phase 2
  - Each task has: content, status, activeForm
  - All tasks in "pending" status

validation:
  - Run /todos to verify
  - Count matches brainstorm output

pass_criteria:
  - Tasks in TodoWrite
  - Correct format
```

### Test 4.2: Gap Addition to TodoWrite

```yaml
test_id: PLAN-TW-002
name: "Add approved gaps to TodoWrite"
description: "Verify approved gaps correctly added"

setup:
  - Complete Phase 1-3
  - 5 gaps identified

input: |
  User approval: "1,3,5"

expected:
  - Only gaps 1, 3, 5 added
  - Gaps 2, 4 not added
  - TodoWrite total increased by 3
  - New tasks marked as from review

pass_criteria:
  - Selective addition works
  - Count matches selection
```

### Test 4.3: TodoWrite State Preservation

```yaml
test_id: PLAN-TW-003
name: "Preserve existing TodoWrite state"
description: "Verify planning doesn't corrupt existing tasks"

setup:
  - Add 5 existing tasks to TodoWrite
  - Mark 2 as "in_progress"

input: |
  /planning "새 기능"

expected:
  - Existing 5 tasks preserved
  - In-progress status preserved
  - New tasks appended, not replaced

pass_criteria:
  - No task loss
  - Status preserved
```

---

## 5. Error Recovery Scenarios

### Test 5.1: Session Interruption Recovery

```yaml
test_id: PLAN-ER-001
name: "Recovery from session interruption"
description: "Verify state preserved and resume works"

setup:
  - Start /planning "목표"
  - Complete Phase 1-3
  - Simulate session end (Ctrl+C)

recovery_input: |
  /planning --resume

expected:
  - State checkpoint found
  - Resume from Phase 4
  - Previous gaps still available

pass_criteria:
  - State recovered
  - Resume successful
```

### Test 5.2: Partial Review Recovery

```yaml
test_id: PLAN-ER-002
name: "Recovery from partial review failure"
description: "Verify partial results usable"

setup:
  - Start review phase
  - Edge Cases: Complete
  - Missing Features: Complete
  - Maintainability: FAIL (timeout)
  - Convention Guard: Complete
  - Domain Master: FAIL (MCP error)

expected:
  - Partial failure reported
  - Completed perspectives shown
  - User can proceed with available results

pass_criteria:
  - Partial results used
  - Clear failure reporting
```

### Test 5.3: Invalid Approval Recovery

```yaml
test_id: PLAN-ER-003
name: "Recovery from invalid approval input"
description: "Verify graceful handling of bad input"

test_cases:
  invalid_number:
    input: "1,2,99"  # 99 doesn't exist
    expected: "Gap #99 not found, please retry"

  invalid_format:
    input: "yes please"
    expected: "Invalid format, use: all / 1,2,3 / none"

  empty_input:
    input: ""
    expected: "Please select: all / numbers / none"

pass_criteria:
  - Clear error messages
  - Retry allowed
  - No state corruption
```

---

## 6. User Approval Workflow Tests

### Test 6.1: Full Approval Flow

```yaml
test_id: PLAN-UA-001
name: "Complete approval workflow"
description: "Verify full approval path"

input_sequence:
  1. /planning "기능 구현"
  2. (Wait for Phase 1-3)
  3. Review shows 7 gaps
  4. User inputs: "all"

expected:
  - All 7 gaps added
  - Finalize message shown
  - Final task count = original + 7

pass_criteria:
  - Full approval works
  - All gaps added
```

### Test 6.2: Selective Approval Flow

```yaml
test_id: PLAN-UA-002
name: "Selective approval workflow"
description: "Verify partial approval path"

input_sequence:
  1. Review shows 7 gaps
  2. User inputs: "1,3,5"

expected:
  - Only gaps 1, 3, 5 added
  - Rejected gaps (2, 4, 6, 7) shown
  - Final count = original + 3

pass_criteria:
  - Selective works
  - Rejection recorded
```

### Test 6.3: Full Rejection Flow

```yaml
test_id: PLAN-UA-003
name: "Full rejection workflow"
description: "Verify rejection path"

input_sequence:
  1. Review shows 7 gaps
  2. User inputs: "none"

expected:
  - No gaps added
  - Original tasks preserved
  - Rejection acknowledged

pass_criteria:
  - No unwanted additions
  - Clean exit
```

---

## Test Execution Checklist

```markdown
## Pre-Test Setup
- [ ] Clear TodoWrite
- [ ] Clear queue
- [ ] Reset session state
- [ ] Verify MCP servers available

## Test Execution
- [ ] PLAN-BS-001: Basic brainstorm
- [ ] PLAN-BS-002: Context files
- [ ] PLAN-BS-003: Failure recovery
- [ ] PLAN-Q-001: Auto-queue
- [ ] PLAN-Q-002: Conflict detection
- [ ] PLAN-Q-003: Queue failure
- [ ] PLAN-DE-001: Domain detection
- [ ] PLAN-DE-002: Domain override
- [ ] PLAN-DE-003: Expert handoff
- [ ] PLAN-TW-001: Task creation
- [ ] PLAN-TW-002: Gap addition
- [ ] PLAN-TW-003: State preservation
- [ ] PLAN-ER-001: Session recovery
- [ ] PLAN-ER-002: Partial review
- [ ] PLAN-ER-003: Invalid input
- [ ] PLAN-UA-001: Full approval
- [ ] PLAN-UA-002: Selective approval
- [ ] PLAN-UA-003: Full rejection

## Post-Test Cleanup
- [ ] Clear test files
- [ ] Reset configurations
- [ ] Document any issues
```

---

## Known Limitations

1. **Brainstorm Quality**: Depends on `/sc:brainstorm` output quality
2. **Queue Timing**: Auto-execution timing may vary
3. **Domain Detection**: Ambiguous goals may need manual override
4. **MCP Dependency**: Some features require MCP servers
