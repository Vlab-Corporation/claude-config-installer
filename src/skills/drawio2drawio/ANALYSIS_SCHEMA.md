# FlowChart JSON Schema

Claude가 Phase 3 (RESTRUCTURE)에서 생성하는 FlowChart JSON의 스키마 정의.

## Schema

```json
{
  "$schema": "FlowChart v1.0",
  "title": "string — 다이어그램 제목",
  "domain": "medical | business | technical | default",
  "nodes": [
    {
      "id": "string — 고유 식별자 (예: START, A1, RF, END_REF)",
      "label": "string — 노드 표시 텍스트 (HTML 허용: <br> 등)",
      "node_type": "start | end | process | decision | referral | education | warning | success",
      "phase": "string — 소속 Phase 이름 (optional)",
      "description": "string — 노드 설명/메모 (optional)"
    }
  ],
  "edges": [
    {
      "id": "string — 고유 식별자 (예: e1, e2, ...)",
      "source": "string — 출발 노드 ID",
      "target": "string — 도착 노드 ID",
      "label": "string — 엣지 라벨 (optional, Decision 분기는 필수)",
      "edge_type": "normal | yes | no | loop_back"
    }
  ],
  "phases": [
    "string — Phase 이름 목록 (순서대로)"
  ]
}
```

## Node Type Enum

| Value | Description | Shape | Example |
|-------|-------------|-------|---------|
| `start` | 시작점 | Pill (arcSize=50) | "🟢 START: 무릎 통증 호소 환자 내원" |
| `end` | 종료점 | Pill (arcSize=50) | "🔴 END: 전문의 의뢰" |
| `process` | 일반 프로세스 | Rounded rect | "📋 인적사항 수집" |
| `decision` | 조건 분기 | Diamond (rhombus) | "🚨 Red Flag 스크리닝" |
| `referral` | 의뢰/이관 | Rounded rect (red) | "🔴 전문의 의뢰" |
| `education` | 교육/안내 | Rounded rect (purple) | "🟡 환자 교육 우선" |
| `warning` | 경고/주의 | Rounded rect (orange) | "🔶 염증성 패턴 의심" |
| `success` | 성공/확인 | Rounded rect (mint) | "✅ 진단: Knee OA 확정" |

## Edge Type Enum

| Value | Description | Visual | Example |
|-------|-------------|--------|---------|
| `normal` | 일반 흐름 | Solid black | 순차적 연결 |
| `yes` | 긍정 분기 | Solid green | "예", "일치", "충족" |
| `no` | 부정 분기 | Solid red | "아니요", "불일치", "미충족" |
| `loop_back` | 루프 (역방향) | Dashed yellow | 재평가 → 중재 |

## ID Convention

### Node IDs
- `START` — 시작 노드 (하나만)
- `END_xxx` — 종료 노드 (END_REF, END_GOOD 등)
- `{Phase Letter}{Number}` — Phase 내 순서 (A1, A2, B1, C1 등)
- `{Phase Letter}{Number}{Sub}` — 분기 하위 노드 (C1A, C1B, D3A1 등)
- `{Special}` — 특수 노드 (RF, DIAG_OA, REF_ORTHO 등)

### Edge IDs
- `e{number}` — 순차 번호 (e1, e2, ..., e109)

### Phase Letters (Knee OA Example)
| Letter | Phase |
|--------|-------|
| A | 초기 접수 |
| B | 주관적 평가 |
| C | 통증 패턴 분석 |
| D | 악화/완화 요인 |
| E | 이력 조사 |
| F | 동반질환 |
| G | 영상 |
| H | 가설 수립 |
| I | 객관적 평가 |
| J | 임상 추론 |
| K | 중재 계획 |
| L | 중재 실행 |
| M | 재평가 |

## Example: Knee OA (Simplified)

```json
{
  "title": "Knee OA Clinical Reasoning",
  "domain": "medical",
  "nodes": [
    {
      "id": "START",
      "label": "🟢 START: 무릎 통증 호소 환자 내원",
      "node_type": "start",
      "phase": "초기 접수"
    },
    {
      "id": "A1",
      "label": "📋 인적사항 수집<br>나이 / 성별 / 신장 / 체중 / 직업",
      "node_type": "process",
      "phase": "초기 접수"
    },
    {
      "id": "RF",
      "label": "🚨 Red Flag 스크리닝<br>야간통 악화 / 체중감소<br>발열 / 외상력 / 종양력",
      "node_type": "decision",
      "phase": "주관적 평가"
    },
    {
      "id": "REF_OUT",
      "label": "🔴 전문의 의뢰<br>추가 검사 필요",
      "node_type": "referral",
      "phase": "주관적 평가"
    },
    {
      "id": "END_REF",
      "label": "🔴 END: 전문의 의뢰",
      "node_type": "end",
      "phase": "주관적 평가"
    },
    {
      "id": "END_GOOD",
      "label": "🟢 END: 성공적 종료<br>자가 관리 지속",
      "node_type": "end",
      "phase": "재평가"
    }
  ],
  "edges": [
    {
      "id": "e1",
      "source": "START",
      "target": "A1",
      "label": "",
      "edge_type": "normal"
    },
    {
      "id": "e6",
      "source": "RF",
      "target": "REF_OUT",
      "label": "Red Flag 있음",
      "edge_type": "yes"
    },
    {
      "id": "e8",
      "source": "RF",
      "target": "C1",
      "label": "Red Flag 없음",
      "edge_type": "no"
    },
    {
      "id": "e100",
      "source": "M5",
      "target": "L1",
      "label": "",
      "edge_type": "loop_back"
    }
  ],
  "phases": [
    "초기 접수",
    "주관적 평가",
    "통증 패턴 분석",
    "악화/완화 요인",
    "이력 조사",
    "동반질환",
    "영상",
    "가설 수립",
    "객관적 평가",
    "임상 추론",
    "중재 계획",
    "중재 실행",
    "재평가"
  ]
}
```

## Validation Rules

### Structural
1. `nodes` 배열에 `node_type: "start"`인 노드가 정확히 1개
2. `nodes` 배열에 `node_type: "end"`인 노드가 1개 이상
3. 모든 `edge.source`와 `edge.target`이 유효한 `node.id`를 참조
4. 모든 `node_type: "decision"` 노드가 2개 이상의 출력 엣지 보유
5. `edges`에 순환이 있으면 반드시 `loop_back` 타입

### Content
1. 모든 노드에 비어있지 않은 `label` 존재
2. Decision 출력 엣지에 비어있지 않은 `label` 존재
3. `id`는 배열 내에서 고유
4. `phases` 배열의 값이 최소 1개의 노드의 `phase`와 매칭

### Quality
1. 고아 노드 없음 (연결이 하나도 없는 노드)
2. 도달 불가 노드 없음 (START에서 도달할 수 없는 노드)
3. Phase 순서가 논리적 (START가 첫 번째 Phase에)
