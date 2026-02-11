# /sc:drawio2drawio — Draw.io Diagram Transformer

비전문가가 만든 draw.io 다이어그램을 공학적 컨벤션에 맞는 정돈된 flowchart로 변환합니다.

## Usage

```
/sc:drawio2drawio @<input.drawio> [options]
```

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `--domain` | 도메인 지정: medical, business, technical | auto-detect |
| `--preview` | JSON 구조만 미리보기 (파일 생성 안 함) | false |
| `--verbose` | 각 Phase 결과 상세 출력 | false |
| `--style-only` | 기존 구조 유지, 스타일만 적용 | false |
| `--output <path>` | 출력 파일 경로 | `<input>_converted.drawio` |

## Examples

```bash
# 기본 사용 (자동 도메인 감지)
/sc:drawio2drawio @knee_OA.drawio

# 의료 도메인 명시
/sc:drawio2drawio @clinical_flow.drawio --domain medical

# 미리보기만
/sc:drawio2drawio @process.drawio --preview

# 상세 출력
/sc:drawio2drawio @diagram.drawio --verbose --domain business

# 출력 경로 지정
/sc:drawio2drawio @input.drawio --output ~/Desktop/result.drawio
```

## Pipeline

5단계 자동 실행:

1. **PARSE** → Python parser로 텍스트/연결 추출
2. **ANALYZE** → 도메인 감지 + 텍스트 분류
3. **RESTRUCTURE** → START/END 추가, 조건분기 구조화, JSON 생성
4. **GENERATE** → Python generator로 .drawio XML 생성
5. **VALIDATE** → 결과 검증 (실패 시 자동 수정 재시도)

## Tool Coordination

| Tool | Usage |
|------|-------|
| Bash | Python 스크립트 실행 (parser.py, generator.py) |
| Read | 입력 .drawio 파일 읽기 |
| Write | 중간 JSON 파일 / 결과 파일 저장 |
| Sequential (--think) | Phase 2-3 분석 시 구조화된 추론 |

## Skill Reference

상세 동작: `~/.claude/skills/drawio2drawio/SKILL.md`
파이프라인: `~/.claude/skills/drawio2drawio/PIPELINE.md`
도형 표준: `~/.claude/skills/drawio2drawio/SHAPE_STANDARDS.md`
JSON 스키마: `~/.claude/skills/drawio2drawio/ANALYSIS_SCHEMA.md`

## Project

코드: `~/00_projects/drawio2drawio/`
골드 스탠다드: `~/00_projects/drawio2drawio/examples/knee_oa/output.drawio`
