"""
오케스트레이터 — scenario_id 기반으로 전용 에이전트를 라우팅합니다.

각 에이전트 내부에서 ReAct 패턴(Tool 호출 → 결과 검증 → 재시도)이 작동합니다.
오케스트레이터 자체는 단순 라우터 역할로 Rule-Base가 아닌 에이전트별 추론에 위임합니다.
"""
from typing import Any
from models.request_models import AgentRunRequest
from models.response_models import (
    AgentResponse,
    SimulationResult,
    RippleEffectResult,
    GitTimelineResult,
    GraphPathResult,
    WikiResult,
    MsaDiffResult,
)
from tools.db_tools import find_diff_keys


async def run_scenario(request: AgentRunRequest) -> Any:
    """시나리오 ID에 따라 전용 에이전트를 실행하고 구조화된 결과를 반환합니다."""
    s = request.scenario_id
    p = request.params

    if s == "S1":
        from agents.simulator_agent import simulator_s1
        width = float(p.get("width", 1200))
        thickness = float(p.get("thickness", 8.5))
        error_code = str(p.get("error_code", "DG320"))

        result = await simulator_s1.run(
            f"에러코드 {error_code} 방지를 위해 폭 {width}mm, 두께 {thickness}mm 기준으로 "
            f"최적 파라미터 조합을 탐색하세요. 폭과 두께를 조금씩 변경하며 3가지 이상 조합을 시도하세요."
        )
        return result.data

    if s == "S2":
        from agents.simulator_agent import simulator_s2
        edging_value = str(p.get("edging_value", "두께 허용 공차 ±0.3 → ±0.5mm"))

        result = await simulator_s2.run(
            f"Edging 기준 변경 '{edging_value}' 에 따른 후공정 파급 효과를 분석하세요."
        )
        return result.data

    if s == "S3":
        from agents.tracer_agent import tracer_s3
        job_id = str(p.get("job_id", "JOB-2025-0325"))
        date_from = str(p.get("date_from", "2025-03-20"))
        date_to = str(p.get("date_to", "2025-03-26"))

        result = await tracer_s3.run(
            f"Job ID '{job_id}'의 비정상 종료 원인을 추적하세요. "
            f"기간: {date_from} ~ {date_to}. 의심 커밋을 is_suspect=true로 표시하세요."
        )
        return result.data

    if s == "S4":
        from agents.rag_agent import rag_s4
        term = str(p.get("term", "단중"))

        result = await rag_s4.run(
            f"'{term}' 용어의 정의와 관련 화면/DB/API 매핑을 Wiki에서 검색하세요."
        )
        return result.data

    if s == "S5":
        from agents.tracer_agent import tracer_s5
        factory_name = str(p.get("factory_name", "HOT_MILL_3"))
        systems_str = str(p.get("systems", ""))
        systems = [s.strip() for s in systems_str.split(",")] if systems_str else []

        result = await tracer_s5.run(
            f"신규 공장 '{factory_name}' 신설 시 영향받는 소스·기준·서비스 컴포넌트를 "
            f"그래프로 탐색하세요. 연동 대상: {systems if systems else '전체 시스템'}"
        )
        return result.data

    if s == "S6":
        from agents.rag_agent import rag_s6
        requester = str(p.get("requester", "홍길동"))
        screen_id = str(p.get("screen_id", "SCR_QUALITY_MGR"))
        permission_level = str(p.get("permission_level", "READ_WRITE"))

        result = await rag_s6.run(
            f"신청자 '{requester}'의 화면 '{screen_id}' 에 대한 "
            f"'{permission_level}' 권한 신청 결재 초안을 런북 기반으로 생성하세요."
        )
        return result.data

    if s == "S7":
        from agents.tracer_agent import tracer_s7
        service_a = str(p.get("service_a", "ORDER_DB"))
        service_b = str(p.get("service_b", "PROD_DB"))

        result = await tracer_s7.run(
            f"'{service_a}'와 '{service_b}' 두 서비스 간 대기량 데이터를 조회하고 "
            f"불일치 항목을 탐지하세요. 불일치 컬럼을 diff_keys에 포함하세요."
        )

        # diff_keys 자동 계산 보정 (에이전트가 누락할 경우 대비)
        data = result.data
        if isinstance(data, MsaDiffResult) and not data.diff_keys:
            data.diff_keys = find_diff_keys(data.rows_a, data.rows_b)
        return data

    raise ValueError(f"알 수 없는 시나리오 ID: {s}")
