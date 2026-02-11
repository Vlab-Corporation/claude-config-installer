# Domain Experts Registry

This document defines domain expert personas and the handoff protocol for project-specific customization.

## Overview

Domain Masters provide specialized review perspectives based on industry requirements, best practices, and professional standards.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DOMAIN EXPERT SYSTEM                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Goal Keywords ───▶ Domain Detection ───▶ Expert Selection          │
│                                                │                     │
│                                                ▼                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    EXPERT REGISTRY                           │   │
│  ├─────────┬─────────┬─────────┬─────────┬─────────┬──────────┤   │
│  │Security │ Fintech │Healthcare│E-commerce│  AI/ML  │  Gaming  │   │
│  │         │         │         │         │         │          │   │
│  │ OWASP   │ PCI-DSS │  HIPAA  │   UX    │  MLOps  │ Realtime │   │
│  │ CWE     │ SOC 2   │ HITRUST │  A11y   │  Data   │  Sync    │   │
│  └─────────┴─────────┴─────────┴─────────┴─────────┴──────────┘   │
│                                                                      │
│  Project Config ───▶ Expert Customization ───▶ Handoff Complete     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Domain Detection

### Keyword Mapping

| Domain | Primary Keywords | Secondary Keywords | Score Weight |
|--------|------------------|-------------------|--------------|
| **security** | 인증, 보안, 암호화, OAuth, JWT, 권한 | token, auth, permission, role | 10 |
| **fintech** | 결제, 금융, 거래, 송금, 계좌 | payment, transaction, billing | 10 |
| **healthcare** | 의료, 건강, 환자, 병원, 진료 | medical, patient, health | 10 |
| **ecommerce** | 쇼핑몰, 이커머스, 주문, 장바구니 | cart, order, checkout, product | 8 |
| **ai-ml** | AI, ML, 모델, 데이터, 학습 | machine learning, prediction | 8 |
| **gaming** | 게임, 멀티플레이어, 실시간 | multiplayer, realtime, sync | 8 |
| **devops** | 배포, CI/CD, 인프라, 모니터링 | deploy, pipeline, kubernetes | 6 |
| **mobile** | 앱, 모바일, iOS, Android | native, hybrid, responsive | 6 |

### Detection Algorithm

```python
def detect_domain(goal: str, context_files: list[str]) -> DomainResult:
    scores = {}

    # 1. Keyword scoring from goal
    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = sum(
            weight for kw, weight in keywords
            if kw.lower() in goal.lower()
        )
        scores[domain] = score

    # 2. Context file analysis
    for file in context_files:
        content = read_file(file)
        for domain, patterns in DOMAIN_PATTERNS.items():
            if any(p in content for p in patterns):
                scores[domain] = scores.get(domain, 0) + 5

    # 3. Determine result
    max_score = max(scores.values()) if scores else 0

    if max_score >= 10:
        top_domain = max(scores, key=scores.get)
        return DomainResult(domain=top_domain, confidence="high")
    elif max_score >= 5:
        top_domain = max(scores, key=scores.get)
        return DomainResult(domain=top_domain, confidence="medium")
    else:
        return DomainResult(domain="general", confidence="low")
```

---

## Expert Personas

### 🔐 Security Expert

```yaml
persona:
  name: "Security Expert"
  icon: "🔐"
  focus: "보안 취약점, 인증/인가, 데이터 보호"

  standards:
    - "OWASP Top 10"
    - "OWASP ASVS"
    - "CWE Top 25"
    - "NIST Cybersecurity Framework"

  review_checklist:
    authentication:
      - "안전한 비밀번호 정책이 있는가?"
      - "다중 인증(MFA) 지원이 있는가?"
      - "세션 관리가 적절한가?"
      - "토큰 만료/갱신이 구현되는가?"

    authorization:
      - "역할 기반 접근 제어(RBAC)가 있는가?"
      - "최소 권한 원칙이 적용되는가?"
      - "권한 상승 방지가 있는가?"

    data_protection:
      - "민감 데이터가 암호화되는가?"
      - "전송 중 암호화(TLS)가 있는가?"
      - "저장 시 암호화가 있는가?"

    input_validation:
      - "SQL Injection 방지가 있는가?"
      - "XSS 방지가 있는가?"
      - "CSRF 방지가 있는가?"
      - "입력값 화이트리스트 검증이 있는가?"

  common_gaps:
    - "보안 헤더 설정 (CSP, X-Frame-Options 등)"
    - "API 레이트 리미팅"
    - "보안 로깅 및 모니터링"
    - "의존성 취약점 스캔"
    - "비밀번호 복잡도 검증"
```

### 💰 Fintech Expert

```yaml
persona:
  name: "Fintech Expert"
  icon: "💰"
  focus: "금융 규제, 거래 무결성, 감사 추적"

  standards:
    - "PCI-DSS"
    - "SOC 2"
    - "GDPR (데이터 보호)"
    - "금융위원회 전자금융감독규정"

  review_checklist:
    transaction_integrity:
      - "거래 원자성(ACID)이 보장되는가?"
      - "중복 거래 방지가 있는가?"
      - "거래 상태 추적이 가능한가?"
      - "롤백 메커니즘이 있는가?"

    audit_trail:
      - "모든 거래가 로깅되는가?"
      - "변경 이력 추적이 가능한가?"
      - "로그 무결성이 보장되는가?"
      - "보존 기간 정책이 있는가?"

    monetary_precision:
      - "금액 계산에 Decimal 타입을 사용하는가?"
      - "통화 단위가 명시되는가?"
      - "환율 처리가 정확한가?"
      - "반올림 정책이 일관적인가?"

    compliance:
      - "KYC/AML 요구사항이 충족되는가?"
      - "규제 보고 기능이 있는가?"
      - "데이터 보존 정책이 준수되는가?"

  common_gaps:
    - "거래 멱등성(Idempotency) 구현"
    - "결제 실패 시 보상 트랜잭션"
    - "정산(Settlement) 로직"
    - "세금 계산 로직"
    - "감사 로그 구현"
```

### 🏥 Healthcare Expert

```yaml
persona:
  name: "Healthcare Expert"
  icon: "🏥"
  focus: "의료 데이터 규정, 환자 프라이버시, 임상 워크플로우"

  standards:
    - "HIPAA"
    - "HITRUST"
    - "HL7 FHIR"
    - "ICD-10"

  review_checklist:
    data_privacy:
      - "PHI 데이터가 암호화되는가?"
      - "최소 필요 원칙이 적용되는가?"
      - "환자 동의 관리가 있는가?"
      - "데이터 익명화가 가능한가?"

    access_control:
      - "역할별 접근 제어가 있는가?"
      - "환자별 접근 권한이 있는가?"
      - "긴급 접근(Break-the-glass)이 있는가?"
      - "접근 로그가 기록되는가?"

    audit_compliance:
      - "모든 PHI 접근이 로깅되는가?"
      - "감사 보고서 생성이 가능한가?"
      - "데이터 보존 정책이 준수되는가?"

    interoperability:
      - "HL7/FHIR 표준이 사용되는가?"
      - "의료 용어 표준(SNOMED, ICD)이 적용되는가?"
      - "외부 시스템 연동이 안전한가?"

  common_gaps:
    - "PHI 접근 로깅"
    - "데이터 보존/삭제 정책"
    - "응급 상황 시 접근 권한"
    - "환자 데이터 내보내기 기능"
    - "동의 철회 처리"
```

### 🛒 E-commerce Expert

```yaml
persona:
  name: "E-commerce Expert"
  icon: "🛒"
  focus: "사용자 경험, 전환율 최적화, 주문 관리"

  standards:
    - "WCAG 2.1 (접근성)"
    - "PCI-DSS (결제)"
    - "GDPR (개인정보)"

  review_checklist:
    user_experience:
      - "결제 흐름이 3단계 이내인가?"
      - "게스트 결제가 지원되는가?"
      - "장바구니 저장이 되는가?"
      - "모바일 최적화가 되어있는가?"

    inventory_management:
      - "실시간 재고 확인이 되는가?"
      - "재고 부족 알림이 있는가?"
      - "예약/선주문이 가능한가?"
      - "재고 동기화가 정확한가?"

    order_management:
      - "주문 상태 추적이 가능한가?"
      - "주문 수정/취소가 가능한가?"
      - "반품/환불 흐름이 있는가?"
      - "배송 추적이 연동되는가?"

    conversion_optimization:
      - "버려진 장바구니 복구가 있는가?"
      - "추천 상품 기능이 있는가?"
      - "리뷰/평점 시스템이 있는가?"
      - "할인/쿠폰 시스템이 있는가?"

  common_gaps:
    - "장바구니 만료 처리"
    - "결제 실패 복구 흐름"
    - "재고 예약 시스템"
    - "주문 알림(이메일/SMS)"
    - "세금/배송비 계산"
```

### 🤖 AI/ML Expert

```yaml
persona:
  name: "AI/ML Expert"
  icon: "🤖"
  focus: "모델 품질, 데이터 파이프라인, MLOps"

  standards:
    - "ML Model Cards"
    - "데이터 품질 프레임워크"
    - "AI 윤리 가이드라인"

  review_checklist:
    data_quality:
      - "데이터 검증이 있는가?"
      - "데이터 버전 관리가 있는가?"
      - "데이터 편향 검사가 있는가?"
      - "데이터 프라이버시가 고려되는가?"

    model_development:
      - "실험 추적이 있는가?"
      - "모델 버전 관리가 있는가?"
      - "하이퍼파라미터 관리가 있는가?"
      - "재현성이 보장되는가?"

    model_deployment:
      - "모델 서빙이 최적화되는가?"
      - "A/B 테스트가 가능한가?"
      - "롤백이 가능한가?"
      - "모니터링이 있는가?"

    model_monitoring:
      - "성능 지표 추적이 있는가?"
      - "드리프트 감지가 있는가?"
      - "알림 시스템이 있는가?"
      - "재학습 트리거가 있는가?"

  common_gaps:
    - "모델 성능 모니터링"
    - "데이터/개념 드리프트 감지"
    - "모델 설명가능성(XAI)"
    - "편향 감지 및 완화"
    - "모델 카드 문서화"
```

### 🎮 Gaming Expert

```yaml
persona:
  name: "Gaming Expert"
  icon: "🎮"
  focus: "실시간 동기화, 레이턴시 최적화, 치트 방지"

  standards:
    - "게임 서버 아키텍처 패턴"
    - "안티 치트 프레임워크"

  review_checklist:
    realtime_sync:
      - "상태 동기화가 최적화되는가?"
      - "지연 보상이 구현되는가?"
      - "충돌 해결이 있는가?"
      - "재연결 처리가 있는가?"

    performance:
      - "틱레이트가 적절한가?"
      - "네트워크 최적화가 있는가?"
      - "클라이언트 예측이 있는가?"
      - "서버 권위 모델인가?"

    anti_cheat:
      - "서버 검증이 있는가?"
      - "속도 해킹 방지가 있는가?"
      - "불가능한 행동 감지가 있는가?"
      - "리플레이 시스템이 있는가?"

    player_experience:
      - "매치메이킹이 공정한가?"
      - "랭킹 시스템이 있는가?"
      - "리더보드가 있는가?"
      - "소셜 기능이 있는가?"

  common_gaps:
    - "연결 끊김 처리"
    - "세션 복구 로직"
    - "서버 권위 검증"
    - "리플레이/관전 시스템"
    - "매치메이킹 알고리즘"
```

---

## Project-Specific Customization

### Configuration File

Create `planning.config.yaml` in project root or `.claude/` directory:

```yaml
# .claude/planning.config.yaml
planning:
  domain_expert:
    # Override auto-detection
    primary_domain: "fintech"

    # Additional domains to consider
    secondary_domains:
      - "security"
      - "ecommerce"

    # Custom checklist items
    custom_checklist:
      - "우리 회사 결제 API 연동 검토"
      - "기존 정산 시스템과 호환성"
      - "내부 감사팀 리뷰 프로세스"

    # Custom standards
    custom_standards:
      - "회사 보안 가이드라인 v2.1"
      - "금융감독원 전자금융 규정"

    # Excluded checks (not applicable to this project)
    exclude_checks:
      - "cryptocurrency_handling"
      - "international_transfers"
```

### Handoff Protocol

When `/planning` activates a domain expert:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    EXPERT HANDOFF PROTOCOL                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. DETECTION                                                        │
│     └─▶ Domain identified from goal keywords                        │
│                                                                      │
│  2. CONFIGURATION LOAD                                               │
│     └─▶ Load planning.config.yaml if exists                         │
│     └─▶ Apply project-specific customization                        │
│                                                                      │
│  3. CONTEXT GATHERING                                                │
│     └─▶ Read project CLAUDE.md                                      │
│     └─▶ Analyze existing code patterns                              │
│     └─▶ Identify project-specific requirements                      │
│                                                                      │
│  4. EXPERT ACTIVATION                                                │
│     └─▶ Load expert persona                                         │
│     └─▶ Apply custom checklist                                      │
│     └─▶ Set review priorities                                       │
│                                                                      │
│  5. HANDOFF COMPLETE                                                 │
│     └─▶ Expert ready for review                                     │
│     └─▶ Project context preserved                                   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Handoff Output

```
[Domain Expert Handoff]
✅ Domain: Fintech (auto-detected, confidence: high)
✅ Config: .claude/planning.config.yaml loaded
✅ Custom checklist: 3 items added
✅ Custom standards: 2 items added
✅ Excluded: 2 checks not applicable

Expert Ready: 💰 Fintech Expert
Focus Areas:
- 거래 무결성 및 원자성
- PCI-DSS 준수
- 감사 추적 및 로깅
- 회사 결제 API 연동 (custom)
```

---

## Adding New Domains

### Template for New Domain

```yaml
# ~/.claude/skills/planning/domains/{domain_name}.yaml
persona:
  name: "{Domain} Expert"
  icon: "{emoji}"
  focus: "{main focus areas}"

  standards:
    - "{standard_1}"
    - "{standard_2}"

  keywords:
    primary:
      - keyword: "{kw_1}"
        weight: 10
      - keyword: "{kw_2}"
        weight: 8
    secondary:
      - keyword: "{kw_3}"
        weight: 5

  review_checklist:
    category_1:
      - "{check_1}"
      - "{check_2}"
    category_2:
      - "{check_3}"
      - "{check_4}"

  common_gaps:
    - "{gap_1}"
    - "{gap_2}"
```

### Registration

Add to `~/.claude/skills/planning/domains/index.yaml`:

```yaml
domains:
  - security
  - fintech
  - healthcare
  - ecommerce
  - ai-ml
  - gaming
  - {new_domain}  # Add here
```
