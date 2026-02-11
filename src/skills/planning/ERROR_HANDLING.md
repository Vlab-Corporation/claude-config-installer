# Error Handling and Fallback Logic

This document defines error scenarios, recovery strategies, and fallback mechanisms for the `/planning` skill.

---

## Error Categories

```
┌─────────────────────────────────────────────────────────────────────┐
│                      ERROR CATEGORIES                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │
│  │  PHASE 1    │  │  PHASE 2    │  │  PHASE 3    │  │  PHASE 4-5 │  │
│  │  Analysis   │  │ Brainstorm  │  │   Review    │  │  Approval  │  │
│  │  Errors     │  │   Errors    │  │   Errors    │  │   Errors   │  │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └─────┬──────┘  │
│         │                │                │               │          │
│   • Goal parse     • Queue fail    • Partial fail   • Timeout       │
│   • Domain detect  • Execution     • MCP error      • Invalid input │
│   • Context load   • Timeout       • Analysis fail  • State corrupt │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Analysis Errors

### Goal Parsing Failure

```yaml
error:
  type: "GOAL_PARSE_ERROR"
  description: "Unable to understand user's goal"

triggers:
  - Empty goal string
  - Non-actionable goal (e.g., "help", "?")
  - Goal in unsupported language

recovery:
  action: ASK_USER
  prompt: |
    목표를 이해하지 못했습니다. 다음 형식으로 다시 입력해주세요:
    /planning "구현하고자 하는 기능 설명"

    예시:
    /planning "사용자 인증 시스템 구현"
    /planning "결제 API 리팩토링"

fallback: null  # Cannot proceed without valid goal
```

### Domain Detection Failure

```yaml
error:
  type: "DOMAIN_DETECT_ERROR"
  description: "Unable to auto-detect domain"

triggers:
  - Ambiguous keywords
  - No domain keywords found
  - Multiple conflicting domains

recovery:
  action: ASK_USER
  prompt: |
    도메인을 자동으로 감지하지 못했습니다.
    다음 중 선택해주세요:
    1. security (보안/인증)
    2. fintech (금융/결제)
    3. healthcare (의료/건강)
    4. ecommerce (쇼핑/주문)
    5. general (일반)
    6. 직접 입력

fallback:
  action: USE_DEFAULT
  default_domain: "general"
  message: "General domain expert를 사용합니다."
```

### Context File Load Failure

```yaml
error:
  type: "CONTEXT_LOAD_ERROR"
  description: "Unable to load specified context files"

triggers:
  - File not found
  - Permission denied
  - File too large (>100KB)
  - Binary file

recovery:
  action: PARTIAL_CONTINUE
  strategy: |
    1. Skip failed files
    2. Report which files failed
    3. Continue with available context
  prompt: |
    일부 컨텍스트 파일을 로드하지 못했습니다:
    ❌ @missing-file.ts - 파일을 찾을 수 없음
    ✅ @existing-file.ts - 로드 완료

    로드된 파일로 계속 진행할까요? (Y/n)

fallback:
  action: CONTINUE_WITHOUT_CONTEXT
  message: "컨텍스트 없이 기본 분석을 진행합니다."
```

---

## Phase 2: Brainstorm Errors

### Queue Execution Failure

```yaml
error:
  type: "QUEUE_EXEC_ERROR"
  description: "/sc:brainstorm queue execution failed"

triggers:
  - Queue system not responding
  - Task conflict in queue
  - Queue full

recovery:
  action: RETRY_DIRECT
  max_retries: 2
  strategy: |
    1. First retry: Queue with delay
    2. Second retry: Direct execution (bypass queue)
    3. Final: Manual fallback

fallback:
  action: MANUAL_TASK_ENTRY
  prompt: |
    자동 작업 목록 생성에 실패했습니다.

    Options:
    1. [R]etry - 재시도
    2. [M]anual - 수동으로 작업 목록 작성
    3. [C]ancel - 취소
```

### Brainstorm Timeout

```yaml
error:
  type: "BRAINSTORM_TIMEOUT"
  description: "Brainstorm execution exceeded time limit"
  timeout: 120s

triggers:
  - Complex goal requiring extensive analysis
  - MCP server slowdown
  - Resource exhaustion

recovery:
  action: PARTIAL_RESULT
  strategy: |
    1. Check if partial results available
    2. If yes: Use partial results, warn user
    3. If no: Offer simplified goal

fallback:
  action: SIMPLIFIED_GOAL
  prompt: |
    작업 목록 생성이 시간 초과되었습니다.

    Options:
    1. 목표를 단순화하여 재시도
    2. 부분 결과로 진행 (N개 작업 생성됨)
    3. 취소
```

### Empty Task List

```yaml
error:
  type: "EMPTY_TASK_LIST"
  description: "Brainstorm generated no tasks"

triggers:
  - Goal too vague
  - Goal not actionable
  - Analysis failure

recovery:
  action: REFINE_GOAL
  prompt: |
    작업 목록을 생성하지 못했습니다.

    현재 목표: "{goal}"

    더 구체적인 목표를 입력해주세요:
    예: "React로 로그인 폼 구현" 대신
        "이메일/비밀번호 로그인 폼을 React Hook Form으로 구현, 유효성 검증 포함"

fallback: null  # Cannot proceed without tasks
```

---

## Phase 3: Review Errors

### Partial Review Failure

```yaml
error:
  type: "PARTIAL_REVIEW_FAIL"
  description: "Some review perspectives failed"

triggers:
  - Individual perspective timeout
  - MCP server error
  - Analysis complexity exceeded

recovery:
  action: CONTINUE_PARTIAL
  strategy: |
    1. Report which perspectives completed
    2. Report which perspectives failed
    3. Allow user to proceed with partial review

output: |
  ⚠️ 일부 리뷰 관점에서 오류가 발생했습니다:

  ✅ Edge Cases - 완료 (2 gaps)
  ✅ Missing Features - 완료 (1 gap)
  ❌ Maintainability - 실패 (timeout)
  ✅ Convention Guard - 완료 (0 gaps)
  ❌ Domain Master - 실패 (MCP error)

  Options:
  1. 완료된 리뷰 결과로 진행
  2. 실패한 관점 재시도
  3. 취소

fallback:
  action: PROCEED_WITH_AVAILABLE
  message: "완료된 리뷰 결과로 진행합니다."
```

### MCP Server Error

```yaml
error:
  type: "MCP_SERVER_ERROR"
  description: "MCP server communication failed"

affected_servers:
  - sequential
  - context7
  - serena

recovery:
  action: FALLBACK_TO_NATIVE
  strategy: |
    Sequential → Native multi-step reasoning
    Context7 → Cached patterns + WebSearch
    Serena → Session-only context

message: |
  MCP 서버 연결 실패. 대체 방법을 사용합니다.
  (일부 기능이 제한될 수 있습니다)
```

### Domain Expert Unavailable

```yaml
error:
  type: "DOMAIN_EXPERT_UNAVAILABLE"
  description: "Specified domain expert not found"

triggers:
  - Invalid domain specified
  - Custom domain not configured
  - Domain configuration corrupted

recovery:
  action: FALLBACK_TO_GENERAL
  prompt: |
    지정된 도메인 전문가를 찾을 수 없습니다: "{domain}"

    사용 가능한 도메인:
    - security, fintech, healthcare, ecommerce, ai-ml, gaming

    Options:
    1. General 전문가로 진행
    2. 다른 도메인 선택
    3. 취소

fallback:
  action: USE_GENERAL_EXPERT
  message: "General domain expert를 사용합니다."
```

---

## Phase 4-5: Approval/Finalize Errors

### User Approval Timeout

```yaml
error:
  type: "APPROVAL_TIMEOUT"
  description: "User did not respond to approval request"
  timeout: 300s  # 5 minutes

recovery:
  action: PRESERVE_STATE
  strategy: |
    1. Save current state to session
    2. Allow resume later
    3. Provide resume command

message: |
  승인 대기 시간이 초과되었습니다.

  현재 상태가 저장되었습니다.
  나중에 재개하려면: /planning --resume

  또는 기본 옵션으로 진행:
  /planning --resume --auto-approve
```

### Invalid Approval Input

```yaml
error:
  type: "INVALID_APPROVAL_INPUT"
  description: "User provided invalid approval selection"

triggers:
  - Invalid gap numbers
  - Unrecognized command
  - Out of range selection

recovery:
  action: RETRY_INPUT
  max_retries: 3
  prompt: |
    입력을 인식하지 못했습니다.

    유효한 입력:
    • all - 전체 승인
    • none - 전체 거부
    • 1,3,5 - 특정 항목 승인 (쉼표로 구분)
    • 1-5 - 범위 승인

    다시 입력해주세요:
```

### TodoWrite Update Failure

```yaml
error:
  type: "TODOWRITE_UPDATE_FAIL"
  description: "Failed to update TodoWrite with approved gaps"

triggers:
  - TodoWrite tool error
  - State corruption
  - Concurrent modification

recovery:
  action: RETRY_WITH_BACKUP
  strategy: |
    1. Save backup of approved gaps
    2. Retry TodoWrite update
    3. If fail: Provide manual add instructions

fallback:
  action: MANUAL_INSTRUCTIONS
  message: |
    TodoWrite 업데이트에 실패했습니다.

    승인된 작업을 수동으로 추가해주세요:

    추가할 작업:
    1. 네트워크 오류 재시도 로직
    2. 동시 로그인 처리
    3. 비밀번호 강도 검증 UI

    또는 다시 시도: /planning --resume --retry-update
```

---

## Global Error Handlers

### Session State Corruption

```yaml
error:
  type: "SESSION_STATE_CORRUPT"
  description: "Planning session state is corrupted"

recovery:
  action: RESET_AND_RETRY
  strategy: |
    1. Backup any salvageable state
    2. Reset planning session
    3. Offer to restart from beginning

message: |
  세션 상태가 손상되었습니다.

  Options:
  1. 처음부터 다시 시작
  2. 마지막 체크포인트에서 복구 시도
  3. 취소
```

### Resource Exhaustion

```yaml
error:
  type: "RESOURCE_EXHAUSTION"
  description: "System resources exhausted"

triggers:
  - Context window full
  - Memory limit reached
  - API rate limit

recovery:
  action: REDUCE_AND_RETRY
  strategy: |
    1. Reduce context (summarize history)
    2. Simplify goal
    3. Retry with reduced scope

message: |
  리소스 한계에 도달했습니다.

  자동으로 컨텍스트를 축소하고 재시도합니다...
```

---

## Error Reporting Format

### Standard Error Output

```
┌─────────────────────────────────────────────────────────────────┐
│  ⚠️ PLANNING ERROR                                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Error Type: {ERROR_TYPE}                                       │
│  Phase: {CURRENT_PHASE}                                         │
│  Description: {ERROR_DESCRIPTION}                               │
│                                                                 │
│  Recovery Options:                                              │
│  1. {OPTION_1}                                                  │
│  2. {OPTION_2}                                                  │
│  3. {OPTION_3}                                                  │
│                                                                 │
│  Fallback: {FALLBACK_ACTION}                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Debug Information

When `--debug` flag is used:

```
[DEBUG] Planning Error Details
├── Error Type: BRAINSTORM_TIMEOUT
├── Phase: 2 (Brainstorm)
├── Timestamp: 2024-01-15T10:30:45Z
├── Duration: 125.3s (timeout: 120s)
├── Goal: "복잡한 마이크로서비스 구현"
├── Context Files: 3 loaded
├── Queue Status: running
├── MCP Servers: sequential (ok), context7 (ok)
├── Partial Results: 5 tasks generated
└── Stack Trace: [truncated]
```

---

## Recovery State Management

### State Checkpoints

```yaml
checkpoints:
  phase_1_complete:
    saved: [goal, domain, context_summary]

  phase_2_complete:
    saved: [task_list, brainstorm_context]

  phase_3_complete:
    saved: [gaps, review_results]

  phase_4_pending:
    saved: [approval_request, user_options]
```

### Resume Command

```bash
# Resume from last checkpoint
/planning --resume

# Resume with specific options
/planning --resume --auto-approve
/planning --resume --retry-from phase_2
/planning --resume --skip-failed-perspectives
```
