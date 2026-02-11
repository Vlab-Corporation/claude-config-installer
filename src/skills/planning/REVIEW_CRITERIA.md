# Multi-Perspective Review Criteria

This document defines the 5 review perspectives used by `/planning` to validate task lists.

## Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    REVIEW PERSPECTIVES                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   1. 🔧 Edge Cases        - "What could go wrong?"                  │
│   2. 📦 Missing Features  - "What else is needed?"                  │
│   3. 🔄 Maintainability   - "Is this sustainable?"                  │
│   4. 🛡️ Convention Guard  - "Will rules be followed?"               │
│   5. 🎓 Domain Master     - "Is this professionally adequate?"      │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 1. 🔧 Edge Cases Perspective

**Focus**: Exception handling, boundary conditions, failure scenarios

### Review Questions

| Category | Questions to Ask |
|----------|------------------|
| **Input Boundaries** | 빈 값, null, 최대/최소값은 처리되는가? |
| **Network Failures** | 네트워크 오류, 타임아웃 처리가 있는가? |
| **Concurrency** | 동시 접근, 레이스 컨디션은 고려되었는가? |
| **State Transitions** | 비정상 상태 전환은 방지되는가? |
| **External Dependencies** | 외부 서비스 장애 시 대응이 있는가? |
| **Data Corruption** | 데이터 손상/불일치 복구가 가능한가? |

### Gap Detection Rules

```yaml
edge_case_gaps:
  # Input validation
  - condition: "입력 검증 작업이 없음"
    check: "validate|validation|sanitize|check input"
    gap: "입력값 검증 로직 추가"

  # Error handling
  - condition: "에러 처리 작업이 없음"
    check: "error|exception|catch|try|handle"
    gap: "에러 핸들링 작업 추가"

  # Timeout handling
  - condition: "타임아웃 처리 없음"
    check: "timeout|retry|fallback"
    gap: "타임아웃 및 재시도 로직 추가"

  # Concurrent access
  - condition: "동시성 고려 없음"
    check: "lock|mutex|concurrent|atomic|transaction"
    gap: "동시 접근 처리 로직 추가"

  # Boundary conditions
  - condition: "경계값 테스트 없음"
    check: "boundary|edge|limit|max|min|overflow"
    gap: "경계값 테스트 케이스 추가"
```

### Severity Levels

| Level | Criteria | Example |
|-------|----------|---------|
| 🔴 Critical | 데이터 손실/보안 위험 | 트랜잭션 롤백 누락 |
| 🟡 High | 기능 장애 가능 | 네트워크 에러 미처리 |
| 🟢 Medium | UX 저하 가능 | 로딩 상태 미표시 |

---

## 2. 📦 Missing Features Perspective

**Focus**: Feature completeness, user requirements, functional gaps

### Review Questions

| Category | Questions to Ask |
|----------|------------------|
| **Core Features** | 핵심 기능이 모두 포함되었는가? |
| **User Flows** | 모든 사용자 시나리오가 커버되는가? |
| **CRUD Completeness** | 생성/조회/수정/삭제가 모두 있는가? |
| **Feedback** | 사용자에게 충분한 피드백이 있는가? |
| **Accessibility** | 접근성 요구사항이 충족되는가? |
| **Internationalization** | 다국어/지역화 고려가 있는가? |

### Gap Detection Rules

```yaml
feature_gaps:
  # CRUD completeness
  - condition: "생성 기능만 있고 조회/수정/삭제 없음"
    check_pattern: "create|add|insert"
    missing_pattern: "read|get|update|edit|delete|remove"
    gap: "누락된 CRUD 작업 추가"

  # User feedback
  - condition: "성공/실패 피드백 없음"
    check: "toast|notification|alert|message|feedback"
    gap: "사용자 피드백 UI 추가"

  # Loading states
  - condition: "로딩 상태 처리 없음"
    check: "loading|spinner|skeleton|pending"
    gap: "로딩 상태 UI 추가"

  # Empty states
  - condition: "빈 상태 처리 없음"
    check: "empty|no data|no results"
    gap: "빈 상태 UI 추가"

  # Search/Filter
  - condition: "목록에 검색/필터 없음"
    check: "search|filter|sort"
    gap: "검색/필터 기능 추가"

  # Pagination
  - condition: "대량 데이터에 페이지네이션 없음"
    check: "pagina|page|limit|offset|cursor"
    gap: "페이지네이션 추가"
```

### Completeness Checklist

```yaml
feature_checklist:
  api_endpoint:
    - "HTTP 메서드가 RESTful한가?"
    - "응답 형식이 일관적인가?"
    - "에러 응답이 표준화되어 있는가?"
    - "API 문서화 작업이 있는가?"

  ui_component:
    - "모든 상태(default, hover, active, disabled)가 있는가?"
    - "반응형 디자인이 고려되었는가?"
    - "키보드 네비게이션이 지원되는가?"
    - "스크린 리더 호환이 되는가?"

  data_model:
    - "필수 필드가 모두 정의되었는가?"
    - "관계(relations)가 명확한가?"
    - "인덱스 전략이 있는가?"
    - "마이그레이션 작업이 있는가?"
```

---

## 3. 🔄 Maintainability Perspective

**Focus**: Code quality, technical debt, long-term sustainability

### Review Questions

| Category | Questions to Ask |
|----------|------------------|
| **Refactoring** | 기존 코드 정리 작업이 포함되었는가? |
| **Testing** | 테스트 작성/업데이트 작업이 있는가? |
| **Documentation** | 코드/API 문서화가 계획되었는가? |
| **Code Quality** | 린트/포맷팅 적용이 있는가? |
| **Dependencies** | 의존성 업데이트가 필요한가? |
| **Technical Debt** | 기술 부채 해결이 포함되었는가? |

### Gap Detection Rules

```yaml
maintainability_gaps:
  # Testing
  - condition: "테스트 작업 없음"
    check: "test|spec|coverage"
    gap: "단위 테스트 작성 작업 추가"

  # Refactoring
  - condition: "리팩토링 계획 없음"
    check: "refactor|cleanup|reorganize|simplify"
    gap: "관련 코드 리팩토링 작업 추가"

  # Documentation
  - condition: "문서화 작업 없음"
    check: "document|readme|comment|jsdoc|docstring"
    gap: "코드/API 문서화 작업 추가"

  # Code review
  - condition: "코드 리뷰 없음"
    check: "review|PR|pull request"
    gap: "코드 리뷰 단계 추가"

  # Monitoring
  - condition: "모니터링 없음"
    check: "log|monitor|metric|trace|alert"
    gap: "로깅/모니터링 추가"

  # Performance
  - condition: "성능 고려 없음"
    check: "performance|optimize|cache|lazy"
    gap: "성능 최적화 검토 작업 추가"
```

### Technical Debt Indicators

```yaml
debt_indicators:
  high_priority:
    - "TODO/FIXME 주석이 많은 영역"
    - "테스트 커버리지가 낮은 모듈"
    - "중복 코드가 있는 영역"
    - "복잡도가 높은 함수"

  medium_priority:
    - "오래된 의존성"
    - "일관성 없는 네이밍"
    - "하드코딩된 값"

  low_priority:
    - "오래된 주석"
    - "사용되지 않는 코드"
    - "포맷팅 불일치"
```

---

## 4. 🛡️ Convention Guard Perspective

**Focus**: Rule compliance, pattern consistency, context preservation

### Review Questions

| Category | Questions to Ask |
|----------|------------------|
| **Existing Conventions** | 프로젝트 규칙이 준수되는가? |
| **New Patterns** | 새 코드에서 발생한 패턴이 문서화되는가? |
| **Naming** | 네이밍 규칙이 일관적인가? |
| **Structure** | 디렉토리/파일 구조가 규칙을 따르는가? |
| **Context Loss Risk** | 맥락 손실 시 규칙 위반 위험이 있는가? |

### Gap Detection Rules

```yaml
convention_gaps:
  # Naming conventions
  - condition: "네이밍 규칙 확인 없음"
    check: "naming|convention|style"
    gap: "네이밍 규칙 준수 검증 작업 추가"

  # Import order
  - condition: "import 정리 없음"
    check: "import|organize import|sort import"
    gap: "import 순서 정리 작업 추가"

  # Error message format
  - condition: "에러 메시지 표준화 없음"
    check: "error message|i18n|localization"
    gap: "에러 메시지 표준화 작업 추가"

  # File structure
  - condition: "파일 위치 검토 없음"
    check: "file structure|directory|organize"
    gap: "파일 구조 규칙 준수 확인 작업 추가"

  # New rule documentation
  - condition: "새 패턴 문서화 없음"
    check: "document pattern|update convention|update rule"
    gap: "새로 도입된 패턴 문서화 작업 추가"
```

### Convention Sources (Priority Order)

```yaml
convention_sources:
  1_project_claude_md:
    path: "PROJECT_ROOT/CLAUDE.md"
    priority: highest
    description: "프로젝트별 규칙"

  2_project_conventions:
    path: ".claude/CONVENTIONS.md"
    priority: high
    description: "상세 컨벤션 문서"

  3_superclaude_rules:
    path: "~/.claude/RULES.md"
    priority: medium
    description: "SuperClaude 프레임워크 규칙"

  4_language_defaults:
    path: "~/.claude/docs/conventions/"
    priority: low
    description: "언어별 기본 규칙"
```

### Context Loss Prevention

```yaml
context_loss_risks:
  high_risk_scenarios:
    - "복잡한 비즈니스 로직 구현"
    - "여러 파일에 걸친 변경"
    - "새로운 아키텍처 패턴 도입"
    - "외부 라이브러리 통합"

  prevention_tasks:
    - "구현 전 규칙 문서 확인 작업"
    - "변경 후 컨벤션 검증 작업"
    - "새 패턴 발생 시 문서화 작업"
    - "복잡한 로직 주석 작성 작업"
```

---

## 5. 🎓 Domain Master Perspective

**Focus**: Professional adequacy, domain-specific requirements, expert standards

### Domain-Specific Criteria

#### Security Domain

```yaml
security_criteria:
  questions:
    - "OWASP Top 10 취약점이 고려되었는가?"
    - "인증/인가가 적절히 구현되는가?"
    - "민감 데이터가 안전하게 처리되는가?"
    - "입력 검증이 충분한가?"

  required_tasks:
    - "보안 취약점 검토"
    - "인증 토큰 만료/갱신 처리"
    - "XSS/CSRF 방어"
    - "SQL Injection 방지"
    - "민감 데이터 암호화"

  standards:
    - "OWASP ASVS"
    - "CWE Top 25"
```

#### Fintech Domain

```yaml
fintech_criteria:
  questions:
    - "금융 규제 준수가 고려되었는가?"
    - "거래 무결성이 보장되는가?"
    - "감사 로그가 충분한가?"
    - "PCI-DSS 요구사항이 충족되는가?"

  required_tasks:
    - "거래 원자성 보장"
    - "감사 로그 구현"
    - "금액 계산 정밀도"
    - "중복 거래 방지"
    - "규제 준수 검토"

  standards:
    - "PCI-DSS"
    - "SOC 2"
```

#### Healthcare Domain

```yaml
healthcare_criteria:
  questions:
    - "의료 데이터 규정이 준수되는가?"
    - "환자 프라이버시가 보호되는가?"
    - "데이터 접근 제어가 적절한가?"
    - "감사 추적이 가능한가?"

  required_tasks:
    - "HIPAA 준수 검토"
    - "PHI 데이터 암호화"
    - "접근 권한 세분화"
    - "감사 로그 구현"
    - "데이터 보존 정책"

  standards:
    - "HIPAA"
    - "HITRUST"
```

#### E-commerce Domain

```yaml
ecommerce_criteria:
  questions:
    - "사용자 경험이 최적화되었는가?"
    - "결제 흐름이 안전한가?"
    - "재고 관리가 정확한가?"
    - "주문 상태 추적이 가능한가?"

  required_tasks:
    - "장바구니 동기화"
    - "재고 실시간 확인"
    - "주문 상태 알림"
    - "결제 실패 복구"
    - "반품/환불 처리"

  standards:
    - "PCI-DSS (결제)"
    - "WCAG 2.1 (접근성)"
```

### Expert Review Format

```yaml
domain_review_output:
  format: |
    🎓 Domain Master Review [{domain}]

    ## Professional Assessment
    - Overall Score: {score}/10
    - Compliance Level: {level}

    ## Missing Industry Requirements
    | # | Requirement | Standard | Priority |
    |---|-------------|----------|----------|
    | 1 | {req_1}     | {std_1}  | {pri_1}  |

    ## Recommendations
    - {recommendation_1}
    - {recommendation_2}

    ## Required Tasks to Add
    - [ ] {task_1}
    - [ ] {task_2}
```

---

## Review Execution Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                      REVIEW EXECUTION                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Task List ───▶ [Parallel Review]                                   │
│                      │                                               │
│       ┌──────────────┼──────────────┬──────────────┐                │
│       ▼              ▼              ▼              ▼                │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐             │
│  │  Edge   │   │ Missing │   │ Maintain│   │Convention│             │
│  │  Cases  │   │ Features│   │ ability │   │  Guard   │             │
│  └────┬────┘   └────┬────┘   └────┬────┘   └────┬─────┘             │
│       │             │             │              │                   │
│       └─────────────┴─────────────┴──────────────┘                  │
│                           │                                          │
│                           ▼                                          │
│                  ┌──────────────┐                                    │
│                  │Domain Master │ (Sequential - needs context)       │
│                  └──────┬───────┘                                    │
│                         │                                            │
│                         ▼                                            │
│               Aggregate All Gaps                                     │
│                         │                                            │
│                         ▼                                            │
│               Deduplicate & Prioritize                               │
│                         │                                            │
│                         ▼                                            │
│               Generate Review Report                                 │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Gap Prioritization

```yaml
priority_matrix:
  critical:
    indicators:
      - "보안 취약점"
      - "데이터 손실 위험"
      - "규제 위반"
    action: "필수 추가 권장"

  high:
    indicators:
      - "주요 기능 누락"
      - "심각한 UX 문제"
      - "성능 병목"
    action: "강력 권장"

  medium:
    indicators:
      - "편의 기능 누락"
      - "코드 품질 이슈"
      - "문서화 부족"
    action: "권장"

  low:
    indicators:
      - "스타일 불일치"
      - "마이너 개선"
      - "선택적 기능"
    action: "선택적"
```

## Output Format

See [REVIEW_FORMAT.md](./REVIEW_FORMAT.md) for standardized output templates.
