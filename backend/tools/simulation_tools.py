"""
시뮬레이션 Tool 함수 — S1, S2 담당.

⚠️ 교체 포인트 (Phase 1):
    run_dg320_simulation() → 실제 공정 시뮬레이터 Python 함수로 교체
    analyze_ripple_effect() → 실제 열연 공정 파급 효과 계산 모듈로 교체
"""


async def run_dg320_simulation(width: float, thickness: float) -> dict:
    """
    주어진 폭(mm)/두께(mm)로 DG320 에러 위험도를 계산합니다.
    에이전트가 여러 파라미터 조합으로 반복 호출하여 최적값을 탐색합니다.

    ⚠️ Mock 구현 — 선형 근사 계산
    교체 대상: 실제 열연 공정 시뮬레이터의 DG320 위험도 계산 함수
    """
    # 선형 근사: 폭이 크고 두께가 얇을수록 위험
    risk = max(0.0, min(100.0, (width - 1000) * 0.15 + (9.0 - thickness) * 20))
    risk = round(risk, 1)

    if risk > 70:
        status = "❌ 위험"
    elif risk > 30:
        status = "⚠️ 경고"
    else:
        status = "✅ 안전"

    return {
        "폭": f"{width}mm",
        "두께": f"{thickness}mm",
        "DG320_위험도": f"{risk}%",
        "상태": status,
        "_risk_value": risk,  # 최적 인덱스 계산용 내부 필드
    }


async def analyze_ripple_effect(edging_change: str) -> dict:
    """
    Edging 기준 변경 시 후공정 파급 효과를 분석합니다.

    ⚠️ Mock 구현 — 하드코딩 파급 효과 데이터
    교체 대상: 실제 공정 연동 데이터를 기반으로 한 파급 효과 계산 모듈
    """
    return {
        "diagram": (
            "graph LR\n"
            "A[Edging 기준 변경\\n두께 +0.5mm] -->|영향| B[압연 하중 증가]\n"
            "B -->|연쇄| C[냉각속도 재계산]\n"
            "B -->|연쇄| D[롤 교체 주기 단축]\n"
            "C -->|파급| E[표면 품질 등급 변동]\n"
            "D -->|파급| F[설비 유지보수 일정 충돌]\n"
            "style A fill:#4f46e5,color:#fff\n"
            "style E fill:#ef4444,color:#fff\n"
            "style F fill:#f97316,color:#fff"
        ),
        "timeline": [
            {"name": "압연 하중", "before": 320, "after": 387},
            {"name": "냉각속도(°C/s)", "before": 45, "after": 39},
            {"name": "표면 품질 점수", "before": 92, "after": 78},
            {"name": "롤 수명(일)", "before": 30, "after": 22},
        ],
    }
