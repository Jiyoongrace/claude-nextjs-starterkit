"""
트레이서 에이전트 — S3(Git Timeline), S5(Graph Path), S7(MSA Diff)

ReAct 패턴:
  S3: parse_git_log Tool 호출 → 의심 커밋 탐지 → GitTimelineResult 반환
  S5: traverse_factory_impact Tool 호출 → 영향받는 컴포넌트 그래프 반환
  S7: get_order_data + get_production_data 호출 → 불일치 탐지 → MsaDiffResult 반환
"""
import os
from pydantic_ai import Agent
from models.response_models import GitTimelineResult, GraphPathResult, MsaDiffResult

_MODEL = os.getenv("CLAUDE_MODEL", "anthropic:claude-sonnet-4-20250514")

# ─── S3: Slab Job 비정상 종료 원인 추적 ─────────────────────────────────────────
tracer_s3 = Agent(
    model=_MODEL,
    output_type=GitTimelineResult,
    output_retries=3,
    system_prompt="""
당신은 Git 이력 분석 전문 AI 에이전트입니다.
Slab 설계 Job 비정상 종료의 원인이 된 커밋을 탐지합니다.

반드시 parse_git_log Tool을 호출하여 해당 기간의 커밋 이력을 가져오세요.
의심 커밋(단중 허용값, 상수, 임계값 변경 등)은 is_suspect=true로 표시하세요.
Tool 없이 커밋 이력을 가정하는 것을 금지합니다.

출력 형식: GitTimelineResult (type="git_timeline")
""",
)


@tracer_s3.tool_plain
async def parse_git_log(job_id: str, date_from: str, date_to: str) -> list:
    """
    지정 기간의 Git 커밋 이력을 파싱하고 의심 커밋을 탐지합니다.

    Args:
        job_id: 비정상 종료된 Job ID (예: JOB-2025-0325)
        date_from: 조회 시작 날짜 (YYYY-MM-DD)
        date_to: 조회 종료 날짜 (YYYY-MM-DD)
    """
    from tools.git_tools import parse_git_log as _run
    return await _run(job_id, date_from, date_to)


# ─── S5: 열연공장 신설 영향도 파악 ──────────────────────────────────────────────
tracer_s5 = Agent(
    model=_MODEL,
    output_type=GraphPathResult,
    output_retries=3,
    system_prompt="""
당신은 시스템 영향도 분석 전문 AI 에이전트입니다.
신규 공장 설비 추가 시 영향받는 소스·기준·서비스를 그래프로 탐색합니다.

반드시 traverse_factory_impact Tool을 호출하여 영향받는 컴포넌트를 탐색하세요.
노드 타입: target(보라), db(파랑), service(초록), code(주황)으로 분류하세요.
Tool 없이 임의로 그래프를 구성하는 것을 금지합니다.

출력 형식: GraphPathResult (type="graph_path")
""",
)


@tracer_s5.tool_plain
async def traverse_factory_impact(factory_name: str, target_systems: list) -> dict:
    """
    신규 공장 추가 시 영향받는 소스 컴포넌트를 그래프 탐색합니다.

    Args:
        factory_name: 신규 공장 ID (예: HOT_MILL_3)
        target_systems: 연동 대상 시스템 목록 (예: ["PlanningAPI", "WeightCalc"])
    """
    from tools.graph_tools import traverse_factory_impact as _run
    return await _run(factory_name, target_systems)


# ─── S7: MSA 대기량 불일치 추적 ──────────────────────────────────────────────────
tracer_s7 = Agent(
    model=_MODEL,
    output_type=MsaDiffResult,
    output_retries=3,
    system_prompt="""
당신은 MSA 데이터 정합성 분석 전문 AI 에이전트입니다.
두 서비스 DB 간 대기량 불일치를 탐지합니다.

반드시 get_order_data와 get_production_data Tool을 모두 호출하여
두 테이블의 데이터를 비교하고 불일치 컬럼(diff_keys)을 식별하세요.
Tool 없이 데이터를 가정하는 것을 금지합니다.

출력 형식: MsaDiffResult (type="msa_diff")
""",
)


@tracer_s7.tool_plain
async def get_order_data(service_a: str) -> list:
    """
    주문 서비스 DB에서 현재 대기 주문 데이터를 조회합니다.

    Args:
        service_a: 조회할 서비스 이름 (예: ORDER_DB)
    """
    from tools.db_tools import get_order_data as _run
    return await _run(service_a)


@tracer_s7.tool_plain
async def get_production_data(service_b: str) -> list:
    """
    생산 서비스 DB에서 동일 주문에 대한 생산 상태를 조회합니다.

    Args:
        service_b: 조회할 서비스 이름 (예: PROD_DB)
    """
    from tools.db_tools import get_production_data as _run
    return await _run(service_b)
