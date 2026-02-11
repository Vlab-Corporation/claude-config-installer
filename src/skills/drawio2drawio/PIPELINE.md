# drawio2drawio Pipeline Details

5단계 파이프라인의 상세 행동 지침.

## Phase 1: PARSE

### Input
- `.drawio` 파일 경로

### Execution
```bash
python3 ~/00_projects/drawio2drawio/src/parser.py <input.drawio>
```

### Output Format
```json
{
  "file": "input.drawio",
  "texts": [
    {
      "id": "cell_id",
      "value": "텍스트 내용 (HTML 제거됨)",
      "style": "rounded=1;whiteSpace=wrap;...",
      "shape_hint": "process|decision|terminal",
      "geometry": {"x": 100, "y": 200, "width": 240, "height": 70}
    }
  ],
  "connections": [
    {
      "id": "edge_id",
      "source": "source_cell_id",
      "target": "target_cell_id",
      "label": "edge label or empty"
    }
  ],
  "stats": {"node_count": 87, "edge_count": 45}
}
```

### Error Handling
- 파일 없음: 사용자에게 경로 확인 요청
- XML 파싱 오류: `.drawio` 파일 형식 확인 안내
- 텍스트 없음: "이미지만 있는 다이어그램은 지원되지 않습니다" 안내

---

## Phase 2: ANALYZE

### Input
- Phase 1의 JSON 출력

### Process

#### Step 2.1: Domain Detection
텍스트 목록에서 도메인 키워드 매칭:

```yaml
medical_keywords:
  ko: [환자, 진단, 통증, 검사, 의뢰, 치료, 평가, 증상, 수술, 약물, 질환, 임상, NRS, ROM, 재활]
  en: [patient, diagnosis, pain, exam, referral, treatment, assessment, symptom, clinical]

business_keywords:
  ko: [승인, 프로세스, 고객, 매출, KPI, 보고, 결재, 기안, 검토, 계약]
  en: [approval, process, customer, revenue, KPI, report, contract, review]

technical_keywords:
  ko: [API, 서버, 배포, 에러, 로그, DB, 코드, 빌드, 테스트, 모니터링]
  en: [API, server, deploy, error, log, database, code, build, test, CI/CD]
```

3+ 키워드 매칭 시 해당 도메인 선택. 동점 시 첫 번째 우선.

#### Step 2.2: Text Classification

각 텍스트 항목에 대해 node_type 분류:

| Condition | node_type |
|-----------|-----------|
| "?" 포함 또는 "여부", "확인", "스크리닝" 키워드 | decision |
| "START", "시작", "내원", "접수" 키워드 | start |
| "END", "종료", "의뢰" + 터미널 위치 | end |
| "교육", "설명", "상담", "인지" 키워드 | education |
| "경고", "위험", "Red Flag", "염증" 키워드 | warning |
| "의뢰", "전문의" 키워드 (비터미널) | referral |
| "성공", "달성", "확정", "확인" + 긍정 컨텍스트 | success |
| 기타 모든 항목 | process |

#### Step 2.3: Phase Grouping

연관 항목을 Phase로 묶기:
1. 기존 연결(connections)의 순서를 기반으로 순차적 그룹 형성
2. 의미적 관련성으로 보완 (같은 주제, 연속된 평가 항목 등)
3. Phase 이름 부여 (예: "초기 접수", "주관적 평가", "통증 패턴 분석")

### Output
분류된 텍스트 목록 + 도메인 + Phase 그룹핑

---

## Phase 3: RESTRUCTURE

### Input
- Phase 2의 분류 결과

### Process

#### Step 3.1: Structure Validation
- START 노드 없으면 → 추가 (첫 번째 프로세스 노드 앞에)
- END 노드 없으면 → 모든 터미널 경로에 추가
- 터미널 경로 = 출력 엣지가 없는 노드들

#### Step 3.2: Decision Structuring
모든 decision 노드에 대해:
- 2+ 출력 엣지 확인
- 부족 시: 컨텍스트 기반으로 분기 생성
  - 예/아니요 분기
  - 조건별 분기 (경미/중등/심각 등)
- 각 분기에 라벨 부여

#### Step 3.3: Loop Detection & Creation
재평가/반복 패턴 감지:
- "재평가 → 중재" 루프: 치료 반응 평가 후 중재 단계로 복귀
- "재발 → 분류" 루프: 추적 관찰 후 재분류
- loop_back 엣지 생성

#### Step 3.4: FlowChart JSON Assembly

@ANALYSIS_SCHEMA.md의 스키마에 따라 완전한 JSON 생성:
- 모든 노드에 고유 ID 부여
- 모든 엣지에 source/target 매핑
- Phase 목록 정리
- 메타데이터 포함

### Output
완전한 FlowChart JSON (ANALYSIS_SCHEMA.md 준수)

---

## Phase 4: GENERATE

### Input
- Phase 3의 FlowChart JSON
- 도메인 스타일 (Phase 2에서 결정)

### Execution
1. FlowChart JSON을 임시 파일에 저장
2. generator.py 실행:
```bash
python3 ~/00_projects/drawio2drawio/src/generator.py /tmp/flowchart.json --style <domain> --output <output_path>
```
3. 임시 파일 정리

### Output
`.drawio` XML 파일

---

## Phase 5: VALIDATE

### Input
- 생성된 `.drawio` 파일

### Validation Checklist

```yaml
structural:
  - has_start: "START 노드 1개 존재"
  - has_end: "END 노드 1+ 존재"
  - no_orphans: "모든 노드가 1+ 연결"
  - decisions_branched: "모든 Decision에 2+ 출력"
  - all_paths_terminate: "모든 경로가 END에 도달"

visual:
  - style_consistency: "모든 노드가 도메인 스타일 적용"
  - shape_correctness: "node_type과 도형 일치 (decision=rhombus 등)"
  - label_present: "모든 노드에 라벨 존재"

quality:
  - no_duplicate_labels: "동일 라벨 중복 없음"
  - meaningful_edge_labels: "Decision 출력에 라벨 존재"
  - phase_ordering: "Phase 순서가 논리적"
```

### Failure Action
검증 실패 시:
1. 실패 항목 목록 출력
2. Phase 3 (RESTRUCTURE)로 돌아가 수정
3. 최대 2회 재시도
4. 그래도 실패 시: 사용자에게 문제점 보고 + 부분 결과 제공

---

## Edge Cases

### 텍스트 없는 다이어그램
- parser 결과에 texts가 비어있는 경우
- 안내: "텍스트가 없는 다이어그램입니다. 이미지/도형만 있는 경우 변환이 불가능합니다."

### 이미지만 있는 경우
- shape에 "image" 스타일이 있는 경우
- 안내: "이미지 기반 다이어그램은 텍스트 추출이 불가합니다."

### 이미 잘 구조화된 다이어그램
- 기존에 START/END/Decision이 있는 경우
- 기존 구조 최대한 보존, 스타일만 적용

### 매우 큰 다이어그램 (100+ 노드)
- Phase 그룹핑을 더 세밀하게
- 레이아웃에서 페이지 크기 자동 조정

### 한국어/영어 혼합
- 키워드 매칭에 양 언어 포함
- 라벨은 원본 언어 유지
