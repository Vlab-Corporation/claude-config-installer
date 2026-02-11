# Review Result Format Standardization

This document defines the standardized output formats for the `/planning` multi-perspective review.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    REVIEW OUTPUT COMPONENTS                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐             │
│  │   Header    │    │   Body      │    │   Footer    │             │
│  │             │    │             │    │             │             │
│  │ • Phase info│    │ • Per-view  │    │ • Summary   │             │
│  │ • Task count│    │   results   │    │ • Options   │             │
│  │ • Domain    │    │ • Gap list  │    │ • Actions   │             │
│  └─────────────┘    └─────────────┘    └─────────────┘             │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Phase 3: Review Output Format

### Header Section

```markdown
┌─────────────────────────────────────────────────────────────────┐
│  [Phase 3: Multi-Perspective Review]                            │
├─────────────────────────────────────────────────────────────────┤
│  Original Tasks: {N}                                            │
│  Domain Expert: {domain_icon} {domain_name}                     │
│  Review Status: {In Progress | Complete | Partial}              │
└─────────────────────────────────────────────────────────────────┘
```

### Body Section - Per Perspective

```markdown
🔧 Edge Cases ({N} gaps found)
  │
  ├─ ⚠️ {Gap description}
  │    └─ Why: {Explanation of why this is needed}
  │    └─ Priority: {Critical | High | Medium | Low}
  │
  └─ ⚠️ {Gap description}
       └─ Why: {Explanation}
       └─ Priority: {Priority}

📦 Missing Features ({N} gaps found)
  │
  ├─ ⚠️ {Gap description}
  │    └─ Why: {Explanation}
  │    └─ Priority: {Priority}
  │
  └─ ✅ No additional gaps found

🔄 Maintainability ({N} gaps found)
  │
  └─ ⚠️ {Gap description}
       └─ Why: {Explanation}
       └─ Priority: {Priority}

🛡️ Convention Guard ({N} gaps found)
  │
  ├─ ⚠️ {Gap description}
  │    └─ Rule: {Convention/Rule reference}
  │    └─ Priority: {Priority}
  │
  └─ 📝 New pattern detected: {pattern_name}
       └─ Recommendation: Document in CLAUDE.md

🎓 Domain Master [{domain}] ({N} gaps found)
  │
  ├─ ⚠️ {Gap description}
  │    └─ Standard: {Standard/Guideline reference}
  │    └─ Priority: {Priority}
  │
  └─ 💡 Recommendation: {Expert recommendation}
```

### Footer Section - Summary

```markdown
┌─────────────────────────────────────────────────────────────────┐
│  REVIEW SUMMARY                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Total Gaps Found: {N}                                          │
│                                                                 │
│  By Priority:                                                   │
│    🔴 Critical: {N}                                             │
│    🟠 High: {N}                                                 │
│    🟡 Medium: {N}                                               │
│    🟢 Low: {N}                                                  │
│                                                                 │
│  By Perspective:                                                │
│    🔧 Edge Cases: {N}                                           │
│    📦 Missing Features: {N}                                     │
│    🔄 Maintainability: {N}                                      │
│    🛡️ Convention Guard: {N}                                     │
│    🎓 Domain Master: {N}                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 4: Approval Interface Format

### Standard Approval Table

```markdown
┌─────────────────────────────────────────────────────────────────┐
│  📊 PLANNING REVIEW REPORT                                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Original Tasks: {N}  │  Gaps Found: {M}                        │
│                                                                 │
│  ┌───┬──────────────────────────────────────┬─────────┬────────┐│
│  │ # │ Gap Description                      │ Source  │Priority││
│  ├───┼──────────────────────────────────────┼─────────┼────────┤│
│  │ 1 │ {gap_1_description}                  │ {src_1} │ {pri_1}││
│  │ 2 │ {gap_2_description}                  │ {src_2} │ {pri_2}││
│  │ 3 │ {gap_3_description}                  │ {src_3} │ {pri_3}││
│  │ 4 │ {gap_4_description}                  │ {src_4} │ {pri_4}││
│  │ 5 │ {gap_5_description}                  │ {src_5} │ {pri_5}││
│  └───┴──────────────────────────────────────┴─────────┴────────┘│
│                                                                 │
│  Options:                                                       │
│  • 전체 승인 (all) - Add all {M} gaps                          │
│  • 선택 승인 (1,3,5) - Add specific gaps                       │
│  • 거부 (none) - Keep original {N} tasks only                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Compact Approval Format

For smaller gap counts (≤5):

```markdown
📊 Review found {N} gaps:

1. 🔴 {gap_1} (Edge Cases)
2. 🟠 {gap_2} (Features)
3. 🟡 {gap_3} (Maintainability)

Add? (all / 1,2 / none)
```

### Extended Approval Format

For larger gap counts (>10):

```markdown
📊 Review found {N} gaps

🔴 Critical ({N}):
  1. {gap_description}
  2. {gap_description}

🟠 High ({N}):
  3. {gap_description}
  4. {gap_description}
  5. {gap_description}

🟡 Medium ({N}):
  6. {gap_description}
  ...

🟢 Low ({N}):
  {N}. {gap_description}

Recommended: Add all Critical and High (1-5)

Options:
• all - 전체 승인 ({N} gaps)
• critical - Critical만 승인 ({N} gaps)
• high+ - Critical + High 승인 ({N} gaps)
• 1,3,5 - 선택 승인
• none - 거부
```

---

## Phase 5: Finalize Output Format

### Standard Finalize Output

```markdown
┌─────────────────────────────────────────────────────────────────┐
│  [Phase 5: Finalize]                                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ✅ {N} gaps approved by user                                   │
│  ✅ TodoWrite updated: {original} → {final} tasks               │
│                                                                 │
│  Added Tasks:                                                   │
│  • {task_1} (Priority: {priority})                              │
│  • {task_2} (Priority: {priority})                              │
│  • {task_3} (Priority: {priority})                              │
│                                                                 │
│  ✅ Planning complete!                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### With Rejection Information

```markdown
┌─────────────────────────────────────────────────────────────────┐
│  [Phase 5: Finalize]                                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ✅ {N} of {M} gaps approved                                    │
│  ✅ TodoWrite updated: {original} → {final} tasks               │
│                                                                 │
│  Added:                                                         │
│  ├─ ✅ {task_1}                                                 │
│  ├─ ✅ {task_2}                                                 │
│  └─ ✅ {task_3}                                                 │
│                                                                 │
│  Rejected (not added):                                          │
│  ├─ ❌ {task_4}                                                 │
│  └─ ❌ {task_5}                                                 │
│                                                                 │
│  ✅ Planning complete!                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Final Task List Format

### Compact List

```markdown
📋 Final Task List ({N} tasks):
 1. [pending] {task_1}
 2. [pending] {task_2}
 3. [pending] {task_3}
 4. [pending] {task_4} ← NEW
 5. [pending] {task_5} ← NEW
 ...
```

### Grouped by Source

```markdown
📋 Final Task List ({N} tasks)

Original Tasks ({M}):
 1. [pending] {task_1}
 2. [pending] {task_2}
 3. [pending] {task_3}

Added from Review ({K}):
 4. [pending] {task_4} (Edge Cases)
 5. [pending] {task_5} (Domain Master)
 6. [pending] {task_6} (Maintainability)
```

### With Priority Markers

```markdown
📋 Final Task List ({N} tasks)

🔴 Critical:
 1. [pending] {task_critical_1}
 2. [pending] {task_critical_2}

🟠 High:
 3. [pending] {task_high_1}
 4. [pending] {task_high_2}

🟡 Medium:
 5. [pending] {task_medium_1}
 ...

🟢 Low:
 {N}. [pending] {task_low_1}
```

---

## Gap Description Templates

### Edge Cases Gap

```markdown
⚠️ {Edge case description}
   └─ Scenario: {When this edge case occurs}
   └─ Impact: {What happens if not handled}
   └─ Suggestion: {Recommended handling approach}
```

### Missing Features Gap

```markdown
⚠️ {Feature description}
   └─ User Need: {Why user needs this}
   └─ Current: {Current behavior/state}
   └─ Expected: {Expected behavior with feature}
```

### Maintainability Gap

```markdown
⚠️ {Maintainability issue}
   └─ Affected: {Files/modules affected}
   └─ Debt Type: {Technical debt category}
   └─ Recommendation: {Refactoring approach}
```

### Convention Guard Gap

```markdown
⚠️ {Convention issue}
   └─ Rule: {Convention/rule being violated}
   └─ Source: {Where rule is defined}
   └─ Fix: {How to comply}
```

### Domain Master Gap

```markdown
⚠️ {Domain-specific issue}
   └─ Standard: {Industry standard reference}
   └─ Requirement: {Specific requirement}
   └─ Compliance: {How to achieve compliance}
```

---

## Color and Icon Reference

### Priority Colors

| Priority | Color | Icon | Usage |
|----------|-------|------|-------|
| Critical | Red | 🔴 | Security issues, data loss risks |
| High | Orange | 🟠 | Major functionality gaps |
| Medium | Yellow | 🟡 | Quality improvements |
| Low | Green | 🟢 | Nice-to-have additions |

### Perspective Icons

| Perspective | Icon | Meaning |
|-------------|------|---------|
| Edge Cases | 🔧 | Technical edge cases |
| Missing Features | 📦 | Functional completeness |
| Maintainability | 🔄 | Code quality/sustainability |
| Convention Guard | 🛡️ | Rule compliance |
| Domain Master | 🎓 | Professional standards |

### Status Icons

| Status | Icon | Meaning |
|--------|------|---------|
| Success | ✅ | Completed/Approved |
| Warning | ⚠️ | Gap/Issue found |
| Error | ❌ | Failed/Rejected |
| Info | ℹ️ | Information |
| New | 🆕 | Newly added |
| Pending | ⏳ | Awaiting action |

---

## Localization Notes

### Korean Output (Default)

```markdown
📊 리뷰 결과 보고서

원본 작업: 12개 │ 발견된 누락: 7개

# │ 누락 항목                    │ 출처          │ 우선순위
──┼─────────────────────────────┼──────────────┼──────────
1 │ 네트워크 오류 재시도 로직     │ Edge Cases   │ 높음
```

### English Output (with --lang en)

```markdown
📊 Review Report

Original Tasks: 12 │ Gaps Found: 7

# │ Gap Description              │ Source       │ Priority
──┼─────────────────────────────┼──────────────┼──────────
1 │ Network error retry logic    │ Edge Cases   │ High
```
