---
name: planning
description: "Automated task planning with multi-perspective review. Generates comprehensive task lists via brainstorming, then validates through 5-perspective review (Edge Cases, Missing Features, Maintainability, Convention Guard, Domain Master) with user approval workflow."
category: orchestration
complexity: advanced
mcp-servers: [sequential, context7, serena]
personas: [analyzer, architect, security, project-manager]
---

# /planning - Automated Task Planning with Multi-Perspective Review

> **Context Framework Note**: This file provides behavioral instructions for Claude Code when users type `/planning` patterns. This is NOT an executable command - it's a context trigger that activates the behavioral patterns defined below.

## Triggers
- Comprehensive task planning for a goal
- Keywords: "planning", "plan", "작업 목록", "task list"
- Complex projects requiring thorough gap analysis
- After `/sc:brainstorm` when validation is needed

## Context Trigger Pattern
```
/planning "goal description" [@context_files] [--domain domain_name] [--review-only] [--no-review]
```
**Usage**: Type this pattern in your Claude Code conversation to activate automated task planning with multi-perspective review.

## Behavioral Flow

```
┌────────────────────────────────────────────────────────────────────┐
│  /planning "목표"                                                  │
└──────────────────┬─────────────────────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────────────────┐
│  Phase 1: GOAL ANALYSIS                                            │
│  └─▶ Analyze scope, detect domain, load context                   │
└──────────────────┬─────────────────────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────────────────┐
│  Phase 2: BRAINSTORM (AUTO-QUEUED)                                 │
│  └─▶ Execute /sc:brainstorm with optimized prompt                 │
│  └─▶ Generate initial task list → TodoWrite                       │
└──────────────────┬─────────────────────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────────────────┐
│  Phase 3: MULTI-PERSPECTIVE REVIEW                                 │
│  ├─▶ 🔧 Edge Cases: Exception handling, boundary conditions       │
│  ├─▶ 📦 Missing Features: Functional completeness                 │
│  ├─▶ 🔄 Maintainability: Refactoring, testing, documentation     │
│  ├─▶ 🛡️ Convention Guard: Rule compliance, new patterns          │
│  └─▶ 🎓 Domain Master: Professional adequacy                      │
└──────────────────┬─────────────────────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────────────────┐
│  Phase 4: USER APPROVAL                                            │
│  └─▶ Present gaps with options: 전체 승인 / 선택 승인 / 거부      │
└──────────────────┬─────────────────────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────────────────┐
│  Phase 5: FINALIZE                                                 │
│  └─▶ Update TodoWrite with approved additions                     │
└────────────────────────────────────────────────────────────────────┘
```

## 5 Review Perspectives

| # | Perspective | Icon | Focus Area | Key Questions |
|---|-------------|------|------------|---------------|
| 1 | Edge Cases | 🔧 | 예외/경계 조건 | "What could go wrong?" |
| 2 | Missing Features | 📦 | 기능 완성도 | "What else is needed?" |
| 3 | Maintainability | 🔄 | 유지보수성 | "Is refactoring planned?" |
| 4 | Convention Guard | 🛡️ | 규칙 준수 | "Will conventions be followed?" |
| 5 | Domain Master | 🎓 | 전문가 관점 | "Is this professionally adequate?" |

## MCP Integration
- **Sequential MCP**: Complex multi-step reasoning for gap analysis
- **Context7 MCP**: Framework patterns and best practices lookup
- **Serena MCP**: Cross-session persistence and project context

## Tool Coordination
- **TodoWrite**: Task list management and progress tracking
- **Task**: Delegation for `/sc:brainstorm` execution
- **Read/Write/Edit**: Documentation and context file handling
- **AskUserQuestion**: Approval workflow interaction

## Domain Expert Selection

Domains are auto-detected from goal keywords or manually specified:

| Domain | Keywords | Expert Focus |
|--------|----------|--------------|
| security | 인증, 보안, OAuth | OWASP, 취약점 분석 |
| fintech | 결제, 금융, 거래 | PCI-DSS, 감사 로그 |
| healthcare | 의료, 환자, 건강 | HIPAA, 데이터 규정 |
| ecommerce | 쇼핑몰, 주문, 장바구니 | UX, 전환율 최적화 |
| ai-ml | AI, ML, 모델 | MLOps, 데이터 품질 |
| gaming | 게임, 멀티플레이어 | 실시간, 동기화 |

## Examples

### Basic Planning
```
/planning "사용자 인증 시스템 구현"

# Output:
[Phase 1] Goal: 사용자 인증 시스템, Domain: Security
[Phase 2] /sc:brainstorm executed, 12 tasks generated
[Phase 3] Review found 7 gaps
[Phase 4] User approval requested
[Phase 5] Final: 19 tasks
```

### With Context Files
```
/planning "결제 시스템 리팩토링" @payment.ts @types.d.ts

# Context-aware planning with file analysis
```

### Specify Domain
```
/planning "의료 데이터 처리 기능" --domain healthcare

# Healthcare domain expert activated with HIPAA focus
```

### Review Only
```
/planning --review-only

# Skip brainstorm, review existing TodoWrite tasks
```

## Flags

| Flag | Description | Example |
|------|-------------|---------|
| `--domain` | Force specific domain expert | `--domain fintech` |
| `--review-only` | Review existing tasks only | Skip brainstorm phase |
| `--no-review` | Skip auto-review | Manual review later |
| `--auto-approve` | Auto-add all gaps | No user confirmation |

## User Approval Interface

```
┌─────────────────────────────────────────────────────────────────┐
│  📊 PLANNING REVIEW REPORT                                      │
├─────────────────────────────────────────────────────────────────┤
│  Original Tasks: 12 │ Gaps Found: 7                             │
│                                                                 │
│  # │ Gap                          │ Source          │ Priority │
│  ──┼──────────────────────────────┼─────────────────┼──────────│
│  1 │ 네트워크 오류 재시도 로직     │ Edge Cases      │ High     │
│  2 │ 비밀번호 강도 검증 UI        │ Missing Features│ Medium   │
│  3 │ 레거시 코드 리팩토링          │ Maintainability │ Medium   │
│  4 │ 에러 메시지 i18n             │ Convention Guard│ Low      │
│  5 │ OWASP 가이드라인 검토        │ Domain Master   │ High     │
│                                                                 │
│  Options:                                                       │
│  • 전체 승인 (all)                                              │
│  • 선택 승인 (1,3,5)                                            │
│  • 거부 (none)                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Queue Integration

When `/planning` is invoked, it automatically queues:

1. `/sc:brainstorm "{goal}"` - Generate initial task list
2. `INTERNAL:multi_perspective_review` - Execute 5-perspective review
3. `INTERNAL:user_approval` - Present gaps for approval
4. `INTERNAL:finalize` - Update TodoWrite

See [MODE_Task_Queue.md](../../MODE_Task_Queue.md) for queue system details.

## Related Commands

| Command | Relationship |
|---------|--------------|
| `/sc:brainstorm` | Used internally for task generation |
| `/sc:implement` | Execute tasks after planning |
| `/sc:reflect` | Validate task completion |

## Skill Documentation

Full documentation available at:
- `~/.claude/skills/planning/SKILL.md` - Main skill definition
- `~/.claude/skills/planning/REVIEW_CRITERIA.md` - Review criteria details
- `~/.claude/skills/planning/DOMAIN_EXPERTS.md` - Domain expert registry
- `~/.claude/skills/planning/CONVENTION_TRACKER.md` - Convention tracking

## Boundaries

**Will:**
- Auto-trigger `/sc:brainstorm` for goal-based planning
- Execute 5-perspective review automatically
- Detect domain and assign appropriate expert
- Track new conventions from recent code
- Present gaps with clear approval workflow
- Support selective approval of gaps

**Will Not:**
- Add gaps without user approval (except `--auto-approve`)
- Skip review perspectives without explicit flag
- Override user's rejection of gaps
- Push changes to git (separate commit workflow)
- Modify code directly (planning only)
