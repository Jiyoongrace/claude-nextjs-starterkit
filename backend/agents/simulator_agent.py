"""
시뮬레이터 에이전트 — S1(DG320), S2(Edging 파생 효과)

ReAct 패턴:
  S1: run_dg320_simulation을 여러 파라미터 조합으로 반복 호출 → 최적 인덱스 결정
  S2: analyze_ripple_effect를 호출하여 Mermaid 다이어그램 + 시계열 데이터 획득
"""
import os
from pydantic_ai import Agent
from models.response_models import SimulationResult, RippleEffectResult, TimelineItem

_MODEL = os.getenv("CLAUDE_MODEL", "anthropic:claude-sonnet-4-20250514")

# ─── S1: DG320 에러 방지 파라미터 탐색 ─────────────────────────────────────────
simulator_s1 = Agent(
    model=_MODEL,
    output_type=SimulationResult,
    output_retries=3,
    system_prompt="""
당신은 열연 공정 시뮬레이션 전문 AI 에이전트입니다.
DG320 에러(단중 초과) 방지를 위한 최적 파라미터 조합을 탐색합니다.

반드시 run_dg320_simulation Tool을 최소 3가지 파라미터 조합(폭, 두께 변화)으로 호출하여
결과를 비교하고 DG320 위험도가 가장 낮은 조합을 optimal_index로 지정하세요.
Tool 없이 추측으로 답변하는 것을 금지합니다.

출력 형식: SimulationResult (type="simulation_table")
""",
)


@simulator_s1.tool_plain
async def run_dg320_simulation(width: float, thickness: float) -> dict:
    """
    주어진 폭(mm)/두께(mm) 조합의 DG320 위험도를 계산합니다.
    최적 파라미터 탐색을 위해 여러 조합으로 반복 호출하세요.

    Args:
        width: 슬라브 폭 (mm), 권장 범위 900~1300
        thickness: 슬라브 두께 (mm), 권장 범위 6.0~12.0
    """
    from tools.simulation_tools import run_dg320_simulation as _run
    return await _run(width, thickness)


# ─── S2: Edging 기준 변경 파생 효과 분석 ────────────────────────────────────────
simulator_s2 = Agent(
    model=_MODEL,
    output_type=RippleEffectResult,
    output_retries=3,
    system_prompt="""
당신은 열연 공정 파급 효과 분석 전문 AI 에이전트입니다.
Edging 기준 변경이 후공정에 미치는 파급 효과를 분석합니다.

반드시 analyze_ripple_effect Tool을 호출하여
Mermaid 다이어그램과 시계열 데이터를 획득한 뒤 결과를 반환하세요.
Tool 없이 임의로 다이어그램을 생성하는 것을 금지합니다.

출력 형식: RippleEffectResult (type="ripple_effect")
""",
)


@simulator_s2.tool_plain
async def analyze_ripple_effect(edging_change: str) -> dict:
    """
    Edging 기준 변경 내용을 분석하여 후공정 파급 효과를 반환합니다.

    Args:
        edging_change: 변경된 Edging 기준값 설명 (예: "두께 허용 공차 ±0.3 → ±0.5mm")
    """
    from tools.simulation_tools import analyze_ripple_effect as _run
    return await _run(edging_change)
