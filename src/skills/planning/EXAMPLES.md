# Planning Skill Examples

This document provides comprehensive usage examples for the `/planning` skill.

---

## Basic Usage

### Example 1: Simple Feature Planning

```
User: /planning "사용자 프로필 수정 기능 구현"

Claude:
┌─────────────────────────────────────────────────────────────────┐
│  [Phase 1: Goal Analysis]                                       │
├─────────────────────────────────────────────────────────────────┤
│  ✅ Goal: 사용자 프로필 수정 기능 구현                           │
│  ✅ Scope: Feature-level implementation                         │
│  ✅ Domain: General (no specific domain detected)               │
│  ✅ Context: No additional files                                │
└─────────────────────────────────────────────────────────────────┘

[Phase 2: Brainstorm] ⏳ Queued
→ Executing /sc:brainstorm with optimized prompt...

프롬프트:
"다음 목표를 위한 작업 목록을 최대한 꼼꼼하게 파악하여, 구체적으로 추가해주세요.
목표: 사용자 프로필 수정 기능 구현
고려사항: Edge cases, 테스트, 보안, 문서화, 리팩토링, 배포"

✅ 8 tasks generated:
1. [pending] 기존 프로필 API 분석
2. [pending] 프로필 수정 API 엔드포인트 설계
3. [pending] 프로필 수정 폼 UI 구현
4. [pending] 이미지 업로드 기능 구현
5. [pending] 입력값 유효성 검증
6. [pending] API 연동 및 에러 처리
7. [pending] 단위 테스트 작성
8. [pending] 통합 테스트 작성

┌─────────────────────────────────────────────────────────────────┐
│  [Phase 3: Multi-Perspective Review]                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🔧 Edge Cases (2 gaps found)                                   │
│     • 이미지 업로드 실패 시 롤백 처리 누락                        │
│     • 동시 수정 충돌(Race condition) 처리 누락                    │
│                                                                 │
│  📦 Missing Features (1 gap found)                              │
│     • 프로필 수정 성공/실패 알림 UI 누락                          │
│                                                                 │
│  🔄 Maintainability (1 gap found)                               │
│     • 기존 프로필 관련 코드 리팩토링 계획 없음                     │
│                                                                 │
│  🛡️ Convention Guard (0 gaps)                                   │
│     ✅ All convention checks passed                              │
│                                                                 │
│  🎓 Domain Master [General] (0 gaps)                            │
│     ✅ Standard implementation, no domain-specific concerns      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  [Phase 4: User Approval]                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Original Tasks: 8  │  Gaps Found: 4                            │
│                                                                 │
│  # │ Gap                              │ Source        │ Priority│
│  ──┼──────────────────────────────────┼───────────────┼─────────│
│  1 │ 이미지 업로드 실패 롤백 처리       │ Edge Cases    │ High    │
│  2 │ 동시 수정 충돌 처리                │ Edge Cases    │ Medium  │
│  3 │ 성공/실패 알림 UI                 │ Features      │ Medium  │
│  4 │ 기존 코드 리팩토링                 │ Maintainability│ Low    │
│                                                                 │
│  Options: 전체 승인(all) / 선택 승인(1,2,3) / 거부(none)         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

User: all

[Phase 5: Finalize]
✅ 4 gaps approved
✅ TodoWrite updated: 8 → 12 tasks

📋 Final Task List:
 1. [pending] 기존 프로필 API 분석
 2. [pending] 프로필 수정 API 엔드포인트 설계
 3. [pending] 프로필 수정 폼 UI 구현
 4. [pending] 이미지 업로드 기능 구현
 5. [pending] 이미지 업로드 실패 롤백 처리 ← NEW
 6. [pending] 동시 수정 충돌 처리 ← NEW
 7. [pending] 입력값 유효성 검증
 8. [pending] 성공/실패 알림 UI ← NEW
 9. [pending] API 연동 및 에러 처리
10. [pending] 단위 테스트 작성
11. [pending] 통합 테스트 작성
12. [pending] 기존 프로필 코드 리팩토링 ← NEW

✅ Planning complete!
```

---

## Domain-Specific Planning

### Example 2: Security Domain

```
User: /planning "OAuth 2.0 로그인 구현"

Claude:
[Phase 1: Goal Analysis]
✅ Goal: OAuth 2.0 로그인 구현
✅ Domain: Security (auto-detected from "OAuth", "로그인")
✅ Expert: 🔐 Security Expert activated

[Phase 2: Brainstorm]
✅ 10 tasks generated (security-aware)

[Phase 3: Multi-Perspective Review]

🔧 Edge Cases (3 gaps)
  • 토큰 만료 시 자동 갱신 처리
  • OAuth 제공자 장애 시 fallback
  • 세션 하이재킹 방지

📦 Missing Features (1 gap)
  • 로그인 실패 횟수 제한(Rate limiting)

🔄 Maintainability (1 gap)
  • 기존 인증 코드와 통합 테스트

🛡️ Convention Guard (1 gap)
  • 토큰 저장 방식 보안 가이드라인 준수

🎓 Domain Master [Security] (3 gaps)
  • OWASP 인증 가이드라인 검토 작업 없음
  • CSRF 방어 구현 작업 없음
  • 보안 로깅 구현 작업 없음

Total: 9 gaps found

[Phase 4: User Approval]
# │ Gap                              │ Source          │ Priority
──┼──────────────────────────────────┼─────────────────┼─────────
1 │ 토큰 만료 자동 갱신               │ Edge Cases      │ High
2 │ OAuth 제공자 장애 fallback        │ Edge Cases      │ High
3 │ 세션 하이재킹 방지                 │ Edge Cases      │ Critical
4 │ 로그인 실패 횟수 제한              │ Features        │ High
5 │ 기존 인증 코드 통합 테스트         │ Maintainability │ Medium
6 │ 토큰 저장 보안 가이드라인          │ Convention      │ High
7 │ OWASP 인증 가이드라인 검토        │ Domain Master   │ High
8 │ CSRF 방어 구현                    │ Domain Master   │ Critical
9 │ 보안 로깅 구현                    │ Domain Master   │ Medium

User: 1,2,3,4,6,7,8

[Phase 5: Finalize]
✅ 7 of 9 gaps approved
✅ Final: 17 tasks
```

### Example 3: Fintech Domain

```
User: /planning "결제 시스템 구현" --domain fintech

Claude:
[Phase 1: Goal Analysis]
✅ Goal: 결제 시스템 구현
✅ Domain: Fintech (explicitly specified)
✅ Expert: 💰 Fintech Expert activated
✅ Standards: PCI-DSS, SOC 2

[Phase 3: Multi-Perspective Review]

🎓 Domain Master [Fintech] (5 gaps)
  • 거래 원자성(ACID) 보장 작업 없음
  • 중복 결제 방지(Idempotency) 작업 없음
  • 감사 로그 구현 작업 없음
  • 정산(Settlement) 로직 작업 없음
  • PCI-DSS 준수 검토 작업 없음

... (continues with full review)
```

---

## Context-Aware Planning

### Example 4: With Context Files

```
User: /planning "API 리팩토링" @src/api/users.ts @src/types/user.d.ts

Claude:
[Phase 1: Goal Analysis]
✅ Goal: API 리팩토링
✅ Context Files: 2 files loaded
  • src/api/users.ts (342 lines)
  • src/types/user.d.ts (45 lines)
✅ Detected Patterns:
  • Express.js API structure
  • TypeScript strict mode
  • Custom error handling pattern

[Phase 2: Brainstorm]
→ Context-aware brainstorming...

Prompt includes:
"기존 코드 분석 결과:
- Express.js 기반 REST API
- 커스텀 에러 핸들러 사용 (AppError 클래스)
- 응답 포맷: { success, data, error }
- 기존 패턴을 유지하면서 리팩토링해야 함"

✅ 12 tasks generated (context-aware)

[Phase 3: Multi-Perspective Review]

🛡️ Convention Guard (3 gaps)
  • 기존 응답 포맷 유지 확인 작업 없음
  • AppError 패턴 일관성 검증 작업 없음
  • 새로운 헬퍼 함수 문서화 작업 없음

...
```

---

## Review-Only Mode

### Example 5: Review Existing Tasks

```
User: /planning --review-only

Claude:
[Skip Phase 1-2]

Loading existing TodoWrite tasks...
Found 15 tasks in current todo list.

[Phase 3: Multi-Perspective Review]

Reviewing existing tasks:
1. [pending] 사용자 CRUD API 구현
2. [pending] 인증 미들웨어 구현
3. [in_progress] 데이터베이스 스키마 설계
4. [pending] 프론트엔드 로그인 폼
...

🔧 Edge Cases (2 gaps)
  • Task #1: API 입력 검증 작업 없음
  • Task #2: 토큰 갱신 에러 처리 없음

📦 Missing Features (1 gap)
  • 전체: 에러 응답 표준화 작업 없음

🔄 Maintainability (2 gaps)
  • 테스트 커버리지 목표 설정 작업 없음
  • API 문서화(Swagger) 작업 없음

🛡️ Convention Guard (1 gap)
  • Task #3에서 발생한 새 스키마 패턴 문서화 없음

🎓 Domain Master [General] (0 gaps)
  ✅ No domain-specific concerns

Total: 6 gaps found for existing 15 tasks

[Phase 4: User Approval]
...
```

---

## Selective Approval

### Example 6: Partial Approval

```
User: /planning "마이크로서비스 분리"

Claude:
[Phase 3: Review Complete]
Total: 12 gaps found

[Phase 4: User Approval]
# │ Gap                              │ Source          │ Priority
──┼──────────────────────────────────┼─────────────────┼─────────
 1 │ 서비스 간 통신 프로토콜 정의      │ Edge Cases      │ High
 2 │ Circuit breaker 패턴 구현        │ Edge Cases      │ High
 3 │ 분산 트랜잭션 처리               │ Edge Cases      │ Critical
 4 │ 서비스 디스커버리 설정            │ Features        │ High
 5 │ API Gateway 설정                │ Features        │ Medium
 6 │ 공유 라이브러리 추출              │ Maintainability │ Medium
 7 │ 모노레포 설정                    │ Maintainability │ Low
 8 │ 서비스별 CLAUDE.md 작성          │ Convention      │ Medium
 9 │ 새 폴더 구조 문서화               │ Convention      │ Low
10 │ k8s 배포 전략 수립               │ Domain Master   │ High
11 │ 서비스 메시 도입 검토              │ Domain Master   │ Medium
12 │ 장애 복구 테스트 계획              │ Domain Master   │ High

User: 1,2,3,4,10,12

Claude:
[Phase 5: Finalize]
✅ 6 of 12 gaps approved

Added tasks:
• 서비스 간 통신 프로토콜 정의 (Priority: High)
• Circuit breaker 패턴 구현 (Priority: High)
• 분산 트랜잭션 처리 (Priority: Critical)
• 서비스 디스커버리 설정 (Priority: High)
• k8s 배포 전략 수립 (Priority: High)
• 장애 복구 테스트 계획 (Priority: High)

Rejected (not added):
• API Gateway 설정
• 공유 라이브러리 추출
• 모노레포 설정
• 서비스별 CLAUDE.md 작성
• 새 폴더 구조 문서화
• 서비스 메시 도입 검토

✅ Final: Original 18 + Added 6 = 24 tasks
```

---

## Error Recovery

### Example 7: Brainstorm Failure

```
User: /planning "복잡한 기능 구현"

Claude:
[Phase 2: Brainstorm]
⚠️ /sc:brainstorm execution failed

Error: Context too complex, unable to generate comprehensive task list

Recovery Options:
1. [R]etry with simplified goal
2. [M]anual task entry
3. [S]kip to review-only mode

User: R

Claude:
Simplified goal prompt:
"기본적인 CRUD 기능 위주로 작업 목록 생성"

[Retry] /sc:brainstorm executing...
✅ 6 tasks generated (simplified)

Proceeding with review phase...
```

---

## Quick Reference

### Command Variations

```bash
# Basic
/planning "goal"

# With context
/planning "goal" @file1.ts @file2.ts

# Specify domain
/planning "goal" --domain security

# Review only
/planning --review-only

# Skip review
/planning "goal" --no-review

# Auto-approve all
/planning "goal" --auto-approve
```

### Approval Shortcuts

| Input | Action |
|-------|--------|
| `all` | Approve all gaps |
| `none` | Reject all gaps |
| `1,3,5` | Approve specific gaps |
| `1-5` | Approve range |
| `all except 3,7` | Approve all except specific |
