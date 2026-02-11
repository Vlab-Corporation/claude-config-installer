# Flowchart Shape Standards

draw.io에서의 플로우차트 도형 표준. ISO 5807 기반 + 실용적 확장.

## Node Type → Shape Mapping

| node_type | Shape | draw.io Style Key | Description |
|-----------|-------|-------------------|-------------|
| start | 둥근 사각형 (pill) | `rounded=1;arcSize=50` | 시작점 |
| end | 둥근 사각형 (pill) | `rounded=1;arcSize=50` | 종료점 |
| process | 모서리 둥근 사각형 | `rounded=1` | 프로세스/액션 |
| decision | 마름모 | `rhombus` | 조건 분기 |
| education | 모서리 둥근 사각형 | `rounded=1` | 교육/안내 (색상으로 구분) |
| warning | 모서리 둥근 사각형 | `rounded=1` | 경고/주의 (색상으로 구분) |
| referral | 모서리 둥근 사각형 | `rounded=1` | 의뢰/이관 (색상으로 구분) |
| success | 모서리 둥근 사각형 | `rounded=1` | 성공/확인 (색상으로 구분) |

## Color Semantics

| Color | Hex | Meaning | Usage |
|-------|-----|---------|-------|
| Green | `#10b981` | 시작, 성공 | START 노드, 성공적 종료 |
| Red | `#ef4444` | 종료, 위험 | END 노드 (비정상 종료), 의뢰 |
| Yellow | `#fbbf24` | 결정, 판단 | Decision 노드 |
| Blue | `#dbeafe` | 프로세스 | 일반 프로세스/액션 |
| Purple | `#a78bfa` | 교육, 안내 | Education 노드 |
| Orange | `#f97316` | 경고, 주의 | Warning 노드 |
| Mint | `#34d399` | 확인, 완료 | Success/확정 노드 |

## Dimension Standards

| Element | Width | Height | Notes |
|---------|-------|--------|-------|
| Start/End | 240px | 60px | Pill shape (arcSize=50) |
| Process | 240px | 70px | Standard rectangle |
| Decision | 200px | 90px | Diamond (rhombus) |
| Education | 200px | 70px | Slightly narrower |
| Warning | 200px | 70px | Slightly narrower |
| Referral | 180px | 70px | Narrower for branch nodes |

## Edge Styles

| Edge Type | Style | Color | Usage |
|-----------|-------|-------|-------|
| normal | Solid, orthogonal | Default (black) | 일반 흐름 |
| yes | Solid, green tint | `strokeColor=#059669` | 긍정 분기 |
| no | Solid, red tint | `strokeColor=#dc2626` | 부정 분기 |
| loop_back | Dashed | `strokeColor=#d97706;dashed=1` | 재평가/반복 루프 |

## Layout Rules

### Flow Direction
- **Primary**: Top → Down (위에서 아래로)
- **Branches**: Left/Right (좌우 분기)
- **Loop Back**: Right side waypoints (우측 경유 루프)

### Spacing
- **Vertical (V_SPACING)**: 110px between consecutive nodes
- **Horizontal (H_SPACING)**: 280px between branch columns
- **Phase Gap**: 40px additional spacing between phases

### Alignment
- **Main flow**: Center column (x=300)
- **Yes branch**: Right of center (+H_SPACING)
- **No branch**: Left of center (-H_SPACING)
- **Sub-branches**: Additional H_SPACING offset

## Label Placement

### Node Labels
- 중앙 정렬 (whiteSpace=wrap)
- HTML 허용 (`<br>` for line breaks)
- 최대 3줄 권장
- 이모지 사용 가능 (🟢, 🔴, 📋 등)

### Edge Labels
- 엣지 중간점에 배치
- Decision 출력 엣지: 필수 (예/아니요, 조건 텍스트)
- 일반 엣지: 선택적 (필요 시에만)
- 폰트 크기: 10-11px

## Stroke Width

| Element | strokeWidth | Notes |
|---------|-------------|-------|
| START/END | 2 | 강조 |
| Decision | 2 | 강조 |
| Process | 1 | 기본 |
| Education | 1 | 기본 |
| Warning | 1 | 기본 |
| Referral | 2 | 강조 (종료 경로) |
| Edges | 1 (default) | 기본 |

## Font Sizes

| Element | fontSize | Notes |
|---------|----------|-------|
| START/END | 12 | 큰 글씨 |
| Decision | 11 | 기본 |
| Process | 11 | 기본 |
| Edge Labels | 10 | 작은 글씨 |
| Sub-labels | 9 | 세부 분기 라벨 |
