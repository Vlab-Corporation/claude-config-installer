# Convention Tracker

This document defines the logic for detecting, tracking, and enforcing coding conventions in the `/planning` workflow.

## Overview

The Convention Tracker ensures that task lists include proper convention compliance, especially:
1. **Existing Rules**: Project's established conventions
2. **New Patterns**: Recently introduced patterns that should become conventions
3. **Context Loss Prevention**: Tasks that maintain convention awareness across sessions

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CONVENTION TRACKING SYSTEM                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐  │
│  │ EXISTING RULES  │    │  NEW PATTERNS   │    │ CONTEXT LOSS    │  │
│  │                 │    │                 │    │  PREVENTION     │  │
│  │ • CLAUDE.md     │    │ • Recent code   │    │                 │  │
│  │ • RULES.md      │    │ • New imports   │    │ • Session gaps  │  │
│  │ • Project style │    │ • New helpers   │    │ • Complex logic │  │
│  │ • .eslintrc     │    │ • New patterns  │    │ • Multi-file    │  │
│  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘  │
│           │                      │                      │            │
│           └──────────────────────┼──────────────────────┘            │
│                                  │                                   │
│                                  ▼                                   │
│                    ┌─────────────────────────┐                      │
│                    │  CONVENTION GAP FINDER  │                      │
│                    └─────────────────────────┘                      │
│                                  │                                   │
│                                  ▼                                   │
│                    Generate Convention Tasks                         │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Convention Sources

### Priority Hierarchy

| Priority | Source | Location | Description |
|----------|--------|----------|-------------|
| 1 (Highest) | Project CLAUDE.md | `PROJECT_ROOT/CLAUDE.md` | Project-specific rules |
| 2 | Project Conventions | `.claude/CONVENTIONS.md` | Detailed convention doc |
| 3 | SuperClaude Rules | `~/.claude/RULES.md` | Framework-wide rules |
| 4 | Language Defaults | `~/.claude/docs/conventions/` | Language-specific defaults |
| 5 | Tool Configs | `.eslintrc`, `pyproject.toml`, etc. | Tooling configurations |

### Source Detection

```yaml
convention_sources:
  auto_detect:
    - pattern: "CLAUDE.md"
      location: "PROJECT_ROOT"
      parser: "markdown_rules"

    - pattern: ".claude/CONVENTIONS.md"
      location: "PROJECT_ROOT/.claude"
      parser: "markdown_rules"

    - pattern: ".eslintrc*"
      location: "PROJECT_ROOT"
      parser: "eslint_config"

    - pattern: "pyproject.toml"
      location: "PROJECT_ROOT"
      parser: "python_config"

    - pattern: "tsconfig.json"
      location: "PROJECT_ROOT"
      parser: "typescript_config"

    - pattern: ".prettierrc*"
      location: "PROJECT_ROOT"
      parser: "prettier_config"
```

---

## Existing Rules Detection

### Rule Categories

```yaml
rule_categories:
  naming:
    description: "변수, 함수, 클래스 네이밍 규칙"
    patterns:
      - "camelCase|snake_case|PascalCase"
      - "prefix|suffix 규칙"
      - "약어 사용 규칙"

  structure:
    description: "파일/폴더 구조 규칙"
    patterns:
      - "디렉토리 구조"
      - "파일 위치 규칙"
      - "모듈 구성"

  imports:
    description: "import 순서 및 스타일"
    patterns:
      - "import 그룹핑"
      - "절대/상대 경로"
      - "barrel exports"

  formatting:
    description: "코드 포맷팅 규칙"
    patterns:
      - "들여쓰기"
      - "줄바꿈"
      - "최대 줄 길이"

  error_handling:
    description: "에러 처리 패턴"
    patterns:
      - "에러 타입"
      - "에러 메시지 포맷"
      - "로깅 패턴"

  testing:
    description: "테스트 규칙"
    patterns:
      - "테스트 파일 위치"
      - "테스트 네이밍"
      - "테스트 구조"
```

### Rule Extraction

```python
def extract_rules_from_claude_md(content: str) -> list[Rule]:
    """Extract rules from CLAUDE.md content."""
    rules = []

    # Pattern matching for common rule formats
    patterns = [
        r"- \*\*(.+?)\*\*: (.+)",  # - **Rule**: Description
        r"^\d+\.\s+(.+)",           # 1. Rule description
        r"^- (.+)$",                # - Rule description
    ]

    for pattern in patterns:
        matches = re.findall(pattern, content, re.MULTILINE)
        for match in matches:
            rules.append(parse_rule(match))

    return rules
```

---

## New Pattern Detection

### What Constitutes a "New Pattern"?

A new pattern is code that:
1. Introduces a new helper function/utility
2. Establishes a new architectural pattern
3. Creates new type definitions
4. Implements new error handling approaches
5. Adds new configuration structures

### Detection Algorithm

```yaml
new_pattern_indicators:
  new_helper_function:
    trigger: "새로운 유틸 함수 작성"
    check: |
      - utils/ 또는 helpers/ 디렉토리에 새 함수
      - 2개 이상 파일에서 재사용 가능
    action: "유틸 함수 문서화 작업 추가"

  new_type_definition:
    trigger: "새로운 타입/인터페이스 정의"
    check: |
      - types/ 디렉토리에 새 타입
      - 기존 타입 확장
    action: "타입 정의 문서화 작업 추가"

  new_api_pattern:
    trigger: "새로운 API 패턴 도입"
    check: |
      - 새로운 응답 포맷
      - 새로운 에러 코드
      - 새로운 인증 방식
    action: "API 패턴 문서화 작업 추가"

  new_component_pattern:
    trigger: "새로운 컴포넌트 패턴"
    check: |
      - 새로운 HOC 패턴
      - 새로운 훅 패턴
      - 새로운 레이아웃 패턴
    action: "컴포넌트 패턴 문서화 작업 추가"

  new_state_pattern:
    trigger: "새로운 상태 관리 패턴"
    check: |
      - 새로운 store 구조
      - 새로운 context 패턴
      - 새로운 캐싱 전략
    action: "상태 관리 패턴 문서화 작업 추가"
```

### Pattern Analysis Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    NEW PATTERN ANALYSIS                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Task List ───▶ Code Impact Analysis                                │
│                        │                                             │
│                        ▼                                             │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ For each task that creates/modifies code:                    │   │
│  │                                                               │   │
│  │  1. Will it create new utility functions?                    │   │
│  │     └─▶ If yes: Add "Document new utility" task              │   │
│  │                                                               │   │
│  │  2. Will it establish new patterns?                          │   │
│  │     └─▶ If yes: Add "Update convention doc" task             │   │
│  │                                                               │   │
│  │  3. Will it introduce new types?                             │   │
│  │     └─▶ If yes: Add "Document type definitions" task         │   │
│  │                                                               │   │
│  │  4. Will future code need to follow this pattern?            │   │
│  │     └─▶ If yes: Add "Add to CLAUDE.md" task                  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Context Loss Prevention

### High-Risk Scenarios

When might convention violations occur due to context loss?

```yaml
context_loss_scenarios:
  session_gap:
    description: "세션 간 컨텍스트 손실"
    risk_factors:
      - "복잡한 비즈니스 로직"
      - "프로젝트 특유의 규칙"
      - "암묵적 가정"
    prevention:
      - "작업 전 CLAUDE.md 참조 태스크"
      - "규칙 체크리스트 태스크"

  multi_file_changes:
    description: "여러 파일 동시 변경"
    risk_factors:
      - "파일 간 일관성"
      - "import 패턴 불일치"
      - "네이밍 불일치"
    prevention:
      - "전체 변경 후 일관성 검증 태스크"
      - "lint/format 실행 태스크"

  new_team_member:
    description: "새로운 개발자 작업 시작"
    risk_factors:
      - "프로젝트 규칙 미숙지"
      - "기존 패턴 미인지"
    prevention:
      - "온보딩 문서 참조 태스크"
      - "코드 리뷰 태스크"

  complex_feature:
    description: "복잡한 기능 구현"
    risk_factors:
      - "아키텍처 결정 필요"
      - "새로운 패턴 도입"
      - "기존 패턴과 충돌"
    prevention:
      - "설계 문서 작성 태스크"
      - "아키텍처 리뷰 태스크"
```

### Prevention Tasks

```yaml
prevention_task_templates:
  pre_implementation:
    - content: "구현 전 CLAUDE.md 규칙 검토"
      activeForm: "Reviewing CLAUDE.md rules before implementation"
      trigger: "complex_feature OR session_gap"

    - content: "기존 코드 패턴 분석"
      activeForm: "Analyzing existing code patterns"
      trigger: "new_feature_area"

  post_implementation:
    - content: "변경 후 컨벤션 준수 검증"
      activeForm: "Verifying convention compliance after changes"
      trigger: "multi_file_changes"

    - content: "lint 및 format 실행"
      activeForm: "Running lint and format checks"
      trigger: "any_code_change"

  documentation:
    - content: "새로운 패턴 CLAUDE.md에 추가"
      activeForm: "Adding new patterns to CLAUDE.md"
      trigger: "new_pattern_detected"

    - content: "코드 주석으로 컨텍스트 보존"
      activeForm: "Adding comments for context preservation"
      trigger: "complex_logic"
```

---

## Gap Detection Rules

### Convention Check Matrix

```yaml
convention_check_matrix:
  task_type_to_checks:
    api_development:
      - "API 응답 포맷 일관성"
      - "에러 코드 표준화"
      - "엔드포인트 네이밍 규칙"

    ui_development:
      - "컴포넌트 네이밍 규칙"
      - "스타일링 패턴"
      - "접근성 규칙"

    database_changes:
      - "테이블/컬럼 네이밍"
      - "마이그레이션 패턴"
      - "인덱스 규칙"

    testing:
      - "테스트 파일 위치"
      - "테스트 네이밍"
      - "mock 패턴"
```

### Gap Detection Algorithm

```python
def detect_convention_gaps(tasks: list[Task], conventions: list[Rule]) -> list[Gap]:
    gaps = []

    for task in tasks:
        # 1. Check if task affects convention-sensitive areas
        affected_areas = analyze_task_impact(task)

        # 2. For each affected area, check if convention task exists
        for area in affected_areas:
            relevant_conventions = get_conventions_for_area(area, conventions)

            if relevant_conventions and not has_convention_task(tasks, area):
                gaps.append(Gap(
                    type="convention_check_missing",
                    area=area,
                    suggestion=f"{area} 컨벤션 준수 검증 작업 추가"
                ))

        # 3. Check for new pattern documentation
        if task.introduces_new_pattern():
            if not has_documentation_task(tasks, task):
                gaps.append(Gap(
                    type="pattern_documentation_missing",
                    task=task,
                    suggestion="새 패턴 문서화 작업 추가"
                ))

    # 4. Check for context preservation
    if has_complex_changes(tasks) and not has_review_task(tasks):
        gaps.append(Gap(
            type="review_missing",
            suggestion="변경 후 컨벤션 리뷰 작업 추가"
        ))

    return gaps
```

---

## Output Format

### Convention Check Report

```markdown
## 🛡️ Convention Guard Review

### Existing Rules Compliance
| Rule | Source | Task Coverage | Status |
|------|--------|---------------|--------|
| camelCase 함수명 | CLAUDE.md | Task #3 | ✅ |
| API 응답 포맷 | conventions.md | - | ⚠️ 검증 필요 |
| import 순서 | .eslintrc | Task #7 | ✅ |

### New Patterns Detected
| Pattern | Location | Recommendation |
|---------|----------|----------------|
| 새로운 에러 핸들링 | src/errors.ts | CLAUDE.md 업데이트 필요 |
| 새로운 API 훅 | src/hooks/useApi.ts | 문서화 필요 |

### Context Loss Risks
| Risk | Tasks Affected | Prevention Task |
|------|----------------|-----------------|
| 복잡한 인증 로직 | #2, #5, #8 | 구현 전 규칙 검토 추가 |
| 다중 파일 변경 | #3, #4, #6 | 변경 후 일관성 검증 추가 |

### Recommended Tasks to Add
1. [ ] API 응답 포맷 컨벤션 검증 작업
2. [ ] 새로운 에러 핸들링 패턴 CLAUDE.md 추가
3. [ ] 구현 전 CLAUDE.md 규칙 검토
4. [ ] 전체 변경 후 컨벤션 일관성 검증
```

---

## Integration with Planning

### Phase 3 Integration

```yaml
phase_3_review:
  convention_guard:
    order: 4  # 4th perspective in review
    parallel: false  # Needs results from other perspectives

    inputs:
      - task_list
      - project_conventions
      - recent_code_changes

    outputs:
      - existing_rule_gaps
      - new_pattern_gaps
      - context_loss_prevention_gaps

    gap_format:
      type: "convention_guard"
      source: "Convention Guard"
      priority: "medium|high"
      suggestion: "string"
```

### Automatic Task Generation

When gaps are approved, generate tasks:

```yaml
auto_generated_tasks:
  convention_verification:
    template: "{area} 컨벤션 준수 검증"
    activeForm: "Verifying {area} convention compliance"
    insert_position: "after_implementation"

  pattern_documentation:
    template: "새로운 {pattern} 패턴 문서화"
    activeForm: "Documenting new {pattern} pattern"
    insert_position: "end_of_list"

  context_preservation:
    template: "{action} 전 CLAUDE.md 규칙 검토"
    activeForm: "Reviewing CLAUDE.md rules before {action}"
    insert_position: "before_implementation"
```
