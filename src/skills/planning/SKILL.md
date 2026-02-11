---
name: planning
description: Automated task planning with multi-perspective review. Generates comprehensive task lists via brainstorming, then validates through 5-perspective review (Edge Cases, Missing Features, Maintainability, Convention Guard, Domain Master) with user approval workflow.
---

# Overview

The `/planning` skill orchestrates comprehensive task planning by:

1. **Brainstorming**: Automatically triggers `/sc:brainstorm` to generate task list
2. **Multi-Perspective Review**: Validates through 5 expert perspectives
3. **Gap Detection**: Identifies missing tasks, edge cases, and convention violations
4. **User Approval**: Presents findings for selective approval
5. **Finalization**: Updates TodoWrite with approved additions

**When Claude should use this skill:**
- User wants comprehensive task planning for a goal
- User mentions "planning", "plan", "task list", "작업 목록"
- Complex projects requiring thorough gap analysis
- After `/sc:brainstorm` when validation is needed

# Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                        /planning ORCHESTRATOR                       │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  User Goal ───▶ /sc:brainstorm ───▶ Task List Draft                │
│                                           │                         │
│                                           ▼                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              MULTI-PERSPECTIVE REVIEW ENGINE                 │   │
│  ├─────────────────────────────────────────────────────────────┤   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌────────┐ │   │
│  │  │  Edge   │ │ Missing │ │ Maintain│ │Convention│ │ Domain │ │   │
│  │  │  Cases  │ │ Features│ │ ability │ │  Guard   │ │ Master │ │   │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬─────┘ └───┬────┘ │   │
│  │       │           │           │           │           │       │   │
│  │       └───────────┴───────────┴───────────┴───────────┘       │   │
│  │                              │                                 │   │
│  │                              ▼                                 │   │
│  │                    GAP DETECTION ENGINE                        │   │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                 │                                   │
│                                 ▼                                   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    USER APPROVAL FLOW                        │   │
│  │  ┌──────────────┬──────────────┬──────────────┐             │   │
│  │  │ 전체 승인    │  선택 승인    │    거부      │             │   │
│  │  │ (All Accept) │ (Selective)  │  (Reject)    │             │   │
│  │  └──────┬───────┴──────┬───────┴──────┬───────┘             │   │
│  └─────────┼──────────────┼──────────────┼─────────────────────┘   │
│            │              │              │                          │
│            ▼              ▼              ▼                          │
│      Add All Items   Add Selected   Keep Original                   │
│            │              │              │                          │
│            └──────────────┴──────────────┘                          │
│                           │                                         │
│                           ▼                                         │
│                 FINALIZE TodoWrite                                  │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

# Usage

```bash
# Basic usage
/planning "사용자 인증 시스템 구현"

# With context files
/planning "결제 기능 추가" @requirements.md @existing-code.ts

# Skip brainstorm (review existing todos only)
/planning --review-only

# Skip auto-review (manual review later)
/planning "feature" --no-review

# Specify domain expert
/planning "의료 데이터 처리" --domain healthcare
```

# Pipeline Phases

## Phase 1: Goal Analysis

Analyze user's goal to determine:
- Scope and complexity
- Domain classification (for Domain Master selection)
- Context files to include
- Existing project patterns

**Output:**
```
[Phase 1: Goal Analysis]
✅ Goal: "사용자 인증 시스템 구현"
✅ Scope: Module-level implementation
✅ Domain: Authentication/Security
✅ Context: 2 files referenced
```

## Phase 2: Brainstorm Execution

Queue and execute `/sc:brainstorm` to generate initial task list.

**Process:**
1. Format goal with optimal prompting
2. Execute `/sc:brainstorm` via queue
3. Capture generated task list
4. Store in TodoWrite

**Auto-Generated Prompt Template:**
```
다음 목표를 위한 작업 목록을 최대한 꼼꼼하게 파악하여, 구체적으로 추가해주세요.

목표: {user_goal}

고려사항:
- Edge cases 및 예외 처리
- 테스트 및 검증 단계
- 보안 및 에러 처리
- 문서화 및 커뮤니케이션
- 리팩토링 및 코드 품질
- 배포 및 운영 고려사항

컨텍스트:
{context_files}
```

**Output:**
```
[Phase 2: Brainstorm]
✅ Prompt generated and queued
✅ /sc:brainstorm executed
✅ 12 tasks generated
✅ Tasks stored in TodoWrite
```

## Phase 3: Multi-Perspective Review

Execute 5-perspective review on generated task list.

See [REVIEW_CRITERIA.md](./REVIEW_CRITERIA.md) for detailed criteria.

**Review Perspectives:**

| # | Perspective | Focus Area | Key Questions |
|---|-------------|------------|---------------|
| 1 | Edge Cases | 예외/경계 조건 | "What could go wrong?" |
| 2 | Missing Features | 기능 완성도 | "What else is needed?" |
| 3 | Maintainability | 유지보수성 | "Is refactoring planned?" |
| 4 | Convention Guard | 규칙 준수 | "Will conventions be followed?" |
| 5 | Domain Master | 전문가 관점 | "Is this professionally adequate?" |

**Output:**
```
[Phase 3: Multi-Perspective Review]

🔧 Edge Cases (2 gaps found)
  - Missing: 네트워크 오류 시 재시도 로직
  - Missing: 동시 로그인 처리

📦 Missing Features (1 gap found)
  - Missing: 비밀번호 강도 검증 UI

🔄 Maintainability (2 gaps found)
  - Missing: 레거시 인증 코드 리팩토링
  - Missing: 테스트 커버리지 목표 설정

🛡️ Convention Guard (1 gap found)
  - Missing: 에러 메시지 i18n 처리

🎓 Domain Master [Security] (1 gap found)
  - Missing: OWASP 인증 가이드라인 검토
```

## Phase 4: User Approval

Present gaps to user with approval options.

**Approval Interface:**
```
┌─────────────────────────────────────────────────────────────┐
│  📊 PLANNING REVIEW REPORT                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Original Tasks: 12                                         │
│  Gaps Found: 7                                              │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ # │ Gap                           │ Source        │ Add?││
│  ├───┼───────────────────────────────┼───────────────┼─────┤│
│  │ 1 │ 네트워크 오류 재시도 로직      │ Edge Cases    │ [ ] ││
│  │ 2 │ 동시 로그인 처리               │ Edge Cases    │ [ ] ││
│  │ 3 │ 비밀번호 강도 검증 UI          │ Features      │ [ ] ││
│  │ 4 │ 레거시 인증 코드 리팩토링       │ Maintainability│ [ ] ││
│  │ 5 │ 테스트 커버리지 목표 설정       │ Maintainability│ [ ] ││
│  │ 6 │ 에러 메시지 i18n 처리          │ Convention    │ [ ] ││
│  │ 7 │ OWASP 인증 가이드라인 검토     │ Domain Master │ [ ] ││
│  └─────────────────────────────────────────────────────────┘│
│                                                             │
│  Options:                                                   │
│  • 전체 승인 (all) - Add all 7 gaps                        │
│  • 선택 승인 (1,3,5) - Add specific items                  │
│  • 거부 (none) - Keep original 12 tasks only               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Phase 5: Finalize

Update TodoWrite with approved additions.

**Output:**
```
[Phase 5: Finalize]
✅ 5 gaps approved by user
✅ TodoWrite updated: 12 → 17 tasks
✅ Planning complete

📋 Final Task List:
1. [pending] 기존 인증 흐름 분석
2. [pending] JWT 토큰 구조 설계
...
17. [pending] OWASP 인증 가이드라인 검토
```

# Domain Expert Selection

## Auto-Detection

Domain is inferred from goal keywords:

| Keywords | Domain | Expert Focus |
|----------|--------|--------------|
| 인증, 보안, 암호화, OAuth | security | OWASP, 취약점 분석 |
| 결제, 금융, 거래 | fintech | PCI-DSS, 금융 규제 |
| 의료, 건강, 환자 | healthcare | HIPAA, 의료 데이터 규정 |
| 쇼핑몰, 이커머스, 주문 | ecommerce | UX, 전환율 최적화 |
| AI, ML, 데이터 | ai-ml | 모델 성능, 데이터 품질 |
| 게임, 멀티플레이어 | gaming | 레이턴시, 동기화 |

## Manual Override

```bash
/planning "기능 구현" --domain healthcare
```

## Domain Expert Handoff

See [DOMAIN_EXPERTS.md](./DOMAIN_EXPERTS.md) for:
- Expert persona definitions
- Project-specific customization
- Handoff protocol

# Convention Tracking

## New Rule Detection

The Convention Guard perspective checks:

1. **Existing Conventions**: CLAUDE.md, RULES.md, project patterns
2. **New Rules in Code**: Recently added patterns that should be followed
3. **Context Loss Risk**: Tasks that might violate conventions when context is lost

See [CONVENTION_TRACKER.md](./CONVENTION_TRACKER.md) for:
- Rule detection algorithm
- Convention inheritance
- Context preservation strategies

# Queue Integration

## Auto-Execution Flow

When `/planning` is invoked:

```yaml
queue_sequence:
  - step: 1
    command: "/sc:brainstorm {goal}"
    on_complete: proceed
    on_fail: report_and_stop

  - step: 2
    command: "INTERNAL:multi_perspective_review"
    on_complete: proceed
    on_fail: partial_review

  - step: 3
    command: "INTERNAL:user_approval_flow"
    on_complete: proceed
    on_fail: keep_original

  - step: 4
    command: "INTERNAL:finalize_todowrite"
    on_complete: complete
    on_fail: rollback
```

See [MODE_Task_Queue.md](../../MODE_Task_Queue.md) for queue system integration.

# Error Handling

## Brainstorm Failure

```yaml
action: PAUSE
recovery:
  - Retry with simplified goal
  - Fall back to manual task entry
  - Report error and continue with review-only
```

## Review Partial Failure

```yaml
action: CONTINUE_PARTIAL
recovery:
  - Skip failed perspective
  - Report which perspectives completed
  - Allow user to proceed with partial review
```

## Approval Timeout

```yaml
action: PRESERVE_STATE
recovery:
  - Save current state
  - Allow resume with /planning --resume
  - Auto-apply defaults after 5 minutes
```

See [ERROR_HANDLING.md](./ERROR_HANDLING.md) for full error scenarios.

# Examples

## Basic Planning

```
User: /planning "사용자 인증 시스템 구현"

Claude:
[Phase 1: Goal Analysis]
✅ Goal: 사용자 인증 시스템 구현
✅ Domain: Security (auto-detected)

[Phase 2: Brainstorm] ⏳ Queued
→ /sc:brainstorm executing...
✅ 12 tasks generated

[Phase 3: Multi-Perspective Review]
🔧 Edge Cases: 2 gaps
📦 Missing Features: 1 gap
🔄 Maintainability: 2 gaps
🛡️ Convention Guard: 1 gap
🎓 Domain Master [Security]: 1 gap

Total: 7 gaps found

[Phase 4: User Approval]
Select options: (all / 1,2,3 / none)

User: all

[Phase 5: Finalize]
✅ 7 gaps added
✅ Final: 19 tasks in TodoWrite
```

## With Context Files

```
User: /planning "결제 시스템 리팩토링" @payment.ts @types.d.ts

Claude:
[Phase 1: Goal Analysis]
✅ Goal: 결제 시스템 리팩토링
✅ Domain: Fintech (auto-detected)
✅ Context: 2 files loaded

[Phase 2: Brainstorm]
✅ 15 tasks generated (context-aware)

[Phase 3: Review]
...
```

## Review Only (Existing Todos)

```
User: /planning --review-only

Claude:
[Skip Phase 1-2]

[Phase 3: Review]
Reviewing existing 10 tasks...

🔧 Edge Cases: 3 gaps
📦 Missing Features: 2 gaps
...
```

## Selective Approval

```
User: 1,3,5

Claude:
[Phase 5: Finalize]
✅ Selected 3 of 7 gaps
✅ Added: 네트워크 오류 재시도, 비밀번호 강도 검증 UI, 테스트 커버리지 목표
✅ Final: 15 tasks
```

# Boundaries

**Will:**
- Auto-trigger `/sc:brainstorm` for goal-based planning
- Execute 5-perspective review automatically
- Detect domain and assign appropriate expert
- Track new conventions from recent code
- Present gaps with clear approval workflow
- Integrate with queue system for sequencing
- Support context files for better analysis
- Allow selective approval of gaps

**Will Not:**
- Add gaps without user approval (except `--auto-approve` flag)
- Skip any review perspective without explicit flag
- Override user's rejection of gaps
- Push changes to git (separate commit workflow)
- Modify code directly (planning only)
- Replace `/sc:brainstorm` (uses it internally)
