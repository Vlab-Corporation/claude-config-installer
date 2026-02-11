# cq analyze - Ultrathink Task Analysis Command

## Overview

The `cq analyze` command provides intelligent analysis of task lists for:
- **Dependency detection**: Identifies which tasks depend on others
- **Conflict detection**: Finds tasks that may conflict (same files/modules)
- **Parallel grouping**: Creates optimal execution groups for parallel execution
- **Time estimation**: Calculates potential time savings

## Usage

### Basic Usage
```bash
# Analyze tasks from string
cq analyze "테스트 작성, API 구현, 문서화"

# Analyze current queue
cq analyze --queue
cq analyze -q

# Analyze from file
cq analyze --file tasks.md
cq analyze --file tasks.json
```

### Execution Modes
```bash
# Dry run (default) - show analysis only
cq analyze "task1, task2, task3"

# Execute after confirmation
cq analyze --queue --execute
cq analyze -q -e

# Full automation (no confirmation)
cq analyze --queue --auto
cq analyze -q -a
```

### Output Formats
```bash
# Pretty format (default for terminal)
cq analyze --queue

# JSON format (for scripts/API)
cq -f json analyze --queue

# Minimal format (for shell prompts)
cq -f minimal analyze --queue
```

## Input Formats

### String Input
```bash
# Comma separated
cq analyze "작업1, 작업2, 작업3"

# Newline separated (in quotes)
cq analyze "작업1
작업2
작업3"
```

### File Input (--file)

**Markdown (.md)**:
```markdown
# Tasks
- [ ] 테스트 작성
- [ ] API 구현
- [x] 문서화
```

**JSON (.json)**:
```json
{
  "tasks": ["테스트 작성", "API 구현", "문서화"]
}
```

**Plain text (.txt)**:
```
테스트 작성
API 구현
문서화
```

### Queue Analysis (--queue)
Analyzes all tasks currently in the queue with status "queued".

## Analysis Features

### Dependency Detection
Automatically detects common dependency patterns:
- `테스트` depends on `구현` (same module)
- `배포` depends on `빌드`
- `통합 테스트` depends on `단위 테스트`

### Conflict Detection

**Hard Conflicts** (same file):
- `auth.py 수정` vs `auth.py 리팩토링`
- Cannot run in parallel

**Soft Conflicts** (same module/directory):
- `auth 로그인 구현` vs `auth 로그아웃 구현`
- Can run in parallel with caution

### Parallel Grouping
Creates execution groups based on:
1. Dependency constraints
2. Hard conflicts
3. Optimal parallelization

Example output:
```
🚀 Execution Groups:
   Group 1 (✅ Parallel): auth 구현, payment 구현
   Group 2 (✅ Parallel): auth 테스트, payment 테스트
```

### Time Estimation
```
⏱️  Time Estimate:
   Sequential: ~4 units
   Parallel:   ~2 units
   Savings:    ~50%
```

## Integration with Queue System

### Adding to Queue
```bash
# Analyze and add to queue
cq analyze "테스트, 구현, 배포" --execute

# Tasks are added with proper dependencies
```

### Respecting Existing Dependencies
When using `--queue`, the analyzer respects:
- Existing `depends_on` relationships
- Task priorities
- Current task status

## Examples

### Example 1: Simple Analysis
```bash
$ cq analyze "문서화, 테스트 작성, 코드 리뷰"

============================================================
  📊 Task Analysis Result
============================================================

📝 Tasks (3):
   1. 문서화
   2. 테스트 작성
   3. 코드 리뷰

🔗 Dependencies:
   (none detected - all independent)

🚀 Execution Groups:
   Group 1 (✅ Parallel): 문서화, 테스트 작성, 코드 리뷰

⏱️  Time Estimate:
   Sequential: ~3 units
   Parallel:   ~1 units
   Savings:    ~67%

============================================================

💡 To execute: cq analyze --queue --execute
💡 For full auto: cq analyze --queue --auto
```

### Example 2: With Dependencies
```bash
$ cq analyze "auth 구현, auth 테스트, auth 배포"

📝 Tasks (3):
   1. auth 구현
   2. auth 테스트
   3. auth 배포

🔗 Dependencies:
   auth 테스트 ← auth 구현
   auth 배포 ← auth 테스트

🚀 Execution Groups:
   Group 1 (➡️  Sequential): auth 구현
   Group 2 (➡️  Sequential): auth 테스트
   Group 3 (➡️  Sequential): auth 배포
```

### Example 3: Mixed Parallel/Sequential
```bash
$ cq analyze "auth 구현, payment 구현, auth 테스트, payment 테스트"

🚀 Execution Groups:
   Group 1 (✅ Parallel): auth 구현, payment 구현
   Group 2 (✅ Parallel): auth 테스트, payment 테스트

⏱️  Time Estimate:
   Sequential: ~4 units
   Parallel:   ~2 units
   Savings:    ~50%
```

## Best Practices

1. **Use specific task names**: Include module/component names for better dependency detection
   - Good: "auth 모듈 로그인 구현"
   - Less specific: "로그인 구현"

2. **Review before execution**: Use dry run first, then `--execute`

3. **JSON for automation**: Use `-f json` for scripting

4. **Queue analysis for ongoing work**: Use `--queue` to optimize existing tasks

## Technical Details

### Task Analyzer Module
Location: `~/.claude/scripts/task_analyzer.py`

Key classes:
- `TaskAnalyzer`: Main analysis class
- `AnalysisResult`: Analysis result data structure

### Dependency Rules
Built-in dependency patterns (configurable):
```python
DEPENDENCY_RULES = {
    'test': ['impl', 'implement', 'build', '구현', '빌드'],
    'deploy': ['build', 'test', '빌드', '테스트'],
    'integration': ['impl', 'unit', '구현', '단위'],
    '테스트': ['구현', '빌드', 'implement', 'build'],
    '배포': ['빌드', '테스트', 'build', 'test'],
}
```

### Conflict Detection
Uses scope extraction to identify:
- File patterns: `*.py`, `*.ts`, `@file`
- Module patterns: `모듈`, `컴포넌트`, `service`
- Directory patterns: `src/`, `in directory/`

## Related Commands

- `cq list`: View current queue
- `cq parallel plan`: View parallel execution plan
- `cq parallel analyze <id_a> <id_b>`: Analyze conflict between two specific tasks
