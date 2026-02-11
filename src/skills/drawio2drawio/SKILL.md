# drawio2drawio Skill

비전문가가 만든 draw.io 다이어그램을 공학적 컨벤션에 맞는 정돈된 flowchart로 변환합니다.

## Trigger

- `/sc:drawio2drawio` 명령어
- `.drawio` 파일 변환 요청
- 플로우차트 정리/개선 요청

## Usage

```
/sc:drawio2drawio @input.drawio [--domain medical|business|technical] [--preview] [--verbose] [--output path]
```

## 5-Phase Pipeline

이 Skill은 5단계 파이프라인을 순차적으로 실행합니다. 상세 지침은 @PIPELINE.md를 참조합니다.

### Phase 1: PARSE (Python)
```bash
python3 ~/00_projects/drawio2drawio/src/parser.py <input.drawio>
```
- 결과: JSON (texts + connections + stats)
- 실패 시: 파일 형식 오류 안내

### Phase 2: ANALYZE (Claude)
- 추출된 텍스트 목록을 분석
- 도메인 감지 (--domain 미지정 시 자동 감지)
- 각 텍스트 항목 분류: process | decision | start | end | education | warning | referral | success
- 그룹핑: 관련 항목을 Phase로 묶기
- 조건문 감지: "?" 포함, "여부", "확인" 등의 키워드
- 루프 감지: "재평가", "재검사", "follow-up" 등

### Phase 3: RESTRUCTURE (Claude)
- START 노드 추가 (없는 경우)
- END 노드 추가 (모든 터미널 경로에)
- Decision 노드에 2+ 분기 보장
- 루프 백 엣지 추가 (재평가 → 중재 등)
- FlowChart JSON 구조 생성 (@ANALYSIS_SCHEMA.md 참조)
- 도형 표준 적용 (@SHAPE_STANDARDS.md 참조)

### Phase 4: GENERATE (Python)
```bash
# FlowChart JSON을 임시 파일에 저장 후:
python3 ~/00_projects/drawio2drawio/src/generator.py <flowchart.json> --style <domain> --output <output.drawio>
```

### Phase 5: VALIDATE (Claude)
검증 체크리스트:
- [ ] START 노드 1개 존재
- [ ] END 노드 1+ 존재
- [ ] 모든 노드가 1+ 연결 보유
- [ ] Decision 노드에 2+ 출력 엣지
- [ ] 고아 노드 없음
- [ ] 스타일이 도메인과 일치
- 문제 발견 시 Phase 3으로 돌아가 수정

## Domain Detection Rules

도메인 자동 감지 우선순위:

1. **medical**: 의료 키워드 3+ 매칭 (환자, 진단, 통증, 검사, 의뢰, 치료, 평가, NRS, ROM)
2. **business**: 비즈니스 키워드 3+ 매칭 (승인, 프로세스, 고객, 매출, KPI, 보고)
3. **technical**: 기술 키워드 3+ 매칭 (API, 서버, 배포, 에러, 로그, DB, 코드)
4. **default**: 위 조건 미충족 시

## Output

- 변환된 `.drawio` 파일 생성
- `--preview` 플래그 시: FlowChart JSON 구조만 표시 (생성 안 함)
- `--verbose` 플래그 시: 각 Phase 결과 상세 출력

## Tool Coordination

| Phase | Tool | Purpose |
|-------|------|---------|
| PARSE | Bash | Python parser.py 실행 |
| ANALYZE | Native | 텍스트 분석 + 도메인 감지 |
| RESTRUCTURE | Native + Sequential (--think) | 구조화 + JSON 생성 |
| GENERATE | Bash | Python generator.py 실행 |
| VALIDATE | Native | 결과 검증 |

## Reference Files

- @PIPELINE.md — 상세 파이프라인 지침
- @SHAPE_STANDARDS.md — 플로우차트 도형 표준
- @ANALYSIS_SCHEMA.md — FlowChart JSON 스키마
- ~/00_projects/drawio2drawio/examples/knee_oa/output.drawio — 골드 스탠다드
